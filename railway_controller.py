import os
import sys
import requests
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List


class RailwayController:
    """Simple Railway API automation controller"""
    
    def __init__(self, api_key: str, project_id: Optional[str] = None, use_project_token: bool = False):
        self.api_key = api_key
        self.base_url = "https://backboard.railway.com/graphql/v2"
        
        # Support both account tokens and project tokens
        if use_project_token:
            self.headers = {
                "Project-Access-Token": api_key,
                "Content-Type": "application/json"
            }
        else:
            self.headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        
        self.workspace_id: Optional[str] = None
        self.project_id: Optional[str] = project_id
        self.service_id: Optional[str] = None
        self.use_project_token = use_project_token
    
    def _execute_query(self, query: str, variables: Optional[Dict] = None) -> Dict[Any, Any]:
        """Execute GraphQL query against Railway API"""
        payload: Dict[str, Any] = {"query": query}
        if variables:
            payload["variables"] = variables
        
        try:
            response = requests.post(
                self.base_url,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code >= 400:
                try:
                    error_details = response.json()
                    raise Exception(f"Railway API error ({response.status_code}): {error_details}")
                except:
                    raise Exception(f"Railway API error ({response.status_code}): {response.text}")
            
            result = response.json()
            
            if "errors" in result:
                raise Exception(f"GraphQL errors: {result['errors']}")
            
            return result.get("data", {})
        except requests.exceptions.RequestException as e:
            raise Exception(f"Railway API request failed: {str(e)}")
    
    def introspect_user_type(self) -> Optional[Dict]:
        """Introspect the User type to see available fields"""
        query = """
        query IntrospectionQuery {
            __type(name: "User") {
                name
                kind
                fields {
                    name
                    type {
                        name
                        kind
                        ofType {
                            name
                            kind
                        }
                    }
                    description
                }
            }
        }
        """
        
        try:
            data = self._execute_query(query)
            user_type = data.get("__type", {})
            
            if user_type:
                print(f"\n📋 User Type Fields:")
                fields = user_type.get("fields", [])
                for field in fields:
                    field_name = field.get("name")
                    print(f"  - {field_name}")
            
            return user_type
        except Exception as e:
            print(f"✗ Introspection failed: {str(e)}")
            return None
    
    def introspect_project_input(self) -> Optional[Dict]:
        """Introspect the ProjectCreateInput schema"""
        query = """
        query IntrospectionQuery {
            __type(name: "ProjectCreateInput") {
                name
                kind
                inputFields {
                    name
                    type {
                        name
                        kind
                        ofType {
                            name
                            kind
                        }
                    }
                    description
                }
            }
        }
        """
        
        try:
            data = self._execute_query(query)
            input_type = data.get("__type", {})
            
            if input_type:
                print(f"\n📋 ProjectCreateInput Schema:")
                fields = input_type.get("inputFields", [])
                for field in fields:
                    field_name = field.get("name")
                    field_type = field.get("type", {})
                    type_name = field_type.get("name") or field_type.get("ofType", {}).get("name")
                    desc = field.get("description", "")
                    print(f"  - {field_name}: {type_name} {desc}")
            
            return input_type
        except Exception as e:
            print(f"✗ Introspection failed: {str(e)}")
            return None
    
    def get_workspace_id(self) -> Optional[str]:
        """Get the user's default workspace ID"""
        query = """
        query {
            me {
                id
                workspaces {
                    edges {
                        node {
                            id
                            name
                        }
                    }
                }
            }
        }
        """
        
        try:
            data = self._execute_query(query)
            user = data.get("me", {})
            workspaces = user.get("workspaces", {}).get("edges", [])
            
            if workspaces:
                workspace = workspaces[0].get("node", {})
                workspace_id = workspace.get("id")
                print(f"  Workspace: {workspace.get('name')} (ID: {workspace_id})")
                return workspace_id
            return None
        except Exception as e:
            print(f"✗ Failed to get workspace ID: {str(e)}")
            return None
    
    def test_connection(self) -> bool:
        """Test Railway API connection"""
        if self.use_project_token:
            # For project tokens, test by querying the project
            if not self.project_id:
                print("✗ Project ID required for project token")
                return False
            
            query = """
            query GetProject($projectId: String!) {
                project(id: $projectId) {
                    id
                    name
                }
            }
            """
            
            try:
                data = self._execute_query(query, {"projectId": self.project_id})
                project = data.get("project", {})
                
                if project and project.get("id"):
                    print(f"✓ Successfully connected to Railway API")
                    print(f"  Project: {project.get('name')} (ID: {project.get('id')})")
                    return True
                else:
                    print("✗ Failed to access project with this token")
                    return False
            except Exception as e:
                print(f"✗ Connection test failed: {str(e)}")
                return False
        else:
            # For account tokens, query user info
            query = """
            query {
                me {
                    id
                    name
                    email
                }
            }
            """
            
            try:
                data = self._execute_query(query)
                user = data.get("me", {})
                
                if user:
                    print(f"✓ Successfully connected to Railway API")
                    print(f"  User: {user.get('name', 'N/A')} ({user.get('email', 'N/A')})")
                    return True
                else:
                    print("✗ Failed to authenticate with Railway API")
                    return False
            except Exception as e:
                error_str = str(e)
                print(f"✗ Connection test failed: {error_str}")
                
                if "Not Authorized" in error_str:
                    print("\n⚠️  Token Authorization Issue - please verify your token")
                
                return False
    
    def create_project(self, project_name: str = "StudySmart-AI-Worker") -> Optional[str]:
        """Create a new Railway project"""
        
        # Try without workspace ID first (uses default)
        query_simple = """
        mutation {
            projectCreate {
                id
                name
            }
        }
        """
        
        print(f"  Attempting to create project (using default workspace)...")
        
        try:
            data = self._execute_query(query_simple)
            project = data.get("projectCreate", {})
            
            if project and project.get("id"):
                self.project_id = project["id"]
                print(f"✓ Created project: {project.get('name', 'Unnamed')} (ID: {self.project_id})")
                return self.project_id
            else:
                print("✗ Failed to create project - empty response")
                return None
        except Exception as e:
            print(f"✗ Project creation failed: {str(e)}")
            return None
    
    def list_projects(self) -> list:
        """List existing Railway projects"""
        query = """
        query {
            projects {
                edges {
                    node {
                        id
                        name
                        createdAt
                    }
                }
            }
        }
        """
        
        try:
            data = self._execute_query(query)
            projects = data.get("projects", {}).get("edges", [])
            
            print(f"\n📋 Your Railway Projects:")
            for edge in projects:
                node = edge.get("node", {})
                print(f"  - {node.get('name')} (ID: {node.get('id')})")
            
            return projects
        except Exception as e:
            print(f"✗ Failed to list projects: {str(e)}")
            return []
    
    def create_service(self, project_id: str, service_name: str = "lesson-worker") -> Optional[str]:
        """Create a service in the project"""
        query = """
        mutation ServiceCreate($input: ServiceCreateInput!) {
            serviceCreate(input: $input) {
                service {
                    id
                    name
                }
            }
        }
        """
        
        variables = {
            "input": {
                "projectId": project_id,
                "name": service_name
            }
        }
        
        try:
            data = self._execute_query(query, variables)
            service = data.get("serviceCreate", {}).get("service", {})
            
            if service and service.get("id"):
                self.service_id = service["id"]
                print(f"✓ Created service: {service.get('name')} (ID: {self.service_id})")
                return self.service_id
            else:
                print("✗ Failed to create service")
                return None
        except Exception as e:
            print(f"✗ Service creation failed: {str(e)}")
            return None
    
    def get_project_info(self, project_id: str) -> Optional[Dict]:
        """Get detailed project information"""
        query = """
        query Project($id: String!) {
            project(id: $id) {
                id
                name
                createdAt
                environments {
                    edges {
                        node {
                            id
                            name
                        }
                    }
                }
                services {
                    edges {
                        node {
                            id
                            name
                        }
                    }
                }
            }
        }
        """
        
        variables = {"id": project_id}
        
        try:
            data = self._execute_query(query, variables)
            return data.get("project")
        except Exception as e:
            print(f"✗ Failed to get project info: {str(e)}")
            return None
    
    def list_workspaces(self) -> None:
        """List user's available workspaces"""
        query = """
        query {
            me {
                teams {
                    edges {
                        node {
                            id
                            name
                        }
                    }
                }
            }
        }
        """
        
        try:
            data = self._execute_query(query)
            teams = data.get("me", {}).get("teams", {}).get("edges", [])
            
            if teams:
                print(f"\n📋 Your Railway Teams/Workspaces:")
                for edge in teams:
                    node = edge.get("node", {})
                    print(f"  - {node.get('name')} (ID: {node.get('id')})")
            else:
                print("\n📋 No teams found - using personal workspace")
        except Exception as e:
            print(f"✗ Failed to list workspaces: {str(e)}")
    
    def run_deployment(self) -> bool:
        """Main deployment workflow"""
        print("\n" + "="*60)
        print("  Railway Automation Controller - StudySmart AI Worker")
        print("="*60 + "\n")
        
        print("Step 1: Testing Railway API connection...")
        if not self.test_connection():
            print("\n❌ Cannot proceed without valid Railway connection")
            if self.use_project_token:
                print("   Please verify RAILWAY_PROJECT_TOKEN and RAILWAY_PROJECT_ID in Secrets")
                print("\n📝 To get your project ID:")
                print("   1. Go to your project in Railway dashboard")
                print("   2. The URL will be: https://railway.app/project/PROJECT_ID")
                print("   3. Copy the PROJECT_ID and update RAILWAY_PROJECT_ID in Secrets")
            else:
                print("   Please check your RAILWAY_API_KEY in Secrets")
            return False
        
        # Skip workspace/project listing if using project token (already have project)
        if self.use_project_token:
            print(f"\n✓ Using existing project: {self.project_id}")
            print("\n📋 Project Details:")
            if self.project_id:
                project_info = self.get_project_info(self.project_id)
                if project_info:
                    print(f"  Name: {project_info.get('name')}")
                    environments = project_info.get('environments', {}).get('edges', [])
                    if environments:
                        print(f"  Environments:")
                        for env_edge in environments:
                            env = env_edge.get('node', {})
                            print(f"    - {env.get('name')} (ID: {env.get('id')})")
            return True
        
        self.list_workspaces()
        
        print("\nStep 2: Listing existing projects...")
        existing_projects = self.list_projects()
        
        # Check if StudySmart-AI-Worker already exists
        studysmart_project = None
        for proj in existing_projects:
            if proj.get("name") == "StudySmart-AI-Worker":
                studysmart_project = proj
                self.project_id = proj.get("id")
                print(f"\n✓ Found existing 'StudySmart-AI-Worker' project")
                print(f"  Project ID: {self.project_id}")
                break
        
        if not studysmart_project:
            print("\nStep 3: Creating new project 'StudySmart-AI-Worker'...")
            created_id = self.create_project("StudySmart-AI-Worker")
            
            if not created_id:
                print("\n⚠️  API-based project creation failed")
                print("\n📋 Manual Setup Required:")
                print("   1. Go to https://railway.app/new")
                print("   2. Click 'Empty Project'")
                print("   3. Rename it to 'StudySmart-AI-Worker'")
                print("   4. Copy the project ID from the URL")
                print("   5. Add it to Secrets as RAILWAY_PROJECT_ID")
                print("   6. Re-run this controller")
                return False
        
        if not self.project_id:
            print("\n❌ Project ID not set")
            return False
        
        print("\nStep 4: Creating worker service...")
        service_id = self.create_service(self.project_id, "lesson-worker")
        
        if not service_id:
            print("\n⚠️  Project created but service creation failed")
            print(f"   You can manually add a service to project: {self.project_id}")
            return False
        
        print("\nStep 5: Verifying deployment...")
        project_info = self.get_project_info(self.project_id)
        
        if project_info:
            print(f"✓ Project verified: {project_info.get('name')}")
            services = project_info.get('services', {}).get('edges', [])
            print(f"  Services: {len(services)} active")
        
        print("\n" + "="*60)
        print("  ✅ Railway Connection Established Successfully!")
        print("="*60)
        print(f"\n📍 Project ID: {self.project_id}")
        print(f"📍 Service ID: {service_id}")
        print(f"\n🔗 Dashboard: https://railway.app/project/{self.project_id}")
        print("\n💡 Next steps:")
        print("   1. Add your StudySmart AI lesson directives")
        print("   2. Upload curriculum JSON files")
        print("   3. Configure worker deployment settings")
        print("\n" + "="*60 + "\n")
        
        return True


class StudySmartOrchestrator:
    """Orchestrates StudySmart AI lesson generation using DeepSeek V3.1 via OpenRouter"""
    
    def __init__(self, openrouter_key: str):
        self.openrouter_key = openrouter_key
        self.openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "deepseek/deepseek-chat"
        self.curriculum_dir = Path("curriculum")
        self.output_dir = Path("output")
        self.master_directive = None
        self.lesson_mappings = []
        
    def load_curriculum_files(self) -> bool:
        """Load master directive and lesson mappings from curriculum directory"""
        print("\n📂 Loading curriculum files...")
        
        if not self.curriculum_dir.exists():
            print("✗ Curriculum directory not found")
            return False
        
        json_files = list(self.curriculum_dir.glob("*.json"))
        
        if not json_files:
            print("✗ No JSON files found in curriculum directory")
            print("\n📝 Please upload:")
            print("   1. MASTER_DIRECTIVE_v*.json")
            print("   2. Your lesson mapping JSON files")
            return False
        
        # Load master directive
        for file_path in json_files:
            if "MASTER_DIRECTIVE" in file_path.name.upper():
                with open(file_path, 'r') as f:
                    self.master_directive = json.load(f)
                print(f"✓ Loaded master directive: {file_path.name}")
            else:
                with open(file_path, 'r') as f:
                    mapping = json.load(f)
                    self.lesson_mappings.append({
                        "filename": file_path.name,
                        "data": mapping
                    })
                print(f"✓ Loaded lesson mapping: {file_path.name}")
        
        if not self.master_directive:
            print("⚠️  No master directive found (looking for MASTER_DIRECTIVE_*.json)")
        
        print(f"\n📊 Summary: {len(self.lesson_mappings)} lesson mapping(s) loaded")
        return len(self.lesson_mappings) > 0
    
    def generate_lesson_script(self, lesson_data: Dict, directive: Optional[Dict] = None) -> Optional[str]:
        """Generate a single lesson script using DeepSeek V3.1"""
        headers = {
            "Authorization": f"Bearer {self.openrouter_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://replit.com",
            "X-Title": "StudySmart AI Controller"
        }
        
        # Build prompt
        prompt = "Generate a StudySmart AI lesson script following these requirements:\n\n"
        
        if directive or self.master_directive:
            directive_text = json.dumps(directive or self.master_directive, indent=2)
            prompt += f"MASTER DIRECTIVE:\n{directive_text}\n\n"
        
        prompt += f"LESSON DATA:\n{json.dumps(lesson_data, indent=2)}\n\n"
        prompt += "Generate a complete lesson script (7,000-8,000 characters) following the StudySmart format."
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 8192
        }
        
        try:
            response = requests.post(
                self.openrouter_url,
                headers=headers,
                json=payload,
                timeout=120
            )
            
            if response.status_code != 200:
                print(f"✗ OpenRouter API error: {response.status_code}")
                return None
            
            result = response.json()
            lesson_script = result['choices'][0]['message']['content']
            return lesson_script
            
        except Exception as e:
            print(f"✗ Lesson generation failed: {str(e)}")
            return None
    
    def process_batch(self, mapping_file: Dict, max_lessons: int = 100) -> Dict[str, Any]:
        """Process a batch of lessons from a mapping file"""
        filename = mapping_file["filename"]
        data = mapping_file["data"]
        
        print(f"\n{'='*60}")
        print(f"Processing: {filename}")
        print(f"{'='*60}")
        
        lessons = data.get("lessons", [])
        total = min(len(lessons), max_lessons)
        
        print(f"📊 Batch size: {total} lessons")
        
        # Create output directory for this batch
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
            lesson_id = lesson.get("lesson_id", f"L{i:03d}")
            print(f"\n[{i}/{total}] Generating lesson: {lesson_id}")
            
            script = self.generate_lesson_script(lesson)
            
            if script:
                # Save lesson script
                output_file = output_path / f"{lesson_id}.json"
                lesson_output = {
                    "lesson_id": lesson_id,
                    "generated_at": datetime.now().isoformat(),
                    "source_mapping": filename,
                    "lesson_data": lesson,
                    "script": script
                }
                
                with open(output_file, 'w') as f:
                    json.dump(lesson_output, f, indent=2)
                
                results["successful"] += 1
                print(f"✓ Saved: {output_file}")
            else:
                results["failed"] += 1
                print(f"✗ Failed to generate lesson {lesson_id}")
            
            # Progress update every lesson
            print(f"Progress: {results['successful']}/{total} successful, {results['failed']} failed")
            time.sleep(1)  # Rate limiting
        
        return results
    
    def run_generation(self, max_lessons_per_batch: int = 100) -> bool:
        """Main lesson generation workflow"""
        print("\n" + "="*60)
        print("  StudySmart AI - DeepSeek V3.1 Lesson Generation")
        print("="*60)
        
        if not self.load_curriculum_files():
            return False
        
        all_results = []
        
        for mapping in self.lesson_mappings:
            results = self.process_batch(mapping, max_lessons_per_batch)
            all_results.append(results)
            
            print(f"\n✓ Batch complete: {results['successful']}/{results['total']} successful")
        
        # Final summary
        print("\n" + "="*60)
        print("  ✅ DeepSeek V3.1 Batch Complete")
        print("="*60)
        
        total_successful = sum(r["successful"] for r in all_results)
        total_failed = sum(r["failed"] for r in all_results)
        
        print(f"\n📊 Total lessons generated: {total_successful}")
        print(f"⚠️  Failed: {total_failed}")
        
        for result in all_results:
            print(f"\n  📁 {result['filename']}")
            print(f"     Output: {result['output_dir']}")
            print(f"     Success: {result['successful']}/{result['total']}")
        
        return True


def main():
    """Main entry point - StudySmart AI Orchestration Controller"""
    print("\n" + "="*60)
    print("  StudySmart AI - Railway Orchestration Controller")
    print("="*60 + "\n")
    
    # Check for Railway connection first
    project_token = os.getenv("RAILWAY_PROJECT_TOKEN")
    project_id = os.getenv("RAILWAY_PROJECT_ID")
    
    if project_token and project_id:
        print("✓ Using RAILWAY_PROJECT_TOKEN (project-specific token)")
        controller = RailwayController(project_token, project_id=project_id, use_project_token=True)
        
        # Test Railway connection
        print("\n🔗 Testing Railway connection...")
        if controller.test_connection():
            print("✓ Railway connection verified")
        else:
            print("✗ Railway connection failed")
            sys.exit(1)
    else:
        print("⚠️  Railway tokens not configured (optional for local generation)")
        print("   Add RAILWAY_PROJECT_TOKEN and RAILWAY_PROJECT_ID to enable Railway deployment")
    
    # Check for OpenRouter API key
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    
    if not openrouter_key:
        print("\n❌ ERROR: OPENROUTER_API_KEY not found")
        print("\n📝 To enable StudySmart AI lesson generation:")
        print("   1. Go to https://openrouter.ai/keys")
        print("   2. Create an API key")
        print("   3. Add to Replit Secrets:")
        print("      Key: OPENROUTER_API_KEY")
        print("      Value: (your OpenRouter API key)")
        sys.exit(1)
    
    print("✓ OpenRouter API key found")
    
    # Initialize StudySmart Orchestrator
    orchestrator = StudySmartOrchestrator(openrouter_key)
    
    # Run lesson generation
    print("\n🚀 Starting StudySmart AI lesson generation...")
    success = orchestrator.run_generation(max_lessons_per_batch=100)
    
    if not success:
        print("\n❌ Lesson generation failed")
        sys.exit(1)
    
    print("\n✅ All operations completed successfully!")


if __name__ == "__main__":
    main()
