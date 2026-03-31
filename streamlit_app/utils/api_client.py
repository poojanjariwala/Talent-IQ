"""
API client for the Streamlit frontend to communicate with the FastAPI backend.
"""
import os
import requests
from typing import Optional, List, Dict, Any
import streamlit as st

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")


def _headers(token: Optional[str] = None) -> dict:
    h = {"Content-Type": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def _get_token() -> Optional[str]:
    return st.session_state.get("token")


def handle_response(response: requests.Response) -> dict:
    if response.status_code == 204:
        return {}
        
    try:
        data = response.json()
    except Exception:
        data = {"detail": response.text}

    if not response.ok:
        detail = data.get("detail", "Unknown error")
        
        # User-friendly transformation for technical errors
        if response.status_code == 422:
            if isinstance(detail, list):
                # FastAPI Validation Error list
                msgs = []
                for err in detail:
                    loc = ".".join([str(x) for x in err.get("loc", []) if x != "body"])
                    msg = err.get("msg", "Invalid input")
                    msgs.append(f"{loc}: {msg}" if loc else msg)
                detail = "; ".join(msgs)
            raise Exception(f"Check your input: {detail}")
        
        if response.status_code == 401:
            raise Exception("Invalid credentials or session expired.")
        if response.status_code == 403:
            raise Exception("You don't have permission to perform this action.")
        if response.status_code == 404:
            raise Exception("The requested information was not found.")
        if response.status_code >= 500:
            raise Exception("Server is having trouble. Please try again later.")
            
        raise Exception(f"API Error {response.status_code}: {detail}")
    
    return data


# ─── Auth ─────────────────────────────────────────────────────────────────────

def signup(email: str, password: str, full_name: str, **kwargs) -> dict:
    payload = {"email": email, "password": password, "full_name": full_name, **kwargs}
    r = requests.post(f"{API_BASE_URL}/auth/signup", json=payload)
    return handle_response(r)


def login(email: str, password: str) -> dict:
    r = requests.post(f"{API_BASE_URL}/auth/login", json={"email": email, "password": password})
    return handle_response(r)


def demo_login() -> dict:
    r = requests.post(f"{API_BASE_URL}/auth/demo")
    return handle_response(r)


def get_me(token: str) -> dict:
    r = requests.get(f"{API_BASE_URL}/auth/me", headers=_headers(token))
    return handle_response(r)


def update_profile(data: dict) -> dict:
    token = _get_token()
    r = requests.put(f"{API_BASE_URL}/auth/me", json=data, headers=_headers(token))
    return handle_response(r)


# ─── Jobs ─────────────────────────────────────────────────────────────────────

def list_jobs() -> List[dict]:
    token = _get_token()
    r = requests.get(f"{API_BASE_URL}/jobs/", headers=_headers(token))
    return handle_response(r)


def create_job(data: dict) -> dict:
    token = _get_token()
    r = requests.post(f"{API_BASE_URL}/jobs/", json=data, headers=_headers(token))
    return handle_response(r)


def update_job(job_id: str, data: dict) -> dict:
    token = _get_token()
    r = requests.put(f"{API_BASE_URL}/jobs/{job_id}", json=data, headers=_headers(token))
    return handle_response(r)


def delete_job(job_id: str) -> None:
    token = _get_token()
    r = requests.delete(f"{API_BASE_URL}/jobs/{job_id}", headers=_headers(token))
    handle_response(r)


# ─── Candidates ───────────────────────────────────────────────────────────────

def list_candidates(job_id: str) -> List[dict]:
    token = _get_token()
    r = requests.get(f"{API_BASE_URL}/candidates/job/{job_id}", headers=_headers(token))
    return handle_response(r)


def get_candidate(candidate_id: str) -> dict:
    token = _get_token()
    r = requests.get(f"{API_BASE_URL}/candidates/{candidate_id}", headers=_headers(token))
    return handle_response(r)


def upload_resumes(job_id: str, files: List[tuple]) -> dict:
    """files: list of (filename, bytes, content_type) tuples."""
    token = _get_token()
    headers = {"Authorization": f"Bearer {token}"}
    file_list = [("files", (name, data, ct)) for name, data, ct in files]
    r = requests.post(
        f"{API_BASE_URL}/candidates/upload",
        data={"job_id": job_id},
        files=file_list,
        headers=headers,
    )
    return handle_response(r)


def paste_resumes(job_id: str, texts: List[str]) -> dict:
    token = _get_token()
    r = requests.post(
        f"{API_BASE_URL}/candidates/paste",
        params={"job_id": job_id},
        json=texts,
        headers=_headers(token),
    )
    return handle_response(r)


def get_system_config() -> dict:
    try:
        r = requests.get(f"{API_BASE_URL}/config")
        return handle_response(r)
    except Exception:
        return {"enable_gemini": False}


def update_candidate(candidate_id: str, data: dict) -> dict:
    token = _get_token()
    r = requests.put(f"{API_BASE_URL}/candidates/{candidate_id}", json=data, headers=_headers(token))
    return handle_response(r)


def delete_candidate(candidate_id: str) -> None:
    token = _get_token()
    r = requests.delete(f"{API_BASE_URL}/candidates/{candidate_id}", headers=_headers(token))
    handle_response(r)


def download_resume(candidate_id: str) -> bytes:
    token = _get_token()
    r = requests.get(f"{API_BASE_URL}/candidates/{candidate_id}/download", headers=_headers(token))
    if not r.ok:
        raise Exception(f"Download failed: {r.status_code}")
    return r.content


# ─── Export ───────────────────────────────────────────────────────────────────

def export_excel(job_id: str) -> bytes:
    token = _get_token()
    r = requests.get(f"{API_BASE_URL}/export/job/{job_id}/excel", headers=_headers(token))
    if not r.ok:
        raise Exception(f"Export failed: {r.status_code}")
    return r.content
