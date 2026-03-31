"""
Session state helpers for the Streamlit app.
"""
import streamlit as st
from typing import Optional


def init_state():
    """Initialize all session state variables."""
    defaults = {
        "authenticated": False,
        "token": None,
        "recruiter": None,
        "current_page": "landing",
        "selected_job_id": None,
        "selected_job": None,
        "selected_candidate_id": None,
        "selected_candidate": None,
        "candidates": [],
        "jobs": [],
        "active_tab": "dashboard",
        "upload_results": None,
        "email_draft": None,
        "filters": {},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def is_authenticated() -> bool:
    return st.session_state.get("authenticated", False)


def get_token() -> Optional[str]:
    return st.session_state.get("token")


def get_recruiter() -> Optional[dict]:
    return st.session_state.get("recruiter")


def login(token: str, recruiter: dict):
    st.session_state.authenticated = True
    st.session_state.token = token
    st.session_state.recruiter = recruiter
    st.session_state.current_page = "dashboard"


def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]


def navigate_to(page: str):
    st.session_state.current_page = page


def set_selected_job(job: dict):
    st.session_state.selected_job_id = job["id"]
    st.session_state.selected_job = job
    st.session_state.selected_candidate = None
    st.session_state.candidates = []


def set_selected_candidate(candidate: dict):
    st.session_state.selected_candidate_id = candidate["id"]
    st.session_state.selected_candidate = candidate
