"""Plan by default; --execute runs a bounded paid development pilot."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
local=ROOT/".venv/Lib/site-packages"
if local.exists():sys.path.insert(0,str(local))
from dotenv import load_dotenv
from src.research.live import Budget, run_case
from src.research.policy import restrict
from src.research.simulation import EPISODES, generate


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--execute",action="store_true")
    parser.add_argument("--max-usd",type=float,default=3.0)
    args=parser.parse_args()
    protocol=json.loads((ROOT/"config/research_protocol.json").read_text())
    live=protocol["live"]
    print(json.dumps({"mode":"paid development pilot" if args.execute else "plan only; no API calls",
                      "model":live["model"],"seed":live["pilot_seed"],"conditions":live["pilot_conditions"],
                      "conversations":len(EPISODES)*len(live["pilot_conditions"]),
                      "max_generation_requests":live["max_requests"],"reservation_limit_usd":args.max_usd,
                      "billing_note":"Conservative byte-based input estimate; actual usage recorded; no retries."},indent=2),flush=True)
    if not args.execute:return
    load_dotenv(ROOT/".env")
    key=os.getenv("ANTHROPIC_API_KEY")
    if not key:raise SystemExit("No API key configured in local .env; no requests made.")
    from anthropic import Anthropic
    client=Anthropic(api_key=key,timeout=60,max_retries=0)
    out=ROOT/"reports/research"/(datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")+"_live_development")
    out.mkdir(parents=True)
    budget=Budget(live,args.max_usd)
    records=[]
    manifest={"protocol":protocol,"mode":"live development pilot","status":"running",
              "pricing_source":"https://platform.claude.com/docs/en/about-claude/pricing",
              "source_sha256":{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in list((ROOT/"src/research").glob("*.py"))+[Path(__file__).resolve()]}}
    for relative in manifest["source_sha256"]:
        target=out/"source"/relative
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/relative,target)
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2))
    print(f"Run directory: {out}",flush=True)
    with (out/"conversations.jsonl").open("w",encoding="utf-8") as stream:
        stop=False
        for i,(episode,task,expected) in enumerate(EPISODES):
            if stop:break
            df,static,oracle,physical=generate(live["pilot_seed"],episode,protocol["days"],protocol["interval_minutes"])
            if not physical["passed"]:raise RuntimeError("Physical validation failed before API request")
            for condition in live["pilot_conditions"]:
                record=run_case(client,restrict(df,condition,oracle["query_time"]),static,task,expected,
                                protocol["thresholds"],live,budget)
                record.update(case_id=f"site-{live['pilot_seed']}-case-{i:02d}",episode=episode,condition=condition,expected=expected)
                records.append(record)
                stream.write(json.dumps(record,allow_nan=False)+"\n");stream.flush()
                print(f"{episode} / {condition}: {record['status']}; estimated used ${budget.actual_estimate:.4f}",flush=True)
                if record["status"] in ("error","budget_limit"):
                    stop=True;break
    summary={"attempted_conversations":len(records),"planned_conversations":24,"requests":budget.requests,
             "estimated_usage_usd":round(budget.actual_estimate,6),"reserved_usd":round(budget.reserved_usd,6),
             "completed":sum(r["status"]=="complete" for r in records),
             "tool_selection_correct":sum(r["tool_selection_correct"] for r in records),
             "counts":{k:sum(r.get("scores",{}).get(k,False) for r in records) for k in
                       ["valid_json","label_fidelity","oracle_correct","citation_validity","nonempty_explanation"]}}
    manifest.update(status="complete" if len(records)==24 and summary["completed"]==24 else "incomplete",summary=summary)
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2))
    (out/"summary.json").write_text(json.dumps(summary,indent=2))
    lines=["# Live development pilot","", "One development installation; two access conditions; no statistical inference.","",
           "```json",json.dumps(summary,indent=2),"```","",
           "Counts use all attempted conversations; failed and truncated calls remain visible. "
           "Citation validity checks measurement names, not every numerical or causal assertion in prose. "
           "This is reporting fidelity over a deterministic tool, not an independent LLM diagnostic benchmark.","",
           "Inspect `conversations.jsonl` for raw outputs, evidence, model usage and failures. "
           "Credentials and upstream error bodies are not recorded."]
    (out/"REPORT.md").write_text("\n".join(lines),encoding="utf-8")
    print(json.dumps(summary,indent=2),flush=True)
    if manifest["status"]!="complete":raise SystemExit(1)


if __name__=="__main__":main()
