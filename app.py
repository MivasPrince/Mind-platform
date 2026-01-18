"""
MIND Platform - Educational Analytics Dashboard
Main Portal & Authentication Page
"""

import base64
from pathlib import Path

import streamlit as st

from utils.auth_handler import (
    initialize_session_state,
    show_login_page,
    logout,
)
from config.auth import can_access_page


def _project_root() -> Path:
    return Path(__file__).resolve().parent


def _load_logo_base64(theme: str) -> str | None:
    logo_file = "miva_logo_light.png" if theme == "dark" else "miva_logo_dark.png"
    candidates = [
        _project_root() / "assets" / logo_file,
        Path("assets") / logo_file,
    ]
    for p in candidates:
        try:
            if p.exists():
                return base64.b64encode(p.read_bytes()).decode("utf-8")
        except Exception:
            continue
    return None


# Page configuration
st.set_page_config(
    page_title="MIVA - MIND Platform",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session/theme
initialize_session_state()

# Global CSS
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    section[data-testid="stSidebarNav"] {display: none;}

    .block-container { padding-top: 2rem; padding-bottom: 2rem; }

    ::-webkit-scrollbar { width: 10px; height: 10px; }
    ::-webkit-scrollbar-track { background: #262730; }
    ::-webkit-scrollbar-thumb { background: #FF6B6B; border-radius: 5px; }
    ::-webkit-scrollbar-thumb:hover { background: #ff5252; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Theme-specific CSS
if st.session_state.theme == "light":
    st.markdown(
        """
        <style>
        .stApp { background-color: #ffffff; color: #262730 !important; }
        .stSidebar, section[data-testid="stSidebar"] { background-color: #f0f2f6; }
        .stMarkdown, .stText, p, span, div, h1, h2, h3, h4, h5, h6, label { color: #262730 !important; }
        input, textarea, select { background-color: #ffffff !important; color: #262730 !important; border: 1px solid #cccccc !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <style>
        .stApp { background-color: #0e1117; color: #fafafa !important; }
        .stSidebar, section[data-testid="stSidebar"] { background-color: #262730; }
        .stMarkdown, .stText, p, span, div, h1, h2, h3, h4, h5, h6, label { color: #fafafa !important; }
        input, textarea, select { background-color: #262730 !important; color: #fafafa !important; border: 1px solid #4a4a4a !important; }
        input::placeholder, textarea::placeholder { color: #999999 !important; }
        div[data-baseweb="select"] > div { background-color: #262730 !important; color: #fafafa !important; }
        div[role="listbox"] { background-color: #262730 !important; }
        div[role="option"] { background-color: #262730 !important; color: #fafafa !important; }
        div[role="option"]:hover { background-color: #3a3a3a !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Sidebar
with st.sidebar:
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.session_state.theme == "dark":
            if st.button("☀️", help="Switch to light mode", key="theme_toggle"):
                st.session_state.theme = "light"
                st.rerun()
        else:
            if st.button("🌙", help="Switch to dark mode", key="theme_toggle"):
                st.session_state.theme = "dark"
                st.rerun()

    logo_b64 = _load_logo_base64(st.session_state.theme)
    if logo_b64:
        st.markdown(
            f"""
            <div style="margin-bottom: 1rem;">
                <img src="data:image/png;base64,{logo_b64}" width="180" alt="MIVA Logo">
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown("# 🧠 MIND")

    st.markdown("---")

    if st.session_state.get("authenticated", False):
        st.markdown(f"**👤 {st.session_state.user_name}**")
        st.markdown(f"*{st.session_state.user_role.title()}*")
        st.markdown(f"📧 {st.session_state.user_email}")
        st.markdown("---")

        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()
    else:
        st.markdown("### 📊 MIND Platform")
        st.markdown("AI-Enhanced Educational Analytics Dashboard")
        st.markdown("---")
        st.markdown(
            """
            **Four Specialized Dashboards:**

            👨🏿‍💼 **Admin**  
            System oversight & governance

            👨🏿‍💻 **Developer**  
            Technical performance & debugging

            👩🏿‍🏫 **Faculty**  
            Student analytics & outcomes

            🎓 **Student**  
            Personal learning journey
            """
        )

# Main Content
if not st.session_state.get("authenticated", False):
    # Single source of truth for login UI
    show_login_page()
    st.stop()

# DASHBOARD PORTAL
user_role = st.session_state.user_role
user_name = st.session_state.user_name

st.markdown(
    f"""
    <div style="text-align: center; margin-bottom: 3rem;">
        <h1>Welcome back, {user_name}! 👋</h1>
        <p style="font-size: 1.2rem; opacity: 0.8;">
            Select a dashboard to begin your analytics journey
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")
st.markdown("### 📊 Your Available Dashboards")
st.markdown("")

# Admin Dashboard
if can_access_page(user_role, "Admin"):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            "👨🏿‍💼 Administrator Dashboard\n\nSystem Health • User Analytics • AI Resources • Platform Configuration",
            use_container_width=True,
            key="nav_admin",
        ):
            st.switch_page("pages/1_👨🏿‍💼_Admin.py")
        st.markdown("<br>", unsafe_allow_html=True)

# Developer Dashboard
if can_access_page(user_role, "Developer"):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            "👨🏿‍💻 Developer Dashboard\n\nAPI Performance • Error Tracking • Backend Telemetry • Web Vitals",
            use_container_width=True,
            key="nav_dev",
        ):
            st.switch_page("pages/2_👨🏿‍💻_Developer.py")
        st.markdown("<br>", unsafe_allow_html=True)

# Faculty Dashboard
if can_access_page(user_role, "Faculty"):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            "👩🏿‍🏫 Faculty Dashboard\n\nStudent Performance • Case Study Analytics • At-Risk Students • Progress Tracking",
            use_container_width=True,
            key="nav_faculty",
        ):
            st.switch_page("pages/3_👩🏿‍🏫_Faculty.py")
        st.markdown("<br>", unsafe_allow_html=True)

# Student Dashboard
if can_access_page(user_role, "Student"):
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            "🎓 Student Dashboard\n\nLearning Journey • Performance Tracking • Progress Visualization • Achievements",
            use_container_width=True,
            key="nav_student",
        ):
            st.switch_page("pages/4_🎓_Student.py")
        st.markdown("<br>", unsafe_allow_html=True)

st.markdown("---")

col1, col2, col3 = st.columns(3)
with col1:
    st.info(
        """
        **💡 Quick Tip**  
        Use the sidebar to quickly navigate between dashboards after selecting one.
        """
    )
with col2:
    st.info(
        f"""
        **🎯 Your Role**  
        You have **{user_role.title()}** level access with specialized analytics.
        """
    )
with col3:
    st.info(
        """
        **🔐 Security**  
        Your session is secure. Remember to logout when done.
        """
    )

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #888; padding: 20px;'>
        <p><strong>MIND Platform v2.0</strong></p>
        <p>AI-Enhanced Educational Analytics Dashboard</p>
    </div>
    """,
    unsafe_allow_html=True,
)
