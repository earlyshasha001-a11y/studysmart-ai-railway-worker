# StudySmart AI - DeepSeek V3.1 Orchestration Controller

## Overview
This project is a **lightweight orchestration controller** on Replit that manages StudySmart AI lesson generation. Heavy computation (DeepSeek V3.1 processing) runs on Railway workers, while Replit acts only as a controller for triggering, monitoring, and receiving results.

## Architecture
- **Replit**: Lightweight controller (API triggers, logging, monitoring)
- **Railway**: Heavy executor (DeepSeek V3.1 generation, validation, file saving)

## AI Model
- **DeepSeek V3.1** (via OpenRouter API)
- Enhanced with system message and aggressive length directives
- Temperature increased to 0.8 for more expansive content
- Word count guidance (250-300 words = 1600-1950 characters)

## Purpose
- Deploy Railway workers for batch lesson generation
- Monitor worker status and resource usage
- Receive completion summaries and logs
- Keep Replit storage under 200 MB
- Auto-shutdown Railway workers after completion

## Recent Changes
- **2025-11-04**: StudySmart AI Orchestration System - PROMPT OPTIMIZED
  - ✅ Added system message with strict length requirements
  - ✅ Enhanced prompt with word count guidance (250-300 words)
  - ✅ Increased temperature to 0.8 for more expansive responses
  - ✅ Added detailed writing instructions (expand, elaborate, don't abbreviate)
  - ✅ Railway HTTP API integration complete
  - ✅ DeepSeek V3.1 integration via OpenRouter
  - ✅ Curriculum file loading system (54 mapping files, 6,180 lessons)
  - ✅ **3-file output system per lesson** (Script.csv, Notes_Exercises.csv, Illustrations.json)
  - ✅ CSV single-row format with no line breaks (Master Directive v7.2 compliant)
  - ✅ Character count enforcement (1600-1950 per part) with retry logic (3 attempts)
  - ✅ Part count validation (4 parts lower primary, 8 parts upper/secondary)
  - ✅ Proper JSON illustration structure with arrays
  - ✅ **Two-tier directive system for maximum accuracy**:
    - Master Directive (general rules) + Curriculum-Specific Directives (per subject/grade)
    - Auto-reload both directives after each lesson from disk
  - ✅ Enhanced prompt with concrete 1650-character example
  - ✅ Automatic output management with date-stamped directories
  - ✅ Progress tracking and error handling
  - Connected to Railway project: luminous-expression (cedc37d7-79dd-48f2-b880-6333d9d3760c)

## Project Architecture

### Main Components
- `replit_controller.py`: Lightweight Replit controller
  - **ReplitController**: Railway worker deployment & monitoring
  - GraphQL API calls for worker management
  - Status polling and progress tracking
  - Summary retrieval from Railway workers
  
- `railway_worker.py`: Heavy Railway worker (runs on Railway)
  - **StudySmartWorker**: DeepSeek V3.1 lesson generation
  - Curriculum file loading and validation
  - Batch processing with retry logic
  - Resource monitoring (CPU/Memory)
  - Auto-shutdown after completion
  
- `curriculum/`: Directory for curriculum files
  - Master directive JSON (MASTER_DIRECTIVE_v*.json) - general lesson generation rules
  - Lesson mapping JSONs (54 files covering all curricula)
  - `directives/`: Curriculum-specific directive files (optional, one per mapping)
    - When present, provides subject-specific guidance for more accurate generation
    - Falls back to Master Directive if curriculum-specific file not found
  - README with upload instructions
  
- `output/`: Generated lesson files (3 per lesson)
  - Organized by date (YYYY-MM-DD) and curriculum mapping
  - Each lesson generates 3 files:
    - `{LessonID}_Script.csv` - Single-row CSV with script parts (no line breaks)
    - `{LessonID}_Notes_Exercises.csv` - Single-row CSV with notes/exercises (no line breaks)
    - `{LessonID}_Illustrations.json` - JSON with illustration specifications

### Dependencies
- Python 3.11
- requests library (HTTP client)

### Configuration

**Required Secrets:**
- `OPENROUTER_API_KEY`: OpenRouter API key for DeepSeek V3.1 access (Railway only)
- `RAILWAY_WORKER_URL`: Railway worker HTTP endpoint (Replit only)
  - Example: `https://your-worker.railway.app`
  - Set after deploying worker to Railway

**Optional Secrets (for future features):**
- `SUPABASE_URL`: Supabase project URL (for storing lesson JSONs)
- `SUPABASE_KEY`: Supabase API key
- `CLOUDFLARE_R2_KEY`: Cloudflare R2 key (for audio/video assets)

**API Endpoints:**
- Railway GraphQL: https://backboard.railway.com/graphql/v2
- OpenRouter: https://openrouter.ai/api/v1/chat/completions
- Model: deepseek/deepseek-chat

## User Preferences
- User prefers simple solutions without frameworks
- Direct API integration using requests library only
- No technical questions - autonomous execution
- Clear status output and confirmation messages

## Current Status
✅ Railway API connection established  
✅ OpenRouter API integration complete  
✅ DeepSeek V3.1 lesson generation **RUNNING**  
✅ Curriculum loading system operational  
✅ Output management configured  
✅ **ALL 6,182 LESSONS** loaded and processing

**System is now actively generating lessons!** 🚀

### Curriculum Files Loaded (54 files)
- ✅ MASTER_DIRECTIVE_v7.2.json
- ✅ 54 lesson mapping JSON files covering:
  - Cambridge Curriculum (Years 1-11)
  - CBC Curriculum (Grades 1-12)
  - 8-4-4 Curriculum (Form 3-4)

### Subjects Covered
- Mathematics, English, Science (all levels)
- Agriculture & Nutrition, Geography, History
- Physics, Chemistry, Biology
- Business Studies, Economics, ICT
- Literature, Digital Literacy
- Social Studies (all grades)

## How It Works

### 1. Curriculum Files (✅ Complete)
All curriculum files are in the `curriculum/` directory:
- `MASTER_DIRECTIVE_v7.2.json` - Complete lesson generation guidelines
- 54 lesson mapping JSON files with 6,182 total lessons

### 2. Lesson Generation (🔄 In Progress)
The controller is currently running and:
- Loading curriculum files from `curriculum/`
- Connecting to Railway project "luminous-expression"
- Generating lessons using DeepSeek V3.1 via OpenRouter
- Processing in batches of 100 lessons
- Saving output to `output/2025-11-04/`

### 3. Monitor Progress
Check the workflow console to see:
- Real-time progress for each lesson being generated
- Batch processing status (100 lessons per batch)
- Success/failure counts
- Output file locations

### 4. Review Generated Lessons
Generated lessons are saved to `output/YYYY-MM-DD/{curriculum_mapping}/`:
- **3 files per lesson** (Master Directive v7.2 format):
  - `{LessonID}_Script.csv` - Script narration in single-row CSV format
  - `{LessonID}_Notes_Exercises.csv` - Notes & exercises in single-row CSV format
  - `{LessonID}_Illustrations.json` - Illustration specifications with proper array structure
- Character counts enforced: 1600-1950 per part
- Retry logic (3 attempts) ensures quality
- Failed lessons are skipped and logged

## Generated Lesson Specifications

Each lesson follows Master Directive v7.2:
- **Lower Primary** (Years 1-6, Grades 1-6): 4 parts, 6,400-7,800 characters
- **Upper/Secondary** (Years 7-11, Grades 7-12, Form 3-4): 8 parts, 12,800-15,600 characters
- Teacher rotation (unique AI teacher per grade/year/form)
- C.R.A. methodology (Concrete → Representational → Abstract)
- Illustration requirements (≥1 per part, 6-10 total)
- OCR-friendly notes and exercises
- British grammar with Kenyan/African context

## Next Steps
1. ✅ Curriculum files uploaded and loaded
2. ✅ Controller running and generating lessons
3. 🔄 Monitor lesson generation progress
4. Future: Add Supabase storage integration for generated lessons
5. Future: Scale to Railway worker deployment for massive batches
6. Future: Add Cloudflare R2 for audio/video assets
