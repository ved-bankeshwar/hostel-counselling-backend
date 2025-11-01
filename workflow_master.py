"""
Master Endpoint Development Workflow
Automates the entire process: Generate -> Integrate -> Test -> Validate
"""

import subprocess
import time
import os
import sys

class EndpointDevelopmentWorkflow:
    """Manages the complete endpoint development lifecycle"""
    
    def __init__(self):
        self.server_process = None
        
    def step1_generate_endpoints(self):
        """Generate endpoint code, tests, and docs"""
        print("\n" + "="*70)
        print("📝 STEP 1: Generating Endpoint Code")
        print("="*70)
        
        result = subprocess.run(
            ["python", "endpoint_generator.py"],
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            return False
        return True
    
    def step2_show_generated_code(self):
        """Display generated code for review"""
        print("\n" + "="*70)
        print("👀 STEP 2: Review Generated Code")
        print("="*70)
        
        if os.path.exists("generated_endpoints.py"):
            print("\n📄 Generated Endpoints Preview:")
            with open("generated_endpoints.py", "r") as f:
                lines = f.readlines()[:50]  # Show first 50 lines
                print("".join(lines))
                if len(lines) >= 50:
                    print("\n... (file continues)")
            return True
        else:
            print("❌ generated_endpoints.py not found")
            return False
    
    def step3_integration_instructions(self):
        """Provide instructions for integrating generated code"""
        print("\n" + "="*70)
        print("🔧 STEP 3: Integration Instructions")
        print("="*70)
        
        print("""
To integrate the generated endpoints into your API:

1. Open api.py
2. Locate the section for the endpoint category (e.g., # Hostel Endpoints)
3. Copy the relevant functions from generated_endpoints.py
4. Paste them into api.py in the appropriate section
5. Save the file

Example:
  - For Hostel endpoints: Copy all @app.get("/api/hostels...") functions
  - For Block endpoints: Copy all @app.get("/api/blocks...") functions

The auto-reload feature will automatically restart the server.
        """)
        
        return True
    
    def step4_start_server(self):
        """Start the API server"""
        print("\n" + "="*70)
        print("🚀 STEP 4: Starting API Server")
        print("="*70)
        
        print("\nStarting server on http://localhost:8000...")
        print("Server will run in background. Press Ctrl+C in the server terminal to stop.")
        print("\n⚠️  Note: Start server manually with:")
        print("   python -m uvicorn api:app --reload --port 8000")
        print("\nWaiting 5 seconds for you to start the server...")
        time.sleep(5)
        
        return True
    
    def step5_test_endpoints(self):
        """Run endpoint tests"""
        print("\n" + "="*70)
        print("🧪 STEP 5: Testing Endpoints")
        print("="*70)
        
        # Check if server is running
        import requests
        try:
            response = requests.get("http://localhost:8000/docs", timeout=2)
            if response.status_code == 200:
                print("✅ Server is running!")
            else:
                print("❌ Server not responding correctly")
                return False
        except:
            print("❌ Server is not running. Please start it first.")
            return False
        
        print("\nRunning tests...")
        result = subprocess.run(
            ["python", "generated_tests.py"],
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(f"⚠️  Some tests may have failed: {result.stderr}")
        
        return True
    
    def step6_generate_report(self):
        """Generate final report"""
        print("\n" + "="*70)
        print("📊 STEP 6: Development Report")
        print("="*70)
        
        files_created = []
        if os.path.exists("generated_endpoints.py"):
            files_created.append("✅ generated_endpoints.py (API code)")
        if os.path.exists("generated_tests.py"):
            files_created.append("✅ generated_tests.py (Test suite)")
        if os.path.exists("GENERATED_API_DOCS.md"):
            files_created.append("✅ GENERATED_API_DOCS.md (Documentation)")
        
        print("\n📁 Files Created:")
        for file in files_created:
            print(f"  {file}")
        
        print("\n🎯 Workflow Complete!")
        print("\n📚 Next Steps:")
        print("  1. Review GENERATED_API_DOCS.md for API documentation")
        print("  2. Integrate more endpoints from generated_endpoints.py into api.py")
        print("  3. Run tests with: python generated_tests.py")
        print("  4. Access API docs at: http://localhost:8000/docs")
        
        return True
    
    def run_full_workflow(self):
        """Execute the complete workflow"""
        print("\n" + "="*70)
        print("🏗️  ENDPOINT DEVELOPMENT MASTER WORKFLOW")
        print("="*70)
        print("\nThis workflow will:")
        print("  1. Generate endpoint code")
        print("  2. Show preview of generated code")
        print("  3. Provide integration instructions")
        print("  4. Help you start the server")
        print("  5. Test the endpoints")
        print("  6. Generate final report")
        
        input("\n Press Enter to continue...")
        
        # Execute workflow steps
        if not self.step1_generate_endpoints():
            print("\n❌ Workflow failed at Step 1")
            return
        
        if not self.step2_show_generated_code():
            print("\n❌ Workflow failed at Step 2")
            return
        
        self.step3_integration_instructions()
        
        self.step4_start_server()
        
        # self.step5_test_endpoints()  # Optional - requires server running
        
        self.step6_generate_report()
        
        print("\n" + "="*70)
        print("✅ Workflow Complete!")
        print("="*70)

def quick_test_single_endpoint():
    """Quick test for a single endpoint"""
    import requests
    
    print("\n🧪 Quick Endpoint Test")
    print("="*70)
    
    endpoint = input("Enter endpoint path (e.g., /api/friends/1): ").strip()
    method = input("Enter method (GET/POST/PUT/DELETE): ").strip().upper()
    
    try:
        if method == "GET":
            response = requests.get(f"http://localhost:8000{endpoint}")
        elif method == "POST":
            payload = input("Enter JSON payload (or press Enter for empty): ").strip()
            response = requests.post(f"http://localhost:8000{endpoint}", json=eval(payload) if payload else {})
        elif method == "PUT":
            payload = input("Enter JSON payload (or press Enter for empty): ").strip()
            response = requests.put(f"http://localhost:8000{endpoint}", json=eval(payload) if payload else {})
        elif method == "DELETE":
            response = requests.delete(f"http://localhost:8000{endpoint}")
        else:
            print("❌ Invalid method")
            return
        
        print(f"\n📊 Status Code: {response.status_code}")
        print(f"📄 Response:")
        try:
            import json
            print(json.dumps(response.json(), indent=2))
        except:
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Main entry point"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║   Scalable Endpoint Development System                          ║
║   Automate: Generate → Integrate → Test → Validate              ║
╚══════════════════════════════════════════════════════════════════╝
""")
    
    print("\nOptions:")
    print("  1. Run Full Workflow (Generate + Instructions + Report)")
    print("  2. Generate Endpoints Only")
    print("  3. Quick Test Single Endpoint")
    print("  4. Exit")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    workflow = EndpointDevelopmentWorkflow()
    
    if choice == "1":
        workflow.run_full_workflow()
    elif choice == "2":
        workflow.step1_generate_endpoints()
    elif choice == "3":
        quick_test_single_endpoint()
    elif choice == "4":
        print("\nExiting...")
        sys.exit(0)
    else:
        print("\n❌ Invalid option")

if __name__ == "__main__":
    main()
