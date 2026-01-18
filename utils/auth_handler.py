"""
Authentication Handler
Manages user login, logout, and session state
"""

from __future__ import annotations

import base64
from pathlib import Path

import bcrypt
import streamlit as st

from config.auth import USERS, get_user_permissions


# ---------- Helpers ----------

def _project_root() -> Path:
    # utils/auth_handler.py -> utils -> project root
    return Path(__file__).resolve().parents[1]


def _get_asset_path(filename: str) -> Path:
    return _project_root() / "assets" / filename


def _load_logo_base64(theme: str) -> str | None:
    """
    Returns base64 string for the appropriate theme logo, or None if not found.
    """
    # Dark theme uses light logo, light theme uses dark logo
    logo_file = "miva_logo_light.png" if theme == "dark" else "miva_logo_dark.png"

    # Try absolute (local/dev), then relative (Streamlit Cloud working dir)
    candidates = [
        _get_asset_path(logo_file),
        Path("assets") / logo_file,
    ]

    for p in candidates:
        try:
            if p.exists():
                return base64.b64encode(p.read_bytes()).decode("utf-8")
        except Exception:
            continue

    return None


# ---------- Session & Auth ----------

def initialize_session_state():
    """Initialize session state variables"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_email" not in st.session_state:
        st.session_state.user_email = None
    if "user_name" not in st.session_state:
        st.session_state.user_name = None
    if "user_role" not in st.session_state:
        st.session_state.user_role = None
    if "user_data" not in st.session_state:
        st.session_state.user_data = None

    # Theme defaults
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"

    # For clearer login feedback
    if "login_error" not in st.session_state:
        st.session_state.login_error = None


def verify_password(email: str, password: str) -> bool:
    """
    Verify user credentials
    """
    if not email or not password:
        return False

    email = email.strip().lower()

    if email not in USERS:
        return False

    user = USERS[email]
    password_hash = user.get("password_hash")

    if not password_hash:
        return False

    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash)
    except Exception:
        return False


def login(email: str, password: str) -> bool:
    """
    Authenticate user and create session
    """
    st.session_state.login_error = None

    email_clean = (email or "").strip().lower()
    password_clean = password or ""

    if not email_clean:
        st.session_state.login_error = "Please enter your email address."
        return False

    if not password_clean:
        st.session_state.login_error = "Please enter your password."
        return False

    if verify_password(email_clean, password_clean):
        user = USERS[email_clean]
        st.session_state.authenticated = True
        st.session_state.user_email = email_clean
        st.session_state.user_name = user.get("name", "User")
        st.session_state.user_role = user.get("role")
        st.session_state.user_data = user
        st.session_state.login_error = None
        return True

    st.session_state.login_error = "Invalid email or password."
    return False


def logout():
    """Clear session and logout user (keeps theme preference)."""
    theme = st.session_state.get("theme", "dark")

    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.session_state.user_name = None
    st.session_state.user_role = None
    st.session_state.user_data = None
    st.session_state.login_error = None

    st.session_state.theme = theme


def require_authentication():
    """
    Helper to require authentication.
    Redirects to home page (login) if not authenticated.
    """
    initialize_session_state()
    if not st.session_state.get("authenticated", False):
        st.switch_page("app.py")


def get_current_user():
    """Get current logged-in user data"""
    return st.session_state.get("user_data", None)


def has_permission(permission: str) -> bool:
    """
    Check if current user has a specific permission
    """
    if not st.session_state.get("authenticated", False):
        return False

    role = st.session_state.get("user_role")
    permissions = get_user_permissions(role)
    return bool(permissions.get(permission, False))


# ---------- UI ----------

def show_login_page():
    """Display login page with theme-aware MIVA logo and better validation feedback."""
    initialize_session_state()

    # Theme toggle (top right)
    _, _, col_right = st.columns([1, 3, 1])
    with col_right:
        if st.session_state.theme == "dark":
            if st.button("☀️", help="Switch to light mode", key="login_theme_toggle"):
                st.session_state.theme = "light"
                st.rerun()
        else:
            if st.button("🌙", help="Switch to dark mode", key="login_theme_toggle"):
                st.session_state.theme = "dark"
                st.rerun()

    # Theme CSS
    if st.session_state.theme == "light":
        st.markdown(
            """
            <style>
            .stApp { background-color: #ffffff; color: #262730; }
            .stButton > button { background-color: #e63946; color: #ffffff !important; border: none; font-weight: 600; }
            .stButton > button:hover { background-color: #c7313a; color: #ffffff !important; border: none; }
            button[kind="primaryFormSubmit"] { background-color: #e63946 !important; color: #ffffff !important; border: none !important; }
            button[kind="primaryFormSubmit"]:hover { background-color: #c7313a !important; color: #ffffff !important; }
            </style>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <style>
            .stApp { background-color: #0e1117; color: #fafafa; }
            .stButton > button { background-color: #FF6B6B; color: #ffffff !important; border: none; font-weight: 600; }
            .stButton > button:hover { background-color: #ff5252; color: #ffffff !important; border: none; }
            button[kind="primaryFormSubmit"] { background-color: #FF6B6B !important; color: #ffffff !important; border: none !important; }
            button[kind="primaryFormSubmit"]:hover { background-color: #ff5252 !important; color: #ffffff !important; }
            </style>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <style>
        .logo-container { text-align: center; margin-bottom: 1rem; }
        .logo-container img { max-width: 200px; height: auto; }
        .dashboard-title { text-align: center; margin-top: 0.5rem; margin-bottom: 1.25rem; font-size: 1.5rem; font-weight: 400; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        logo_b64 = _load_logo_base64(st.session_state.theme)
        if logo_b64:
            st.markdown(
                f"""
                <div class="logo-container">
                    <img src="data:image/png;base64,{logo_b64}" alt="MIVA Logo">
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown("# 🧠 MIND Platform")

        st.markdown('<div class="dashboard-title">MIND Analytics Dashboard</div>', unsafe_allow_html=True)
        st.caption("AI-Enhanced Educational Analytics")
        st.markdown("---")

        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("Email", placeholder="user@mind.edu", key="login_email")
            password = st.text_input("Password", type="password", placeholder="Enter password", key="login_password")
            submit = st.form_submit_button("Login", use_container_width=True)

            if submit:
                if login(email, password):
                    st.success(f"Welcome, {st.session_state.user_name}!")
                    st.rerun()
                else:
                    st.error(st.session_state.login_error or "Login failed. Please try again.")

        st.caption("Need access? Contact your administrator.")


def show_user_info_sidebar():
    """Display user info in sidebar"""
    initialize_session_state()

    if st.session_state.get("authenticated", False):
        with st.sidebar:
            st.markdown("---")
            st.markdown(f"**👤 {st.session_state.user_name}**")
            st.markdown(f"*{str(st.session_state.user_role).title()}*")
            st.markdown(f"📧 {st.session_state.user_email}")

            if st.button("🚪 Logout", use_container_width=True):
                logout()
                st.rerun()
