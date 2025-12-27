"""Configuration package for MIND Platform"""

from .database import get_bigquery_client, run_query, get_cached_query, DATASET_ID
from .auth import UserRole, USERS, get_user_permissions, can_access_page

__all__ = [
    'get_bigquery_client',
    'run_query', 
    'get_cached_query',
    'DATASET_ID',
    'UserRole',
    'USERS',
    'get_user_permissions',
    'can_access_page'
]
