# NASEF 2026 synthetic evaluation protocol — v1

## Scope and research question

This study evaluates **information access in an evidence-producing diagnostic layer**:
when do installation history and cross-component measurements improve diagnosis or
enable justified abstention? It does not evaluate a built logger, deployment lifetime,
field accuracy, user usefulness, fleet operations or causal customer responsibility.
The existing M1–M6 demo and interactive interface remain separate and reproducible.

The supplied working draft describes a broader infrastructure vision. For this paper,
frame the contribution as an implemented architecture plus a controlled synthetic
ablation study. Replace assertions that nobody has built such a system with a verified
related-work comparison. Neither this protocol nor code execution establishes novelty
or guarantees acceptance.

## Design fixed before evaluation

Machine-readable specification: `config/research_protocol.json`. The runner archives
that file, this protocol, code hashes, seed lists and environment versions **before**
evaluating. v1 is a timestamped internal protocol, not an external preregistration.
Development seeds 100–107 and evaluation seeds 1000–1023 are disjoint. No threshold
tuning on evaluation outcomes is permitted; subsequent changes require a new version
and new evaluation seeds. Splits test new stochastic installations from the same
simulator, not novel fault families, real installations or independent authorship.

### Matched 2 × 2 information-access conditions

| Condition | Time access | Measurement access |
|---|---|---|
| full_cross | All 60 days up to question time | Inverter, PV, weather, load, battery, grid |
| recent_cross | Last 24 hours only | Same cross-component channels |
| full_inverter | All 60 days | Timestamp, inverter AC output, temperature and generic alarm |
| recent_inverter | Last 24 hours | Same inverter-only channels |

All receive the same legitimate static nameplate ratings, task type and question time.
All use the same deterministic diagnostic policy, with data-dependent feature paths.
Recent-only may still diagnose acute events. Inverter-only can detect thermal events
and raw output trends. These are **information ablations, not independently optimized
state-of-the-art competitors**. Manual dashboards and user judgement are not simulated.
The access boundary uses an explicit column allowlist, removes all future rows, and
passes no scenario name, seed, injected parameter or oracle label to the policy.

### Cases and replication

Each independently seeded installation has 12 matched episodes:

1. Daily output: normal, weather attenuation, PV conversion derating.
2. Alarm: no alarm, preceding overload, thermal stress, unexplained generic alarm.
3. Longitudinal PV: stable, gradual decline, declining irradiance, static low conversion.
4. Unavailable telemetry: entire queried daytime interval missing.

An unexplained alarm and missing telemetry require abstention; normal cases require a
supported normal result. Generic alarms are identical across causes to prevent label
leakage. Case questions identify a day/task, not an injected cause or onset. Evaluation
has 24 independent installation clusters × 12 episodes = 288 cases. Cases are paired
across four conditions and three stress levels: 3,456 predictions, not 3,456 independent
installations. Eight development clusters are reported separately.

### Simulator and independent physical checks

An isolated study generator varies PV size, inverter rating, battery capacity,
conversion efficiency, initial SOC, demand scale, weather, event severity and timing.
Clouds have daily and short-term temporal dependence. A simple irradiance/temperature
PV model feeds battery dispatch with bounded SOC and power, conversion losses, import
and export. Fault changes occur before dispatch. Battery state transitions and AC
energy balance are checked numerically before corruption. Exact ranges are in the
generator and archived parameter CSV. They are design assumptions, **not distributions
fitted to Nigerian installations**. The diurnal model omits seasonal geometry, spatial
weather and vendor protection behaviour. This generator is project-authored, and the
diagnostic policy knows its broad mechanisms: inverse-model optimism remains possible.
Temperature coefficients and static efficiencies vary; the policy uses a fixed
temperature coefficient and does not receive the hidden efficiency.

Clean physical trajectories are distinct from measured telemetry. Moderate and severe
stress add independent multiplicative Gaussian meter noise (3%/8% SD) and MCAR numeric
missingness (1%/5%). All arms get exactly the same corrupted input realization.
Noisy readings are not expected to obey exact physical equations. This is a limited
robustness analysis; it does not cover all communication faults or sensor biases.
Original dataset store and original ground-truth file are never overwritten.

## Outcomes and uncertainty

Primary: correct diagnostic label on the ten identifiable cases per installation;
abstentions count as failures to resolve those cases. Report by task as well as pooled.
Secondary: coverage (non-abstention), selective accuracy conditional on answering,
false-positive rate on the five normal/control cases, and correct abstention on the
two ambiguous/unavailable cases. Report confusion counts including abstentions.
Evidence receipts contain measurements, columns, time windows, thresholds and reasons.
Receipt presence is provenance, **not independent clinical/engineering validation**.

Compute 95% percentile bootstrap intervals by resampling whole installation clusters
(2,000 replicates, fixed seed). The same draws are used for paired contrasts. Main
contrasts: full_cross minus recent_cross; full_cross minus full_inverter. Also report
the factorial interaction in primary accuracy. Do not pool stress levels or development
and evaluation splits. Intervals describe variability within this simulator; no field
confidence or formal hypothesis-test claim is made. Zero-width intervals can occur
when every simulated cluster has the same score. No samples are dropped on failure;
invalid physical trajectories stop the run and errors must be retained.

## Live Claude layer

Live experiments are separate from the deterministic study. A bounded development
pilot uses seed 100, 12 episodes and two extreme conditions (24 conversations; at most
48 generation requests). Temperature 0, fixed dated model, at most 700 output tokens
per request. The first request requires a call to a constrained evidence tool; the
second returns structured diagnosis, explanation and cited receipt measurement names.
The tool sees only the assigned view. The model gets no raw series or oracle labels.
This tests evidence retrieval and reporting fidelity; it does **not** establish LLM
diagnostic superiority, numerical fidelity throughout prose or conversational usability.

Record raw response blocks, prompt, tool receipts, exact returned model, token usage,
latency, errors and parsed final output. Report tool invocation, valid JSON, label
agreement with the receipt, reference validity and oracle label accuracy separately.
Independent review of unsupported prose remains necessary. The pilot is development
data and one model pass: no live generalization or statistical significance claim.
Paid execution requires the CLI `--execute` flag; a plan is printed by default. A
request cap and bounded evidence prevent runaway loops; estimated prices use standard
Sonnet 4.5 rates and actual billing may differ. No retries are automatic.

## Artifacts and publication

Each offline run writes manifest, per-case oracle records, physical checks, predictions
with receipts, installation parameters, metrics, paired effects, confusion matrices,
paper tables, PNG/SVG figures and a findings report. Optional compressed telemetry
archives support independent inspection; otherwise seeds plus hashed code regenerate it.
Never silently relabel a development or smoke run as evaluation.

Before submission: review the failure cases, narrow claims to measured outcomes,
verify literature references, review the physical assumptions with a domain expert,
and describe limitations prominently. Human assessment, public/real data validation
and the broader hardware/product vision remain future work.
