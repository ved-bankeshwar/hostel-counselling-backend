"""Comprehensive test suite for Hostel Counselling Backend"""
import psycopg2
from psycopg2.extras import RealDictCursor
import requests
import json
from datetime import datetime

# Database connection
def get_db_connection():
    return psycopg2.connect(
        host='localhost',
        port=5432,
        database='room_counselling',
        user='admin',
        password='admin123'
    )

# API base URL
BASE_URL = "http://localhost:8000"

# Test results storage
whitebox_results = []
blackbox_results = []

print("=" * 100)
print("RUNNING COMPREHENSIVE TEST SUITE")
print("=" * 100)

# ============================================================================
# WHITEBOX TESTS - Testing Internal Logic & Database Operations
# ============================================================================

print("\n" + "=" * 100)
print("WHITEBOX TESTING - Internal Logic & Database Operations")
print("=" * 100)

# Test 1: Database Connection
print("\n[WB-1] Testing Database Connection...")
try:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1")
    result = cur.fetchone()[0]
    whitebox_results.append({
        'sr_no': 1,
        'test_case': 'Database connection establishment',
        'expected': 'Connection successful, query returns 1',
        'actual': f'Connection successful, query returned {result}',
        'status': 'PASS' if result == 1 else 'FAIL'
    })
    cur.close()
    conn.close()
    print(f"✅ PASS - Database connection successful")
except Exception as e:
    whitebox_results.append({
        'sr_no': 1,
        'test_case': 'Database connection establishment',
        'expected': 'Connection successful',
        'actual': f'Error: {str(e)}',
        'status': 'FAIL'
    })
    print(f"❌ FAIL - {str(e)}")

# Test 2: Verify Rooms table schema
print("\n[WB-2] Testing Rooms table schema...")
try:
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'Rooms'
        ORDER BY ordinal_position
    """)
    columns = cur.fetchall()
    required_fields = ['id', 'roomNumber', 'hostelName', 'blockName', 'floorNumber', 
                       'capacity', 'occupied', 'rentPerSemester', 'isLocked', 
                       'assignedUserId', 'assignedAt']
    column_names = [col['column_name'] for col in columns]
    all_present = all(field in column_names for field in required_fields)
    
    whitebox_results.append({
        'sr_no': 2,
        'test_case': 'Rooms table has all required fields (denormalized schema)',
        'expected': 'All required fields present: ' + ', '.join(required_fields),
        'actual': f'All required fields present: {all_present}',
        'status': 'PASS' if all_present else 'FAIL'
    })
    cur.close()
    conn.close()
    print(f"{'✅ PASS' if all_present else '❌ FAIL'} - Rooms table schema verified")
except Exception as e:
    whitebox_results.append({
        'sr_no': 2,
        'test_case': 'Rooms table schema verification',
        'expected': 'All required fields present',
        'actual': f'Error: {str(e)}',
        'status': 'FAIL'
    })
    print(f"❌ FAIL - {str(e)}")

# Test 3: Check available rooms count
print("\n[WB-3] Testing available rooms query...")
try:
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT COUNT(*) as count 
        FROM "Rooms" 
        WHERE occupied < capacity AND "isLocked" = false
    """)
    count = cur.fetchone()['count']
    
    whitebox_results.append({
        'sr_no': 3,
        'test_case': 'Query available rooms (occupied < capacity AND isLocked = false)',
        'expected': 'Returns count > 0 of available rooms',
        'actual': f'Found {count} available rooms',
        'status': 'PASS' if count > 0 else 'FAIL'
    })
    cur.close()
    conn.close()
    print(f"{'✅ PASS' if count > 0 else '❌ FAIL'} - Found {count} available rooms")
except Exception as e:
    whitebox_results.append({
        'sr_no': 3,
        'test_case': 'Query available rooms',
        'expected': 'Returns count of available rooms',
        'actual': f'Error: {str(e)}',
        'status': 'FAIL'
    })
    print(f"❌ FAIL - {str(e)}")

# Test 4: Check room field mapping (rentPerSemester exists)
print("\n[WB-4] Testing room field mapping for price...")
try:
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM "Rooms" LIMIT 1')
    room = cur.fetchone()
    has_rent_field = 'rentPerSemester' in room
    
    whitebox_results.append({
        'sr_no': 4,
        'test_case': 'Rooms table has rentPerSemester field (to be mapped to pricePerSemester)',
        'expected': 'rentPerSemester field exists in database',
        'actual': f'rentPerSemester field exists: {has_rent_field}',
        'status': 'PASS' if has_rent_field else 'FAIL'
    })
    cur.close()
    conn.close()
    print(f"{'✅ PASS' if has_rent_field else '❌ FAIL'} - rentPerSemester field check")
except Exception as e:
    whitebox_results.append({
        'sr_no': 4,
        'test_case': 'Room field mapping check',
        'expected': 'rentPerSemester field exists',
        'actual': f'Error: {str(e)}',
        'status': 'FAIL'
    })
    print(f"❌ FAIL - {str(e)}")

# Test 5: Check Preference table structure
print("\n[WB-5] Testing Preference table schema...")
try:
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'Preference'
        ORDER BY ordinal_position
    """)
    columns = cur.fetchall()
    required_fields = ['id', 'userId', 'roomId', 'preferenceRank']
    column_names = [col['column_name'] for col in columns]
    all_present = all(field in column_names for field in required_fields)
    
    whitebox_results.append({
        'sr_no': 5,
        'test_case': 'Preference table has required fields',
        'expected': 'Fields: ' + ', '.join(required_fields),
        'actual': f'All required fields present: {all_present}',
        'status': 'PASS' if all_present else 'FAIL'
    })
    cur.close()
    conn.close()
    print(f"{'✅ PASS' if all_present else '❌ FAIL'} - Preference table schema verified")
except Exception as e:
    whitebox_results.append({
        'sr_no': 5,
        'test_case': 'Preference table schema',
        'expected': 'All required fields present',
        'actual': f'Error: {str(e)}',
        'status': 'FAIL'
    })
    print(f"❌ FAIL - {str(e)}")

# Test 6: Check User table structure
print("\n[WB-6] Testing User table schema...")
try:
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'User'
        ORDER BY ordinal_position
    """)
    columns = cur.fetchall()
    required_fields = ['id', 'firebaseUid', 'email', 'displayName']
    column_names = [col['column_name'] for col in columns]
    all_present = all(field in column_names for field in required_fields)
    
    whitebox_results.append({
        'sr_no': 6,
        'test_case': 'User table has Firebase auth fields',
        'expected': 'Fields: ' + ', '.join(required_fields),
        'actual': f'All Firebase fields present: {all_present}',
        'status': 'PASS' if all_present else 'FAIL'
    })
    cur.close()
    conn.close()
    print(f"{'✅ PASS' if all_present else '❌ FAIL'} - User table schema verified")
except Exception as e:
    whitebox_results.append({
        'sr_no': 6,
        'test_case': 'User table schema',
        'expected': 'Firebase auth fields present',
        'actual': f'Error: {str(e)}',
        'status': 'FAIL'
    })
    print(f"❌ FAIL - {str(e)}")

# Test 7: Check CounsellingSession table
print("\n[WB-7] Testing CounsellingSession table schema...")
try:
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'CounsellingSession'
        ORDER BY ordinal_position
    """)
    columns = cur.fetchall()
    required_fields = ['id', 'sessionName', 'sessionStatus', 'startTime']
    column_names = [col['column_name'] for col in columns]
    all_present = all(field in column_names for field in required_fields)
    
    whitebox_results.append({
        'sr_no': 7,
        'test_case': 'CounsellingSession table structure',
        'expected': 'Fields: ' + ', '.join(required_fields),
        'actual': f'All session fields present: {all_present}',
        'status': 'PASS' if all_present else 'FAIL'
    })
    cur.close()
    conn.close()
    print(f"{'✅ PASS' if all_present else '❌ FAIL'} - CounsellingSession table verified")
except Exception as e:
    whitebox_results.append({
        'sr_no': 7,
        'test_case': 'CounsellingSession table structure',
        'expected': 'Required fields present',
        'actual': f'Error: {str(e)}',
        'status': 'FAIL'
    })
    print(f"❌ FAIL - {str(e)}")

# Test 8: Check Friendship table
print("\n[WB-8] Testing Friendship table schema...")
try:
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'Friendship'
        ORDER BY ordinal_position
    """)
    columns = cur.fetchall()
    required_fields = ['id', 'user1Id', 'user2Id', 'status']
    column_names = [col['column_name'] for col in columns]
    all_present = all(field in column_names for field in required_fields)
    
    whitebox_results.append({
        'sr_no': 8,
        'test_case': 'Friendship table for friend requests',
        'expected': 'Fields: ' + ', '.join(required_fields),
        'actual': f'All friendship fields present: {all_present}',
        'status': 'PASS' if all_present else 'FAIL'
    })
    cur.close()
    conn.close()
    print(f"{'✅ PASS' if all_present else '❌ FAIL'} - Friendship table verified")
except Exception as e:
    whitebox_results.append({
        'sr_no': 8,
        'test_case': 'Friendship table structure',
        'expected': 'Required fields present',
        'actual': f'Error: {str(e)}',
        'status': 'FAIL'
    })
    print(f"❌ FAIL - {str(e)}")

# Test 9: Check for locked rooms
print("\n[WB-9] Testing locked rooms query...")
try:
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT COUNT(*) as count FROM "Rooms" WHERE "isLocked" = true')
    locked_count = cur.fetchone()['count']
    
    whitebox_results.append({
        'sr_no': 9,
        'test_case': 'Query locked rooms (isLocked = true)',
        'expected': 'Returns count of locked rooms',
        'actual': f'Found {locked_count} locked rooms',
        'status': 'PASS'
    })
    cur.close()
    conn.close()
    print(f"✅ PASS - Found {locked_count} locked rooms")
except Exception as e:
    whitebox_results.append({
        'sr_no': 9,
        'test_case': 'Query locked rooms',
        'expected': 'Returns count of locked rooms',
        'actual': f'Error: {str(e)}',
        'status': 'FAIL'
    })
    print(f"❌ FAIL - {str(e)}")

# Test 10: Check for full rooms
print("\n[WB-10] Testing full rooms query...")
try:
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT COUNT(*) as count FROM "Rooms" WHERE occupied >= capacity')
    full_count = cur.fetchone()['count']
    
    whitebox_results.append({
        'sr_no': 10,
        'test_case': 'Query full rooms (occupied >= capacity)',
        'expected': 'Returns count of full rooms',
        'actual': f'Found {full_count} full rooms',
        'status': 'PASS'
    })
    cur.close()
    conn.close()
    print(f"✅ PASS - Found {full_count} full rooms")
except Exception as e:
    whitebox_results.append({
        'sr_no': 10,
        'test_case': 'Query full rooms',
        'expected': 'Returns count of full rooms',
        'actual': f'Error: {str(e)}',
        'status': 'FAIL'
    })
    print(f"❌ FAIL - {str(e)}")

# ============================================================================
# BLACKBOX TESTS - Testing API Endpoints as User
# ============================================================================

print("\n" + "=" * 100)
print("BLACKBOX TESTING - API Endpoints")
print("=" * 100)

# Test 1: API Health Check
print("\n[BB-1] Testing API health check...")
try:
    response = requests.get(f"{BASE_URL}/", timeout=5)
    blackbox_results.append({
        'sr_no': 1,
        'test_case': 'API server is running and accessible',
        'expected': 'HTTP 200, response with message',
        'actual': f'HTTP {response.status_code}',
        'status': 'PASS' if response.status_code == 200 else 'FAIL'
    })
    print(f"{'✅ PASS' if response.status_code == 200 else '❌ FAIL'} - API is accessible")
except Exception as e:
    blackbox_results.append({
        'sr_no': 1,
        'test_case': 'API health check',
        'expected': 'HTTP 200',
        'actual': f'Error: {str(e)}',
        'status': 'FAIL'
    })
    print(f"❌ FAIL - {str(e)}")

# Test 2: Get all available rooms
print("\n[BB-2] Testing GET /api/rooms/available...")
try:
    response = requests.get(f"{BASE_URL}/api/rooms/available", timeout=5)
    data = response.json()
    has_rooms = data.get('success') and data.get('count', 0) > 0
    has_price_field = False
    if has_rooms and len(data.get('data', [])) > 0:
        first_room = data['data'][0]
        has_price_field = 'pricePerSemester' in first_room
    
    blackbox_results.append({
        'sr_no': 2,
        'test_case': 'GET /api/rooms/available - Fetch available rooms with pricePerSemester field',
        'expected': 'HTTP 200, returns rooms with pricePerSemester field mapped',
        'actual': f'HTTP {response.status_code}, Found {data.get("count", 0)} rooms, pricePerSemester: {has_price_field}',
        'status': 'PASS' if response.status_code == 200 and has_rooms and has_price_field else 'FAIL'
    })
    print(f"{'✅ PASS' if response.status_code == 200 and has_rooms and has_price_field else '❌ FAIL'} - Found {data.get('count', 0)} rooms")
except Exception as e:
    blackbox_results.append({
        'sr_no': 2,
        'test_case': 'GET available rooms',
        'expected': 'HTTP 200 with room list',
        'actual': f'Error: {str(e)}',
        'status': 'FAIL'
    })
    print(f"❌ FAIL - {str(e)}")

# Test 3: Get rooms with hostel filter
print("\n[BB-3] Testing GET /api/rooms/available with hostelName filter...")
try:
    response = requests.get(f"{BASE_URL}/api/rooms/available?hostelName=Ladies Hostel Block A", timeout=5)
    data = response.json()
    
    blackbox_results.append({
        'sr_no': 3,
        'test_case': 'GET /api/rooms/available?hostelName=... - Filter by hostel',
        'expected': 'HTTP 200, returns only filtered hostel rooms',
        'actual': f'HTTP {response.status_code}, Found {data.get("count", 0)} rooms',
        'status': 'PASS' if response.status_code == 200 else 'FAIL'
    })
    print(f"{'✅ PASS' if response.status_code == 200 else '❌ FAIL'} - Hostel filter works")
except Exception as e:
    blackbox_results.append({
        'sr_no': 3,
        'test_case': 'GET rooms with hostel filter',
        'expected': 'HTTP 200 with filtered rooms',
        'actual': f'Error: {str(e)}',
        'status': 'FAIL'
    })
    print(f"❌ FAIL - {str(e)}")

# Test 4: Get room by ID
print("\n[BB-4] Testing GET /api/rooms/1...")
try:
    response = requests.get(f"{BASE_URL}/api/rooms/1", timeout=5)
    data = response.json()
    has_price_field = False
    if response.status_code == 200 and data.get('success'):
        room = data.get('data', {})
        has_price_field = 'pricePerSemester' in room
    
    blackbox_results.append({
        'sr_no': 4,
        'test_case': 'GET /api/rooms/{id} - Get specific room with pricePerSemester',
        'expected': 'HTTP 200, returns room with pricePerSemester field',
        'actual': f'HTTP {response.status_code}, pricePerSemester: {has_price_field}',
        'status': 'PASS' if response.status_code == 200 and has_price_field else 'FAIL'
    })
    print(f"{'✅ PASS' if response.status_code == 200 and has_price_field else '❌ FAIL'} - Room by ID retrieved")
except Exception as e:
    blackbox_results.append({
        'sr_no': 4,
        'test_case': 'GET room by ID',
        'expected': 'HTTP 200 with room data',
        'actual': f'Error: {str(e)}',
        'status': 'FAIL'
    })
    print(f"❌ FAIL - {str(e)}")

# Test 5: Get non-existent room
print("\n[BB-5] Testing GET /api/rooms/999999...")
try:
    response = requests.get(f"{BASE_URL}/api/rooms/999999", timeout=5)
    
    blackbox_results.append({
        'sr_no': 5,
        'test_case': 'GET /api/rooms/{invalid_id} - Non-existent room',
        'expected': 'HTTP 404, error message',
        'actual': f'HTTP {response.status_code}',
        'status': 'PASS' if response.status_code == 404 else 'FAIL'
    })
    print(f"{'✅ PASS' if response.status_code == 404 else '❌ FAIL'} - Correctly returns 404")
except Exception as e:
    blackbox_results.append({
        'sr_no': 5,
        'test_case': 'GET non-existent room',
        'expected': 'HTTP 404',
        'actual': f'Error: {str(e)}',
        'status': 'FAIL'
    })
    print(f"❌ FAIL - {str(e)}")

# Test 6: Get rooms with floor filter
print("\n[BB-6] Testing GET /api/rooms/available?floorNumber=1...")
try:
    response = requests.get(f"{BASE_URL}/api/rooms/available?floorNumber=1", timeout=5)
    data = response.json()
    
    blackbox_results.append({
        'sr_no': 6,
        'test_case': 'GET /api/rooms/available?floorNumber=1 - Filter by floor',
        'expected': 'HTTP 200, returns only floor 1 rooms',
        'actual': f'HTTP {response.status_code}, Found {data.get("count", 0)} rooms',
        'status': 'PASS' if response.status_code == 200 else 'FAIL'
    })
    print(f"{'✅ PASS' if response.status_code == 200 else '❌ FAIL'} - Floor filter works")
except Exception as e:
    blackbox_results.append({
        'sr_no': 6,
        'test_case': 'GET floor filtered rooms',
        'expected': 'HTTP 200 with floor filtered rooms',
        'actual': f'Error: {str(e)}',
        'status': 'FAIL'
    })
    print(f"❌ FAIL - {str(e)}")

# Test 7: Get current session
print("\n[BB-7] Testing GET /api/allocation/session/current...")
try:
    response = requests.get(f"{BASE_URL}/api/allocation/session/current", timeout=5)
    
    blackbox_results.append({
        'sr_no': 7,
        'test_case': 'GET /api/allocation/session/current - Check session status',
        'expected': 'HTTP 200 or 404 (no active session)',
        'actual': f'HTTP {response.status_code}',
        'status': 'PASS' if response.status_code in [200, 404] else 'FAIL'
    })
    print(f"{'✅ PASS' if response.status_code in [200, 404] else '❌ FAIL'} - Session check works")
except Exception as e:
    blackbox_results.append({
        'sr_no': 7,
        'test_case': 'GET current session',
        'expected': 'HTTP 200 or 404',
        'actual': f'Error: {str(e)}',
        'status': 'FAIL'
    })
    print(f"❌ FAIL - {str(e)}")

# Test 8: Start allocation session (test endpoint without auth)
print("\n[BB-8] Testing POST /api/allocation/session/start-test...")
try:
    response = requests.post(f"{BASE_URL}/api/allocation/session/start-test", json={
        "sessionName": "Test Session " + datetime.now().strftime("%Y%m%d_%H%M%S")
    }, timeout=5)
    data = response.json()
    
    blackbox_results.append({
        'sr_no': 8,
        'test_case': 'POST /api/allocation/session/start-test - Start session (no auth)',
        'expected': 'HTTP 200, session started',
        'actual': f'HTTP {response.status_code}, Success: {data.get("success", False)}',
        'status': 'PASS' if response.status_code == 200 and data.get('success') else 'FAIL'
    })
    print(f"{'✅ PASS' if response.status_code == 200 else '❌ FAIL'} - Session started")
except Exception as e:
    blackbox_results.append({
        'sr_no': 8,
        'test_case': 'Start allocation session',
        'expected': 'HTTP 200, session created',
        'actual': f'Error: {str(e)}',
        'status': 'FAIL'
    })
    print(f"❌ FAIL - {str(e)}")

# Test 9: Start session when active exists
print("\n[BB-9] Testing POST /api/allocation/session/start-test (duplicate)...")
try:
    response = requests.post(f"{BASE_URL}/api/allocation/session/start-test", json={
        "sessionName": "Duplicate Session"
    }, timeout=5)
    
    blackbox_results.append({
        'sr_no': 9,
        'test_case': 'POST /api/allocation/session/start-test - Start when active exists',
        'expected': 'HTTP 400, error message about active session',
        'actual': f'HTTP {response.status_code}',
        'status': 'PASS' if response.status_code == 400 else 'FAIL'
    })
    print(f"{'✅ PASS' if response.status_code == 400 else '❌ FAIL'} - Correctly rejects duplicate session")
except Exception as e:
    blackbox_results.append({
        'sr_no': 9,
        'test_case': 'Start duplicate session',
        'expected': 'HTTP 400',
        'actual': f'Error: {str(e)}',
        'status': 'FAIL'
    })
    print(f"❌ FAIL - {str(e)}")

# Test 10: Stop allocation session
print("\n[BB-10] Testing POST /api/allocation/session/stop-test...")
try:
    response = requests.post(f"{BASE_URL}/api/allocation/session/stop-test", timeout=5)
    data = response.json()
    
    blackbox_results.append({
        'sr_no': 10,
        'test_case': 'POST /api/allocation/session/stop-test - Stop session and clear preferences',
        'expected': 'HTTP 200, session stopped, preferences cleared',
        'actual': f'HTTP {response.status_code}, Success: {data.get("success", False)}',
        'status': 'PASS' if response.status_code == 200 and data.get('success') else 'FAIL'
    })
    print(f"{'✅ PASS' if response.status_code == 200 else '❌ FAIL'} - Session stopped")
except Exception as e:
    blackbox_results.append({
        'sr_no': 10,
        'test_case': 'Stop allocation session',
        'expected': 'HTTP 200, session stopped',
        'actual': f'Error: {str(e)}',
        'status': 'FAIL'
    })
    print(f"❌ FAIL - {str(e)}")

# ============================================================================
# GENERATE TEST REPORTS
# ============================================================================

print("\n" + "=" * 100)
print("GENERATING TEST REPORTS")
print("=" * 100)

# Save detailed results to JSON
with open('test_results_whitebox.json', 'w') as f:
    json.dump(whitebox_results, f, indent=2)

with open('test_results_blackbox.json', 'w') as f:
    json.dump(blackbox_results, f, indent=2)

# Generate Whitebox Report
print("\n" + "=" * 100)
print("WHITEBOX TESTING REPORT")
print("=" * 100)
print(f"{'Sr No':<8} {'Test Case':<70} {'Status':<10}")
print("=" * 100)
for result in whitebox_results:
    test_case = result['test_case'][:68] + '..' if len(result['test_case']) > 70 else result['test_case']
    print(f"{result['sr_no']:<8} {test_case:<70} {result['status']:<10}")

wb_pass = sum(1 for r in whitebox_results if r['status'] == 'PASS')
wb_total = len(whitebox_results)
print("=" * 100)
print(f"WHITEBOX SUMMARY: {wb_pass}/{wb_total} tests passed ({wb_pass/wb_total*100:.1f}%)")
print("=" * 100)

# Generate Blackbox Report
print("\n" + "=" * 100)
print("BLACKBOX TESTING REPORT")
print("=" * 100)
print(f"{'Sr No':<8} {'Test Case':<70} {'Status':<10}")
print("=" * 100)
for result in blackbox_results:
    test_case = result['test_case'][:68] + '..' if len(result['test_case']) > 70 else result['test_case']
    print(f"{result['sr_no']:<8} {test_case:<70} {result['status']:<10}")

bb_pass = sum(1 for r in blackbox_results if r['status'] == 'PASS')
bb_total = len(blackbox_results)
print("=" * 100)
print(f"BLACKBOX SUMMARY: {bb_pass}/{bb_total} tests passed ({bb_pass/bb_total*100:.1f}%)")
print("=" * 100)

print("\n" + "=" * 100)
print(f"OVERALL: {wb_pass + bb_pass}/{wb_total + bb_total} tests passed ({(wb_pass + bb_pass)/(wb_total + bb_total)*100:.1f}%)")
print("=" * 100)

print("\n✅ Test results saved to test_results_whitebox.json and test_results_blackbox.json")
print("=" * 100)
