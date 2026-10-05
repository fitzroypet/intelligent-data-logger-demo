"""Installation-cluster summaries, paired effects and exportable figures."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

METRICS = ("diagnostic_accuracy", "coverage", "selective_accuracy", "normal_false_positive_rate", "correct_abstention")


def metrics(rows):
    known = rows[rows.expected != "unknown"]
    answered = rows[rows.predicted != "unknown"]
    normal = rows[rows.expected == "normal"]
    unknown = rows[rows.expected == "unknown"]
    return {
        "diagnostic_accuracy": float(known.correct.mean()) if len(known) else np.nan,
        "coverage": float((rows.predicted != "unknown").mean()),
        "selective_accuracy": float(answered.correct.mean()) if len(answered) else np.nan,
        "normal_false_positive_rate": float((~normal.predicted.isin(["normal", "unknown"])).mean()) if len(normal) else np.nan,
        "correct_abstention": float((unknown.predicted == "unknown").mean()) if len(unknown) else np.nan,
    }


def summarize(rows: pd.DataFrame, protocol):
    rng = np.random.default_rng(protocol["bootstrap_seed"])
    seeds = sorted(rows.seed.unique())
    samples = rng.integers(0, len(seeds), size=(protocol["bootstrap_replicates"], len(seeds)))
    summary = []
    cluster = []
    for (stress, condition), group in rows.groupby(["stress", "condition"], sort=True):
        # Macro-average over independently seeded installations, not rows or episodes.
        per = pd.DataFrame([dict(seed=seed, **metrics(group[group.seed == seed])) for seed in seeds])
        cluster += [dict(stress=stress, condition=condition, **r) for r in per.to_dict("records")]
        item = {"stress": stress, "condition": condition, "installations": len(seeds), "cases": len(group)}
        for metric in METRICS:
            values = per[metric].to_numpy()
            available = np.isfinite(values)
            item[metric] = float(np.nanmean(values)) if available.any() else None
            if available.all():
                boot = values[samples].mean(axis=1)
                lo, hi = np.quantile(boot, [.025, .975])
                item[metric+"_lo"] = float(lo); item[metric+"_hi"] = float(hi)
            else:
                item[metric+"_lo"] = item[metric+"_hi"] = None
        summary.append(item)
    cluster = pd.DataFrame(cluster)
    effects = []
    for stress in protocol["stress_levels"]:
        frame = cluster[cluster.stress == stress].pivot(index="seed", columns="condition", values="diagnostic_accuracy").loc[seeds]
        contrasts = {
            "history_given_cross": frame.full_cross-frame.recent_cross,
            "cross_given_history": frame.full_cross-frame.full_inverter,
            "factorial_interaction": frame.full_cross-frame.recent_cross-frame.full_inverter+frame.recent_inverter,
        }
        for name, contrast in contrasts.items():
            values = contrast.to_numpy()
            lo, hi = np.quantile(values[samples].mean(axis=1), [.025, .975])
            effects.append({"stress": stress, "contrast": name, "difference": float(values.mean()),
                            "ci_low": float(lo), "ci_high": float(hi), "clusters": len(seeds)})
    return pd.DataFrame(summary), pd.DataFrame(effects), cluster


def write_report(output: Path, rows, protocol, split, physical):
    summary, effects, clusters = summarize(rows, protocol)
    summary.to_csv(output/"metrics.csv", index=False)
    effects.to_csv(output/"paired_effects.csv", index=False)
    clusters.to_csv(output/"installation_metrics.csv", index=False)
    task = []
    for (stress, condition, family), group in rows.groupby(["stress", "condition", "task"]):
        task.append(dict(stress=stress, condition=condition, task=family, **metrics(group)))
    pd.DataFrame(task).to_csv(output/"task_metrics.csv", index=False)
    confusion = rows.groupby(["stress", "condition", "task", "expected", "predicted"]).size().reset_index(name="count")
    confusion.to_csv(output/"confusion.csv", index=False)
    failures = rows[~rows.correct]
    failures.to_csv(output/"unresolved_or_incorrect.csv", index=False)
    def percent(value):
        return "N/A" if pd.isna(value) else f"{100*value:.1f}%"
    lines = ["# Synthetic information-access study", "", f"Split: **{split}**. Protocol: `{protocol['protocol_id']}`.", "",
             f"{rows.seed.nunique()} independent synthetic installation clusters; {len(physical)} physical episodes; "
             f"{len(rows)} paired predictions across four access conditions and three stress levels.", "",
             "All clean physical trajectories passed validation. Observation corruption was applied afterward.", "",
             "## Condition results", "",
             "Accuracy denominator: identifiable cases; abstentions on those cases count as unresolved. "
             "95% intervals resample whole installations. Coverage is reported separately.", "",
             "| Stress | Condition | Diagnostic accuracy [95% CI] | Coverage | Selective accuracy | Normal false positives | Correct abstention |",
             "|---|---|---|---|---|---|---|"]
    for r in summary.to_dict("records"):
        lines.append(f"| {r['stress']} | {r['condition']} | {percent(r['diagnostic_accuracy'])} "
                     f"[{percent(r['diagnostic_accuracy_lo'])}, {percent(r['diagnostic_accuracy_hi'])}] | "
                     + " | ".join(percent(r[k]) for k in METRICS[1:]) + " |")
    lines += ["", "## Paired effects on diagnostic accuracy", "",
              "Differences in percentage points; paired cluster bootstrap, not independent-case tests.", "",
              "| Stress | Contrast | Difference [95% CI], pp |", "|---|---|---|"]
    for r in effects.to_dict("records"):
        lines.append(f"| {r['stress']} | {r['contrast']} | {100*r['difference']:.1f} "
                     f"[{100*r['ci_low']:.1f}, {100*r['ci_high']:.1f}] |")
    lines += ["", "## Read the evidence", "",
              "- `predictions.csv` and `receipts.jsonl`: every outcome and its diagnostic evidence.",
              "- `oracle.jsonl`: evaluation-only causes and generator parameters.",
              "- `task_metrics.csv` / `confusion.csv`: task-specific results and confusion counts.",
              "- `unresolved_or_incorrect.csv`: every abstention on an identifiable case and every misclassification.",
              "- `physical_checks.jsonl`: clean-trajectory checks; `dataset_hashes.csv`: input fingerprints.",
              "- `manifest.json`, `protocol.json`, `source/`: frozen run provenance and source snapshot.",
              "- `accuracy.png` / `.svg`, `robustness.png` / `.svg`: figures for review/export.", "",
              "## Limits on interpretation", "",
              "These are project-authored synthetic tasks and matched information ablations using one shared "
              "policy, not independently optimized competing products. Same-simulator evaluation seeds "
              "do not establish external validity. Cases deliberately probe information dependencies, so "
              "the pooled result depends on this task mix. Inspect task-level outcomes.", "",
              "No live language-model performance, hardware deployment, user study or field accuracy is "
              "measured here. Neither the policy nor its uncertainty intervals support customer blame.", "",
              "Development results must not be presented as held-out evaluation. Receipt presence does "
              "not by itself establish that an explanation is causally correct.", ""]
    (output/"REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    colors = ["#1c6652", "#6d9b81", "#d1a35c", "#8a9aa8"]
    clean = summary[summary.stress == "clean"].set_index("condition").loc[protocol["conditions"]]
    fig, ax = plt.subplots(figsize=(8, 4.5), constrained_layout=True)
    values = clean.diagnostic_accuracy.to_numpy()*100
    ax.bar(np.arange(4), values, color=colors, yerr=np.vstack([
        values-clean.diagnostic_accuracy_lo.to_numpy()*100,
        clean.diagnostic_accuracy_hi.to_numpy()*100-values]), capsize=5)
    ax.set_xticks(np.arange(4), [c.replace("_", "\n") for c in protocol["conditions"]])
    ax.set_ylabel("Correct diagnosis on identifiable cases (%)")
    ax.set_ylim(0, 105); ax.set_title(f"Synthetic {split}: clean telemetry\n95% installation-cluster bootstrap intervals")
    ax.spines[["top", "right"]].set_visible(False)
    for ext in ("png", "svg"): fig.savefig(output/f"accuracy.{ext}", dpi=220)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 4.5), constrained_layout=True)
    for condition, color in zip(protocol["conditions"], colors):
        group = summary[summary.condition == condition].set_index("stress").loc[list(protocol["stress_levels"])]
        ax.plot(list(protocol["stress_levels"]), group.diagnostic_accuracy*100, marker="o", label=condition, color=color)
    ax.set_ylim(0, 105); ax.set_ylabel("Correct diagnosis on identifiable cases (%)")
    ax.set_title(f"Synthetic {split}: sensor-noise and missingness sensitivity")
    ax.legend(frameon=False); ax.spines[["top", "right"]].set_visible(False)
    for ext in ("png", "svg"): fig.savefig(output/f"robustness.{ext}", dpi=220)
    plt.close(fig)
    return summary
