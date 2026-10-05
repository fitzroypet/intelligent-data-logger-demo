"""Run a frozen offline information-access study without changing the original demo."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import shutil
import sys
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
local = ROOT/".venv/Lib/site-packages"
if local.exists(): sys.path.insert(0, str(local))
import pandas as pd
from src.research.simulation import EPISODES, generate, corrupt
from src.research.policy import restrict, diagnose
from src.research.reporting import write_report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=["development", "evaluation"], default="development")
    parser.add_argument("--protocol", type=Path, default=ROOT/"config/research_protocol.json")
    parser.add_argument("--archive-telemetry", action="store_true")
    args = parser.parse_args()
    protocol = json.loads(args.protocol.read_text())
    assert not set(protocol["development_seeds"]) & set(protocol["evaluation_seeds"])
    seeds = protocol[args.split+"_seeds"]
    started = datetime.now(timezone.utc)
    output = ROOT/"reports/research"/(started.strftime("%Y%m%dT%H%M%S%fZ")+"_"+args.split)
    output.mkdir(parents=True)
    sources = list((ROOT/"src/research").glob("*.py")) + [Path(__file__).resolve(), args.protocol,
                ROOT/"docs/RESEARCH_PROTOCOL.md"]
    hashes = {}
    for source in sources:
        relative = source.relative_to(ROOT)
        dest = output/"source"/relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)
        hashes[str(relative)] = hashlib.sha256(source.read_bytes()).hexdigest()
    manifest = {"protocol_id": protocol["protocol_id"], "split": args.split, "seeds": seeds,
        "started_utc": started.isoformat(), "status": "running", "synthetic": True,
        "python": platform.python_version(), "packages": {p:version(p) for p in ["numpy", "pandas", "matplotlib"]},
        "code_sha256": hashes, "telemetry_archived": args.archive_telemetry,
        "sampling_unit": "installation seed; episodes, conditions and stress levels are paired"}
    def save_manifest(): (output/"manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    save_manifest()
    (output/"protocol.json").write_text(json.dumps(protocol, indent=2), encoding="utf-8")
    print(f"Run directory: {output}", flush=True)
    predictions=[]; checks=[]; fingerprints=[]
    try:
        with (output/"receipts.jsonl").open("w", encoding="utf-8") as receipts, \
             (output/"oracle.jsonl").open("w", encoding="utf-8") as oracle_file, \
             (output/"physical_checks.jsonl").open("w", encoding="utf-8") as physical_file:
            for seed in seeds:
                for episode_index, (episode, task, _) in enumerate(EPISODES):
                    case_id = f"site-{seed}-case-{episode_index:02d}"
                    df, static, oracle, physical = generate(seed, episode, protocol["days"], protocol["interval_minutes"])
                    checks.append(physical)
                    physical_file.write(json.dumps(dict(case_id=case_id, **physical))+"\n")
                    oracle_file.write(json.dumps(dict(case_id=case_id, **oracle))+"\n")
                    if not physical["passed"]:
                        raise RuntimeError(f"Physical validation failed for {case_id}; no trajectory discarded")
                    if args.archive_telemetry:
                        folder = ROOT/"data/research"/output.name
                        folder.mkdir(parents=True, exist_ok=True)
                        df.to_csv(folder/f"{case_id}.csv.gz", index=False, compression="gzip")
                    for stress_index, (stress, settings) in enumerate(protocol["stress_levels"].items()):
                        noise_seed = seed*10000+episode_index*10+stress_index
                        observed = corrupt(df, noise_seed, settings["relative_noise_sd"], settings["missing_fraction"])
                        fingerprints.append({"case_id": case_id, "stress": stress, "noise_seed": noise_seed,
                            "rows": len(observed), "data_hash": hashlib.sha256(pd.util.hash_pandas_object(observed, index=True).values.tobytes()).hexdigest()})
                        for condition in protocol["conditions"]:
                            view = restrict(observed, condition, oracle["query_time"])
                            receipt = diagnose(view, static, task, protocol["thresholds"])
                            row = dict(case_id=case_id, seed=seed, episode=episode, task=task,
                                       stress=stress, condition=condition, expected=oracle["label"],
                                       predicted=receipt["label"], correct=receipt["label"] == oracle["label"])
                            predictions.append(row)
                            receipts.write(json.dumps(dict(**row, evidence=receipt), allow_nan=False)+"\n")
                print(f"Completed installation {seed}: {len(predictions)} predictions", flush=True)
        rows = pd.DataFrame(predictions)
        rows.to_csv(output/"predictions.csv", index=False)
        pd.DataFrame(fingerprints).to_csv(output/"dataset_hashes.csv", index=False)
        write_report(output, rows, protocol, args.split, checks)
        manifest.update(status="complete", finished_utc=datetime.now(timezone.utc).isoformat(),
                        predictions=len(predictions), episodes=len(checks), all_physical_checks_passed=True)
        manifest["artifact_sha256"] = {p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                                      for p in output.iterdir() if p.is_file() and p.name!="manifest.json"}
        save_manifest()
        print(f"Complete: {output/'REPORT.md'}", flush=True)
    except Exception as exc:
        manifest.update(status="failed", error_type=type(exc).__name__, completed_predictions=len(predictions))
        save_manifest()
        raise


if __name__ == "__main__":
    main()
