# Presentation prototype, separate from the research pipeline

Date: 14 October 2026

The user explicitly requested a simple Streamlit demo of the intended end-product
workflow, and clarified that its purpose is to show how the service will work.
This authorizes a bounded presentation prototype ahead of the CLI research gates.
It does not activate job-launching controls in the scientific application.

`app.py` and `prototype/` implement a separate, session-only demonstration. The
interface can launch an illustrative local job only on an explicit button click.
Reruns and navigation do not repeat that job. Saving upstream inputs invalidates
downstream example results. There are no background scientific jobs to own,
cancel or resume; durable job orchestration remains unresolved for the real product.

Real intake checks and causal rolling-reference replay are labelled separately
from fixed calibration fixtures. Every exported package is explicitly a
non-executable preview without a fitted GeCo model. Source CSVs are immutable;
uploads are not persisted. No scientific correctness or comparative benefit claim
is made. Existing 0/28 and 0/37 feature counts remain unchanged.

Design: slate navigation (#152c47), white workspace (#ffffff), pale blue sections
(#f3f7fc), cobalt controls (#245cce), secondary text (#637187). IBM Plex Sans with
a system fallback. A seven-step left-aligned workspace matches the actual service
sequence; sensor traces and quality findings carry the visual emphasis.

Verification commands and results are recorded in the progress tracker after
execution. The prototype's tested Python environment is independent of the
unverified upstream GeCo compatibility target.
