import os
import sys
# Fix for Streamlit Cloud module path
sys.path.append(os.getcwd())

import streamlit as st
from streamlit_app.state import init_state, logout, navigate_to
from streamlit_app.views import landing, dashboard, job_creation, resume_upload, candidate_review, bulk_email, interview_scheduler

# Layout configuration
st.set_page_config(
    page_title="TalentIQ | Rebuild",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium UI Theme & CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

    * {
        font-family: 'Outfit', sans-serif !important;
    }

    .stApp {
        background: #0F111A;
        color: #E6E6E6;
    }

    /* Input Fields styling */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
        background-color: #1A1C26 !important;
        color: #FFFFFF !important;
        border: 1px solid #2D303E !important;
        border-radius: 8px !important;
        padding: 12px !important;
    }

    /* Labels - FIXING THE VISIBILITY ISSUE */
    label[data-testid="stWidgetLabel"] {
        color: #B0B3C1 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        margin-bottom: 8px !important;
    }

    /* Titles */
    h1, h2, h3 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #080A0F !important;
        border-right: 1px solid #1A1C26;
    }

    .sidebar-header {
        font-size: 1.4rem;
        font-weight: 700;
        margin: 2rem 0;
        text-align: center;
        background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2);
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(79, 70, 229, 0.35);
    }

    /* Secondary Buttons */
    .stButton>button[kind="secondary"] {
        background: transparent !important;
        border: 1px solid #2D303E !important;
        color: #B0B3C1 !important;
    }

    /* Metric */
    [data-testid="stMetricValue"] {
        color: #7C3AED !important;
        font-weight: 700 !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background-color: transparent !important;
    }

    .stTabs [data-baseweb="tab"] {
        color: #888888 !important;
        font-weight: 600 !important;
    }

    .stTabs [aria-selected="true"] {
        color: #FFFFFF !important;
        border-bottom-color: #7C3AED !important;
    }

    /* Card like containers */
    .element-container:has(div.stExpander) div[data-testid="stExpander"] {
        background-color: #1A1C26 !important;
        border: 1px solid #2D303E !important;
        border-radius: 12px !important;
    }

    /* Alerts */
    div[data-testid="stNotification"] {
        background-color: #1A1C26 !important;
        color: #FFFFFF !important;
        border-radius: 10px !important;
        border: 1px solid #2D303E !important;
    }
    
    div[data-testid="stNotificationContent"] p {
        color: #E6E6E6 !important;
    }

    /* Sidebar Nav removal (final force) */
    ul[data-testid="main-menu-list"] {
        display: none !important;
    }
    
    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    /* Dataframe colors */
    [data-testid="stDataFrame"] {
        background-color: #1A1C26 !important;
        color: #FFFFFF !important;
    }
    </style>
""", unsafe_allow_html=True)

def main():
    init_state()

    # Handle Auth redirection
    if not st.session_state.authenticated:
        landing.show_landing()
        return

    # Sidebar Navigation
    with st.sidebar:
        st.markdown('<div class="sidebar-header">🤖 <b>TALENT IQ</b></div>', unsafe_allow_html=True)

        st.markdown(f"**{st.session_state.recruiter['full_name']}**")
        st.caption(f"{st.session_state.recruiter.get('company_name', 'Recruiter')}")

        st.markdown("---")

        if st.button("🏠 Dashboard", use_container_width=True):
            st.session_state.active_tab = "dashboard"
            st.rerun()

        if st.button("📂 Create Job", use_container_width=True):
            st.session_state.selected_job = None
            st.session_state.active_tab = "create_job"
            st.rerun()

        if st.button("📤 Upload Resumes", use_container_width=True):
            st.session_state.active_tab = "upload_resumes"
            st.rerun()

        st.markdown("---")
        if st.button("🔓 Logout", type="secondary", use_container_width=True):
            logout()
            st.rerun()

    # Route based on active_tab
    tab = st.session_state.get("active_tab", "dashboard")

    if tab == "dashboard":
        dashboard.show_dashboard()
    elif tab == "create_job":
        job_creation.show_job_creation()
    elif tab == "upload_resumes":
        resume_upload.show_resume_upload()
    elif tab == "candidates":
        candidate_review.show_candidate_review()
    elif tab == "bulk_email":
        bulk_email.show_bulk_email()
    elif tab == "interview_scheduler":
        interview_scheduler.show_interview_scheduler()
    else:
        st.session_state.active_tab = "dashboard"
        st.rerun()

if __name__ == "__main__":
    main()
