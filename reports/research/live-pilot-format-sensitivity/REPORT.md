# Live pilot: post-hoc format sensitivity

The frozen primary evaluation recorded **0/24 strict JSON outputs**. All 24 model
responses were wrapped in a Markdown JSON fence despite the instruction to return
only JSON. No original scores, prompts or responses have been changed.

This supplementary analysis removes exactly one enclosing Markdown fence and then
applies the original scorer. It was specified after seeing the output and is therefore
**exploratory**, not a replacement primary endpoint. No further paid requests were made.

```json
{
  "analysis": "post-hoc outer Markdown fence removal only; original primary scores unchanged",
  "source_run": "live-pilot",
  "denominator": 24,
  "counts": {
    "outer_fence_removed": 24,
    "valid_json": 24,
    "label_fidelity": 24,
    "oracle_correct": 16,
    "citation_validity": 15,
    "nonempty_explanation": 24
  },
  "by_condition": {
    "full_cross": {
      "outer_fence_removed": 12,
      "valid_json": 12,
      "label_fidelity": 12,
      "oracle_correct": 12,
      "citation_validity": 10,
      "nonempty_explanation": 12
    },
    "recent_inverter": {
      "outer_fence_removed": 12,
      "valid_json": 12,
      "label_fidelity": 12,
      "oracle_correct": 4,
      "citation_validity": 5,
      "nonempty_explanation": 12
    }
  },
  "latency_seconds": {
    "median": 6.263,
    "min": 4.184,
    "max": 37.639
  },
  "source_sha256": {
    "conversations.jsonl": "6fc584e85f3186b77ec8c22686ed8a529139758a5f320387017614dd02dbcd93"
  },
  "script_sha256": "1b7229fc76a91559f78269c45e37f3ef4c4db70e4abab83e0235eb8ffdd959fc"
}
```

`cases.csv` lists every invalid citation. References to telemetry columns, data_window
or minimum_history_days are not valid measurement names under the frozen rubric,
even when those strings appear elsewhere in the tool receipt.

A qualitative assistant review of the 24 explanations identified examples needing
human/domain review: alarm_normal/recent_inverter generalized zero alarm samples to
all telemetry being normal; alarm_normal/full_cross described all columns as examined;
day_missing/recent_inverter named irradiance as missing although that channel was
excluded by design; alarm_overload/recent_inverter used categorical "ruling out"
language. These observations are not blinded expert ratings or a scored prose-quality
estimate. Numerical fidelity throughout the prose remains unvalidated.

Interpretation: the tool-selection path operated in 24/24 conversations, but strict
output compliance failed. Label fidelity after a transparent parser normalization
must not be reported as 100% end-to-end success. The limited development pilot does
not establish field reliability or general conversational safety.
