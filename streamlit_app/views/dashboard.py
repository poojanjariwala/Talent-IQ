import streamlit as st
from streamlit_app.utils import api_client
from streamlit_app.state import set_selected_job

def show_dashboard():
    recruiter = st.session_state.recruiter
    st.title(f"Welcome back, {recruiter['full_name']}")

    # Quick Stats
    jobs = api_client.list_jobs()
    st.session_state.jobs = jobs

    col1, col2, col3 = st.columns(3)
    col1.metric("Active Jobs", len(jobs))
    total_candidates = sum(j.get('candidate_count', 0) for j in jobs)
    col2.metric("Total Candidates", total_candidates)
    col3.metric("Company", recruiter.get('company_name', 'Independent'))

    st.markdown("---")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("Active Jobs")
        if not jobs:
            st.info("No active jobs. Create one to get started.")
        else:
            for job in jobs:
                with st.expander(f"**{job['title']}** - {job.get('candidate_count', 0)} candidates", expanded=False):
                    st.write(f"**Department:** {job.get('department', 'N/A')}")
                    st.write(f"**Location:** {job.get('location', 'N/A')}")
                    st.write(f"**Status:** {job['status']}")

                    c1, c2 = st.columns(2)
                    if c1.button("View Pipeline", key=f"view_{job['id']}"):
                        set_selected_job(job)
                        st.session_state.active_tab = "candidates"
                        st.rerun()
                    if c2.button("Edit Job", key=f"edit_{job['id']}"):
                        set_selected_job(job)
                        st.session_state.active_tab = "create_job"
                        st.rerun()

    with col_right:
        st.subheader("Quick Actions")
        if st.button("➕ Create New Job", use_container_width=True):
            st.session_state.selected_job = None
            st.session_state.selected_job_id = None
            st.session_state.active_tab = "create_job"
            st.rerun()

        if st.button("📤 Bulk Resume Upload", use_container_width=True):
            if not jobs:
                st.warning("Please create a job first.")
            else:
                st.session_state.active_tab = "upload_resumes"
                st.rerun()

        st.subheader("Company Profile")
        if recruiter.get('company_name'):
            st.write(f"**{recruiter['company_name']}**")
            st.write(f"Industry: {recruiter.get('company_industry', 'N/A')}")
            st.write(f"Size: {recruiter.get('company_size', 'N/A')}")
        else:
            st.info("Profile incomplete. Update in settings.")
