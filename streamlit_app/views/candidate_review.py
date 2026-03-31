import streamlit as st
import pandas as pd
from streamlit_app.utils import api_client

def show_candidate_review():
    job_id = st.session_state.get("selected_job_id")
    if not job_id:
        st.warning("Please select a job from the dashboard first")
        if st.button("Go to dashboard"):
            st.session_state.active_tab = "dashboard"
            st.rerun()
        return

    st.title("TalentIQ | Candidate Pipeline")

    # Feature Tip: Semantic Matching
    try:
        sys_config = api_client.get_system_config()
        is_gemini = sys_config.get("enable_gemini", False)
    except Exception:
        is_gemini = False

    if not is_gemini:
        with st.expander("💡 Understanding Match Scores", expanded=False):
            st.info("""
            Current matching is **Heuristic-based**. 
            To enable semantic AI matching, set `ENABLE_GEMINI=True` in your `.env`.
            """)

    # Status mapping for visual clarity
    status_map = {
        "new": "🆕 New",
        "shortlist": "🟢 Shortlisted",
        "hold": "🟠 On Hold",
        "reject": "🔴 Rejected"
    }

    # Fetch and list candidates for this job
    try:
        candidates = api_client.list_candidates(job_id)
        st.session_state.candidates = candidates
    except Exception as e:
        st.error(f"Error fetching candidates: {e}")
        return

    if not candidates:
        st.info("No candidates here yet.")
        if st.button("Upload Resumes"):
            st.session_state.active_tab = "upload_resumes"
            st.rerun()
        return

    # Header Metrics
    c1, c2, c3, c4 = st.columns(4)
    total = len(candidates)
    c1.metric("Total Applicants", total)
    c2.metric("New", len([c for c in candidates if c['bucket'] == 'new']))
    c3.metric("Shortlisted", len([c for c in candidates if c['bucket'] == 'shortlist']))
    c4.metric("Rejected", len([c for c in candidates if c['bucket'] == 'reject']))

    # Sidebar style filters for the candidate list
    with st.expander("Filter and Sort Options", expanded=False):
        col1, col2, col3 = st.columns(3)
        # SHOW ALL BY DEFAULT TO AVOID "NOT WORKING" CONFUSION
        all_options = ["new", "shortlist", "hold", "reject"]
        bucket_filter = col1.multiselect(
            "Bucket Filter", 
            all_options, 
            default=all_options,
            format_func=lambda x: status_map.get(x, x)
        )
        sort_by = col2.selectbox("Sort By", ["Match Score", "Years Exp", "Date Uploaded"], index=0)
        search_query = col3.text_input("Search Candidate")

    # Dataframe display
    df = pd.DataFrame(candidates)
    
    # 1. Apply local filtering first
    if bucket_filter:
        df = df[df['bucket'].isin(bucket_filter)]
    if search_query:
        df = df[df['full_name'].str.contains(search_query, case=False, na=False)]

        # 2. Check if we have any candidates LEFT after filtering
    if not df.empty:
        # Sorting
        if sort_by == "Match Score":
            df = df.sort_values(by="match_score", ascending=False)
        elif sort_by == "Years Exp":
            df = df.sort_values(by="total_experience_years", ascending=False)

        # Basic table for browsing
        display_cols = ["match_score", "full_name", "total_experience_years", "bucket", "stage"]
        
        # Prepare display dataframe
        df_display = df[display_cols].copy()
        df_display['bucket'] = df_display['bucket'].map(lambda x: status_map.get(x, x))
        df_display['stage'] = df_display['stage'].str.title()

        st.dataframe(
            df_display,
            column_config={
                "match_score": st.column_config.ProgressColumn("Match Score", min_value=0, max_value=100, format="%.2f"),
                "full_name": "Name",
                "total_experience_years": "Yrs Exp",
                "bucket": "Decision Status",
                "stage": "Pipeline Stage"
            },
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")
        st.subheader("Candidate Detail View")

        selected_name = st.selectbox(
            "Select Candidate to Review Details",
            options=df['full_name'].tolist(),
            index=0
        )

        if selected_name:
            try:
                candidate = next(c for c in candidates if c['full_name'] == selected_name)
                st.session_state.selected_candidate = candidate

                # Detailed cards
                col1, col2 = st.columns([1, 1])

                with col1:
                    st.markdown(f"### {candidate['full_name']}")
                    st.write(f"📧 {candidate.get('email', 'N/A')}")
                    st.write(f"📞 {candidate.get('phone', 'N/A')}")
                    st.write(f"📍 {candidate.get('location', 'N/A')}")
                    st.write(f"Years of Experience: **{candidate.get('total_experience_years', 'N/A')}**")
                    st.write(f"📄 Source: `{candidate.get('source_filename', 'N/A')}`")

                    st.write("---")
                    st.write("**Match Score Breakdown:**")
                    score_data = candidate.get("score_breakdown", {})
                    if score_data:
                        for k, v in score_data.items():
                            st.write(f"- {k.replace('_', ' ').capitalize()}: **{v:.2f}**")
                    else:
                        st.write("No score details available.")

                with col2:
                    st.markdown("### Decision Status")
                    new_bucket = st.selectbox(
                        "Action Bucket", 
                        options=["new", "shortlist", "hold", "reject"], 
                        index=["new", "shortlist", "hold", "reject"].index(candidate["bucket"]),
                        format_func=lambda x: status_map.get(x, x)
                    )
                    new_stage = st.selectbox(
                        "Pipeline Stage", 
                        options=["applied", "screening", "interview", "offer", "hired", "rejected"], 
                        index=["applied", "screening", "interview", "offer", "hired", "rejected"].index(candidate["stage"]),
                        format_func=lambda x: x.title()
                    )
                    notes = st.text_area("Notes", value=candidate.get("notes", ""))

                    if st.button("Update Status"):
                        try:
                            payload = {"bucket": new_bucket, "stage": new_stage, "notes": notes}
                            api_client.update_candidate(candidate["id"], payload)
                            st.success("Candidate status updated!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Update failed: {e}")

                    if st.button("📧 Generate Email Draft"):
                        st.session_state.active_tab = "bulk_email"
                        st.rerun()
                    if st.button("📅 Schedule Interview"):
                        st.session_state.active_tab = "interview_scheduler"
                        st.rerun()

                # Tabs for more detail: Resume, Skills, Experience, Audit
                t1, t2, t3, t4 = st.tabs(["📄 Job Resume", "🎯 Skills & Matching", "💼 Work History", "📜 Audit Log"])
                
                with t1:
                    filename = candidate.get("source_filename")
                    if filename:
                        st.markdown(f"### 📥 Original Resume: `{filename}`")
                        try:
                            # Fetch the real binary data from the API
                            file_bytes = api_client.download_resume(candidate["id"])
                            st.download_button(
                                label=f"Download {filename}",
                                data=file_bytes,
                                file_name=filename,
                                mime=candidate.get("resume_mime") or "application/octet-stream",
                                type="primary",
                                use_container_width=True
                            )
                        except Exception as e:
                            st.warning(f"Note: Original file download unavailable (Legacy or error: {e})")
                            st.write("You can still view the extracted text below.")
                    else:
                        st.info("This resume was pasted as text.")

                    with st.expander("📄 View Extracted Text (AI Preview)", expanded=not filename):
                        st.text_area("Full Extracted Content", candidate.get("raw_resume_text", "No content extracted."), height=400)

                with t2:
                    st.markdown("**Matched Skills:**")
                    st.write(", ".join(candidate.get("matched_skills", [])) or "None")
                    st.markdown("**Missing Required Skills:**")
                    st.write(", ".join(candidate.get("missing_skills", [])) or "None")
                    st.markdown("**All Normalized Skills:**")
                    st.write(", ".join(candidate.get("normalized_skills", [])) or "None")
                    st.markdown("**Inferred Skills:**")
                    st.write(", ".join(candidate.get("inferred_skills", [])) or "None")

                with t3:
                    st.write(candidate.get("summary", "No summary provided."))
                    st.write("---")
                    exp_list = candidate.get("work_experience", [])
                    for exp in exp_list:
                        st.markdown(f"**{exp.get('title')} @ {exp.get('company')}**")
                        st.write(f"_{exp.get('duration', '')}_")
                        st.write(exp.get("description", ""))
                        st.write("---")

                with t4:
                    st.markdown("#### Log Trail")
                    audit_entries = candidate.get("audit_entries", [])
                    if not audit_entries:
                        st.info("No audit logs found.")
                    else:
                        for entry in audit_entries:
                            color = "#28a745" if entry["status"] == "ok" else "#ffc107" if entry["status"] == "warn" else "#dc3545"
                            st.markdown(f"<span style='color:{color}'>{entry['status'].upper()}</span> | **{entry['step']}** | {entry['message']}", unsafe_allow_html=True)
            except StopIteration:
                st.error("Selected candidate not found.")
    else:
        st.info("No candidates match the current filters.")
    # Excel export fixed as secondary option
    st.markdown("---")
    if st.button("📥 Export Entire Job Pipeline to Excel"):
        try:
            excel_bytes = api_client.export_excel(job_id)
            st.download_button("Click here to download", excel_bytes, file_name=f"pipeline_export_{job_id}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        except Exception as e:
            st.error(f"Export failed: {e}")
