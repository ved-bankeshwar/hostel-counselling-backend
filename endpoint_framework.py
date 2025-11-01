"""
Endpoint Development Framework
This script helps develop, test, and validate API endpoints systematically at scale
"""

import subprocess
import time
import requests
import json
import sys
from typing import Dict, List, Any, Callable
from dataclasses import dataclass
from enum import Enum

class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"

@dataclass
class EndpointTest:
    """Represents a single endpoint test case"""
    name: str
    method: HTTPMethod
    url: str
    payload: Dict[str, Any] = None
    headers: Dict[str, str] = None
    expected_status: int = 200
    description: str = ""
    
class EndpointTestRunner:
    """Runs and validates API endpoint tests"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = []
        
    def run_test(self, test: EndpointTest) -> Dict[str, Any]:
        """Run a single test and return results"""
        print(f"\n🧪 Testing: {test.name}")
        print(f"   Method: {test.method.value} {test.url}")
        if test.description:
            print(f"   Description: {test.description}")
        
        try:
            url = f"{self.base_url}{test.url}"
            headers = test.headers or {}
            
            if test.method == HTTPMethod.GET:
                response = requests.get(url, headers=headers, timeout=5)
            elif test.method == HTTPMethod.POST:
                response = requests.post(url, json=test.payload, headers=headers, timeout=5)
            elif test.method == HTTPMethod.PUT:
                response = requests.put(url, json=test.payload, headers=headers, timeout=5)
            elif test.method == HTTPMethod.DELETE:
                response = requests.delete(url, headers=headers, timeout=5)
            elif test.method == HTTPMethod.PATCH:
                response = requests.patch(url, json=test.payload, headers=headers, timeout=5)
            
            success = response.status_code == test.expected_status
            
            result = {
                "test_name": test.name,
                "success": success,
                "status_code": response.status_code,
                "expected_status": test.expected_status,
                "response": response.json() if response.text else None,
                "url": url
            }
            
            if success:
                print(f"   ✅ PASS - Status: {response.status_code}")
            else:
                print(f"   ❌ FAIL - Expected: {test.expected_status}, Got: {response.status_code}")
            
            self.results.append(result)
            return result
            
        except requests.exceptions.ConnectionError:
            print(f"   ❌ ERROR - Server not responding")
            return {"test_name": test.name, "success": False, "error": "Connection Error"}
        except Exception as e:
            print(f"   ❌ ERROR - {str(e)}")
            return {"test_name": test.name, "success": False, "error": str(e)}
    
    def run_test_suite(self, tests: List[EndpointTest], suite_name: str = "Test Suite"):
        """Run multiple tests and generate report"""
        print(f"\n{'='*70}")
        print(f"🚀 Running {suite_name}")
        print(f"{'='*70}")
        
        for test in tests:
            self.run_test(test)
            time.sleep(0.1)  # Small delay between tests
        
        self.print_summary()
    
    def print_summary(self):
        """Print test results summary"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.get("success"))
        failed = total - passed
        
        print(f"\n{'='*70}")
        print(f"📊 Test Summary")
        print(f"{'='*70}")
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "N/A")
        print(f"{'='*70}\n")
        
        return {"total": total, "passed": passed, "failed": failed}

class APICodeGenerator:
    """Generates FastAPI endpoint code from specifications"""
    
    @staticmethod
    def generate_endpoint_code(
        path: str,
        method: str,
        function_name: str,
        crud_function: str,
        description: str,
        tags: List[str],
        request_model: str = None,
        path_params: List[str] = None
    ) -> str:
        """Generate FastAPI endpoint code"""
        
        # Build function signature
        params = []
        if path_params:
            for param in path_params:
                params.append(f"{param}: int")
        if request_model:
            params.append(f"data: {request_model}")
        
        param_str = ", ".join(params) if params else ""
        
        # Build decorator
        decorator = f'@app.{method.lower()}("{path}", tags={tags})'
        
        # Build function
        code = f'''
{decorator}
def {function_name}({param_str}):
    """{description}"""
    try:
        result = {crud_function}
        return {{"success": True, "data": result}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
'''
        return code
    
    @staticmethod
    def generate_pydantic_model(model_name: str, fields: Dict[str, str]) -> str:
        """Generate Pydantic model code"""
        field_lines = []
        for field_name, field_type in fields.items():
            field_lines.append(f'    {field_name}: {field_type}')
        
        fields_str = '\n'.join(field_lines)
        
        return f'''
class {model_name}(BaseModel):
{fields_str}
'''

def check_server_health(base_url: str = "http://localhost:8000") -> bool:
    """Check if API server is running"""
    try:
        response = requests.get(f"{base_url}/docs", timeout=2)
        return response.status_code == 200
    except:
        return False

def start_server_background(port: int = 8000) -> subprocess.Popen:
    """Start API server in background"""
    print(f"🚀 Starting API server on port {port}...")
    process = subprocess.Popen(
        ["python", "-m", "uvicorn", "api:app", "--port", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(3)  # Wait for server to start
    return process

def create_endpoint_specification() -> Dict[str, List[Dict[str, Any]]]:
    """Define all endpoint specifications for the system"""
    
    specs = {
        "Friendship": [
            {
                "path": "/api/friends/{user_id}",
                "method": "GET",
                "function_name": "get_user_friends",
                "crud_module": "friendship",
                "crud_function": "get_friendships_by_user_id(user_id)",
                "description": "Get all friends for a user",
                "path_params": ["user_id"]
            },
            {
                "path": "/api/friends/request",
                "method": "POST",
                "function_name": "send_friend_request",
                "crud_module": "friendship",
                "crud_function": "create_friendship(data.dict())",
                "description": "Send a friend request",
                "request_model": "FriendshipRequest"
            },
        ],
        "Hostel": [
            {
                "path": "/api/hostels",
                "method": "GET",
                "function_name": "get_all_hostels",
                "crud_module": "hostel",
                "crud_function": "get_all_hostels()",
                "description": "Get all hostels"
            },
            {
                "path": "/api/hostels/{hostel_id}",
                "method": "GET",
                "function_name": "get_hostel_by_id",
                "crud_module": "hostel",
                "crud_function": "get_hostel_by_id(hostel_id)",
                "description": "Get hostel details by ID",
                "path_params": ["hostel_id"]
            },
        ],
        # Add more categories here...
    }
    
    return specs

if __name__ == "__main__":
    print("🏗️  Endpoint Development Framework")
    print("=" * 70)
    
    # Check if server is running
    if not check_server_health():
        print("❌ Server is not running. Please start it with:")
        print("   python -m uvicorn api:app --port 8000")
        sys.exit(1)
    
    print("✅ Server is running and healthy!\n")
    
    # Example: Test friendship endpoints
    runner = EndpointTestRunner()
    
    friendship_tests = [
        EndpointTest(
            name="Get Friends for User 1",
            method=HTTPMethod.GET,
            url="/api/friends/1",
            expected_status=200,
            description="Should return all friendships for user 1"
        ),
        EndpointTest(
            name="Send Friend Request",
            method=HTTPMethod.POST,
            url="/api/friends/request",
            payload={"userId": 1, "friendId": 2},
            expected_status=200,
            description="User 1 sends request to User 2"
        ),
        EndpointTest(
            name="Send Friend Request to Self (Should Fail)",
            method=HTTPMethod.POST,
            url="/api/friends/request",
            payload={"userId": 1, "friendId": 1},
            expected_status=400,
            description="Should fail - cannot friend yourself"
        ),
    ]
    
    runner.run_test_suite(friendship_tests, "Friendship Endpoints")
