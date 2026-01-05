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

# Show login page if not authenticated
if not st.session_state.get('authenticated', False):
    show_login_page()
else:
    # Show sidebar with user info and navigation
    show_user_info_sidebar()
    
    # Main content area
    st.title("MIND Platform")
    st.markdown("### AI-Enhanced Educational Analytics Dashboard")
    
    # Welcome message with role-specific information
    user_role = st.session_state.get('user_role', 'user')
    user_name = st.session_state.get('user_name', 'User')
    
    st.markdown(f"""
    Welcome back, **{user_name}**! 
    
    You are logged in as: **{user_role.title()}**
    """)
    
    # Role-specific guidance
    if user_role == 'admin':
        st.info("""
        **Admin Dashboard Features:**
        - 📊 System health monitoring and KPIs
        - 👥 User management and activity tracking
        - 💰 AI resource consumption and costs
        - ⚙️ Platform configuration and settings
        - 📈 Comprehensive analytics across all users
        """)
    elif user_role == 'developer':
        st.info("""
        **Developer Dashboard Features:**
        - 🔧 API performance metrics and latency analysis
        - 🤖 AI model usage and token distribution
        - 🐛 Error tracking and trace debugging
        - 📡 Backend telemetry and system health
        """)
    elif user_role == 'faculty':
        st.info("""
        **Faculty Dashboard Features:**
        - 📚 Student performance analytics
        - 📊 Case study effectiveness tracking
        - 🎯 Learning outcome assessment
        - ⚠️ At-risk student identification
        - 📈 Cohort and department comparisons
        """)
    elif user_role == 'student':
        st.info("""
        **Student Dashboard Features:**
        - 📖 Personal learning journey tracking
        - 🎯 Performance across rubric categories
        - 📊 Progress comparison with class averages
        - 📝 Past conversation reviews
        - 🏆 Achievement highlights
        """)
    
    st.markdown("---")
    
    # Quick navigation
    st.markdown("### 🚀 Quick Navigation")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if can_access_page(user_role, 'Admin'):
            if st.button("👨🏿‍💼 Admin Dashboard", use_container_width=True):
                st.switch_page("pages/1_👨🏿‍💼_Admin.py")
    
    with col2:
        if can_access_page(user_role, 'Developer'):
            if st.button("👨🏿‍💻 Developer Dashboard", use_container_width=True):
                st.switch_page("pages/2_👨🏿‍💻_Developer.py")
    
    with col3:
        if can_access_page(user_role, 'Faculty'):
            if st.button("👩🏿‍🏫 Faculty Dashboard", use_container_width=True):
                st.switch_page("pages/3_👩🏿‍🏫_Faculty.py")
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        if can_access_page(user_role, 'Student'):
            if st.button("👨🏿‍🎓 Student Dashboard", use_container_width=True):
                st.switch_page("pages/4_👨🏿‍🎓_Student.py")
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #666; padding: 20px;'>
            <p>MIND Platform v1.0 | AI-Enhanced Educational Analytics</p>
            <p>Powered by BigQuery, Streamlit & Plotly</p>
        </div>
    """, unsafe_allow_html=True)
