"""Real intake checks and deliberately illustrative calibration artifacts."""
from __future__ import annotations

import io
import json
import zipfile

import numpy as np
import pandas as pd


def sample_data(days=14, seed=41):
    rng = np.random.default_rng(seed)
    n = days * 288
    t = np.arange(n)
    pump = ((t % 96) < 64).astype(int)
    level = 3.4 + .45 * np.sin(t / 45) + rng.normal(0, .025, n)
    flow = 24 + 9 * pump + 2 * np.sin(t / 45) + rng.normal(0, .35, n)
    pressure = 2.2 + .6 * pump + .08 * level + rng.normal(0, .025, n)
    aux = rng.normal(18, .2, n)
    aux[rng.random(n) < .24] = np.nan
    return pd.DataFrame({
        "timestamp": pd.date_range("2026-09-01", periods=n, freq="5min"),
        "level_m": level.round(3), "flow_m3h": flow.round(3),
        "pressure_bar": pressure.round(3), "pump_state": pump,
        "valve_position_pct": np.full(n, 100),
        "aux_temperature_c": aux.round(2),
    })


def read_csv(raw):
    frame = pd.read_csv(io.BytesIO(raw))
    frame.columns = frame.columns.str.strip()
    if frame.empty:
        raise ValueError("The CSV has no readings. Upload a file with a header and data rows.")
    if frame.columns.duplicated().any():
        raise ValueError("Column names must be unique.")
    if len(frame) > 150_000:
        raise ValueError("Use at most 150,000 rows in this presentation prototype.")
    return frame


def assess(frame, timestamp, excluded=None):
    times = pd.to_datetime(frame[timestamp], errors="coerce", format="mixed")
    errors = []
    if times.isna().any():
        errors.append("Some timestamps cannot be read. Correct them before continuing.")
    if times.duplicated().any():
        errors.append("Duplicate timestamps found. Resolve duplicate readings before continuing.")
    if not times.is_monotonic_increasing:
        errors.append("Timestamps must be in strictly increasing order; no automatic sorting was applied.")
    original = frame.copy()
    original[timestamp] = times
    clean = original
    removed = 0
    if excluded is not None:
        start, end = excluded
        mask = (times >= start) & (times < end)
        removed = int(mask.sum())
        clean = original.loc[~mask].copy()
    delta = times.diff().dt.total_seconds()
    sampling = float(delta[delta > 0].median()) if (delta > 0).any() else 0
    # Count contiguous observed support, never count an excluded/gap interval as exposure.
    clean_delta = clean[timestamp].diff().dt.total_seconds()
    exposure = float(clean_delta.where(clean_delta <= sampling * 1.5, 0).sum() / 86400) if sampling else 0
    channels = []
    for channel in frame.columns:
        if channel == timestamp:
            continue
        values = pd.to_numeric(clean[channel], errors="coerce").replace([np.inf, -np.inf], np.nan)
        missing = float(values.isna().mean()) if len(values) else 1.0
        unique = int(values.nunique())
        reason = "Suitable for demo"
        if channel.lower() in {"attack", "attack_id", "label", "fault", "fault_class", "anomaly"}:
            reason = "Evaluation annotation; exclude"
        elif missing > .1:
            reason = "Excessive missing readings"
        elif unique < 2:
            reason = "Insufficient variation"
        discrete = unique <= 8 and values.dropna().isin([0, 1]).all()
        channels.append({"Use": reason == "Suitable for demo", "Channel": channel,
                         "Role": "Actuator" if discrete else "Sensor",
                         "Unit": {"level_m":"m", "flow_m3h":"m³/h", "pressure_bar":"bar",
                                  "pump_state":"0 / 1", "valve_position_pct":"%",
                                  "aux_temperature_c":"°C"}.get(channel, "Unknown"),
                         "Missing %": round(missing * 100, 1), "Assessment": reason})
    table = pd.DataFrame(channels)
    if len(clean) < 200 or exposure < 1:
        errors.append("Insufficient history for this demo: supply at least one day and 200 usable rows.")
    if table.empty or int(table["Use"].sum()) < 2:
        errors.append("At least two varying, sufficiently complete numeric channels are needed for this demo.")
    gaps = int((delta > sampling * 1.5).sum()) if sampling else 0
    return {"data": clean, "channels": table, "errors": errors, "days": exposure,
            "sampling": sampling, "gaps": gaps, "removed": removed}


def candidates(budget):
    """A presentation fixture. These values are never computed detection results."""
    table = pd.DataFrame([
        {"Candidate": "Sensitive", "S": .8, "G": 1.0, "Episodes / day": 1.8, "Synthetic recall %": 96, "Delay (min)": 5},
        {"Candidate": "Balanced", "S": 1.2, "G": 1.5, "Episodes / day": .7, "Synthetic recall %": 89, "Delay (min)": 10},
        {"Candidate": "Conservative", "S": 1.8, "G": 2.0, "Episodes / day": .25, "Synthetic recall %": 76, "Delay (min)": 20},
    ])
    table["Meets budget"] = table["Episodes / day"] <= budget
    feasible = table.loc[table["Meets budget"]]
    selected = None if feasible.empty else feasible.sort_values("Synthetic recall %", ascending=False).iloc[0].to_dict()
    return table, selected


def package(project, result, selection, budget, metadata, source_hash, context):
    manifest = {"schema_version": "prototype-1", "project": project,
        "artifact_type": "NON_EXECUTABLE_DEMO_PACKAGE", "geco_integrated": False,
        "calibration_results": "ILLUSTRATIVE_FIXTURE_NOT_MEASURED",
        "source_sha256": source_hash, "sampling_seconds": result["sampling"],
        "preprocessing": "No filling, scaling, smoothing or resampling",
        "alarm_budget_per_day": budget, "disturbance_profile": ["bias", "drift", "freeze"],
        "selected_demo_settings": selection, "operating_context": context,
        "input_channels": metadata.to_dict(orient="records"),
        "real_attack_performance": "Not evaluated", "limitations": [
            "No trained GeCo model is included.", "All calibration scores are illustrative.",
            "Not suitable for deployment or safety decisions."]}
    report = f"""# {project} — demonstration report

This is a presentation prototype, not an experimental result.

## Uploaded-data checks (computed)
- Usable observed history: {result['days']:.2f} days
- Sampling interval: {result['sampling']:g} seconds
- Excluded rows: {result['removed']}
- Source SHA-256: {source_hash}

## Calibration (illustrative)
- Required budget: {budget:g} episodes/day
- Selected example: {selection['Candidate']}
- Example normal alarm burden: {selection['Episodes / day']} episodes/day
- Example synthetic recall: {selection['Synthetic recall %']}%
- Tested profile shown: bias, drift, freeze

The example metrics are fixed presentation fixtures and are not derived from the uploaded data.
No real-attack detection rate has been measured. No GeCo training or fitting was performed.
An executable detector package will require verified model equations, preprocessing,
dependencies, calibration evidence, upstream revision and a tested environment lock.
"""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("manifest.demo.json", json.dumps(manifest, indent=2, ensure_ascii=False))
        archive.writestr("validation-report.md", report)
        archive.writestr("input-schema.csv", metadata.to_csv(index=False))
        archive.writestr("model/README.txt", "Placeholder for future verified GeCo equations. No model is trained or included.\n")
        archive.writestr("dependencies.demo.json", json.dumps({"status":"illustrative", "checks":[
            {"target": c, "required_inputs": [{"channel":c,"lag":1},{"channel":c,"lag":0}]} for c in metadata["Channel"]]}, indent=2))
    return buffer.getvalue(), report


def replay(frame, timestamp, channel, training, sampling, scenario="Recorded readings"):
    """Causal rolling-reference illustration; explicitly not GeCo."""
    data = frame.copy()
    times = pd.to_datetime(data[timestamp], errors="coerce", format="mixed")
    if times.isna().any() or times.duplicated().any() or not times.is_monotonic_increasing:
        raise ValueError("Replay timestamps must be readable, unique and increasing.")
    if len(data) < 30:
        raise ValueError("Replay needs at least 30 readings.")
    deltas = times.diff().dt.total_seconds()
    if abs(float(deltas.median()) - sampling) > max(1, sampling * .05):
        raise ValueError("Replay sampling does not match the project. Use compatible readings.")
    values = pd.to_numeric(data[channel], errors="coerce").replace([np.inf, -np.inf], np.nan)
    reference_scale = float(pd.to_numeric(training[channel], errors="coerce").std())
    start, end = len(values)//3, len(values)//3 + max(12, len(values)//8)
    if scenario == "Incorrect reading":
        values.iloc[start:end] += max(reference_scale * 5, .5)
    elif scenario == "Missing measurement":
        values.iloc[start:end] = np.nan
    # Separate segments at gaps, and require fresh history after a missing reading.
    groups = ((deltas > sampling * 1.5) | values.isna()).cumsum()
    expected = values.groupby(groups).transform(lambda s: s.shift(1).rolling(12, min_periods=12).median())
    threshold = max(reference_scale * 1.5, .001)
    available = values.notna() & expected.notna()
    alarm = pd.Series(pd.NA, index=data.index, dtype="boolean")
    alarm.loc[available] = (values[available] - expected[available]).abs() > threshold
    states = np.where(values.isna(), "Unavailable", np.where(~available, "Initializing", np.where(alarm.fillna(False), "Alarm", "Supported")))
    trace = pd.DataFrame({"timestamp":times, "Reading":values, "Reference":expected,
                          "Alarm":alarm, "Monitoring status":states})
    episodes = int((alarm.fillna(False) & ~alarm.fillna(False).shift(1, fill_value=False)).sum())
    return trace, episodes, threshold
