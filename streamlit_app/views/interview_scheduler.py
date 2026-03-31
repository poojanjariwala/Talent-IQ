import streamlit as st
import datetime
from streamlit_app.utils import api_client

def show_interview_scheduler():
    candidate = st.session_state.get("selected_candidate")
    if not candidate:
        st.warning("Please select a candidate first.")
        if st.button("Back"):
            st.session_state.active_tab = "candidates"
            st.rerun()
        return

    st.title(f"📅 Schedule Interview for {candidate['full_name']}")

    with st.form("scheduler_form"):
        col1, col2 = st.columns(2)
        date = col1.date_input("Interview Date", datetime.date.today() + datetime.timedelta(days=1))
        time = col2.time_input("Interview Time", datetime.time(10, 0))

        cal_link = st.text_input("Calendar Link (Google/Outlook)", value="https://meet.google.com/abc-defg-hij")

        submit = st.form_submit_button("Confirm Interview", use_container_width=True)

        if submit:
            try:
                # Combine date and time
                dt_obj = datetime.datetime.combine(date, time)
                api_client.update_candidate(candidate["id"], {
                    "interview_scheduled_at": dt_obj.isoformat(),
                    "interview_calendar_link": cal_link,
                    "stage": "interview"
                })
                st.success(f"Interview scheduled for {dt_obj.strftime('%Y-%m-%d %H:%M')}")
                st.session_state.active_tab = "candidates"
                st.rerun()
            except Exception as e:
                st.error(f"Failed to schedule: {e}")

    if st.button("Cancel"):
        st.session_state.active_tab = "candidates"
        st.rerun()
