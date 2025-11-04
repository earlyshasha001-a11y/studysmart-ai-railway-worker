# StudySmart AI - DeepSeek V3.1 Orchestration Controller

## Overview
This project is a lightweight orchestration controller that manages StudySmart AI lesson generation using DeepSeek V3.1 via OpenRouter. It connects to Railway for future heavy workload deployment, while keeping Replit as the control hub.

## Purpose
- Generate StudySmart AI lesson scripts using DeepSeek V3.1 (via OpenRouter)
- Process curriculum directives and lesson mappings
- Batch generate lessons with progress tracking
- Connect to Railway project "luminous-expression" for future deployment
- Save generated lesson JSONs to output directory

## Recent Changes
- **2025-11-04**: StudySmart AI Orchestration System - PRODUCTION READY
  - ✅ Railway GraphQL API integration complete
  - ✅ DeepSeek V3.1 integration via OpenRouter
  - ✅ Curriculum file loading system (54 mapping files, 6,180 lessons)
  - ✅ **3-file output system per lesson** (Script.csv, Notes_Exercises.csv, Illustrations.json)
  - ✅ CSV single-row format with no line breaks (Master Directive v7.2 compliant)
  - ✅ Character count enforcement (1600-1950 per part) with retry logic (3 attempts)
  - ✅ Part count validation (4 parts lower primary, 8 parts upper/secondary)
  - ✅ Proper JSON illustration structure with arrays
  - ✅ Automatic output management with date-stamped directories
  - ✅ Progress tracking and error handling
  - Connected to Railway project: luminous-expression (cedc37d7-79dd-48f2-b880-6333d9d3760c)

## Project Architecture

### Main Components
- `railway_controller.py`: Main orchestration controller
  - **RailwayController**: Railway API management & GraphQL operations
  - **StudySmartOrchestrator**: DeepSeek V3.1 lesson generation
  - Curriculum file loading (directives + mappings)
  - Batch processing with progress tracking
  - Automatic output management
  
- `curriculum/`: Directory for curriculum files
  - Master directive JSON (MASTER_DIRECTIVE_v*.json)
  - Lesson mapping JSONs
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
- `OPENROUTER_API_KEY`: OpenRouter API key for DeepSeek V3.1 access
- `RAILWAY_PROJECT_TOKEN`: Railway project token
- `RAILWAY_PROJECT_ID`: cedc37d7-79dd-48f2-b880-6333d9d3760c

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
