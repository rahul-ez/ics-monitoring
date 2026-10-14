# Relay — industrial monitoring service demo

A Streamlit presentation prototype of the intended service: normal operating
history → data assessment → alarm requirement → disturbance profile → automatic
calibration → detector export → shadow monitoring.

## Run locally (Windows / PowerShell)

```powershell
py -3.11 -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements-demo.txt
.venv/Scripts/python.exe -m streamlit run app.py
```

Open <http://localhost:8501>. The launcher `run-demo.ps1` uses the project virtual
environment and keeps Streamlit in the current terminal. Stop it with Ctrl+C.
The verified prototype dependency versions are in `requirements-demo.lock`.
This lock is separate from the future research application's environment.

## Presentation walkthrough

1. Keep **Pumping Station A** and choose the bundled sample. Alternatively upload
   `sample-data/pumping_station_normal.csv`. Confirm normal operation.
2. Confirm timestamps, roles and units. The sample has four suitable channels,
   one constant valve channel and one auxiliary channel with excessive missingness.
   Leave the two unsuitable channels excluded. Optional maintenance exclusion uses
   a half-open interval `[start, end)` without editing the source upload.
3. Keep the requirement at **1 episode/day**. Read the warning about limited audit
   history; the demo does not imply two weeks proves a rare alarm rate.
4. Choose the recommended **bias, drift and freeze** profile.
5. Run demo calibration and review the illustrated progress. The balanced example
   meets the budget. For the failure path, try **0.10 episodes/day**: none qualifies.
6. Download the non-executable detector-package preview and evidence report.
7. Run the generated trial with **Incorrect reading**, then **Missing measurement**.
   Alternatively upload `sample-data/pumping_station_trial.csv` with compatible
   inputs. Missing readings produce unavailable decisions rather than false normal
   readings. Download the replay trace for review.

To demonstrate insufficient history, upload `sample-data/insufficient_history.csv`.
To demonstrate manual upload, download the sample from the first screen, choose
**Upload my CSV**, and select that file.

## What works and what is illustrated

**Computed:** CSV reading, timestamp validation, channel completeness/variation,
user metadata, interval exclusion, sampling and observed exposure, export creation,
and causal rolling-reference replay. Replay is a single-channel UI illustration
and is independent of the example calibration settings.

**Illustrated:** GeCo fitting, data partitioning, pseudo-event calibration, candidate
metrics, configuration selection and check dependencies. Fixed candidate metrics
are used for every upload, labelled on screen and in exports. There is no trained
GeCo model, measured synthetic detection rate, real-attack result or deployment-ready
detector. Future detector packages must include the verified upstream revision and
environment, full equations, dependencies and frozen validation evidence.

Sessions are temporary and independent. Refreshing the browser can reset the demo.
Uploads remain in the local Streamlit process; the app writes no uploaded files to
disk and calls no external data service. It can run without the optional Google
Fonts request, using the system sans-serif font. There is no login or persistent
project store. Do not expose this presentation server as a production service.

## Verification

```powershell
.venv/Scripts/python.exe -m unittest discover -s tests -v
```

These checks exercise the complete Streamlit flow, no-feasible-settings outcome,
source immutability, insufficient-history handling, export labels and causal replay.
No implementation milestone in `context/build-plan.md` is claimed complete by this
prototype. See `docs/decisions/2026-10-14-presentation-prototype.md`.
