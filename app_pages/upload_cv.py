"""Original one-button Hugging Face CV extraction; no hybrid or local fallback."""
from __future__ import annotations

import hashlib
import streamlit as st

from job_hunter.config import settings
from job_hunter.cv.pdf import CVError, extract_pdf_text
from job_hunter.inference.client import HFGateway, InferenceFailure
from job_hunter.models import CandidateProfile
from job_hunter.session import replace_cv

st.title("Find jobs that actually fit you.")
st.write("Upload your CV. Let AI discover real opportunities and explain why they match — with evidence from original job postings.")
left, right = st.columns([3, 2], gap="large")

with left:
    st.subheader("Upload your CV")
    st.caption("Text-based PDF only · Maximum 5 MB · No account needed")
    uploaded = st.file_uploader(
        "Choose or drag a PDF here", type=["pdf"],
        key=f"cv_upload_{st.session_state.upload_epoch}",
    )
    st.info("🔐 Your CV is processed for this session only and is not permanently stored.")

    content_hash = hashlib.sha256(uploaded.getvalue()).hexdigest() if uploaded else ""
    if content_hash and st.session_state.get("cv_sha256") and content_hash != st.session_state.cv_sha256:
        replace_cv(preserve_upload=True)
        st.info("A different PDF was selected. Old profile and job results were cleared.")

    provider = settings().provider
    st.warning(
        "External AI processing: after you confirm, extracted CV text (not the PDF file) "
        f"will be sent to Hugging Face and its **{provider}** inference provider. "
        "Their data-handling policies may apply."
    )
    consent = st.checkbox(
        "I understand and agree to this CV-text processing.",
        value=False, key="original_cv_consent",
    )

    if st.button("Analyze CV", type="primary", disabled=uploaded is None or not consent,
                 width="stretch", key="original_cv_analyze"):
        if st.session_state.get("profile") is not None:
            replace_cv(preserve_upload=True)
        try:
            text = extract_pdf_text(uploaded.getvalue())
            with st.spinner("Extracting supported profile facts using Hugging Face..."):
                parsed = HFGateway().extract_profile(text)
            st.session_state.extraction = parsed
            st.session_state.original_profile = parsed.model_dump()
            st.session_state.profile = CandidateProfile(
                **parsed.model_dump(), profile_version=st.session_state.profile_version,
            )
            st.session_state.cv_name = uploaded.name
            st.session_state.cv_sha256 = content_hash
            st.session_state.cv_text = ""
            st.session_state.disclosure_accepted = consent
            st.session_state.profile_extraction_mode = "ai"
            st.switch_page("app_pages/review_profile.py")
        except CVError as error:
            st.error(str(error))
        except InferenceFailure as error:
            st.error(str(error))
        except Exception:
            st.error("Unable to analyze this PDF safely. Check that it contains selectable text.")

with right:
    st.subheader("How it works")
    st.markdown("**1. Upload CV**")
    st.caption("Read only the text in your PDF.")
    st.markdown("**2. Review Profile**")
    st.caption("Correct the skills and experience before searching.")
    st.markdown("**3. Set Preferences**")
    st.caption("Tell us what roles and restrictions matter.")
    st.markdown("**4. Find Jobs**")
    st.caption("An AI agent calls real job tools.")
    st.markdown("**5. Inspect Evidence**")
    st.caption("See both skills match and eligibility, separately.")
