# Live development pilot

One development installation; two access conditions; no statistical inference.

```json
{
  "attempted_conversations": 1,
  "planned_conversations": 24,
  "requests": 1,
  "estimated_usage_usd": 0.0,
  "reserved_usd": 0.02112,
  "completed": 0,
  "tool_selection_correct": 0,
  "counts": {
    "valid_json": 0,
    "label_fidelity": 0,
    "oracle_correct": 0,
    "citation_validity": 0,
    "nonempty_explanation": 0
  }
}
```

Counts use all attempted conversations; failed and truncated calls remain visible. Citation validity checks measurement names, not every numerical or causal assertion in prose. This is reporting fidelity over a deterministic tool, not an independent LLM diagnostic benchmark.

Inspect `conversations.jsonl` for raw outputs, evidence, model usage and failures. Credentials and upstream error bodies are not recorded.