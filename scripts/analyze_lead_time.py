"""Post-hoc detection-delay analysis (daily rolling checks). Does not alter any frozen v1 result."""
from pathlib import Path
import sys, json, hashlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
local = ROOT/".venv/Lib/site-packages"
if local.exists(): sys.path.insert(0, str(local))
import pandas as pd
from src.research.lead_time import rolling_checks, summarize, CONTROLS, DECLINE

OUT = ROOT/"reports/research/20261005_lead_time"
CONDITIONS = ["full_cross", "full_inverter"]       # recent_* never reach the 14-day history requirement


def main():
    protocol = json.loads((ROOT/"config/research_protocol.json").read_text())
    days = protocol["days"]
    OUT.mkdir(exist_ok=True)
    checks = rolling_checks(protocol)
    checks.to_csv(OUT/"rolling_checks.csv.gz", index=False, compression="gzip")
    # the final-day check must reproduce the archived one-shot benchmark exactly
    archive = next((ROOT/"reports/research").glob("*_evaluation"))
    archived = pd.read_csv(archive/"predictions.csv")
    archived = archived[archived.episode.isin((DECLINE,) + CONTROLS)]
    final = checks[checks.day == days].merge(archived, on=["seed", "episode", "stress", "condition"])
    mismatches = int((final.label != final.predicted).sum())
    assert len(final) == len(archived) and mismatches == 0, (len(final), len(archived), mismatches)
    single = summarize(checks, days, 1, CONDITIONS)
    persistent = summarize(checks, days, 3, CONDITIONS)
    table = pd.concat([single, persistent], ignore_index=True)
    table.to_csv(OUT/"delay_summary.csv", index=False)
    never = checks[checks.condition.str.startswith("recent")].label.eq("pv_decline").sum()
    summary = {"analysis": "post-hoc rolling daily checks of the unchanged v1 policy; not part of the frozen protocol; "
                           "3-consecutive-flag rule specified after seeing results (exploratory)",
               "protocol_id": protocol["protocol_id"], "seeds": protocol["evaluation_seeds"],
               "checks": len(checks), "final_day_checks_matching_archive": len(final), "mismatches": mismatches,
               "recent_conditions_pv_decline_flags": int(never),
               "source_archive": archive.name,
               "source_sha256": {"predictions.csv": hashlib.sha256((archive/"predictions.csv").read_bytes()).hexdigest()},
               "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "module_sha256": hashlib.sha256((ROOT/"src/research/lead_time.py").read_bytes()).hexdigest()}
    (OUT/"summary.json").write_text(json.dumps(summary, indent=2)+"\n")
    (OUT/"analyze_lead_time.py").write_bytes(Path(__file__).read_bytes())
    pd.set_option("display.width", 250, "display.max_columns", 30)
    print(f"validation: {len(final)} final-day checks, {mismatches} mismatches")
    print(table.round(2).to_string(index=False))


if __name__ == "__main__":
    main()
