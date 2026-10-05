"""Oracle-free diagnostic policy shared by all information-access conditions."""
from __future__ import annotations

import numpy as np
import pandas as pd

INVERTER = ("timestamp", "pv_ac_power_w", "inverter_temp_c", "inverter_alarm")
CROSS = INVERTER + ("irradiance_wm2", "ambient_temp_c", "load_power_w",
                   "battery_soc_pct", "battery_charge_w", "battery_discharge_w",
                   "grid_import_w", "grid_export_w")
CONDITIONS = ("full_cross", "recent_cross", "full_inverter", "recent_inverter")


def restrict(df, condition, query_time):
    if condition not in CONDITIONS:
        raise ValueError("Unknown information-access condition")
    end = pd.Timestamp(query_time)
    view = df.loc[df.timestamp <= end]
    if condition.startswith("recent"):
        view = view.loc[view.timestamp > end-pd.Timedelta(hours=24)]
    columns = CROSS if condition.endswith("cross") else INVERTER
    return view.loc[:, [c for c in columns if c in view]].copy()


def diagnose(view, static, task, thresholds):
    """No file access, no simulator import and no oracle arguments."""
    measurements = {}
    receipt = {"label": "unknown", "reason": "Insufficient evidence", "measurements": measurements,
               "columns_available": list(view.columns), "rows_available": len(view),
               "data_window": None, "thresholds": dict(thresholds)}
    def done(label, reason):
        receipt.update(label=label, reason=reason)
        return receipt
    if view.empty:
        return receipt
    receipt["data_window"] = {"start": str(view.timestamp.min()), "end": str(view.timestamp.max())}
    current_date = view.timestamp.max().date()
    day = view[view.timestamp.dt.date == current_date]
    cross = "irradiance_wm2" in view
    t = thresholds
    def enough(data, columns):
        if data.empty or not set(columns).issubset(data.columns):
            return False
        coverage = float(data[columns].notna().all(axis=1).mean())
        measurements["required_input_coverage"] = coverage
        return coverage >= t["minimum_coverage"]
    def daytime(data):
        return data[(data.timestamp.dt.hour >= 9) & (data.timestamp.dt.hour < 16)]
    def normalized(data):
        valid = data.dropna(subset=["pv_ac_power_w", "irradiance_wm2", "ambient_temp_c"])
        valid = valid[(valid.irradiance_wm2 > 200) & (valid.pv_ac_power_w < .97*static["inverter_rating_w"])]
        expected = static["pv_kwp"]*valid.irradiance_wm2*(1-.004*np.maximum(valid.ambient_temp_c-25, 0))
        return pd.Series((valid.pv_ac_power_w/expected).to_numpy(), index=valid.timestamp)
    if task == "alarm":
        if not enough(day, ["inverter_alarm"]):
            return receipt
        alarms = day.loc[day.inverter_alarm.fillna(0)>0]
        measurements["alarm_samples"] = int(len(alarms))
        if alarms.empty:
            return done("normal", "No inverter alarm in the queried day")
        onset = alarms.timestamp.min()
        window = day[(day.timestamp >= onset-pd.Timedelta(minutes=45)) &
                     (day.timestamp <= alarms.timestamp.max())]
        if cross and enough(window, ["load_power_w", "inverter_temp_c"]):
            above = window.load_power_w > static["inverter_rating_w"]
            minutes = int(above.sum())*static["interval_minutes"]
            prior = window[(window.timestamp < onset) & (window.load_power_w > static["inverter_rating_w"])]
            measurements.update(overload_minutes=minutes, peak_load_w=float(window.load_power_w.max()),
                                inverter_rating_w=static["inverter_rating_w"])
            if minutes >= t["overload_minutes"] and not prior.empty:
                return done("overload", "Above-rating load preceded a generic inverter alarm; responsibility is not inferred")
        if enough(window, ["inverter_temp_c"]):
            maximum = float(window.inverter_temp_c.max())
            measurements["max_inverter_temp_c"] = maximum
            if maximum >= t["thermal_c"]:
                return done("thermal", "Elevated inverter temperature coincides with the alarm")
        return done("unknown", "An alarm alone does not establish its cause")
    if task == "daily_output":
        target = daytime(day)
        needed = ["pv_ac_power_w"] + (["irradiance_wm2", "ambient_temp_c"] if cross else [])
        if not enough(target, needed):
            return receipt
        baseline = daytime(view[view.timestamp.dt.date < current_date])
        baseline = baseline[baseline.timestamp >= view.timestamp.max()-pd.Timedelta(days=8)]
        observed = float(target.pv_ac_power_w.mean())
        measurements["target_mean_pv_w"] = observed
        history = baseline.timestamp.dt.date.nunique() >= 3
        if cross:
            ratio = normalized(target)
            if len(ratio) < 6:
                return done("unknown", "Too few unclipped daylight observations")
            perf = float(ratio.median())
            measurements["target_normalized_performance"] = perf
            if history and enough(baseline, needed):
                before = normalized(baseline)
                if before.empty:
                    return receipt
                relative = 1-perf/float(before.median())
                irradiance_loss = 1-float(target.irradiance_wm2.mean())/float(baseline.irradiance_wm2.mean())
                measurements.update(relative_performance_loss=relative, irradiance_loss=irradiance_loss)
                if relative > t["relative_performance_loss"]:
                    return done("pv_loss", "Output fell relative to the weather-normalized historical baseline")
                if irradiance_loss > t["drop_fraction"]:
                    return done("weather_loss", "Lower irradiance explains the observed output reduction")
                return done("normal", "No material drop against the observed baseline")
            if perf < t["absolute_performance_ratio"]:
                return done("pv_loss", "Low normalized output against a fixed nameplate expectation; no historical baseline")
            return done("unknown", "A single day cannot establish a weather-driven drop relative to prior days")
        if history and enough(baseline, ["pv_ac_power_w"]):
            loss = 1-observed/float(baseline.pv_ac_power_w.mean())
            measurements["raw_output_loss"] = loss
            if loss <= t["drop_fraction"]:
                return done("normal", "No material output reduction against recent history")
        return done("unknown", "Output-only telemetry cannot separate weather from conversion loss")
    if task == "pv_trend":
        daylight = daytime(view)
        needed = ["pv_ac_power_w"] + (["irradiance_wm2", "ambient_temp_c"] if cross else [])
        if not enough(daylight, needed):
            return receipt
        if cross:
            ratio = normalized(daylight)
            daily = ratio.groupby(ratio.index.floor("D")).median().dropna()
        else:
            daily = daylight.groupby(daylight.timestamp.dt.floor("D")).pv_ac_power_w.mean().dropna()
        measurements["valid_days"] = len(daily)
        if len(daily) < t["minimum_history_days"]:
            return done("unknown", "Insufficient historical days to estimate a longitudinal change")
        width = max(3, len(daily)//6)
        early, late = float(daily.iloc[:width].median()), float(daily.iloc[-width:].median())
        decline = 1-late/early if early>0 else 0
        measurements.update(early_median=early, late_median=late, decline_fraction=decline,
                            weather_normalized=cross)
        if decline > t["trend_decline_fraction"]:
            return done("pv_decline", "Sustained decline in " + ("weather-normalized performance" if cross else "raw daily output; weather is unobserved"))
        return done("normal", "No material longitudinal decline in the available measurements")
    raise ValueError("Unsupported research task")
