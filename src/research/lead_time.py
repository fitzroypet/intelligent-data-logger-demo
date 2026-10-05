"""Post-hoc rolling-check (detection delay) analysis; not part of the frozen v1 protocol.

The frozen policy is queried at the end of every day from the minimum-history day to the end
of the record instead of once at the end. Simulator, corruption, access restrictions and policy
are re-used unchanged. Truth (the injected decline) is read only for scoring.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .policy import restrict, diagnose
from .simulation import EPISODES, generate, corrupt

DECLINE = "trend_decline"
CONTROLS = ("trend_stable", "trend_weather", "trend_low_efficiency")
_INDEX = {name: i for i, (name, _, _) in enumerate(EPISODES)}
_TASK = {name: task for name, task, _ in EPISODES}


def true_crossing_day(decline_fraction, days, threshold, steps_per_day=96):
    """First 1-based day on which the injected mean performance loss reaches `threshold`, else NaN."""
    loss = decline_fraction * np.linspace(0, 1, days * steps_per_day).reshape(days, steps_per_day).mean(axis=1)
    hit = np.flatnonzero(loss >= threshold)
    return float(hit[0] + 1) if hit.size else np.nan


def rolling_checks(protocol, seeds=None, episodes=(DECLINE,) + CONTROLS):
    """One row per (seed, episode, stress, condition, day): the label returned by the unchanged policy."""
    thresholds, days = protocol["thresholds"], protocol["days"]
    first_day = thresholds["minimum_history_days"]
    rows = []
    for seed in (seeds if seeds is not None else protocol["evaluation_seeds"]):
        for episode in episodes:
            df, static, oracle, _ = generate(seed, episode, days, protocol["interval_minutes"])
            crossing = np.nan
            if episode == DECLINE:
                crossing = true_crossing_day(oracle["decline_fraction"], days, thresholds["trend_decline_fraction"])
            for s_index, (stress, settings) in enumerate(protocol["stress_levels"].items()):
                noise_seed = seed*10000 + _INDEX[episode]*10 + s_index      # same seeds as the archived benchmark
                observed = corrupt(df, noise_seed, settings["relative_noise_sd"], settings["missing_fraction"])
                for condition in protocol["conditions"]:
                    for day in range(first_day, days+1):                     # `day` = days of record at the check
                        view = restrict(observed, condition, df.timestamp.iloc[day*96-1])
                        label = diagnose(view, static, _TASK[episode], thresholds)["label"]
                        rows.append(dict(seed=seed, episode=episode, stress=stress, condition=condition, day=day,
                                         label=label, true_decline=oracle["decline_fraction"], crossing_day=crossing))
    return pd.DataFrame(rows)


def first_flag_day(days, flags, consecutive=1):
    """Day of the first check at which `consecutive` flags in a row have occurred (NaN if never)."""
    order = np.argsort(days)
    flags = np.asarray(flags, bool)[order]
    days = np.asarray(days)[order]
    if consecutive > 1:
        flags = np.convolve(flags, np.ones(consecutive, int), "full")[:len(flags)] >= consecutive
    return float(days[flags.argmax()]) if flags.any() else np.nan


def summarize(checks, days, consecutive=1, conditions=None, bootstrap=2000, bootstrap_seed=20261005):
    """Detection delay on declines that reach the threshold, and installations with any false flag on controls."""
    rng = np.random.default_rng(bootstrap_seed)
    out = []
    selected = checks if conditions is None else checks[checks.condition.isin(conditions)]
    for (stress, condition), g in selected.groupby(["stress", "condition"]):
        dec = g[g.episode == DECLINE]
        detect = dec.groupby("seed").apply(
            lambda x: first_flag_day(x.day.to_numpy(), (x.label == "pv_decline").to_numpy(), consecutive),
            include_groups=False)
        meta = dec.drop_duplicates("seed").set_index("seed")
        eligible = meta.crossing_day.notna()
        delay = (detect - meta.crossing_day)[eligible]
        ctl = g[g.episode.isin(CONTROLS)]
        false_any = ctl.groupby("seed").apply(
            lambda x: any(not np.isnan(first_flag_day(y.day.to_numpy(), (y.label == "pv_decline").to_numpy(), consecutive))
                          for _, y in x.groupby("episode")), include_groups=False)
        valid = delay.dropna().to_numpy()
        lo, hi = (np.percentile([rng.choice(valid, len(valid)).mean() for _ in range(bootstrap)], [2.5, 97.5])
                  if len(valid) > 1 else (np.nan, np.nan))
        out.append(dict(rule=f"{consecutive} consecutive" if consecutive > 1 else "single flag",
                        stress=stress, condition=condition,
                        declines_reaching_threshold=int(eligible.sum()), flagged=int(detect[eligible].notna().sum()),
                        median_delay_days=float(delay.median()), mean_delay_days=float(delay.mean()),
                        mean_delay_ci_lo=float(lo), mean_delay_ci_hi=float(hi),
                        single_check_at_end_median_delay=float((days-meta.crossing_day[eligible]).median()),
                        installations_with_false_flag=int(false_any.sum()), installations=int(len(false_any))))
    return pd.DataFrame(out)
