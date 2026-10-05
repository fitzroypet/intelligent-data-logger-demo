# Synthetic information-access study

Split: **evaluation**. Protocol: `nasef-synthetic-v1`.

24 independent synthetic installation clusters; 288 physical episodes; 3456 paired predictions across four access conditions and three stress levels.

All clean physical trajectories passed validation. Observation corruption was applied afterward.

## Condition results

Accuracy denominator: identifiable cases; abstentions on those cases count as unresolved. 95% intervals resample whole installations. Coverage is reported separately.

| Stress | Condition | Diagnostic accuracy [95% CI] | Coverage | Selective accuracy | Normal false positives | Correct abstention |
|---|---|---|---|---|---|---|
| clean | full_cross | 97.1% [95.4%, 98.8%] | 83.0% | 97.5% | 0.8% | 100.0% |
| clean | full_inverter | 53.8% [51.3%, 56.2%] | 58.7% | 76.4% | 19.2% | 100.0% |
| clean | recent_cross | 40.0% [40.0%, 40.0%] | 33.3% | 100.0% | 0.0% | 100.0% |
| clean | recent_inverter | 20.0% [20.0%, 20.0%] | 16.7% | 100.0% | 0.0% | 100.0% |
| moderate | full_cross | 97.5% [95.4%, 99.2%] | 83.3% | 97.5% | 0.8% | 100.0% |
| moderate | full_inverter | 53.8% [51.3%, 56.2%] | 58.7% | 76.4% | 19.2% | 100.0% |
| moderate | recent_cross | 40.0% [40.0%, 40.0%] | 33.3% | 100.0% | 0.0% | 100.0% |
| moderate | recent_inverter | 20.0% [20.0%, 20.0%] | 16.7% | 100.0% | 0.0% | 100.0% |
| severe | full_cross | 90.0% [87.1%, 92.9%] | 78.5% | 95.6% | 0.8% | 100.0% |
| severe | full_inverter | 53.3% [50.8%, 55.8%] | 58.3% | 76.2% | 20.0% | 100.0% |
| severe | recent_cross | 38.3% [36.7%, 39.6%] | 31.9% | 100.0% | 0.0% | 100.0% |
| severe | recent_inverter | 20.0% [20.0%, 20.0%] | 16.7% | 100.0% | 0.0% | 100.0% |

## Paired effects on diagnostic accuracy

Differences in percentage points; paired cluster bootstrap, not independent-case tests.

| Stress | Contrast | Difference [95% CI], pp |
|---|---|---|
| clean | history_given_cross | 57.1 [55.4, 58.8] |
| clean | cross_given_history | 43.3 [40.8, 45.8] |
| clean | factorial_interaction | 23.3 [20.8, 25.8] |
| moderate | history_given_cross | 57.5 [55.4, 59.2] |
| moderate | cross_given_history | 43.8 [41.7, 45.8] |
| moderate | factorial_interaction | 23.7 [21.7, 25.8] |
| severe | history_given_cross | 51.7 [48.3, 54.6] |
| severe | cross_given_history | 36.7 [32.5, 40.4] |
| severe | factorial_interaction | 18.3 [14.2, 22.1] |

## Read the evidence

- `predictions.csv` and `receipts.jsonl`: every outcome and its diagnostic evidence.
- `oracle.jsonl`: evaluation-only causes and generator parameters.
- `task_metrics.csv` / `confusion.csv`: task-specific results and confusion counts.
- `unresolved_or_incorrect.csv`: every abstention on an identifiable case and every misclassification.
- `physical_checks.jsonl`: clean-trajectory checks; `dataset_hashes.csv`: input fingerprints.
- `manifest.json`, `protocol.json`, `source/`: frozen run provenance and source snapshot.
- `accuracy.png` / `.svg`, `robustness.png` / `.svg`: figures for review/export.

## Limits on interpretation

These are project-authored synthetic tasks and matched information ablations using one shared policy, not independently optimized competing products. Same-simulator evaluation seeds do not establish external validity. Cases deliberately probe information dependencies, so the pooled result depends on this task mix. Inspect task-level outcomes.

No live language-model performance, hardware deployment, user study or field accuracy is measured here. Neither the policy nor its uncertainty intervals support customer blame.

Development results must not be presented as held-out evaluation. Receipt presence does not by itself establish that an explanation is causally correct.
