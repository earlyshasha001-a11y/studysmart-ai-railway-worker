import os
import sys
import requests
import time
from typing import Optional, Dict, Any


class RailwayController:
    """Simple Railway API automation controller"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://backboard.railway.app/graphql/v2"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.workspace_id = None
        self.project_id = None
        self.service_id = None
    
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
                
                workspace_id = self.get_workspace_id()
                if workspace_id:
                    self.workspace_id = workspace_id
                
                return True
            else:
                print("✗ Failed to authenticate with Railway API")
                return False
        except Exception as e:
            print(f"✗ Connection test failed: {str(e)}")
            return False
    
    def create_project(self, project_name: str = "StudySmart-AI-Worker") -> Optional[str]:
        """Create a new Railway project"""
        query = """
        mutation ProjectCreate($input: ProjectCreateInput!) {
            projectCreate(input: $input) {
                project {
                    id
                    name
                }
            }
        }
        """
        
        input_data = {"name": project_name}
        
        if self.workspace_id:
            input_data["workspaceId"] = self.workspace_id
        
        variables = {"input": input_data}
        
        try:
            data = self._execute_query(query, variables)
            project = data.get("projectCreate", {}).get("project", {})
            
            if project and project.get("id"):
                self.project_id = project["id"]
                print(f"✓ Created project: {project.get('name')} (ID: {self.project_id})")
                return self.project_id
            else:
                print("✗ Failed to create project")
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
    
    def run_deployment(self) -> bool:
        """Main deployment workflow"""
        print("\n" + "="*60)
        print("  Railway Automation Controller - StudySmart AI Worker")
        print("="*60 + "\n")
        
        print("Step 1: Testing Railway API connection...")
        if not self.test_connection():
            print("\n❌ Cannot proceed without valid Railway connection")
            print("   Please check your RAILWAY_API_KEY in Secrets")
            return False
        
        print("\nStep 2: Introspecting Railway schema...")
        self.introspect_user_type()
        self.introspect_project_input()
        
        print("\nStep 3: Listing existing projects...")
        self.list_projects()
        
        print("\nStep 4: Creating new project 'StudySmart-AI-Worker'...")
        project_id = self.create_project("StudySmart-AI-Worker")
        
        if not project_id:
            print("\n❌ Failed to create project")
            return False
        
        print("\nStep 5: Creating worker service...")
        service_id = self.create_service(project_id, "lesson-worker")
        
        if not service_id:
            print("\n⚠️  Project created but service creation failed")
            print(f"   You can manually add a service to project: {project_id}")
            return False
        
        print("\nStep 6: Verifying deployment...")
        project_info = self.get_project_info(project_id)
        
        if project_info:
            print(f"✓ Project verified: {project_info.get('name')}")
            services = project_info.get('services', {}).get('edges', [])
            print(f"  Services: {len(services)} active")
        
        print("\n" + "="*60)
        print("  ✅ Railway Connection Established Successfully!")
        print("="*60)
        print(f"\n📍 Project ID: {project_id}")
        print(f"📍 Service ID: {service_id}")
        print(f"\n🔗 Dashboard: https://railway.app/project/{project_id}")
        print("\n💡 Next steps:")
        print("   1. Add your StudySmart AI lesson directives")
        print("   2. Upload curriculum JSON files")
        print("   3. Configure worker deployment settings")
        print("\n" + "="*60 + "\n")
        
        return True


def main():
    """Main entry point"""
    api_key = os.getenv("RAILWAY_API_KEY")
    
    if not api_key:
        print("\n❌ ERROR: RAILWAY_API_KEY not found in environment")
        print("\n📝 Please add your Railway API key to Replit Secrets:")
        print("   1. Click on 'Tools' in the left sidebar")
        print("   2. Select 'Secrets'")
        print("   3. Add: RAILWAY_API_KEY = your_api_key_here")
        print("\n   Get your API key from: https://railway.app/account/tokens")
        sys.exit(1)
    
    controller = RailwayController(api_key)
    success = controller.run_deployment()
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
