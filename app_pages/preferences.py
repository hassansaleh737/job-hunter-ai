import streamlit as st
from job_hunter.models import Preferences

if st.session_state.get("profile") is None or not st.session_state.profile.confirmed:
    st.switch_page("app_pages/upload_cv.py")
st.title("Job Preferences")
st.caption("Step 3 of 5 · Help the agent find opportunities relevant to your goals")
previous=st.session_state.get("preferences")
with st.form("preferences_form"):
    roles=st.text_input("Target job roles *",value=", ".join(previous.roles) if previous else "AI Engineer, Python Developer",help="Use commas for multiple target roles.")
    levels=["Student / Intern","Entry-Level / Junior","Both"]
    level=st.selectbox("Experience level *",levels,index=levels.index(previous.level) if previous else 2)
    country=st.text_input("Applying from *",value=previous.country if previous else "Egypt")
    types=["Internship","Part-time","Full-time","Contract","Freelance"]
    employment=st.multiselect("Employment types (optional)",types,default=previous.employment_types if previous else ["Internship","Part-time"])
    paid_only=st.checkbox("Paid opportunities only",value=previous.paid_only if previous else False)
    st.text_input("Work mode",value="Remote Only",disabled=True)
    st.caption("Unknown salary, work authorization, or hiring-location details remain Unknown. Remote is not automatically Worldwide.")
    continue_btn=st.form_submit_button("Continue to Find Jobs →",type="primary",use_container_width=True)
if continue_btn:
    try:
        prefs=Preferences(roles=[x.strip() for x in roles.split(",") if x.strip()],level=level,country=country.strip(),
                          employment_types=employment,paid_only=paid_only)
        if not prefs.country: raise ValueError("Country is required")
        if st.session_state.get("active_run"):
            st.session_state.active_run.cancel()
        st.session_state.preferences=prefs
        st.session_state.active_run=None
        st.session_state.results=[]
        st.switch_page("app_pages/find_jobs.py")
    except Exception:
        st.error("Provide at least one target role, an experience level, and your applying-from country.")
if st.button("← Back to Profile"):
    st.switch_page("app_pages/review_profile.py")
