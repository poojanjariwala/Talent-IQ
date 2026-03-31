import streamlit as st
from streamlit_app.utils import api_client

def show_resume_upload():
    st.title("Upload Resumes")

    jobs = st.session_state.get("jobs", [])
    if not jobs:
        st.warning("Please create a job first.")
        if st.button("New Job"):
            st.session_state.active_tab = "create_job"
            st.rerun()
        return

    job_options = {j["id"]: j["title"] for j in jobs}
    selected_job_id = st.selectbox(
        "Select Job Target",
        options=list(job_options.keys()),
        format_func=lambda x: job_options[x],
        index=0 if not st.session_state.selected_job_id else list(job_options.keys()).index(st.session_state.selected_job_id)
    )

    st.markdown("---")

    tab1, tab2 = st.tabs(["File Upload", "Paste Content"])

    with tab1:
        st.write("Upload PDF, DOCX, TXT, CSV, or XLSX files")
        uploaded_files = st.file_uploader(
            "Select Resume Files",
            accept_multiple_files=True,
            type=["pdf", "docx", "doc", "txt", "csv", "xlsx", "xls"]
        )

        if st.button("Process Files", disabled=not uploaded_files):
            with st.spinner("Processing resumes..."):
                files_payload = []
                for f in uploaded_files:
                    files_payload.append((f.name, f.getvalue(), f.type))

                try:
                    res = api_client.upload_resumes(selected_job_id, files_payload)
                    st.success(f"Successfully processed {res['processed']} files.")
                    st.session_state.upload_results = res.get("results", [])
                    st.session_state.active_tab = "candidates"
                    st.session_state.selected_job_id = selected_job_id
                    st.rerun()
                except Exception as e:
                    st.error(f"Upload failed: {e}")

    with tab2:
        st.write("Paste one or more resumes as raw text")
        pasted_text = st.text_area("Paste Content (separate multiple resumes with empty lines)", height=300)

        if st.button("Process Text", disabled=not pasted_text):
            with st.spinner("Parsing text..."):
                texts = [p.strip() for p in pasted_text.split("\n\n") if p.strip()]
                try:
                    res = api_client.paste_resumes(selected_job_id, texts)
                    st.success(f"Successfully processed {res['processed']} resumes.")
                    st.session_state.active_tab = "candidates"
                    st.session_state.selected_job_id = selected_job_id
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to process text: {e}")

    if st.button("Cancel"):
        st.session_state.active_tab = "dashboard"
        st.rerun()
