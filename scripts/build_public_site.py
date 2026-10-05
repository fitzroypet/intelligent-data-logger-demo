"""Build a public static site from explicitly selected assets and verified archives."""
from pathlib import Path
import csv, hashlib, json, shutil, argparse, re
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'src/interface/static/explorer'
DEMO=ROOT/'reports/runs/20260921T055826825005Z'
EVAL=ROOT/'reports/research/offline-evaluation'
LIVE='live-pilot'
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def validate_demo():
    demo=read(ASSETS/'data/experiment.json'); official=read(DEMO/'m6_dry_run.json')
    truth=read(ROOT/'data/ground_truth.json')
    for case in demo['scenarios']:
        match=next(c for c in official['scenario_results'] if c['event_type']==case['event_type'])
        for key in ['evidence','dimensions','overall']:
            if case[key]!=match[key]:raise ValueError(f'Explorer/archive mismatch: {case["event_type"]} {key}')
        if case['ground_truth']!=next(c for c in truth['events'] if c['event_type']==case['event_type']):
            raise ValueError('Ground truth mismatch')
    return demo

def generate_data():
    validate_demo()
    metrics=list(csv.DictReader((EVAL/'metrics.csv').open(encoding='utf-8',newline='')))
    source_files=['metrics.csv','paired_effects.csv','task_metrics.csv','unresolved_or_incorrect.csv','predictions.csv']
    data={'run':EVAL.name,'installations':24,'episodes':288,'predictions':3456,'identifiable_per_condition':240,
          'abstention_cases_per_condition':48,'metrics':metrics,
          'source_sha256':{name:sha(EVAL/name) for name in source_files},'live':None}
    live=ROOT/'reports/research'/LIVE
    if (live/'summary.json').exists():
        records=[json.loads(line) for line in (live/'conversations.jsonl').read_text(encoding='utf-8').splitlines()]
        data['live']={'run':LIVE,'summary':read(live/'summary.json'),'model':read(live/'manifest.json')['protocol']['live']['model'],
            'format_sensitivity':read(ROOT/'reports/research/live-pilot-format-sensitivity/summary.json'),
            'records':[{key:r.get(key) for key in ['case_id','episode','condition','status','question','final_text','scores','elapsed_seconds']} for r in records]}
    (ASSETS/'data/research.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    telemetry=ROOT/'data/processed/telemetry.csv'
    if telemetry.exists():
        expected=next(v for k,v in read(DEMO/'run_manifest.json')['sha256'].items() if k.replace('\\','/')=='data/processed/telemetry.csv')
        if sha(telemetry)!=expected:raise ValueError('Demo telemetry differs from archived hash; refusing new trace')
        keys=['grid_import_w','battery_discharge_w','load_power_w','battery_soc_pct','grid_available','unmet_load_w']
        rows=[]
        with telemetry.open(encoding='utf-8',newline='') as stream:
            for r in csv.DictReader(stream):
                t=r['timestamp']
                if t[:10]=='2026-10-10' and '20:30'<=t[11:16]<='23:30':
                    rows.append({'timestamp':t,**{k:float(r[k]) if r[k] not in ['True','False'] else int(r[k]=='True') for k in keys}})
        (ASSETS/'data/outage.json').write_text(json.dumps({'source_run':DEMO.name,'source_file':'data/processed/telemetry.csv','sha256':expected,'rows':rows},indent=2)+'\n',encoding='utf-8')
    elif not (ASSETS/'data/outage.json').exists():raise ValueError('Verified outage trace is missing')
    return data

def dashboard_assets(out):
    source=ROOT/'src/interface/static'
    recorded=source/'offline/data'
    manifest=read(recorded/'manifest.json')
    names=manifest['sha256']
    if len(names)!=122 or not {'snapshot.json','answers.json'}<=names.keys():
        raise ValueError('Incomplete offline dashboard export')
    for name,digest in names.items():
        if not re.fullmatch(r'(snapshot|answers)\.json|days/\d{4}-\d{2}-\d{2}\.json',name):
            raise ValueError('Unexpected offline dashboard asset')
        if sha(recorded/name)!=digest:raise ValueError('Offline dashboard hash mismatch: '+name)
    target=out/'dashboard';target.mkdir(parents=True,exist_ok=True)
    html=(source/'index.html').read_text(encoding='utf-8')
    html=html.replace('href="/app.css"','href="./app.css"').replace('<script src="/app.js" defer></script>','<script src="./demo-api.js" defer></script><script src="./app.js" defer></script>')
    html=html.replace('href="/"','href="./"').replace('href="/explorer/"','href="../index.html"')
    html=html.replace('Local workspace','Public offline demo').replace('Synthetic data','Synthetic offline demo')
    html=html.replace('</header>','</header><p class="mode-note" style="padding:12px 0">Public demonstration using synthetic telemetry. Charts are interactive; suggested answers replay recorded analysis. Claude requires a backend. <a href="../research.html">View research results</a>.</p>',1)
    html=html.replace('Claude · API usage','Claude · backend required').replace('Ask about your solar system…','Choose a topic below, or type status')
    (target/'index.html').write_text(html,encoding='utf-8')
    for name in ['app.css','app.js']:shutil.copyfile(source/name,target/name)
    shutil.copyfile(source/'offline/demo-api.js',target/'demo-api.js')
    for name in [*names,'manifest.json']:
        dest=target/'data'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(recorded/name,dest)
    return ['dashboard/'+name for name in ['index.html','app.css','app.js','demo-api.js']]+['dashboard/data/'+name for name in [*names,'manifest.json']]

def build(out):
    # Only these named files are eligible for publication. No .env, logs, or raw local tree.
    data=generate_data()
    out.mkdir(parents=True,exist_ok=True)
    allowed=['index.html','research.html','app.js','research.js','styles.css','data/experiment.json','data/research.json','data/outage.json']
    for relative in allowed:
        target=out/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ASSETS/relative,target)
    allowed+=dashboard_assets(out)
    (out/'.nojekyll').write_text('')
    (out/'publication.json').write_text(json.dumps({'demo':DEMO.name,'evaluation':EVAL.name,'live':data['live']['run'] if data['live'] else None,
        'sha256':{name:sha(out/name) for name in allowed}},indent=2)+'\n')
    print(f'Published build: {out}; {len(allowed)} reviewed assets plus provenance')
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='.site');args=parser.parse_args()
    build((ROOT/args.output).resolve())
