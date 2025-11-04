# Railway Worker Setup Instructions

## Overview
This guide helps you deploy the StudySmart AI worker to Railway for heavy DeepSeek V3.1 lesson generation.

## Architecture (HTTP-Based Communication)
- **Replit**: Lightweight controller
  - Sends HTTP requests to Railway worker
  - Monitors progress via REST API (/status endpoint)
  - Receives final summary via /summary endpoint
  
- **Railway**: Heavy executor
  - Runs HTTP server on port 5000
  - Exposes REST API for job control
  - Handles all DeepSeek V3.1 generation
  - Validates and saves lesson files

## Prerequisites
- Railway account: https://railway.app
- Railway project "luminous-expression" (ID: cedc37d7-79dd-48f2-b880-6333d9d3760c)
- `RAILWAY_PROJECT_TOKEN` secret in Replit
- `OPENROUTER_API_KEY` secret in both Replit and Railway

## Setup Steps

### 1. Railway Project Setup

#### A. Connect Repository to Railway
1. Go to https://railway.app/project/cedc37d7-79dd-48f2-b880-6333d9d3760c
2. Click "New Service"
3. Select "GitHub Repo" or "Empty Service"
4. If using GitHub:
   - Connect this repository
   - Railway will auto-detect `railway.json` configuration
5. If using Empty Service:
   - You'll need to manually upload files

#### B. Configure Environment Variables in Railway
1. In Railway project settings, add these variables:
   ```
   OPENROUTER_API_KEY=<your_openrouter_key>
   ```

#### C. Upload Curriculum Files to Railway
The worker needs access to curriculum files. Options:

**Option 1: Use Railway Volumes**
1. Create a volume in Railway
2. Upload curriculum files to `/curriculum`
3. Mount volume to service

**Option 2: Include in Repository**
- Commit curriculum files to your repository
- Railway will clone them automatically

**Option 3: Download at Runtime**
- Modify `railway_worker.py` to download curriculum from Replit or external storage

### 2. Railway Deployment Configuration

The project includes these Railway configuration files:

#### `railway.json`
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python railway_worker.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 2,
    "numReplicas": 1,
    "healthcheckPath": "/status",
    "healthcheckTimeout": 300
  }
}
```

#### `Procfile`
```
worker: python railway_worker.py
```

#### `requirements.txt`
```
requests==2.31.0
psutil==5.9.8
```

#### Environment Variables (Railway)
```
OPENROUTER_API_KEY=<your_key>
PORT=5000
WORKER_MODE=http
```

### 3. Worker Behavior

The Railway worker runs as an HTTP server and provides these endpoints:

#### REST API Endpoints

**POST /start** - Start batch processing
```json
{
  "max_mappings": 54,
  "max_lessons_per_mapping": 100
}
```
Response: `{"message": "Batch job started", "status": "processing"}`

**GET /status** - Get current status
Response:
```json
{
  "status": "processing",
  "lessons_generated": 42,
  "lessons_failed": 3,
  "runtime": 1234.5
}
```

**GET /summary** - Get detailed summary
Response:
```json
{
  "status": "completed",
  "lessons_generated": 100,
  "lessons_failed": 5,
  "runtime": 3600.2,
  "batch_results": [...]
}
```

#### Processing Behavior

1. **Load Curriculum Files**
   - Master Directive (MASTER_DIRECTIVE_v7.2.json)
   - 54 lesson mapping JSON files

2. **Process Lessons**
   - Generate lessons using DeepSeek V3.1 via OpenRouter
   - Validate character counts (1600-1950 per part)
   - Save to `/tmp/output/YYYY-MM-DD/`

3. **Monitor Resources**
   - Log CPU and memory usage every 10 lessons
   - Pause if CPU > 85% for > 1 minute

4. **Rate Limiting**
   - 4-second delay between API calls
   - 60-second backoff on 429 (rate limit) errors
   - 3 retry attempts per lesson

### 4. Replit Controller Usage

#### Set Environment Variable
After deploying the Railway worker, set the worker URL in Replit:
```bash
RAILWAY_WORKER_URL=https://your-worker.railway.app
```

#### Run Controller
From Replit, run:
```bash
python replit_controller.py [max_mappings] [max_lessons_per_mapping]
```

Examples:
```bash
python replit_controller.py                  # Process all 54 mappings, 100 lessons each
python replit_controller.py 5 50            # Process 5 mappings, 50 lessons each
python replit_controller.py 1 10            # Test: 1 mapping, 10 lessons
```

The controller will:
1. ✅ Test Railway worker connection (HTTP GET /status)
2. 🚀 Start batch job (HTTP POST /start)
3. ⏳ Monitor progress every 30 seconds (HTTP GET /status)
4. 📊 Retrieve completion summary (HTTP GET /summary)
5. ✓ Display results

### 5. Monitoring Progress

#### Railway Dashboard
View real-time logs at:
```
https://railway.app/project/cedc37d7-79dd-48f2-b880-6333d9d3760c
```

Look for:
- `[X/100] Generating lesson: LX` - Current lesson being processed
- `✓ Validation passed` - Successful generation
- `✗ Failed to generate` - Failed attempts
- `Resources: CPU=X%, Memory=Y%` - Resource usage

#### Replit Controller
The Replit controller logs:
- Connection status
- Deployment triggers
- Worker status polls (every 30 seconds)
- Final summary

### 6. Output Files

Lessons are saved to Railway storage at:
```
/tmp/output/YYYY-MM-DD/{curriculum_mapping}/
```

Each lesson generates:
- `L{X}_complete.json` - Complete lesson data including:
  - Script parts (4 or 8 parts depending on grade level)
  - Notes & Exercises (single comprehensive section)
  - Illustrations (6-10 per lesson)
  - Metadata and generation timestamp

### 7. Troubleshooting

#### Cannot Connect to Worker
```
✗ RAILWAY_WORKER_URL not configured
```
**Solution**: 
- Deploy worker to Railway first
- Copy the Railway service URL (e.g., `https://your-worker.railway.app`)
- Set `RAILWAY_WORKER_URL` environment variable in Replit

#### Worker Can't Find Curriculum Files
```
✗ No lesson mappings found!
```
**Solution**:
- Upload curriculum files to Railway (see Step 1C)
- Verify curriculum directory structure:
  ```
  curriculum/
  ├── MASTER_DIRECTIVE_v7.2.json
  ├── directives/
  │   └── README.md
  └── [54 lesson mapping files]
  ```

#### Rate Limit Errors (429)
```
⚠️  Rate limit hit - waiting 60 seconds...
```
**Solution**:
- This is expected behavior - worker will retry
- If persistent, reduce batch size in `railway_worker.py`

#### High CPU Usage
```
⚠️  High CPU usage detected - pausing briefly...
```
**Solution**:
- Worker automatically pauses for 30 seconds
- If persistent, upgrade Railway plan for more resources

### 8. Scaling Considerations

#### Current Limits
- Max lessons per mapping: 100
- Max runtime per worker: 2 hours (7200 seconds)
- Rate limit buffer: 4-second delay between calls

#### To Process More Lessons
1. Increase `max_lessons` in `railway_worker.py`
2. Adjust `max_runtime` for longer batches
3. Deploy multiple workers for parallel processing

#### Cost Optimization
- Workers auto-shutdown after completion
- No idle resource charges
- Replit stays lightweight (< 200 MB storage)

## System Flow

```
┌─────────────────────┐
│   Replit Controller │
│  (Lightweight Hub)  │
│                     │
│  HTTP Client        │
└──────────┬──────────┘
           │
           │ POST /start (trigger batch)
           │ GET /status (poll progress)
           │ GET /summary (final results)
           ▼
┌─────────────────────┐
│   Railway Worker    │
│  (Heavy Executor)   │
│                     │
│  HTTP Server :5000  │
│                     │
│ ┌─────────────────┐ │
│ │ REST API        │ │
│ │ /start /status  │ │
│ │ /summary        │ │
│ └─────────────────┘ │
│         │           │
│         ▼           │
│ ┌─────────────────┐ │
│ │ Load Curriculum │ │
│ └─────────────────┘ │
│         │           │
│         ▼           │
│ ┌─────────────────┐ │
│ │ DeepSeek V3.1   │ │
│ │   Generation    │ │
│ └─────────────────┘ │
│         │           │
│         ▼           │
│ ┌─────────────────┐ │
│ │  Validate &     │ │
│ │  Save Lessons   │ │
│ └─────────────────┘ │
│         │           │
│         ▼           │
│ ┌─────────────────┐ │
│ │  Return Status  │ │
│ └─────────────────┘ │
└─────────────────────┘
```

## Quick Start

### Step 1: Deploy to Railway
1. Push this code to GitHub repository
2. In Railway, create new service from GitHub repo
3. Railway will auto-detect `railway.json` and deploy
4. Set environment variable: `OPENROUTER_API_KEY`
5. Upload curriculum files to service (via volume or include in repo)
6. Copy the Railway service URL (e.g., `https://your-worker.railway.app`)

### Step 2: Configure Replit
1. In Replit, set environment variable:
   ```
   RAILWAY_WORKER_URL=https://your-worker.railway.app
   ```

### Step 3: Run Controller
```bash
python replit_controller.py
```

### Step 4: Monitor
- Watch Replit console for progress updates
- Check Railway logs for detailed DeepSeek generation logs
- Review generated lessons in Railway's `/tmp/output/` directory
