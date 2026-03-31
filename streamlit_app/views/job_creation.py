import streamlit as st
from streamlit_app.utils import api_client

def show_job_creation():
    job = st.session_state.get("selected_job")
    is_edit = job is not None

    st.title("Edit Job" if is_edit else "Create New Job")

    with st.form("job_form"):
        title = st.text_input("Job Title*", value=job["title"] if is_edit else "")
        col1, col2 = st.columns(2)
        department = col1.text_input("Department", value=job.get("department", "") if is_edit else "")
        location = col2.text_input("Location", value=job.get("location", "") if is_edit else "")

        col3, col4 = st.columns(2)
        emp_type = col3.selectbox("Employment Type", ["Full-time", "Part-time", "Contract", "Freelance", "Internship"], index=0)
        status = col4.selectbox("Job Status", ["open", "closed", "draft"], index=0 if not is_edit else ["open", "closed", "draft"].index(job["status"]))

        col5, col6 = st.columns(2)
        exp_min = col5.number_input("Min Experience (Years)", min_value=0, value=job.get("experience_min_years", 0) if is_edit else 0)
        exp_max = col6.number_input("Max Experience (Years)", min_value=0, value=job.get("experience_max_years", 0) if is_edit else 0)

        description = st.text_area("Job Description", value=job.get("description", "") if is_edit else "")

        required_skills = st.text_input("Required Skills (comma separated)", value=", ".join(job.get("required_skills", [])) if is_edit else "")
        nice_to_have = st.text_input("Nice to Have Skills (comma separated)", value=", ".join(job.get("nice_to_have_skills", [])) if is_edit else "")
        tech_stack = st.text_input("Tech Stack (comma separated)", value=", ".join(job.get("tech_stack", [])) if is_edit else "")

        submit = st.form_submit_button("Save Job", use_container_width=True)

        if submit:
            if not title:
                st.error("Job title is required")
                return

            payload = {
                "title": title,
                "department": department,
                "location": location,
                "employment_type": emp_type,
                "experience_min_years": int(exp_min),
                "experience_max_years": int(exp_max),
                "description": description,
                "required_skills": [s.strip() for s in required_skills.split(",") if s.strip()],
                "nice_to_have_skills": [s.strip() for s in nice_to_have.split(",") if s.strip()],
                "tech_stack": [s.strip() for s in tech_stack.split(",") if s.strip()],
                "status": status
            }

            try:
                if is_edit:
                    api_client.update_job(job["id"], payload)
                    st.success("Job updated successfully!")
                else:
                    api_client.create_job(payload)
                    st.success("Job created successfully!")

                st.session_state.active_tab = "dashboard"
                st.rerun()
            except Exception as e:
                st.error(f"Error saving job: {e}")

    if is_edit:
        if st.button("Delete Job", type="secondary"):
            if st.checkbox("Confirm Delete"):
                api_client.delete_job(job["id"])
                st.session_state.selected_job = None
                st.session_state.active_tab = "dashboard"
                st.rerun()
