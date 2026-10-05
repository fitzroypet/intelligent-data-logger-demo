"""Project-authored plant model and evaluation-only episode oracle."""
from __future__ import annotations

import numpy as np
import pandas as pd

EPISODES = (
    ("day_normal", "daily_output", "normal"),
    ("day_weather", "daily_output", "weather_loss"),
    ("day_derating", "daily_output", "pv_loss"),
    ("alarm_normal", "alarm", "normal"),
    ("alarm_overload", "alarm", "overload"),
    ("alarm_thermal", "alarm", "thermal"),
    ("alarm_unexplained", "alarm", "unknown"),
    ("trend_stable", "pv_trend", "normal"),
    ("trend_decline", "pv_trend", "pv_decline"),
    ("trend_weather", "pv_trend", "normal"),
    ("trend_low_efficiency", "pv_trend", "normal"),
    ("day_missing", "daily_output", "unknown"),
)


def generate(seed: int, episode: str, days: int = 60, interval: int = 15):
    if episode not in {e[0] for e in EPISODES} or days < 21 or interval != 15:
        raise ValueError("v1 requires a known episode, at least 21 days and 15-minute cadence")
    rng = np.random.default_rng(seed)
    pv_kwp = float(rng.uniform(3, 9))
    inverter = pv_kwp * 1000 / float(rng.uniform(1.05, 1.45))
    capacity = float(rng.uniform(5, 15) * 1000 * .9)
    efficiency = float(rng.uniform(.90, .98))
    temp_coefficient = float(rng.uniform(.003, .005))
    demand_scale = float(rng.uniform(.7, 1.4))
    power_limit = capacity * float(rng.uniform(.25, .5))
    charge_eff = float(rng.uniform(.91, .98))
    discharge_eff = float(rng.uniform(.91, .98))
    initial = capacity * float(rng.uniform(.35, .8))
    n = days * 96
    start = pd.Timestamp("2026-01-01", tz="Africa/Lagos") + pd.Timedelta(days=int(rng.integers(0, 60)))
    idx = pd.date_range(start, periods=n, freq="15min")
    hours = idx.hour.to_numpy() + idx.minute.to_numpy() / 60
    day_index = np.arange(n) // 96
    daylight = np.clip(np.sin(np.pi * (hours - 6) / 12), 0, None)
    daily_cloud = np.clip(rng.normal(.85, .09, days), .5, 1)
    clouds = np.zeros(n)
    for i, innovation in enumerate(rng.normal(0, .035, n)):
        clouds[i] = .85 * clouds[i-1] + innovation
    irradiation = 1000 * daylight * np.clip(daily_cloud[day_index] + clouds, .25, 1)
    ambient = rng.uniform(24, 31) + 6 * daylight + rng.normal(0, .3, n)
    load = inverter * demand_scale * (
        .10 + .13 * np.exp(-.5 * ((hours-7)/1.3)**2)
        + .26 * np.exp(-.5 * ((hours-20)/2)**2)
        + rng.normal(0, .007, n))
    load = np.maximum(load, 0)
    day = day_index == days-1
    target = day & (hours >= 9) & (hours < 16)
    loss = float(rng.uniform(.25, .65))
    decline = float(rng.uniform(.035, .18))
    event_hour = int(rng.integers(17, 21))
    event = day & (hours >= event_hour) & (hours < event_hour + 1.5)
    alarm = np.zeros(n, dtype=int)
    inverter_temp = ambient + 8 + .001 * load
    performance = np.ones(n)
    if episode == "day_weather":
        irradiation[target] *= 1-loss
    if episode == "day_derating":
        performance[target] *= 1-loss
    if episode == "trend_decline":
        performance *= 1-decline*np.linspace(0, 1, n)
    if episode == "trend_weather":
        irradiation *= 1-rng.uniform(.15, .35)*np.linspace(0, 1, n)
    if episode == "trend_low_efficiency":
        efficiency = float(rng.uniform(.62, .74))
    if episode == "alarm_overload":
        load[event] = inverter * rng.uniform(1.12, 1.5)
        alarm[event & (hours >= event_hour+.5)] = 1
    if episode == "alarm_thermal":
        inverter_temp[event] = rng.uniform(78, 90)
        alarm[event] = 1
        performance[event] *= .7
    if episode == "alarm_unexplained":
        alarm[event] = 1
    pv = np.minimum(inverter, pv_kwp*1000*irradiation/1000 *
                    (1-temp_coefficient*np.maximum(ambient-25, 0)) * efficiency * performance)
    charge = np.zeros(n); discharge = np.zeros(n)
    imports = np.zeros(n); exports = np.zeros(n); stored = np.zeros(n)
    energy = initial
    dt = interval/60
    for i in range(n):
        net = pv[i]-load[i]
        if net >= 0:
            charge[i] = min(net, power_limit, (capacity-energy)/charge_eff/dt)
            energy += charge[i]*charge_eff*dt
            exports[i] = net-charge[i]
        else:
            discharge[i] = min(-net, power_limit, max(0, energy-.1*capacity)*discharge_eff/dt)
            energy -= discharge[i]/discharge_eff*dt
            imports[i] = -net-discharge[i]
        stored[i] = energy
    df = pd.DataFrame({
        "timestamp": idx, "pv_ac_power_w": pv, "irradiance_wm2": irradiation,
        "ambient_temp_c": ambient, "load_power_w": load, "inverter_temp_c": inverter_temp,
        "inverter_alarm": alarm, "battery_charge_w": charge, "battery_discharge_w": discharge,
        "battery_soc_pct": stored/capacity*100, "grid_import_w": imports, "grid_export_w": exports,
    })
    residual = pv+discharge+imports-load-charge-exports
    transitions = stored-np.r_[initial, stored[:-1]]-(charge*charge_eff-discharge/discharge_eff)*dt
    physical = {
        "max_ac_balance_residual_w": float(np.abs(residual).max()),
        "max_battery_transition_residual_wh": float(np.abs(transitions).max()),
        "min_soc_pct": float(df.battery_soc_pct.min()), "max_soc_pct": float(df.battery_soc_pct.max()),
        "power_limits_respected": bool(max(charge.max(), discharge.max()) <= power_limit+1e-8),
        "simultaneous_charge_discharge": bool(((charge>1e-8)&(discharge>1e-8)).any()),
        "pv_rating_respected": bool(pv.max() <= inverter+1e-8),
    }
    physical["passed"] = bool(np.abs(residual).max()<1e-7 and np.abs(transitions).max()<1e-7
        and stored.min()>=.1*capacity-1e-7 and stored.max()<=capacity+1e-7
        and physical["power_limits_respected"] and not physical["simultaneous_charge_discharge"]
        and physical["pv_rating_respected"])
    if episode == "day_missing":
        df.loc[target, [c for c in df if c != "timestamp"]] = np.nan
    task, label = next((task, label) for name, task, label in EPISODES if name == episode)
    public = {"pv_kwp": pv_kwp, "inverter_rating_w": inverter, "interval_minutes": interval}
    oracle = {"episode": episode, "task": task, "label": label, "seed": seed,
              "query_time": str(idx[-1]), "loss_fraction": loss, "decline_fraction": decline,
              "hidden_efficiency": efficiency, "hidden_temp_coefficient": temp_coefficient,
              "battery_capacity_wh": capacity, "battery_power_limit_w": power_limit,
              "charge_efficiency": charge_eff, "discharge_efficiency": discharge_eff,
              "demand_scale": demand_scale, "event_hour": event_hour, **public}
    return df, public, oracle, physical


def corrupt(df, seed, noise_sd, missing_fraction):
    rng = np.random.default_rng(seed)
    observed = df.copy()
    columns = [c for c in df if c not in ("timestamp", "inverter_alarm")]
    for column in columns:
        values = observed[column].to_numpy().copy()
        values *= 1+rng.normal(0, noise_sd, len(values))
        values[rng.random(len(values)) < missing_fraction] = np.nan
        observed[column] = values
    return observed
