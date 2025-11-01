"""
Scalable Endpoint Implementation System
Generates endpoint code, tests, and documentation automatically
"""

import os
from typing import Dict, List, Any
from dataclasses import dataclass, field

@dataclass
class EndpointSpec:
    """Specification for a single API endpoint"""
    path: str
    method: str  # GET, POST, PUT, DELETE, PATCH
    function_name: str
    crud_module: str
    crud_function: str
    description: str
    tags: List[str]
    path_params: List[str] = field(default_factory=list)
    query_params: List[str] = field(default_factory=list)
    request_model: str = None
    response_model: str = None
    auth_required: bool = False
    admin_only: bool = False

class EndpointBatchGenerator:
    """Generate multiple endpoints and their tests in batches"""
    
    def __init__(self, output_dir: str = "."):
        self.output_dir = output_dir
        self.endpoints = []
        
    def add_endpoint_batch(self, category: str, specs: List[EndpointSpec]):
        """Add a batch of related endpoints"""
        for spec in specs:
            self.endpoints.append((category, spec))
    
    def generate_api_code(self) -> str:
        """Generate FastAPI code for all endpoints"""
        code_sections = {}
        
        for category, spec in self.endpoints:
            if category not in code_sections:
                code_sections[category] = []
            
            # Generate endpoint code
            endpoint_code = self._generate_single_endpoint(spec)
            code_sections[category].append(endpoint_code)
        
        # Combine all sections
        full_code = ""
        for category, codes in code_sections.items():
            full_code += f"\n# ==================== {category} Endpoints ====================\n\n"
            full_code += "\n\n".join(codes)
        
        return full_code
    
    def _generate_single_endpoint(self, spec: EndpointSpec) -> str:
        """Generate code for a single endpoint"""
        # Build parameters
        params = []
        for param in spec.path_params:
            params.append(f"{param}: int")
        for param in spec.query_params:
            params.append(f"{param}: str = None")
        if spec.request_model:
            params.append(f"data: {spec.request_model}")
        
        param_str = ", ".join(params) if params else ""
        
        # Build CRUD function call
        crud_call_params = []
        for param in spec.path_params:
            crud_call_params.append(param)
        if spec.request_model:
            crud_call_params.append("data.dict()")
        
        crud_call = f"{spec.crud_module}.{spec.crud_function}({', '.join(crud_call_params)})" if crud_call_params else f"{spec.crud_module}.{spec.crud_function}()"
        
        # Generate code
        code = f'''@app.{spec.method.lower()}("{spec.path}", tags={spec.tags})
def {spec.function_name}({param_str}):
    """{spec.description}"""
    try:
        result = {crud_call}
        return {{"success": True, "data": result}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))'''
        
        return code
    
    def generate_test_code(self) -> str:
        """Generate test code for all endpoints"""
        test_code = '''"""Auto-generated endpoint tests"""
import requests
import pytest

BASE_URL = "http://localhost:8000"

'''
        for category, spec in self.endpoints:
            test_func = self._generate_single_test(spec, category)
            test_code += test_func + "\n\n"
        
        return test_code
    
    def _generate_single_test(self, spec: EndpointSpec, category: str) -> str:
        """Generate test function for a single endpoint"""
        test_name = f"test_{spec.function_name}"
        
        # Build test URL
        test_url = spec.path
        for param in spec.path_params:
            test_url = test_url.replace(f"{{{param}}}", "1")
        
        # Generate test
        if spec.method == "GET":
            test_code = f'''def {test_name}():
    """Test {spec.description}"""
    response = requests.get(f"{{BASE_URL}}{test_url}")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert data["success"] == True'''
        
        elif spec.method == "POST":
            payload = "{}"  # Default empty payload
            if spec.request_model:
                # Generate sample payload
                payload = '{"key": "value"}'  # Simplified
            
            test_code = f'''def {test_name}():
    """Test {spec.description}"""
    payload = {payload}
    response = requests.post(f"{{BASE_URL}}{test_url}", json=payload)
    assert response.status_code in [200, 201]
    data = response.json()
    assert "success" in data'''
        
        else:
            test_code = f'''def {test_name}():
    """Test {spec.description}"""
    response = requests.{spec.method.lower()}(f"{{BASE_URL}}{test_url}")
    assert response.status_code in [200, 204]'''
        
        return test_code
    
    def generate_documentation(self) -> str:
        """Generate markdown documentation"""
        doc = "# API Endpoints Documentation\n\n"
        
        # Group by category
        by_category = {}
        for category, spec in self.endpoints:
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(spec)
        
        # Generate docs
        for category, specs in by_category.items():
            doc += f"## {category}\n\n"
            for spec in specs:
                doc += f"### `{spec.method} {spec.path}`\n\n"
                doc += f"**Description:** {spec.description}\n\n"
                
                if spec.path_params:
                    doc += f"**Path Parameters:**\n"
                    for param in spec.path_params:
                        doc += f"- `{param}` (integer)\n"
                    doc += "\n"
                
                if spec.request_model:
                    doc += f"**Request Body:** `{spec.request_model}`\n\n"
                
                doc += "**Response:**\n```json\n{\n  \"success\": true,\n  \"data\": {}\n}\n```\n\n"
                doc += "---\n\n"
        
        return doc
    
    def save_all(self):
        """Save generated code, tests, and docs"""
        # Save API code snippet
        api_code = self.generate_api_code()
        with open(os.path.join(self.output_dir, "generated_endpoints.py"), "w") as f:
            f.write(api_code)
        print(f"✅ Generated API code: generated_endpoints.py")
        
        # Save test code
        test_code = self.generate_test_code()
        with open(os.path.join(self.output_dir, "generated_tests.py"), "w") as f:
            f.write(test_code)
        print(f"✅ Generated test code: generated_tests.py")
        
        # Save documentation
        docs = self.generate_documentation()
        with open(os.path.join(self.output_dir, "GENERATED_API_DOCS.md"), "w") as f:
            f.write(docs)
        print(f"✅ Generated documentation: GENERATED_API_DOCS.md")


# ==================== Endpoint Specifications ====================

def define_all_endpoints() -> EndpointBatchGenerator:
    """Define all API endpoints for the system"""
    generator = EndpointBatchGenerator()
    
    # Friendship Endpoints
    friendship_specs = [
        EndpointSpec(
            path="/api/friends/{user_id}",
            method="GET",
            function_name="get_user_friends",
            crud_module="friendship",
            crud_function="get_friendships_by_user_id",
            description="Get all friends for a user",
            tags=["Friendship"],
            path_params=["user_id"]
        ),
        EndpointSpec(
            path="/api/friends/{user_id}/accepted",
            method="GET",
            function_name="get_accepted_friends",
            crud_module="friendship",
            crud_function="get_accepted_friends",
            description="Get accepted friends only",
            tags=["Friendship"],
            path_params=["user_id"]
        ),
        EndpointSpec(
            path="/api/friends/{user_id}/requests",
            method="GET",
            function_name="get_friend_requests",
            crud_module="friendship",
            crud_function="get_friendships_by_user_id",
            description="Get pending friend requests",
            tags=["Friendship"],
            path_params=["user_id"]
        ),
        EndpointSpec(
            path="/api/friends/request",
            method="POST",
            function_name="send_friend_request",
            crud_module="friendship",
            crud_function="create_friendship",
            description="Send a friend request",
            tags=["Friendship"],
            request_model="FriendshipRequest"
        ),
        EndpointSpec(
            path="/api/friends/{friendship_id}/accept",
            method="PUT",
            function_name="accept_friend_request",
            crud_module="friendship",
            crud_function="update_friendship",
            description="Accept a friend request",
            tags=["Friendship"],
            path_params=["friendship_id"]
        ),
        EndpointSpec(
            path="/api/friends/{friendship_id}/reject",
            method="PUT",
            function_name="reject_friend_request",
            crud_module="friendship",
            crud_function="update_friendship",
            description="Reject a friend request",
            tags=["Friendship"],
            path_params=["friendship_id"]
        ),
        EndpointSpec(
            path="/api/friends/{friendship_id}",
            method="DELETE",
            function_name="remove_friend",
            crud_module="friendship",
            crud_function="delete_friendship",
            description="Remove a friend",
            tags=["Friendship"],
            path_params=["friendship_id"]
        ),
    ]
    
    # Hostel Structure Endpoints
    hostel_specs = [
        EndpointSpec(
            path="/api/hostels",
            method="GET",
            function_name="get_all_hostels",
            crud_module="hostel",
            crud_function="get_all_hostels",
            description="Get all hostels",
            tags=["Hostel"]
        ),
        EndpointSpec(
            path="/api/hostels/{hostel_id}",
            method="GET",
            function_name="get_hostel_by_id",
            crud_module="hostel",
            crud_function="get_hostel_by_id",
            description="Get hostel details by ID",
            tags=["Hostel"],
            path_params=["hostel_id"]
        ),
        EndpointSpec(
            path="/api/hostels/{hostel_id}/blocks",
            method="GET",
            function_name="get_hostel_blocks",
            crud_module="block",
            crud_function="get_all_blocks",
            description="Get all blocks in a hostel",
            tags=["Hostel"],
            path_params=["hostel_id"]
        ),
    ]
    
    # Block Endpoints
    block_specs = [
        EndpointSpec(
            path="/api/blocks/{block_id}",
            method="GET",
            function_name="get_block_by_id",
            crud_module="block",
            crud_function="get_block_by_id",
            description="Get block details by ID",
            tags=["Block"],
            path_params=["block_id"]
        ),
        EndpointSpec(
            path="/api/blocks/{block_id}/floors",
            method="GET",
            function_name="get_block_floors",
            crud_module="floor",
            crud_function="get_all_floors",
            description="Get all floors in a block",
            tags=["Block"],
            path_params=["block_id"]
        ),
    ]
    
    # Floor Endpoints
    floor_specs = [
        EndpointSpec(
            path="/api/floors/{floor_id}",
            method="GET",
            function_name="get_floor_by_id",
            crud_module="floor",
            crud_function="get_floor_by_id",
            description="Get floor details by ID",
            tags=["Floor"],
            path_params=["floor_id"]
        ),
        EndpointSpec(
            path="/api/floors/{floor_id}/rooms",
            method="GET",
            function_name="get_floor_rooms",
            crud_module="room",
            crud_function="get_all_rooms",
            description="Get all rooms on a floor",
            tags=["Floor"],
            path_params=["floor_id"]
        ),
    ]
    
    # Room Endpoints
    room_specs = [
        EndpointSpec(
            path="/api/rooms/{room_id}",
            method="GET",
            function_name="get_room_by_id",
            crud_module="room",
            crud_function="get_room_by_id",
            description="Get room details by ID",
            tags=["Room"],
            path_params=["room_id"]
        ),
        EndpointSpec(
            path="/api/rooms/available",
            method="GET",
            function_name="get_available_rooms",
            crud_module="room",
            crud_function="get_all_rooms",
            description="Get all available rooms with optional filters",
            tags=["Room"]
        ),
    ]
    
    # Session Endpoints
    session_specs = [
        EndpointSpec(
            path="/api/session/current",
            method="GET",
            function_name="get_current_session",
            crud_module="counselling_session",
            crud_function="get_active_session",
            description="Get the current active counselling session",
            tags=["Session"]
        ),
        EndpointSpec(
            path="/api/session/{session_id}",
            method="GET",
            function_name="get_session_by_id",
            crud_module="counselling_session",
            crud_function="get_session_by_id",
            description="Get session details by ID",
            tags=["Session"],
            path_params=["session_id"]
        ),
    ]
    
    # Preference Endpoints
    preference_specs = [
        EndpointSpec(
            path="/api/preferences/{user_id}",
            method="GET",
            function_name="get_user_preferences",
            crud_module="preference",
            crud_function="get_preferences_by_user_id",
            description="Get all preferences for a user",
            tags=["Preference"],
            path_params=["user_id"]
        ),
        EndpointSpec(
            path="/api/preferences",
            method="POST",
            function_name="create_preference",
            crud_module="preference",
            crud_function="create_preference",
            description="Create a new preference",
            tags=["Preference"],
            request_model="PreferenceCreate"
        ),
        EndpointSpec(
            path="/api/preferences/{preference_id}",
            method="PUT",
            function_name="update_preference",
            crud_module="preference",
            crud_function="update_preference",
            description="Update a preference",
            tags=["Preference"],
            path_params=["preference_id"],
            request_model="PreferenceUpdate"
        ),
        EndpointSpec(
            path="/api/preferences/{preference_id}",
            method="DELETE",
            function_name="delete_preference",
            crud_module="preference",
            crud_function="delete_preference",
            description="Delete a preference",
            tags=["Preference"],
            path_params=["preference_id"]
        ),
    ]
    
    # Roommate Approval Endpoints
    approval_specs = [
        EndpointSpec(
            path="/api/approvals/{user_id}",
            method="GET",
            function_name="get_user_approvals",
            crud_module="roommate_approval",
            crud_function="get_approvals_by_user_id",
            description="Get all approvals for a user",
            tags=["Approval"],
            path_params=["user_id"]
        ),
        EndpointSpec(
            path="/api/approvals/{user_id}/pending",
            method="GET",
            function_name="get_pending_approvals",
            crud_module="roommate_approval",
            crud_function="get_pending_approvals_for_user",
            description="Get pending approvals for a user",
            tags=["Approval"],
            path_params=["user_id"]
        ),
        EndpointSpec(
            path="/api/approvals",
            method="POST",
            function_name="send_approval_request",
            crud_module="roommate_approval",
            crud_function="create_approval",
            description="Send a roommate approval request",
            tags=["Approval"],
            request_model="ApprovalRequest"
        ),
        EndpointSpec(
            path="/api/approvals/{approval_id}/approve",
            method="PUT",
            function_name="approve_request",
            crud_module="roommate_approval",
            crud_function="update_approval_status",
            description="Approve a roommate request",
            tags=["Approval"],
            path_params=["approval_id"]
        ),
        EndpointSpec(
            path="/api/approvals/{approval_id}/reject",
            method="PUT",
            function_name="reject_request",
            crud_module="roommate_approval",
            crud_function="update_approval_status",
            description="Reject a roommate request",
            tags=["Approval"],
            path_params=["approval_id"]
        ),
    ]
    
    # Room Assignment Endpoints
    assignment_specs = [
        EndpointSpec(
            path="/api/assignments/{user_id}",
            method="GET",
            function_name="get_user_assignment",
            crud_module="room_assignment",
            crud_function="get_assignment_by_user_id",
            description="Get room assignment for a user",
            tags=["Assignment"],
            path_params=["user_id"]
        ),
        EndpointSpec(
            path="/api/assignments/room/{room_id}",
            method="GET",
            function_name="get_room_assignments",
            crud_module="room_assignment",
            crud_function="get_assignments_by_room_id",
            description="Get all assignments for a room",
            tags=["Assignment"],
            path_params=["room_id"]
        ),
    ]
    
    # Queue Endpoints
    queue_specs = [
        EndpointSpec(
            path="/api/queue/turn/{user_id}",
            method="GET",
            function_name="get_turn_position",
            crud_module="queue_management",
            crud_function="get_turn_queue_entry_by_user",
            description="Get turn queue position for a user",
            tags=["Queue"],
            path_params=["user_id"]
        ),
        EndpointSpec(
            path="/api/queue/processing/{user_id}",
            method="GET",
            function_name="get_processing_status",
            crud_module="queue_management",
            crud_function="get_processing_queue_entry_by_user",
            description="Get processing queue status for a user",
            tags=["Queue"],
            path_params=["user_id"]
        ),
    ]
    
    # Add all batches
    generator.add_endpoint_batch("Friendship", friendship_specs)
    generator.add_endpoint_batch("Hostel", hostel_specs)
    generator.add_endpoint_batch("Block", block_specs)
    generator.add_endpoint_batch("Floor", floor_specs)
    generator.add_endpoint_batch("Room", room_specs)
    generator.add_endpoint_batch("Session", session_specs)
    generator.add_endpoint_batch("Preference", preference_specs)
    generator.add_endpoint_batch("Approval", approval_specs)
    generator.add_endpoint_batch("Assignment", assignment_specs)
    generator.add_endpoint_batch("Queue", queue_specs)
    
    return generator


if __name__ == "__main__":
    print("🏗️  Scalable Endpoint Implementation System")
    print("="*70)
    
    # Generate all endpoints
    generator = define_all_endpoints()
    
    print(f"\n📊 Total Endpoints Defined: {len(generator.endpoints)}")
    print("\n🔨 Generating code, tests, and documentation...")
    
    generator.save_all()
    
    print("\n✅ All files generated successfully!")
    print("\n📝 Next steps:")
    print("  1. Review generated_endpoints.py")
    print("  2. Copy relevant sections to api.py")
    print("  3. Run generated_tests.py to validate")
    print("  4. Check GENERATED_API_DOCS.md for documentation")
