"""
Authentication Handler - ENHANCED WITH RBAC NAVIGATION
Manages user login, logout, session state, and role-based routing
"""

import streamlit as st
import bcrypt
from config.auth import USERS, get_user_permissions, can_access_page


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


def verify_password(email: str, password: str) -> bool:
    """
    Verify user credentials
    
    Args:
        email: User email
        password: Plain text password
        
    Returns:
        True if credentials are valid
    """
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


def get_user_home_page(role: str) -> str:
    """
    Get the home page/dashboard for a given role
    
    Args:
        role: User role
        
    Returns:
        Path to the user's home dashboard page
    """
    role_page_map = {
        "admin": "pages/1_👨🏿‍💼_Admin.py",
        "developer": "pages/2_👨🏿‍💻_Developer.py",
        "faculty": "pages/3_👩🏿‍🏫_Faculty.py",
        "student": "pages/4_👨🏿‍🎓_Student.py",
    }
    
    return role_page_map.get(role, "app.py")


def get_accessible_pages(role: str) -> list:
    """
    Get list of pages accessible to a role
    
    Args:
        role: User role
        
    Returns:
        List of dictionaries with page info {name, path, icon, accessible}
    """
    all_pages = [
        {"name": "Admin", "path": "pages/1_👨🏿‍💼_Admin.py", "icon": "👨🏿‍💼"},
        {"name": "Developer", "path": "pages/2_👨🏿‍💻_Developer.py", "icon": "👨🏿‍💻"},
        {"name": "Faculty", "path": "pages/3_👩🏿‍🏫_Faculty.py", "icon": "👩🏿‍🏫"},
        {"name": "Student", "path": "pages/4_👨🏿‍🎓_Student.py", "icon": "👨🏿‍🎓"},
    ]
    
    accessible_pages = []
    for page in all_pages:
        if can_access_page(role, page["name"]):
            page["accessible"] = True
            accessible_pages.append(page)
    
    return accessible_pages


def show_user_info_sidebar():
    """
    Display user info in sidebar with RBAC-aware navigation
    
    - Admin users: See navigation buttons to ALL dashboards
    - Non-admin users: See only user info + logout (no navigation links)
    """
    if st.session_state.get('authenticated', False):
        with st.sidebar:
            st.markdown("---")
            
            # User info section
            st.markdown(f"**👤 {st.session_state.user_name}**")
            st.markdown(f"*{st.session_state.user_role.title()}*")
            st.markdown(f"📧 {st.session_state.user_email}")
            
            # Only show navigation for admin users
            role = st.session_state.user_role
            
            if role == "admin":
                # Admin gets navigation to all dashboards
                accessible = get_accessible_pages(role)
                st.markdown("---")
                st.markdown("**📊 Dashboards:**")
                for page in accessible:
                    if st.button(f"{page['icon']} {page['name']}", key=f"nav_{page['name']}", use_container_width=True):
                        st.switch_page(page['path'])
            
            # Non-admin users: No navigation links shown
            # They are already in their designated dashboard
            
            st.markdown("---")
            
            # Logout button for all users
            if st.button("🚪 Logout", use_container_width=True):
                logout()
                st.rerun()
