"""
MIND Platform - Educational Analytics Dashboard
Main Portal & Authentication Page - FIXED ROUTING
"""

import streamlit as st
from utils.auth_handler import initialize_session_state, login, logout
from config.auth import can_access_page
import base64
import os

# Page configuration
st.set_page_config(
    page_title="MIVA - MIND Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed" if not st.session_state.get('authenticated', False) else "expanded"
)

# Initialize theme and session
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

initialize_session_state()

# ============================================================
# ROLE-TO-PAGE MAPPING - Using page labels (not file paths)
# ============================================================
# Important: st.switch_page() in Streamlit Cloud works best with
# the page label (what shows in the URL), not the full file path
ROLE_PAGES = {
    'admin': 'Admin',
    'developer': 'Developer',
    'faculty': 'Faculty',
    'student': 'Student'
}

def get_user_home_page(role: str) -> str:
    """Get the home page label for a role"""
    return ROLE_PAGES.get(role.lower(), 'Student')

# ============================================================
# AUTHENTICATED USER REDIRECT (FRESH EXECUTION CHECK)
# ============================================================
# This check runs at the TOP of the script on every execution.
# If user is authenticated (from a previous st.rerun()), redirect them.
# This is safe because it's NOT during form submission.
if st.session_state.get('authenticated', False):
    # User is logged in - redirect to their dashboard
    user_role = st.session_state.get('user_role', 'student').lower()
    target_page = get_user_home_page(user_role)
    
    try:
        st.switch_page(target_page)
    except Exception as e:
        # Fallback: try with full path if label doesn't work
        ROLE_PAGES_FULL = {
            'admin': 'pages/1_👨🏿‍💼_Admin.py',
            'developer': 'pages/2_👨🏿‍💻_Developer.py',
            'faculty': 'pages/3_👩🏿‍🏫_Faculty.py',
            'student': 'pages/4_👨🏿‍🎓_Student.py'
        }
        target_path = ROLE_PAGES_FULL.get(user_role, 'pages/4_👨🏿‍🎓_Student.py')
        try:
            st.switch_page(target_path)
        except Exception as e2:
            st.error(f"Redirect failed: {e2}")
            st.info(f"Please click on '{target_page}' in the sidebar to continue.")

# ============================================================
# GLOBAL CSS
# ============================================================
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    section[data-testid="stSidebarNav"] {display: none;}
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
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

# Theme-specific CSS
if st.session_state.get('theme') == 'light':
    st.markdown("""
        <style>
        :root {
            --background-color: #ffffff;
            --secondary-background-color: #f0f2f6;
            --text-color: #262730;
        }
        .stApp {
            background-color: #ffffff;
            color: #262730;
        }
        .stSidebar, section[data-testid="stSidebar"] {
            background-color: #f0f2f6;
        }
        .stMarkdown, .stText {
            color: #262730;
        }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        :root {
            --background-color: #0e1117;
            --secondary-background-color: #262730;
            --text-color: #fafafa;
        }
        .stApp {
            background-color: #0e1117;
            color: #fafafa !important;
        }
        .stSidebar, section[data-testid="stSidebar"] {
            background-color: #262730;
        }
        .stMarkdown, .stText, p, span, div, h1, h2, h3, h4, h5, h6, label {
            color: #fafafa !important;
        }
        input, textarea, select {
            background-color: #262730 !important;
            color: #fafafa !important;
            border: 1px solid #4a4a4a !important;
        }
        </style>
    """, unsafe_allow_html=True)

# ============================================================
# LOGIN PAGE (Only shown when NOT authenticated)
# ============================================================

# Theme toggle in sidebar
with st.sidebar:
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.session_state.theme == 'dark':
            if st.button("☀️", help="Switch to light mode", key="theme_toggle"):
                st.session_state.theme = 'light'
                st.rerun()
        else:
            if st.button("🌙", help="Switch to dark mode", key="theme_toggle"):
                st.session_state.theme = 'dark'
                st.rerun()

# Logo
try:
    if st.session_state.theme == 'dark':
        LOGO_PATH = "/mount/src/mind-platform/assets/miva_logo_light.png"
    else:
        LOGO_PATH = "/mount/src/mind-platform/assets/miva_logo_dark.png"
    
    with open(LOGO_PATH, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode()
    
    st.sidebar.markdown(f"""
        <div style="margin-bottom: 1rem; text-align: center;">
            <img src="data:image/png;base64,{logo_b64}" width="180" alt="MIVA Logo">
        </div>
    """, unsafe_allow_html=True)
except:
    st.sidebar.markdown("### 🎓 MIVA Open University")

# Navigation links for sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 📚 Navigation")
st.sidebar.page_link("app.py", label="🏠 Home", icon="🏠")
st.sidebar.page_link("pages/1_👨🏿‍💼_Admin.py", label="Admin Dashboard", icon="👨🏿‍💼")
st.sidebar.page_link("pages/2_👨🏿‍💻_Developer.py", label="Developer Dashboard", icon="👨🏿‍💻")
st.sidebar.page_link("pages/3_👩🏿‍🏫_Faculty.py", label="Faculty Dashboard", icon="👩🏿‍🏫")
st.sidebar.page_link("pages/4_👨🏿‍🎓_Student.py", label="Student Dashboard", icon="👨🏿‍🎓")

# Main login area
st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='color: #FF6B6B; font-size: 3rem; margin-bottom: 0.5rem;'>
            🎓 MIND Platform
        </h1>
        <p style='font-size: 1.2rem; color: #888;'>
            Educational Analytics Dashboard
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# Login form
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("### 🔐 Login")
    
    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submit_button = st.form_submit_button("Login", use_container_width=True)
        
        if submit_button:
            if not email or not password:
                st.error("❌ Please enter both email and password")
            else:
                # Attempt login
                if login(email, password):
                    # Login successful!
                    st.success(f"✅ Welcome, {st.session_state.user_name}!")
                    
                    # CRITICAL: Use st.rerun() to trigger a fresh execution
                    # The redirect will happen at the TOP of the script on the fresh run
                    # This avoids the "cannot switch_page during form submission" error
                    st.rerun()
                else:
                    st.error("❌ Incorrect email or password. Please try again.")
    
    st.markdown("---")
    
    # Demo credentials info
    with st.expander("📋 Demo Credentials"):
        st.markdown("""
        | Role | Email | Password |
        |------|-------|----------|
        | Admin | admin@mind.edu | admin123 |
        | Developer | developer@mind.edu | dev123 |
        | Faculty | faculty@mind.edu | faculty123 |
        | Student | student@mind.edu | student123 |
        """)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #888; padding: 20px;'>
        <p><strong>MIND Platform v2.0</strong></p>
        <p>AI-Enhanced Educational Analytics</p>
        <p>Powered by BigQuery, Streamlit & Plotly</p>
        <p style="font-size: 0.9rem; margin-top: 1rem;">
            MIVA Open University
        </p>
    </div>
""", unsafe_allow_html=True)
