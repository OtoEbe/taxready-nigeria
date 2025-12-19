# 🚀 TaxReady Nigeria - Deployment Guide

## Option 1: Streamlit Cloud (FREE - Recommended)

This is the fastest way to get live. Takes 5 minutes.

### Prerequisites
- GitHub account (free at github.com)
- The taxready folder from the zip

### Step-by-Step

#### 1. Create GitHub Repository

Go to: https://github.com/new

Fill in:
- **Repository name:** `taxready-nigeria`
- **Description:** `Tax compliance platform for Nigeria Tax Act 2025`
- **Visibility:** Public (required for free Streamlit hosting)
- Click **Create repository**

#### 2. Upload Files to GitHub

**Option A: Using GitHub Web Interface (Easiest)**

1. On your new repo page, click **"uploading an existing file"**
2. Drag and drop ALL files from the `taxready` folder:
   - `app.py`
   - `requirements.txt`
   - `README.md`
   - `.gitignore`
   - `.streamlit/` folder (with config.toml inside)
   - `calculators/` folder (with __init__.py, paye.py, contractor.py)
   - `utils/` folder (with __init__.py, constants.py)
3. Add commit message: "Initial commit"
4. Click **Commit changes**

**Option B: Using Git Command Line**

```bash
# Navigate to the taxready folder
cd taxready

# Initialize git
git init
git add .
git commit -m "Initial commit - TaxReady Nigeria MVP"

# Add your GitHub repo as remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/taxready-nigeria.git
git branch -M main
git push -u origin main
```

#### 3. Deploy on Streamlit Cloud

1. Go to: https://share.streamlit.io
2. Click **"New app"** (top right)
3. Sign in with GitHub if prompted
4. Fill in:
   - **Repository:** `YOUR_USERNAME/taxready-nigeria`
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. Click **Deploy!**

#### 4. Wait 2-3 Minutes

Streamlit will:
- Clone your repo
- Install dependencies
- Start your app

Your app will be live at:
```
https://taxready-nigeria.streamlit.app
```

Or similar URL based on your username.

---

## Option 2: Railway (Free tier, more control)

### Step-by-Step

1. Go to: https://railway.app
2. Sign up with GitHub
3. Click **New Project** → **Deploy from GitHub repo**
4. Select your `taxready-nigeria` repo
5. Railway auto-detects Streamlit
6. Add environment variable:
   - `PORT`: `8501`
7. Deploy

Your app will be at: `https://taxready-nigeria.up.railway.app`

---

## Option 3: Render (Free tier)

### Step-by-Step

1. Go to: https://render.com
2. Sign up with GitHub
3. Click **New** → **Web Service**
4. Connect your GitHub repo
5. Configure:
   - **Name:** `taxready-nigeria`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
6. Click **Create Web Service**

---

## Custom Domain (Optional)

Once deployed on Streamlit Cloud:

1. Go to your app's settings (⚙️ icon)
2. Click **General** → **Custom domain**
3. Enter your domain (e.g., `app.taxready.ng`)
4. Add CNAME record in your DNS:
   - **Type:** CNAME
   - **Name:** app (or www)
   - **Value:** `cname.streamlit.app`

---

## Post-Deployment Checklist

- [ ] Test all calculators with sample data
- [ ] Check mobile responsiveness
- [ ] Share link on social media
- [ ] Set up Google Analytics (optional)
- [ ] Monitor for errors in Streamlit Cloud dashboard

---

## Troubleshooting

**App not loading?**
- Check if all files uploaded correctly
- Verify `requirements.txt` is in root folder
- Check Streamlit Cloud logs for errors

**Import errors?**
- Ensure `__init__.py` files exist in `calculators/` and `utils/`
- Check file paths match exactly

**Styling looks wrong?**
- Clear browser cache
- Verify `.streamlit/config.toml` uploaded

---

## Need Help?

- Streamlit Docs: https://docs.streamlit.io
- Streamlit Community: https://discuss.streamlit.io
- GitHub Issues: Create issue in your repo

---

**Congratulations! Your app is now live! 🎉**
