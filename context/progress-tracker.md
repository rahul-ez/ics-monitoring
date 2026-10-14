# Progress Tracker

Update this file after each verified feature, material decision, blocker or session handoff. `build-plan.md` defines the features and verification requirements; this file records their actual status. The supplied tracker from another project was used for structure only.

---

## Current Status

**Last updated:** 14 October 2026  
**Phase:** Before Phase 1 - Foundation  
**Last completed:** Project context documents created; no numbered implementation feature is verified complete.  
**Next:** 01 Repository, Package and Verified Environment.  
**Status:** Planning/context setup complete. Calibration, model training, detector export, dashboard and resilience experiments remain unverified.  
**Active feature:** None.  
**Verified progress:** 0/28 first-milestone features; 0/37 core features. Eight additional research-extension features are conditional and not activated.  
**Current blocker:** No implementation blocker has been established. Dataset pin, environment compatibility and experiment choices remain unresolved prerequisites to their relevant features.

The existence of a GeCo review checkout, proposal PDF or inspected remote dataset headers is not evidence of completed model reproduction, dataset acquisition or scientific evaluation.

---

## Progress

Checkboxes mean **implemented and verified against the feature's stated requirements**. Leave a feature unchecked while planned, in progress, blocked, deferred, or awaiting verification. Record that detailed status below instead of using an ambiguous checkbox symbol.

**Phase 1 - Foundation**

- [ ] 01 Repository, Package and Verified Environment
- [ ] 02 Validated Experiment Configuration
- [ ] 03 Shared Contracts and Failure States
- [ ] 04 Artifact Provenance and Verification Harness

**Phase 2 - Dataset Intake and Leakage-Free Partitions**

- [ ] 05 Dataset Acquisition and Subsystem Decision
- [ ] 06 Canonical HAI Adapter
- [ ] 07 Data Quality and Suitability Report
- [ ] 08 Normal-Data Partition Manifest
- [ ] 09 Held-Out Evaluation Protocol and Truth Boundary

**Phase 3 - GeCo Baseline Reproduction**

- [ ] 10 Pinned Upstream Integration
- [ ] 11 Normal Model Fitting and Export
- [ ] 12 Sequential Predictions and Alarm Parity
- [ ] 13 Executed Dependency Extraction
- [ ] 14 Baseline Suitability and Compute Gate

**Phase 4 - Offline Pseudo-Event Families**

- [ ] 15 Event Specification and Generator Framework
- [ ] 16 Additive Bias Family
- [ ] 17 Gradual Drift Family
- [ ] 18 Frozen-Reading Family
- [ ] 19 Balanced Event Suite and Synthetic Holdout

**Phase 5 - Calibration Engine**

- [ ] 20 Alarm Episodes, Exposure and Event Metrics
- [ ] 21 Candidate Replay and Valid Residual Cache
- [ ] 22 Constrained Objective and Selection
- [ ] 23 Stability and Unseen Pseudo-Event Assessment
- [ ] 24 Frozen Selection and Untouched Normal Audit

**Phase 6 - Detector Export and First Research Evaluation**

- [ ] 25 Exportable Detector Package
- [ ] 26 End-to-End CLI User Journey
- [ ] 27 Held-Out Attack Evaluation and Baseline Comparison
- [ ] 28 First-Milestone Report and Business Evidence

**Phase 7 - Dependency-Aware Monitoring Resilience**

- [ ] 29 Measurement-Loss and Quality Experiments
- [ ] 30 Check Eligibility and Coverage Accounting
- [ ] 31 Selective Replay and Recovery State Policy
- [ ] 32 Validated Alternative-Check Library
- [ ] 33 Resilience Evaluation and Failure Analysis

**Phase 8 - Review and Monitoring Interface**

- [ ] 34 Project and Suitability Review
- [ ] 35 Calibration Results and Detector Review
- [ ] 36 Incident, Dependency and Coverage Replay View

**Phase N - Final Integration**

- [ ] 37 Integrated Delivery and Context Reconciliation

**Phase R0 - Portability Across Processes (conditional; not activated)**

- [ ] 38 Second-Process Adapter and Suitability Gate
- [ ] 39 Frozen-Procedure Portability Evaluation

**Phase R1 - Operating-Mode Awareness (conditional; not activated)**

- [ ] 40 Documented Mode Definitions and Exposure Gate
- [ ] 41 Per-Mode Calibration and Switching Evaluation

**Phase R2 - Suspect-Channel Inference and Pattern Diagnosis (conditional; not activated)**

- [ ] 42 Observable-Evidence Suspect-Channel Inference
- [ ] 43 Anomaly-Pattern Characterization

**Phase R3 - Responsive Physical-Resilience Simulation (conditional; not activated)**

- [ ] 44 Small Process Simulator and Fixed Response Policy
- [ ] 45 Physical-Resilience Comparison and Claims Audit

---

## Milestone Summary

| Milestone | Feature range | Verified | Current outcome |
| --- | --- | ---: | --- |
| First calibration product | 01-28 | 0/28 | Not implemented/verified |
| Monitoring resilience | 29-33 | 0/5 | Not started |
| Review interface and final delivery | 34-37 | 0/4 | Not started |
| Core total | 01-37 | 0/37 | Planning stage |
| Conditional research extensions | 38-45 | 0/8 | Not activated |

Do not treat feature count as an estimate of time or effort. Verified implementation and evidence of improved performance are different outcomes. A correctly executed experiment with a negative result can complete an evaluation feature.

---

## Decisions Made During Build

No implementation decisions have been verified yet. The following planning decisions establish the starting context; they do not imply completed features.

**14 October 2026 - Product and first milestone:**

- Core product: user-provided normal readings and a monitoring requirement produce a trained/calibrated GeCo detector package plus a validation report.
- First workflow: intake -> schema confirmation -> suitability assessment -> alarm budget and disturbance profile -> training/calibration -> review/export -> replay compatible new readings.
- The first milestone uses a CLI pipeline. The architecture currently specifies a later read-only artifact dashboard; a dashboard that uploads data and launches jobs is a desired subsequent product interface, not a verified or fully specified implementation.
- Before implementing job-launching UI controls, reconcile `architecture.md` and `build-plan.md` with explicit background-job ownership, progress, cancellation and rerun behaviour. Dashboard refreshes must never restart fitting or mutate detector state.

**14 October 2026 - Input and preprocessing:**

- Column names and channel counts may differ between user datasets. Their roles, values, timestamps, sampling and compatibility still require validation.
- Preserve original readings and schema mappings. Do not silently interpolate, smooth, remove outliers, normalize, clip or invent units.
- Fit any learned transforms on normal training data only. Record and export transformations with the model.
- A trained detector requires compatible input channels and sampling; an unrelated schema requires an explicit validated mapping or a new fit.

**14 October 2026 - Calibration and event scope:**

- Begin with fixed `k` and a recorded search over `S/G`; reproduce upstream behaviour before extending it.
- Initial event families: additive bias, gradual drift and frozen readings. Add measurement loss for the resilience milestone; timing, replay and structured multi-channel tests are later expansions.
- Disturbance profiles represent observable effects, not proof of attack type or attacker intent.
- Keep real attack labels out of fitting and calibration. Audit/test exposure, including any reuse after redesign, must be recorded.

**14 October 2026 - Dataset investigation:**

- HAI is the planned first dataset; HAI 23.05 is the current recommended release, not yet a pinned, locally validated dataset.
- Remote header inspection found 87 columns in the HAI 23.05 training/test observation CSVs: `timestamp` plus 86 process channels.
- Attack labels are separate `label-test1.csv` and `label-test2.csv` files. Labels are evaluation-only; confirm full alignment during acquisition/ingestion.
- Exact row counts, file checksums, release identity, selected subsystem, units and normal/test partitions remain to be established in Features 05-09.

**14 October 2026 - Resilience and claims:**

- Begin with known measurement degradation and dependency tracking. Automatically inferring suspect channels is a conditional extension.
- Alternatives need separate fitting, calibration and validation. Predictions without an observed target are estimates, not valid residual comparisons.
- Operating modes depend on documented states and sufficient exposure; portability requires separate process models; physical-resilience claims require responsive simulation.
- Cost reductions and detection gains remain hypotheses. No measured performance, monetary saving or production deployment has been established.

---

## Verification Evidence

No numbered implementation feature has a verified evidence entry yet. Add one entry per completed feature with the following fields:

- **Feature:** number and exact title from `build-plan.md`.
- **Date / owner:** verification date and responsible team member, if assigned.
- **Status:** planned, in progress, awaiting verification, verified, blocked, deferred or failed.
- **Changes:** implemented behaviour and affected modules.
- **Verification:** exact command/procedure, environment and source/model/configuration identities.
- **Result:** observed outcome; include failed/skipped checks and numerical tolerances where relevant.
- **Artifacts:** project-relative report, manifest, test-output and decision-note paths.
- **Scientific outcome:** positive, negative, inconclusive or not applicable; separate from implementation status.
- **Remaining limitations / next action:** what is unresolved and what the next person should do.

Do not invent test counts, runtime, metrics, artifact locations or completion evidence. Logs from another project never qualify. Detailed results belong in `docs/experiments/` or run artifacts; this tracker links to them.

---

## Blockers and Open Decisions

| Item | Current state | Resolve before |
| --- | --- | --- |
| Python/package compatibility and exact lock | Unverified; architecture supplies an initial target | Feature 01 completion |
| Official GeCo pin and compatibility patches | Review checkout exists; final revision unselected | Features 10-12 |
| Dataset release/subsystem and local acquisition | HAI 23.05 recommended; not pinned/validated | Features 05-07 |
| Time interpretation, sampling and gap handling | To establish from selected data | Features 06-08 |
| Normal partitions and final event reservation | Not defined | Features 08-09 |
| Alarm budget, exposure requirements and scoring rules | Not selected; no plant-specific defaults assumed | Executable calibration/metric protocol |
| Fixed `k`, candidate ranges and compute limits | Not selected | Features 14 and 21 |
| Event severity/duration, constraints and seeds | Not selected | Features 15-19 |
| Resilient reset, warm-up and switch policy | Proposed semantics require verification | Features 30-32 |
| Full dashboard execution controls | Desired flow; architecture currently viewer-only | Any job-launching interface work |
| Extension activation and resources | No extension activated | Features 38-45 |

An unresolved future decision is not automatically a current blocker. A blocker entry should identify the affected feature, concrete cause, attempted safe alternatives and next resolving action. Remove no historical evidence when a blocker is resolved; record the resolution.

---

## Notes

**14 October 2026 - Tracker initialization (documentation only):**

- Created this tracker using only the supplied example's organizational structure.
- Mapped every checkbox to Features 01-45 in this project's `build-plan.md`; all remain unchecked.
- Existing context documents: `project-overview.md`, `architecture.md`, `build-plan.md` and this tracker. A proposal PDF is available under `output/pdf/`.
- This initialization does not install dependencies, acquire full datasets, train models, run calibration or verify implementation features.

**Next session handoff:**

- Read `project-overview.md`, `architecture.md`, `build-plan.md` and this file.
- Start Feature 01 after inspecting current repository state and applicable instructions; preserve existing work.
- Do not jump to UI development or extensions before the relevant baseline gates.
- After verification, add an evidence entry, update the checkbox and milestone counts, then update Current Status and the next concrete action.
