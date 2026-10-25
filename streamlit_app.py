"""Job Hunter AI — five guarded Streamlit steps."""
import streamlit as st
from job_hunter.session import init_session

st.set_page_config(page_title="Job Hunter AI",page_icon="🎯",layout="wide",initial_sidebar_state="collapsed")
init_session()
st.markdown("""<style>
.block-container{max-width:1120px;padding-top:2rem;padding-bottom:3rem}
h1,h2,h3{letter-spacing:-.035em;color:#172b43}
[data-testid="stMetric"]{border:1px solid #d8e2ee;border-radius:14px;padding:14px;background:#fff}
.stButton>button[kind="primary"]{border-radius:11px;font-weight:650}
header[data-testid="stHeader"]{background:transparent}
</style>""",unsafe_allow_html=True)

pages=[
    st.Page("app_pages/upload_cv.py",title="Upload CV",icon="📄",url_path="upload",default=True),
    st.Page("app_pages/review_profile.py",title="Review Profile",icon="🪪",url_path="review"),
    st.Page("app_pages/preferences.py",title="Preferences",icon="🎛️",url_path="preferences"),
    st.Page("app_pages/find_jobs.py",title="Find Jobs",icon="🔎",url_path="search"),
    st.Page("app_pages/results.py",title="Results",icon="📋",url_path="results"),
]
page=st.navigation(pages,position="hidden")
st.markdown("### 🎯 Job Hunter AI")
st.caption("Real job sources  ·  Evidence-based decisions  ·  Privacy first")
steps=["Upload CV","Review Profile","Preferences","Find Jobs","Results"]
try: current=next(i for i,p in enumerate(pages) if p==page)
except StopIteration:current=0
cols=st.columns(5)
for i,(col,text) in enumerate(zip(cols,steps)):
    col.markdown(f"{'**' if i==current else ''}{'●' if i==current else '○'} {i+1}. {text}{'**' if i==current else ''}")
st.divider()
# Page-specific checks provide a second defense against direct URL navigation.
page.run()
