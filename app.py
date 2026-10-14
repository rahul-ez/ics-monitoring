"""Run with: python -m streamlit run app.py"""
from __future__ import annotations

import hashlib
import html
import time

import pandas as pd
import streamlit as st

from prototype.demo import assess, candidates, package, read_csv, replay, sample_data

st.set_page_config(page_title="Relay | Industrial monitoring", page_icon="◈", layout="wide")

STEPS = ["Create project", "Check data", "Monitoring requirement", "Disturbance profile",
         "Train & calibrate", "Review & export", "Shadow monitoring"]
S = st.session_state
if "step" not in S:
    S.update(step=0, unlocked=0, project=None, assessment=None, metadata=None,
             requirement=None, profile=False, calibration=None, replay_result=None)


def navigate(step):
    S.step = step


def advance(step):
    S.unlocked = max(S.unlocked, step)
    S.step = step
    st.rerun()


def invalidate(after):
    """Saved upstream changes invalidate dependent artifacts and navigation."""
    if after <= 1:
        S.assessment = S.metadata = None
    if after <= 2:
        S.requirement = None
    if after <= 3:
        S.profile = False
    if after <= 4:
        S.calibration = S.replay_result = None
    S.unlocked = after


st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;450;500;600;700&display=swap');
html, body, [class*="css"], .stApp {font-family:'IBM Plex Sans',sans-serif;}
.stApp {background:#fff;}
[data-testid="stSidebar"] {background:#152c47; border-right:1px solid #243e5d;}
[data-testid="stSidebar"] * {color:#dce6f2;}
[data-testid="stSidebar"] button {background:transparent; border:1px solid #37506d; text-align:left;}
[data-testid="stSidebar"] button:hover {background:#284564; border-color:#83a7e3;}
[data-testid="stSidebar"] button:disabled {opacity:.4;}
[data-testid="stSidebar"] [data-testid="stProgress"] {margin:10px 0 20px;}
[data-testid="stHeader"] {background:transparent;}
.block-container {max-width:1260px; padding:2rem 3rem 3.5rem;}
h1 {font-size:2.55rem!important; letter-spacing:-1.3px; font-weight:600!important; margin-bottom:.35rem;}
h2 {font-size:1.45rem!important; font-weight:600!important; letter-spacing:-.3px;}
h3 {font-size:1.12rem!important; font-weight:600!important;}
p {line-height:1.6;}
.brand {font-size:29px; font-weight:600; letter-spacing:-1px; margin:10px 0 0; color:white;}
.brand span {color:#88b8ff; margin-right:8px;}
.sidebar-note {font-size:12px; color:#b2c3d9!important; line-height:1.7; padding-top:20px;}
.topline {display:flex; justify-content:space-between; gap:16px; align-items:center; border-bottom:1px solid #e3e9f1; padding-bottom:17px; margin-bottom:26px; color:#65748a; font-size:13px;}
.demo-tag {background:#edf3ff;color:#245cce;padding:5px 11px;border-radius:5px;font-weight:500;white-space:nowrap;}
.intro {font-size:17px; color:#637187; max-width:740px; margin:0 0 25px;}
.panel {background:#f3f7fc;border-left:3px solid #245cce;padding:22px 25px;border-radius:0 8px 8px 0;margin-bottom:20px;}
.panel h3 {margin:0 0 5px;}
.panel p {margin:0;color:#576a82;font-size:14px;}
.process {display:flex;align-items:center;gap:12px;padding:14px 0;border-bottom:1px solid #e3e9f1;}
.process .n {width:28px;height:28px;border-radius:50%;background:#e9f0fc;color:#245cce;display:flex;align-items:center;justify-content:center;font-size:13px;flex-shrink:0;}
.process p {margin:0;font-size:14px;}
.process small {color:#69798d;}
.footer {border-top:1px solid #e3e9f1;margin-top:32px;padding-top:15px;font-size:12px;color:#778397;}
[data-testid="stMetric"] {border-top:2px solid #dbe5f4;padding-top:10px;}
[data-testid="stMetricValue"] {font-size:1.8rem;}
[data-testid="stFileUploader"] {border-radius:8px;}
.stButton button, .stDownloadButton button {border-radius:6px;min-height:42px;font-weight:500;}
.stButton button:focus-visible {outline:3px solid #88b8ff;}
@media(max-width:750px){.block-container{padding:1.2rem;}h1{font-size:2rem!important;}.topline{flex-wrap:wrap;}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important;}}
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="brand"><span>◈</span> Relay</div>', unsafe_allow_html=True)
    st.caption("Industrial monitoring workspace")
    st.divider()
    st.markdown(f"**{html.escape(S.project['name']) if S.project else 'New monitoring project'}**")
    st.caption("Setup & trial")
    st.progress(S.unlocked / 6)
    for index, label in enumerate(STEPS):
        prefix = "●" if S.step == index else ("✓" if index < S.unlocked else str(index + 1))
        st.button(f"{prefix}  {label}", key=f"nav_{index}", width="stretch",
                  disabled=index > S.unlocked, on_click=navigate, args=(index,))
    st.markdown('<div class="sidebar-note">Presentation prototype<br>Data checks are computed. Calibration scores are illustrative. GeCo integration is pending.</div>', unsafe_allow_html=True)
    st.divider()
    if st.button("Start a new demo", width="stretch"):
        S.clear()
        st.rerun()

project_name = html.escape(S.project["name"]) if S.project else "New project"
st.markdown(f'<div class="topline"><span>Workspace / {project_name}</span><span class="demo-tag">Interactive service demo</span></div>', unsafe_allow_html=True)
st.caption(f"Step {S.step + 1} of 7")


def heading(title, subtitle):
    st.title(title)
    st.markdown(f'<p class="intro">{subtitle}</p>', unsafe_allow_html=True)


def back(step):
    st.button("Back", key=f"back_{step}", on_click=navigate, args=(step,))


if S.step == 0:
    heading("Turn normal readings into a monitoring plan.",
            "Start with your plant’s operating history. Review the data, set an alarm requirement, and see how automatic calibration would work.")
    left, right = st.columns([1.65, 1], gap="large")
    with left:
        st.subheader("Create your monitoring project")
        name = st.text_input("Plant or subsystem name", value=S.project["name"] if S.project else "Pumping Station A", max_chars=100)
        source = st.radio("Normal operating data", ["Use the sample dataset", "Upload my CSV"], horizontal=True)
        if source == "Use the sample dataset":
            raw = sample_data().to_csv(index=False).encode()
            st.markdown('<div class="panel"><h3>Pumping Station A</h3><p>14 days · 5-minute readings · 6 process channels<br>Synthetic level, flow, pressure, pump state, valve position and auxiliary temperature.</p></div>', unsafe_allow_html=True)
            st.download_button("Download sample CSV", raw, "pumping_station_normal.csv", "text/csv", on_click="ignore")
            st.caption("To demonstrate an upload, download this CSV and choose ‘Upload my CSV’.")
        else:
            uploaded = st.file_uploader("Upload normal operating data", type=["csv"], help="A timestamp column and numeric process channels. Maximum 20 MB / 150,000 rows.")
            raw = uploaded.getvalue() if uploaded else None
        context = st.text_area("Operating context (optional)", value=S.project["context"] if S.project else "Water transfer subsystem with a cycling pump. Units are included in the sample channel names.", height=95)
        confirmed = st.checkbox("I confirm these readings represent normal operation, apart from intervals I will exclude in the next step.")
        if st.button("Create project & check data", type="primary", disabled=not(raw and confirmed and name.strip()), width="stretch"):
            try:
                frame = read_csv(raw)
            except (ValueError, UnicodeError, pd.errors.ParserError) as error:
                st.error(str(error))
            else:
                invalidate(1)
                S.pop("channel_editor", None)
                S.project = {"name":name.strip(), "context":context, "frame":frame,
                             "hash":hashlib.sha256(raw).hexdigest(), "source":source}
                advance(1)
    with right:
        st.subheader("From history to shadow monitoring")
        for n, (title, detail) in enumerate([
            ("Understand the data", "Check channels, quality and usable history."),
            ("Define the requirement", "Choose an alarm burden your team can review."),
            ("Calibrate & review", "Compare settings against offline disturbances."),
            ("Export & trial", "Review a detector package and replay new readings.")], 1):
            st.markdown(f'<div class="process"><span class="n">{n}</span><p>{title}<br><small>{detail}</small></p></div>', unsafe_allow_html=True)
        st.info("Normal history is enough to start. You do not need to provide attack examples.")

elif S.step == 1:
    heading("Know what your data can support.", "Confirm the timestamp and channel descriptions. Unsuitable history should stop the workflow before training.")
    frame = S.project["frame"]
    timestamp = st.selectbox("Timestamp column", frame.columns, index=list(frame.columns).index("timestamp") if "timestamp" in frame else 0)
    with st.expander("Exclude a maintenance or abnormal interval"):
        excluded_enabled = st.checkbox("Exclude an interval from the normal history")
        x, y = st.columns(2)
        start_text = x.text_input("Start (inclusive)", placeholder="2026-09-03 08:00:00")
        end_text = y.text_input("End (exclusive)", placeholder="2026-09-03 12:00:00")
        st.caption("The original upload stays unchanged. This demo supports one exclusion interval.")
    excluded, exclusion_error = None, None
    if excluded_enabled:
        try:
            if not start_text or not end_text:
                raise ValueError("Enter both interval boundaries.")
            start, end = pd.Timestamp(start_text), pd.Timestamp(end_text)
            if start >= end:
                raise ValueError("The end must be after the start.")
            excluded = (start, end)
        except (ValueError, TypeError) as error:
            exclusion_error = str(error)
    try:
        result = assess(frame, timestamp, excluded)
    except (ValueError, TypeError, AttributeError) as error:
        st.error(f"Could not interpret the time column or exclusion: {error}")
        st.stop()
    if exclusion_error:
        result["errors"].append(exclusion_error)
    a, b, c, d = st.columns(4)
    a.metric("Uploaded readings", f"{len(frame):,}")
    b.metric("Usable history", f"{result['days']:.1f} days")
    c.metric("Sampling interval", f"{result['sampling']/60:g} min")
    d.metric("Excluded readings", f"{result['removed']:,}")
    st.subheader("Channel assessment")
    st.caption("Confirm roles and units. The demo flags >10% missing data and channels with no variation; these are prototype screening rules.")
    table = st.data_editor(result["channels"], hide_index=True, width="stretch",
        disabled=["Channel", "Missing %", "Assessment"],
        column_config={"Use":st.column_config.CheckboxColumn("Include"),
                       "Role":st.column_config.SelectboxColumn(options=["Sensor", "Actuator"]),
                       "Unit":st.column_config.TextColumn("Unit / state")}, key="channel_editor")
    selected = table.loc[table["Use"]]
    unsuitable = selected.loc[selected["Assessment"] != "Suitable for demo"]
    if len(selected) < 2:
        result["errors"].append("Select at least two suitable channels.")
    if not unsuitable.empty:
        result["errors"].append("Uncheck channels flagged as unsuitable before continuing.")
    if not (selected["Role"] == "Sensor").any():
        result["errors"].append("Select at least one sensor channel for the replay demonstration.")
    if result["gaps"]:
        st.warning(f"{result['gaps']} sampling gaps found. Gaps are excluded from observed exposure; replay resets its reference after a gap.")
    for error in result["errors"]:
        st.error(error)
    if not result["errors"]:
        st.success(f"{len(selected)} channels pass the demo checks. Suitability for GeCo still requires baseline fitting.")
    with st.expander("Inspect uploaded readings"):
        st.dataframe(frame.head(100), hide_index=True, width="stretch")
        plot_channels = selected["Channel"].head(3).tolist()
        if plot_channels:
            chart = result["data"].set_index(timestamp)[plot_channels].apply(pd.to_numeric, errors="coerce")
            st.line_chart(chart.iloc[::max(1,len(chart)//500)], height=220)
            st.caption("Channels are in their original units; no normalization was applied.")
    if st.button("Confirm data & continue", type="primary", disabled=bool(result["errors"])):
        invalidate(2)
        S.assessment, S.metadata, S.timestamp = result, selected.copy(), timestamp
        S.exclusion = [str(x) for x in excluded] if excluded else None
        advance(2)
    back(0)

elif S.step == 2:
    heading("How many alarms can your team review?", "Set an alarm burden to test against. This is a selection requirement; future alarm rates can change.")
    left, right = st.columns([1.5, 1], gap="large")
    with left:
        budget = st.number_input("Acceptable false-alarm episodes per day", min_value=0.05, max_value=10.0, value=float(S.requirement["budget"]) if S.requirement else 1.0, step=.05)
        st.caption("An episode groups repeated alarms into one incident. The prototype illustrates a 15-minute merge gap.")
        days = S.assessment["days"]
        st.info(f"Available normal history: {days:.1f} days. A future pipeline will reserve separate training, calibration and untouched audit blocks.")
        if days * .2 * budget < 5:
            st.warning("The planned 20% audit block would contain fewer than five episodes at this budget. It is too short for a convincing low-rate assessment; more normal history is needed.")
        st.caption("History sufficiency is a demo heuristic, not a statistical confidence guarantee.")
        with st.expander("Advanced detector settings"):
            st.write("The intended service searches threshold and accumulation settings automatically. Users normally do not need to choose k, S or G.")
            st.code("k: fixed during the initial search\nS, G: searched automatically\nExact ranges: to be verified against the pinned GeCo implementation", language="text")
        if st.button("Save requirement & continue", type="primary"):
            invalidate(3)
            S.requirement = {"budget":budget, "merge_gap_minutes":15}
            advance(3)
        back(1)
    with right:
        st.markdown('<div class="panel"><h3>A requirement your team understands</h3><p>“We can investigate approximately one false-alarm episode per day.”<br><br>The service compares candidate configurations with that requirement and reports when none qualifies.</p></div>', unsafe_allow_html=True)
        st.subheader("What the report should show")
        st.write("Observed episodes per day, time in alarm, usable normal exposure and uncertainty. A quiet detector with no usable decisions is not a successful result.")

elif S.step == 3:
    heading("Choose what calibration should test.", "Disturbance profiles describe changes in readings. They do not establish whether the cause is a faulty sensor or an attacker.")
    st.markdown('<div class="panel"><h3>Balanced sensor disturbances · Recommended</h3><p>Bias, gradual drift and frozen readings. A shared set of offline tests balances sensitivity across three observable effects.</p></div>', unsafe_allow_html=True)
    a,b,c = st.columns(3, gap="large")
    for column, title, text in [(a,"Incorrect readings","A positive or negative offset changes a sensor reading."),
                               (b,"Deteriorating readings","A gradual drift moves a measurement away from its normal value."),
                               (c,"Unresponsive readings","A reading freezes while the surrounding process continues changing.")]:
        with column:
            st.subheader(title)
            st.write(text)
    st.info("Offline tests modify copies of normal data. Original readings remain unchanged.")
    with st.expander("Additional profiles planned for later"):
        st.dataframe(pd.DataFrame({"User concern":["Scaled readings", "Older or delayed readings", "Missing measurements"],
            "Offline tests":["Scaling", "Replay-like sequences and delay", "Dropouts and channel loss"],
            "Status":["Later customization", "Later timing tests", "Primarily coverage evaluation"]}), hide_index=True, width="stretch")
        st.caption("Narrowing a future profile may reduce performance on other disturbances. Choose before reviewing final benchmark results.")
    if st.button("Use balanced profile & continue", type="primary"):
        invalidate(4)
        S.profile = True
        advance(4)
    back(2)

elif S.step == 4:
    heading("Let the service compare the options.", "Preview how the training and calibration job will progress. This demo animates the workflow and uses fixed example candidate results.")
    a,b,c = st.columns(3)
    a.metric("Selected channels", len(S.metadata))
    b.metric("Alarm requirement", f"≤ {S.requirement['budget']:g} / day")
    c.metric("Disturbance families", "3")
    st.warning("Simulated job: no GeCo fitting or calibration is performed. Example scores do not depend on your uploaded readings.")
    if st.button("Run demo calibration" if not S.calibration else "Run demo again", type="primary"):
        started = time.perf_counter()
        bar = st.progress(0, text="Preparing the demonstration")
        with st.status("Calibration preview running", expanded=True) as status:
            phases = ["Validate saved project inputs", "Reserve training, calibration and audit blocks (illustrated)",
                      "Fit process equations (simulated)", "Generate bias, drift and freeze tests (simulated)",
                      "Compare three example configurations", "Prepare the example selection report"]
            for index, phase in enumerate(phases):
                st.write(f"✓ {phase}")
                time.sleep(.22)
                bar.progress((index+1)/len(phases), text=phase)
            table, chosen = candidates(S.requirement["budget"])
            S.calibration = {"table":table, "selected":chosen, "elapsed":time.perf_counter()-started}
            S.replay_result = None
            status.update(label="Example selection complete" if chosen else "No feasible example configuration", state="complete" if chosen else "error", expanded=False)
        st.rerun()
    if S.calibration:
        st.caption(f"Actual demo UI runtime: {S.calibration['elapsed']:.2f} s · Local process · 3 illustrative candidates · GeCo resource usage not measured")
        chosen = S.calibration["selected"]
        if chosen:
            st.success("Demo outcome: a configuration meeting the example alarm budget was found.")
            st.caption("Detection and stability values shown next are illustrative. A real job must verify both.")
            if st.button("Review example result", type="primary"):
                advance(5)
        else:
            st.error("Demo outcome: no tested configuration met the requirement with adequate detection.")
            st.write("The lowest example rate is 0.25 episodes/day. Revisit the requirement or collect more representative history; the service must not silently relax your budget.")
            if st.button("Revise monitoring requirement"):
                navigate(2)
                st.rerun()
    back(3)

elif S.step == 5:
    heading("Review the evidence before the trial.", "Inspect the example selection, understand its limits and download a preview of the detector package structure.")
    selected = S.calibration["selected"]
    a,b,c,d = st.columns(4)
    a.metric("Example configuration", selected["Candidate"])
    b.metric("Example alarm episodes", f"{selected['Episodes / day']:g} / day")
    c.metric("Example synthetic recall", f"{selected['Synthetic recall %']}%")
    d.metric("Real-attack performance", "Not evaluated")
    st.caption("All selection metrics are illustrative fixtures. Synthetic recall is not a real-attack detection rate.")
    tab1, tab2, tab3 = st.tabs(["Calibration comparison", "Package contents", "Validation & limitations"])
    with tab1:
        st.subheader("Three example trade-offs")
        st.dataframe(S.calibration["table"], hide_index=True, width="stretch")
        st.bar_chart(S.calibration["table"].set_index("Candidate")[["Synthetic recall %"]], color="#245cce", height=235)
        st.caption("In the real service, stable performance across blocks and seeds will be checked before selection.")
    with tab2:
        st.code("detector-preview.zip\n  manifest.demo.json\n  input-schema.csv\n  dependencies.demo.json\n  validation-report.md\n  model/README.txt  # no trained model included", language="text")
        st.write("The eventual executable package will add trained equations, frozen settings, complete dependencies, preprocessing and tested version information.")
    with tab3:
        st.info("Computed: uploaded-data quality, usable history and channel descriptions. Illustrated: fitting, selection, synthetic scores and detector dependencies.")
        st.write("This prototype does not validate attack detection, guarantee future alarm rates, establish safety or connect to industrial equipment. Replay uses a causal rolling reference to illustrate reviewable alarms.")
    blob, report = package(S.project["name"], S.assessment, selected, S.requirement["budget"], S.metadata, S.project["hash"], S.project["context"])
    x,y = st.columns(2)
    x.download_button("Download demo detector package", blob, "detector-preview.zip", "application/zip", type="primary", width="stretch", on_click="ignore")
    y.download_button("Download evidence report", report, "demo-validation-report.md", "text/markdown", width="stretch", on_click="ignore")
    st.caption("Preview exports are marked non-executable. They contain no raw recordings or trained GeCo model.")
    if st.button("Continue to shadow monitoring", type="primary"):
        advance(6)
    back(4)

elif S.step == 6:
    heading("Trial the experience on new readings.", "Replay recorded data in shadow mode. Review alarms and unavailable intervals while leaving the physical process untouched.")
    st.info("Replay illustration: a causal rolling median is the reference, not a trained GeCo detector. The example calibration settings are not applied to this heuristic.")
    x,y,z = st.columns([1.4, 1, 1])
    mode = x.selectbox("Replay source", ["Generated trial readings", "Upload replay CSV"])
    sensors = S.metadata.loc[S.metadata["Role"] == "Sensor", "Channel"].tolist()
    channel = y.selectbox("Channel to review", sensors)
    scenario = z.selectbox("Demo scenario", ["Recorded readings", "Incorrect reading", "Missing measurement"], disabled=mode != "Generated trial readings")
    new_raw = None
    if mode == "Upload replay CSV":
        uploaded = st.file_uploader("Compatible new readings", type="csv", key="replay_upload")
        new_raw = uploaded.getvalue() if uploaded else None
    else:
        trial = sample_data(days=2, seed=83)
        trial["timestamp"] = pd.date_range("2026-09-15", periods=len(trial), freq="5min")
        new_raw = trial.to_csv(index=False).encode()
        st.download_button("Download trial readings CSV", new_raw, "pumping_station_trial.csv", "text/csv", on_click="ignore")
    current_key = hashlib.sha256((new_raw or b"") + f"{mode}|{channel}|{scenario}".encode()).hexdigest()
    if st.button("Run recorded-data replay", type="primary", disabled=new_raw is None):
        try:
            trial = read_csv(new_raw)
            required = [S.timestamp] + S.metadata["Channel"].tolist()
            missing = [name for name in required if name not in trial]
            if missing:
                raise ValueError(f"Missing required input columns: {', '.join(missing)}. Use compatible data or create a new project.")
            trace, episodes, threshold = replay(trial, S.timestamp, channel, S.assessment["data"], S.assessment["sampling"], scenario if mode == "Generated trial readings" else "Recorded readings")
            S.replay_result = {"key":current_key, "trace":trace, "episodes":episodes, "threshold":threshold}
        except (ValueError, UnicodeError, pd.errors.ParserError) as error:
            S.replay_result = None
            st.error(str(error))
    output = S.replay_result
    if output and output["key"] == current_key:
        trace = output["trace"]
        a,b,c = st.columns(3)
        a.metric("Illustrative alarm episodes", output["episodes"])
        b.metric("Comparable readings", f"{trace['Alarm'].notna().mean():.1%}")
        c.metric("Missing readings", int(trace["Reading"].isna().sum()))
        st.subheader(f"{channel}: reading and rolling reference")
        st.line_chart(trace.set_index("timestamp")[["Reading", "Reference"]], color=["#245cce", "#98a9bd"], height=300)
        st.caption(f"Heuristic deviation threshold: {output['threshold']:.3g} channel units. First 12 valid readings initialize the reference; missing measurements emit no anomaly decision.")
        events = trace.loc[trace["Monitoring status"].ne(trace["Monitoring status"].shift()), ["timestamp", "Monitoring status"]]
        st.subheader("Review timeline")
        st.dataframe(events, hide_index=True, width="stretch")
        with st.expander("What does monitoring status mean?"):
            st.write("Supported: this one illustrative check has enough input history. Alarm: its deviation exceeded the heuristic threshold. Unavailable: the target measurement is missing. Initializing: valid history is being collected. These statuses do not establish plant safety or attacker intent.")
        st.download_button("Download replay trace", trace.to_csv(index=False), "demo-replay.csv", "text/csv", on_click="ignore")
    else:
        st.markdown('<div class="panel"><h3>Ready for a shadow trial</h3><p>Run the replay to inspect readings, example alarms and monitoring availability. Try an incorrect reading, then a missing measurement to see the difference.</p></div>', unsafe_allow_html=True)
    st.caption("Live historian integration and the full dependency-aware coverage engine are later engineering steps.")
    back(5)

st.markdown('<div class="footer">Relay prototype · Normal history → calibration → evidence → shadow trial · Session-only workspace</div>', unsafe_allow_html=True)
