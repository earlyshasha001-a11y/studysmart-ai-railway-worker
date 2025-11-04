import os
import sys
import json
from pathlib import Path
from railway_controller import StudySmartOrchestrator

def test_single_lesson():
    """Test generating a single lesson to verify output format"""
    
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    
    if not openrouter_key:
        print("ERROR: OPENROUTER_API_KEY not found")
        sys.exit(1)
    
    print("="*60)
    print("  Testing Single Lesson Generation")
    print("="*60)
    
    orchestrator = StudySmartOrchestrator(openrouter_key)
    
    if not orchestrator.load_curriculum_files():
        print("ERROR: Failed to load curriculum files")
        sys.exit(1)
    
    if not orchestrator.lesson_mappings:
        print("ERROR: No lesson mappings found")
        sys.exit(1)
    
    first_mapping = orchestrator.lesson_mappings[0]
    print(f"\n📋 Using: {first_mapping['filename']}")
    
    lessons = first_mapping['data'].get('lessons', [])
    if not lessons:
        print("ERROR: No lessons in mapping")
        sys.exit(1)
    
    test_lesson = lessons[0]
    print(f"📝 Test lesson: {test_lesson}")
    
    print("\n🔄 Generating lesson content...")
    lesson_content = orchestrator.generate_lesson_content(test_lesson)
    
    if not lesson_content:
        print("ERROR: Failed to generate lesson content")
        sys.exit(1)
    
    print("\n✓ Lesson content generated successfully!")
    print(f"  Script parts: {len(lesson_content.get('script_parts', []))}")
    print(f"  Notes parts: {len(lesson_content.get('notes_parts', []))}")
    print(f"  Illustrations: {len(lesson_content.get('illustrations', []))}")
    
    output_path = Path("output") / "test"
    output_path.mkdir(parents=True, exist_ok=True)
    
    lesson_id = "L001_TEST"
    
    print(f"\n💾 Saving 3 files to {output_path}/...")
    success = orchestrator.save_lesson_files(output_path, lesson_id, lesson_content, test_lesson)
    
    if not success:
        print("ERROR: Failed to save lesson files")
        sys.exit(1)
    
    print("\n✅ Test completed successfully!")
    print(f"\n📂 Output files created in: {output_path}/")
    print(f"  - {lesson_id}_Script.csv")
    print(f"  - {lesson_id}_Notes_Exercises.csv")
    print(f"  - {lesson_id}_Illustrations.json")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    test_single_lesson()
