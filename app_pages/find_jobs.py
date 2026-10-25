import streamlit as st
from job_hunter.agent.run_controller import RunController, RunBusyError, is_running
from job_hunter.snapshots.loader import DEFAULT_SNAPSHOT,load_snapshot,SnapshotError

if not st.session_state.get("preferences") or not st.session_state.get("profile"):
    st.switch_page("app_pages/upload_cv.py")
st.title("Find Jobs")
st.caption("Step 4 of 5 · Real tool activity, evidence verification, and transparent progress")
run=st.session_state.get("active_run")
if run is None:
    options=["Live Search","Dated Snapshot"]
    chosen=st.radio("Search mode",options,horizontal=True)
    if chosen=="Dated Snapshot":
        try:
            collected,jobs=load_snapshot()
            st.info(f"Dated Snapshot · Collected {collected} · {len(jobs)} real public postings · Not live or reverified")
        except SnapshotError as e:
            st.warning(str(e))
    else:
        st.info("Live Search requests job listings from Remotive and four public Greenhouse boards. Results depend on current availability.")
    previous_finishing = is_running(st.session_state.run_session_key)
    if previous_finishing:
        st.warning("Previous search is still finishing its network request. Start will be available when it exits.")
    if st.button("Start Agent Search",type="primary",use_container_width=True,
                 disabled=previous_finishing):
        if chosen=="Dated Snapshot" and not DEFAULT_SNAPSHOT.exists():
            st.error("Create a real-data snapshot before selecting this mode.")
        else:
            try:
                st.session_state.active_run=RunController(
                    st.session_state.profile,st.session_state.preferences,
                    "live" if chosen=="Live Search" else "snapshot",
                    st.session_state.profile_version,
                    session_key=st.session_state.run_session_key)
                st.rerun()
            except RunBusyError:
                st.warning("The previous search is still exiting; retry when it finishes.")
else:
    st.write(f"**Run status:** {run.state} · **Mode:** {'Live Search' if run.mode=='live' else 'Dated Snapshot'}")
    if run.mode=="snapshot":
        try:
            collected,_=load_snapshot()
            st.caption(f"Dated Snapshot collected {collected} · No live job-source calls · Job facts may be prepared beforehand")
        except SnapshotError: pass
    @st.fragment(run_every="1s")
    def show_progress():
        run.poll()
        for name,status in run.stages.items():
            symbols={"Pending":"○","Running":"◉","Completed":"✓","Failed":"✕","Skipped":"↷"}
            st.write(f"{symbols.get(status,'·')} **{name}** — {status}")
        if run.total:
            st.caption(f"Evaluated {run.checked}/{run.total} shortlisted jobs")
        with st.expander("Source activity",expanded=False):
            for msg in run.messages[-12:]:st.caption(msg)
        if run.state=="Running":
            if st.button("Cancel Search",key="cancel_run"):
                run.cancel();st.rerun()
        elif run.state=="Completed":
            st.success(f"Completed · {len(run.result)} evidence-based job assessments")
            if any(v in ("Failed","Partial") for v in run.outcomes.values()):
                st.warning("Partial results: one or more job sources failed. See Source activity.")
            if st.button("View Results →",type="primary",key="to_results"):
                if run.version==st.session_state.profile_version:
                    st.session_state.results=run.result
                    st.session_state.result_mode=run.mode
                    st.session_state.collected_at=run.collected
                    st.switch_page("app_pages/results.py")
        elif run.state in ("Cancelled","Failed"):
            st.warning(f"Search {run.state.lower()}. You can explicitly retry.")
            if st.button("Retry Search",key="retry_run"):
                if not run.future.done():
                    st.info("Finishing the cancelled network request; retry will be available shortly.")
                else:
                    st.session_state.active_run=None
                    st.rerun()
    show_progress()
if st.button("← Edit Preferences",key="back_pref"):
    if run:run.cancel()
    st.session_state.active_run=None
    st.switch_page("app_pages/preferences.py")
