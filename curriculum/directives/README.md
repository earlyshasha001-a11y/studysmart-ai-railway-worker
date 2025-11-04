# Curriculum-Specific Directive Files

## Purpose
This directory contains optional curriculum-specific directive files that provide subject and grade-level specific guidance for lesson generation. When present, these directives are combined with the Master Directive to ensure maximum accuracy for each curriculum.

## How It Works

### Two-Tier Directive System
1. **Master Directive** (`MASTER_DIRECTIVE_v*.json` in parent folder)
   - Contains general lesson generation rules
   - Applies to ALL lessons across all curricula
   - Character count requirements, output format, C.R.A. methodology, etc.

2. **Curriculum-Specific Directives** (optional, in this `directives/` folder)
   - Named identically to their corresponding lesson mapping files
   - Example: `science_stages_7_9_Cambridge_mapping.json`
   - Contains subject-specific guidance, terminology, teaching approaches
   - If not present, system uses only the Master Directive

## File Structure

### Curriculum-Specific Directive Template
```json
{
  "curriculum_name": "Science - Cambridge Lower Secondary Stages 7-9",
  "subject": "Science",
  "grade_level": "Stages 7-9",
  "specific_guidance": {
    "key_terminology": [
      "Use 'learner' instead of 'student'",
      "Use British spelling (e.g., 'colour', 'metre')",
      "Refer to stages (7, 8, 9) not grades"
    ],
    "subject_specific_approaches": [
      "Emphasize scientific thinking and inquiry skills",
      "Include hands-on investigation descriptions",
      "Connect to Science in Context strand",
      "Reference safety procedures where applicable"
    ],
    "content_focus": [
      "Biology: Living organisms, cells, organ systems",
      "Chemistry: Atoms, elements, compounds, reactions",
      "Physics: Forces, energy, motion, electricity",
      "Earth and Space: Solar system, rocks, climate"
    ],
    "assessment_guidance": [
      "Align with Cambridge Lower Secondary Checkpoint",
      "Include formative assessment opportunities",
      "Provide clear success criteria"
    ]
  },
  "character_count_notes": "Remember: 1600-1950 characters per part (Master Directive requirement)"
}
```

## Creating Curriculum-Specific Directives

### Step 1: Identify the Curriculum
Find the corresponding lesson mapping file in the parent `curriculum/` directory.
Example: `Maths_grade_7_cbc_mapping.json`

### Step 2: Create Matching Directive File
Create a new JSON file in this `directives/` folder with the EXACT SAME NAME.
Example: `Maths_grade_7_cbc_mapping.json`

### Step 3: Add Subject-Specific Guidance
Include:
- Key terminology and vocabulary specific to this subject/grade
- Teaching approaches relevant to this curriculum framework
- Content focus areas from the official curriculum design
- Assessment methods and success criteria
- Cultural context (e.g., Kenyan examples for CBC curricula)

### Step 4: Reference Official Curriculum Documents
Use official curriculum frameworks as reference:
- CBC Curriculum Designs (Grades 1-12)
- Cambridge Lower Secondary Curriculum Frameworks (Stages 7-9)
- 8-4-4 Syllabus documents (Forms 3-4)

## Example: Mathematics Grade 7 CBC

```json
{
  "curriculum_name": "Mathematics - CBC Grade 7",
  "subject": "Mathematics",
  "grade_level": "Grade 7",
  "specific_guidance": {
    "key_terminology": [
      "Use CBC competency-based terminology",
      "Refer to 'learners' not 'students'",
      "Use Kenyan context for all examples"
    ],
    "subject_specific_approaches": [
      "Apply C.R.A. approach: Concrete → Representational → Abstract",
      "Include real-world Kenyan mathematical applications",
      "Emphasize problem-solving and critical thinking",
      "Connect to everyday situations (market, farming, construction)"
    ],
    "content_focus": [
      "Numbers: Integers, fractions, decimals, percentages",
      "Algebra: Patterns, simple equations, inequalities",
      "Geometry: 2D and 3D shapes, transformations",
      "Measurements: Length, area, volume, time, money",
      "Statistics: Data collection, representation, interpretation"
    ],
    "kenyan_context_examples": [
      "Use Kenyan currency (KES) for money problems",
      "Reference local markets, matatus, farming",
      "Include Kenyan geographical measurements",
      "Use local sports, games, and cultural activities"
    ]
  }
}
```

## Benefits of Curriculum-Specific Directives

✅ **Accuracy**: Subject-specific terminology and approaches
✅ **Relevance**: Contextually appropriate examples and scenarios
✅ **Alignment**: Matches official curriculum frameworks
✅ **Quality**: Higher quality lessons tailored to each subject
✅ **Flexibility**: Optional - falls back to Master Directive if not present

## When to Create Curriculum-Specific Directives

**High Priority** (Create these first):
- Core subjects with distinct approaches (Mathematics, Science, English)
- Curricula with unique frameworks (Cambridge vs CBC vs 8-4-4)
- Subjects requiring specialized terminology or context

**Medium Priority**:
- Subject-specific electives
- Advanced grade levels with complex content

**Lower Priority**:
- Subjects already well-covered by Master Directive
- Similar curricula that can share directives

## Notes

- Directive files are completely optional
- System automatically falls back to Master Directive if not found
- Can add directives incrementally over time
- Each directive is reloaded from disk after every lesson (ensures accuracy)
- Curriculum-specific directives do NOT override character count requirements
