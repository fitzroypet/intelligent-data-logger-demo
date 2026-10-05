# A reproducible methodology for evidence-grounded conversational diagnostics of solar PV–battery systems: implementation and synthetic evaluation

Oyewale, D.O.¹ and Meyer-Petgrave, F.¹

¹Petgrave.io Technologies Ltd, Nigeria

## Abstract

Conversational diagnostics for solar PV–battery installations require reproducible methods to constrain diagnostic access, preserve engineering evidence, expose uncertainty and separately evaluate diagnostic and conversational outputs. This paper presents an implemented methodology separating telemetry preparation, controlled historical and cross-component access, deterministic diagnostic tools, structured evidence receipts, conversational reporting and separate scoring against evaluation-only reference labels. A proposed field-acquisition workflow maps observations to inverter interfaces, battery monitoring, energy meters, environmental sensors and installation records; no field data were collected.

A controlled synthetic evaluation comprises twelve matched episodes for each of 24 evaluation installations, separate from eight development installations. A 2 × 2 design varies historical access (60 days versus 24 hours) and measurement access (cross-component versus inverter-only). Three observation-quality levels produce 3,456 paired predictions under a shared deterministic policy. With clean observations, full historical and cross-component access resolved 233/240 identifiable cases (97.1%; 95% installation-cluster bootstrap interval: 95.4–98.8%), compared with 53.8% for historical inverter-only access and 40.0% for recent cross-component access. Severe corruption reduced full-access accuracy to 90.0%; restricted conditions frequently abstained when evidence was insufficient.

A separate 24-conversation Claude development pilot selected the intended tool throughout but failed the prespecified strict JSON output contract in every response. Post-hoc removal of Markdown fences recovered 24 receipt-consistent labels; 15 responses satisfied the predefined measurement-name citation rule. The evaluation distinguishes evidence-access limitations, diagnostic outcomes, abstention and conversational-interface failures. The contribution is a reproducible methodology, reference implementation and controlled worked evaluation. Shared simulator–policy assumptions and the absence of field validation limit generalization. Application to real installations requires verified device-to-schema mappings, independent fault references and a new field evaluation protocol.

Keywords: solar diagnostics, reproducible methodology, evidence grounding, conversational diagnostics, synthetic evaluation

## 1. Introduction

A solar installation combines photovoltaic generation, conversion, storage, demand and grid exchange. A change in one observed signal can have several explanations: reduced output may reflect lower irradiance, conversion loss, or a changing operating regime. A useful diagnostic interface must therefore identify which measurements support its explanation and when the available record cannot resolve the question. This motivates a persistent installation record and a conversational layer that reports engineering evidence in accessible language.

Established photovoltaic modelling already represents environmental effects on output [1,2], and degradation analysis already exploits longitudinal records while addressing confounding effects [3]. Language-model tool use is also established [4,5]. The contribution claimed here is narrower than inventing these components: a reproducible methodology that links telemetry preparation and controlled information access to auditable diagnostic receipts, conversational reporting and separate evaluation of each layer. Its implementation and synthetic worked evaluation examine how access to history and component measurements affects task resolution. We distinguish the deterministic diagnostic result from the language model's ability to retrieve and report that result.

The intended application is evidence-supported interpretation for owners and installers, including settings relevant to solar adoption in Nigeria. However, the present study contains no Nigerian field measurements, hardware prototype, installer assessment or deployment trial. The methodology is demonstrated through an explicitly synthetic information-access study. The proposed field-acquisition pathway is a design for subsequent implementation, not a completed deployment. The research questions are: (RQ1) how does historical access affect correct resolution of identifiable cases; (RQ2) how does cross-component access affect resolution and false positives; and (RQ3) how sensitive are these outcomes to observation noise and missingness? A separate development pilot examines tool selection, structured-output compliance and evidence-reference validity.

## 2. Related work and contribution boundary

The Sandia photovoltaic array performance model describes electrical, thermal and optical behaviour for performance prediction and measurement comparison [1]. The pvlib python software provides reusable solar-energy modelling implementations [2]. These works establish a substantial modelling foundation; our deliberately simplified project-authored generator does not replace their physical detail or inherit their validation. It provides matched interventions for an information-access experiment, with physical consistency checks and disclosed assumptions.

Jordan et al. [3] developed a degradation methodology addressing operational confounders using clear-sky irradiance and year-over-year analysis, demonstrated on a fleet of 486 PV systems. Accordingly, history-dependent PV diagnosis and weather normalization are not novel claims of this paper. Our 60-day synthetic decline task is a controlled signature test, not an annual field degradation estimator. No performance comparison with RdTools is made.

ReAct combines language-model reasoning and actions to obtain external information [4]. Toolformer studies learning to select and use APIs [5]. Our system instead uses an existing tool-capable model with a small, fixed engineering-tool interface. The pilot forces one tool call and then requests a structured explanation; it does not reproduce those training methods or establish autonomous diagnostic reasoning. The computational boundary keeps engineering quantities in deterministic code and exposes their provenance to the conversational layer.

Selective classification illustrates why performance on answered cases must be interpreted together with coverage [6]. We apply that distinction descriptively to a deterministic policy with explicit unknown outcomes, without claiming the statistical risk guarantees of selective-classification methods. Our methodological contribution is the combination of explicit data-access boundaries, inspectable evidence receipts, reproducible information-access evaluation and separate assessment of conversational reporting. The software is a reference implementation; the synthetic study and failure-transparent pilot demonstrate its use rather than establish field effectiveness. This targeted comparison of primary sources does not establish an exhaustive literature gap or a first-of-its-kind system.

## 3. Proposed methodology and worked evaluation

### 3.1 Architecture and evidence boundary

The pipeline separates clean physical trajectories, corrupted observations, condition-specific access, deterministic diagnosis and oracle-based evaluation. The oracle stores injected causes and simulation parameters solely for scoring. The diagnostic function receives an allowed telemetry view, legitimate nameplate information, a task and fixed thresholds; it has no file access or simulator import. It produces a label, explanation of the decision, measurement dictionary, available columns, time window and thresholds. No scenario identifier, seed, latent state, oracle label or future row is supplied to it.

The conversational layer selects an approved tool and receives its receipt rather than raw time series. The operational dashboard displays the latest complete stored synthetic snapshot and supports investigations. A separate public experiment explorer presents archived evidence and comparative results. Neither a website interaction nor an interface screenshot is counted as a research trial. Figure 1 summarizes the evaluation boundary.

![Figure 1. Separation of observed evidence, diagnostic access and evaluation-only ground truth.](figures/architecture.png)

### 3.2 Reusable workflow and implementation boundary

The proposed method has six stages. First, define each diagnostic task and its required measurements, units, history and legitimate installation metadata. Second, retain raw observations and produce a timestamp-aligned analysis view with explicit missing-data flags. Third, restrict that view to the measurements and history available at the query time. Fourth, run deterministic tools that return a diagnostic label or an explicit unknown result with supporting measurements, time windows and assumptions. Fifth, supply these receipts to the conversational layer and check its output format, label fidelity and cited measurement identifiers. Sixth, score diagnosis against an independently maintained reference and report correctness together with coverage, false positives and abstention. Raw model responses and failed checks remain part of the record.

The repository implements synthetic generation, restricted telemetry views, deterministic policies, receipt production, separate model-output scoring and archived reporting. It does not implement or validate a field gateway or device-specific acquisition adapters. Receipt inspection and output checking make failures visible; the completed pilot does not demonstrate an output contract that always succeeds. New tools, schemas or parser rules would require versioned implementation and fresh evaluation.

To reproduce the worked example, a researcher installs the repository's recorded dependencies, examines the frozen protocol and development cases, and runs the offline benchmark with the evaluation split. The archive records configuration, source hashes, installation seeds, raw predictions and derived metrics. The optional live runner has a planning mode before paid execution and records model identity, prompts, receipts, usage and raw responses. Development and evaluation installations remain separate. Replication under the same generator assesses reproducibility within its assumptions; transferring the method to another generator or real data is a separate test.

### 3.3 Proposed field-data acquisition and integration

No field measurements were collected in this study. A future implementation would obtain operational data from consenting owners or operators of residential or small-commercial PV–battery installations, potentially recruited through installer or maintenance partners in Nigeria. No site, recruitment agreement or data-access partnership is claimed here. Existing owner-authorized monitoring exports could also supply historical records where their channels, sampling intervals and provenance are adequate. Table 1 maps the synthetic observations to proposed field sources; the mapping is a design specification rather than evidence of device compatibility.

Table 1. Proposed field sources and their relationship to the synthetic study.

| Observation or record | Proposed acquisition source | Mapping and qualification |
|---|---|---|
| PV AC output (W), inverter temperature (°C), state and alarm | Supported inverter monitoring interface or owner-authorized export | Map to PV AC power, inverter temperature and alarm fields; verify that output represents PV generation rather than combined battery/grid flows |
| Irradiance (W/m²) and ambient temperature (°C) | On-site plane-of-array irradiance sensor and ambient temperature sensor | Map to irradiance and ambient-temperature inputs; record orientation, siting and calibration; module temperature is an optional additional measurement, not an interchangeable ambient-temperature input |
| Battery SOC (%) and charge/discharge power (W) | Supported BMS, battery inverter interface or dedicated metering | Map to battery SOC and power channels; identify AC/DC measurement boundary and conversion assumptions; SOC is a reported estimate |
| Served load and grid import/export (W) | Appropriately installed load and bidirectional grid meters | Map to load and separate grid-flow channels; verify meter location, phase aggregation and sign conventions |
| Ratings, commissioning and maintenance history | Equipment specifications, commissioning sheets and dated service records | Supply legitimate metadata and configuration changes; never infer nameplate ratings from evaluation fault labels |
| Confirmed faults and event intervals | Technician inspection and maintenance records, with supporting observations | Maintain independent evaluation labels; distinguish confirmed cause, suspected cause and unresolved event |

Where equipment supports it, a gateway could read documented registers through a compatible Modbus interface; SunSpec defines information models for inverters, batteries and meters [7]. Manufacturer-specific mappings or authorized exports would need separate adapters. The proposal does not assume that every inverter exposes all required fields, that every BMS is accessible, or that communications support has been tested. The gateway would buffer readings locally during connectivity loss and transfer records to the persistent store when a connection is available. This monitoring pathway would use read-only access and would not issue inverter-control commands.

The proposed acquisition procedure would preserve device timestamps and gateway receipt times, normalize timestamps to UTC and retain the site's time zone. Each record would carry installation and device identifiers, channel, value, unit, measurement boundary and quality flag. Raw readings and source files would remain immutable; a versioned transformation would standardize units, reconcile duplicate or out-of-order records and mark missing or stale observations. Sensor selection, calibration, maintenance and irradiance-data quality assessment should be informed by established solar-resource measurement guidance [8]. No monitoring-standard compliance is claimed for this prototype.

For a first field pilot, one-minute polling where supported is a proposed starting point, subject to device update rates and diagnostic time scales. Analysis could aggregate valid numeric readings to the benchmark's 15-minute intervals using time-weighted means and explicit coverage, while retaining native-resolution data and separate event/alarm timestamps. Cumulative energy readings would require checked interval differences rather than averaging counters. Short alarms must not disappear through numeric averaging, and gaps must not be filled with zeros. This cadence is a proposed design choice, not a field-tested optimum. Clock drift, vendor delays, meter uncertainty, clipping, sensor fouling and communication outages would need explicit checks. Any imputation or resampling rule would be fixed on development data and documented before evaluation.

Field diagnostic references would be assembled independently of model predictions from inspection, maintenance evidence and, where available, post-repair observations. A generic alarm alone would not establish its physical cause. Reviewers would record supporting evidence, event timing and label uncertainty; unresolved events would remain unresolved, with their frequency reported. Future experiments would separate installations for development and evaluation, prevent overlapping histories from leaking across splits, set thresholds on development data only, and report uncertainty at the installation level. Longer-term degradation claims would require an appropriately longer observation period than the present 60-day signature test. Site permission, access controls and removal of identifying household information would precede data sharing or transfer to an external model.

Synthetic and field observations would therefore enter the same conceptual evidence pipeline, but substituting real data is not a validated drop-in operation. Device semantics, sensor availability, time alignment and label reliability must first be verified. A new field protocol would specify these mappings, recruitment and sampling, comparison methods, independent technical review and installer assessment before making claims of diagnostic effectiveness or usefulness.

### 3.4 Simulator and sampling

Eight development installations (seeds 100–107) and 24 evaluation installations (1000–1023) use disjoint random seeds. Each installation contributes twelve matched episodes, each with 60 days at 15-minute cadence (5,760 timestamps). Evaluation therefore contains 288 episodes and 1,658,880 timestamp rows, with 24 installation-level sampling units. Matched episodes reuse installation parameters and underlying stochastic conditions to isolate interventions; they are not 288 independent installations.

PV rating varies uniformly from 3 to 9 kWp; inverter rating derives from a PV/inverter ratio of 1.05–1.45. Nominal battery capacity varies from 5 to 15 kWh, with 90% represented as usable capacity. Conversion efficiency varies from 0.90 to 0.98 and charge/discharge efficiencies from 0.91 to 0.98. Temperature coefficients vary from 0.003 to 0.005 per degree Celsius. Demand scale, initial battery energy, power limits, cloud variation, intervention severity and alarm timing also vary. These are design assumptions, not fitted distributions for Nigerian installations.

The generator uses a clipped sinusoidal daylight profile, daily cloud variation and autocorrelated short-term cloud perturbations. PV power depends on irradiance, temperature, conversion efficiency and the injected performance factor, capped at inverter rating. Fault effects precede dispatch. For each interval, PV and battery discharge plus grid imports balance served load, battery charging and exports. Battery energy evolves using interval duration and charge/discharge efficiencies. Independent numerical checks verify AC energy balance, battery transitions, SOC and power limits before telemetry corruption. All 288 clean evaluation trajectories passed these checks. This establishes internal consistency, not validation against a physical plant.

The twelve episodes comprise three daily-output cases (normal, weather attenuation and conversion loss), four alarm cases (none, overload, thermal stress and unexplained), four longitudinal cases (stable, declining conversion performance, declining irradiance and static low efficiency), and one unavailable-telemetry case. Five of the ten identifiable episodes are normal/control cases. Unexplained alarms and unavailable telemetry require abstention. Generic alarms do not disclose their causes. The comparative study does not evaluate the original demonstration's battery-health, financial or islanding functions.

### 3.5 Information-access conditions and diagnostic policy

Table 2 defines a matched 2 × 2 design. All conditions share the same questions, nameplate ratings, query times and deterministic policy. Cross-component views contain inverter AC output, temperature and alarm, plus irradiance, ambient temperature, load, battery SOC, battery charge/discharge and grid import/export. Inverter-only views contain timestamp and the three inverter channels. An explicit allowlist and timestamp filter enforce access before diagnosis.

Table 2. Matched information-access conditions.

| Condition | Historical access | Measurement access |
|---|---|---|
| Full cross-component | All 60 days to query time | Inverter plus weather, load, battery and grid |
| Recent cross-component | Last 24 hours | Same cross-component channels |
| Full inverter-only | All 60 days to query time | AC output, inverter temperature and alarm |
| Recent inverter-only | Last 24 hours | Same inverter-only channels |

The daily-output tool examines 09:00–16:00 observations and, when available, compares them with preceding days. Cross-component normalization adjusts nameplate output for measured irradiance and temperature, excludes irradiance at or below 200 W/m² and near-clipping output, and requires sufficient valid observations. A relative normalized loss above 15% supports conversion loss; irradiance loss above 20% with preserved normalized performance supports weather loss. Without a historical baseline, sufficiently low absolute normalized performance can support conversion loss; otherwise the tool can abstain.

Alarm diagnosis checks for above-rating load before the generic alarm, using at least 30 minutes of overload as its criterion; alternatively, inverter temperature at or above 75°C supports a thermal explanation. An unexplained alarm remains unknown. Longitudinal diagnosis requires at least 14 valid days, compares early and late daily summaries, and uses a 5% decline threshold. It normalizes for weather only when those channels are available. Required-input coverage must be at least 80%. These policy-specific thresholds were internally frozen before the evaluation run; the protocol was not externally preregistered.

The cross-component bundle varies weather and load availability together with other channels. Thus this design estimates the effect of the bundle under this policy, not separate causal contributions of every battery or grid measurement. These are information ablations, not independently optimized competitor algorithms. No manual-dashboard or installer baseline was simulated.

### 3.6 Observation stress, outcomes and uncertainty

Moderate stress adds independent multiplicative Gaussian numeric-meter noise with 3% standard deviation and 1% missingness; severe stress uses 8% noise and 5% missingness. All four access conditions receive the same corrupted realization. Missingness is independent across numeric readings and does not reproduce every real communication or sensor fault. Corrupted readings are not expected to satisfy exact physical balance. Four conditions and three stress levels yield 3,456 predictions; stress levels remain separate in analysis.

The primary endpoint is correct diagnostic label on ten identifiable cases per installation. Unknown on such a case counts as unresolved. Coverage is the fraction of all twelve cases receiving a non-unknown label. Selective accuracy is correctness among non-unknown answers, averaged within installations. We also report abnormal predictions on five normal/control cases and correct abstention on the two ambiguous/unavailable cases. Each metric is computed per installation and then averaged; 95% percentile intervals use 2,000 whole-installation bootstrap draws with a fixed seed. Paired contrasts use the same draws. Intervals describe within-simulator variability, not field performance; no formal significance test is claimed.

### 3.7 Live-model development pilot

The frozen live protocol uses seed 100, all twelve episodes and two extreme access conditions: full cross-component and recent inverter-only. Claude Sonnet 4.5 (claude-sonnet-4-5-20250929) operates at temperature zero with at most 700 output tokens per request, two requests per conversation, no automatic retries and a USD 3 reservation limit. The first request forces selection of one of three tools; the second requests only a JSON object containing label, explanation and cited measurement names. The model receives no oracle labels. A total of 24 conversations and 48 requests completed on 28 September 2026.

Primary checks retain the original strict JSON parser and separately record tool selection, label fidelity, oracle agreement, citation-name validity and nonempty explanation. After observing fenced responses, a supplementary sensitivity analysis removed exactly one enclosing Markdown fence and reapplied the same scorer. This was post-hoc and exploratory. It did not replace primary results or trigger additional generation. Earlier workspace-authentication and connection failures remain archived. Qualitative assistant inspection of prose is distinguished from independent human assessment.

## 4. Results of the synthetic worked evaluation

### 4.1 Clean-data information access

Table 3 reports clean-data results. Full historical and cross-component access resolved 233 of 240 identifiable cases correctly (97.1%; 95% interval 95.4–98.8%). Its paired difference was 57.1 percentage points versus recent cross-component access (55.4–58.8) and 43.3 points versus full inverter-only access (40.8–45.8). The factorial interaction was 23.3 points (20.8–25.8). These differences concern the fixed policy and authored task mix.

Table 3. Clean-data outcomes (%); 24 installations, 240 identifiable and 48 abstention-required cases per condition. Intervals are installation-cluster bootstrap intervals.

| Access condition | Correct diagnosis [95% interval] | Coverage | Selective accuracy | False positives |
|---|---:|---:|---:|---:|
| Full cross-component | 97.1 [95.4, 98.8] | 83.0 | 97.5 | 0.8 |
| Full inverter-only | 53.8 [51.3, 56.2] | 58.7 | 76.4 | 19.2 |
| Recent cross-component | 40.0 [40.0, 40.0] | 33.3 | 100.0 | 0.0 |
| Recent inverter-only | 20.0 [20.0, 20.0] | 16.7 | 100.0 | 0.0 |

Acute alarm accuracy was 100% for both cross-component conditions: extended history was unnecessary for these constructed events. Recent-only conditions abstained throughout the longitudinal task because one day did not meet the temporal evidence requirement. Their perfect selective accuracy coexisted with low coverage. Zero-width intervals reflect identical simulated installation scores, not certainty about a population. Always predicting normal would score 50% on the primary endpoint because five of ten identifiable cases are controls, while missing every identifiable abnormal case. This sanity check emphasizes task-level and coverage reporting rather than supplying a fitted comparator.

The full condition missed five gradual declines, classified one normal day as weather loss and left one normal day unresolved. These seven failures remain included. Inverter-only history sometimes confused weather-related output change with PV decline. A control-day weather-loss response also illustrates a label limitation: natural stochastic weather variation can occur when no weather intervention was injected. An injection-label disagreement therefore does not always imply an incorrect description of observed conditions.

![Figure 2. Clean-data correct diagnostic labels on identifiable cases under four information-access conditions.](../reports/research/offline-evaluation/accuracy.png)

### 4.2 Observation stress and abstention

Full cross-component accuracy was 97.5% under moderate corruption (95.4–99.2%) and 90.0% under severe corruption (87.1–92.9%). The slight increase under moderate noise is retained: individual threshold crossings can help or harm label agreement. It is not evidence that noise improves diagnosis generally. All conditions abstained on all 48 deliberately ambiguous/unavailable cases per stress level. This covers two authored mechanisms, not general uncertainty calibration or a safety guarantee.

![Figure 3. Accuracy under clean, moderate and severe observation corruption; conditions share each corrupted realization.](../reports/research/offline-evaluation/robustness.png)

### 4.3 Conversational pilot and output-contract failures

All 24 conversations completed, and the intended tool was selected in every case. However, every final answer enclosed its JSON in Markdown code fences. The frozen strict parser therefore accepted 0/24 outputs, and downstream primary structured checks received no credit. Completion is consequently not equivalent to successful end-to-end operation.

Table 4. Live development pilot: primary strict scores and explicitly post-hoc fence-removal scores. Denominator is 24 conversations throughout.

| Check | Primary strict evaluation | Post-hoc fence removal |
|---|---:|---:|
| Intended tool selected | 24/24 | Not re-evaluated |
| JSON accepted | 0/24 | 24/24 |
| Label matches tool receipt | 0/24 | 24/24 |
| Label matches evaluation oracle | 0/24 | 16/24 |
| All citations are receipt measurement names | 0/24 | 15/24 |
| Nonempty explanation parsed | 0/24 | 24/24 |

After fence removal, full cross-component labels matched the oracle in 12/12 conversations and recent inverter-only labels in 4/12. These counts include abstention-required cases and are not the offline primary endpoint. Nine responses cited at least one telemetry column, threshold or receipt field outside the allowed measurement-name dictionary. A string appearing elsewhere in a receipt did not satisfy the prespecified citation rule.

Estimated token cost was USD 0.2130, using the protocol's rates; this is not an independently reconciled invoice. Median recorded conversation duration was 6.263 seconds (range 4.184–37.639). Qualitative inspection flagged explanations that generalized zero alarm samples to all telemetry being normal, described all channels as examined, or treated a channel excluded by design as missing observed data. These are examples for independent review, not a blinded or quantitatively validated prose-quality assessment. Numerical fidelity throughout explanations remains unevaluated.

## 5. Discussion

The worked evaluation demonstrates how the methodology can test a task-dependent architectural argument. A temporal comparison requires history, while weather and load context can separate mechanisms that look similar in inverter output. The successful acute cases show that longer history is not always needed. The aggregate improvement should therefore be interpreted alongside the deliberate selection of history-dependent and context-dependent tasks, the normal-case proportion and the restricted conditions' abstentions.

The live pilot identifies a different engineering problem. A model can select the right tool and preserve its label while violating the machine-readable output contract and citation schema. A polished interface alone would conceal this distinction. Strict parsing, validation of cited identifiers, preservation of raw outputs and explicit separation of primary and exploratory analyses make these failures inspectable. Future schema-constrained generation or parser revisions require a new protocol and fresh evaluation rather than retroactive success claims for this run.

The public offline dashboard replays precomputed deterministic answers and synthetic charts; it does not execute Claude conversations. The public explorer communicates two evidence levels: the original single-installation M1–M6 feasibility demonstration and the separate multi-installation access study. It includes the outage trace and raw evidence links, while the local dashboard supports conversation. This separation permits a public, static demonstration without distributing API credentials or implying that a recorded page is connected to a live solar system. Usability and the effect of explanations on installer decisions have not been measured.

Several limitations constrain the findings. The simulator and policy share authorship and broad mechanisms, creating inverse-model optimism. Disjoint seeds test stochastic variation within the same generator rather than unseen fault families or independent physics. The simplified daylight, temperature and dispatch models are not validated against field data; corruption covers only limited noise and missingness mechanisms. Recent-only policy paths are intentionally conservative, and optimized alternatives could perform better. Oracle labels identify injected mechanisms rather than universally adjudicated engineering diagnoses. The pilot has one development seed, one model pass and forced tool use; it does not test autonomous evidence seeking, multi-turn user interaction, expert-rated usefulness or model generalization. No hardware reliability, financial benefit, customer responsibility or real-world battery-health claim follows.

## 6. Conclusion

This paper presents an implemented methodology for evidence-grounded conversational solar diagnostics, with a proposed field-data acquisition pathway and a reproducible synthetic worked evaluation. The method separates measurement access, deterministic diagnosis, evidence receipts, conversational reporting and separate scoring against evaluation-only reference labels. Under the shared policy, full historical and cross-component access resolved 233/240 identifiable clean cases; severe observation corruption reduced accuracy to 90.0%. The development pilot selected the intended tools but failed strict output formatting and exposed citation limitations. These results demonstrate the evaluation procedure and identify implementation weaknesses; they do not establish field accuracy. Researchers extending the method should verify device-to-schema mappings, preserve independent fault references and conduct a newly specified evaluation on independent data. Physical acquisition, domain review and installer assessment remain future work.

## Data and code availability

The repository contains the internally frozen protocol, source snapshots, seed lists, manifests, raw predictions, receipts, failure tables and plot exports: https://github.com/Engr-Daniel/intelligent-data-logger-demo. Offline evaluation archive: offline-evaluation. Completed live archive: live-pilot. The separate post-hoc analysis is live-pilot-format-sensitivity. Simulated calendar dates are not field-observation dates. A public evidence explorer is available at https://Engr-Daniel.github.io/intelligent-data-logger-demo/; comparative results are at the same address followed by research.html. The public offline dashboard is available at https://engr-daniel.github.io/intelligent-data-logger-demo/dashboard/. Generated static-site provenance identifies the source archives and asset hashes. The field-acquisition proposal was added during manuscript revision after the synthetic evaluation; it is not part of the frozen v1 experimental protocol.

## References

[1] King, D.L., Boyson, W.E. and Kratochvil, J.A. (2004). Photovoltaic array performance model. Sandia National Laboratories, SAND2004-3535. https://doi.org/10.2172/919131.

[2] Holmgren, W.F., Hansen, C.W. and Mikofski, M.A. (2018). pvlib python: a python package for modeling solar energy systems. Journal of Open Source Software, 3(29), 884. https://doi.org/10.21105/joss.00884.

[3] Jordan, D., Deline, C., Kurtz, S., Kimball, G. and Anderson, M. (2018). Robust PV degradation methodology and application. IEEE Journal of Photovoltaics, 8(2), 525–531. https://doi.org/10.1109/JPHOTOV.2017.2779779.

[4] Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K. and Cao, Y. (2023). ReAct: Synergizing reasoning and acting in language models. International Conference on Learning Representations. https://arxiv.org/abs/2210.03629.

[5] Schick, T., Dwivedi-Yu, J., Dessì, R., Raileanu, R., Lomeli, M., Zettlemoyer, L., Cancedda, N. and Scialom, T. (2023). Toolformer: Language models can teach themselves to use tools. arXiv:2302.04761. https://doi.org/10.48550/arXiv.2302.04761.

[6] Geifman, Y. and El-Yaniv, R. (2017). Selective classification for deep neural networks. Advances in Neural Information Processing Systems, 30. https://papers.neurips.cc/paper_files/paper/2017/hash/4a8423d5e91fda00bb7e46540e2b0cf1-Abstract.html.

[7] SunSpec Alliance (2018). SunSpec Information Model Reference. https://sunspec.org/sunspec-information-model-reference-sunspec-alliance/ (accessed 30 September 2026).

[8] Sengupta, M., Habte, A., Wilbert, S., Gueymard, C., Remund, J., Lorenz, E., van Sark, W. and Jensen, A.R. (eds.) (2024). Best Practices Handbook for the Collection and Use of Solar Resource Data for Solar Energy Applications: Fourth Edition. National Renewable Energy Laboratory, NREL/TP-5D00-88300. https://doi.org/10.2172/2448063.
