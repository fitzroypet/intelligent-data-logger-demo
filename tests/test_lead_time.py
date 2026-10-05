import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.research.lead_time import rolling_checks, first_flag_day, true_crossing_day, summarize, DECLINE
from src.research.policy import restrict, diagnose
from src.research.simulation import generate, corrupt

PROTOCOL = json.loads((Path(__file__).resolve().parents[1]/"config/research_protocol.json").read_text())


def test_first_flag_day_handles_order_and_persistence():
    days = [5, 3, 4, 6, 7]
    flags = [True, False, True, False, True]            # by day: 3 F, 4 T, 5 T, 6 F, 7 T
    assert first_flag_day(days, flags) == 4
    assert first_flag_day(days, flags, consecutive=2) == 5
    assert np.isnan(first_flag_day(days, flags, consecutive=3))
    assert np.isnan(first_flag_day([1, 2], [False, False]))


def test_true_crossing_day_is_nan_when_decline_never_reaches_threshold():
    assert np.isnan(true_crossing_day(.04, 60, .05))
    assert 18 <= true_crossing_day(.18, 60, .05) <= 51
    assert true_crossing_day(.18, 60, .05) < true_crossing_day(.08, 60, .05)


def test_final_rolling_check_reproduces_one_shot_diagnosis_and_never_sees_the_future():
    seed = 100
    checks = rolling_checks(PROTOCOL, seeds=[seed], episodes=(DECLINE,))
    df, static, oracle, _ = generate(seed, DECLINE)
    for s_index, (stress, settings) in enumerate(PROTOCOL["stress_levels"].items()):
        observed = corrupt(df, seed*10000 + 8*10 + s_index, settings["relative_noise_sd"], settings["missing_fraction"])
        for condition in PROTOCOL["conditions"]:
            one_shot = diagnose(restrict(observed, condition, oracle["query_time"]), static, "pv_trend",
                                PROTOCOL["thresholds"])["label"]
            row = checks[(checks.stress == stress) & (checks.condition == condition) & (checks.day == 60)]
            assert row.label.iloc[0] == one_shot
    assert checks.day.min() == PROTOCOL["thresholds"]["minimum_history_days"]
    assert not checks[checks.condition.str.startswith("recent")].label.eq("pv_decline").any()


def test_summary_counts_false_flags_per_installation_not_per_check():
    rows = []
    for seed, flagged in ((1, [False, True, True]), (2, [False, False, False])):
        for episode in ("trend_decline", "trend_stable"):
            for day, f in zip((20, 21, 22), flagged):
                rows.append(dict(seed=seed, episode=episode, stress="clean", condition="full_cross", day=day,
                                 label="pv_decline" if f else "normal", true_decline=.1,
                                 crossing_day=21. if episode == "trend_decline" else np.nan))
    result = summarize(pd.DataFrame(rows), 60, consecutive=1, bootstrap=10).iloc[0]
    assert result.installations == 2 and result.installations_with_false_flag == 1
    assert result.flagged == 1 and result.median_delay_days == 0
    assert summarize(pd.DataFrame(rows), 60, consecutive=3, bootstrap=10).iloc[0].installations_with_false_flag == 0
