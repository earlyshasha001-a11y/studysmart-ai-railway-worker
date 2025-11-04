import os
import sys
import requests
import time
from typing import Optional, Dict, Any


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


def main():
    """Main entry point"""
    # Check for project token first (preferred method)
    project_token = os.getenv("RAILWAY_PROJECT_TOKEN")
    project_id = os.getenv("RAILWAY_PROJECT_ID")
    
    if project_token and project_id:
        print("✓ Using RAILWAY_PROJECT_TOKEN (project-specific token)")
        controller = RailwayController(project_token, project_id=project_id, use_project_token=True)
    else:
        # Fallback to account token
        account_token = os.getenv("RAILWAY_API_KEY2") or os.getenv("RAILWAY_API_KEY")
        
        if not account_token:
            print("\n❌ ERROR: No Railway token found in environment")
            print("\n📝 Option 1 - Project Token (Recommended):")
            print("   1. Go to your Railway project settings")
            print("   2. Go to 'Tokens' tab")
            print("   3. Create a new project token")
            print("   4. Add to Replit Secrets:")
            print("      RAILWAY_PROJECT_TOKEN: (your token)")
            print("      RAILWAY_PROJECT_ID: (your project ID)")
            print("\n📝 Option 2 - Account Token:")
            print("   1. Go to https://railway.app/account/tokens")
            print("   2. Create a new account token")
            print("   3. Add to Secrets as RAILWAY_API_KEY")
            sys.exit(1)
        
        if os.getenv("RAILWAY_API_KEY2"):
            print("✓ Using RAILWAY_API_KEY2")
        else:
            print("✓ Using RAILWAY_API_KEY")
        
        controller = RailwayController(account_token, project_id=project_id)
        
        workspace_id = os.getenv("RAILWAY_WORKSPACE_ID")
        if workspace_id:
            controller.workspace_id = workspace_id
            print(f"✓ Loaded workspace ID from secrets")
    
    success = controller.run_deployment()
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
