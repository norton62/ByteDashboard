# Deployment Guide - ByteDashboard

## Quick Deploy to Streamlit Community Cloud (Recommended - FREE)

### Step 1: Prepare Your Repository

1. **Create a GitHub repository:**
   - Go to https://github.com/new
   - Name it "ByteDashboard" (or any name you prefer)
   - Make it **Private** to keep your data secure
   - Don't initialize with README (we have files already)

2. **Push your code to GitHub:**
   ```bash
   cd Z:\Github\ByteDashboard
   git init
   git add .
   git commit -m "Initial commit - Dashboard with authentication"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/ByteDashboard.git
   git push -u origin main
   ```

### Step 2: Deploy to Streamlit Community Cloud

1. **Go to Streamlit Community Cloud:**
   - Visit https://streamlit.io/cloud
   - Click "Sign in" and use your GitHub account

2. **Deploy your app:**
   - Click "New app"
   - Select your repository: `YOUR_USERNAME/ByteDashboard`
   - Main file path: `app.py`
   - Click "Deploy"

### Step 3: Configure Secrets (Password & API Key)

1. **In Streamlit Cloud dashboard:**
   - Click on your deployed app
   - Go to Settings (⚙️) → Secrets

2. **Add these secrets:**
   ```toml
   # Your dashboard password
   DASHBOARD_PASSWORD = "your_secure_password_here"

   # Your Companies House API key
   COMPANIES_HOUSE_API_KEY = "your_api_key_here"
   ```

3. **Save** and your app will restart with the secrets

### Step 4: Upload Your Database

**Option A: Include in Git (if data is not sensitive)**
- The `client_data.db` and `clients.xlsx` are already in your repo
- They'll be deployed automatically

**Option B: Upload Fresh Data After Deployment**
- Go to your deployed app
- Navigate to the main page
- Use the "📤 Re-Import" button to import from Excel

### Your App is Live! 🎉

Your dashboard will be accessible at:
```
https://YOUR_APP_NAME.streamlit.app
```

---

## Security Notes

✅ **Password Protection**: Users must enter password to access
✅ **Private Repository**: Code is not publicly visible
✅ **Secrets Management**: API keys stored securely in Streamlit Cloud
✅ **HTTPS**: All traffic encrypted

### Default Password

The default password is `admin123` - **CHANGE THIS IMMEDIATELY** in Streamlit Cloud secrets!

### Changing Password

1. Go to your app settings in Streamlit Cloud
2. Edit Secrets
3. Change `DASHBOARD_PASSWORD` to your new password
4. Save (app will restart)

---

## Alternative Deployment Options

### Option 2: Deploy to Heroku

1. **Install Heroku CLI:**
   ```bash
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Create these files:**

   `Procfile`:
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

   `runtime.txt`:
   ```
   python-3.10.12
   ```

3. **Deploy:**
   ```bash
   heroku login
   heroku create your-dashboard-name
   heroku config:set DASHBOARD_PASSWORD=your_password
   heroku config:set COMPANIES_HOUSE_API_KEY=your_api_key
   git push heroku main
   ```

### Option 3: Self-Host on VPS (AWS/DigitalOcean/etc.)

1. **SSH into your server**
2. **Install dependencies:**
   ```bash
   sudo apt update
   sudo apt install python3-pip
   pip3 install -r requirements.txt
   ```

3. **Set environment variables:**
   ```bash
   export DASHBOARD_PASSWORD=your_password
   export COMPANIES_HOUSE_API_KEY=your_api_key
   ```

4. **Run with systemd or screen:**
   ```bash
   streamlit run app.py --server.port 8501
   ```

5. **Set up reverse proxy with nginx for HTTPS**

---

## Troubleshooting

### "Module not found" errors
- Check `requirements.txt` includes all dependencies
- Redeploy the app

### Database not found
- Make sure `client_data.db` is in the repository
- Or use "Re-Import" to create it from Excel

### Password not working
- Check Streamlit Cloud Secrets are saved correctly
- Password is case-sensitive

### API not working
- Verify `COMPANIES_HOUSE_API_KEY` is in Secrets
- Check the key is still valid at Companies House Developer Hub

---

## Monitoring & Maintenance

### View Logs
- Streamlit Cloud: Click on your app → View logs
- Heroku: `heroku logs --tail`

### Update the App
1. Make changes locally
2. Commit: `git add . && git commit -m "Update"`
3. Push: `git push`
4. Streamlit Cloud auto-deploys from GitHub

### Backup Database
- Download `client_data.db` periodically
- Export to Excel using the "📥 Export Excel" button

---

## Cost

- **Streamlit Community Cloud**: FREE (1 private app)
- **Heroku**: $7/month (Eco Dynos)
- **VPS**: $5-10/month (DigitalOcean, AWS Lightsail)

**Recommended**: Start with Streamlit Community Cloud (free)

---

Need help? Check:
- Streamlit docs: https://docs.streamlit.io/streamlit-community-cloud
- This project's issues: GitHub Issues tab
