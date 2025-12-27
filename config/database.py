"""
BigQuery Database Configuration
Handles connection and query execution for MIND Platform
"""

import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
from typing import Optional
import json


def get_bigquery_client():
    """
    Initialize and return BigQuery client with credentials
    Uses Streamlit secrets for secure credential management
    """
    try:
        # Get credentials from Streamlit secrets
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"]
        )
        
        client = bigquery.Client(
            credentials=credentials,
            project=st.secrets["gcp_service_account"]["project_id"],
            location="europe-west3"  # As per the notebook
        )
        
        return client
    except Exception as e:
        st.error(f"Failed to initialize BigQuery client: {str(e)}")
        return None


def run_query(sql: str, use_cache: bool = True) -> Optional[pd.DataFrame]:
    """
    Execute a SQL query and return results as DataFrame
    
    Args:
        sql: SQL query string (SELECT or WITH only)
        use_cache: Whether to use Streamlit's caching
        
    Returns:
        pandas DataFrame with query results or None on error
    """
    # Security check - only allow SELECT and WITH queries
    if not sql.strip().lower().startswith(("select", "with")):
        st.error("Only SELECT and WITH queries are allowed")
        return None
    
    try:
        client = get_bigquery_client()
        if client is None:
            return None
            
        # Execute query with optional caching
        if use_cache:
            query_job = client.query(sql)
            df = query_job.to_dataframe()
        else:
            query_job = client.query(sql)
            df = query_job.to_dataframe()
            
        return df
    
    except Exception as e:
        st.error(f"Query execution failed: {str(e)}")
        return None


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_cached_query(sql: str) -> Optional[pd.DataFrame]:
    """
    Execute query with caching for better performance
    Use this for queries that don't change frequently
    """
    return run_query(sql, use_cache=True)


# Dataset configuration
DATASET_ID = "gen-lang-client-0625543859.mind_analytics"
DATASET_NAME = "mind_analytics"


def get_table_list() -> list:
    """Get list of all tables in the dataset"""
    sql = f"""
    SELECT table_name
    FROM `{DATASET_NAME}.INFORMATION_SCHEMA.TABLES`
    ORDER BY table_name
    """
    df = get_cached_query(sql)
    return df['table_name'].tolist() if df is not None else []


def test_connection() -> bool:
    """Test database connection"""
    try:
        client = get_bigquery_client()
        if client is None:
            return False
            
        # Simple test query
        query = f"SELECT COUNT(*) as count FROM `{DATASET_ID}.user` LIMIT 1"
        result = client.query(query).to_dataframe()
        return True
    except Exception as e:
        st.error(f"Connection test failed: {str(e)}")
        return False
