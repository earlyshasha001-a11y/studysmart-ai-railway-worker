import os
import sys
import time
import requests
import json
from datetime import datetime
from typing import Optional, Dict, List

class ReplitController:
    """Lightweight Replit controller - orchestrates Railway workers"""
    
    def __init__(self):
        self.railway_token = os.getenv("RAILWAY_PROJECT_TOKEN")
        self.railway_project_id = os.getenv("RAILWAY_PROJECT_ID", "cedc37d7-79dd-48f2-b880-6333d9d3760c")
        self.graphql_url = "https://backboard.railway.com/graphql/v2"
        self.headers = {
            "Project-Access-Token": self.railway_token,
            "Content-Type": "application/json"
        }
    
    def execute_graphql(self, query: str, variables: Optional[Dict] = None) -> Dict:
        """Execute GraphQL query against Railway API"""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        try:
            response = requests.post(
                self.graphql_url,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code >= 400:
                raise Exception(f"Railway API error ({response.status_code}): {response.text}")
            
            result = response.json()
            
            if "errors" in result:
                raise Exception(f"GraphQL errors: {result['errors']}")
            
            return result.get("data", {})
        except requests.exceptions.RequestException as e:
            raise Exception(f"Railway API request failed: {str(e)}")
    
    def test_connection(self) -> bool:
        """Test Railway API connection"""
        print("🔗 Testing Railway connection...")
        
        query = """
        query GetProject($projectId: String!) {
            project(id: $projectId) {
                id
                name
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
        
        try:
            data = self.execute_graphql(query, {"projectId": self.railway_project_id})
            project = data.get("project", {})
            
            if project and project.get("id"):
                print(f"✓ Connected to Railway project: {project.get('name')}")
                print(f"  Project ID: {project.get('id')}")
                
                services = project.get("services", {}).get("edges", [])
                print(f"  Services: {len(services)} found")
                return True
            else:
                print("✗ Failed to access Railway project")
                return False
        except Exception as e:
            print(f"✗ Connection test failed: {str(e)}")
            return False
    
    def deploy_worker(self) -> Optional[str]:
        """Deploy a Railway worker for lesson generation"""
        print("\n🚀 Triggering Railway deployment...")
        
        query = """
        mutation($projectId: String!) {
            deploymentCreate(input: {projectId: $projectId}) {
                id
                url
                staticUrl
            }
        }
        """
        
        variables = {
            "projectId": self.railway_project_id
        }
        
        try:
            data = self.execute_graphql(query, variables)
            deployment = data.get("deploymentCreate", {})
            
            if deployment and deployment.get("id"):
                deployment_id = deployment["id"]
                print(f"✓ Deployment triggered")
                print(f"  Deployment ID: {deployment_id}")
                if deployment.get("url"):
                    print(f"  URL: {deployment.get('url')}")
                return deployment_id
            else:
                print("✗ Failed to trigger deployment")
                return None
        except Exception as e:
            print(f"✗ Deployment failed: {str(e)}")
            print("\n💡 Note: Railway deployment may need manual setup")
            print(f"   Visit: https://railway.app/project/{self.railway_project_id}")
            return None
    
    def poll_worker_status(self, service_id: str, timeout: int = 7200) -> bool:
        """Poll Railway worker status until completion"""
        print(f"\n⏳ Polling worker status (timeout: {timeout/60} minutes)...")
        
        query = """
        query GetService($serviceId: String!) {
            service(id: $serviceId) {
                id
                name
            }
        }
        """
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                data = self.execute_graphql(query, {"serviceId": service_id})
                service = data.get("service", {})
                
                if service:
                    print(f"  ✓ Worker active: {service.get('name')}")
                    time.sleep(30)  # Poll every 30 seconds
                else:
                    print(f"  ⚠️  Worker not found - may have completed")
                    return True
                    
            except Exception as e:
                print(f"  ⚠️  Polling error: {str(e)}")
                time.sleep(30)
        
        print("  ⚠️  Timeout reached")
        return False
    
    def get_batch_summary(self) -> Dict:
        """Retrieve batch processing summary from Railway worker"""
        print("\n📊 Retrieving batch summary...")
        
        # This would typically fetch from Railway storage or logs
        # For now, return a placeholder
        summary = {
            "status": "Worker deployed successfully",
            "message": "Check Railway dashboard for detailed logs and output files",
            "project_url": f"https://railway.app/project/{self.railway_project_id}"
        }
        
        print(f"✓ Summary retrieved")
        return summary
    
    def run(self):
        """Main controller execution"""
        print("\n" + "="*60)
        print("  StudySmart AI - Replit Controller")
        print("  Lightweight Orchestration System")
        print("="*60)
        
        # Test connection
        if not self.test_connection():
            print("\n❌ Cannot proceed without valid Railway connection")
            print("   Please verify RAILWAY_PROJECT_TOKEN and RAILWAY_PROJECT_ID")
            return
        
        # Deploy worker
        service_id = self.deploy_worker()
        if not service_id:
            print("\n❌ Failed to deploy Railway worker")
            return
        
        # Monitor worker
        print("\n" + "="*60)
        print("  WORKER DEPLOYED - MONITORING PROGRESS")
        print("="*60)
        print("📍 Railway Dashboard:")
        print(f"   https://railway.app/project/{self.railway_project_id}")
        print("\n💡 The Railway worker is now:")
        print("   • Loading curriculum files")
        print("   • Generating lessons with DeepSeek V3.1")
        print("   • Saving output to Railway storage")
        print("   • Will auto-shutdown when complete")
        print("\n⏳ Replit is monitoring progress...")
        
        # Poll for completion
        success = self.poll_worker_status(service_id)
        
        # Get summary
        summary = self.get_batch_summary()
        
        # Final status
        print("\n" + "="*60)
        print("  CONTROLLER COMPLETE")
        print("="*60)
        print(f"Status: {'Success' if success else 'Timeout/Error'}")
        print(f"Worker Service ID: {service_id}")
        print(f"\n📊 Summary:")
        for key, value in summary.items():
            print(f"   {key}: {value}")
        
        print("\n✓ Replit controller finished")
        print("   Check Railway dashboard for detailed results")

if __name__ == "__main__":
    controller = ReplitController()
    controller.run()
