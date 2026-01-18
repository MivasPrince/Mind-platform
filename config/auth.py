"""
Authentication Configuration
Defines user roles and credentials for RBAC
"""

from __future__ import annotations

from typing import Dict, Any
import bcrypt


# User roles
class UserRole:
    ADMIN = "admin"
    DEVELOPER = "developer"
    FACULTY = "faculty"
    STUDENT = "student"


# -------------------------------------------------------------------
# IMPORTANT:
# Do NOT generate bcrypt hashes at import time using gensalt().
# Streamlit reruns / deployments can reload modules, which would
# regenerate hashes and create inconsistent auth behavior.
#
# Default password for demo users: "mind2026"
# -------------------------------------------------------------------
DEFAULT_PASSWORD_HASH: bytes = b"$2b$12$zpk89WA.sxSD/fEfGIRxJ./nDXU5swNkjLKTuWf.nIiG6qSoBwiTO"


# Predefined users with hashed passwords
USERS: Dict[str, Dict[str, Any]] = {
    "admin@mind.edu": {
        "name": "System Administrator",
        "role": UserRole.ADMIN,
        "password_hash": DEFAULT_PASSWORD_HASH,
        "departments": ["All"],
        "cohorts": ["All"],
    },
    "dev@mind.edu": {
        "name": "Development Team",
        "role": UserRole.DEVELOPER,
        "password_hash": DEFAULT_PASSWORD_HASH,
        "departments": ["IT"],
        "cohorts": ["All"],
    },
    "faculty@mind.edu": {
        "name": "Dr. Sarah Johnson",
        "role": UserRole.FACULTY,
        "password_hash": DEFAULT_PASSWORD_HASH,
        "departments": ["Computer Science", "Engineering"],
        "cohorts": ["2024", "2025"],
    },
    "student@mind.edu": {
        "name": "John Smith",
        "role": UserRole.STUDENT,
        "password_hash": DEFAULT_PASSWORD_HASH,
        "departments": ["Computer Science"],
        "cohorts": ["2025"],
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
    },
}


# Role permissions mapping
ROLE_PERMISSIONS: Dict[str, Dict[str, Any]] = {
    UserRole.ADMIN: {
        "pages": ["Admin", "Developer", "Faculty", "Student"],
        "can_view_all_users": True,
        "can_modify_settings": True,
        "can_view_telemetry": True,
        "can_export_data": True,
    },
    UserRole.DEVELOPER: {
        "pages": ["Developer"],
        "can_view_all_users": False,
        "can_modify_settings": False,
        "can_view_telemetry": True,
        "can_export_data": True,
    },
    UserRole.FACULTY: {
        "pages": ["Faculty"],
        "can_view_all_users": False,
        "can_modify_settings": False,
        "can_view_telemetry": False,
        "can_export_data": True,
    },
    UserRole.STUDENT: {
        "pages": ["Student"],
        "can_view_all_users": False,
        "can_modify_settings": False,
        "can_view_telemetry": False,
        "can_export_data": False,
    },
}


def get_user_permissions(role: str) -> Dict[str, Any]:
    """Get permissions for a given role"""
    return ROLE_PERMISSIONS.get(role, {})


def can_access_page(role: str, page: str) -> bool:
    """Check if a role can access a specific page"""
    permissions = get_user_permissions(role)
    return page in permissions.get("pages", [])
