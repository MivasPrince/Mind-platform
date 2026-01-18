"""
Authentication Handler
Manages user login, logout, and session state
"""

import re
import streamlit as st
import bcrypt
from config.auth import USERS, get_user_permissions


# Simple, practical email pattern (enough for UI validation)
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def initialize_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None


def _normalize_email(email: str) -> str:
    """Normalize email to reduce false login failures."""
    return (email or "").strip().lower()


def validate_login_inputs(email: str, password: str) -> tuple[bool, str | None]:
    """
    Validate login inputs (UI-level validation).
    Returns: (is_valid, error_message)
    """
    email = _normalize_email(email)
    password = (password or "").strip()

    if not email and not password:
        return False, "Email and password are required."
    if not email:
        return False, "Email is required."
    if not _EMAIL_RE.match(email):
        return False, "Enter a valid email address (e.g., name@domain.com)."
    if not password:
        return False, "Password is required."

    return True, None


def verify_password(email: str, password: str) -> bool:
    """
    Verify user credentials

    Args:
        email: User email
        password: Plain text password

    Returns:
        True if credentials are valid
    """
    email = _normalize_email(email)
    if email not in USERS:
        return False

    user = USERS[email]
    return bcrypt.checkpw(password.encode('utf-8'), user['password_hash'])


def login(email: str, password: str) -> bool:
    """
    Authenticate user and create session

    Args:
        email: User email
        password: Plain text password

    Returns:
        True if login successful
    """
    email = _normalize_email(email)

    if verify_password(email, password):
        user = USERS[email]
        st.session_state.authenticated = True
        st.session_state.user_email = email
        st.session_state.user_name = user['name']
        st.session_state.user_role = user['role']
        st.session_state.user_data = user
        return True

    return False


def logout():
    """Clear session and logout user"""
    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.session_state.user_name = None
    st.session_state.user_role = None
    st.session_state.user_data = None


def require_authentication():
    """
    Decorator/helper to require authentication
    Redirects to home page (login) if not authenticated
    """
    if not st.session_state.get('authenticated', False):
        st.switch_page("app.py")


def get_current_user():
    """Get current logged-in user data"""
    return st.session_state.get('user_data', None)


def has_permission(permission: str) -> bool:
    """
    Check if current user has a specific permission

    Args:
        permission: Permission key to check

    Returns:
        True if user has permission
    """
    if not st.session_state.get('authenticated', False):
        return False

    role = st.session_state.get('user_role')
    permissions = get_user_permissions(role)
    return permissions.get(permission, False)


def show_login_page():
    """Display login page with theme-aware MIVA logo"""
    import base64
    import os

    # Initialize theme if not set
    if 'theme' not in st.session_state:
        st.session_state.theme = 'dark'  # Default to dark theme

    # Theme toggle in top corner
    col_left, col_center, col_right = st.columns([1, 3, 1])
    with col_right:
        # Small theme toggle
        if st.session_state.theme == 'dark':
            if st.button("☀️", help="Switch to light mode", key="login_theme_toggle"):
                st.session_state.theme = 'light'
                st.rerun()
        else:
            if st.button("🌙", help="Switch to dark mode", key="login_theme_toggle"):
                st.session_state.theme = 'dark'
                st.rerun()

    # Apply theme CSS
    if st.session_state.theme == 'light':
        st.markdown("""
            <style>
            .stApp {
                background-color: #ffffff;
                color: #262730;
            }
            .login-container {
                background-color: #f0f2f6 !important;
            }
            /* Login button styling for light mode */
            .stButton > button {
                background-color: #e63946;
                color: #ffffff !important;
                border: none;
                font-weight: 600;
            }
            .stButton > button:hover {
                background-color: #c7313a;
                color: #ffffff !important;
                border: none;
            }
            /* Form submit button specifically */
            button[kind="primaryFormSubmit"] {
                background-color: #e63946 !important;
                color: #ffffff !important;
                border: none !important;
            }
            button[kind="primaryFormSubmit"]:hover {
                background-color: #c7313a !important;
                color: #ffffff !important;
            }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
            .stApp {
                background-color: #0e1117;
                color: #fafafa;
            }
            /* Login button styling for dark mode */
            .stButton > button {
                background-color: #FF6B6B;
                color: #ffffff !important;
                border: none;
                font-weight: 600;
            }
            .stButton > button:hover {
                background-color: #ff5252;
                color: #ffffff !important;
                border: none;
            }
            /* Form submit button specifically */
            button[kind="primaryFormSubmit"] {
                background-color: #FF6B6B !important;
                color: #ffffff !important;
                border: none !important;
            }
            button[kind="primaryFormSubmit"]:hover {
                background-color: #ff5252 !important;
                color: #ffffff !important;
            }
            </style>
        """, unsafe_allow_html=True)

    st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 40px;
            background-color: #262730;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }
        .logo-container {
            text-align: center;
            margin-bottom: 2rem;
        }
        .logo-container img {
            max-width: 200px;
            height: auto;
        }
        .dashboard-title {
            text-align: center;
            margin-top: 1rem;
            margin-bottom: 2rem;
            font-size: 1.5rem;
            font-weight: 400;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Display theme-aware MIVA logo
        try:
            # Select logo based on theme
            if st.session_state.theme == 'dark':
                logo_path = "/mount/src/mind-platform/assets/miva_logo_light.png"
            else:
                logo_path = "/mount/src/mind-platform/assets/miva_logo_dark.png"

            # Try to load and display logo
            if os.path.exists(logo_path):
                with open(logo_path, "rb") as f:
                    logo_b64 = base64.b64encode(f.read()).decode()

                st.markdown(f"""
                    <div class="logo-container">
                        <img src="data:image/png;base64,{logo_b64}" alt="MIVA Logo">
                    </div>
                """, unsafe_allow_html=True)
            else:
                # Fallback if logo not found
                st.markdown("# 🧠 MIND Platform")
        except Exception:
            # Fallback on any error
            st.markdown("# 🧠 MIND Platform")

        # Centered dashboard title
        st.markdown('<div class="dashboard-title">MIND Analytics Dashboard</div>', unsafe_allow_html=True)
        st.markdown("---")

        with st.form("login_form"):
            email = st.text_input("Email", placeholder="user@mind.edu")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submit = st.form_submit_button("Login", use_container_width=True)

            if submit:
                ok, err = validate_login_inputs(email, password)
                if not ok:
                    st.error(err)
                else:
                    normalized_email = _normalize_email(email)

                    # Give specific feedback per UAT
                    if normalized_email not in USERS:
                        st.error("No account found for that email.")
                    else:
                        if login(normalized_email, password):
                            st.success(f"Welcome, {st.session_state.user_name}!")
                            st.rerun()
                        else:
                            st.error("Incorrect password.")


def show_user_info_sidebar():
    """Display user info in sidebar"""
    if st.session_state.get('authenticated', False):
        with st.sidebar:
            st.markdown("---")
            st.markdown(f"**👤 {st.session_state.user_name}**")
            st.markdown(f"*{st.session_state.user_role.title()}*")
            st.markdown(f"📧 {st.session_state.user_email}")

            if st.button("🚪 Logout", use_container_width=True):
                logout()
                st.rerun()
