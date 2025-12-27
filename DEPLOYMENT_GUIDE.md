# 🚀 MIND Platform - Deployment Guide

## Complete Deployment Checklist

### ✅ Pre-Deployment Checklist

- [ ] GitHub repository created
- [ ] BigQuery credentials ready
- [ ] Service account has read permissions
- [ ] All files reviewed and tested locally
- [ ] Secrets properly configured

---

## 📋 Step-by-Step Deployment

### 1. Local Testing (5 minutes)

```bash
# Navigate to project
cd mind-platform

# Install dependencies
pip install -r requirements.txt

# Configure secrets
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
# Edit secrets.toml with your BigQuery credentials

# Run locally
streamlit run app.py
```

**Test all 4 dashboards:**
- ✅ Login as admin@mind.edu (password: mind2024)
- ✅ Verify data loads correctly
- ✅ Check all visualizations
- ✅ Test navigation between pages

---

### 2. GitHub Setup (3 minutes)

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial MIND Platform deployment"

# Add remote (replace with your repo)
git remote add origin https://github.com/YOUR_USERNAME/mind-platform.git

# Push to GitHub
git push -u origin main
```

**Important:** Verify `.gitignore` includes:
```
.streamlit/secrets.toml
__pycache__/
*.pyc
```

---

### 3. Streamlit Cloud Deployment (5 minutes)

#### A. Create App

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"New app"**
3. Select:
   - **Repository:** your-username/mind-platform
   - **Branch:** main
   - **Main file path:** app.py
4. Click **"Advanced settings..."**

#### B. Configure Secrets

In the **Secrets** section, paste:

```toml
[gcp_service_account]
type = "service_account"
project_id = "gen-lang-client-0625543859"
private_key_id = "4c621b4ae3b06e6d092dd2476c9197740f6977f4"
private_key = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDEYHUFKTi6FGC1
9/uOFt3qui02PFjfDMh88FN22fjwqbfmSeOtBhLXQhPehCq91HKlV+AxOeSWnWVN
zoohOJU5pjCA/wERpW49uPFulUORfI9UT2pEmdqy1f3KRsWwXLiOcDtwv1DYAccp
yjpnIy+W5KqAzmLZbSfisHWsZLi5X3hq1pGSCei4XovUxPtfiNjglhBPKAvMWJJ3
LXeBnTOaPmSbYDDPiADOseELGr108FfCUwfeM21AGo9V44VB5LWtr1VF8OCiMyBO
6NTK7fVN5PwfcYMSiRe+F6+TWkJWt/jZDvUMhm2FhdmuWVno+HI3SGrhH5RvgDLW
tkwqdj+hAgMBAAECggEAElLSRHaj1IgXfI88rZXQY+k2lAWWQMzJbdACZ7f/yJv7
fP1WxVOoYSXJIxWHw/H9dxRfptQ5Mj0SQWv021PzZ59MThMNQ1thcZiuzXPXy8zY
tmQZHTjSbWa2gT/wjQvfzCmogDUXyuoCjpGQOMSxmXWxe6aWVmWfJ8GxnzIAQwqd
tjOC3DJoMHqMhtIUABYLhfH8sBeTu1Iq3WAzyouEMzunIzIYfAW4Hv3M7jfbzl3X
88mIHFJ9VbI4S7u5fcbuS4RmcPtyxzyqLQ0mCJsnBzNvzEta9wxHlJF8kToHVktM
nO3bKF3XhYf+/wHylGgnhP7M0ZGFXHf3E+pdr/MAmQKBgQDra9en4yFLuNN94Kxy
Q7pHq4WGeomFFs7z7cSNRS8myVIP41DkwlgFHw0kcqOWAXhlUXvpXwNsjV2/fFSy
5uI25h2VINEvMFy8gpx1Rm2bdZeH36t1dTXCpSSfWwOpGcCEqZ/NjKrH0F/W6bAX
Qg/kf0P2HlledaAw3TeZUE7FyQKBgQDViuTZrBe1ikobwhiYbHslAafpMoNVNGX9
sMOMKfHcydACsafFk3i0UNzfomwMf03sevDGdCb9g5eBuA5L/qw7jz/oyfHWKV55
yciNWOyap9eGYHO7zplWnxJhyYhC+b0dp46sftO+ue+U/eFej18SbhbExx0kpnmE
1uGnenD3GQKBgGbZ/qXCfVFvtjZQagahwEh/jx5peptCk7fOMQjnKOpxGgEG9th6
b6oNHtjFnOJ0Uf0x1Ejo0b4jJMn7r6VZaYtCjboRVFKhdmKFTYWO92PrxAAAoA/4
3TvkmlNkl/zQ22MaGE7dHd+eEcD654vBuN/DGhX0vGagTRQMEbZRd5jBAoGBAKM1
Ic2/+ur0Q8nNYhD1MHVLO7M+uSPhBWaMuBgjYsh1sjas42ZdXO6rsvR1ZhFzJvJr
0CRNWBOAhMZPDxZEEgz/YkAgQGaHfb6lW1O0uDlHuLDqfOn4cDfFIj580lkmGMVW
b/Qkht+JqrP8CkjEWUxzuZEyAXMmjU/bD+J58WbZAoGABzqO4ieymjgGjjn1Pv89
DOBcU4a1DIBgh7+loUIkWoyYn6v/1YwMUyCcVqXBhE6WDzhWw+3faYRL9NZrR1vm
k1IA0mhWbNxHnAI3q8SU7/vCRqtE+4UmaIIAvVipGwloDwoqC55ZrZIZwa8MFewl
gIDTw2Xjnw1vp6Pr5QvirXk=
-----END PRIVATE KEY-----"""
client_email = "mind-streamlit-dashboard@gen-lang-client-0625543859.iam.gserviceaccount.com"
client_id = "106153175537431031935"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/mind-streamlit-dashboard%40gen-lang-client-0625543859.iam.gserviceaccount.com"
```

#### C. Deploy

1. Click **"Deploy!"**
2. Wait 2-3 minutes for deployment
3. Your app will be live at: `https://your-app-name.streamlit.app`

---

## 🔐 Security Best Practices

### ⚠️ CRITICAL: Never commit secrets to GitHub!

Always verify:
```bash
# Check what's being committed
git status

# Ensure secrets.toml is NOT listed
# If it is, add to .gitignore immediately
```

### 🔒 Production Recommendations

1. **Change Default Passwords**
   - Edit `config/auth.py`
   - Update password hashes for all demo users
   - Use strong, unique passwords

2. **Enable HTTPS Only**
   - Streamlit Cloud uses HTTPS by default
   - Verify SSL certificate is valid

3. **Monitor Usage**
   - Check BigQuery usage regularly
   - Set up billing alerts
   - Review access logs

4. **Regular Updates**
   - Update dependencies monthly
   - Apply security patches promptly
   - Monitor for vulnerabilities

---

## 📊 Post-Deployment Testing

### Test Checklist

- [ ] App loads without errors
- [ ] Login page displays correctly
- [ ] All 4 user roles can login
- [ ] Data loads from BigQuery
- [ ] Charts render properly
- [ ] Navigation works between pages
- [ ] Export functions work
- [ ] Mobile responsive design works

### Demo User Testing

```
Admin Dashboard:
✅ Login: admin@mind.edu / mind2024
✅ Verify system health metrics
✅ Check user analytics
✅ View AI resource consumption

Developer Dashboard:
✅ Login: dev@mind.edu / mind2024
✅ Check API performance
✅ View AI model distribution
✅ Test trace lookup

Faculty Dashboard:
✅ Login: faculty@mind.edu / mind2024
✅ View student performance
✅ Check at-risk students
✅ Export data to CSV

Student Dashboard:
✅ Login: student@mind.edu / mind2024
✅ View personal performance
✅ Check conversation history
✅ View achievements
```

---

## 🐛 Troubleshooting

### Common Issues & Solutions

#### 1. "Failed to initialize BigQuery client"
**Solution:**
- Verify secrets are correctly formatted in Streamlit Cloud
- Check service account permissions
- Ensure project_id matches your BigQuery project

#### 2. "No data available"
**Solution:**
- Verify dataset name: `mind_analytics`
- Check table names match schema
- Confirm service account has BigQuery Data Viewer role

#### 3. App is slow
**Solution:**
- Increase cache TTL in queries
- Use date range filters
- Optimize SQL queries
- Check BigQuery quotas

#### 4. Authentication fails
**Solution:**
- Clear browser cache
- Check password spelling
- Verify user exists in `config/auth.py`

---

## 📈 Monitoring & Maintenance

### Daily Checks
- [ ] App is accessible
- [ ] Login works
- [ ] Data loads correctly

### Weekly Maintenance
- [ ] Review error logs
- [ ] Check BigQuery costs
- [ ] Monitor user feedback

### Monthly Updates
- [ ] Update dependencies
- [ ] Review security settings
- [ ] Analyze usage patterns
- [ ] Optimize slow queries

---

## 🎉 Success Criteria

Your deployment is successful when:

✅ All 4 dashboards load without errors
✅ Authentication works for all roles
✅ Data displays correctly from BigQuery
✅ Charts and visualizations render
✅ Export functionality works
✅ Mobile responsive design functions
✅ App is accessible via public URL

---

## 📞 Support

If you encounter issues:

1. Check this guide first
2. Review README.md for detailed info
3. Check Streamlit Cloud logs
4. Review BigQuery query logs
5. Create GitHub issue if needed

---

## 🚀 Next Steps

After successful deployment:

1. **Customize Users**
   - Update demo credentials
   - Add real users to `config/auth.py`

2. **Configure Branding**
   - Update colors in `.streamlit/config.toml`
   - Add organization logo

3. **Optimize Performance**
   - Adjust cache settings
   - Fine-tune SQL queries
   - Set up monitoring

4. **Add Features**
   - Implement user management UI
   - Add more visualizations
   - Create custom reports

---

**Deployment Complete! 🎊**

Your MIND Platform is now live and ready to use!
