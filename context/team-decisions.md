Here are the decisions to bring back. **Decide 1–6 now; the experimental settings can follow after inspecting normal data.**

1. **Committed scope:** Calibration/export only, or also dependency tracking and alternative monitoring? Which extensions are mandatory?
2. **Interface:** CLI with a results viewer, or a dashboard that uploads data, launches calibration and exports the detector?
3. **Dataset:** Use HAI 23.05 first? Which subsystem/channels should we investigate?
4. **Timeline:** Submission date and first working-demo deadline.
5. **Team ownership:** Who handles data/GeCo, pseudo-events/calibration, resilience, evaluation and integration?
6. **Resources:** Available machines, RAM, shared compute and any spending limit.
7. **Input requirements:** Supported file format and required timestamp, channel-type, units and normal-operation information.
8. **Preprocessing policy:** Handling of gaps, duplicates, missing values, scaling and unsuitable channels.
9. **Data splits:** Exact normal training/calibration/audit blocks and reserved attack-test events.
10. **GeCo baseline:** Source revision, tested environment and acceptable reproduction tolerances.
11. **Search settings:** Initial fixed `k`, candidate `S/G` ranges and compute limits.
12. **Disturbance profile:** Which pseudo-event families are included and whether users can customize them.
13. **Event parameters:** Magnitudes, durations, affected channels, constraints, seeds and held-out variations.
14. **Alarm requirement:** Which false-alarm budgets to evaluate and how much normal exposure is required.
15. **Selection objective:** How to balance detection, delay, missed events and stability; how to break ties.
16. **Evaluation rules:** Alarm-episode grouping, event matching, baselines, metrics and success criteria.
17. **Monitoring degradation:** Which failure scenarios to support and how to define supported/degraded/unavailable coverage.
18. **Fallback behaviour:** Which targets need alternatives, validation requirements and switching/warm-up rules.
19. **Business evaluation:** What manual workflow to compare against and how to measure engineering effort and costs.
20. **Extensions:** Whether to include a second process, operating modes, suspect-channel diagnosis or responsive simulation—and their priority.

You can answer by number. Mark unresolved items **“investigate first”**; we should determine their values from development evidence rather than guess.