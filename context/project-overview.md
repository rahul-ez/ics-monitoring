# Project overview

Last updated: 2026-10-14  
Status: scope agreed; baseline reproduction and experiments still require verification.

## Purpose of this file

Read this file at the start of each project session. It records what we are building, the current milestone, the broader roadmap, and the rules that keep our experiments credible. Do not treat planned capabilities as completed work. Update this file when the team explicitly changes the scope or verifies a milestone.

## Project in one paragraph

We are building a software framework for resilient industrial anomaly monitoring around the existing GeCo detector. First, we automatically select detector settings using historical normal operating data and controlled disturbances injected into offline copies, without using real attack labels during calibration. Next, we track which measurements each monitoring check requires and assess which checks remain usable when measurements become unavailable or suspect. Validated alternative checks may preserve partial monitoring; otherwise the system explicitly reports lost coverage. Operating-mode handling and evaluation across different processes are staged extensions.

Working title: **Resilient Industrial Monitoring Through Automatic Calibration and Sensor-Dependency Analysis**.

## Problem and intended users

Industrial monitoring teams may have substantial normal operating history but few representative labelled attacks. Selecting detector settings requires balancing sensitivity, false alarms, computation, and engineering effort. During sensor failure or manipulation, several checks can become unreliable because they share the same input. An absence of alarms can then be misleading.

Our intended users are plant monitoring/security engineers and researchers. We aim to reduce repetitive calibration work and make monitoring limitations visible during disruption. This supports critical-infrastructure resilience through monitoring continuity. Physical service continuity, safety improvements, and downtime reduction require additional evidence.

Suitable processes have aligned measurements, representative normal data, and learnable temporal dependencies between recorded variables. The framework is reusable, but every process needs its own fitted models and calibrated settings. Time-series data alone does not establish suitability.

## Current milestone: calibration on one dataset

**Build and evaluate an end-to-end calibration pipeline before implementing a dashboard or the wider roadmap.**

1. Select one documented HAI release and a manageable subsystem; preserve required input dependencies.
2. Pin the GeCo implementation revision and reproduce its normal fitting and alarm generation.
3. Record actual-versus-predicted behaviour, residuals, configuration, preprocessing, and compute cost.
4. Create separate normal training, calibration, and audit blocks, plus an untouched real-attack test set.
5. Implement bias, drift, and freeze pseudo-events with reproducible metadata.
6. Initially hold `k` fixed and search feasible `S` and `G` settings.
7. Select a stable configuration under a predefined empirical false-alarm budget.
8. Freeze the method and evaluate on held-out real attacks against the reproduced baseline.

The first deliverable is a reproducible experiment and results table. It is not a claim that synthetic calibration is already effective.

Research question: **Do configurations selected using normal data and pseudo-events retain useful detection performance on unseen real attacks?**

## Baseline and proposed additions

GeCo is an existing industrial intrusion detector that learns comprehensible state-transition equations and accumulates prediction deviations. We are extending and evaluating it, not inventing GeCo.

- `k`: equation-search complexity/function length; changing it can require model fitting.
- `S`: threshold scaling.
- `G`: cumulative-deviation behaviour; verify exact semantics and valid ranges in the pinned implementation.

Our proposed additions are the calibration procedure, dependency registry, coverage reporting, and eventually selection among validated alternative checks. Synthetic-anomaly selection, process modelling, and analytical redundancy already exist in prior work; their use alone is not a novelty claim.

## Pseudo-event library

Pseudo-events are modifications of offline data copies. They represent selected observable disturbance patterns, not complete cyberattacks or confirmed malicious intent.

| Stage | Families | Intended use |
| --- | --- | --- |
| First implementation | Additive bias, gradual drift, frozen reading | Calibrate sensitivity and detection delay |
| Resilience extension | Missing blocks, intermittent dropout, complete channel loss | Assess check eligibility and lost coverage |
| Later timing tests | Delay, stale updates, channel misalignment | Stress temporal dependencies |
| Later value tests | Scaling and replay-like sequences | Broaden disturbance diversity |
| Later structured tests | Single-channel inconsistency and coordinated multi-channel changes | Test dependence on related measurements and difficult cases |

Each event records its source block, affected channels, transformation, start, duration, severity, and seed. Severity is grounded in normal-data statistics and documented process constraints. Preserve discrete actuator states and make any out-of-range stress tests explicit. Include weak events and varied durations, not only obvious extreme changes.

Missingness can be identified directly by data-quality checks. Do not count an absent reading as successful GeCo attack detection. Evaluate missingness through retained coverage and detection on the remaining inputs. Expected legitimate operating changes belong in normal stress tests, not automatically in the attack class.

## Calibration and evaluation rules

- Fit models and preprocessing on normal training data only.
- Use separate normal calibration data and its modified copies for parameter selection.
- Reserve an untouched normal audit block for checking the selected configuration.
- Keep real attack labels, event times, and targets out of fitting, feature selection, pseudo-event design, and calibration decisions. Use them for final evaluation.
- Split by chronological blocks or complete runs/events. Do not randomly distribute neighbouring windows from one event across splits.
- Define event matching, alarm aggregation, score weights, and parameter ranges before inspecting final attack results.
- Evaluate false alarms on untouched normal data. Report alarm episodes per day and time in alarm; record the episode merge-gap rule.
- Prefer configurations stable across normal blocks and pseudo-event seeds. Hold out severities, channels, or families where feasible.
- Reuse predictions/residuals only where valid; rerun sequential alarm accumulation for each detector setting.
- Report infeasible alarm budgets and failed transfer honestly. Observed alarm rates are not guarantees of future rates.
- If the test set informs a redesign, it has become development data; obtain a new held-out evaluation or disclose that limitation.

Selection principle: maximize balanced pseudo-event detection utility, accounting for delay, subject to the empirical normal-data alarm budget. The budget and score weights remain decisions to document. Synthetic labels are allowed: the precise claim is **no real attack labels used during calibration**.

## Broader scope and priority

| Capability | Commitment |
| --- | --- |
| Baseline reproduction and automatic calibration | Current milestone |
| Dependency tracking and coverage reporting under known sensor degradation | Core resilience milestone after calibration |
| Validated alternatives for selected checks | Next priority where sufficient redundancy exists |
| Inference of suspect sensors from ambiguous evidence | Harder extension; assess separately from known degradation |
| Portability to a second dataset/process | Planned extension after the core pipeline works |
| Two or three documented operating modes | Conditional extension if the chosen data supports meaningful modes |
| Responsive simulation of service continuity or recovery | Optional extension; required for physical-resilience claims |
| Attack-pattern characterization | Optional diagnostic feature; allow unknown and mixed patterns |

### Dependency-aware monitoring

Store each check's target, all required inputs (including historical target values), supported conditions, calibrated settings, and validation results. When an input is missing, invalidate dependent checks. A large residual alone does not identify which sensor is faulty or manipulated.

Start with controlled degradation where the affected channel is known. Keep original hidden readings available only to the evaluator. Later evaluate inferred suspect-channel handling separately, including localization errors.

Fallbacks must be separately fitted and validated. Do not simply remove a term from an equation. If the target sensor itself is absent, a prediction is an estimate; it cannot be compared with that missing observation to verify the target. Never count reconstructed readings as independent corroboration.

Report support per monitored target:

- **Supported:** a validated check has acceptable available inputs under supported conditions; this is not proof of safety or uncompromised data.
- **Degraded:** useful checks remain, but some coverage or independent evidence has been lost.
- **Unavailable:** no validated eligible check remains, or conditions are unsupported.

Check eligibility is not a detection guarantee. Measure actual retained detection, alternative-model error, and misleading support declarations under controlled tests. Validate detector-state handling when switching checks.

### Operating modes and portability

Prefer documented operating states over arbitrary clustering. Begin with separate alarm calibration before fitting separate models. Validate transitions, unknown modes, and cumulative detector-state handling. Do not suppress all transition alarms or automatically retrain on suspicious data.

For portability, reuse the procedure and evaluation rules while refitting on the second process's normal data. Record changes to adapters, constraints, and manual configuration effort. Multiple subsystems of one testbed are weaker evidence than independent processes. Freeze methodological choices before the second evaluation.

## Dataset plan

These are candidates, not confirmation that data has been acquired, processed, or found suitable.

| Dataset | Role | Access / limitation |
| --- | --- | --- |
| HAI | First calibration and attack evaluation | Public repository; choose and pin one release. Inspect technical manual and attack metadata. Mode labels are not assumed available. |
| SWaT | Independent second attack benchmark | Request from SUTD iTrust using institutional access; observe its usage terms. |
| BATADAL | Optional lightweight water benchmark | Public downloads; hourly sampling limits fast-event analysis and some development labels are partial. |
| Tennessee Eastman, Rieth release | Optional chemical-process fault evaluation | Public dataset; fault categories are not cyberattack labels. |

Do not train fault-versus-attack attribution by assigning one plant/dataset to each class: this can learn dataset identity. Static recordings support monitoring experiments; a responsive simulator is needed to test consequences of physical interventions.

## Baselines and evidence

Compare reproduced GeCo, automatically calibrated GeCo, and later the framework with dependency tracking/alternatives. Include disabling affected checks and simple imputation as relevant alternatives. If modes are implemented, compare against one global configuration.

Report event recall, missed events, detection delay, false-alarm episodes, time in alarm, retained coverage, actual detection under degradation, estimation error, compute cost, and manual effort. Repeat controlled disturbances across seeds/blocks. Do not treat every correlated timestamp as an independent experimental replicate.

Business hypotheses: less calibration effort and lower alarm-review workload at comparable detection quality. Measure labour time, runtime, integration and maintenance costs before claiming savings. Earlier illustrative rupee figures were hypothetical, not industry evidence or project results.

## Boundaries and current unknowns

- No autonomous live-plant control, universal applicability claim, or guarantee of safety.
- Signal patterns such as bias, freeze, and replay-like repetition do not establish attacker intent. Stronger attribution requires independent evidence.
- No unrestricted online adaptation, LLM dependency, or new detector architecture in the current milestone.
- Dataset release/subsystem, pinned code revision, compute budget, alarm budget, score weights, exact splits, and achieved baseline results still need to be recorded.
- Source checkouts or generated proposals in this workspace do not establish that experiments have succeeded.

## Key references and shared artifacts

- [GeCo paper and official presentation](https://www.usenix.org/conference/usenixsecurity25/presentation/wolsing)
- [GeCo reproducibility artifact](https://zenodo.org/records/15120036)
- [HAI data and manuals](https://github.com/icsdataset/hai)
- [SWaT dataset description](https://www.sutd.edu.sg/itrust/itrust-labs/datasets/dataset-characteristics/swat/)
- [iTrust dataset request](https://www.sutd.edu.sg/itrust/request-for-datasets/)
- [BATADAL data](https://www.batadal.net/data.html)
- [Tennessee Eastman data](https://doi.org/10.7910/DVN/6C3JR1)
- [TSADAMS](https://arxiv.org/abs/2210.01078) and [AutoTSAD](https://www.vldb.org/pvldb/vol17/p2987-schmidl.pdf): related synthetic-anomaly model-selection work.
- [NIST resilience framework](https://csrc.nist.gov/pubs/sp/800/160/v2/r1/final)
- `output/pdf/Resilient_Industrial_Monitoring_Project_Proposal.pdf`: earlier full proposal. This overview records subsequent scope clarification; neither document is experimental evidence.

## Session handoff

At the start, read this file, applicable repository instructions, and the latest verified experiment notes. Before implementing a new feature, check its priority above. At the end, record completed work, commands/configurations needed to reproduce it, results, unresolved issues, and the next concrete action. Update this overview for scope changes; keep detailed experiment logs separate.
