import os
import sys
import requests
import time
import json
import csv
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
    
    def validate_character_count(self, text: str, min_chars: int = 1600, max_chars: int = 1950) -> bool:
        """Validate text meets character count requirements"""
        char_count = len(text)
        return min_chars <= char_count <= max_chars
    
    def format_csv_field(self, text: str) -> str:
        """Format text for CSV: remove line breaks, escape quotes"""
        text = text.replace('\n', ' ').replace('\r', ' ')
        text = ' '.join(text.split())
        text = text.replace('"', '""')
        return text
    
    def _reload_current_files(self, current_mapping_filename: str) -> Optional[Dict]:
        """Reload master directive, curriculum-specific directive, and current lesson mapping from disk for accuracy"""
        try:
            master_directive_files = list(self.curriculum_dir.glob("MASTER_DIRECTIVE*.json"))
            if master_directive_files:
                with open(master_directive_files[0], 'r') as f:
                    self.master_directive = json.load(f)
                print(f"  ✓ Reloaded: {master_directive_files[0].name}")
            
            curriculum_specific_directive = None
            directive_path = self.curriculum_dir / "directives" / current_mapping_filename
            if directive_path.exists():
                with open(directive_path, 'r') as f:
                    curriculum_specific_directive = json.load(f)
                print(f"  ✓ Loaded curriculum-specific directive: {current_mapping_filename}")
            
            current_mapping_file = self.curriculum_dir / current_mapping_filename
            if current_mapping_file.exists():
                with open(current_mapping_file, 'r') as f:
                    mapping_data = json.load(f)
                
                for idx, mapping in enumerate(self.lesson_mappings):
                    if mapping["filename"] == current_mapping_filename:
                        self.lesson_mappings[idx]["data"] = mapping_data
                        print(f"  ✓ Reloaded: {current_mapping_filename}")
                        break
            
            return curriculum_specific_directive
        except Exception as e:
            print(f"  ⚠️  Reload warning: {str(e)}")
            return None
    
    def generate_lesson_content(self, lesson_data: Dict, directive: Optional[Dict] = None, max_retries: int = 3) -> Optional[Dict]:
        """Generate complete lesson content (Script, Notes & Exercises, Illustrations) using DeepSeek V3.1 with retry logic"""
        
        grade = lesson_data.get("Grade", "").lower()
        year = lesson_data.get("Year", "").lower()
        form = lesson_data.get("Form", "").lower()
        
        is_lower_primary = any(x in grade + year for x in ["grade 1", "grade 2", "grade 3", "grade 4", "grade 5", "grade 6", "year 1", "year 2", "year 3", "year 4", "year 5", "year 6"])
        num_parts = 4 if is_lower_primary else 8
        
        for attempt in range(1, max_retries + 1):
            if attempt > 1:
                print(f"  Retry attempt {attempt}/{max_retries}...")
            
            lesson_content = self._call_deepseek(lesson_data, directive, num_parts)
            
            if not lesson_content:
                continue
            
            script_parts = lesson_content.get("script_parts", [])
            notes_content = lesson_content.get("notes_exercises", "")
            
            if len(script_parts) != num_parts:
                print(f"⚠️  Wrong number of script parts: {len(script_parts)} (expected {num_parts})")
                continue
            
            if not isinstance(notes_content, str):
                print(f"⚠️  Notes & Exercises must be a single text string, not a list")
                continue
            
            script_valid = all(self.validate_character_count(part.get("content", "")) for part in script_parts)
            notes_valid = self.validate_character_count(notes_content)
            
            if script_valid and notes_valid:
                print(f"✓ Character counts validated successfully")
                return lesson_content
            
            for i, part in enumerate(script_parts, 1):
                content_text = part.get("content", "")
                if not self.validate_character_count(content_text):
                    print(f"⚠️  Script part {i}: {len(content_text)} chars (expected 1600-1950)")
            
            if not self.validate_character_count(notes_content):
                print(f"⚠️  Notes & Exercises: {len(notes_content)} chars (expected 1600-1950)")
        
        print(f"✗ Failed to generate valid content after {max_retries} attempts")
        return None
    
    def _call_deepseek(self, lesson_data: Dict, directive: Optional[Dict], num_parts: int) -> Optional[Dict]:
        """Internal method to call DeepSeek API"""
        headers = {
            "Authorization": f"Bearer {self.openrouter_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://replit.com",
            "X-Title": "StudySmart AI Controller"
        }
        
        prompt = f"""You are generating a StudySmart AI lesson following Master Directive v7.2.

🚨🚨🚨 CRITICAL REQUIREMENT: STRICT PART COUNT AND CHARACTER REQUIREMENTS 🚨🚨🚨

YOUR RESPONSE WILL BE REJECTED IF IT DOESN'T MATCH THESE EXACT REQUIREMENTS!

MANDATORY STRUCTURE:
• EXACTLY {num_parts} script parts - EACH 1600-1950 chars (NO EXCEPTIONS!)
• EXACTLY ONE notes_exercises field - 1600-1950 chars TOTAL (NOT multiple parts - just ONE comprehensive text!)
• At least {num_parts} illustrations (minimum 1 per script part)

⚠️ NOTES & EXERCISES IS JUST ONE PART (NOT {num_parts} PARTS)! ⚠️
Write a single comprehensive Notes & Exercises section combining notes and practice questions!

CONCRETE EXAMPLE - THIS IS 1650 CHARACTERS (YOUR MINIMUM):

"Photosynthesis is the remarkable process by which green plants convert light energy from the sun into chemical energy stored in glucose molecules. This process is absolutely essential for life on Earth because it produces the oxygen we breathe and forms the foundation of most food chains. Plants contain special structures called chloroplasts in their cells, and within these chloroplasts is a green pigment called chlorophyll that captures light energy. Let's explore this process step by step. First, plants absorb water from the soil through their root systems. This water travels up through the stem in special tubes called xylem vessels, eventually reaching the leaves. At the same time, tiny pores called stomata on the underside of leaves open up to allow carbon dioxide from the air to enter the leaf. Now here's where the magic happens: when sunlight hits the chlorophyll in the chloroplast, it provides the energy needed to split water molecules into hydrogen and oxygen. The oxygen is released back into the atmosphere as a waste product - this is the oxygen that we humans and animals breathe! Meanwhile, the hydrogen combines with carbon dioxide in a complex series of chemical reactions to produce glucose, a simple sugar that the plant uses for energy and growth. We can write this as a chemical equation: 6CO2 + 6H2O + light energy → C6H12O6 + 6O2. In Kenya, we can see photosynthesis happening all around us - in the maize fields of the Rift Valley, in the tea plantations of Kericho, and in the lush forests of Mount Kenya. Farmers understand that crops need sunlight, water, and air to grow well. Without adequate sunlight, plants become weak and yellowish because they cannot produce enough chlorophyll. This is why farmers clear weeds that might shade their crops and why greenhouses are designed to maximize light exposure. Understanding photosynthesis helps us appreciate why protecting our forests and planting more trees is so important for our environment and our future."

READ THIS CAREFULLY: The above example is 1,650 characters. Every part you write MUST be this length or longer!

HOW TO REACH 1600+ CHARACTERS IN EACH PART:
1. Start with a solid introduction (200-250 chars)
2. Provide 3-4 detailed examples with full explanations (400-500 chars each)
3. Include real-world applications and connections (200-300 chars)
4. Add step-by-step processes where applicable (300-400 chars)
5. Conclude with synthesis and reinforcement (200-250 chars)

CONTENT EXPANSION STRATEGIES:
✓ Use concrete examples from African/Kenyan context
✓ Include step-by-step explanations with reasoning
✓ Add real-world applications and scenarios
✓ Provide multiple examples showing different aspects
✓ Explain the "why" behind concepts, not just the "what"
✓ Use analogies and comparisons to aid understanding
✓ Include historical context or background where relevant
✗ DO NOT use filler text or repetition
✗ DO NOT write brief summaries - write FULL DETAILED CONTENT

MASTER DIRECTIVE:
{json.dumps(directive or self.master_directive, indent=2)}

LESSON DATA:
{json.dumps(lesson_data, indent=2)}

OUTPUT FORMAT (strict JSON):
{{
  "script_parts": [
    {{"heading": "Introduction to [Topic]", "content": "MINIMUM 1600 characters of detailed narration script..."}},
    {{"heading": "[Concept 1]", "content": "MINIMUM 1600 characters of detailed narration script..."}},
    ... ({num_parts} total parts, EACH 1600-1950 chars)
  ],
  "notes_exercises": "SINGLE comprehensive text combining all notes and exercises. 1600-1950 characters TOTAL. Include bulleted notes explaining key concepts, then 8-10 practice questions. OCR-friendly format.",
  "illustrations": [
    {{
      "illustration_number": 1,
      "scene_description": "Detailed visual scene description",
      "elements": ["element1", "element2", "element3"],
      "part_association": 1
    }},
    ... (at least {num_parts} illustrations)
  ]
}}

⚠️  CRITICAL REMINDERS:
- Each script part "content": MINIMUM 1600 characters
- "notes_exercises" field: SINGLE text string of 1600-1950 characters (NOT an array!)
- Do NOT create "notes_parts" array - use "notes_exercises" string instead!

Return ONLY the JSON, no additional text."""
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.8,
            "max_tokens": 16384
        }
        
        try:
            response = requests.post(
                self.openrouter_url,
                headers=headers,
                json=payload,
                timeout=180
            )
            
            if response.status_code != 200:
                print(f"✗ OpenRouter API error: {response.status_code}")
                return None
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            lesson_content = json.loads(content)
            
            if not all(k in lesson_content for k in ["script_parts", "notes_exercises", "illustrations"]):
                print(f"✗ Missing required keys in response (need: script_parts, notes_exercises, illustrations)")
                return None
            
            return lesson_content
            
        except json.JSONDecodeError as e:
            print(f"✗ Failed to parse JSON response: {str(e)}")
            return None
        except Exception as e:
            print(f"✗ Lesson generation failed: {str(e)}")
            return None
    
    def save_lesson_files(self, output_path: Path, lesson_id: str, lesson_content: Dict, lesson_data: Dict) -> bool:
        """Save 3 separate files per lesson: Script.csv, Notes_Exercises.csv, Illustrations.json"""
        try:
            subject = lesson_data.get("Subject", "SUBJECT").replace(" ", "")
            grade_year_form = lesson_data.get("Grade", lesson_data.get("Year", lesson_data.get("Form", "GRADE"))).replace(" ", "")
            lesson_num = lesson_data.get("Lesson Number", lesson_id.replace("L", ""))
            
            base_filename = f"{subject}_{grade_year_form}_Lesson{lesson_num}"
            
            script_parts = lesson_content.get("script_parts", [])
            notes_exercises = lesson_content.get("notes_exercises", "")
            illustrations = lesson_content.get("illustrations", [])
            
            script_csv = output_path / f"{lesson_id}_Script.csv"
            with open(script_csv, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
                
                row = []
                row.append(self.format_csv_field(f"{base_filename}_Script.csv"))
                row.append(self.format_csv_field(base_filename))
                
                for part in script_parts:
                    heading = self.format_csv_field(part.get("heading", ""))
                    content = self.format_csv_field(part.get("content", ""))
                    row.append(heading)
                    row.append(content)
                
                writer.writerow(row)
            
            notes_csv = output_path / f"{lesson_id}_Notes_Exercises.csv"
            with open(notes_csv, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
                
                row = []
                row.append(self.format_csv_field(f"{base_filename}_Notes_Exercises.csv"))
                row.append(self.format_csv_field(base_filename))
                row.append(self.format_csv_field(notes_exercises))
                
                writer.writerow(row)
            
            illustrations_json = output_path / f"{lesson_id}_Illustrations.json"
            illustrations_output = {
                "lesson_id": lesson_id,
                "project_name": base_filename,
                "total_illustrations": len(illustrations),
                "illustrations": illustrations
            }
            
            with open(illustrations_json, 'w', encoding='utf-8') as f:
                json.dump(illustrations_output, f, indent=2)
            
            print(f"✓ Saved 3 files: {lesson_id}_Script.csv, {lesson_id}_Notes_Exercises.csv, {lesson_id}_Illustrations.json")
            return True
            
        except Exception as e:
            print(f"✗ Error saving lesson files: {str(e)}")
            return False
    
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
            lesson_id = lesson.get("Lesson Number", f"{i:03d}")
            if not lesson_id.startswith("L"):
                lesson_id = f"L{lesson_id}"
            
            print(f"\n[{i}/{total}] Generating lesson: {lesson_id}")
            
            print("🔄 Reloading directives and lesson mapping for accuracy...")
            curriculum_directive = self._reload_current_files(filename)
            
            lesson_content = self.generate_lesson_content(lesson, curriculum_directive)
            
            if lesson_content:
                if self.save_lesson_files(output_path, lesson_id, lesson_content, lesson):
                    results["successful"] += 1
                else:
                    results["failed"] += 1
            else:
                results["failed"] += 1
                print(f"✗ Failed to generate lesson {lesson_id}")
            
            print(f"Progress: {results['successful']}/{total} successful, {results['failed']} failed")
            time.sleep(2)
        
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
