# Build Plan

## Core Principle

Build the industrial calibration product in verifiable stages: approved normal data -> validated dataset -> reproduced GeCo baseline -> offline pseudo-events -> calibrated configuration -> exportable detector -> held-out evaluation. Then add dependency-aware monitoring and its operator view. Verify scientific behaviour before presenting it through a UI.

This plan follows `project-overview.md` and `architecture.md`. All features below are **planned**, not implemented. The first milestone ends at Phase 6. Phases 7-8 and Phase N complete the scoped monitoring product. The research extensions are conditional and are not required to finish the first milestone.

Every numbered feature uses the same structure: Goal, Implementation, Inputs / Outputs, and Verification. Unresolved dataset versions, parameter ranges, budgets, durations, tolerances and numerical weights must be resolved in recorded experiment decisions before the relevant execution stage. Draft configs may contain unresolved values; runnable experiments must reject them.

---

## Phase 1 - Foundation

Establish the minimal package, validated configuration, shared contracts and experiment provenance. Do not build empty future modules merely to populate the target architecture tree.

### 01 Repository, Package and Verified Environment

**Goal:** Create a reproducible foundation without disturbing existing research artifacts.

**Implementation:**
- Add `pyproject.toml`, `src/resilient_monitoring/`, `configs/`, `tests/` and the artifact/data directories needed for the first milestone, following `architecture.md`.
- Verify the initial Python compatibility target against the selected GeCo source; record the tested environment and generate `requirements.lock` after compatibility is established.
- Add ignore rules for raw recordings, large generated artifacts, local environments and secrets. Preserve existing `work/`, proposal outputs and user changes.

**Inputs / Outputs:**
- Inputs: project context files and reviewed GeCo source.
- Outputs: importable package, tested installation procedure, dependency lock and ignore rules.

**Verification:**
- Install in a clean environment and import the package and selected GeCo integration dependencies. Record actual runtime/platform versions; verify restricted data is excluded from version-control candidates.

---

### 02 Validated Experiment Configuration

**Goal:** Make every consequential experiment choice explicit.

**Implementation:**
- Implement `config.py` with typed JSON configuration validation, unknown-field rejection and version handling.
- Define dataset/release, channel selection, splits, fixed `k`, candidate `S/G` settings, event profile, seeds, alarm budget, score rules, resource bounds and warm-up/reset policies.
- Distinguish draft configurations from runnable configurations; reject unresolved required values and invalid combinations before computation.

**Inputs / Outputs:**
- Input: dataset and experiment JSON files.
- Output: validated resolved configuration with an immutable identity/hash.

**Verification:**
- Test valid configuration loading and rejection of unknown keys, invalid types, missing budgets, invalid ranges and unsupported schema versions. Check that changing a scientific setting changes configuration identity.

---

### 03 Shared Contracts and Failure States

**Goal:** Establish consistent observations, events, checks and outputs across modules.

**Implementation:**
- Implement `contracts.py` for canonical dataset metadata, split manifests, pseudo-event specifications, check registry entries, predictions, selection results and run manifests.
- Represent missing observations and unavailable decisions explicitly. Separate quality status, anomaly status and monitoring coverage.
- Include schema versions, reason codes and failure outcomes such as invalid data, fit failure and no feasible configuration.

**Inputs / Outputs:**
- Inputs: the data contracts in `architecture.md`.
- Outputs: validated serializable contracts shared by all later features.

**Verification:**
- Round-trip representative contracts and reject inconsistent dependencies, invalid intervals and unavailable decisions represented as normal. Test that observation contracts reject annotation fields.

---

### 04 Artifact Provenance and Verification Harness

**Goal:** Make every later experiment traceable and protect completed outputs.

**Implementation:**
- Implement `artifacts/manifests.py`, `hashing.py` and `storage.py` for unique run directories, source/configuration hashes, stage status and atomic completion records.
- Configure pytest and Ruff; add small synthetic fixtures and a baseline command skeleton in `cli.py`.
- Define stage failure exit behaviour and completion evidence. Do not regard an empty test suite as verified scientific behaviour.

**Inputs / Outputs:**
- Inputs: resolved config, code/environment identity and synthetic fixture.
- Outputs: inspectable run manifest, deterministic content identities and a working test harness.

**Verification:**
- Verify that completed runs cannot be overwritten, interrupted writes cannot appear complete, changed inputs invalidate identity and failures return a non-success status.

---

## Phase 2 - Dataset Intake and Leakage-Free Partitions

Make one HAI release usable before adding another dataset. Raw recordings remain unchanged; observations and privileged annotations are stored separately.

### 05 Dataset Acquisition and Subsystem Decision

**Goal:** Choose a documented, computationally manageable first dataset.

**Implementation:**
- Obtain an official HAI release and its technical manual; record release, source, terms, file checksums and channel meanings.
- Select a small related subsystem using normal-data availability and process documentation, preserving necessary context channels.
- Record sampling/time interpretation, normal-label provenance, channel roles and selection rationale in a decision note. Do not inspect real attack outcomes to optimize the choice.

**Inputs / Outputs:**
- Inputs: approved source recordings and documentation.
- Outputs: dataset configuration, acquisition manifest and subsystem decision.

**Verification:**
- Confirm source checksums, readable files, sufficient normal duration and documented channel identities. If access or suitability fails, document the blocker and choose another approved source explicitly.

---

### 06 Canonical HAI Adapter

**Goal:** Convert the chosen release into a stable internal format.

**Implementation:**
- Implement the HAI adapter under `data/adapters/` using explicit channel mappings and timestamp policies.
- Write observations and quality masks as typed Parquet; write dataset annotations to the separate truth location.
- Preserve original names, units, run boundaries and timestamps in metadata. Unknown units or timezone remain explicit.

**Inputs / Outputs:**
- Inputs: source CSVs and dataset config.
- Outputs: canonical observations, metadata, quality tables and separate evaluation annotations.

**Verification:**
- On source excerpts and synthetic fixtures, compare counts, timestamps, values, types and channel mappings before/after conversion. Ensure attack columns never appear in model-facing observations.

---

### 07 Data Quality and Suitability Report

**Goal:** Identify unusable data before model fitting.

**Implementation:**
- Implement `data/validation.py` checks for duplicate keys, non-monotonic time, gaps, missingness, constant channels, invalid discrete states and unexplained sampling changes.
- Split recordings into valid contiguous segments under the declared gap policy; do not silently interpolate or concatenate independent runs.
- Produce a suitability report listing accepted channels/segments and exclusions with reasons.

**Inputs / Outputs:**
- Inputs: canonical observations and metadata.
- Outputs: validated segments, quality findings and proposed exclusions.

**Verification:**
- Inject duplicates, gaps, nulls and invalid states into fixtures; verify each is rejected or handled only under an explicit policy. Confirm the original source hashes remain unchanged.

---

### 08 Normal-Data Partition Manifest

**Goal:** Separate model fitting, calibration and untouched audit data correctly.

**Implementation:**
- Implement `data/partitions.py` using chronological blocks or independent runs for normal training, calibration and audit.
- Account for required lag/window overlap and warm-up intervals; preserve source segment identity.
- Reserve normal blocks or event realizations for pseudo-event generalization tests where available. Do not fit transforms on audit data.

**Inputs / Outputs:**
- Inputs: validated normal segments and split policy.
- Outputs: exact split manifest and permitted preprocessing-fit ranges.

**Verification:**
- Test disjoint source support, boundary lags and window overlap. Confirm changing held-out normal values cannot change training-fitted transforms or model inputs.

---

### 09 Held-Out Evaluation Protocol and Truth Boundary

**Goal:** Reserve real attack evaluation without making labels accessible to selection.

**Implementation:**
- Create a separate evaluation manifest/loader in `evaluation/annotations.py`; constrain model-facing loaders to observation allowlists.
- Define which independent events/runs are reserved for the calibration milestone and final resilience evaluation before outcome inspection. If data cannot support both, defer final evaluation or disclose later reuse.
- Specify normal exposure, event grouping, warm-up handling and how annotation uncertainty is reported.

**Inputs / Outputs:**
- Inputs: source evaluation annotations and recorded protocol decisions.
- Outputs: evaluator-only manifest and tested stage input boundaries.

**Verification:**
- Verify calibration/replay run without annotation files and that modifying truth labels changes only evaluator results. Ensure the final reserved events cannot enter pseudo-event design or fitting.

---

## Phase 3 - GeCo Baseline Reproduction

Establish a trusted reference implementation before optimizing parameters or changing handling of missing inputs.

### 10 Pinned Upstream Integration

**Goal:** Make the selected GeCo revision an explicit dependency.

**Implementation:**
- Pin the official implementation or reproducibility artifact; record source revision, hashes and any compatibility patches.
- Implement `detectors/base.py`, `geco_adapter.py` and `geco_runner.py` around the architecture contracts.
- Verify the upstream settings mapping and serialization format. Keep all upstream imports inside the integration layer.

**Inputs / Outputs:**
- Inputs: verified environment and pinned source.
- Outputs: integration identity and adapter capable of constructing/loading a detector.

**Verification:**
- Exercise a minimal valid state sequence through the adapter and upstream directly. Reject unsupported settings/schema mappings; record any behavioural deviation instead of concealing it.

---

### 11 Normal Model Fitting and Export

**Goal:** Fit the first complete GeCo model using normal training data only.

**Implementation:**
- Fit one manageable contiguous training segment with fixed `k`; record fitting cost and numerical warnings.
- Save equations, coefficients, input ordering, training provenance and model-completion status.
- Do not join unrelated segments into adjacent transitions. Any later multi-segment fitting change needs separate verification.

**Inputs / Outputs:**
- Inputs: training observations, resolved settings and upstream integration.
- Outputs: complete model artifact and fitting report.

**Verification:**
- Save/load the model and compare predictions within recorded tolerance. Confirm no calibration/audit/test samples enter fitting and incomplete/failed models are rejected for selection.

---

### 12 Sequential Predictions and Alarm Parity

**Goal:** Reproduce upstream decisions on complete data.

**Implementation:**
- Implement ordered replay with explicit initialization and reset at independent segment boundaries.
- Record actual values, predictions, residuals, cumulative scores, thresholds and alarms.
- Verify `S` threshold scaling and `G` cap/overshoot semantics against the pin. Preserve baseline first-sample behaviour while identifying initialization separately in evaluation.

**Inputs / Outputs:**
- Inputs: fitted model and complete observation segments.
- Outputs: timestamped baseline predictions and alarm traces.

**Verification:**
- Compare direct-upstream and adapter outputs on synthetic sequences and a normal recorded block. Include threshold crossings, recovery and reset cases. Appending future observations must not alter earlier outputs.

---

### 13 Executed Dependency Extraction

**Goal:** Obtain a machine-readable description of what each equation actually needs.

**Implementation:**
- Implement `monitoring/registry.py` by extracting model combinations, target history, current comparison target and required lags.
- Store check/model IDs, equation details, training provenance and baseline role.
- Do not describe predictive dependencies as proven physical causality.

**Inputs / Outputs:**
- Input: complete GeCo model.
- Output: check registry linked to the executed model.

**Verification:**
- For known fixture equations, verify the registry includes every accessed observation and lag, especially the historical target. Reject a mismatched registry/model pair.

---

### 14 Baseline Suitability and Compute Gate

**Goal:** Establish whether the selected subsystem is viable before calibration work expands.

**Implementation:**
- Produce normal-data actual-versus-predicted plots, residual summaries, baseline alarm traces and measured fitting/replay cost.
- Identify poorly modelled channels using declared normal-development criteria; record exclusions and their effect on the monitored-target set.
- Resolve resource limits and the initial fixed `k`; changes at this point use development normal data, not held-out attack outcomes.

**Inputs / Outputs:**
- Inputs: Features 11-13 artifacts and normal development blocks.
- Outputs: verified baseline report and proceed/replan decision.

**Verification:**
- Confirm an independently loaded model reproduces the report and that observed runtime fits the declared development budget. Poor fit or infeasible compute is a recorded reason to replan, not a reason to tune on test attacks.

---

## Phase 4 - Offline Pseudo-Event Families

Implement bias, drift and freeze first. Their realizations are shared across candidate settings. Measurement-loss families are introduced later for coverage experiments.

### 15 Event Specification and Generator Framework

**Goal:** Make every injected event reproducible and auditable.

**Implementation:**
- Implement `events/specifications.py`, `generators.py` and `constraints.py` around versioned contracts.
- Record family, source block/checksum, affected channels, half-open interval, severity units, duration, seed, constraints and generator version.
- Separate modified observations from truth metadata; initially generate isolated events with context and an explicit reset policy.

**Inputs / Outputs:**
- Inputs: normal calibration copy, event spec and training-derived statistics.
- Outputs: modified observation copy and separate event manifest.

**Verification:**
- Verify deterministic regeneration, exact altered support, interval boundary behaviour and unchanged originals. Reject invalid channel/type combinations and events exceeding the source block.

---

### 16 Additive Bias Family

**Goal:** Test persistent incorrect readings of different strengths.

**Implementation:**
- Apply positive and negative offsets to selected continuous channels during the event interval.
- Express severity through documented units or a declared training-normal scale; handle zero-variation channels explicitly.
- Enforce documented limits or label deliberate out-of-range stress tests; record actual modification after constraints.

**Inputs / Outputs:**
- Inputs: continuous normal channel and bias specification.
- Outputs: bias-modified observations and metadata.

**Verification:**
- Check offset magnitude/sign, boundaries and constrained results on hand-calculated fixtures. A zero offset is a no-change control, not an automatically valid anomaly.

---

### 17 Gradual Drift Family

**Goal:** Test slow departures that may be harder to detect than abrupt changes.

**Implementation:**
- Define a ramp by duration and endpoint magnitude, making sample-count and elapsed-time conventions explicit.
- Implement positive/negative drift on continuous measurements using the common constraint path.
- Record the post-event return policy rather than silently adding an undocumented recovery transformation.

**Inputs / Outputs:**
- Inputs: normal copy and drift specification.
- Outputs: drift-modified observations and metadata.

**Verification:**
- Verify ramp endpoints, direction, timing and behaviour on short intervals. Confirm timestamps and unrelated channels remain unchanged.

---

### 18 Frozen-Reading Family

**Goal:** Test readings that stop responding while the surrounding process changes.

**Implementation:**
- Hold a declared observed value constant over the event interval, using a causal value-selection rule.
- Avoid awarding sensitivity credit for a channel that was already constant; record no-op/insufficient-change realizations.
- Preserve related measurements so disagreement arises from the specified modification rather than hidden extra edits.

**Inputs / Outputs:**
- Inputs: normal copy and freeze specification.
- Outputs: freeze-modified observations, valid-event status and metadata.

**Verification:**
- Check the frozen value, exact support and unchanged other channels. Test an already-flat channel and require explicit handling rather than artificial event success.

---

### 19 Balanced Event Suite and Synthetic Holdout

**Goal:** Prevent calibration from succeeding only on one easy event type.

**Implementation:**
- Assemble repeated seeds, varied severities/durations and several eligible channels under a fixed profile.
- Reserve selected severities, channels or a family as pseudo-event holdout; distinguish those results from real-attack testing.
- Define per-family balancing and controls using the normal data and documented threat assumptions, not attack-test results.

**Inputs / Outputs:**
- Inputs: three verified generators and configured suite policy.
- Outputs: calibration suite, separate pseudo-holdout and reproducible suite manifest.

**Verification:**
- Confirm suite/holdout separation, requested family balance and reproducibility. No-op events and failed realizations must be reported and excluded under a predeclared rule.

---

## Phase 5 - Calibration Engine

Turn the first prototype into a parameter-selection procedure with explicit false-alarm accounting and stable selection rules.

### 20 Alarm Episodes, Exposure and Event Metrics

**Goal:** Define correct scoring before using it to select settings.

**Implementation:**
- Implement `evaluation/matching.py` and `metrics.py` for declared episode grouping, event detection, delay, misses and alarm-time fraction.
- Implement clean-normal exposure accounting, unavailable time and episodes/day; do not count unknown truth as normal.
- Keep the annotation loader separate: calibration metrics accept synthetic metadata only and are reusable without importing real truth.

**Inputs / Outputs:**
- Inputs: prediction traces, synthetic events or clean-normal intervals and frozen metric rules.
- Outputs: checkable metric records and undefined/insufficient-exposure statuses.

**Verification:**
- Use manually computed fixtures for prolonged alarms, adjacent events, boundary alarms, misses, zero exposure and unavailable decisions. Verify one long alarm is visible in alarm duration even if it is one episode.

---

### 21 Candidate Replay and Valid Residual Cache

**Goal:** Evaluate candidate `S/G` settings fairly without unnecessary model refits.

**Implementation:**
- Implement `calibration/search.py` with bounded explicit candidates and isolated sequential detector state.
- Cache predictions/residuals only under matching data/model/preprocessing/prediction-policy identities.
- Recompute cumulative alarm state for every setting; persist failures and runtime rather than skipping them silently.

**Inputs / Outputs:**
- Inputs: fitted model, fixed event suite, untouched normal calibration blocks and candidate settings.
- Outputs: candidate prediction/metric artifacts and provenance-aware caches.

**Verification:**
- Compare cached and uncached outcomes. Verify candidate order does not change results, changed inputs invalidate caches, and state from one candidate cannot influence another.

---

### 22 Constrained Objective and Selection

**Goal:** Choose a useful configuration under the requested observed alarm budget.

**Implementation:**
- Implement `calibration/objective.py` and `selection.py` using a declared family-balanced utility and delay/miss handling.
- Reject candidates exceeding normal false-alarm or validity requirements; require adequate decision coverage so abstention cannot win.
- Apply a deterministic tie-break and return `no_feasible_configuration` when appropriate.

**Inputs / Outputs:**
- Inputs: candidate results and explicit budget/objective configuration.
- Outputs: candidate ranking, rejection reasons and selected configuration or typed failure.

**Verification:**
- Use synthetic candidate tables where the feasible winner is known. Test all-infeasible, tied, unavailable and insufficient-exposure cases. Changing real attack labels cannot change selection.

---

### 23 Stability and Unseen Pseudo-Event Assessment

**Goal:** Avoid choosing a narrow optimum that fails under small changes.

**Implementation:**
- Implement `calibration/stability.py` across declared normal blocks and event seeds.
- Select a near-best stable candidate under a recorded rule; evaluate the frozen rule against reserved pseudo-events.
- Report per-family results and variation across blocks/events, not independent-sample claims from correlated timestamps.

**Inputs / Outputs:**
- Inputs: repeated candidate outcomes and pseudo-holdout manifest.
- Outputs: stability report, candidate sensitivity and finalized development selection.

**Verification:**
- Confirm the rule rejects an unstable fixture winner and gives reproducible results. If pseudo-holdout results drive redesign, document that it has become development data.

---

### 24 Frozen Selection and Untouched Normal Audit

**Goal:** Seal the selection before examining held-out audit or attack outcomes.

**Implementation:**
- Save the model, settings, profile, scoring protocol, dependency identities and source/config hashes as a frozen selection package.
- Evaluate observed normal alarm burden on the reserved audit block, including uncertainty/insufficient-duration findings.
- Record audit failure without automatic parameter adjustment. Any redesign starts a new lineage and changes the held-out-data claim.

**Inputs / Outputs:**
- Inputs: finalized development selection and untouched audit block.
- Outputs: immutable selection package and separate audit report.

**Verification:**
- Verify hash consistency and rejection of mutation/incomplete artifacts. Test that audit results cannot trigger an implicit reselection.

---

## Phase 6 - Detector Export and First Research Evaluation

Complete the core product: normal-data intake, automatic calibration, reviewable results and a reusable detector package. A customer does not need to supply attack examples to use this workflow.

### 25 Exportable Detector Package

**Goal:** Produce a detector that another team member can load without retraining.

**Implementation:**
- Package the frozen model, selected settings, channel schema/order, preprocessing, sampling requirements and dependency registry.
- Include validation scope, tested disturbance profile, known limitations and model/environment provenance.
- Validate compatibility at load time. Exclude raw recordings, real attack annotations and sensitive local paths from the package.

**Inputs / Outputs:**
- Input: frozen selection package.
- Output: distributable detector package with a manifest and documented loading contract.

**Verification:**
- Load in the verified clean environment and replay a fixture with matching outputs. Reject missing channels, incompatible schemas and corrupted model hashes. Inspect exported content for prohibited data.

---

### 26 End-to-End CLI User Journey

**Goal:** Make the calibration product usable through one documented command workflow.

**Implementation:**
- Wire the architecture's `prepare`, `fit-baseline`, `generate-events`, `calibrate`, `freeze`, `replay`, `evaluate` and `report` responsibilities into the CLI.
- Support the core path: register normal data -> inspect suitability -> set budget/profile -> calibrate -> review -> export/load -> replay new observations.
- Keep real annotation paths exclusive to evaluation. Use the balanced bias/drift/freeze profile first; expose `k/S/G` only as explicit advanced configuration.

**Inputs / Outputs:**
- Inputs: normal recordings, metadata and validated project configuration.
- Outputs: status/progress, detector package, replay outputs and a normal/synthetic validation report.

**Verification:**
- Exercise the complete path on a small fixture with annotation storage inaccessible. Test invalid input, insufficient data and no-feasible-settings responses. Document only commands that actually execute.

---

### 27 Held-Out Attack Evaluation and Baseline Comparison

**Goal:** Test transfer of synthetic calibration to documented attacks without influencing the selection.

**Implementation:**
- Use `evaluation/comparisons.py` to compare reproduced baseline and frozen calibrated GeCo on the reserved first-milestone test events.
- Match inputs, initialization, grouping and exposure policies; report misses, delay, false alarms and per-event outcomes.
- Record that viewed attack events are no longer an untouched final test for later redesigned methods.

**Inputs / Outputs:**
- Inputs: frozen baseline/calibrated detectors, held-out observations and evaluator-only annotations.
- Outputs: paired comparison results with uncertainty, failure cases and lineage.

**Verification:**
- Confirm test annotations are joined only after replay. Regenerate the report from saved predictions and independently check representative matches. A negative transfer result is a valid completed evaluation.

---

### 28 First-Milestone Report and Business Evidence

**Goal:** Deliver a defensible account of the calibration product and its value.

**Implementation:**
- Implement reporting tables/plots for predictions, candidate search, selected settings, synthetic results, normal audit and attack results where available.
- Measure model/search/replay runtime and human setup/review effort against a documented baseline procedure.
- Separate observed costs from hypothetical rates and savings. A normal-only customer report cannot claim measured real-attack performance for that customer's plant.

**Inputs / Outputs:**
- Inputs: Features 14-27 artifacts and measured effort records.
- Outputs: first-milestone report, reproducible demonstration and gate decision for resilience work.

**Verification:**
- Trace every result to a run/metric artifact. Ensure the report distinguishes synthetic performance, benchmark attack performance and unmeasured business hypotheses. Do not require a positive gain to mark the implementation verified.

---

## Phase 7 - Dependency-Aware Monitoring Resilience

Extend a verified calibration pipeline to known measurement degradation. Separate check availability, prediction availability and anomaly decisions.

### 29 Measurement-Loss and Quality Experiments

**Goal:** Introduce missing blocks and single-channel loss without leaking the original hidden readings.

**Implementation:**
- Extend the event generator with missing intervals and channel loss; record event truth separately.
- Implement `monitoring/quality.py` from observable nulls/timestamps and documented quality evidence.
- Retain clean hidden measurements only for evaluation. Label supplied suspect-channel masks as known-degradation/oracle experiments, not automatic localization.

**Inputs / Outputs:**
- Inputs: permitted normal development blocks and measurement-loss specs.
- Outputs: degraded observations, observable quality masks and separate evaluator truth.

**Verification:**
- Confirm replay cannot access hidden originals or injected-channel labels. Verify missingness produces quality status rather than an automatic cyberattack success.

---

### 30 Check Eligibility and Coverage Accounting

**Goal:** Identify exactly which monitoring functions lose their required evidence.

**Implementation:**
- Implement `monitoring/eligibility.py` and `coverage.py` using actual current/lagged dependencies.
- Define a fixed target denominator and supported/degraded/unavailable/initializing outcomes with reasons.
- Keep estimates without target observations outside residual-check coverage; report shared dependencies and unavailable exposure.

**Inputs / Outputs:**
- Inputs: check registry, observation history and quality masks.
- Outputs: check eligibility and target-level coverage timeline.

**Verification:**
- On a known dependency fixture, remove one channel and verify precisely the affected checks at the correct times/lags. Test missing target history, missing current target and total coverage loss.

---

### 31 Selective Replay and Recovery State Policy

**Goal:** Run valid checks during degradation without corrupting sequential detector state.

**Implementation:**
- Implement resilient replay/state ownership in `monitoring/replay.py` and `state.py`, keeping baseline replay separate.
- Invalidate ineligible-check history/accumulators under the declared policy; require valid warm-up before reactivation.
- Preserve unaffected checks and make every reset, cold start and unavailable decision explicit.

**Inputs / Outputs:**
- Inputs: frozen models/settings, quality/eligibility sequence and reset policy.
- Outputs: resilient predictions, nullable alarms and state-transition log.

**Verification:**
- Establish complete-data parity, then test loss/recovery, independent runs and future-data prefix invariance. Verify an unavailable check never becomes a false normal output or inherits another check's accumulator.

---

### 32 Validated Alternative-Check Library

**Goal:** Preserve partial monitoring where independent usable inputs support another validated check.

**Implementation:**
- Implement `monitoring/alternatives.py` for a small set of targets and excluded-input configurations.
- Fit alternatives on normal training data, calibrate separately on development data and export their full dependencies/validation evidence.
- Freeze alternative ranking and switching rules before evaluation. Record no-valid-alternative outcomes instead of forcing a fallback.

**Inputs / Outputs:**
- Inputs: normal development data, baseline dependencies and declared alternative candidates.
- Outputs: independently validated alternatives, eligibility rules and switch policy.

**Verification:**
- Confirm excluded channels are absent from all required inputs, including lagged self-inputs. Check cold-start/switching behaviour and compare against disabling checks/simple imputation. Estimates cannot independently validate themselves.

---

### 33 Resilience Evaluation and Failure Analysis

**Goal:** Determine whether alternatives preserve useful detection rather than only increasing coverage counts.

**Implementation:**
- Freeze the resilience method and compare original/calibrated GeCo, disabling affected checks and alternative selection under matched degradation schedules.
- Measure coverage, retained event detection, unavailable duration, alternative estimation error and misleading support declarations against controlled truth.
- Use the separately reserved final events where feasible; disclose any reused evaluation data and method changes.

**Inputs / Outputs:**
- Inputs: frozen methods, degradation observations and separate evaluation truth.
- Outputs: resilience report, paired results and explicit failure cases.

**Verification:**
- Show dependency/accounting correctness independently of any comparative gain. Report known-degradation assumptions, targets with no alternatives and coordinated-manipulation limitations. Do not translate monitoring metrics into physical downtime savings.

---

## Phase 8 - Review and Monitoring Interface

Build an artifact viewer after the scientific pipeline works. CLI stages remain the authoritative experiment path; the interface does not silently start training or advance detector state.

### 34 Project and Suitability Review

**Goal:** Let a user inspect the data/project configuration before accepting calibration results.

**Implementation:**
- Create the optional `apps/dashboard.py` viewer for completed project runs, data quality, accepted/excluded channels and resolved configuration.
- Display the alarm-budget requirement and tested disturbance profile in plain language.
- Show failed/insufficient-data outcomes prominently. File intake and execution remain the verified CLI workflow initially.

**Inputs / Outputs:**
- Inputs: completed preparation/configuration artifacts.
- Output: read-only project and suitability view.

**Verification:**
- Confirm displayed values match stored artifacts and widget reruns cannot modify configurations or start experiments. Check the empty, failed and incomplete-run views.

---

### 35 Calibration Results and Detector Review

**Goal:** Make the selected configuration and its evidence understandable.

**Implementation:**
- Display candidate trade-offs, observed false alarms, synthetic detection/delay and validation limitations.
- Link the exact frozen detector package and provenance; keep parameter internals in an advanced view.
- Clearly distinguish unavailable real-attack evaluation from zero attack detections or verified customer performance.

**Inputs / Outputs:**
- Inputs: selection package, audit report and optional benchmark comparison.
- Output: reviewable calibration result and artifact download links.

**Verification:**
- Check selected-setting identity, infeasible outcomes, report labels and export hashes. User interface choices must not silently change scientific results.

---

### 36 Incident, Dependency and Coverage Replay View

**Goal:** Demonstrate what monitoring remains supported during a recorded degradation event.

**Implementation:**
- Show recorded values, predictions, alarms, check dependencies, coverage reasons and alternative switches from completed replay outputs.
- Mark estimates, unavailable intervals and initialization explicitly; distinguish observed pattern from suspected cause.
- Allow navigating the timeline without recomputing or mutating detector state.

**Inputs / Outputs:**
- Inputs: completed baseline/resilient replay artifacts and registry.
- Output: explanatory replay demonstration.

**Verification:**
- Inspect a normal, alarm, sensor-loss, fallback and no-fallback case. Verify absent decisions do not appear as healthy readings and UI navigation leaves run hashes unchanged.

---

## Phase N - Final Integration

Package the implemented scope with evidence and a reproducible team handoff. Completion means the planned engineering behaviour is verified, not that every research hypothesis produced a positive result.

### 37 Integrated Delivery and Context Reconciliation

**Goal:** Deliver a reproducible software project with honest capability and result claims.

**Implementation:**
- Run the complete normal-data calibration/export/replay path and the implemented resilience demonstration in the verified environment.
- Reconcile `project-overview.md`, `architecture.md`, README and experiment notes with actual implemented/proposed status.
- Package source, lock, configs, allowed fixtures, reports and demonstration steps. Include limitations, prior-work attribution and measured resource/effort records.

**Inputs / Outputs:**
- Inputs: verified core features and their artifacts.
- Outputs: final submission package, user guide, report and explicit remaining roadmap.

**Verification:**
- A teammate reproduces the demonstration from instructions without undocumented local paths. All completed features link to evidence; restricted recordings and secrets are absent from exports. No future extension is presented as implemented.

---

## Research Extension - Conditional Features 38-45

These features extend a verified core. They are planned only; they are not commitments for the first milestone. Activate an extension after its data/resource gate is satisfied, and record its effect on the evaluation protocol. Sibling extension phases are independent unless a feature explicitly adds a dependency.

## Phase R0 - Portability Across Processes

### 38 Second-Process Adapter and Suitability Gate

**Goal:** Reuse the pipeline on an independent process without copying a trained model.

**Implementation:**
- Obtain SWaT subject to approved access, or document another appropriate second process; add its adapter and metadata only.
- Reuse the canonical schema and frozen procedure; establish separate normal and evaluation partitions.
- Record mapping effort, manual constraints, suitability and compute requirements.

**Inputs / Outputs:**
- Inputs: verified core, second source and fixed-method identity.
- Outputs: second canonical dataset and suitability decision.

**Verification:**
- Confirm no second-dataset branches enter calibration/coverage logic and source semantics are preserved. Failure of model suitability is a documented portability limitation.

---

### 39 Frozen-Procedure Portability Evaluation

**Goal:** Test reuse across processes under transparently reported customization.

**Implementation:**
- Refit and recalibrate on the second process's normal data using the frozen procedure.
- Evaluate on its reserved events and record resource/manual effort differences.
- Treat Tennessee Eastman, if used, as fault generalization rather than cyberattack attribution; distinguish shared-testbed subsystems from independent processes.

**Inputs / Outputs:**
- Inputs: Feature 38 data and fixed protocol.
- Outputs: portability comparison and process-specific model package.

**Verification:**
- Verify new model provenance and shared method identity. Disclose any second-test-informed adaptation; do not describe a reused trained model as necessary for portability.

---

## Phase R1 - Operating-Mode Awareness

### 40 Documented Mode Definitions and Exposure Gate

**Goal:** Establish meaningful modes only where the data supports them.

**Implementation:**
- Inspect documented normal state tags/actuator combinations and define a small interpretable mode set using normal development data.
- Implement `monitoring/modes.py` with current/past inputs only and explicit unknown/transition states.
- Record mode-selector dependencies and verify adequate normal exposure across separate episodes. Defer the feature if suitable modes cannot be established.

**Inputs / Outputs:**
- Inputs: verified core and documented normal operating context.
- Outputs: mode specification, assignments and exposure/suitability report.

**Verification:**
- Verify online assignments cannot access future data or attack labels. A failed mode input produces uncertainty; arbitrary clusters are not asserted to be physical operating modes.

---

### 41 Per-Mode Calibration and Switching Evaluation

**Goal:** Test whether mode-specific settings improve monitoring over one global configuration.

**Implementation:**
- Start with separate alarm calibration using existing equations; fit separate equations only if a recorded development result justifies it.
- Define cumulative-state/reset rules and validate transitions, cold starts, unknown modes and mode-selector loss.
- Freeze the mode method before test evaluation; compare against the global configuration with complete-sequence exposure accounting.

**Inputs / Outputs:**
- Inputs: Feature 40 modes, normal development partitions and verified calibration engine.
- Outputs: mode configurations and paired evaluation.

**Verification:**
- Confirm no blanket suppression of transition alarms and no silent state transfer. Report within-mode and transition results, including whether the extra complexity gives no improvement.

---

## Phase R2 - Suspect-Channel Inference and Pattern Diagnosis

### 42 Observable-Evidence Suspect-Channel Inference

**Goal:** Assess degradation when the affected channel is not supplied by experiment truth.

**Implementation:**
- Add inference using available residual patterns, quality evidence and check dependencies; record assumptions about trusted measurements.
- Emit uncertainty or multiple suspects when evidence cannot isolate one channel.
- Use the same dependency/coverage contracts; never feed injected-channel IDs or event labels to inference.

**Inputs / Outputs:**
- Inputs: frozen check outputs and observable evidence.
- Outputs: suspect-channel hypotheses with evidence/reasons, not definitive attack attribution.

**Verification:**
- Compare unknown-degradation results with the explicitly labelled known-degradation upper-reference case. Report localization errors and downstream coverage/detection damage under single and selected multi-channel changes.

---

### 43 Anomaly-Pattern Characterization

**Goal:** Explain detected patterns without implying the cause has been proven.

**Implementation:**
- Classify observable bias-like, drift-like and freeze-like patterns with unknown/mixed outcomes, using rules or synthetic-label development.
- Predeclare evaluation categories and map documented benchmark events only in the evaluator.
- Separate pattern recognition from fault-versus-attack attribution. Independent cyber evidence would require a new documented contract.

**Inputs / Outputs:**
- Inputs: event windows available at decision time and frozen diagnosis rules.
- Outputs: pattern hypotheses and validation report.

**Verification:**
- Test confusable/no-op/unknown patterns and evaluate whole held-out events. Synthetic pattern accuracy cannot be reported as verified identification of cyberattack mechanisms.

---

## Phase R3 - Responsive Physical-Resilience Simulation

### 44 Small Process Simulator and Fixed Response Policy

**Goal:** Create an environment that reacts to interventions so physical outcomes can be evaluated.

**Implementation:**
- Record an extension decision defining the separate simulator module, state equations, units, observations, constraints, disturbances and response-policy interface before implementation.
- Implement a small tank/pump/valve process and explicitly model the assumed difference between corrupted reports and physical state.
- Keep simulator truth and response-policy access distinct from monitor inputs; retain a no-response and conservative-policy baseline.

**Inputs / Outputs:**
- Inputs: verified monitoring core, documented process assumptions and simulator protocol.
- Outputs: responsive simulation with separate physical truth, observations and action logs.

**Verification:**
- Verify conservation/timestep behaviour, command effects, repeatability and no truth leakage. Match trusted information available to competing response policies; no connection to live equipment is introduced.

---

### 45 Physical-Resilience Comparison and Claims Audit

**Goal:** Measure service continuity and recovery only within the validated simulation assumptions.

**Implementation:**
- Freeze methods, policies and scenario schedules; compare equivalent scenarios with independent held-out runs/seeds.
- Measure unsafe-limit duration, service delivered, intervention frequency, monitoring loss and recovery time.
- Report model mismatch, intervention cost and policies that preserve safety by sacrificing service; keep simulated claims distinct from field evidence.

**Inputs / Outputs:**
- Inputs: Feature 44 simulator, frozen monitoring methods/policies and scenario protocol.
- Outputs: paired physical-resilience results and limitations.

**Verification:**
- Confirm all reported physical outcomes come from responsive trajectories rather than fixed CSV replay. Trace differences to matched scenarios/policies and report negative or inconclusive results.

---

## Feature Count

| Phase | Features | Cumulative Total |
| --- | ---: | ---: |
| Phase 1 - Foundation | 4 | 4 |
| Phase 2 - Dataset Intake and Leakage-Free Partitions | 5 | 9 |
| Phase 3 - GeCo Baseline Reproduction | 5 | 14 |
| Phase 4 - Offline Pseudo-Event Families | 5 | 19 |
| Phase 5 - Calibration Engine | 5 | 24 |
| Phase 6 - Detector Export and First Research Evaluation | 4 | 28 |
| Phase 7 - Dependency-Aware Monitoring Resilience | 5 | 33 |
| Phase 8 - Review and Monitoring Interface | 3 | 36 |
| Phase N - Final Integration | 1 | 37 |
| Phase R0 - Portability Across Processes | 2 | 39 |
| Phase R1 - Operating-Mode Awareness | 2 | 41 |
| Phase R2 - Suspect-Channel Inference and Pattern Diagnosis | 2 | 43 |
| Phase R3 - Responsive Physical-Resilience Simulation | 2 | 45 |
| **Total planned: 37 core + 8 conditional extensions** | **45** | **45** |

First milestone: Features 01-28. Monitoring-product completion: Features 01-37. Feature count is a work breakdown, not a claim that all tasks take equal effort or that the full roadmap fits one semester.

---

## Build Order Rules

- Follow phase dependency order for the core. Independently scoped work may proceed concurrently once its contracts and prerequisites are verified; later integration cannot conceal failed earlier behaviour.
- Each feature requires observable verification evidence. Source files, successful imports or an attractive dashboard do not establish correct detection/calibration.
- Begin with Feature 01, then acquire/select data and verify the GeCo baseline. Do not start mode discovery, a dashboard or physical simulation as substitutes for that baseline.
- Preserve all invariants I01-I27 in `architecture.md`; the template used for this plan contributes structure only and has no authority over this project.
- Treat all features as planned until linked evidence establishes completion. Mark blocked, failed, deferred and inconclusive outcomes explicitly.
- Use the package paths/contracts in `architecture.md`. New architectural modules or boundary changes require a recorded decision and context reconciliation before dependent implementation.
- Fit only on allowed normal development partitions. Real attack annotations remain evaluator-only; synthetic metadata can score calibration but cannot enter replay decisions.
- Declare splitting, event definitions, score weights, candidate ranges, alarm budget, exposure, warm-up and reset policies before test inspection. Reject unresolved runnable configs.
- Preserve raw data and create unique derived/run artifacts. Do not overwrite completed experiments or distribute restricted recordings.
- Cache predictions only when provenance and semantics match. Always recompute sequential alarm accumulation for changed detector settings; never share mutable state across candidates/runs.
- Verify upstream parity before selective missing-input replay. Missing targets produce unavailable comparisons or explicitly labelled estimates, not healthy decisions.
- Report false-alarm duration and unavailable exposure alongside episodes/day. A detector cannot win by abstaining everywhere or remaining in one endless alarm.
- Separate known-degradation experiments from inferred suspect-channel handling. Hidden clean readings and injected-channel truth remain evaluator-only.
- Validate alternatives separately; dependencies include lagged target readings. No reconstructed value becomes independent corroboration.
- Complete the first CLI/export milestone before spending effort on the artifact viewer. UI reruns do not train models, change the experiment configuration or mutate detector state.
- Maintain distinct held-out claims for the first milestone and later resilience methods. A viewed test is not untouched after it informs redesign; record lineage or obtain new evaluation data.
- Portability reuses the procedure and refits models. Modes require documented meaning and sufficient data. Simulation requires a responsive process and separate physical metrics.
- Record implementation correctness and comparative research benefit separately. A verified feature may yield no improvement; report that result rather than tuning the claim.
- Cost reductions are hypotheses until time, compute and integration effort are measured. Never reuse illustrative business figures as experimental evidence.
- A successful core delivery does not require completing every extension. Replan against actual data, fitting runtime and team capacity without silently dropping scientific validity.
