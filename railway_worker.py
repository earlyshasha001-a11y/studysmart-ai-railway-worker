import os
import sys
import json
import time
import requests
import psutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

class StudySmartWorker:
    """Railway worker for heavy DeepSeek V3.1 lesson generation"""
    
    def __init__(self):
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY")
        self.openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "deepseek/deepseek-chat"
        self.output_dir = Path("/tmp/output")
        self.curriculum_dir = Path("curriculum")
        self.start_time = time.time()
        self.max_runtime = 7200  # 2 hours
        self.lessons_generated = 0
        self.lessons_failed = 0
        self.current_status = "idle"
        self.batch_results = []
        
    def log_resources(self):
        """Log memory and CPU usage"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        print(f"📊 Resources: CPU={cpu_percent}%, Memory={memory.percent}% used")
        
        if cpu_percent > 85:
            print("⚠️  High CPU usage detected - pausing briefly...")
            time.sleep(30)
    
    def load_curriculum_files(self) -> tuple:
        """Load master directive and lesson mappings"""
        print("\n📂 Loading curriculum files from Railway environment...")
        
        master_directive = None
        lesson_mappings = []
        
        if not self.curriculum_dir.exists():
            print(f"✗ Curriculum directory not found: {self.curriculum_dir}")
            return None, []
        
        json_files = list(self.curriculum_dir.glob("*.json"))
        
        for file_path in json_files:
            if "MASTER_DIRECTIVE" in file_path.name.upper():
                with open(file_path, 'r') as f:
                    master_directive = json.load(f)
                print(f"✓ Loaded master directive: {file_path.name}")
            else:
                with open(file_path, 'r') as f:
                    mapping = json.load(f)
                    lesson_mappings.append({
                        "filename": file_path.name,
                        "data": mapping
                    })
                print(f"✓ Loaded lesson mapping: {file_path.name}")
        
        print(f"\n📊 Summary: {len(lesson_mappings)} lesson mapping(s) loaded")
        return master_directive, lesson_mappings
    
    def validate_character_count(self, text: str, min_chars: int = 1600, max_chars: int = 1950) -> bool:
        """Validate text meets character count requirements"""
        char_count = len(text)
        return min_chars <= char_count <= max_chars
    
    def call_deepseek(self, lesson_data: Dict, directive: Dict, num_parts: int, max_retries: int = 3) -> Optional[Dict]:
        """Call DeepSeek V3.1 with retry logic"""
        
        # Extract relevant directive rules
        lesson_structure = directive.get("lesson_structure", {})
        if num_parts == 4:
            structure_info = lesson_structure.get("lower_primary", {})
        else:
            structure_info = lesson_structure.get("upper_secondary", {})
        
        part_names = structure_info.get("flow", [])
        teacher_rotation = directive.get("teacher_rotation", {}).get("assignments", {})
        
        for attempt in range(1, max_retries + 1):
            if attempt > 1:
                print(f"  🔄 Retry attempt {attempt}/{max_retries}...")
                time.sleep(5)  # Rate limiting backoff
            
            try:
                headers = {
                    "Authorization": f"Bearer {self.openrouter_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://railway.app",
                    "X-Title": "StudySmart AI Worker"
                }
                
                # Get grade/year/form to determine teacher
                grade_year_form = lesson_data.get("Grade", lesson_data.get("Year", lesson_data.get("Form", "")))
                subject = lesson_data.get("Subject", "")
                lesson_num = lesson_data.get("Lesson Number", "")
                topic = lesson_data.get("LessonTopic", "")
                
                prompt = f"""TASK: Generate educational content for StudySmart AI

⚠️ CRITICAL LENGTH REQUIREMENT ⚠️
Each script part MUST be 1600-1950 characters (250-300 words).
Content below 1600 characters will be REJECTED automatically.

📐 HOW TO WRITE 1750 CHARACTERS (Target Length):
Write approximately 12-15 full sentences covering:
- Opening greeting (1-2 sentences)
- Topic introduction with context (2-3 sentences)
- Main explanation with examples (5-7 sentences)
- Real-world application (2-3 sentences)
- Reinforcement/summary (1-2 sentences)

EXAMPLE - Notice the LENGTH (1650 chars):
"Hello learners. I am Sarah Johnson from StudySmart AI. This is Grade one Mathematics, Lesson three. Today we will learn about counting to ten. In our previous lesson, we learned about recognizing numbers from one to five. Now we will extend our knowledge to count all the way to ten, which is an important skill you will use every single day of your life. Let us begin our journey with numbers. When we count, we say the number names in order: one, two, three, four, five, six, seven, eight, nine, and ten. Each number represents a specific quantity. For example, if I show you one pencil, you say 'one'. If I show you two pencils, you say 'two'. Here is an illustration of ten colorful pencils arranged in a row from left to right. Notice how each pencil is different, but we can count them all. We start from the left and point to each pencil as we count: one, two, three, four, five, six, seven, eight, nine, ten. Let me give you another example using something you see every day. Imagine you have fingers on your hands. If you hold up all your fingers, you have ten fingers total! Five on your left hand and five on your right hand. When you add five plus five together, you get ten. This is why ten is such a special number. You can use your fingers to help you count whenever you need to. Now let us practice counting different objects. Here is an illustration of ten bright red apples on a table. Can you imagine counting them one by one? You would say: one apple, two apples, three apples, four apples, five apples, six apples, seven apples, eight apples, nine apples, ten apples. Well done!"

LESSON INFORMATION:
Subject: {subject}
Level: {grade_year_form}
Lesson {lesson_num}: {topic}
Learning Objective: {lesson_data.get('LessonObjective', '')}

STRUCTURE - You must create {num_parts} parts following this sequence:
{chr(10).join(f"{i+1}. {part_names[i] if i < len(part_names) else f'Part {i+1}'}" for i in range(num_parts))}

CONTENT GUIDELINES:
- Use natural spoken English (British/Kenyan style)
- Write numbers as words (one, two, ten) NOT numerals (1, 2, 10)
- No mathematical symbols (write "plus" not "+", "equals" not "=")
- Each part needs 1600-1950 characters minimum
- Include 6-10 illustrations total (at least 1 per part)
- Notes & exercises: 1600-1950 characters (bulleted notes + 8-10 exercises)

OUTPUT FORMAT (JSON only):
{{
  "script_parts": [
    {{"heading": "{part_names[0] if len(part_names) > 0 else 'Part 1'}", "content": "1600-1950 character detailed narration"}},
    {{"heading": "{part_names[1] if len(part_names) > 1 else 'Part 2'}", "content": "1600-1950 character detailed narration"}},
    {"..." if num_parts > 2 else ""}
    {{"heading": "{part_names[num_parts-1] if len(part_names) >= num_parts else f'Part {num_parts}'}", "content": "1600-1950 character detailed narration"}}
  ],
  "notes_exercises": "1600-1950 characters with bulleted notes and 8-10 practice exercises",
  "illustrations": [
    {{"illustration_number": 1, "scene_description": "Clear description of visual", "elements": ["object1", "object2"], "part_association": 1}},
    ... (6-10 total illustrations)
  ]
}}

⚠️ WRITE LONG, DETAILED CONTENT - Each part needs ~270 words (1750 chars target). Short content FAILS validation.

Return ONLY the JSON object."""
                
                system_message = """You are an expert educational content writer. You MUST generate LONG, DETAILED content that meets EXACT length requirements. 

CRITICAL RULE: Each script part must be EXACTLY 1600-1950 characters (approximately 250-300 words).
This is NOT optional - content shorter than 1600 characters will be REJECTED.

Write comprehensive, thorough explanations with:
- Detailed introductions and context
- Multiple examples and illustrations
- Step-by-step explanations
- Real-world applications
- Summary and reinforcement

DO NOT write brief, concise, or summarized content. EXPAND everything fully."""

                payload = {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.8,
                    "max_tokens": 16384
                }
                
                response = requests.post(
                    self.openrouter_url,
                    headers=headers,
                    json=payload,
                    timeout=180
                )
                
                if response.status_code == 429:
                    print(f"  ⚠️  Rate limit hit - waiting 60 seconds...")
                    time.sleep(60)
                    continue
                
                if response.status_code != 200:
                    print(f"  ✗ API error: {response.status_code}")
                    continue
                
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Clean JSON
                content = content.strip()
                if content.startswith('```json'):
                    content = content[7:]
                if content.startswith('```'):
                    content = content[3:]
                if content.endswith('```'):
                    content = content[:-3]
                content = content.strip()
                
                lesson_content = json.loads(content)
                
                # Validate structure
                if not all(k in lesson_content for k in ["script_parts", "notes_exercises", "illustrations"]):
                    print(f"  ✗ Missing required keys")
                    continue
                
                script_parts = lesson_content.get("script_parts", [])
                notes_exercises = lesson_content.get("notes_exercises", "")
                
                if len(script_parts) != num_parts:
                    print(f"  ⚠️  Wrong number of script parts: {len(script_parts)} (expected {num_parts})")
                    continue
                
                # Validate character counts
                script_valid = all(self.validate_character_count(part.get("content", "")) for part in script_parts)
                notes_valid = self.validate_character_count(notes_exercises)
                
                if script_valid and notes_valid:
                    print(f"  ✓ Validation passed")
                    return lesson_content
                
                print(f"  ⚠️  Character count validation failed")
                
            except Exception as e:
                print(f"  ✗ Error: {str(e)}")
                continue
        
        return None
    
    def save_lesson_files(self, output_path: Path, lesson_id: str, lesson_content: Dict, lesson_data: Dict) -> bool:
        """Save lesson files to Railway storage"""
        try:
            subject = lesson_data.get("Subject", "SUBJECT").replace(" ", "")
            grade_year_form = lesson_data.get("Grade", lesson_data.get("Year", lesson_data.get("Form", "GRADE"))).replace(" ", "")
            lesson_num = lesson_data.get("Lesson Number", lesson_id.replace("L", ""))
            
            base_filename = f"{subject}_{grade_year_form}_Lesson{lesson_num}"
            
            # Save as JSON
            lesson_file = output_path / f"{lesson_id}_complete.json"
            complete_data = {
                "lesson_id": lesson_id,
                "base_filename": base_filename,
                "lesson_data": lesson_data,
                "generated_content": lesson_content,
                "generated_at": datetime.now().isoformat()
            }
            
            with open(lesson_file, 'w', encoding='utf-8') as f:
                json.dump(complete_data, f, indent=2)
            
            print(f"  ✓ Saved: {lesson_id}_complete.json")
            return True
            
        except Exception as e:
            print(f"  ✗ Save error: {str(e)}")
            return False
    
    def process_batch(self, mapping_file: Dict, max_lessons: int = 1000) -> Dict:
        """Process a batch of lessons"""
        filename = mapping_file["filename"]
        data = mapping_file["data"]
        
        print(f"\n{'='*60}")
        print(f"Processing: {filename}")
        print(f"{'='*60}")
        
        lessons = data.get("lessons", [])
        total = min(len(lessons), max_lessons)
        
        today = datetime.now().strftime("%Y-%m-%d")
        output_path = self.output_dir / today / filename.replace(".json", "")
        output_path.mkdir(parents=True, exist_ok=True)
        
        results = {
            "filename": filename,
            "total": total,
            "successful": 0,
            "failed": 0,
            "output_dir": str(output_path)
        }
        
        for i, lesson in enumerate(lessons[:total], 1):
            # Check runtime limit
            if time.time() - self.start_time > self.max_runtime:
                print(f"\n⚠️  Maximum runtime reached ({self.max_runtime/3600} hours)")
                break
            
            # Log resources every 10 lessons
            if i % 10 == 0:
                self.log_resources()
            
            lesson_id = lesson.get("Lesson Number", f"{i:03d}")
            if not lesson_id.startswith("L"):
                lesson_id = f"L{lesson_id}"
            
            print(f"\n[{i}/{total}] Generating lesson: {lesson_id}")
            
            # Determine part count
            grade = lesson.get("Grade", "").lower()
            year = lesson.get("Year", "").lower()
            form = lesson.get("Form", "").lower()
            
            is_lower_primary = any(x in grade + year for x in ["grade 1", "grade 2", "grade 3", "grade 4", "grade 5", "grade 6", "year 1", "year 2", "year 3", "year 4", "year 5", "year 6"])
            num_parts = 4 if is_lower_primary else 8
            
            # Generate lesson
            master_directive_files = list(self.curriculum_dir.glob("MASTER_DIRECTIVE*.json"))
            master_directive = None
            if master_directive_files:
                with open(master_directive_files[0], 'r') as f:
                    master_directive = json.load(f)
            
            lesson_content = self.call_deepseek(lesson, master_directive, num_parts)
            
            if lesson_content:
                if self.save_lesson_files(output_path, lesson_id, lesson_content, lesson):
                    results["successful"] += 1
                    self.lessons_generated += 1
                else:
                    results["failed"] += 1
                    self.lessons_failed += 1
            else:
                results["failed"] += 1
                self.lessons_failed += 1
                print(f"  ✗ Failed to generate lesson {lesson_id}")
            
            print(f"Progress: {results['successful']}/{total} successful, {results['failed']} failed")
            
            # Rate limiting
            time.sleep(4)
        
        return results
    
    def run_batch_job(self, max_mappings: int = 54, max_lessons_per_mapping: int = 100):
        """Run batch processing job"""
        # Reset counters for new batch
        self.start_time = time.time()
        self.lessons_generated = 0
        self.lessons_failed = 0
        self.batch_results = []
        self.current_status = "processing"
        
        print("\n" + "="*60)
        print("  StudySmart AI - Railway Worker")
        print("  DeepSeek V3.1 Lesson Generation")
        print("="*60)
        
        # Load curriculum
        master_directive, lesson_mappings = self.load_curriculum_files()
        
        if not lesson_mappings:
            print("✗ No lesson mappings found!")
            self.current_status = "error"
            return
        
        # Process all mappings
        self.batch_results = []
        for mapping in lesson_mappings[:max_mappings]:
            results = self.process_batch(mapping, max_lessons=max_lessons_per_mapping)
            self.batch_results.append(results)
        
        # Summary
        print("\n" + "="*60)
        print("  BATCH COMPLETE")
        print("="*60)
        print(f"Total lessons generated: {self.lessons_generated}")
        print(f"Total lessons failed: {self.lessons_failed}")
        print(f"Runtime: {(time.time() - self.start_time)/60:.1f} minutes")
        print(f"Output directory: {self.output_dir}")
        
        # Save summary
        summary_file = self.output_dir / f"batch_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        summary_file.parent.mkdir(parents=True, exist_ok=True)
        with open(summary_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "runtime_seconds": time.time() - self.start_time,
                "lessons_generated": self.lessons_generated,
                "lessons_failed": self.lessons_failed,
                "results": self.batch_results
            }, f, indent=2)
        
        print(f"✓ Summary saved: {summary_file}")
        self.current_status = "completed"
        print("\n🎯 Worker batch complete")

class WorkerHTTPHandler(BaseHTTPRequestHandler):
    """HTTP handler for Railway worker API"""
    
    worker = None
    
    def do_GET(self):
        """Handle GET requests for status"""
        if self.path == "/status":
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                "status": self.worker.current_status,
                "lessons_generated": self.worker.lessons_generated,
                "lessons_failed": self.worker.lessons_failed,
                "runtime": time.time() - self.worker.start_time
            }
            self.wfile.write(json.dumps(response).encode())
        
        elif self.path == "/summary":
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                "status": self.worker.current_status,
                "lessons_generated": self.worker.lessons_generated,
                "lessons_failed": self.worker.lessons_failed,
                "runtime": time.time() - self.worker.start_time,
                "batch_results": self.worker.batch_results
            }
            self.wfile.write(json.dumps(response).encode())
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Handle POST requests for starting jobs"""
        if self.path == "/start":
            # Prevent concurrent batch runs
            if self.worker.current_status == "processing":
                self.send_response(409)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                
                response = {"error": "Batch job already in progress"}
                self.wfile.write(json.dumps(response).encode())
                return
            
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                params = json.loads(post_data.decode()) if post_data else {}
                max_mappings = params.get("max_mappings", 54)
                max_lessons = params.get("max_lessons_per_mapping", 100)
                
                # Start batch job in background thread
                thread = threading.Thread(
                    target=self.worker.run_batch_job,
                    args=(max_mappings, max_lessons)
                )
                thread.daemon = True
                thread.start()
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                
                response = {"message": "Batch job started", "status": "processing"}
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                
                response = {"error": str(e)}
                self.wfile.write(json.dumps(response).encode())
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default request logging"""
        pass

def run_http_server(port=5000):
    """Run HTTP server for Railway worker"""
    worker = StudySmartWorker()
    WorkerHTTPHandler.worker = worker
    
    server = HTTPServer(('0.0.0.0', port), WorkerHTTPHandler)
    print(f"\n🚀 Railway Worker API listening on port {port}")
    print(f"Endpoints:")
    print(f"  POST /start - Start batch job")
    print(f"  GET /status - Get current status")
    print(f"  GET /summary - Get detailed summary")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n⚠️  Server stopped")
        server.shutdown()

if __name__ == "__main__":
    # Check if running as HTTP server (Railway) or standalone
    mode = os.getenv("WORKER_MODE", "http")
    
    if mode == "http":
        port = int(os.getenv("PORT", 5000))
        run_http_server(port)
    else:
        # Standalone mode
        worker = StudySmartWorker()
        worker.run_batch_job()
