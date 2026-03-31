import streamlit as st
from streamlit_app.utils import api_client
from streamlit_app.state import login

def show_landing():
    # 1. Initialize session state
    if "auth_view" not in st.session_state:
        st.session_state.auth_view = None

    # 2. Global Styling (Fixing visibility and camouflage)
    st.markdown("""
        <style>
        .hero {
            padding: 6rem 1rem;
            text-align: center;
            background: #0F111A; /* Solid Dark Background for contrast */
            border-radius: 40px;
            margin-bottom: 4rem;
            border: 1px solid rgba(99, 102, 241, 0.3);
        }
        .main-title {
            font-size: 5rem;
            font-weight: 950;
            margin-bottom: 1.5rem;
            color: #FFFFFF !important; /* FORCED VISIBILITY */
            letter-spacing: -3px;
            line-height: 1.1;
        }
        .sub-title {
            font-size: 1.8rem;
            color: #CBD5E1 !important; /* Very Light Gray/Silver */
            max-width: 900px;
            margin: 0 auto 4rem auto;
            line-height: 1.6;
            font-weight: 300;
        }
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 2rem;
            margin: 4rem 0;
        }
        .feature-card {
            background: #1E293B;
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 2.5rem;
            border-radius: 24px;
            text-align: left;
        }
        .feature-icon { font-size: 3rem; margin-bottom: 1.5rem; display: block; }
        .feature-title { font-size: 1.5rem; font-weight: 700; color: #F8FAFC; margin-bottom: 1rem; }
        .feature-desc { color: #94A3B8; font-size: 1.1rem; line-height: 1.7; }
        
        .auth-card {
            background: #161925;
            padding: 3rem;
            border-radius: 32px;
            border: 1px solid #2D303E;
            box-shadow: 0 40px 100px rgba(0,0,0,0.6);
            margin-top: 5vh;
        }
        </style>
    """, unsafe_allow_html=True)

    # 3. Dedicated Auth View (The "Pop Up" experience)
    if st.session_state.auth_view:
        _, mid, _ = st.columns([1, 2, 1])
        with mid:
            st.markdown('<div class="auth-card">', unsafe_allow_html=True)
            
            # Header with back button
            col_back, col_title = st.columns([1, 4])
            with col_back:
                if st.button("← Back", type="secondary"):
                    st.session_state.auth_view = None
                    st.rerun()
            
            if st.session_state.auth_view == "login":
                st.markdown("## 🔐 Recruiter Login")
                st.markdown("<p style='color: #94A3B8; margin-bottom: 2rem;'>Welcome back to your intelligence dashboard.</p>", unsafe_allow_html=True)
                
                with st.form("login_form_final"):
                    u_email = st.text_input("User Email", placeholder="recruiter@company.com")
                    u_pass = st.text_input("Security Password", type="password")
                    if st.form_submit_button("Sign In to TalentIQ", use_container_width=True):
                        try:
                            res = api_client.login(u_email, u_pass)
                            login(res["access_token"], res["recruiter"])
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
                
                st.markdown("<p style='text-align: center; color: #6B7280; font-size: 0.9rem; margin: 1.5rem 0;'>OR</p>", unsafe_allow_html=True)
                if st.button("🚀 Access Demo Workspace", use_container_width=True):
                    try:
                        res = api_client.demo_login()
                        login(res["access_token"], res["recruiter"])
                        st.rerun()
                    except Exception as e:
                        st.error(f"Demo failed: {e}")
                
                st.markdown("---")
                st.markdown("<p style='text-align: center; color: #94A3B8;'>New to TalentIQ?</p>", unsafe_allow_html=True)
                if st.button("Create an account here", use_container_width=True, type="secondary"):
                    st.session_state.auth_view = "signup"
                    st.rerun()

            elif st.session_state.auth_view == "signup":
                st.markdown("## ✨ Create Your Workspace")
                st.markdown("<p style='color: #94A3B8; margin-bottom: 2rem;'>Join high-performance teams using TalentIQ.</p>", unsafe_allow_html=True)
                
                with st.form("signup_form_final"):
                    n_full_name = st.text_input("Full Name")
                    n_email = st.text_input("Work Email")
                    n_password = st.text_input("System Password", type="password")
                    c_name = st.text_input("Company/Agency Name")
                    if st.form_submit_button("Launch Workspace", use_container_width=True):
                        try:
                            res = api_client.signup(n_email, n_password, n_full_name, company_name=c_name)
                            login(res["access_token"], res["recruiter"])
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))
                
                st.markdown("---")
                st.markdown("<p style='text-align: center; color: #94A3B8;'>Already have an account?</p>", unsafe_allow_html=True)
                if st.button("Sign in here", use_container_width=True, type="secondary"):
                    st.session_state.auth_view = "login"
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        return  # EXIT EARLY to skip landing content
    
    # 4. Standard Landing View (When NOT in auth mode)
    # Nav Bar at Top Right
    nav_left, nav_mid, nav_login, nav_signup = st.columns([4, 1, 1, 1.2])
    with nav_login:
        if st.button("🔑 Login", use_container_width=True):
            st.session_state.auth_view = "login"
            st.rerun()
    with nav_signup:
        if st.button("✨ Get Started", type="primary", use_container_width=True):
            st.session_state.auth_view = "signup"
            st.rerun()

    # Hero
    st.markdown("""
        <div class="hero">
            <h1 class="main-title">Talent Intelligence AI</h1>
            <p class="sub-title">The world's first multi-agent workspace built for <b>high-performance teams</b>. Parse complex resumes and shortlist candidates with absolute surgical precision.</p>
        </div>
        <h2 style='text-align: center; margin-bottom: 3rem; color: white;'>Our Edge & Features</h2>
        <div class="feature-grid">
            <div class="feature-card">
                <span class="feature-icon">🧠</span>
                <div class="feature-title">LLM Deep Matching</div>
                <div class="feature-desc">Go beyond keyword matching. Our Gemini-powered engine understands professional intent and nuanced experience.</div>
            </div>
            <div class="feature-card">
                <span class="feature-icon">🛡️</span>
                <div class="feature-title">Audit-Ready Pipeline</div>
                <div class="feature-desc">Every step of the AI analysis is logged and auditable, ensuring transparent and bias-free hiring.</div>
            </div>
            <div class="feature-card">
                <span class="feature-icon">⚡</span>
                <div class="feature-title">Bulk Orchestration</div>
                <div class="feature-desc">Automate your entire outreach and scheduling workflow directly from the candidate scorecard.</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
