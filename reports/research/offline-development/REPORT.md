# Synthetic information-access study

Split: **development**. Protocol: `nasef-synthetic-v1`.

8 independent synthetic installation clusters; 96 physical episodes; 1152 paired predictions across four access conditions and three stress levels.

All clean physical trajectories passed validation. Observation corruption was applied afterward.

## Condition results

Accuracy denominator: identifiable cases; abstentions on those cases count as unresolved. 95% intervals resample whole installations. Coverage is reported separately.

| Stress | Condition | Diagnostic accuracy [95% CI] | Coverage | Selective accuracy | Normal false positives | Correct abstention |
|---|---|---|---|---|---|---|
| clean | full_cross | 97.5% [93.8%, 100.0%] | 83.3% | 97.5% | 2.5% | 100.0% |
| clean | full_inverter | 53.8% [48.8%, 57.5%] | 57.3% | 78.3% | 22.5% | 100.0% |
| clean | recent_cross | 40.0% [40.0%, 40.0%] | 33.3% | 100.0% | 0.0% | 100.0% |
| clean | recent_inverter | 20.0% [20.0%, 20.0%] | 16.7% | 100.0% | 0.0% | 100.0% |
| moderate | full_cross | 97.5% [93.8%, 100.0%] | 83.3% | 97.5% | 2.5% | 100.0% |
| moderate | full_inverter | 53.8% [50.0%, 57.5%] | 56.2% | 79.8% | 20.0% | 100.0% |
| moderate | recent_cross | 40.0% [40.0%, 40.0%] | 33.3% | 100.0% | 0.0% | 100.0% |
| moderate | recent_inverter | 20.0% [20.0%, 20.0%] | 16.7% | 100.0% | 0.0% | 100.0% |
| severe | full_cross | 87.5% [82.5%, 93.8%] | 75.0% | 97.5% | 2.5% | 100.0% |
| severe | full_inverter | 53.8% [50.0%, 57.5%] | 56.2% | 79.8% | 20.0% | 100.0% |
| severe | recent_cross | 35.0% [30.0%, 38.8%] | 29.2% | 100.0% | 0.0% | 100.0% |
| severe | recent_inverter | 20.0% [20.0%, 20.0%] | 16.7% | 100.0% | 0.0% | 100.0% |

## Paired effects on diagnostic accuracy

Differences in percentage points; paired cluster bootstrap, not independent-case tests.

| Stress | Contrast | Difference [95% CI], pp |
|---|---|---|
| clean | history_given_cross | 57.5 [53.8, 60.0] |
| clean | cross_given_history | 43.8 [40.0, 48.8] |
| clean | factorial_interaction | 23.8 [20.0, 28.7] |
| moderate | history_given_cross | 57.5 [53.8, 60.0] |
| moderate | cross_given_history | 43.8 [41.2, 47.5] |
| moderate | factorial_interaction | 23.8 [21.3, 27.5] |
| severe | history_given_cross | 52.5 [47.5, 56.2] |
| severe | cross_given_history | 33.8 [28.8, 37.5] |
| severe | factorial_interaction | 18.8 [16.3, 20.0] |

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
