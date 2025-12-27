"""
Admin Dashboard
System Health, User Management & Governance Analytics
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Direct imports from utils modules
from utils.auth_handler import (
    require_authentication, show_user_info_sidebar, get_current_user
)
from utils.chart_components import (
    create_metric_cards, plot_line_chart, plot_bar_chart, plot_pie_chart,
    plot_gauge, create_multi_line_chart, export_dataframe_to_csv
)
from utils.query_builder import QueryBuilder
from config.database import get_cached_query, run_query
from config.auth import can_access_page

# Page config
st.set_page_config(
    page_title="Admin Dashboard | MIND Platform",
    page_icon="👨‍💼",
    layout="wide"
)

# Authentication check
require_authentication()

# Check role permission
user = get_current_user()
if not can_access_page(user['role'], 'Admin'):
    st.error("⛔ Access Denied: Admin privileges required")
    st.stop()

# Sidebar
show_user_info_sidebar()

# Header
st.title("👨‍💼 Admin Dashboard")
st.markdown("### System Health, Governance & Resource Management")
st.markdown("---")

# Filters in sidebar
with st.sidebar:
    st.markdown("### 📊 Filters")
    
    date_range = st.selectbox(
        "Time Period",
        ["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"],
        index=1
    )
    
    # Convert to days
    days_map = {
        "Last 7 Days": 7,
        "Last 30 Days": 30,
        "Last 90 Days": 90,
        "All Time": 9999
    }
    days = days_map[date_range]
    
    st.markdown("---")
    
    auto_refresh = st.checkbox("Auto-refresh (30s)", value=False)
    
    if auto_refresh:
        st.rerun()

# Main content
tabs = st.tabs([
    "📊 Overview",
    "👥 User Analytics",
    "🎓 Learning Metrics",
    "🤖 AI Resources",
    "🏥 System Health",
    "⚙️ Settings"
])

# TAB 1: OVERVIEW
with tabs[0]:
    st.markdown("## 📊 Executive Overview")
    
    # Top-level KPIs
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Get metrics
    total_users_df = get_cached_query(QueryBuilder.get_total_users())
    active_users_df = get_cached_query(QueryBuilder.get_active_users(days))
    total_sessions_df = get_cached_query(QueryBuilder.get_total_sessions())
    avg_grade_df = get_cached_query(QueryBuilder.get_average_grade())
    system_health_df = get_cached_query(QueryBuilder.get_system_health())
    
    with col1:
        total_users = total_users_df['total_users'].iloc[0] if total_users_df is not None and not total_users_df.empty else 0
        st.metric("Total Users", f"{total_users:,}")
    
    with col2:
        active_users = active_users_df['active_users'].iloc[0] if active_users_df is not None and not active_users_df.empty else 0
        st.metric(f"Active Users ({date_range})", f"{active_users:,}")
    
    with col3:
        total_sessions = total_sessions_df['total_sessions'].iloc[0] if total_sessions_df is not None and not total_sessions_df.empty else 0
        st.metric("Total Sessions", f"{total_sessions:,}")
    
    with col4:
        avg_grade = avg_grade_df['avg_grade'].iloc[0] if avg_grade_df is not None and not avg_grade_df.empty else 0
        st.metric("Average Grade", f"{avg_grade:.1f}%")
    
    with col5:
        if system_health_df is not None and not system_health_df.empty:
            error_rate = (system_health_df['error_count'].iloc[0] / system_health_df['total_requests'].iloc[0] * 100) if system_health_df['total_requests'].iloc[0] > 0 else 0
            st.metric("Error Rate", f"{error_rate:.2f}%", delta=f"-{error_rate:.1f}%" if error_rate < 5 else None)
        else:
            st.metric("Error Rate", "N/A")
    
    st.markdown("---")
    
    # Charts row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Daily Active Users Trend")
        dau_df = get_cached_query(QueryBuilder.get_daily_active_users(days))
        if dau_df is not None and not dau_df.empty:
            fig = plot_line_chart(dau_df, 'date', 'active_users', 
                                 'Daily Active Users', height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No user activity data available")
    
    with col2:
        st.markdown("### 📊 Grade Distribution")
        grade_dist_df = get_cached_query(QueryBuilder.get_grade_distribution())
        if grade_dist_df is not None and not grade_dist_df.empty:
            fig = plot_pie_chart(grade_dist_df, 'count', 'grade_bracket',
                                'Student Grade Distribution', height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No grade data available")
    
    # Charts row 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Case Study Performance")
        case_perf_df = get_cached_query(QueryBuilder.get_case_study_performance())
        if case_perf_df is not None and not case_perf_df.empty:
            fig = plot_bar_chart(case_perf_df, 'case_study', 'avg_score',
                                'Average Score by Case Study',
                                orientation='h', height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No case study data available")
    
    with col2:
        st.markdown("### 📱 Session Engagement")
        engagement_df = get_cached_query(QueryBuilder.get_session_engagement())
        if engagement_df is not None and not engagement_df.empty:
            fig = create_multi_line_chart(
                engagement_df, 'date',
                ['avg_duration_minutes', 'avg_pageviews'],
                'Session Engagement Metrics',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No engagement data available")

# TAB 2: USER ANALYTICS
with tabs[1]:
    st.markdown("## 👥 User Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Performance by Cohort")
        cohort_perf_df = get_cached_query(QueryBuilder.get_cohort_performance())
        if cohort_perf_df is not None and not cohort_perf_df.empty:
            st.dataframe(cohort_perf_df, use_container_width=True, height=300)
            export_dataframe_to_csv(cohort_perf_df, "cohort_performance.csv")
        else:
            st.info("No cohort data available")
    
    with col2:
        st.markdown("### 📊 Performance by Department")
        dept_perf_df = get_cached_query(QueryBuilder.get_department_performance())
        if dept_perf_df is not None and not dept_perf_df.empty:
            st.dataframe(dept_perf_df, use_container_width=True, height=300)
            export_dataframe_to_csv(dept_perf_df, "department_performance.csv")
        else:
            st.info("No department data available")
    
    st.markdown("---")
    st.markdown("### 📋 All Student Performance")
    
    student_perf_df = get_cached_query(QueryBuilder.get_student_performance())
    if student_perf_df is not None and not student_perf_df.empty:
        # Add search functionality
        search = st.text_input("🔍 Search students", placeholder="Enter name or email")
        
        if search:
            filtered_df = student_perf_df[
                student_perf_df['student_name'].str.contains(search, case=False, na=False) |
                student_perf_df['student_email'].str.contains(search, case=False, na=False)
            ]
        else:
            filtered_df = student_perf_df
        
        st.dataframe(filtered_df, use_container_width=True, height=400)
        export_dataframe_to_csv(filtered_df, "student_performance.csv")
    else:
        st.info("No student performance data available")

# TAB 3: LEARNING METRICS
with tabs[2]:
    st.markdown("## 🎓 Learning Analytics")
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    if avg_grade_df is not None and not avg_grade_df.empty:
        with col1:
            st.metric("Avg Communication", f"{avg_grade_df['avg_communication'].iloc[0]:.1f}%")
        with col2:
            st.metric("Avg Comprehension", f"{avg_grade_df['avg_comprehension'].iloc[0]:.1f}%")
        with col3:
            st.metric("Avg Critical Thinking", f"{avg_grade_df['avg_critical_thinking'].iloc[0]:.1f}%")
        with col4:
            st.metric("Overall Average", f"{avg_grade_df['avg_grade'].iloc[0]:.1f}%")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⚠️ Students at Risk")
        at_risk_df = get_cached_query(QueryBuilder.get_students_at_risk(60.0))
        if at_risk_df is not None and not at_risk_df.empty:
            st.dataframe(at_risk_df, use_container_width=True, height=400)
            export_dataframe_to_csv(at_risk_df, "students_at_risk.csv")
            
            st.warning(f"**{len(at_risk_df)} students** are currently below 60% average")
        else:
            st.success("✅ No students at risk!")
    
    with col2:
        st.markdown("### 🏆 Top Performers")
        top_students_df = get_cached_query(QueryBuilder.get_student_performance())
        if top_students_df is not None and not top_students_df.empty:
            top_10 = top_students_df.head(10)
            st.dataframe(top_10, use_container_width=True, height=400)
            export_dataframe_to_csv(top_10, "top_performers.csv")
        else:
            st.info("No performance data available")

# TAB 4: AI RESOURCES
with tabs[3]:
    st.markdown("## 🤖 AI Resource Management")
    
    # AI Token Usage KPIs
    token_usage_df = get_cached_query(QueryBuilder.get_ai_token_usage())
    
    col1, col2, col3, col4 = st.columns(4)
    
    if token_usage_df is not None and not token_usage_df.empty:
        total_tokens = token_usage_df['total_tokens'].iloc[0] if token_usage_df['total_tokens'].iloc[0] else 0
        input_tokens = token_usage_df['input_tokens'].iloc[0] if token_usage_df['input_tokens'].iloc[0] else 0
        output_tokens = token_usage_df['output_tokens'].iloc[0] if token_usage_df['output_tokens'].iloc[0] else 0
        
        # Estimated cost ($15 per 1M tokens as baseline)
        estimated_cost = (total_tokens / 1_000_000) * 15.0
        
        with col1:
            st.metric("Total Tokens", f"{total_tokens:,.0f}")
        with col2:
            st.metric("Input Tokens", f"{input_tokens:,.0f}")
        with col3:
            st.metric("Output Tokens", f"{output_tokens:,.0f}")
        with col4:
            st.metric("Estimated Cost", f"${estimated_cost:,.2f}")
    else:
        st.info("No AI usage data available")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🤖 AI Model Distribution")
        model_dist_df = get_cached_query(QueryBuilder.get_ai_model_distribution())
        if model_dist_df is not None and not model_dist_df.empty:
            fig = plot_bar_chart(model_dist_df, 'model', 'request_count',
                                'Requests by AI Model', height=350)
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(model_dist_df, use_container_width=True)
        else:
            st.info("No AI model data available")
    
    with col2:
        st.markdown("### 💰 Token Usage Over Time")
        # Note: This would need a time-series query
        st.info("Token usage trending chart - data pending")

# TAB 5: SYSTEM HEALTH
with tabs[4]:
    st.markdown("## 🏥 System Health & Performance")
    
    if system_health_df is not None and not system_health_df.empty:
        # KPIs
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Requests", f"{system_health_df['total_requests'].iloc[0]:,}")
        with col2:
            st.metric("Error Count", f"{system_health_df['error_count'].iloc[0]:,}")
        with col3:
            st.metric("Avg Latency", f"{system_health_df['avg_response_time'].iloc[0]:.0f}ms")
        with col4:
            st.metric("P95 Latency", f"{system_health_df['p95_latency'].iloc[0]:.0f}ms")
        with col5:
            st.metric("P99 Latency", f"{system_health_df['p99_latency'].iloc[0]:.0f}ms")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🚦 System Uptime")
        # Calculate uptime percentage
        if system_health_df is not None and not system_health_df.empty:
            uptime = ((system_health_df['total_requests'].iloc[0] - system_health_df['error_count'].iloc[0]) / 
                     system_health_df['total_requests'].iloc[0] * 100) if system_health_df['total_requests'].iloc[0] > 0 else 0
            
            fig = plot_gauge(uptime, "System Uptime %", max_value=100, height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No uptime data available")
    
    with col2:
        st.markdown("### ⚡ Response Time by Route")
        route_perf_df = get_cached_query(QueryBuilder.get_response_time_by_route())
        if route_perf_df is not None and not route_perf_df.empty:
            fig = plot_bar_chart(route_perf_df.head(10), 'http_route', 'p95_latency',
                                'P95 Latency by API Route',
                                orientation='h', height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No route performance data available")
    
    st.markdown("---")
    st.markdown("### 🐛 Recent Errors")
    
    error_log_df = get_cached_query(QueryBuilder.get_error_log(50))
    if error_log_df is not None and not error_log_df.empty:
        st.dataframe(error_log_df, use_container_width=True, height=400)
        export_dataframe_to_csv(error_log_df, "error_log.csv")
    else:
        st.success("✅ No recent errors!")

# TAB 6: SETTINGS
with tabs[5]:
    st.markdown("## ⚙️ System Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔐 Access Control")
        st.info("""
        **User Roles:**
        - Admin: Full system access
        - Developer: Technical metrics & debugging
        - Faculty: Academic analytics
        - Student: Personal performance
        """)
        
        if st.button("👥 Manage Users"):
            st.info("User management interface - Coming soon")
    
    with col2:
        st.markdown("### 📊 Data Settings")
        
        cache_ttl = st.number_input("Cache TTL (seconds)", min_value=60, max_value=3600, value=3600)
        
        if st.button("🔄 Clear Cache"):
            st.cache_data.clear()
            st.success("Cache cleared successfully!")
        
        st.markdown("### 📥 Data Export")
        if st.button("📦 Export All Data"):
            st.info("Full data export - Coming soon")

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Admin Dashboard v1.0")
