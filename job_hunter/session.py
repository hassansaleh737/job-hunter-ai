"""State operations called ONLY on the Streamlit script thread."""
from __future__ import annotations
import uuid
import streamlit as st


def init_session():
    defaults = {
        "profile_version": 0, "profile": None, "extraction": None,
        "cv_name": "", "cv_text": "", "cv_sha256": "",
        "preferences": None, "results": [], "active_run": None,
        "result_mode": "", "collected_at": "", "disclosure_accepted": False,
        "last_error": "", "original_profile": None, "upload_epoch": 0,
        "run_session_key": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    if st.session_state.run_session_key is None:
        st.session_state.run_session_key = uuid.uuid4().hex


def replace_cv(preserve_upload: bool = False):
    """Invalidate every candidate-dependent output, even for same-name PDFs."""
    run = st.session_state.get("active_run")
    if run:
        run.cancel()
    st.session_state.profile_version += 1
    if not preserve_upload:
        st.session_state.upload_epoch += 1
    for key, value in {
        "profile": None, "extraction": None, "cv_name": "", "cv_text": "",
        "cv_sha256": "", "preferences": None, "results": [],
        "active_run": None, "result_mode": "", "collected_at": "",
        "disclosure_accepted": False, "last_error": "", "original_profile": None,
    }.items():
        st.session_state[key] = value
