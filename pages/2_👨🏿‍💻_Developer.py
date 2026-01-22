"""
Developer Dashboard - ENHANCED VERSION with PostHog Metrics
AI Performance, API Analytics, System Debugging & Web Vitals
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from google.cloud import bigquery
from google.oauth2 import service_account
import plotly.express as px
import plotly.graph_objects as go

# Import auth functions directly
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from utils.auth_handler import require_authentication, show_user_info_sidebar, get_current_user
    from config.auth import can_access_page
except Exception:
    st.error("Import error - please check file structure")
    st.stop()

# Page config
st.set_page_config(
    page_title="Developer Dashboard | MIND Platform",
    page_icon="👨🏿‍💻",
    layout="wide"
)

# Hide default Streamlit page navigation
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

# Authentication
require_authentication()
user = get_current_user()
if not can_access_page(user['role'], 'Developer'):
    st.error("⛔ Access Denied: Developer privileges required")
    st.stop()

# Theme toggle and logo display
try:
    import base64
    
    # Initialize theme in session state if not exists
    if 'theme' not in st.session_state:
        st.session_state.theme = 'dark'  # Default to dark theme
    
    # Display theme toggle in sidebar
    with st.sidebar:
        col1, col2 = st.columns([3, 1])
        with col2:
            # Theme toggle button
            if st.session_state.theme == 'dark':
                if st.button("☀️", help="Switch to light mode", key="theme_toggle"):
                    st.session_state.theme = 'light'
                    st.rerun()
            else:
                if st.button("🌙", help="Switch to dark mode", key="theme_toggle"):
                    st.session_state.theme = 'dark'
                    st.rerun()
    
    # Select appropriate logo based on theme
    if st.session_state.theme == 'dark':
        LOGO_PATH = "/mount/src/mind-platform/assets/miva_logo_light.png"
    else:
        LOGO_PATH = "/mount/src/mind-platform/assets/miva_logo_dark.png"
    
    # Display logo
    try:
        with open(LOGO_PATH, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()
        
        st.sidebar.markdown(f"""
            <div style="margin-bottom: 1rem;">
                <img src="data:image/png;base64,{logo_b64}" width="180" alt="MIVA Logo">
            </div>
        """, unsafe_allow_html=True)
    except:
        pass
    
    # Apply theme CSS
    if st.session_state.theme == 'light':
        st.markdown("""
            <style>
            /* Light theme overrides */
            :root {
                --background-color: #ffffff;
                --secondary-background-color: #f0f2f6;
                --text-color: #262730;
            }
            .stApp {
                background-color: #ffffff;
                color: #262730;
            }
            .stSidebar {
                background-color: #f0f2f6;
            }
            section[data-testid="stSidebar"] {
                background-color: #f0f2f6;
            }
            .stMarkdown, .stText {
                color: #262730;
            }
            div[data-testid="stPlotlyChart"] {
                background-color: #ffffff !important;
            }
            .js-plotly-plot {
                background-color: #ffffff !important;
            }
            div[data-testid="stMetric"] {
                background-color: #ffffff;
            }
            div[data-testid="stDataFrame"] {
                background-color: #ffffff;
            }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
            /* Dark theme (default) */
            :root {
                --background-color: #0e1117;
                --secondary-background-color: #262730;
                --text-color: #fafafa;
            }
            .stApp {
                background-color: #0e1117;
                color: #fafafa !important;
            }
            .stSidebar {
                background-color: #262730;
            }
            section[data-testid="stSidebar"] {
                background-color: #262730;
            }
            .stMarkdown, .stText, p, span, div, h1, h2, h3, h4, h5, h6, label {
                color: #fafafa !important;
            }
            .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, 
            .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
                color: #ffffff !important;
            }
            div[data-testid="stMetric"] label,
            div[data-testid="stMetric"] div {
                color: #fafafa !important;
            }
            .dataframe, .dataframe td, .dataframe th {
                color: #fafafa !important;
            }
            button[data-baseweb="tab"] {
                color: #fafafa !important;
            }
            .stTextInput label, .stSelectbox label, .stMultiSelect label,
            .stSlider label, .stRadio label, .stCheckbox label {
                color: #fafafa !important;
            }
            .stSelectbox, .stMultiSelect, .stTextInput, .stTextArea,
            .stDateInput, .stTimeInput, .stNumberInput {
                color: #fafafa !important;
            }
            .stSelectbox > div > div {
                background-color: #262730 !important;
                color: #fafafa !important;
            }
            input, textarea, select {
                background-color: #262730 !important;
                color: #fafafa !important;
                border: 1px solid #444 !important;
            }
            div[role="listbox"] {
                background-color: #262730 !important;
            }
            div[role="option"] {
                background-color: #262730 !important;
                color: #fafafa !important;
            }
            div[role="option"]:hover {
                background-color: #363740 !important;
                color: #ffffff !important;
            }
            .stSlider {
                color: #fafafa !important;
            }
            .stRadio label {
                color: #fafafa !important;
            }
            .stCheckbox label {
                color: #fafafa !important;
            }
            .streamlit-expanderHeader {
                color: #fafafa !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
except Exception:
    pass

# Sidebar user info
show_user_info_sidebar()


# Database connection
@st.cache_resource
def get_db_client():
    """Get BigQuery client"""
    try:
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"]
        )
        return bigquery.Client(
            credentials=credentials,
            project=st.secrets["gcp_service_account"]["project_id"],
            location="europe-west3"
        )
    except Exception as e:
        st.error(f"Database connection failed: {str(e)}")
        return None

@st.cache_data(ttl=3600)
def run_query(sql, show_errors=True):
    """Execute query with caching
    
    Args:
        sql: SQL query string
        show_errors: If False, suppress error messages (useful for optional data sources)
    """
    client = get_db_client()
    if client is None:
        return None
    try:
        return client.query(sql).to_dataframe()
    except Exception as e:
        if show_errors:
            st.error(f"Query failed: {str(e)}")
        return None

# Constants
DATASET_ID = "gen-lang-client-0625543859.mind_analytics"
POSTHOG_TABLE = "gen-lang-client-0625543859.posthog.Events"

# Chart helper functions
def plot_bar_chart(df, x, y, title, orientation='v', height=400):
    fig = px.bar(df, x=x, y=y, title=title, template=('plotly' if st.session_state.get('theme') == 'light' else 'plotly_dark'), orientation=orientation, height=height)
    fig.update_layout(plot_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#262730'), paper_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#0E1117'), font=dict(color=('#262730' if st.session_state.get('theme') == 'light' else '#FAFAFA')))
    return fig

def plot_line_chart(df, x, y, title, height=400):
    fig = px.line(df, x=x, y=y, title=title, template=('plotly' if st.session_state.get('theme') == 'light' else 'plotly_dark'), height=height)
    fig.update_layout(plot_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#262730'), paper_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#0E1117'), font=dict(color=('#262730' if st.session_state.get('theme') == 'light' else '#FAFAFA')), hovermode='x unified')
    return fig

def create_multi_line_chart(df, x, y_columns, title, height=400):
    fig = go.Figure()
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#3498DB']
    for idx, col in enumerate(y_columns):
        fig.add_trace(go.Scatter(x=df[x], y=df[col], name=col, mode='lines+markers', 
                                line=dict(color=colors[idx % len(colors)])))
    fig.update_layout(title=title, template=('plotly' if st.session_state.get('theme') == 'light' else 'plotly_dark'), plot_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#262730'), 
                     paper_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#0E1117'), font=dict(color=('#262730' if st.session_state.get('theme') == 'light' else '#FAFAFA')), 
                     hovermode='x unified', height=height)
    return fig

# Header
st.title("👨🏿‍💻 Developer Dashboard")
st.markdown("### AI Performance, API Analytics & System Debugging")
st.markdown("---")

# Filters in sidebar
with st.sidebar:
    st.markdown("### 🔧 Developer Tools")
    
    time_window = st.selectbox(
        "Analysis Window",
        ["Last Hour", "Last 6 Hours", "Last 24 Hours", "Last 7 Days", "Last 30 Days"],
        index=3
    )
    
    time_map = {
        "Last Hour": 1/24,
        "Last 6 Hours": 6/24,
        "Last 24 Hours": 1,
        "Last 7 Days": 7,
        "Last 30 Days": 30
    }
    days = time_map[time_window]
    
    st.markdown("---")
    st.markdown("### 🐛 Debug Tools")
    
    trace_id = st.text_input("Enter Trace ID", placeholder="trace-xxx-xxx")
    if st.button("🔍 Lookup Trace") and trace_id:
        st.session_state.trace_lookup = trace_id

# Get chart template
chart_template = 'plotly' if st.session_state.get('theme') == 'light' else 'plotly_dark'

# Main content tabs - ADDED WEB VITALS TAB
tabs = st.tabs([
    "📊 Overview",
    "🤖 AI Performance",
    "⚡ API Analytics",
    "🔍 Trace Debugger",
    "📡 Telemetry",
    "⚡ Web Vitals"
])

# TAB 1: OVERVIEW - ENHANCED WITH POSTHOG METRICS
with tabs[0]:
    st.markdown("## 📊 Developer Overview")
    
    # System health metrics - Row 1
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        df = run_query(f"""
            SELECT COUNT(*) as count
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
        """)
        if df is not None and not df.empty:
            st.metric("Total Requests", f"{df['count'].iloc[0]:,}")
        else:
            st.metric("Total Requests", "N/A")
    
    with col2:
        df = run_query(f"""
            SELECT 
                COUNT(*) as total,
                COUNTIF(derived_is_error = TRUE) as errors
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
        """)
        if df is not None and not df.empty and df['total'].iloc[0] > 0:
            success_rate = ((df['total'].iloc[0] - df['errors'].iloc[0]) / df['total'].iloc[0] * 100)
            st.metric("Success Rate", f"{success_rate:.2f}%")
        else:
            st.metric("Success Rate", "N/A")
    
    with col3:
        df = run_query(f"""
            SELECT ROUND(AVG(derived_response_time_ms), 2) as avg_latency
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
                AND derived_response_time_ms IS NOT NULL
        """)
        if df is not None and not df.empty:
            st.metric("Avg Latency", f"{df['avg_latency'].iloc[0]:.0f}ms")
        else:
            st.metric("Avg Latency", "N/A")
    
    with col4:
        df = run_query(f"""
            SELECT SUM(derived_ai_total_tokens) as total_tokens
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE derived_ai_total_tokens IS NOT NULL
        """)
        if df is not None and not df.empty and pd.notna(df['total_tokens'].iloc[0]):
            st.metric("Total Tokens", f"{float(df['total_tokens'].iloc[0]):,.0f}")
        else:
            st.metric("Total Tokens", "N/A")
    
    with col5:
        df = run_query(f"""
            SELECT COUNT(DISTINCT derived_ai_model) as models
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE derived_ai_model IS NOT NULL
        """)
        if df is not None and not df.empty:
            st.metric("AI Models", f"{df['models'].iloc[0]}")
        else:
            st.metric("AI Models", "N/A")
    
    st.markdown("---")
    
    # Exception Tracking Section - WITH GRACEFUL ERROR HANDLING
    st.markdown("### 🐛 Exception Tracking & User Impact (Last 30 Days)")
    
    # Query PostHog silently (no error display)
    df_exceptions = run_query(f"""
        SELECT
          DATE(timestamp) AS date,
          COUNTIF(event = '$exception') AS exception_count,
          COUNT(*) AS total_events,
          ROUND(SAFE_DIVIDE(COUNTIF(event = '$exception'), COUNT(*)) * 100, 2) AS exception_rate_percent,
          COUNT(DISTINCT distinct_id) AS total_users,
          COUNT(DISTINCT IF(event = '$exception', distinct_id, NULL)) AS users_with_errors
        FROM `{POSTHOG_TABLE}`
        WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
          AND timestamp < CURRENT_TIMESTAMP()
        GROUP BY date
        ORDER BY date DESC
    """, show_errors=False)
    
    if df_exceptions is not None and not df_exceptions.empty:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total_exceptions = df_exceptions['exception_count'].sum()
            st.metric("Total Exceptions", f"{total_exceptions:,}")
        with col2:
            avg_rate = df_exceptions['exception_rate_percent'].mean()
            st.metric("Avg Exception Rate", f"{avg_rate:.2f}%")
        with col3:
            max_rate = df_exceptions['exception_rate_percent'].max()
            st.metric("Peak Exception Rate", f"{max_rate:.2f}%")
        with col4:
            total_users_affected = df_exceptions['users_with_errors'].sum()
            st.metric("Users Affected", f"{total_users_affected:,}")
        
        # Exception trend chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_exceptions['date'],
            y=df_exceptions['exception_count'],
            name='Exception Count',
            line=dict(color='#FF6B6B', width=3),
            fill='tozeroy',
            fillcolor='rgba(255, 107, 107, 0.1)'
        ))
        fig.add_trace(go.Scatter(
            x=df_exceptions['date'],
            y=df_exceptions['users_with_errors'],
            name='Users Affected',
            line=dict(color='#FFA500', width=3),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='Exception Count & Users Affected Over Time',
            template=chart_template,
            height=350,
            yaxis=dict(title='Exception Count'),
            yaxis2=dict(title='Users Affected', overlaying='y', side='right'),
            hovermode='x unified',
            plot_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#262730'),
            paper_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#0E1117'),
            font=dict(color=('#262730' if st.session_state.get('theme') == 'light' else '#FAFAFA'))
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("💡 Exception tracking requires PostHog integration. Once configured, you'll see exception counts, user impact metrics, and trends here.")
    
    st.markdown("---")
    
    # Session Quality & Error-Free Rate - WITH GRACEFUL ERROR HANDLING
    st.markdown("### ✅ Session Quality & Error-Free Rate (Last 30 Days)")
    
    df_session_quality = run_query(f"""
        WITH session_errors AS (
          SELECT DISTINCT
            JSON_VALUE(properties, '$."$session_id"') AS session_id
          FROM `{POSTHOG_TABLE}`
          WHERE event = '$exception'
            AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
            AND timestamp < CURRENT_TIMESTAMP()
            AND JSON_VALUE(properties, '$."$session_id"') IS NOT NULL
        ),
        all_sessions AS (
          SELECT DISTINCT
            JSON_VALUE(properties, '$."$session_id"') AS session_id
          FROM `{POSTHOG_TABLE}`
          WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
            AND timestamp < CURRENT_TIMESTAMP()
            AND JSON_VALUE(properties, '$."$session_id"') IS NOT NULL
        )
        SELECT
          CURRENT_DATE() AS report_date,
          COUNT(DISTINCT s.session_id) AS total_sessions,
          COUNT(DISTINCT e.session_id) AS sessions_with_errors,
          COUNT(DISTINCT s.session_id) - COUNT(DISTINCT e.session_id) AS error_free_sessions,
          ROUND(
            SAFE_DIVIDE(
              COUNT(DISTINCT s.session_id) - COUNT(DISTINCT e.session_id),
              COUNT(DISTINCT s.session_id)
            ) * 100,
            2
          ) AS error_free_rate_percent
        FROM all_sessions s
        LEFT JOIN session_errors e ON s.session_id = e.session_id
    """, show_errors=False)
    
    if df_session_quality is not None and not df_session_quality.empty:
        data = df_session_quality.iloc[0]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Sessions", f"{data['total_sessions']:,}")
        with col2:
            st.metric("Error-Free Sessions", f"{data['error_free_sessions']:,}", 
                     f"{data['error_free_rate_percent']:.1f}%")
        with col3:
            st.metric("Sessions with Errors", f"{data['sessions_with_errors']:,}",
                     f"{100 - data['error_free_rate_percent']:.1f}%",
                     delta_color="inverse")
        
        # Gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=data['error_free_rate_percent'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Error-Free Session Rate", 'font': {'size': 20}},
            delta={'reference': 95, 'suffix': '% SLA'},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "#4ECDC4"},
                'steps': [
                    {'range': [0, 80], 'color': '#FF5252'},
                    {'range': [80, 95], 'color': '#FFA726'},
                    {'range': [95, 100], 'color': '#00C853'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 95
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            template=chart_template,
            paper_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#0E1117'),
            font=dict(color=('#262730' if st.session_state.get('theme') == 'light' else '#FAFAFA'))
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # SLA analysis
        if data['error_free_rate_percent'] >= 95:
            st.success(f"✅ **Meeting SLA Target:** {data['error_free_rate_percent']:.2f}% ≥ 95%")
        else:
            gap = 95 - data['error_free_rate_percent']
            st.warning(f"⚠️ **Below SLA Target:** {data['error_free_rate_percent']:.2f}% < 95% (Gap: {gap:.2f}%)")
    else:
        st.info("💡 Session quality tracking requires PostHog integration. Once configured, you'll see error-free session rates and SLA monitoring here.")
    
    st.markdown("---")
    
    # Performance metrics - Row 2
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        df = run_query(f"""
            SELECT ROUND(APPROX_QUANTILES(derived_response_time_ms, 100)[OFFSET(95)], 2) as p95
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
                AND derived_response_time_ms IS NOT NULL
        """)
        if df is not None and not df.empty:
            st.metric("P95 Latency", f"{df['p95'].iloc[0]:.0f}ms", 
                     delta="Target: <2000ms", delta_color="inverse")
        else:
            st.metric("P95 Latency", "N/A")
    
    with col2:
        df = run_query(f"""
            SELECT COUNT(DISTINCT trace_id) as traces
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
                AND trace_id IS NOT NULL
        """)
        if df is not None and not df.empty:
            st.metric("Unique Traces", f"{df['traces'].iloc[0]:,}")
        else:
            st.metric("Unique Traces", "N/A")
    
    with col3:
        df = run_query(f"""
            SELECT COUNT(DISTINCT service_name) as services
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE service_name IS NOT NULL
        """)
        if df is not None and not df.empty:
            st.metric("Active Services", f"{df['services'].iloc[0]}")
        else:
            st.metric("Active Services", "N/A")
    
    with col4:
        df = run_query(f"""
            SELECT COUNTIF(derived_is_error = TRUE) as errors
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
        """)
        if df is not None and not df.empty:
            st.metric("Total Errors", f"{df['errors'].iloc[0]:,}", 
                     delta="0 is ideal", delta_color="inverse")
        else:
            st.metric("Total Errors", "N/A")
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Request Volume Over Time")
        df = run_query(f"""
            SELECT 
                TIMESTAMP_TRUNC(created_at, HOUR) as hour,
                COUNT(*) as request_count
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
            GROUP BY hour
            ORDER BY hour
        """)
        if df is not None and not df.empty:
            fig = plot_line_chart(df, 'hour', 'request_count', 'Hourly Request Volume', height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No request data available")
    
    with col2:
        st.markdown("### ⚡ Response Time Distribution")
        df = run_query(f"""
            SELECT 
                ROUND(AVG(derived_response_time_ms), 2) as avg_latency,
                ROUND(APPROX_QUANTILES(derived_response_time_ms, 100)[OFFSET(50)], 2) as p50,
                ROUND(APPROX_QUANTILES(derived_response_time_ms, 100)[OFFSET(95)], 2) as p95,
                ROUND(APPROX_QUANTILES(derived_response_time_ms, 100)[OFFSET(99)], 2) as p99
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
                AND derived_response_time_ms IS NOT NULL
        """)
        if df is not None and not df.empty:
            latency_data = pd.DataFrame({
                'Metric': ['Average', 'P50', 'P95', 'P99'],
                'Latency (ms)': [
                    df['avg_latency'].iloc[0],
                    df['p50'].iloc[0],
                    df['p95'].iloc[0],
                    df['p99'].iloc[0]
                ]
            })
            fig = plot_bar_chart(latency_data, 'Metric', 'Latency (ms)', 
                               'Response Time Metrics', height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No latency data available")
    
    st.markdown("---")
    
    # Error and success rate trends
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🐛 Error Rate Trend")
        df = run_query(f"""
            SELECT 
                TIMESTAMP_TRUNC(created_at, HOUR) as hour,
                COUNTIF(derived_is_error = TRUE) as errors,
                COUNT(*) as total,
                ROUND(COUNTIF(derived_is_error = TRUE) / COUNT(*) * 100, 2) as error_rate
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
            GROUP BY hour
            ORDER BY hour
        """)
        if df is not None and not df.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['hour'],
                y=df['error_rate'],
                mode='lines+markers',
                name='Error Rate %',
                line=dict(color='#e74c3c', width=2),
                fill='tozeroy',
                fillcolor='rgba(231, 76, 60, 0.2)'
            ))
            fig.update_layout(
                title='Hourly Error Rate %',
                xaxis_title='Time',
                yaxis_title='Error Rate (%)',
                template=chart_template,
                plot_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#262730'),
                paper_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#0E1117'),
                font=dict(color=('#262730' if st.session_state.get('theme') == 'light' else '#FAFAFA')),
                height=350,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No error data available")
    
    with col2:
        st.markdown("### 📊 Request Status Codes")
        df = run_query(f"""
            SELECT 
                http_status_code,
                COUNT(*) as count
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
                AND http_status_code IS NOT NULL
            GROUP BY http_status_code
            ORDER BY count DESC
            LIMIT 10
        """)
        if df is not None and not df.empty:
            fig = go.Figure(go.Bar(
                x=df['count'],
                y=df['http_status_code'].astype(str),
                orientation='h',
                marker=dict(
                    color=df['count'],
                    colorscale='Blues',
                    showscale=False
                ),
                text=df['count'],
                textposition='outside'
            ))
            fig.update_layout(
                title='Top HTTP Status Codes',
                xaxis_title='Count',
                yaxis_title='Status Code',
                template=chart_template,
                plot_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#262730'),
                paper_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#0E1117'),
                font=dict(color=('#262730' if st.session_state.get('theme') == 'light' else '#FAFAFA')),
                height=350,
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No status code data available")
    
    st.markdown("---")
    
    # Database & Session Analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💾 Active User Sessions")
        df = run_query(f"""
            SELECT 
                DATE(start_timestamp) as date,
                COUNT(DISTINCT distinct_id) as unique_users,
                COUNT(*) as total_sessions,
                ROUND(AVG(session_duration_seconds / 60), 2) as avg_duration_min
            FROM `{DATASET_ID}.session_analytics`
            WHERE start_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
            GROUP BY date
            ORDER BY date
        """)
        if df is not None and not df.empty:
            fig = create_multi_line_chart(
                df, 'date', 
                ['unique_users', 'total_sessions'], 
                'Daily Session Metrics',
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No session data available")
    
    with col2:
        st.markdown("### 📝 Grade Submissions Trend")
        df = run_query(f"""
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as submissions,
                ROUND(AVG(final_score), 2) as avg_score
            FROM `{DATASET_ID}.grades`
            WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
            GROUP BY date
            ORDER BY date
        """)
        if df is not None and not df.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df['date'],
                y=df['submissions'],
                name='Submissions',
                marker=dict(color='#3498db')
            ))
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['avg_score'],
                name='Avg Score',
                yaxis='y2',
                mode='lines+markers',
                line=dict(color='#2ecc71', width=3)
            ))
            fig.update_layout(
                title='Daily Grade Submissions & Average Scores',
                xaxis_title='Date',
                yaxis_title='Submissions',
                yaxis2=dict(
                    title='Average Score',
                    overlaying='y',
                    side='right'
                ),
                template=chart_template,
                plot_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#262730'),
                paper_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#0E1117'),
                font=dict(color=('#262730' if st.session_state.get('theme') == 'light' else '#FAFAFA')),
                height=350,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No grade data available")


# TAB 2: AI PERFORMANCE
with tabs[1]:
    st.markdown("## 🤖 AI Performance Analytics")
    
    # Token metrics
    df = run_query(f"""
        SELECT 
            SUM(derived_ai_total_tokens) as total_tokens,
            SUM(derived_ai_input_tokens) as input_tokens,
            SUM(derived_ai_output_tokens) as output_tokens
        FROM `{DATASET_ID}.backend_telemetry`
        WHERE derived_ai_total_tokens IS NOT NULL
    """)
    
    col1, col2, col3 = st.columns(3)
    
    if df is not None and not df.empty and pd.notna(df['total_tokens'].iloc[0]):
        total = float(df['total_tokens'].iloc[0])
        input_tok = float(df['input_tokens'].iloc[0])
        output_tok = float(df['output_tokens'].iloc[0])
        
        with col1:
            st.metric("Input Tokens", f"{input_tok:,.0f}")
        with col2:
            st.metric("Output Tokens", f"{output_tok:,.0f}")
        with col3:
            ratio = output_tok / input_tok if input_tok > 0 else 0
            st.metric("Output/Input Ratio", f"{ratio:.2f}x")
    else:
        with col1:
            st.metric("Input Tokens", "N/A")
        with col2:
            st.metric("Output Tokens", "N/A")
        with col3:
            st.metric("Output/Input Ratio", "N/A")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🤖 Model Distribution")
        df = run_query(f"""
            SELECT 
                derived_ai_model as model,
                COUNT(*) as request_count,
                SUM(derived_ai_total_tokens) as total_tokens,
                ROUND(AVG(derived_ai_total_tokens), 2) as avg_tokens
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE derived_ai_model IS NOT NULL
            GROUP BY model
            ORDER BY request_count DESC
        """)
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True, height=300)
            
            fig = plot_bar_chart(df, 'model', 'request_count', 'Requests by Model', height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No AI model data available")
    
    with col2:
        st.markdown("### 📊 Token Distribution")
        if df is not None and not df.empty:
            fig = plot_bar_chart(df, 'model', 'total_tokens', 'Token Usage by Model', height=300)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("### 💰 Cost Estimation")
            total_cost = (df['total_tokens'].sum() / 1_000_000) * 15.0
            st.metric("Estimated Total Cost", f"${total_cost:,.2f}")
            st.caption("Based on $15 per 1M tokens")
        else:
            st.info("No token distribution data available")


# TAB 3: API ANALYTICS - ENHANCED
with tabs[2]:
    st.markdown("## ⚡ API Performance Analytics")
    
    # Original API route performance
    st.markdown("### 📊 API Route Performance")
    df = run_query(f"""
        SELECT http_route, COUNT(*) as request_count,
            ROUND(AVG(derived_response_time_ms), 2) as avg_latency,
            ROUND(APPROX_QUANTILES(derived_response_time_ms, 100)[OFFSET(95)], 2) as p95_latency,
            ROUND(APPROX_QUANTILES(derived_response_time_ms, 100)[OFFSET(99)], 2) as p99_latency
        FROM `{DATASET_ID}.backend_telemetry`
        WHERE http_route IS NOT NULL
            AND created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
        GROUP BY http_route ORDER BY request_count DESC LIMIT 20
    """)
    
    if df is not None and not df.empty:
        st.dataframe(df, use_container_width=True, height=400)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", csv, "api_performance.csv", "text/csv")
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 Request Volume by Route")
            fig = go.Figure(go.Bar(x=df.head(10)['request_count'], y=df.head(10)['http_route'],
                orientation='h', marker=dict(color='#3498db'), text=df.head(10)['request_count'],
                textposition='outside'))
            fig.update_layout(title='Top Routes by Request Count', xaxis_title='Request Count',
                yaxis_title='Route', template=chart_template,
                plot_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#262730'),
                paper_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#0E1117'),
                font=dict(color=('#262730' if st.session_state.get('theme') == 'light' else '#FAFAFA')),
                height=400, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### ⏱️ P95 Latency by Route")
            fig = go.Figure(go.Bar(x=df.head(10)['p95_latency'], y=df.head(10)['http_route'],
                orientation='h', marker=dict(color='#e74c3c'),
                text=df.head(10)['p95_latency'].apply(lambda x: f"{int(x)}ms"),
                textposition='outside'))
            fig.add_vline(x=2000, line_dash="dash", line_color="yellow",
                annotation_text="SLO: 2000ms", annotation_position="top right")
            fig.update_layout(title='P95 Latency by Route', xaxis_title='Latency (ms)',
                yaxis_title='Route', template=chart_template,
                plot_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#262730'),
                paper_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#0E1117'),
                font=dict(color=('#262730' if st.session_state.get('theme') == 'light' else '#FAFAFA')),
                height=400, yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No API performance data available")
    
    st.markdown("---")
    st.markdown("### 🐛 Error Analysis")
    
    df = run_query(f"""
        SELECT http_route, http_status_code, COUNT(*) as error_count
        FROM `{DATASET_ID}.backend_telemetry`
        WHERE derived_is_error = TRUE
            AND created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
        GROUP BY http_route, http_status_code
        ORDER BY error_count DESC LIMIT 20
    """)
    
    if df is not None and not df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Errors by Route")
            route_errors = df.groupby('http_route')['error_count'].sum().reset_index()
            route_errors = route_errors.sort_values('error_count', ascending=False).head(10)
            fig = plot_bar_chart(route_errors, 'http_route', 'error_count',
                'Errors by Route', orientation='h', height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Errors by Status Code")
            status_errors = df.groupby('http_status_code')['error_count'].sum().reset_index()
            fig = plot_bar_chart(status_errors, 'http_status_code', 'error_count',
                'Errors by Status Code', height=350)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("✅ No errors in the selected time window!")
    
    st.markdown("---")
    
    # Rage Clicks & User Frustration - WITH GRACEFUL ERROR HANDLING
    st.markdown("### 😤 User Frustration Indicators (Rage Clicks)")
    
    df_rage = run_query(f"""
        SELECT DATE(timestamp) AS date, JSON_VALUE(properties, '$.\"$current_url\"') AS page_url,
          COUNT(*) AS rageclick_count, COUNT(DISTINCT distinct_id) AS users_frustrated,
          COUNT(DISTINCT JSON_VALUE(properties, '$.\"$session_id\"')) AS sessions_with_rageclicks
        FROM `{POSTHOG_TABLE}`
        WHERE event = '$rageclick' AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
          AND timestamp < CURRENT_TIMESTAMP()
          AND JSON_VALUE(properties, '$.\"$session_id\"') IS NOT NULL
        GROUP BY date, page_url ORDER BY rageclick_count DESC LIMIT 20
    """, show_errors=False)
    
    if df_rage is not None and not df_rage.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Rage Clicks (30d)", f"{df_rage['rageclick_count'].sum():,}")
        with col2:
            st.metric("Frustrated Users", f"{df_rage['users_frustrated'].sum():,}")
        with col3:
            st.metric("Sessions Affected", f"{df_rage['sessions_with_rageclicks'].sum():,}")
        
        page_summary = df_rage.groupby('page_url').agg({
            'rageclick_count': 'sum', 'users_frustrated': 'sum'
        }).reset_index().sort_values('rageclick_count', ascending=False).head(10)
        
        st.subheader("Most Problematic Pages")
        st.dataframe(page_summary, use_container_width=True)
        
        fig = px.bar(page_summary, x='rageclick_count', y='page_url', orientation='h',
            title='Top 10 Pages by Rage Clicks', template=chart_template,
            color='users_frustrated', color_continuous_scale='Reds')
        fig.update_layout(height=400, yaxis={'categoryorder': 'total ascending'},
            plot_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#262730'),
            paper_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#0E1117'),
            font=dict(color=('#262730' if st.session_state.get('theme') == 'light' else '#FAFAFA')))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("💡 Rage click tracking requires PostHog integration. Once configured, you'll see user frustration indicators here.")
    
    st.markdown("---")
    
    # Error Distribution by Type - WITH GRACEFUL ERROR HANDLING
    st.markdown("### 📋 Error Distribution by Type")
    
    df_error_types = run_query(f"""
        SELECT JSON_VALUE(properties, '$.\"$exception_type\"') AS error_type,
          JSON_VALUE(properties, '$.\"$exception_message\"') AS error_message,
          COUNT(*) AS occurrence_count, COUNT(DISTINCT distinct_id) AS users_affected
        FROM `{POSTHOG_TABLE}`
        WHERE event = '$exception' AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
          AND timestamp < CURRENT_TIMESTAMP()
        GROUP BY error_type, error_message ORDER BY occurrence_count DESC LIMIT 20
    """, show_errors=False)
    
    if df_error_types is not None and not df_error_types.empty:
        st.dataframe(df_error_types, use_container_width=True, height=400)
        csv = df_error_types.to_csv(index=False)
        st.download_button(label="📥 Download Error Analysis (CSV)", data=csv,
            file_name=f"error_analysis_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv")
    else:
        st.info("💡 Error type tracking requires PostHog integration. Once configured, you'll see detailed error breakdowns here.")

# TAB 4: TRACE DEBUGGER
with tabs[3]:
    st.markdown("## 🔍 Request Trace Debugger")
    
    if 'trace_lookup' in st.session_state:
        trace_id = st.session_state.trace_lookup
        st.markdown(f"### 📝 Trace: `{trace_id}`")
        
        df = run_query(f"""
            SELECT * FROM `{DATASET_ID}.backend_telemetry`
            WHERE trace_id = '{trace_id}' ORDER BY start_timestamp
        """)
        
        if df is not None and not df.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Spans", len(df))
            with col2:
                if 'derived_response_time_ms' in df.columns:
                    st.metric("Total Time", f"{df['derived_response_time_ms'].sum():.0f}ms")
            with col3:
                if 'derived_is_error' in df.columns:
                    has_error = df['derived_is_error'].any()
                    st.metric("Status", "❌ Error" if has_error else "✅ Success")
            
            st.markdown("---")
            st.markdown("### 🔬 Trace Details")
            st.dataframe(df, use_container_width=True, height=400)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Trace", csv, f"trace_{trace_id}.csv", "text/csv")
        else:
            st.warning(f"No trace found for ID: {trace_id}")
    else:
        st.info("👈 Enter a Trace ID in the sidebar to begin debugging")
        st.markdown("""
        ### 📚 How to Use
        1. Enter a `trace_id` in the sidebar
        2. Click **Lookup Trace** to retrieve details
        3. View full request lifecycle and timing
        4. Analyze errors and performance bottlenecks
        5. Export trace data for further analysis
        """)
        
        st.markdown("### 🕐 Recent Traces")
        df = run_query(f"""
            SELECT DISTINCT trace_id, MIN(created_at) as start_time, COUNT(*) as span_count,
                BOOL_OR(derived_is_error) as has_error
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE trace_id IS NOT NULL
                AND created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY)
            GROUP BY trace_id ORDER BY start_time DESC LIMIT 20
        """)
        
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No recent traces found")

# TAB 5: TELEMETRY - ENHANCED
with tabs[4]:
    st.markdown("## 📡 Backend Telemetry")
    st.markdown("### 📊 Telemetry Statistics")
    
    df = run_query(f"""
        SELECT COUNT(*) as total_records, COUNT(DISTINCT trace_id) as unique_traces,
            COUNT(DISTINCT service_name) as services, MIN(created_at) as oldest_record,
            MAX(created_at) as newest_record
        FROM `{DATASET_ID}.backend_telemetry`
    """)
    
    if df is not None and not df.empty:
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total Records", f"{df['total_records'].iloc[0]:,}")
        with col2:
            st.metric("Unique Traces", f"{df['unique_traces'].iloc[0]:,}")
        with col3:
            st.metric("Services", f"{df['services'].iloc[0]:,}")
        with col4:
            oldest = pd.to_datetime(df['oldest_record'].iloc[0])
            st.metric("Oldest Record", oldest.strftime('%Y-%m-%d'))
        with col5:
            newest = pd.to_datetime(df['newest_record'].iloc[0])
            st.metric("Newest Record", newest.strftime('%Y-%m-%d'))
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔧 Service Distribution")
        df = run_query(f"""
            SELECT service_name, COUNT(*) as request_count
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE service_name IS NOT NULL
            GROUP BY service_name ORDER BY request_count DESC
        """)
        if df is not None and not df.empty:
            fig = plot_bar_chart(df, 'service_name', 'request_count', 'Requests by Service', height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No service data available")
    
    with col2:
        st.markdown("### 🌍 Environment Distribution")
        df = run_query(f"""
            SELECT deployment_environment, COUNT(*) as request_count
            FROM `{DATASET_ID}.backend_telemetry`
            WHERE deployment_environment IS NOT NULL
            GROUP BY deployment_environment ORDER BY request_count DESC
        """)
        if df is not None and not df.empty:
            fig = plot_bar_chart(df, 'deployment_environment', 'request_count',
                'Requests by Environment', height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No environment data available")
    
    st.markdown("---")
    
    # Network & Application Logs - WITH GRACEFUL ERROR HANDLING
    st.markdown("### 🌐 Network Connectivity & Logs")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Network Status Changes")
        df_network = run_query(f"""
            SELECT DATE(timestamp) AS date, JSON_VALUE(properties, '$.\"$status\"') AS network_status,
              COUNT(*) AS status_change_count, COUNT(DISTINCT distinct_id) AS users_affected
            FROM `{POSTHOG_TABLE}`
            WHERE event = 'network_status_changed'
              AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
              AND timestamp < CURRENT_TIMESTAMP()
            GROUP BY date, network_status ORDER BY date DESC LIMIT 20
        """, show_errors=False)
        
        if df_network is not None and not df_network.empty:
            st.dataframe(df_network, use_container_width=True, height=300)
            st.metric("Total Status Changes", f"{df_network['status_change_count'].sum():,}")
        else:
            st.info("💡 Network tracking requires PostHog integration.")
    
    with col2:
        st.markdown("#### Application Logs Summary")
        df_logs = run_query(f"""
            SELECT JSON_VALUE(properties, '$.level') AS log_level,
              COUNT(*) AS log_count, COUNT(DISTINCT distinct_id) AS users_affected
            FROM `{POSTHOG_TABLE}`
            WHERE event = 'log'
              AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
              AND timestamp < CURRENT_TIMESTAMP()
            GROUP BY log_level ORDER BY log_count DESC
        """, show_errors=False)
        
        if df_logs is not None and not df_logs.empty:
            st.dataframe(df_logs, use_container_width=True, height=300)
            
            fig = px.pie(df_logs, values='log_count', names='log_level',
                title='Logs by Level', template=chart_template,
                color='log_level', color_discrete_map={
                    'error': '#FF5252', 'warn': '#FFA726',
                    'info': '#4ECDC4', 'debug': '#9E9E9E'
                })
            fig.update_layout(paper_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#0E1117'),
                font=dict(color=('#262730' if st.session_state.get('theme') == 'light' else '#FAFAFA')), height=250)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("💡 Log tracking requires PostHog integration.")

# TAB 6: WEB VITALS
with tabs[5]:
    st.markdown("## ⚡ Web Vitals Performance Monitoring")
    
    st.markdown("""
    **Core Web Vitals** are Google's metrics for measuring real-world user experience:
    - **LCP (Largest Contentful Paint)**: Loading performance - **Good: ≤2.5s**
    - **FCP (First Contentful Paint)**: Initial rendering - **Good: ≤1.8s**
    - **INP (Interaction to Next Paint)**: Interactivity - **Good: ≤200ms**
    - **CLS (Cumulative Layout Shift)**: Visual stability - **Good: ≤0.1**
    """)
    
    df_vitals = run_query(f"""
        WITH base AS (
          SELECT DATE(timestamp) AS date,
            SAFE_CAST(JSON_VALUE(properties, '$."$web_vitals_LCP_value"') AS FLOAT64) AS lcp_ms,
            SAFE_CAST(JSON_VALUE(properties, '$."$web_vitals_FCP_value"') AS FLOAT64) AS fcp_ms,
            SAFE_CAST(JSON_VALUE(properties, '$."$web_vitals_INP_value"') AS FLOAT64) AS inp_ms,
            SAFE_CAST(JSON_VALUE(properties, '$."$web_vitals_CLS_value"') AS FLOAT64) AS cls_score
          FROM `{POSTHOG_TABLE}`
          WHERE event = '$web_vitals'
            AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
            AND timestamp < CURRENT_TIMESTAMP()
        )
        SELECT date,
          ROUND(AVG(lcp_ms) / 1000, 2) AS avg_lcp_seconds,
          COUNTIF(lcp_ms / 1000 <= 2.5) AS lcp_good,
          COUNTIF(lcp_ms / 1000 > 2.5 AND lcp_ms / 1000 <= 4.0) AS lcp_needs_improvement,
          COUNTIF(lcp_ms / 1000 > 4.0) AS lcp_poor,
          ROUND(AVG(fcp_ms) / 1000, 2) AS avg_fcp_seconds,
          COUNTIF(fcp_ms / 1000 <= 1.8) AS fcp_good,
          COUNTIF(fcp_ms / 1000 > 1.8 AND fcp_ms / 1000 <= 3.0) AS fcp_needs_improvement,
          COUNTIF(fcp_ms / 1000 > 3.0) AS fcp_poor,
          ROUND(AVG(inp_ms), 2) AS avg_inp_ms,
          COUNTIF(inp_ms <= 200) AS inp_good,
          COUNTIF(inp_ms > 200 AND inp_ms <= 500) AS inp_needs_improvement,
          COUNTIF(inp_ms > 500) AS inp_poor,
          ROUND(AVG(cls_score), 3) AS avg_cls_score,
          COUNTIF(cls_score <= 0.1) AS cls_good,
          COUNTIF(cls_score > 0.1 AND cls_score <= 0.25) AS cls_needs_improvement,
          COUNTIF(cls_score > 0.25) AS cls_poor
        FROM base GROUP BY date ORDER BY date DESC
    """, show_errors=False)
    
    if df_vitals is not None and not df_vitals.empty:
        # Summary metrics
        st.subheader("📊 Current Performance Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        latest = df_vitals.iloc[0]
        
        with col1:
            lcp_val = latest['avg_lcp_seconds']
            lcp_status = "🟢 Good" if lcp_val <= 2.5 else "🟡 Needs Work" if lcp_val <= 4.0 else "🔴 Poor"
            st.metric("LCP (Avg)", f"{lcp_val:.2f}s", lcp_status)
        
        with col2:
            fcp_val = latest['avg_fcp_seconds']
            fcp_status = "🟢 Good" if fcp_val <= 1.8 else "🟡 Needs Work" if fcp_val <= 3.0 else "🔴 Poor"
            st.metric("FCP (Avg)", f"{fcp_val:.2f}s", fcp_status)
        
        with col3:
            inp_val = latest['avg_inp_ms']
            inp_status = "🟢 Good" if inp_val <= 200 else "🟡 Needs Work" if inp_val <= 500 else "🔴 Poor"
            st.metric("INP (Avg)", f"{inp_val:.0f}ms", inp_status)
        
        with col4:
            cls_val = latest['avg_cls_score']
            cls_status = "🟢 Good" if cls_val <= 0.1 else "🟡 Needs Work" if cls_val <= 0.25 else "🔴 Poor"
            st.metric("CLS (Avg)", f"{cls_val:.3f}", cls_status)
        
        st.markdown("---")
        
        # Trend charts
        st.subheader("📈 Performance Trends (30 Days)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_vitals['date'], y=df_vitals['avg_lcp_seconds'],
                name='LCP', line=dict(color='#4ECDC4', width=3), fill='tozeroy'))
            fig.add_hline(y=2.5, line_dash="dash", line_color="green", annotation_text="Good (≤2.5s)")
            fig.add_hline(y=4.0, line_dash="dash", line_color="orange", annotation_text="Needs Improvement (≤4.0s)")
            fig.update_layout(title='LCP - Largest Contentful Paint', yaxis_title='Seconds',
                template=chart_template, height=300,
                plot_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#262730'),
                paper_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#0E1117'),
                font=dict(color=('#262730' if st.session_state.get('theme') == 'light' else '#FAFAFA')))
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=df_vitals['date'], y=df_vitals['avg_fcp_seconds'],
                name='FCP', line=dict(color='#45B7D1', width=3), fill='tozeroy'))
            fig2.add_hline(y=1.8, line_dash="dash", line_color="green", annotation_text="Good (≤1.8s)")
            fig2.add_hline(y=3.0, line_dash="dash", line_color="orange", annotation_text="Needs Improvement (≤3.0s)")
            fig2.update_layout(title='FCP - First Contentful Paint', yaxis_title='Seconds',
                template=chart_template, height=300,
                plot_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#262730'),
                paper_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#0E1117'),
                font=dict(color=('#262730' if st.session_state.get('theme') == 'light' else '#FAFAFA')))
            st.plotly_chart(fig2, use_container_width=True)
        
        col3, col4 = st.columns(2)
        
        with col3:
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(x=df_vitals['date'], y=df_vitals['avg_inp_ms'],
                name='INP', line=dict(color='#F7B731', width=3), fill='tozeroy'))
            fig3.add_hline(y=200, line_dash="dash", line_color="green", annotation_text="Good (≤200ms)")
            fig3.add_hline(y=500, line_dash="dash", line_color="orange", annotation_text="Needs Improvement (≤500ms)")
            fig3.update_layout(title='INP - Interaction to Next Paint', yaxis_title='Milliseconds',
                template=chart_template, height=300,
                plot_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#262730'),
                paper_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#0E1117'),
                font=dict(color=('#262730' if st.session_state.get('theme') == 'light' else '#FAFAFA')))
            st.plotly_chart(fig3, use_container_width=True)
        
        with col4:
            fig4 = go.Figure()
            fig4.add_trace(go.Scatter(x=df_vitals['date'], y=df_vitals['avg_cls_score'],
                name='CLS', line=dict(color='#FF6B6B', width=3), fill='tozeroy'))
            fig4.add_hline(y=0.1, line_dash="dash", line_color="green", annotation_text="Good (≤0.1)")
            fig4.add_hline(y=0.25, line_dash="dash", line_color="orange", annotation_text="Needs Improvement (≤0.25)")
            fig4.update_layout(title='CLS - Cumulative Layout Shift', yaxis_title='Score',
                template=chart_template, height=300,
                plot_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#262730'),
                paper_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#0E1117'),
                font=dict(color=('#262730' if st.session_state.get('theme') == 'light' else '#FAFAFA')))
            st.plotly_chart(fig4, use_container_width=True)
        
        st.markdown("---")
        
        # Performance distribution
        st.subheader("📊 Performance Score Distribution")
        
        total_lcp = latest['lcp_good'] + latest['lcp_needs_improvement'] + latest['lcp_poor']
        total_fcp = latest['fcp_good'] + latest['fcp_needs_improvement'] + latest['fcp_poor']
        total_inp = latest['inp_good'] + latest['inp_needs_improvement'] + latest['inp_poor']
        total_cls = latest['cls_good'] + latest['cls_needs_improvement'] + latest['cls_poor']
        
        perf_data = pd.DataFrame({
            'Metric': ['LCP', 'FCP', 'INP', 'CLS'],
            'Good': [
                (latest['lcp_good'] / total_lcp * 100) if total_lcp > 0 else 0,
                (latest['fcp_good'] / total_fcp * 100) if total_fcp > 0 else 0,
                (latest['inp_good'] / total_inp * 100) if total_inp > 0 else 0,
                (latest['cls_good'] / total_cls * 100) if total_cls > 0 else 0
            ],
            'Needs Improvement': [
                (latest['lcp_needs_improvement'] / total_lcp * 100) if total_lcp > 0 else 0,
                (latest['fcp_needs_improvement'] / total_fcp * 100) if total_fcp > 0 else 0,
                (latest['inp_needs_improvement'] / total_inp * 100) if total_inp > 0 else 0,
                (latest['cls_needs_improvement'] / total_cls * 100) if total_cls > 0 else 0
            ],
            'Poor': [
                (latest['lcp_poor'] / total_lcp * 100) if total_lcp > 0 else 0,
                (latest['fcp_poor'] / total_fcp * 100) if total_fcp > 0 else 0,
                (latest['inp_poor'] / total_inp * 100) if total_inp > 0 else 0,
                (latest['cls_poor'] / total_cls * 100) if total_cls > 0 else 0
            ]
        })
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Good', x=perf_data['Metric'], y=perf_data['Good'], marker_color='#00C853'))
        fig.add_trace(go.Bar(name='Needs Improvement', x=perf_data['Metric'], y=perf_data['Needs Improvement'], marker_color='#FFA726'))
        fig.add_trace(go.Bar(name='Poor', x=perf_data['Metric'], y=perf_data['Poor'], marker_color='#FF5252'))
        
        fig.update_layout(barmode='stack', title='Performance Score Distribution',
            yaxis_title='Percentage (%)', template=chart_template, height=400,
            plot_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#262730'),
            paper_bgcolor=('#ffffff' if st.session_state.get('theme') == 'light' else '#0E1117'),
            font=dict(color=('#262730' if st.session_state.get('theme') == 'light' else '#FAFAFA')))
        
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.info("💡 Web Vitals tracking requires PostHog integration with Web Vitals autocapture enabled.")
        st.markdown("""
        **To enable Web Vitals tracking:**
        1. Install the PostHog library on your frontend
        2. Enable Web Vitals autocapture in PostHog settings
        3. Configure PostHog to export data to BigQuery
        4. Data will appear here within 24 hours
        
        **Metrics you'll see once configured:**
        - **LCP**: Loading performance
        - **FCP**: Initial rendering speed
        - **INP**: Interactivity responsiveness
        - **CLS**: Visual stability
        """)

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Developer Dashboard v2.1 - Enhanced with PostHog Metrics")
