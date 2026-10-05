# Research experiment index

The benchmark isolates historical and cross-component data access. Start with the
[protocol](../../docs/RESEARCH_PROTOCOL.md), then read the evaluation report below.

## Folder names

Archive folders are named by role. Frozen v1 archives were originally named by their run timestamp;
the contents, manifests and hashes are unchanged, and `scripts/verify_research_run.py` still passes.

| Folder | Original name | Role |
|---|---|---|
| `offline-development` | `20260923T190055526477Z_development` | Development split, 8 seeds |
| `offline-evaluation` | `20260923T190318100907Z_evaluation` | Frozen evaluation, 24 seeds (primary results) |
| `live-pilot-attempt-1-incomplete` | `20260923T190500485533Z_live_development` | First live attempt; incomplete (workspace ID required) |
| `live-pilot-attempt-2-connection-failure` | `20260928T072728456454Z_live_development` | Second live attempt; connection failure preserved |
| `live-pilot` | `20260928T072939445717Z_live_development` | Completed 24-conversation live pilot |
| `live-pilot-format-sensitivity` | `20260928_live_format_sensitivity` | Post-hoc Markdown-fence analysis of the pilot |
| `detection-delay` | `20261005_lead_time` | Post-hoc rolling daily-check analysis (not frozen v1) |

| Run | Role | Outcome |
|---|---|---|
| [Development](offline-development/REPORT.md) | 8 seeds, 96 episodes, 1,152 predictions | Complete; clean physical checks passed |
| [Evaluation](offline-evaluation/REPORT.md) | 24 disjoint seeds, 288 episodes, 3,456 predictions | Complete; clean physical checks passed |
| [Live development pilot](live-pilot-attempt-1-incomplete/REPORT.md) | Planned 24 conversations | Incomplete: first request rejected; workspace ID required |

## Live pilot — 28 September 2026

- [Preserved connection failure](live-pilot-attempt-2-connection-failure/REPORT.md):
  one attempted request, no generated response or usage returned.
- [Completed pilot](live-pilot/REPORT.md): 24 conversations,
  48 requests, intended tools selected in 24/24, strict JSON accepted in 0/24.
- [Post-hoc format sensitivity](live-pilot-format-sensitivity/REPORT.md): removing
  one outer Markdown fence recovers 24 receipt-consistent labels; 15/24 satisfy the
  measurement-name citation rule; 16/24 match the oracle including required abstentions.
  This supplements, and does not replace, the frozen primary scores.

## Detection delay — 5 October 2026 (post-hoc)

- [Rolling daily checks](detection-delay/REPORT.md): the unchanged v1 policy queried every day
  from day 14 to day 60. With cross-component data and clean readings a gradual decline is flagged a
  median of 4 days after it reaches 5% (19/20); inverter-only checks flag earlier only through false
  alarms (24/24 installations). Final-day checks reproduce the archived benchmark exactly. This is not
  part of the frozen v1 protocol, and its 3-consecutive-flag variant is exploratory.

## Paper artifacts

- [Clean-data accuracy figure (PNG)](offline-evaluation/accuracy.png)
  / [SVG](offline-evaluation/accuracy.svg)
- [Noise/missingness sensitivity figure (PNG)](offline-evaluation/robustness.png)
  / [SVG](offline-evaluation/robustness.svg)
- [Metric estimates and intervals](offline-evaluation/metrics.csv)
- [Paired effects](offline-evaluation/paired_effects.csv)
- [Task-specific results](offline-evaluation/task_metrics.csv)
- [Confusion counts](offline-evaluation/confusion.csv)
- [Every unresolved/incorrect prediction](offline-evaluation/unresolved_or_incorrect.csv)
- [Raw predictions](offline-evaluation/predictions.csv)
- [Evidence receipts](offline-evaluation/receipts.jsonl)
- [Provenance manifest](offline-evaluation/manifest.json)

The primary clean full-condition result is 233/240 identifiable cases correct (97.1%).
Its seven failures are five missed gradual declines, one normal day called weather loss,
and one normal day left unresolved. Do not suppress them or tune v1 against these seeds.

The original M5/M6 evaluation remains under `reports/runs/`. Its pass/fail rubric and
this benchmark's per-case diagnostic-label metrics answer different questions.
