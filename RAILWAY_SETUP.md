# Railway Worker Setup Instructions

## Overview
This guide helps you deploy the StudySmart AI worker to Railway for heavy DeepSeek V3.1 lesson generation.

## Architecture
- **Replit**: Lightweight controller (triggers, monitors, logs)
- **Railway**: Heavy executor (DeepSeek generation, validation, saving)

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
    "restartPolicyMaxRetries": 2
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

### 3. Worker Behavior

When deployed, the Railway worker will:

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

5. **Auto-Shutdown**
   - Completes all lessons in batch (max 100 per mapping)
   - Saves summary JSON
   - Exits (Railway service stops)

### 4. Replit Controller Usage

From Replit, run:
```bash
python replit_controller.py
```

The controller will:
1. ✅ Test Railway API connection
2. 🚀 Trigger Railway deployment
3. ⏳ Poll worker status every 30 seconds
4. 📊 Retrieve completion summary
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

#### Deployment Fails
```
✗ Deployment failed: Railway API error (400)
```
**Solution**: 
- Verify RAILWAY_PROJECT_TOKEN is correct
- Check Railway project ID
- Ensure Railway project has proper permissions

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
└──────────┬──────────┘
           │
           │ 1. Deploy Worker
           │ 2. Poll Status
           │ 3. Receive Summary
           ▼
┌─────────────────────┐
│   Railway Worker    │
│  (Heavy Executor)   │
│                     │
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
│ │  Auto-Shutdown  │ │
│ └─────────────────┘ │
└─────────────────────┘
```

## Next Steps

1. ✅ Complete Railway project setup (Steps 1-2)
2. ✅ Upload curriculum files to Railway
3. ✅ Verify environment variables
4. 🚀 Run `python replit_controller.py` from Replit
5. 📊 Monitor progress in Railway dashboard
6. ✓ Review generated lessons in output directory
