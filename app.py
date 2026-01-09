"""
MIND Platform - Educational Analytics Dashboard
Main Application Entry Point
"""

import streamlit as st
from utils.auth_handler import initialize_session_state, show_login_page, show_user_info_sidebar
from config.auth import can_access_page

# Page configuration
st.set_page_config(
    page_title="MIVA - MIND Platform",
    page_icon="assets/miva_logo_dark.png",  # Will show in browser tab
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize theme if not set
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

# Apply theme-specific CSS
if st.session_state.theme == 'light':
    st.markdown("""
        <style>
        /* Light theme */
        .stApp {
            background-color: #ffffff;
            color: #262730 !important;
        }
        .stSidebar, section[data-testid="stSidebar"] {
            background-color: #f0f2f6;
        }
        /* Force dark text in light mode */
        .stMarkdown, .stText, p, span, div, h1, h2, h3, h4, h5, h6, label {
            color: #262730 !important;
        }
        
        /* Main container styling */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* Metric cards */
        [data-testid="stMetricValue"] {
            font-size: 2rem;
            font-weight: 600;
        }
        
        [data-testid="stMetricDelta"] {
            font-size: 1rem;
        }
        
        /* Headers */
        h1 {
            color: #e63946 !important;
            padding-bottom: 1rem;
            border-bottom: 2px solid #e63946;
        }
        
        h2 {
            color: #457b9d !important;
            margin-top: 2rem;
        }
        
        h3 {
            color: #1d3557 !important;
        }
        
        /* Cards and containers */
        .stAlert {
            border-radius: 10px;
        }
        
        /* Buttons */
        .stButton>button {
            border-radius: 8px;
            border: 1px solid #e63946;
            transition: all 0.3s;
            color: #262730 !important;
        }
        
        .stButton>button:hover {
            background-color: #e63946;
            color: white !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(230, 57, 70, 0.3);
        }
        
        /* DataFrames */
        .dataframe {
            border-radius: 8px;
        }
        
        /* Hide hamburger menu and footer */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }
        
        ::-webkit-scrollbar-track {
            background: #e0e0e0;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #e63946;
            border-radius: 5px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #c7313a;
        }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        /* Dark theme (default) */
        .stApp {
            background-color: #0e1117;
            color: #fafafa !important;
        }
        .stSidebar, section[data-testid="stSidebar"] {
            background-color: #262730;
        }
        /* Force white text on all elements in dark mode */
        .stMarkdown, .stText, p, span, div, h1, h2, h3, h4, h5, h6, label {
            color: #fafafa !important;
        }
        /* Headers specifically */
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, 
        .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
            color: #ffffff !important;
        }
        /* Metric labels and values */
        div[data-testid="stMetric"] label,
        div[data-testid="stMetric"] div {
            color: #fafafa !important;
        }
        /* Button text */
        .stButton>button {
            color: #fafafa !important;
        }
        /* Input fields - dark backgrounds with white text */
        input, textarea, select {
            background-color: #262730 !important;
            color: #fafafa !important;
            border: 1px solid #4a4a4a !important;
        }
        /* Input placeholders */
        input::placeholder, textarea::placeholder {
            color: #999999 !important;
        }
        /* Selectbox dropdown */
        div[data-baseweb="select"] > div {
            background-color: #262730 !important;
            color: #fafafa !important;
        }
        /* Selectbox options */
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
        /* Date/Time inputs */
        .stDateInput > div > div > input,
        .stTimeInput > div > div > input {
            background-color: #262730 !important;
            color: #fafafa !important;
        }
        /* Number inputs */
        .stNumberInput > div > div > input {
            background-color: #262730 !important;
            color: #fafafa !important;
        }
        /* Text area */
        .stTextArea > div > div > textarea {
            background-color: #262730 !important;
            color: #fafafa !important;
        }
        /* Multiselect */
        .stMultiSelect > div > div {
            background-color: #262730 !important;
            color: #fafafa !important;
        }
        /* Slider labels */
        .stSlider > label {
            color: #fafafa !important;
        }
        
        /* Main container styling */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* Metric cards */
        [data-testid="stMetricValue"] {
            font-size: 2rem;
            font-weight: 600;
        }
        
        [data-testid="stMetricDelta"] {
            font-size: 1rem;
        }
        
        /* Headers */
        h1 {
            color: #FF6B6B !important;
            padding-bottom: 1rem;
            border-bottom: 2px solid #FF6B6B;
        }
        
        h2 {
            color: #4ECDC4 !important;
            margin-top: 2rem;
        }
        
        h3 {
            color: #45B7D1 !important;
        }
        
        /* Cards and containers */
        .stAlert {
            border-radius: 10px;
        }
        
        /* Buttons */
        .stButton>button {
            border-radius: 8px;
            border: 1px solid #FF6B6B;
            transition: all 0.3s;
        }
        
        .stButton>button:hover {
            background-color: #FF6B6B;
            color: white !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(255, 107, 107, 0.3);
        }
        
        /* DataFrames */
        .dataframe {
            border-radius: 8px;
        }
        
        /* Hide hamburger menu and footer */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Custom scrollbar */
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

# Initialize session state
initialize_session_state()

# ALWAYS show sidebar with role cards (whether logged in or not)
with st.sidebar:
    import base64
    
    # Theme toggle at top of sidebar
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.session_state.get('theme', 'dark') == 'dark':
            if st.button("☀️", help="Switch to light mode", key="sidebar_theme_toggle"):
                st.session_state.theme = 'light'
                st.rerun()
        else:
            if st.button("🌙", help="Switch to dark mode", key="sidebar_theme_toggle"):
                st.session_state.theme = 'dark'
                st.rerun()
    
    # Display theme-aware MIVA logo
    try:
        if st.session_state.get('theme', 'dark') == 'dark':
            logo_path = "/mount/src/mind-platform/assets/miva_logo_light.png"
        else:
            logo_path = "/mount/src/mind-platform/assets/miva_logo_dark.png"
        
        import os
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                logo_b64 = base64.b64encode(f.read()).decode()
            
            st.markdown(f"""
                <div style="margin-bottom: 1rem;">
                    <img src="data:image/png;base64,{logo_b64}" width="180" alt="MIVA Logo">
                </div>
            """, unsafe_allow_html=True)
    except:
        pass
    
    st.markdown("---")
    
    # Show user info if authenticated, otherwise show role selection
    if st.session_state.get('authenticated', False):
        st.markdown(f"**👤 {st.session_state.user_name}**")
        st.markdown(f"*{st.session_state.user_role.title()}*")
        st.markdown(f"📧 {st.session_state.user_email}")
        
        st.markdown("---")
        st.markdown("### 📊 Dashboards")
        
        # Show available dashboards based on role
        user_role = st.session_state.user_role
        
        if can_access_page(user_role, 'Admin'):
            if st.button("👨🏿‍💼 Admin", use_container_width=True, key="nav_admin"):
                st.switch_page("pages/1_👨🏿‍💼_Admin.py")
        
        if can_access_page(user_role, 'Developer'):
            if st.button("👨🏿‍💻 Developer", use_container_width=True, key="nav_dev"):
                st.switch_page("pages/2_👨🏿‍💻_Developer.py")
        
        if can_access_page(user_role, 'Faculty'):
            if st.button("👩🏿‍🏫 Faculty", use_container_width=True, key="nav_faculty"):
                st.switch_page("pages/3_👩🏿‍🏫_Faculty.py")
        
        if can_access_page(user_role, 'Student'):
            if st.button("👨🏿‍🎓 Student", use_container_width=True, key="nav_student"):
                st.switch_page("pages/4_👨🏿‍🎓_Student.py")
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            from utils.auth_handler import logout
            logout()
            st.rerun()
    else:
        # Show role cards for non-authenticated users
        st.markdown("### 📊 Choose Your Dashboard")
        st.markdown("Login to access your role-specific analytics")
        
        st.markdown("---")
        
        # Role cards
        st.markdown("""
        **👨🏿‍💼 Admin**  
        System health & analytics
        """)
        
        st.markdown("""
        **👨🏿‍💻 Developer**  
        API performance & debugging
        """)
        
        st.markdown("""
        **👩🏿‍🏫 Faculty**  
        Student performance tracking
        """)
        
        st.markdown("""
        **👨🏿‍🎓 Student**  
        Personal learning journey
        """)

# Main content area - Show login if not authenticated
if not st.session_state.get('authenticated', False):
    # Login page (centered)
    st.markdown("""
        <style>
        .login-container {
            max-width: 450px;
            margin: 50px auto;
            padding: 40px;
            background-color: #262730;
            border-radius: 12px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
        }
        .dashboard-title {
            text-align: center;
            margin-bottom: 2rem;
            font-size: 2rem;
            font-weight: 600;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="dashboard-title">MIND Analytics Dashboard</div>', unsafe_allow_html=True)
        st.markdown("### 🔐 Login to Continue")
        st.markdown("---")
        
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="user@mind.edu", key="login_email")
            password = st.text_input("Password", type="password", placeholder="Enter password", key="login_password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                from utils.auth_handler import login
                if login(email, password):
                    st.success(f"✅ Welcome, {st.session_state.user_name}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid email or password")
        
        st.markdown("---")
        
        # Demo credentials info
        with st.expander("📝 Demo Credentials"):
            st.markdown("""
            **Admin:**  
            📧 admin@miva.edu  
            🔑 admin123
            
            **Developer:**  
            📧 dev@miva.edu  
            🔑 dev123
            
            **Faculty:**  
            📧 faculty@miva.edu  
            🔑 faculty123
            
            **Student:**  
            📧 student@miva.edu  
            🔑 student123
            """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #888; padding: 20px;'>
            <p>MIND Platform v2.0 | AI-Enhanced Educational Analytics</p>
            <p>Powered by BigQuery, Streamlit & Plotly</p>
        </div>
    """, unsafe_allow_html=True)
else:
    # User is authenticated - redirect to their default dashboard
    user_role = st.session_state.get('user_role', 'student')
    
    st.markdown("### 🎉 Login Successful!")
    st.markdown(f"Welcome back, **{st.session_state.user_name}**!")
    
    st.markdown("---")
    
    # Auto-redirect message
    st.info(f"Redirecting you to your {user_role.title()} Dashboard...")
    
    # Role-specific redirect
    if user_role == 'admin':
        st.switch_page("pages/1_👨🏿‍💼_Admin.py")
    elif user_role == 'developer':
        st.switch_page("pages/2_👨🏿‍💻_Developer.py")
    elif user_role == 'faculty':
        st.switch_page("pages/3_👩🏿‍🏫_Faculty.py")
    else:  # student
        st.switch_page("pages/4_👨🏿‍🎓_Student.py")
