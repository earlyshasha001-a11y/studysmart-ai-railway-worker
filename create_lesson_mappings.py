import json
import os
from collections import defaultdict

print("=" * 60)
print("  StudySmart AI - Lesson Mapping JSON Generator")
print("=" * 60)

# Read the extracted lessons file
input_file = "attached_assets/extracted lessons_1762275699072.txt"
output_dir = "curriculum"

print(f"📂 Reading lessons from: {input_file}")

with open(input_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Split by curriculum sections
sections = content.split('\n\n')

# Dictionary to hold lessons grouped by curriculum
curriculum_data = defaultdict(list)
current_curriculum = None
current_headers = []

lesson_count = 0
file_count = 0

for section in sections:
    lines = section.strip().split('\n')
    if not lines or not lines[0]:
        continue
    
    # Check if this is a header line (curriculum title)
    first_line = lines[0].strip()
    if 'lessons' in first_line.lower() and not first_line.startswith('Lesson Number'):
        # This is a curriculum header
        current_curriculum = first_line.replace(' lessons', '').strip()
        print(f"\n📚 Processing: {current_curriculum}")
        continue
    
    # Check if this is the column headers line
    if lines[0].startswith('Lesson Number|'):
        current_headers = lines[0].split('|')
        continue
    
    # Process lesson data
    if current_curriculum and current_headers:
        for line in lines:
            if not line.strip() or line.startswith('Lesson Number|'):
                continue
            
            parts = line.split('|')
            if len(parts) < 3:
                continue
            
            # Create lesson object based on headers
            lesson = {}
            for i, header in enumerate(current_headers):
                if i < len(parts):
                    lesson[header.strip()] = parts[i].strip()
            
            if lesson:
                curriculum_data[current_curriculum].append(lesson)
                lesson_count += 1

print(f"\n✅ Parsed {lesson_count} lessons from {len(curriculum_data)} curricula")

# Save each curriculum as a separate JSON file
for curriculum_name, lessons in curriculum_data.items():
    if not lessons:
        continue
    
    # Create a clean filename
    filename = curriculum_name.replace(' ', '_').replace('/', '_').replace('-', '_')
    filename = ''.join(c for c in filename if c.isalnum() or c == '_')
    filename = f"{filename}_mapping.json"
    filepath = os.path.join(output_dir, filename)
    
    # Create the JSON structure
    output_data = {
        "curriculum_name": curriculum_name,
        "total_lessons": len(lessons),
        "lessons": lessons
    }
    
    # Save to file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    file_count += 1
    print(f"  ✓ Saved: {filename} ({len(lessons)} lessons)")

print(f"\n{'=' * 60}")
print(f"✅ Successfully created {file_count} JSON mapping files")
print(f"📁 Location: {output_dir}/")
print(f"📊 Total lessons processed: {lesson_count}")
print(f"{'=' * 60}")
