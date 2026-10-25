import streamlit as st
from job_hunter.models import CandidateProfile,Education,Experience,Project
from job_hunter.session import replace_cv

if st.session_state.get("profile") is None:
    st.switch_page("app_pages/upload_cv.py")
profile=st.session_state.profile
st.title("Review Your Profile")
st.caption(f"Step 2 of 5 · Extracted from {st.session_state.cv_name} · Please correct any inaccuracies")
st.info("CV-extracted facts are shown as CV. If you edit or add information, it will be marked User-provided. Missing information is never guessed.")

with st.form("review"):
    st.subheader("Skills")
    st.caption("Add, correct or remove skills (comma-separated).")
    skills=st.text_area("Skills",value=", ".join(profile.skills),height=90)
    st.subheader("Education")
    education=st.data_editor([e.model_dump() for e in profile.education] or [Education().model_dump()],num_rows="dynamic",use_container_width=True,
        column_config={"provenance":st.column_config.TextColumn("Source",disabled=True)},key="education_editor")
    st.subheader("Experience")
    experience=st.data_editor([e.model_dump() for e in profile.experience] or [Experience().model_dump()],num_rows="dynamic",use_container_width=True,
        column_config={"provenance":st.column_config.TextColumn("Source",disabled=True)},key="experience_editor")
    st.subheader("Relevant Projects")
    projects=st.data_editor([p.model_dump() for p in profile.projects] or [Project().model_dump()],num_rows="dynamic",use_container_width=True,
        column_config={"provenance":st.column_config.TextColumn("Source",disabled=True)},key="project_editor")
    submitted=st.form_submit_button("Confirm & Continue",type="primary",use_container_width=True)
if submitted:
    try:
        skill_list=list(dict.fromkeys(s.strip() for s in skills.split(",") if s.strip()))
        original=st.session_state.original_profile or {}
        def rebuilt(rows,key,cls):
            old=original.get(key,[])
            clean=[]
            for row in rows:
                if not any(str(v).strip() for k,v in row.items() if k!="provenance"):continue
                core={k:v for k,v in row.items() if k!="provenance"}
                is_original=any(all(str(o.get(k,""))==str(v) for k,v in core.items()) for o in old)
                clean.append(cls(**core,provenance="cv" if is_original else "user"))
            return clean
        updated=CandidateProfile(skills=skill_list,
            education=rebuilt(education,"education",Education),
            experience=rebuilt(experience,"experience",Experience),
            projects=rebuilt(projects,"projects",Project),
            user_added_skills=[s for s in skill_list if s not in original.get("skills",[])],
            profile_version=st.session_state.profile_version,confirmed=True)
        if not updated.usable():
            st.error("Add at least one skill, a meaningful experience entry, or a relevant project before continuing. Education alone is not enough.")
        else:
            st.session_state.profile=updated
            st.session_state.results=[]
            st.session_state.active_run=None
            st.switch_page("app_pages/preferences.py")
    except Exception:
        st.error("Please check the edited profile fields for invalid values.")
if st.button("← Back / Replace CV"):
    replace_cv();st.switch_page("app_pages/upload_cv.py")
