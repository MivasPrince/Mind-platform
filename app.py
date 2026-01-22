"""
MIND Platform - Educational Analytics Dashboard
Main Portal & Authentication Page
"""

import streamlit as st
from utils.auth_handler import initialize_session_state, login, logout
import os

# Page configuration
st.set_page_config(
    page_title="MIVA - MIND Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize theme and session
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

initialize_session_state()

# Global CSS - Hide default Streamlit navigation
st.markdown("""
    <style>
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    section[data-testid="stSidebarNav"] {display: none;}
    
    /* Container styling */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #262730;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #FF6B6B;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #ff5252;
    }
    </style>
""", unsafe_allow_html=True)

# Theme toggle in sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    theme = st.radio("Theme", ["🌙 Dark", "☀️ Light"], index=0 if st.session_state.theme == 'dark' else 1)
    st.session_state.theme = 'dark' if '🌙' in theme else 'light'

# ============================================================
# LOGIN PAGE
# ============================================================

# Check if user is already authenticated (returning visitor)
# This check is safe because it's not during form submission
if st.session_state.get('authenticated', False) and not st.session_state.get('needs_redirect', False):
    # User is already logged in, redirect them to their dashboard
    user_role = st.session_state.get('user_role', 'student')
    ROLE_PAGES = {
        'admin': 'pages/1_👨🏿‍💼_Admin.py',
        'developer': 'pages/2_👨🏿‍💻_Developer.py',
        'faculty': 'pages/3_👩🏿‍🏫_Faculty.py',
        'student': 'pages/4_👨🏿‍🎓_Student.py'
    }
    target_page = ROLE_PAGES.get(user_role, 'pages/4_👨🏿‍🎓_Student.py')
    st.switch_page(target_page)

# Logo
if os.path.exists("assets/miva_logo_dark.png"):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("assets/miva_logo_dark.png", width=200)
else:
    st.markdown("<h1 style='text-align: center;'>🎓 MIVA</h1>", unsafe_allow_html=True)

# Title
st.markdown("<h2 style='text-align: center;'>MIND Analytics Dashboard</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>Educational Intelligence Platform</p>", unsafe_allow_html=True)

st.markdown("---")

# Login Form
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("### 🔐 Login to Continue")
    
    with st.form("login_form", clear_on_submit=False):
        email = st.text_input(
            "Email",
            placeholder="student@mind.edu",
            help="Enter your institutional email address"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password"
        )
        
        submit_button = st.form_submit_button("Login", use_container_width=True)
        
        if submit_button:
            if not email or not password:
                st.error("❌ Please enter both email and password")
            else:
                # Attempt login
                if login(email, password):
                    # Login successful - mark for redirect
                    st.session_state['needs_redirect'] = True
                    st.success(f"✅ Welcome, {st.session_state.user_name}!")
                else:
                    st.error("❌ Invalid email or password")
    
    st.markdown("---")
    
    # Demo credentials info
    with st.expander("📝 Demo Credentials"):
        st.markdown("""
        **Admin:**  
        📧 admin@mind.edu  
        🔑 admin123
        
        **Developer:**  
        📧 dev@mind.edu  
        🔑 dev123
        
        **Faculty:**  
        📧 faculty@mind.edu  
        🔑 faculty123
        
        **Student:**  
        📧 student@mind.edu  
        🔑 student123
        """)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #888; padding: 20px;'>
        <p>MIND Platform v2.0 | AI-Enhanced Educational Analytics</p>
        <p>Powered by BigQuery, Streamlit & Plotly</p>
    </div>
""", unsafe_allow_html=True)

# ============================================================
# POST-FORM REDIRECT LOGIC
# ============================================================
# Check if we need to redirect after successful login
# This must be at the very end, after all form processing is complete
if st.session_state.get('authenticated', False) and st.session_state.get('needs_redirect', False):
    # Clear the redirect flag
    st.session_state['needs_redirect'] = False
    
    # Define role-to-page mapping
    user_role = st.session_state.get('user_role', 'student')
    ROLE_PAGES = {
        'admin': 'pages/1_👨🏿‍💼_Admin.py',
        'developer': 'pages/2_👨🏿‍💻_Developer.py',
        'faculty': 'pages/3_👩🏿‍🏫_Faculty.py',
        'student': 'pages/4_👨🏿‍🎓_Student.py'
    }
    
    # Get the target page for this role
    target_page = ROLE_PAGES.get(user_role, 'pages/4_👨🏿‍🎓_Student.py')
    
    # Now it's safe to redirect
    st.switch_page(target_page)
