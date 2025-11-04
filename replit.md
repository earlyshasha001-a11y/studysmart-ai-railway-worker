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
- **2025-11-04**: StudySmart AI Orchestration System Implemented
  - ✅ Railway GraphQL API integration complete
  - ✅ DeepSeek V3.1 integration via OpenRouter
  - ✅ Curriculum file loading system (directive + mappings)
  - ✅ Batch lesson generation workflow
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
  
- `output/`: Generated lesson scripts
  - Organized by date (YYYY-MM-DD)
  - Each lesson saved as JSON with metadata

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
✅ DeepSeek V3.1 lesson generation ready  
✅ Curriculum loading system operational  
✅ Output management configured  

## How to Use

### 1. Upload Curriculum Files
Place these files in the `curriculum/` directory:
- `MASTER_DIRECTIVE_v7.2.json` (or similar) - Your master directive
- `Cambridge_Year10_Math_mapping.json` (example) - Your lesson mappings

### 2. Run the Controller
The controller runs automatically via the "StudySmart AI Controller" workflow.
It will:
- Load curriculum files
- Connect to Railway (verify access)
- Generate lessons using DeepSeek V3.1 via OpenRouter
- Save output to `output/YYYY-MM-DD/`

### 3. Monitor Progress
The console shows:
- Real-time progress for each lesson
- Success/failure counts
- Output file locations

### 4. Review Generated Lessons
Check `output/YYYY-MM-DD/` for:
- Individual lesson JSON files
- Each contains: lesson data, generated script, metadata

## Next Steps
1. ✅ Upload your MASTER_DIRECTIVE JSON to curriculum/
2. ✅ Upload your lesson mapping JSON(s) to curriculum/
3. ✅ Run the controller and watch lessons generate
4. Future: Add Supabase storage integration
5. Future: Add Railway worker deployment for heavy batches
6. Future: Add Cloudflare R2 for audio/video assets
