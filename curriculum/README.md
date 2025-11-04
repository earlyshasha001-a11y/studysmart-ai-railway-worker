# StudySmart AI Curriculum Files

This directory contains the directives and lesson mappings for StudySmart AI lesson generation.

## Required Files

### 1. Master Directive
Upload your master directive file here:
- **Example**: `MASTER_DIRECTIVE_v7.2.json`
- Contains the core instructions for DeepSeek V3.1 on how to generate StudySmart lessons

### 2. Lesson Mappings
Upload your lesson mapping JSONs here:
- **Example**: `Cambridge_Year10_Math_mapping.json`
- Each file contains the lesson structure for a specific curriculum/subject

## File Format

Your lesson mapping JSON should follow this structure:
```json
{
  "curriculum": "Cambridge IGCSE",
  "subject": "Mathematics",
  "year": "Year 10",
  "lessons": [
    {
      "lesson_id": "L001",
      "title": "Introduction to Algebra",
      "topics": ["Variables", "Expressions", "Equations"]
    }
  ]
}
```

## Upload Instructions

1. Place your `MASTER_DIRECTIVE_v*.json` file in this directory
2. Place your lesson mapping JSONs (e.g., `Cambridge_Year10_Math_mapping.json`) in this directory
3. Run the controller - it will automatically detect and use these files

## Notes

- The controller will scan this directory for JSON files
- Master directive takes precedence (should have "MASTER_DIRECTIVE" in filename)
- Multiple mapping files can be processed in batches
