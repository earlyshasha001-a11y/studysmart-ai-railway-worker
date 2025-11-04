# StudySmart AI - Railway Automation Controller

## Overview
This project is an automation controller that connects Replit to Railway for managing lesson generation worker containers. Built with Python, it uses the Railway GraphQL API to programmatically create and manage infrastructure.

## Purpose
- Connect Replit to Railway platform using API key
- Automatically create Railway projects for StudySmart AI workers
- Manage lesson generation worker containers
- Future: Add AI lesson directives and curriculum JSON files

## Recent Changes
- **2025-11-04**: Initial project setup
  - Created Railway API automation controller
  - Implemented GraphQL API integration using requests library
  - Added project creation and service management capabilities
  - Set up simple CLI interface for deployment

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
- Requires `RAILWAY_API_KEY` in Replit Secrets
- Uses Railway GraphQL API v2 endpoint
- Simple CLI interface, no web frameworks

## User Preferences
- User prefers simple solutions without frameworks
- Direct API integration using requests library only
- No technical questions - autonomous execution
- Clear status output and confirmation messages

## Next Steps
1. User will add Railway API key to Secrets
2. User will add StudySmart AI lesson directives
3. User will upload curriculum JSON files
4. Configure worker deployment settings on Railway
