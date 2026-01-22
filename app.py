"""
MIND Platform - Educational Analytics Dashboard
Main Portal & Authentication Page - FIXED FOR CLEAN LOGIN + RBAC
"""

import streamlit as st
from utils.auth_handler import initialize_session_state, login, logout
from config.auth import can_access_page
import base64
import os

# Page configuration
st.set_page_config(
    page_title="MIVA - MIND Platform",
    page_icon="assets/miva_logo_dark.png",
    layout="wide",
    initial_sidebar_state="collapsed" if not st.session_state.get('authenticated', False) else "expanded"
)

# Initialize theme and session
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

initialize_session_state()

# Helper function defined locally (no import needed)
def get_user_home_page(role: str) -> str:
    """Get the home page for a role"""
    role_page_map = {
        "admin": "pages/1_👨🏿‍💼_Admin.py",
        "developer": "pages/2_👨🏿‍💻_Developer.py",
        "faculty": "pages/3_👩🏿‍🏫_Faculty.py",
        "student": "pages/4_👨🏿‍🎓_Student.py",
    }
    return role_page_map.get(role, "app.py")

# Global CSS
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
if st.session_state.theme == 'light':
    st.markdown("""
        <style>
        .stApp {
            background-color: #ffffff;
            color: #262730 !important;
        }
        .stSidebar, section[data-testid="stSidebar"] {
            background-color: #f0f2f6;
        }
        .stMarkdown, .stText, p, span, div, h1, h2, h3, h4, h5, h6, label {
            color: #262730 !important;
        }
        input, textarea, select {
            background-color: #ffffff !important;
            color: #262730 !important;
            border: 1px solid #cccccc !important;
        }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
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
        input::placeholder, textarea::placeholder {
            color: #999999 !important;
        }
        div[data-baseweb="select"] > div {
            background-color: #262730 !important;
            color: #fafafa !important;
        }
        div[role="listbox"] {
            background-color: #262730 !important;
        }
        div[role="option"] {
            background-color: #262730 !important;
            color: #fafafa !important;
        }
        div[role="option"]:hover {
            background-color: #3a3a3a !important;
        }
        </style>
    """, unsafe_allow_html=True)

# Check authentication status
is_authenticated = st.session_state.get('authenticated', False)

# CONDITIONAL SIDEBAR - Only show when authenticated
if is_authenticated:
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
        
        try:
            if st.session_state.theme == 'dark':
                logo_path = "/mount/src/mind-platform/assets/miva_logo_light.png"
            else:
                logo_path = "/mount/src/mind-platform/assets/miva_logo_dark.png"
            
            if os.path.exists(logo_path):
                with open(logo_path, "rb") as f:
                    logo_b64 = base64.b64encode(f.read()).decode()
                
                st.markdown(f"""
                    <div style="margin-bottom: 1rem;">
                        <img src="data:image/png;base64,{logo_b64}" width="180" alt="MIVA Logo">
                    </div>
                """, unsafe_allow_html=True)
        except:
            st.markdown("# 🧠 MIND")
        
        st.markdown("---")
        
        st.markdown(f"**👤 {st.session_state.user_name}**")
        st.markdown(f"*{st.session_state.user_role.title()}*")
        st.markdown(f"📧 {st.session_state.user_email}")
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()
else:
    # HIDE SIDEBAR ON LOGIN PAGE
    st.markdown("""
        <style>
        section[data-testid="stSidebar"] {
            display: none;
        }
        </style>
    """, unsafe_allow_html=True)

# Main Content
if not is_authenticated:
    # ============================================================
    # CLEAN LOGIN PAGE - NO SIDEBAR, JUST LOGIN FORM
    # ============================================================
    
    # Theme toggle in top right corner (small, unobtrusive)
    col_spacer, col_theme = st.columns([10, 1])
    with col_theme:
        if st.session_state.theme == 'dark':
            if st.button("☀️", help="Switch to light mode", key="login_theme_toggle"):
                st.session_state.theme = 'light'
                st.rerun()
        else:
            if st.button("🌙", help="Switch to dark mode", key="login_theme_toggle"):
                st.session_state.theme = 'dark'
                st.rerun()
    
    # Centered login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Logo
        try:
            if st.session_state.theme == 'dark':
                logo_path = "/mount/src/mind-platform/assets/miva_logo_light.png"
            else:
                logo_path = "/mount/src/mind-platform/assets/miva_logo_dark.png"
            
            if os.path.exists(logo_path):
                with open(logo_path, "rb") as f:
                    logo_b64 = base64.b64encode(f.read()).decode()
                
                st.markdown(f"""
                    <div style="text-align: center; margin-bottom: 2rem;">
                        <img src="data:image/png;base64,{logo_b64}" width="200" alt="MIVA Logo">
                    </div>
                """, unsafe_allow_html=True)
        except:
            pass
        
        st.markdown("""
            <div style="text-align: center; margin-bottom: 2rem;">
                <h1 style="margin-bottom: 0.5rem;">MIND Analytics Dashboard</h1>
                <p style="font-size: 1.2rem; opacity: 0.8;">AI-Enhanced Educational Analytics</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🔐 Login to Continue")
        st.markdown("---")
        
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="user@mind.edu", key="login_email")
            password = st.text_input("Password", type="password", placeholder="Enter password", key="login_password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                # Email format validation
                import re
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                
                if not email:
                    st.error("❌ Please enter your email address")
                elif not re.match(email_pattern, email):
                    st.error("❌ Invalid email format. Please enter a valid email address (e.g., user@miva.edu)")
                elif not password:
                    st.error("❌ Please enter your password")
                elif login(email, password):
                    st.success(f"✅ Welcome, {st.session_state.user_name}!")
                    
                    # RBAC: Redirect to user's home dashboard
                    home_page = get_user_home_page(st.session_state.user_role)
                    st.switch_page(home_page)
                else:
                    st.error("❌ Incorrect email or password. Please try again.")
    
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #888; padding: 20px;'>
            <p><strong>MIND Platform v2.0</strong></p>
            <p>Powered by BigQuery, Streamlit & Plotly</p>
            <p style="font-size: 0.9rem; margin-top: 1rem;">
                MIVA Open University | Educational Analytics Dashboard
            </p>
        </div>
    """, unsafe_allow_html=True)

else:
    # ============================================================
    # AUTHENTICATED - REDIRECT TO USER'S HOME DASHBOARD
    # ============================================================
    # This page should not normally be shown after login
    # User should be auto-redirected to their dashboard
    
    st.info("🔄 Redirecting to your dashboard...")
    
    home_page = get_user_home_page(st.session_state.user_role)
    st.switch_page(home_page)

