"""Post-hoc sensitivity analysis; never overwrites the frozen live-run scores."""
from pathlib import Path
import sys,json,re,hashlib,statistics,csv
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
local=ROOT/'.venv/Lib/site-packages'
if local.exists():sys.path.insert(0,str(local))
from src.research.live import score_final
RUN=ROOT/'reports/research/live-pilot'
OUT=ROOT/'reports/research/live-pilot-format-sensitivity'
def main():
 OUT.mkdir(exist_ok=True)
 records=[json.loads(line) for line in (RUN/'conversations.jsonl').read_text(encoding='utf-8').splitlines()]
 rows=[]
 for r in records:
  text=r.get('final_text','');match=re.fullmatch(r'\s*```(?:json)?\s*\n(.*?)\n```\s*',text,re.S)
  normalized=match.group(1) if match else text
  receipt=r['tool_receipts'][0]['receipt']
  scores=score_final(normalized,receipt,r['expected'])
  parsed=json.loads(normalized)
  rows.append({'case_id':r['case_id'],'episode':r['episode'],'condition':r['condition'],'outer_fence_removed':bool(match),**scores,
    'invalid_citations':sorted(set(parsed.get('citations',[]))-set(receipt['measurements']))})
 counts={k:sum(r[k] for r in rows) for k in ['outer_fence_removed','valid_json','label_fidelity','oracle_correct','citation_validity','nonempty_explanation']}
 summary={'analysis':'post-hoc outer Markdown fence removal only; original primary scores unchanged','source_run':RUN.name,'denominator':len(rows),'counts':counts,
  'by_condition':{c:{k:sum(r[k] for r in rows if r['condition']==c) for k in counts} for c in ['full_cross','recent_inverter']},
  'latency_seconds':{'median':statistics.median(r['elapsed_seconds'] for r in records),'min':min(r['elapsed_seconds'] for r in records),'max':max(r['elapsed_seconds'] for r in records)},
  'source_sha256':{'conversations.jsonl':hashlib.sha256((RUN/'conversations.jsonl').read_bytes()).hexdigest()},
  'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
 (OUT/'analyze_live_format.py').write_bytes(Path(__file__).read_bytes())
 (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 with (OUT/'cases.csv').open('w',newline='',encoding='utf-8') as f:
  writer=csv.DictWriter(f,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
 (OUT/'REPORT.md').write_text('''# Live pilot: post-hoc format sensitivity

The frozen primary evaluation recorded **0/24 strict JSON outputs**. All 24 model
responses were wrapped in a Markdown JSON fence despite the instruction to return
only JSON. No original scores, prompts or responses have been changed.

This supplementary analysis removes exactly one enclosing Markdown fence and then
applies the original scorer. It was specified after seeing the output and is therefore
**exploratory**, not a replacement primary endpoint. No further paid requests were made.

```json
'''+json.dumps(summary,indent=2)+'''
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
''',encoding='utf-8')
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
