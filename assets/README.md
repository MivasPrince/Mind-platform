# 🧠 MIND Platform - Educational Analytics Dashboard

A professional, production-ready analytics dashboard for the MIND Platform, an AI-enhanced educational case study system. Built with Streamlit, BigQuery, and Plotly for comprehensive learning analytics.

## 🌟 Features

### Role-Based Access Control (RBAC)
- **Admin**: System health, user management, AI resource tracking
- **Developer**: API performance, AI metrics, trace debugging
- **Faculty**: Student performance, cohort analytics, at-risk identification
- **Student**: Personal learning journey, performance tracking, conversation history

### Advanced Analytics
- 📊 Interactive visualizations with Plotly
- 🎯 Performance tracking across rubric categories
- 📈 Trend analysis and improvement tracking
- 🔍 Deep-dive capabilities with filtering and drill-down
- 📥 CSV/Excel export functionality
- 🤖 AI usage and cost monitoring

### Professional UI/UX
- 🎨 Modern dark theme
- 📱 Responsive design
- ⚡ Fast query caching
- 🔄 Real-time data updates
- 🎭 Custom CSS styling

## 🏗️ Architecture

```
mind-platform/
├── .streamlit/
│   ├── config.toml          # Streamlit configuration
│   └── secrets.toml         # BigQuery credentials (not in git)
├── app.py                   # Main entry point
├── config/
│   ├── __init__.py
│   ├── database.py          # BigQuery connection
│   └── auth.py              # User roles & permissions
├── utils/
│   ├── __init__.py
│   ├── auth_handler.py      # Authentication logic
│   ├── query_builder.py     # SQL query templates
│   └── chart_components.py  # Reusable visualizations
├── pages/
│   ├── 1_👨‍💼_Admin.py        # Admin dashboard
│   ├── 2_👨‍💻_Developer.py    # Developer dashboard
│   ├── 3_👩‍🏫_Faculty.py      # Faculty dashboard
│   └── 4_🎓_Student.py       # Student dashboard
├── requirements.txt
├── .gitignore
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Cloud BigQuery account
- Service account with BigQuery read permissions

### Local Development

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd mind-platform
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure BigQuery credentials**
```bash
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
# Edit .streamlit/secrets.toml with your service account credentials
```

5. **Run the application**
```bash
streamlit run app.py
```

6. **Access the dashboard**
Open your browser to `http://localhost:8501`

### Demo Credentials

```
Admin:     admin@mind.edu     / mind2024
Developer: dev@mind.edu       / mind2024
Faculty:   faculty@mind.edu   / mind2024
Student:   student@mind.edu   / mind2024
```

## 📦 Deployment to Streamlit Cloud

### Step 1: Prepare Repository

1. **Push to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo>
git push -u origin main
```

2. **Verify .gitignore**
Ensure `.streamlit/secrets.toml` is in `.gitignore` to prevent credentials from being committed.

### Step 2: Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select your repository
4. Set main file path: `app.py`
5. Click "Advanced settings"

### Step 3: Configure Secrets

In the Streamlit Cloud dashboard, add your secrets:

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = """-----BEGIN PRIVATE KEY-----
YOUR_PRIVATE_KEY_HERE
-----END PRIVATE KEY-----"""
client_email = "your-service-account@project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-cert-url"
```

### Step 4: Deploy

Click "Deploy" and wait for the app to start!

## 🔐 Security

### Authentication
- BCrypt password hashing
- Session-based authentication
- Role-based access control
- Read-only BigQuery queries

### Best Practices
- Never commit secrets to version control
- Use environment-specific credentials
- Regularly rotate service account keys
- Review BigQuery permissions

## 📊 Database Schema

The platform uses the following BigQuery tables:

- `user`: Student and user information
- `casestudy`: Case study definitions
- `sessions`: Learning session data
- `conversation`: AI conversation transcripts
- `grades`: Performance and rubric scores
- `session_analytics`: User engagement metrics
- `event_stream`: User interaction events
- `backend_telemetry`: API and AI performance data

## 🎯 Key Features by Role

### Admin Dashboard
- System health monitoring
- User activity tracking
- AI resource consumption
- Error rate analysis
- Grade distribution
- Cohort/department performance

### Developer Dashboard
- API performance metrics
- AI model usage and costs
- Response time analysis
- Trace debugging
- Error tracking
- Token consumption

### Faculty Dashboard
- Student performance analytics
- Rubric category breakdown
- At-risk student identification
- Case study effectiveness
- Cohort comparisons
- Performance trends

### Student Dashboard
- Personal performance radar
- Score progression over time
- Rubric strength analysis
- Conversation history
- Case study completion
- Achievement tracking

## 🛠️ Configuration

### Streamlit Configuration (.streamlit/config.toml)
```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
```

### Query Caching
- Default TTL: 3600 seconds (1 hour)
- Configurable per query
- Manual cache clearing available in Admin settings

## 📈 Performance Optimization

- ✅ Query result caching
- ✅ Efficient SQL with aggregations
- ✅ Lazy loading of visualizations
- ✅ Minimal data transfer
- ✅ Index-optimized queries

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is proprietary and confidential.

## 🐛 Troubleshooting

### Connection Issues
- Verify BigQuery credentials in secrets.toml
- Check service account permissions
- Ensure dataset location matches (europe-west3)

### Authentication Problems
- Clear browser cache
- Check user credentials
- Verify role permissions

### Performance Issues
- Clear Streamlit cache (Admin > Settings)
- Check BigQuery query costs
- Optimize date range filters

## 📞 Support

For issues or questions:
- Create an issue in GitHub
- Contact: [your-email@domain.com]

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io)
- Powered by [Google BigQuery](https://cloud.google.com/bigquery)
- Visualizations by [Plotly](https://plotly.com)

---

**MIND Platform v1.0** | Educational Analytics Dashboard
