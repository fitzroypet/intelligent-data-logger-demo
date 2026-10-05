# Post-hoc detection-delay analysis (daily rolling checks)

**Status: post-hoc extension, not part of the frozen v1 protocol.** No v1 prediction, threshold or
score was changed. The unchanged policy is queried at the end of every day from day 14 (the
minimum-history requirement) to day 60, instead of once at day 60. The simulator, corruption seeds,
access restrictions and policy are those of the 20260923 evaluation (24 seeds, 1000-1023).

**Validation.** The day-60 check reproduces every archived one-shot prediction for the four trend
episodes: 1,152 comparisons, 0 mismatches. The two `recent_*` conditions never flag a decline
(the policy needs 14 days of history), so they are omitted from the summary.

## Definitions

- **True onset:** the first day on which the injected mean performance loss reaches 5%, the policy's
  own `trend_decline_fraction`. Read from the evaluation-only oracle, for scoring only.
  4 of the 24 declines (final loss under 5%) never reach 5% within 60 days and are excluded from delay.
- **Detection delay:** day of the first flag minus the true onset day. Negative = flagged before the
  loss reached 5%.
- **False flag:** an installation is counted if any daily check on any of the three normal trend
  episodes (`trend_stable`, `trend_weather`, `trend_low_efficiency`) returns `pv_decline`.
- **3 consecutive:** alert only after three consecutive daily flags. **This rule was specified after
  seeing the single-flag results and is exploratory.**

## Results (selected rows of `delay_summary.csv`)

| Rule | Stress | Condition | Flagged / 20 | Median delay (days) | False-flag installations / 24 |
|---|---|---|---|---|---|
| single flag | clean | full_cross | 19 | 4.0 | 0 |
| single flag | moderate | full_cross | 19 | 1.0 | 0 |
| single flag | severe | full_cross | 20 | -7.5 | 13 |
| 3 consecutive | severe | full_cross | 18 | 4.5 | 4 |
| single flag | clean | full_inverter | 18 | -7.5 | 24 |

A single check at day 60 flags the same declines a median of 30 days after onset; this reference
depends on the 60-day window and is illustrative.

Interpretation: with cross-component data and clean readings, daily checks flag a gradual decline a
median of 4 days after it reaches 5%. Inverter-only checks are "earlier" only because they cannot
separate a cloudier month from degradation: every installation receives a false flag, and in the
declining-irradiance control the policy flags on about 65% of checks. Under severe corruption even the
cross-component policy produces early flags (13/24 installations with a false flag), which a
persistence rule reduces.

## Limits

Only gradual decline has an onset in the simulator. Onset is defined by the policy's own threshold.
The decline is linear and the simulator is shared with the policy (inverse-model optimism). Acute
faults are flagged by the first check after they occur, so their delay depends only on check
frequency and is not simulated. Not a field result; no incident-rate claim follows.

Files: `delay_summary.csv`, `rolling_checks.csv.gz` (every daily label), `summary.json` (hashes),
`analyze_lead_time.py` (copy of `scripts/analyze_lead_time.py`). Code: `src/research/lead_time.py`.
Run with `python scripts/analyze_lead_time.py` (about 2 minutes).
