# 🚀 Deploy to Railway - Quick Guide

## Files Ready for Git Push

Your project is ready to deploy! Here are the files that will be pushed to GitHub and deployed to Railway:

### ✅ Core Railway Files
- `railway_worker.py` - Main worker service (HTTP server + DeepSeek generation)
- `railway.json` - Railway deployment configuration
- `Procfile` - Process definition for Railway
- `requirements.txt` - Python dependencies (requests, psutil)
- `README.md` - Deployment documentation

### ✅ Curriculum Files (55 total)
- `curriculum/MASTER_DIRECTIVE_v7.2.json` - Master lesson generation rules
- `curriculum/*.json` - 54 lesson mapping files (6,180 lessons)
- `curriculum/directives/` - Optional curriculum-specific directives

### ❌ Files NOT Included (Replit-only)
- `replit_controller.py` - Stays on Replit (controller)
- `replit.md` - Local documentation
- `RAILWAY_SETUP.md` - Local setup guide
- `output/` - Generated lessons (too large)
- `.replit`, `.config/`, temp files

---

## 📋 Deployment Steps

### Step 1: Push to GitHub

```bash
# Check what will be committed
git status

# Add all files
git add .

# Commit with message
git commit -m "Add StudySmart AI Railway Worker with curriculum files"

# Push to GitHub
git push origin main
```

If you don't have a GitHub repo yet:

```bash
# Create new repo on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

---

### Step 2: Deploy on Railway

1. **Go to Railway Dashboard**
   - Visit: https://railway.app
   - Click "New Project"

2. **Deploy from GitHub**
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway auto-detects `railway.json`

3. **Set Environment Variables**
   - Go to project → Variables
   - Add: `OPENROUTER_API_KEY` = `sk-or-v1-...` (your OpenRouter key)
   - Optional: `PORT=5000`, `WORKER_MODE=http`

4. **Get Your Worker URL**
   - After deployment completes
   - Copy the service URL (e.g., `https://your-worker.railway.app`)

---

### Step 3: Configure Replit

In this Replit, set the Railway worker URL:

```bash
# Add this secret in Replit:
RAILWAY_WORKER_URL=https://your-worker.railway.app
```

---

### Step 4: Test the System

Run the test from Replit:

```bash
python replit_controller.py test
```

Expected output:
```
🧪 Running in TEST MODE
✓ Connected to Railway worker
✓ Batch job started
Progress: 1 generated, 0 failed (2.3min)
Progress: 5 generated, 1 failed (8.7min)
Progress: 10 generated, 1 failed (15.2min)
✓ Worker completed successfully
```

---

## 🎯 Quick Commands

```bash
# Test mode (1 mapping, 10 lessons)
python replit_controller.py test

# Custom batch (5 mappings, 50 lessons each)
python replit_controller.py 5 50

# Full run (all 54 mappings, 100 lessons each = 5,400 lessons)
python replit_controller.py
```

---

## 📊 What Gets Deployed to Railway

**Size Check:**
- Curriculum files: ~1.5 MB
- Python code: ~50 KB
- Dependencies: ~10 MB (installed on Railway)
- **Total**: ~11.5 MB (well under Railway limits)

**Files Count:**
- 55 curriculum JSON files ✓
- 4 configuration files ✓
- 1 Python worker ✓
- 1 README ✓

---

## ✅ Verification Checklist

Before pushing to git:

- [ ] All 55 curriculum files in `curriculum/` directory
- [ ] `OPENROUTER_API_KEY` ready (for Railway environment)
- [ ] GitHub repository created
- [ ] Railway account ready

After deployment:

- [ ] Railway service deployed successfully
- [ ] Environment variables set in Railway
- [ ] Worker URL copied
- [ ] `RAILWAY_WORKER_URL` set in Replit
- [ ] Test mode runs successfully

---

## 🆘 Troubleshooting

**If Railway deployment fails:**
- Check Railway build logs
- Verify `railway.json` is present
- Ensure Python version is compatible (3.11+)

**If curriculum files are missing:**
- Verify all 55 files committed to git
- Check `.gitignore` doesn't exclude them
- Re-push to GitHub if needed

**If worker can't be reached:**
- Wait 2-3 minutes for Railway to fully deploy
- Check Railway service is "Active"
- Verify URL includes `https://`

---

## 🎉 You're Ready!

Your project structure is clean and ready for deployment. Just follow the steps above to push to GitHub and deploy to Railway!
