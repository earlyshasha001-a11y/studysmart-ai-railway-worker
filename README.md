# StudySmart AI - Railway Worker

## Overview
This is the Railway worker service for StudySmart AI lesson generation using DeepSeek V3.1.

## Deployment to Railway

### Prerequisites
- Railway account: https://railway.app
- OpenRouter API key for DeepSeek V3.1 access

### Quick Deploy

#### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit - StudySmart AI Railway Worker"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

#### 2. Deploy on Railway
1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose this repository
5. Railway will auto-detect `railway.json` and deploy

#### 3. Set Environment Variables
In Railway project settings, add:
```
OPENROUTER_API_KEY=sk-or-v1-...
PORT=5000
WORKER_MODE=http
```

#### 4. Get Your Worker URL
After deployment, copy your Railway service URL (e.g., `https://your-worker.railway.app`)

### Files Included

**Railway Worker:**
- `railway_worker.py` - Main HTTP server and lesson generation logic
- `railway.json` - Railway deployment configuration
- `Procfile` - Process definition
- `requirements.txt` - Python dependencies

**Curriculum Data:**
- `curriculum/MASTER_DIRECTIVE_v7.2.json` - Lesson generation rules
- `curriculum/*.json` - 54 lesson mapping files (6,180 lessons total)
- `curriculum/directives/` - Curriculum-specific directives (optional)

### API Endpoints

Once deployed, the worker exposes:

**POST /start** - Start batch processing
```json
{
  "max_mappings": 54,
  "max_lessons_per_mapping": 100
}
```

**GET /status** - Get current status
```json
{
  "status": "processing",
  "lessons_generated": 42,
  "lessons_failed": 3,
  "runtime": 1234.5
}
```

**GET /summary** - Get detailed summary
```json
{
  "status": "completed",
  "lessons_generated": 100,
  "lessons_failed": 5,
  "runtime": 3600.2,
  "batch_results": [...]
}
```

### Testing

After deployment, test the worker:
```bash
# Test connection
curl https://your-worker.railway.app/status

# Start small test batch
curl -X POST https://your-worker.railway.app/start \
  -H "Content-Type: application/json" \
  -d '{"max_mappings": 1, "max_lessons_per_mapping": 10}'

# Check progress
curl https://your-worker.railway.app/status
```

### Architecture

This worker is designed to run on Railway and handle all heavy computation:
- Loads curriculum files from repository
- Generates lessons using DeepSeek V3.1 via OpenRouter
- Validates character counts (1600-1950 per part)
- Saves output to Railway storage (`/tmp/output/`)
- Reports progress via REST API

### Controlling from Replit

Use the Replit controller to trigger and monitor jobs:
```bash
# In Replit, set environment variable:
RAILWAY_WORKER_URL=https://your-worker.railway.app

# Run controller:
python replit_controller.py test    # Test mode (1 mapping, 10 lessons)
python replit_controller.py         # Full run (54 mappings, 100 lessons each)
```

### Resource Usage

- CPU: Monitored automatically, pauses if > 85%
- Memory: Tracked with psutil
- Rate Limiting: 4-second delay between API calls
- Retry Logic: 3 attempts per lesson
- Auto-shutdown: Worker completes batch and reports status

### Support

For issues or questions about deployment, check Railway logs:
```
railway logs
```

Or visit the Railway dashboard for real-time monitoring.
