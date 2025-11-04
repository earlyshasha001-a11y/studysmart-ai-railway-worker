import os
import sys
import time
import requests
import json
from datetime import datetime
from typing import Optional, Dict, List

class ReplitController:
    """Lightweight Replit controller - orchestrates Railway workers via HTTP"""
    
    def __init__(self):
        self.railway_worker_url = os.getenv("RAILWAY_WORKER_URL", "")
        
        # Add https:// if missing
        if self.railway_worker_url and not self.railway_worker_url.startswith(("http://", "https://")):
            self.railway_worker_url = f"https://{self.railway_worker_url}"
        
        if not self.railway_worker_url:
            print("⚠️  RAILWAY_WORKER_URL not set - manual configuration required")
    
    def start_batch_job(self, max_mappings: int = 54, max_lessons_per_mapping: int = 100) -> bool:
        """Start batch processing on Railway worker"""
        print(f"\n🚀 Starting batch job on Railway worker...")
        print(f"   Max mappings: {max_mappings}")
        print(f"   Max lessons per mapping: {max_lessons_per_mapping}")
        
        try:
            response = requests.post(
                f"{self.railway_worker_url}/start",
                json={
                    "max_mappings": max_mappings,
                    "max_lessons_per_mapping": max_lessons_per_mapping
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Batch job started: {result.get('message')}")
                return True
            else:
                print(f"✗ Failed to start batch job: {response.status_code}")
                print(f"   {response.text}")
                return False
        except Exception as e:
            print(f"✗ Error starting batch job: {str(e)}")
            return False
    
    def test_connection(self) -> bool:
        """Test Railway worker connection"""
        print("🔗 Testing Railway worker connection...")
        
        if not self.railway_worker_url:
            print("✗ RAILWAY_WORKER_URL not configured")
            print("   Please set the environment variable after deploying Railway worker")
            return False
        
        try:
            response = requests.get(f"{self.railway_worker_url}/status", timeout=10)
            
            if response.status_code == 200:
                status = response.json()
                print(f"✓ Connected to Railway worker")
                print(f"  Status: {status.get('status')}")
                print(f"  Lessons generated: {status.get('lessons_generated', 0)}")
                return True
            else:
                print(f"✗ Worker responded with status {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Connection test failed: {str(e)}")
            print(f"   URL: {self.railway_worker_url}")
            return False
    
    def get_worker_status(self) -> Optional[Dict]:
        """Get current worker status"""
        try:
            response = requests.get(f"{self.railway_worker_url}/status", timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None
    
    def monitor_progress(self, poll_interval: int = 30, timeout: int = 7200) -> bool:
        """Monitor worker progress until completion"""
        print(f"\n⏳ Monitoring worker progress...")
        print(f"   Poll interval: {poll_interval} seconds")
        print(f"   Timeout: {timeout/60} minutes")
        
        start_time = time.time()
        last_generated = 0
        
        while time.time() - start_time < timeout:
            status = self.get_worker_status()
            
            if not status:
                print(f"  ⚠️  Cannot reach worker")
                time.sleep(poll_interval)
                continue
            
            current_status = status.get("status", "unknown")
            lessons_generated = status.get("lessons_generated", 0)
            lessons_failed = status.get("lessons_failed", 0)
            runtime = status.get("runtime", 0)
            
            # Show progress if changed
            if lessons_generated > last_generated:
                print(f"  Progress: {lessons_generated} generated, {lessons_failed} failed ({runtime/60:.1f}min)")
                last_generated = lessons_generated
            
            # Check if completed
            if current_status == "completed":
                print(f"  ✓ Worker completed successfully")
                return True
            elif current_status == "error":
                print(f"  ✗ Worker encountered an error")
                return False
            
            time.sleep(poll_interval)
        
        print("  ⚠️  Monitoring timeout reached")
        return False
    
    def get_batch_summary(self) -> Dict:
        """Retrieve batch processing summary from Railway worker"""
        print("\n📊 Retrieving batch summary...")
        
        try:
            response = requests.get(f"{self.railway_worker_url}/summary", timeout=30)
            if response.status_code == 200:
                summary = response.json()
                print(f"✓ Summary retrieved")
                return summary
            else:
                print(f"✗ Failed to retrieve summary: {response.status_code}")
                return {"error": "Failed to retrieve summary"}
        except Exception as e:
            print(f"✗ Error retrieving summary: {str(e)}")
            return {"error": str(e)}
    
    def run(self, max_mappings: int = 54, max_lessons_per_mapping: int = 100):
        """Main controller execution"""
        print("\n" + "="*60)
        print("  StudySmart AI - Replit Controller")
        print("  Lightweight Orchestration System")
        print("="*60)
        
        # Test connection
        if not self.test_connection():
            print("\n❌ Cannot proceed without valid Railway worker connection")
            print("\n📋 Setup Instructions:")
            print("1. Deploy railway_worker.py to Railway")
            print("2. Ensure Railway service is running")
            print("3. Set RAILWAY_WORKER_URL environment variable")
            print("   Example: https://your-worker.railway.app")
            return
        
        # Start batch job
        if not self.start_batch_job(max_mappings, max_lessons_per_mapping):
            print("\n❌ Failed to start batch job on Railway worker")
            return
        
        # Monitor progress
        print("\n" + "="*60)
        print("  BATCH JOB STARTED - MONITORING PROGRESS")
        print("="*60)
        print("💡 Railway worker is now:")
        print("   • Loading curriculum files")
        print("   • Generating lessons with DeepSeek V3.1")
        print("   • Validating character counts")
        print("   • Saving output to Railway storage")
        print("\n⏳ Replit is monitoring progress...")
        
        # Monitor until completion
        success = self.monitor_progress()
        
        # Get final summary
        summary = self.get_batch_summary()
        
        # Final status
        print("\n" + "="*60)
        print("  BATCH JOB COMPLETE")
        print("="*60)
        print(f"Status: {'Success' if success else 'Timeout/Error'}")
        print(f"\n📊 Summary:")
        print(f"   Lessons generated: {summary.get('lessons_generated', 0)}")
        print(f"   Lessons failed: {summary.get('lessons_failed', 0)}")
        print(f"   Runtime: {summary.get('runtime', 0)/60:.1f} minutes")
        print(f"   Worker status: {summary.get('status', 'unknown')}")
        
        if summary.get('batch_results'):
            print(f"\n📁 Results by mapping:")
            for result in summary['batch_results']:
                print(f"   {result.get('filename')}: {result.get('successful')}/{result.get('total')} successful")
        
        print("\n✓ Replit controller finished")
        print(f"   Worker URL: {self.railway_worker_url}")

if __name__ == "__main__":
    import sys
    
    controller = ReplitController()
    
    # Parse command line arguments
    max_mappings = 54
    max_lessons = 100
    
    if len(sys.argv) > 1:
        # Handle test mode
        if sys.argv[1].lower() in ["test", "demo", "trial"]:
            print("🧪 Running in TEST MODE")
            print("   Processing: 1 mapping, 10 lessons\n")
            max_mappings = 1
            max_lessons = 10
        else:
            try:
                max_mappings = int(sys.argv[1])
            except ValueError:
                print(f"❌ Invalid argument: '{sys.argv[1]}'")
                print("\nUsage:")
                print("  python replit_controller.py                    # Full run (54 mappings, 100 lessons each)")
                print("  python replit_controller.py test               # Test mode (1 mapping, 10 lessons)")
                print("  python replit_controller.py <mappings> <lessons>  # Custom (e.g., 5 50)")
                sys.exit(1)
    
    if len(sys.argv) > 2 and sys.argv[1].lower() not in ["test", "demo", "trial"]:
        try:
            max_lessons = int(sys.argv[2])
        except ValueError:
            print(f"❌ Invalid lessons argument: '{sys.argv[2]}'")
            sys.exit(1)
    
    controller.run(max_mappings=max_mappings, max_lessons_per_mapping=max_lessons)
