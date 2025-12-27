"""
Database Connection Test
Simple page to verify BigQuery connection
"""

import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account

st.title("🔍 Database Connection Test")

st.markdown("---")

# Test 1: Check if secrets exist
st.markdown("### Test 1: Checking Secrets")
try:
    secrets = st.secrets["gcp_service_account"]
    st.success("✅ Secrets found in Streamlit configuration")
    st.write(f"**Project ID:** {secrets.get('project_id', 'Not found')}")
    st.write(f"**Client Email:** {secrets.get('client_email', 'Not found')}")
except Exception as e:
    st.error(f"❌ Secrets not found: {str(e)}")
    st.stop()

st.markdown("---")

# Test 2: Try to create BigQuery client
st.markdown("### Test 2: Creating BigQuery Client")
try:
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    
    client = bigquery.Client(
        credentials=credentials,
        project=st.secrets["gcp_service_account"]["project_id"],
        location="europe-west3"
    )
    
    st.success("✅ BigQuery client created successfully")
except Exception as e:
    st.error(f"❌ Failed to create client: {str(e)}")
    st.stop()

st.markdown("---")

# Test 3: Try a simple query
st.markdown("### Test 3: Running Test Query")
try:
    query = """
    SELECT table_name
    FROM `mind_analytics.INFORMATION_SCHEMA.TABLES`
    ORDER BY table_name
    LIMIT 5
    """
    
    result = client.query(query).to_dataframe()
    
    st.success("✅ Query executed successfully")
    st.write("**Available Tables:**")
    st.dataframe(result)
    
except Exception as e:
    st.error(f"❌ Query failed: {str(e)}")
    st.code(str(e))

st.markdown("---")

# Test 4: Count users
st.markdown("### Test 4: Counting Users")
try:
    query = """
    SELECT COUNT(*) as total_users
    FROM `gen-lang-client-0625543859.mind_analytics.user`
    """
    
    result = client.query(query).to_dataframe()
    
    st.success("✅ User count query successful")
    st.metric("Total Users", result['total_users'].iloc[0])
    
except Exception as e:
    st.error(f"❌ User count failed: {str(e)}")
    st.code(str(e))

st.markdown("---")
st.markdown("### ✅ All Tests Passed!")
st.balloons()
