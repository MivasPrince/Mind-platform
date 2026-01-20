"""
MIND Platform - Educational Analytics Dashboard
Main Portal & Authentication Page
"""

import streamlit as st
from utils.auth_handler import initialize_session_state, login, logout
from config.auth import can_access_page
import base64
import os

# Page configuration
st.set_page_config(
    page_title="MIVA - MIND Platform",
    page_icon="assets/miva_logo_dark.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize theme and session
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

initialize_session_state()

# Global CSS
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    section[data-testid="stSidebarNav"] {display: none;}
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #262730;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #FF6B6B;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #ff5252;
    }
    </style>
""", unsafe_allow_html=True)

# Theme-specific CSS
if st.session_state.theme == 'light':
    st.markdown("""
        <style>
        .stApp {
            background-color: #ffffff;
            color: #262730 !important;
        }
        .stSidebar, section[data-testid="stSidebar"] {
            background-color: #f0f2f6;
        }
        .stMarkdown, .stText, p, span, div, h1, h2, h3, h4, h5, h6, label {
            color: #262730 !important;
        }
        input, textarea, select {
            background-color: #ffffff !important;
            color: #262730 !important;
            border: 1px solid #cccccc !important;
        }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        .stApp {
            background-color: #0e1117;
            color: #fafafa !important;
        }
        .stSidebar, section[data-testid="stSidebar"] {
            background-color: #262730;
        }
        .stMarkdown, .stText, p, span, div, h1, h2, h3, h4, h5, h6, label {
            color: #fafafa !important;
        }
        input, textarea, select {
            background-color: #262730 !important;
            color: #fafafa !important;
            border: 1px solid #4a4a4a !important;
        }
        input::placeholder, textarea::placeholder {
            color: #999999 !important;
        }
        div[data-baseweb="select"] > div {
            background-color: #262730 !important;
            color: #fafafa !important;
        }
        div[role="listbox"] {
            background-color: #262730 !important;
        }
        div[role="option"] {
            background-color: #262730 !important;
            color: #fafafa !important;
        }
        div[role="option"]:hover {
            background-color: #3a3a3a !important;
        }
        </style>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.session_state.theme == 'dark':
            if st.button("☀️", help="Switch to light mode", key="theme_toggle"):
                st.session_state.theme = 'light'
                st.rerun()
        else:
            if st.button("🌙", help="Switch to dark mode", key="theme_toggle"):
                st.session_state.theme = 'dark'
                st.rerun()
    
    try:
        if st.session_state.theme == 'dark':
            logo_path = "/mount/src/mind-platform/assets/miva_logo_light.png"
        else:
            logo_path = "/mount/src/mind-platform/assets/miva_logo_dark.png"
        
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                logo_b64 = base64.b64encode(f.read()).decode()
            
            st.markdown(f"""
                <div style="margin-bottom: 1rem;">
                    <img src="data:image/png;base64,{logo_b64}" width="180" alt="MIVA Logo">
                </div>
            """, unsafe_allow_html=True)
    except:
        st.markdown("# 🧠 MIND")
    
    st.markdown("---")
    
    if st.session_state.get('authenticated', False):
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
        
        st.markdown("""
        **Four Specialized Dashboards:**
        
        👨🏿‍💼 **Admin**  
        System oversight & governance
        
        👨🏿‍💻 **Developer**  
        Technical performance & debugging
        
        👩🏿‍🏫 **Faculty**  
        Student analytics & outcomes
        
        🎓 **Student**  
        Personal learning journey
        """)

# Main Content
if not st.session_state.get('authenticated', False):
    # LOGIN PAGE
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <div style="text-align: center; margin-bottom: 2rem;">
                <h1 style="margin-bottom: 0.5rem;">MIND Analytics Dashboard</h1>
                <p style="font-size: 1.2rem; opacity: 0.8;">AI-Enhanced Educational Analytics</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🔐 Login to Continue")
        st.markdown("---")
        
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="user@mind.edu", key="login_email")
            password = st.text_input("Password", type="password", placeholder="Enter password", key="login_password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                # Email format validation
                import re
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                
                if not email:
                    st.error("❌ Please enter your email address")
                elif not re.match(email_pattern, email):
                    st.error("❌ Invalid email format. Please enter a valid email address (e.g., user@miva.edu)")
                elif not password:
                    st.error("❌ Please enter your password")
                elif login(email, password):
                    st.success(f"✅ Welcome, {st.session_state.user_name}!")
                    st.rerun()
                else:
                    st.error("❌ Incorrect email or password. Please try again.")
    
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #888; padding: 20px;'>
            <p><strong>MIND Platform v2.0</strong></p>
            <p>Powered by BigQuery, Streamlit & Plotly</p>
            <p style="font-size: 0.9rem; margin-top: 1rem;">
                MIVA Open University | Educational Analytics Dashboard
            </p>
        </div>
    """, unsafe_allow_html=True)

else:
    # DASHBOARD PORTAL
    user_role = st.session_state.user_role
    user_name = st.session_state.user_name
    
    st.markdown(f"""
        <div style="text-align: center; margin-bottom: 3rem;">
            <h1>Welcome back, {user_name}! 👋</h1>
            <p style="font-size: 1.2rem; opacity: 0.8;">
                Use the sidebar to access your dashboards
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Dashboard access info - Just show links, don't try to navigate
    st.markdown("### 📊 Your Available Dashboards")
    st.markdown("Click on the dashboard names in the **sidebar** to get started.")
    st.markdown("")
    
    # Show available dashboards as cards
    col1, col2 = st.columns(2)
    
    with col1:
        if can_access_page(user_role, 'Admin'):
            st.info("""
            **👨🏿‍💼 Administrator Dashboard**
            
            • System Health Monitoring  
            • User Analytics  
            • AI Resource Tracking  
            • Platform Configuration
            
            → Access via sidebar
            """)
        
        if can_access_page(user_role, 'Faculty'):
            st.info("""
            **👩🏿‍🏫 Faculty Dashboard**
            
            • Student Performance  
            • Case Study Analytics  
            • At-Risk Identification  
            • Progress Tracking
            
            → Access via sidebar
            """)
    
    with col2:
        if can_access_page(user_role, 'Developer'):
            st.info("""
            **👨🏿‍💻 Developer Dashboard**
            
            • API Performance Metrics  
            • Error Tracking & Debugging  
            • Backend Telemetry  
            • Web Vitals Monitoring
            
            → Access via sidebar
            """)
        
        if can_access_page(user_role, 'Student'):
            st.info("""
            **👨🏿‍🎓 Student Dashboard**
            
            • Learning Journey Tracking  
            • Performance Visualization  
            • Progress Analytics  
            • Achievement Badges
            
            → Access via sidebar
            """)
    
    st.markdown("---")
    
    # Quick stats or tips section
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success("""
        **💡 Quick Tip**  
        All your dashboards are accessible from the sidebar navigation.
        """)
    
    with col2:
        st.success(f"""
        **🎯 Your Role**  
        You have **{user_role.title()}** level access with specialized analytics.
        """)
    
    with col3:
        st.success("""
        **🔐 Security**  
        Your session is secure. Remember to logout when done.
        """)
    
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #888; padding: 20px;'>
            <p><strong>MIND Platform v2.0</strong></p>
            <p>AI-Enhanced Educational Analytics Dashboard</p>
        </div>
    """, unsafe_allow_html=True)
