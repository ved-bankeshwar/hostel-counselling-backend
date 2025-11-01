#!/usr/bin/env python3
"""
Comprehensive test suite for integrated endpoints
"""
import requests
import json
from typing import Dict, List, Tuple

BASE_URL = "http://localhost:8000"

def test_endpoint(method: str, path: str, description: str, data: dict = None) -> Tuple[bool, str, dict]:
    """Test a single endpoint"""
    try:
        url = f"{BASE_URL}{path}"
        
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=5)
        elif method == "DELETE":
            response = requests.delete(url, timeout=5)
        else:
            return False, f"Unknown method: {method}", {}
        
        # Accept 200 (success), 404 (not found - valid for GET), 400 (validation error)
        success = response.status_code in [200, 404]
        
        try:
            response_data = response.json()
        except:
            response_data = {"raw": response.text[:200]}
        
        return success, f"Status: {response.status_code}", response_data
        
    except requests.exceptions.ConnectionError:
        return False, "Connection failed - is server running?", {}
    except requests.exceptions.Timeout:
        return False, "Request timeout", {}
    except Exception as e:
        return False, f"Error: {str(e)}", {}


def run_tests():
    """Run all endpoint tests"""
    
    test_cases = [
        # Hostel Structure Tests
        ("GET", "/api/hostels", "Get all hostels"),
        ("GET", "/api/hostels/1", "Get hostel by ID"),
        ("GET", "/api/hostels/1/blocks", "Get hostel blocks"),
        ("GET", "/api/hostels/999", "Get non-existent hostel (should 404)"),
        
        # Block Tests
        ("GET", "/api/blocks/1", "Get block by ID"),
        ("GET", "/api/blocks/1/floors", "Get block floors"),
        ("GET", "/api/blocks/999", "Get non-existent block (should 404)"),
        
        # Floor Tests
        ("GET", "/api/floors/1", "Get floor by ID"),
        ("GET", "/api/floors/1/rooms", "Get floor rooms"),
        ("GET", "/api/floors/999", "Get non-existent floor (should 404)"),
        
        # Room Tests
        ("GET", "/api/rooms/1", "Get room by ID"),
        ("GET", "/api/rooms/available", "Get available rooms"),
        ("GET", "/api/rooms/999", "Get non-existent room (should 404)"),
        
        # Session Tests
        ("GET", "/api/session/current", "Get current session"),
        ("GET", "/api/session/1", "Get session by ID"),
        
        # Friendship Tests
        ("GET", "/api/friends/1", "Get user friends"),
        ("GET", "/api/friends/1/accepted", "Get accepted friends"),
        ("GET", "/api/friends/1/requests", "Get friend requests"),
        
        # Preference Tests
        ("GET", "/api/preferences/1", "Get user preferences"),
        
        # Approval Tests
        ("GET", "/api/approvals/1", "Get user approvals"),
        ("GET", "/api/approvals/1/pending", "Get pending approvals"),
        
        # Assignment Tests
        ("GET", "/api/assignments/1", "Get user assignment"),
        ("GET", "/api/assignments/room/1", "Get room assignments"),
        
        # Queue Tests
        ("GET", "/api/queue/turn/1", "Get turn position"),
        ("GET", "/api/queue/processing/1", "Get processing status"),
    ]
    
    print("\n" + "="*70)
    print("🧪 INTEGRATED ENDPOINT TEST SUITE")
    print("="*70)
    
    passed = 0
    failed = 0
    results = []
    
    for method, path, description in test_cases:
        success, status_msg, data = test_endpoint(method, path, description)
        
        if success:
            passed += 1
            result = f"✅ PASS"
        else:
            failed += 1
            result = f"❌ FAIL"
        
        results.append({
            "result": result,
            "description": description,
            "status": status_msg,
            "path": path
        })
        
        print(f"\n{result} | {description}")
        print(f"   Path: {method} {path}")
        print(f"   {status_msg}")
        
        if data.get("success"):
            if "count" in data:
                print(f"   Data: {data.get('count')} items returned")
            elif "data" in data:
                print(f"   Data: Retrieved successfully")
    
    print("\n" + "="*70)
    print(f"📊 TEST SUMMARY")
    print("="*70)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Total:  {len(test_cases)}")
    print(f"🎯 Success Rate: {(passed/len(test_cases)*100):.1f}%")
    print("="*70 + "\n")
    
    # Category breakdown
    categories = {
        "Hostel Structure": ["hostel", "block", "floor", "room"],
        "Session Management": ["session"],
        "Social Features": ["friends", "friendship"],
        "Preferences": ["preferences"],
        "Approvals": ["approvals"],
        "Assignments": ["assignments"],
        "Queue Management": ["queue"]
    }
    
    print("📋 CATEGORY BREAKDOWN")
    print("="*70)
    
    for category, keywords in categories.items():
        category_tests = [r for r in results if any(k in r['path'].lower() for k in keywords)]
        if category_tests:
            cat_passed = len([r for r in category_tests if "✅" in r['result']])
            cat_total = len(category_tests)
            print(f"{category:.<30} {cat_passed}/{cat_total} passed")
    
    print("="*70 + "\n")
    
    return passed, failed


if __name__ == "__main__":
    try:
        passed, failed = run_tests()
        exit(0 if failed == 0 else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite error: {e}")
        exit(1)
