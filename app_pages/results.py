"""Evidence-first job results. Labels do not assert facts absent from the source."""
import streamlit as st
from job_hunter.session import replace_cv

if (not st.session_state.get("profile") or not st.session_state.get("preferences")
        or not st.session_state.get("result_mode")):
    st.switch_page("app_pages/upload_cv.py")

st.title("Evidence-Based Job Matches")
st.caption("Step 5 of 5 · Skills match is NOT the same as job eligibility")

if st.session_state.result_mode == "snapshot":
    st.warning(
        f"Dated Snapshot · Collected {st.session_state.collected_at} · "
        "Historical public job data; NOT live or reverified"
    )
else:
    st.info(
        "Live Search · Listings came from source APIs or a time-stamped cache. "
        "Job availability and employer requirements may change."
    )

results = st.session_state.results
cols = st.columns(3)
for col, label in zip(cols, ["Eligible", "Unknown", "Not Eligible"]):
    col.metric(label, sum(item.eligibility == label for item in results))


def _condition(assessment, name):
    return next((c for c in assessment.conditions if c.name == name), None)


def _status_text(condition, confirmed_label: str) -> str:
    if not condition or condition.state == "unknown":
        return "Not confirmed"
    if condition.state == "conflict":
        return "Does not meet selected requirement"
    if condition.state == "not_applicable":
        return "Not requested"
    return confirmed_label


if not results:
    st.warning(
        "No jobs were found in this run. This does not mean no jobs exist; "
        "try adjusting preferences or searching later."
    )
else:
    count_eligible = sum(item.eligibility == "Eligible" for item in results)
    count_unknown = sum(item.eligibility == "Unknown" for item in results)
    if not count_eligible and count_unknown == len(results):
        st.info("Unknown Only · Every listing needs more evidence before eligibility can be confirmed.")
    elif not count_eligible:
        st.warning("No Eligible Jobs · None of the assessed listings is confirmed eligible. "
                   "Unknown listings are not rejections; verify them with the employer.")
    c1, c2, c3 = st.columns(3)
    eligibility = c1.multiselect(
        "Eligibility", ["Eligible", "Unknown", "Not Eligible"],
        default=["Eligible", "Unknown", "Not Eligible"],
    )
    matches = c2.multiselect(
        "Skills match", ["Strong", "Partial", "Weak"],
        default=["Strong", "Partial", "Weak"],
    )
    sources = c3.multiselect(
        "Source", ["Greenhouse", "Remotive"],
        default=["Greenhouse", "Remotive"],
    )
    visible = [item for item in results if item.eligibility in eligibility
               and item.skills.label in matches and item.job.source in sources]
    st.caption(
        f"Showing {len(visible)} of {len(results)} jobs. "
        "Unknown means evidence is insufficient, NOT rejection."
    )
    if not visible:
        st.info("No jobs match these result filters. Adjust the filters above.")

    for item in visible:
        job = item.job
        remote = _condition(item, "Remote work")
        geography = _condition(item, "Geography")
        work_auth = _condition(item, "Work authorization")
        paid = _condition(item, "Paid only")
        posting = _condition(item, "Posting status")
        with st.container(border=True):
            a, b = st.columns([4, 1])
            with a:
                st.subheader(f"{job.title} · {job.company}")
                st.caption(
                    f"{job.source} | {job.location or 'Location unknown'} | "
                    f"{job.employment_type or 'Employment type unknown'}"
                )
            with b:
                st.markdown(f"**Eligibility: {item.eligibility}**")
                st.markdown(f"**Skills: {item.skills.label}**")

            if item.skills.core_missing:
                st.warning(
                    "Important skills not confirmed: "
                    + ", ".join(item.skills.core_missing)
                    + ". Review the detailed requirements before applying."
                )
            if remote is None or remote.state == "unknown":
                st.warning("Remote work NOT confirmed. Do not assume this is a remote position.")
            elif remote.state == "conflict":
                st.error("Remote-work requirement is explicitly not met.")

            if job.link_status == "unavailable":
                st.error("Unavailable · The original job link returned a removal/not-found status. "
                         "Do not assume applications are open.")
            elif posting is None or posting.state == "unknown":
                st.caption("Posting is historical or current availability has NOT been verified.")
            st.caption(
                "Location for your country: " + _status_text(geography, "Advertised scope includes your country")
                + " · Work authorization: " + _status_text(work_auth, "Explicitly confirmed")
                + " · Paid status: " + _status_text(paid, "Pay confirmed")
            )

            conflict = next((c for c in item.conditions if c.state == "conflict"), None)
            unknown = next((c for c in item.conditions if c.state == "unknown"), None)
            focus = conflict or unknown
            if focus:
                st.caption(f"{focus.name}: {focus.explanation}")
            st.caption(
                f"Matched: {', '.join(item.skills.matched[:6]) or 'Not confirmed'} · "
                f"Published/updated: {job.posted_at or 'Unknown'} · "
                f"Retrieved: {job.retrieved_at or 'Unknown'}"
            )

            with st.expander("View evidence and job details"):
                st.markdown("**Skills match**")
                st.write(item.skills.explanation)
                if item.skills.core_missing:
                    st.write("Important missing skills:", ", ".join(item.skills.core_missing))
                st.write("Matched:", ", ".join(item.skills.matched) or "None confirmed")
                st.write("Missing:", ", ".join(item.skills.missing) or "None confirmed")
                if item.evidence:
                    st.markdown("**Verbatim evidence from the job description**")
                    for quote in item.evidence:
                        st.caption(f"Source excerpt: {quote.excerpt}")
                else:
                    st.caption("No additional verifiable employer requirement quotes were extracted.")
                st.markdown("**Eligibility checks**")
                for condition in item.conditions:
                    st.write(f"**{condition.name} — {condition.state}**: {condition.explanation}")
                    for ev in condition.evidence:
                        st.caption(f"Evidence ({ev.field}): {ev.excerpt}")
                st.markdown("**Original job description (excerpt)**")
                st.write(job.description[:1300] or "Not available")
                if job.questions:
                    st.markdown("**Employer application questions**")
                    for question in job.questions[:8]:
                        st.caption(question)
                st.caption(
                    f"Source: {job.source} · Retrieved {job.retrieved_at or 'Unknown'} · "
                    "Check employer terms on the original posting"
                )

            if job.url.startswith("https://"):
                st.link_button("Open Original Job ↗", job.url)
            else:
                st.warning("Original source link unavailable.")

st.divider()
a, b = st.columns(2)
if a.button("← Edit Preferences / New Search", use_container_width=True):
    st.session_state.active_run = None
    st.session_state.results = []
    st.session_state.result_mode = ""
    st.switch_page("app_pages/preferences.py")
if b.button("Replace CV", use_container_width=True):
    replace_cv()
    st.switch_page("app_pages/upload_cv.py")
