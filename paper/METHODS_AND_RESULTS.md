# Methods and results material for the NASEF paper

**Earlier methods/results working material. See [the integrated full manuscript](FULL_PAPER.md) for the current submission text.** These sections are
grounded in the archived evaluation. Related work, references, author details, venue
formatting and domain review still need completion. Do not claim hardware deployment
or validated live-model performance from these results.

## Suggested title

Evaluating historical and cross-component evidence for conversational solar-system diagnostics: a synthetic study

## Contribution and research questions

The Intelligent Data Logger is proposed as an inverter-centred architecture that retains
installation history and makes deterministic engineering evidence available to a
conversational interface. The present study evaluates one part of that architecture:
the diagnostic value of access to historical and cross-component observations.
No physical data logger was built or evaluated for this experiment.

RQ1: Under a fixed diagnostic policy, how does historical access affect the proportion
of identifiable synthetic cases resolved correctly?

RQ2: Under the same policy, how does access to weather and load channels, in addition
to inverter channels, affect diagnosis and false-positive behaviour?

RQ3: How do these results change with meter noise and missing readings?

The evidence-backed conversational interface is implemented. Faithful reporting by a
live language model is a separate evaluation target, not an explanation of the offline
accuracy differences.

## Architecture

The research pipeline separates (1) clean physical trajectories, (2) corrupted observed
telemetry, (3) condition-specific data access, (4) deterministic diagnosis with receipts,
and (5) oracle-based scoring. The oracle contains injected causes and simulation
parameters and is never an input to diagnosis. Four access conditions share the same
policy. A separate Claude runner selects an approved tool and explains its receipt.
The local interface provides a status snapshot followed by questions and evidence
inspection; interactive demonstration records are not included as research samples.

## Synthetic data and sampling

Eight development installations and 24 evaluation installations are represented by
disjoint random seeds. Each seed generates varied nameplate ratings, battery capacity,
conversion and charge/discharge efficiencies, temperature response, load and weather.
Each installation contributes twelve matched episodes, each containing 60 days at
15-minute cadence (5,760 timestamps). Clean evaluation data therefore comprise 288
episodes and 1,658,880 timestamp rows, but only **24 installation-level sampling units**.
Matched episodes from one installation are not independent field assets.

The twelve episodes cover normal and attenuated daily production, PV conversion loss,
normal/overload/thermal/unexplained alarms, stable/declining/weather-driven/static-low-
efficiency longitudinal output, and missing telemetry. Five episodes are normal or
non-degradation controls; two require abstention. Generic inverter alarms do not name
their injected cause. All fault effects precede energy dispatch. AC balance, battery
energy transitions, SOC limits, PV rating and charge/discharge power limits are checked
before measurement corruption. All 288 evaluation trajectories passed these checks.

The simulator is project-authored and is not fitted to Nigerian installation data.
Daily clouds and short-term weather variation are stochastic, but the diurnal PV model
is deliberately simplified. Exact distributions and parameter realizations are
available in the source snapshot and evaluation oracle. They establish controlled
variation, not population representativeness.

## Experimental conditions and outcome definitions

The two factors are temporal access (all 60 days versus the last 24 hours) and channel
access (inverter plus cross-component measurements versus inverter only). Static
nameplate ratings and question times are shared. Explicit column and timestamp filters
exclude prohibited measurements and future observations before diagnosis. These
conditions are information ablations under a shared policy, not separately optimized
baseline products or a comparison against expert installers.

Clean, moderate and severe observation conditions are paired across access conditions.
Moderate stress adds 3% relative Gaussian meter noise and 1% independently missing numeric
readings; severe stress adds 8% noise and 5% missingness. The twelve episodes across
24 installations, four conditions and three stress levels produce 3,456 predictions.

The primary outcome is correct diagnostic label among ten identifiable episodes per
installation, including controls. An unknown response on an identifiable case counts
as unresolved and receives no correctness credit. Coverage is the proportion of all
twelve episodes receiving a non-unknown response. Selective accuracy is correctness
conditional on responding. We additionally report abnormal diagnoses among normal
controls and abstention on the two deliberately ambiguous/unavailable cases.

Each metric is calculated within an installation and averaged across installations.
Uncertainty is a 95% percentile interval from 2,000 installation-cluster bootstrap draws.
Paired effects use the same draws and matched installation differences. Stress levels
are reported separately. These intervals describe stochastic variation within this
simulator, not uncertainty about field performance. There is no hypothesis-test or
statistical-significance claim.

## Results

Table 1. Clean-data evaluation; 24 synthetic installations and 240 identifiable cases
per condition. Percentages are installation means. CI denotes cluster bootstrap interval.

| Access condition | Correct diagnosis, % [95% CI] | Coverage, % | Selective accuracy, % | False positives on controls, % |
|---|---:|---:|---:|---:|
| Full history + cross-component | 97.1 [95.4, 98.8] | 83.0 | 97.5 | 0.8 |
| Full history + inverter-only | 53.8 [51.3, 56.2] | 58.7 | 76.4 | 19.2 |
| Recent-only + cross-component | 40.0 [40.0, 40.0] | 33.3 | 100.0 | 0.0 |
| Recent-only + inverter-only | 20.0 [20.0, 20.0] | 16.7 | 100.0 | 0.0 |

The full-history/cross-component condition resolved 233 of 240 identifiable clean
cases correctly. Its paired advantage was 57.1 percentage points over recent-only
cross-component access (95% CI 55.4–58.8) and 43.3 points over historical inverter-only
access (40.8–45.8). The clean-data factorial interaction was 23.3 points (20.8–25.8).
The improvement concerns this diagnostic policy and this episode mix, not general
superiority over existing monitoring systems.

Acute alarm accuracy was 100% for both cross-component conditions: history beyond
24 hours was not necessary for these constructed events. For the longitudinal task,
the recent-only conditions abstained throughout because a one-day view did not support
a temporal comparison. Their high selective accuracy therefore coexisted with low
coverage. Their zero-width intervals reflect identical per-installation outcomes in
this task design, not known population performance.

Five of the ten identifiable episodes per installation are normal/control cases. As
a class-distribution sanity check, always predicting normal would therefore score
50% on this primary endpoint while missing every injected identifiable abnormality.
This is not an added fitted comparison arm. It underlines why the restricted conditions'
abstention and task-level outcomes must accompany the pooled correctness metric.

The full-history/cross-component condition was imperfect. Five clean decline episodes
were classified as normal, one normal day was classified as weather loss, and one normal
day was left unresolved. These failures remain in the archived results. Inverter-only
history sometimes confused weather-related output changes with PV decline.
Here the oracle labels injected mechanisms: a day labelled normal can still experience
natural stochastic weather variation. A weather-loss answer on that control day is an
injection-label disagreement, not necessarily an incorrect description of the measured
weather. Independent review of such cases is needed before treating label error as
engineering diagnostic error.

Under moderate corruption, full-history/cross-component diagnostic accuracy was 97.5%
(95.4–99.2); under severe corruption it was 90.0% (87.1–92.9). The small non-monotonic
change under moderate noise is reported rather than removed. Some noisy observations
cross policy thresholds in either direction. All conditions abstained on all 48
deliberately ambiguous/unavailable cases per stress level. That result covers two
authored abstention mechanisms and is not a general safety or calibration guarantee.

![Clean-data diagnostic accuracy](../reports/research/offline-evaluation/accuracy.png)

![Observation-stress sensitivity](../reports/research/offline-evaluation/robustness.png)

## Live conversational evaluation status

A 24-conversation development pilot with a dated Claude model and two extreme access
conditions is implemented. A model must select one of three approved tools and return
structured text grounded in the restricted receipt. Forced tool use means this tests
selection/reporting, not whether a model independently decides to seek evidence.
Planned measures separate tool selection, valid output structure, label fidelity,
citation-name validity, oracle correctness, usage and latency. Independent prose review
is still needed: a valid citation name does not prove every sentence is supported.

The first execution was rejected for workspace configuration. On 28 September a new
pilot completed 24 conversations and 48 requests, with intended tool selection in
24/24 but strict JSON acceptance in 0/24: all responses used Markdown fences.
A separate post-hoc fence-removal analysis recovered 24/24 receipt-consistent labels,
15/24 valid measurement-name citation sets and 16/24 oracle agreement including
required abstentions. Primary scores remain unchanged. See the full manuscript and
research run index for costs, latency, raw outputs and qualitative limitations.

## Discussion and limitations

The controlled comparison supports an architectural rationale: longitudinal tasks need
historical observations, and weather/load context can disambiguate otherwise similar
inverter observations. It also shows cases where one day is enough. This supports a
task-dependent design argument rather than a claim that more context always helps.

The evaluation is limited by the shared generator/policy authorship, simplified physics,
finite authored mechanisms, threshold-based diagnosis, and dependency-sensitive task
mix. Different policies may perform better with restricted inputs. Same-simulator held-out
seeds do not substitute for unseen mechanisms, independent simulators or real telemetry.
There is no calibration study of numerical probabilities, field causality, user study,
economic validation or comparison with a learned state-of-the-art method. Battery-health,
financial, forecasting and grid-outage features remain demonstrated in the original
demo but are not validated by this narrower comparative study.

Before publication, a domain expert should review the synthetic assumptions and failure
cases; related work should establish the novelty boundary. The next empirical steps
are independently sourced data, additional measurement-fault models, optimized baseline
policies and blinded installer assessment. A physical logger is future work.

## Reproducibility

Protocol: [RESEARCH_PROTOCOL.md](../docs/RESEARCH_PROTOCOL.md).
Authoritative run: [evaluation report](../reports/research/offline-evaluation/REPORT.md).
Sources, configuration, versions, seeds and hashes were archived before evaluation.
The thresholds were not changed after reviewing the development outcomes. Run
`python scripts/run_research_benchmark.py --split evaluation` to create a fresh archive.
No claim of external preregistration is made.
