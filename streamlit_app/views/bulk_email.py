import streamlit as st
from streamlit_app.utils import api_client

def show_bulk_email():
    candidate = st.session_state.get("selected_candidate")
    job = st.session_state.get("selected_job")
    if not candidate or not job:
        st.warning("Please select a candidate first.")
        if st.button("Back to pipeline"):
            st.session_state.active_tab = "candidates"
            st.rerun()
        return

    st.title(f"📧 Draft Outreach for {candidate['full_name']}")

    template_options = ["Interview Invitation", "Screening Question", "Hold Notice", "Rejection"]
    selected_template = st.selectbox("Select Template", template_options)

    # Basic template generator
    if selected_template == "Interview Invitation":
        subject = f"Interview Invitation: {job['title']} at {st.session_state.recruiter.get('company_name', 'Our Company')}"
        body = f"""Hi {candidate['full_name']},

We reviewed your application for the {job['title']} role and were very impressed with your background in {', '.join(candidate.get('matched_skills', [])[:3])}.

We'd love to schedule a quick 30-minute introductory call. Please let us know your availability.

Best,
{st.session_state.recruiter['full_name']}
"""
    elif selected_template == "Rejection":
        subject = f"Regarding your application for {job['title']}"
        body = f"""Hi {candidate['full_name']},

Thank you for your interest in {st.session_state.recruiter.get('company_name', 'Our Company')}. At this time, we've decided to move forward with other candidates whose experience more closely matches our current needs.

We wish you the best in your job search.

Regards,
{st.session_state.recruiter['full_name']}
"""
    else:
        subject = f"Follow-up: {job['title']}"
        body = f"Hi {candidate['full_name']},\n\n..."

    with st.form("email_form"):
        draft_subject = st.text_input("Subject", value=subject)
        draft_body = st.text_area("Body", value=body, height=300)
        send_btn = st.form_submit_button("💨 Simulate Send Email", use_container_width=True)

        if send_btn:
            try:
                # Update candidate email_sent status
                api_client.update_candidate(candidate["id"], {"email_sent": True})
                st.success("Draft sent successfully! (Simulated)")
                st.session_state.active_tab = "candidates"
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    if st.button("Cancel"):
        st.session_state.active_tab = "candidates"
        st.rerun()
