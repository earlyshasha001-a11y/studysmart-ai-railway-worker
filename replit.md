# StudySmart AI - Railway Automation Controller

## Overview
This project is an automation controller that connects Replit to Railway for managing lesson generation worker containers. Built with Python, it uses the Railway GraphQL API to programmatically create and manage infrastructure.

## Purpose
- Connect Replit to Railway platform using project token
- Monitor and manage Railway project "luminous-expression"
- Manage lesson generation worker containers
- Future: Add AI lesson directives and curriculum JSON files

## Recent Changes
- **2025-11-04**: Successfully connected to Railway
  - Implemented Railway GraphQL API integration using requests library
  - Added support for both account tokens and project-specific tokens
  - Successfully connected to Railway project: luminous-expression
  - Project ID: cedc37d7-79dd-48f2-b880-6333d9d3760c
  - Production environment configured

## Project Architecture

### Main Components
- `railway_controller.py`: Main automation controller
  - RailwayController class for API management
  - GraphQL queries for project/service creation
  - Connection testing and verification
  - Automated deployment workflow

### Dependencies
- Python 3.11
- requests library (HTTP client)

### Configuration
- Uses Railway project token authentication
- Required Secrets:
  - `RAILWAY_PROJECT_TOKEN`: Project-specific access token
  - `RAILWAY_PROJECT_ID`: cedc37d7-79dd-48f2-b880-6333d9d3760c
- Railway GraphQL API v2 endpoint
- Simple CLI interface, no web frameworks

## User Preferences
- User prefers simple solutions without frameworks
- Direct API integration using requests library only
- No technical questions - autonomous execution
- Clear status output and confirmation messages

## Current Status
✅ Railway API connection established
✅ Project authentication working
✅ Production environment detected

## Next Steps
1. Add StudySmart AI lesson directives
2. Upload curriculum JSON files
3. Create and configure worker services on Railway
4. Set up deployment automation
