# Hostel Room Counselling API

A FastAPI-based backend system for managing hostel room allocation using a dual-queue counselling system with Firebase Google Authentication. This API provides comprehensive endpoints for managing hostels, rooms, friendships, preferences, approvals, and the counselling process.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL (running via Docker)
- Firebase project with Google Sign-In enabled
- Required Python packages: `fastapi`, `uvicorn`, `psycopg2-binary`, `pydantic`, `firebase-admin`

### Setup

1. **Start PostgreSQL Database**
```bash
docker-compose up -d
```

2. **Configure Firebase Authentication**
- Download `serviceAccountKey.json` from Firebase Console
- Place it in the project root directory
- See [FIREBASE_SETUP.md](FIREBASE_SETUP.md) for detailed instructions

3. **Load Sample Data**
```bash
python load_sample_data.py
```

4. **Start the API Server**
```bash
python -m uvicorn api:app --reload --port 8000
```

5. **Access API Documentation**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📊 Database Configuration

- **Host:** localhost
- **Port:** 5432
- **Database:** room_counselling
- **Username:** admin
- **Password:** admin123

## 🔐 Firebase Authentication

The system uses Firebase Google Sign-In for user authentication. All authenticated endpoints require a Firebase ID token in the Authorization header.

### Frontend Integration Example

```javascript
// 1. User signs in with Google via Firebase (Frontend)
import { signInWithPopup, GoogleAuthProvider } from 'firebase/auth';

const signInWithGoogle = async () => {
  const provider = new GoogleAuthProvider();
  const result = await signInWithPopup(auth, provider);
  const user = result.user;
  
  // 2. Get Firebase ID token
  const idToken = await user.getIdToken();
  
  // 3. Send to backend
  const response = await fetch('http://localhost:8000/api/auth/firebase', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${idToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      firebaseUid: user.uid,
      email: user.email,
      displayName: user.displayName
    })
  });
  
  const data = await response.json();
  // data.data contains user profile from database
  
  // 4. Store token for future requests
  localStorage.setItem('firebaseToken', idToken);
};

// Making authenticated requests
const getUserProfile = async () => {
  const idToken = localStorage.getItem('firebaseToken');
  
  const response = await fetch('http://localhost:8000/api/auth/me', {
    headers: {
      'Authorization': `Bearer ${idToken}`
    }
  });
  
  return await response.json();
};
```

## 🏗️ System Architecture

The system implements a **dual-queue architecture** for fair room allocation:

1. **Turn Queue**: Users wait for their 30-second turn to select preferences
2. **Processing Queue**: Parallel processing of room assignments based on preferences and roommate approvals

## 📡 API Endpoints

### 🔐 Authentication Endpoints

#### Login/Register with Firebase
```http
POST /api/auth/firebase
```
Verify Firebase ID token and create/update user in database.

**Headers:**
```
Authorization: Bearer <firebase_id_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "firebaseUid": "abc123xyz...",
  "email": "student@example.com",
  "displayName": "John Doe"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "firebaseUid": "abc123xyz...",
    "email": "student@example.com",
    "displayName": "John Doe",
    "registrationNumber": null,
    "gender": "male",
    "rank": 1,
    "hostel": "mens",
    "isActive": true,
    "lastLoginAt": "2025-11-02T10:30:00",
    "createdAt": "2025-01-15T08:00:00"
  },
  "message": "User logged in successfully"
}
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "Invalid or expired token"
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "User not found. Please contact administrator to create your account first."
}
```

#### Get Current User Profile
```http
GET /api/auth/me
```
Get the authenticated user's profile information.

**Headers:**
```
Authorization: Bearer <firebase_id_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "firebaseUid": "abc123xyz...",
  "email": "student@example.com",
  "displayName": "John Doe",
  "registrationNumber": "2021CS001",
  "gender": "male",
  "rank": 1,
  "hostel": "mens",
  "isActive": true,
  "lastLoginAt": "2025-11-02T10:30:00",
  "createdAt": "2025-01-15T08:00:00"
}
```

#### Update User Profile
```http
PATCH /api/auth/me
```
Update the authenticated user's profile (registration number, display name).

**Headers:**
```
Authorization: Bearer <firebase_id_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "registrationNumber": "2021CS001",
  "displayName": "John Doe Updated"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "firebaseUid": "abc123xyz...",
  "email": "student@example.com",
  "displayName": "John Doe Updated",
  "registrationNumber": "2021CS001",
  "gender": "male",
  "rank": 1,
  "hostel": "mens",
  "isActive": true,
  "lastLoginAt": "2025-11-02T10:30:00",
  "createdAt": "2025-01-15T08:00:00"
}
```

#### Get User by Firebase UID
```http
GET /api/auth/user/{firebase_uid}
```
Get user details by Firebase UID (public endpoint, no authentication required).

**Parameters:**
- `firebase_uid` (string): Firebase user UID

**Response (200 OK):**
```json
{
  "id": 1,
  "firebaseUid": "abc123xyz...",
  "email": "student@example.com",
  "displayName": "John Doe",
  "registrationNumber": "2021CS001",
  "gender": "male",
  "rank": 1,
  "hostel": "mens",
  "isActive": true,
  "lastLoginAt": "2025-11-02T10:30:00",
  "createdAt": "2025-01-15T08:00:00"
}
```

---

### 🏨 Hostel Structure Management

#### Get All Hostels
```http
GET /api/hostels
```
Returns a list of all hostels in the system.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Mens Hostel Block A"
    }
  ],
  "count": 4
}
```

#### Get Hostel by ID
```http
GET /api/hostels/{hostel_id}
```
Returns detailed information about a specific hostel.

**Parameters:**
- `hostel_id` (integer): Hostel ID

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Mens Hostel Block A"
  }
}
```

#### Get Hostel Blocks
```http
GET /api/hostels/{hostel_id}/blocks
```
Returns all blocks within a specific hostel.

**Parameters:**
- `hostel_id` (integer): Hostel ID

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "hostelId": 1,
      "name": "Block A"
    }
  ],
  "count": 3
}
```

---

### 🏢 Block Management

#### Get Block by ID
```http
GET /api/blocks/{block_id}
```
Returns detailed information about a specific block.

**Parameters:**
- `block_id` (integer): Block ID

#### Get Block Floors
```http
GET /api/blocks/{block_id}/floors
```
Returns all floors within a specific block.

**Parameters:**
- `block_id` (integer): Block ID

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "blockId": 1,
      "floorNumber": 1
    }
  ],
  "count": 4
}
```

---

### 🏗️ Floor Management

#### Get Floor by ID
```http
GET /api/floors/{floor_id}
```
Returns detailed information about a specific floor.

**Parameters:**
- `floor_id` (integer): Floor ID

#### Get Floor Rooms
```http
GET /api/floors/{floor_id}/rooms
```
Returns all rooms on a specific floor.

**Parameters:**
- `floor_id` (integer): Floor ID

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "floorId": 1,
      "roomNumber": "101",
      "capacity": 4,
      "isAvailable": true
    }
  ],
  "count": 10
}
```

---

### 🚪 Room Management

#### Get Available Rooms
```http
GET /api/rooms/available
```
Returns all rooms that are currently available for allocation.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "roomNumber": "101",
      "capacity": 4,
      "isAvailable": true,
      "floorId": 1
    }
  ],
  "count": 0
}
```

#### Get Room by ID
```http
GET /api/rooms/{room_id}
```
Returns detailed information about a specific room.

**Parameters:**
- `room_id` (integer): Room ID

---

### 👥 Friendship Management

#### Get User Friends
```http
GET /api/friends/{user_id}
```
Returns all friendships for a user (both sent and received).

**Parameters:**
- `user_id` (integer): User ID

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "userId": 1,
      "friendId": 2,
      "status": "accepted",
      "createdAt": "2024-11-01T10:00:00"
    }
  ],
  "count": 2
}
```

#### Get Accepted Friends
```http
GET /api/friends/{user_id}/accepted
```
Returns only accepted friends for a user.

**Parameters:**
- `user_id` (integer): User ID

#### Get Friend Requests
```http
GET /api/friends/{user_id}/requests
```
Returns pending friend requests received by a user.

**Parameters:**
- `user_id` (integer): User ID

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "userId": 2,
      "friendId": 1,
      "status": "pending",
      "createdAt": "2024-11-01T10:00:00"
    }
  ],
  "count": 1
}
```

#### Send Friend Request
```http
POST /api/friends/request
```
Send a friend request to another user.

**Request Body:**
```json
{
  "userId": 1,
  "friendId": 2
}
```

**Response:**
```json
{
  "success": true,
  "message": "Friend request sent",
  "data": {
    "id": 1,
    "userId": 1,
    "friendId": 2,
    "status": "pending"
  }
}
```

#### Accept Friend Request
```http
PUT /api/friends/{friendship_id}/accept
```
Accept a pending friend request.

**Parameters:**
- `friendship_id` (integer): Friendship ID

#### Reject Friend Request
```http
PUT /api/friends/{friendship_id}/reject
```
Reject a pending friend request.

**Parameters:**
- `friendship_id` (integer): Friendship ID

#### Remove Friend
```http
DELETE /api/friends/{friendship_id}
```
Remove a friendship or cancel a friend request.

**Parameters:**
- `friendship_id` (integer): Friendship ID

---

### ⚙️ Preference Management

#### Get User Preferences
```http
GET /api/preferences/{user_id}
```
Returns all room preferences for a user.

**Parameters:**
- `user_id` (integer): User ID

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "userId": 1,
      "sessionId": 1,
      "roomId": 5,
      "priority": 1,
      "roommateUserIds": [2, 3],
      "createdAt": "2024-11-01T10:00:00"
    }
  ],
  "count": 5
}
```

#### Create Preference
```http
POST /api/preferences
```
Create a new room preference for a user.

**Request Body:**
```json
{
  "user_id": 1,
  "session_id": 1,
  "room_id": 5,
  "priority": 1,
  "roommate_user_ids": [2, 3]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Preference created",
  "data": {
    "id": 1,
    "userId": 1,
    "roomId": 5,
    "priority": 1
  }
}
```

#### Update Preference
```http
PUT /api/preferences/{preference_id}
```
Update an existing preference.

**Parameters:**
- `preference_id` (integer): Preference ID

**Request Body:**
```json
{
  "room_id": 10,
  "priority": 2,
  "roommate_user_ids": [3, 4]
}
```

#### Delete Preference
```http
DELETE /api/preferences/{preference_id}
```
Delete a preference.

**Parameters:**
- `preference_id` (integer): Preference ID

---

### ✅ Roommate Approval Management

#### Get User Approvals
```http
GET /api/approvals/{user_id}
```
Returns all approval requests (both sent and received) for a user.

**Parameters:**
- `user_id` (integer): User ID

**Response:**
```json
{
  "success": true,
  "data": {
    "sent": [
      {
        "id": 1,
        "requesterId": 1,
        "approverId": 2,
        "status": "pending",
        "requestedAt": "2024-11-01T10:00:00"
      }
    ],
    "received": []
  },
  "count": 1
}
```

#### Get Pending Approvals
```http
GET /api/approvals/{user_id}/pending
```
Returns pending approval requests that require the user's response.

**Parameters:**
- `user_id` (integer): User ID

#### Send Approval Request
```http
POST /api/approvals
```
Send a roommate approval request.

**Request Body:**
```json
{
  "requester_user_id": 1,
  "approver_user_id": 2,
  "session_id": 1,
  "room_id": 5
}
```

#### Approve Request
```http
PUT /api/approvals/{approval_id}/approve
```
Approve a roommate request.

**Parameters:**
- `approval_id` (integer): Approval ID

#### Reject Request
```http
PUT /api/approvals/{approval_id}/reject
```
Reject a roommate request.

**Parameters:**
- `approval_id` (integer): Approval ID

---

### 🛏️ Room Assignment Management

#### Get User Assignment
```http
GET /api/assignments/{user_id}
```
Returns the room assignment for a specific user.

**Parameters:**
- `user_id` (integer): User ID

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "userId": 1,
    "roomId": 5,
    "sessionId": 1,
    "assignedAt": "2024-11-01T10:00:00"
  }
}
```

#### Get Room Assignments
```http
GET /api/assignments/room/{room_id}
```
Returns all user assignments for a specific room.

**Parameters:**
- `room_id` (integer): Room ID

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "userId": 1,
      "roomId": 5,
      "assignedAt": "2024-11-01T10:00:00"
    }
  ],
  "count": 4
}
```

---

### 📅 Session Management

#### Get Current Session
```http
GET /api/session/current
```
Returns the currently active counselling session.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Fall 2024 Room Allocation",
    "status": "active",
    "turnDuration": 30,
    "startedAt": "2024-11-01T09:00:00"
  }
}
```

#### Get Session by ID
```http
GET /api/session/{session_id}
```
Returns details of a specific counselling session.

**Parameters:**
- `session_id` (integer): Session ID

---

### 🚦 Queue Management

#### Get Turn Position
```http
GET /api/queue/turn/{user_id}
```
Returns the turn queue position and status for a user.

**Parameters:**
- `user_id` (integer): User ID

**Response:**
```json
{
  "success": true,
  "data": {
    "userId": 1,
    "rank": 5,
    "status": "pending",
    "turnStartTime": null
  }
}
```

#### Get Processing Status
```http
GET /api/queue/processing/{user_id}
```
Returns the processing queue status for a user.

**Parameters:**
- `user_id` (integer): User ID

**Response:**
```json
{
  "success": true,
  "data": {
    "total": 50,
    "completed": 20,
    "processing": 5,
    "pending": 25
  },
  "message": "Overall queue status - user-specific status not yet implemented"
}
```

---

### 🔄 Legacy Queue Endpoints

These endpoints are maintained for backwards compatibility:

```http
POST /counselling-session/{session_id}/start
POST /counselling-session/{session_id}/pause
POST /counselling-session/{session_id}/resume
GET  /counselling-session/current
PATCH /counselling-session/{session_id}/rank

POST /queue/turn
GET  /queue/turn/{user_id}/position
PATCH /queue/turn/{user_id}/status
DELETE /queue/turn/{user_id}

POST /queue/processing
GET  /queue/processing/{user_id}/position
PATCH /queue/processing/{user_id}/status
DELETE /queue/processing/{user_id}

POST /roommate-approval/
POST /roommate-approval/{approval_id}/accept
POST /roommate-approval/{approval_id}/reject
GET  /roommate-approval/{user_id}/status
GET  /roommate-approval/{user_id}/pending

POST /preference/
PATCH /preference/{preference_id}
GET  /preference/{user_id}

POST /room-lock/
POST /room-lock/{lock_id}/unlock
GET  /room-lock/{room_id}/status
DELETE /room-lock/{lock_id}
```

---

## 🧪 Testing

### Run All Tests
```bash
python test_integrated_endpoints.py
```

### Test Specific Endpoints
```bash
python test_fixes.py
```

### Expected Test Results
```
✅ Passed: 25/25
📈 Success Rate: 100.0%
```

---

## 📦 Data Models

### User
- `id`: Integer (Primary Key)
- `name`: String
- `email`: String (Unique)
- `registrationNumber`: String (Unique)
- `rank`: Integer
- `isActive`: Boolean

### Hostel
- `id`: Integer (Primary Key)
- `name`: String

### Block
- `id`: Integer (Primary Key)
- `hostelId`: Integer (Foreign Key → Hostel)
- `name`: String

### Floor
- `id`: Integer (Primary Key)
- `blockId`: Integer (Foreign Key → Block)
- `floorNumber`: Integer

### Room
- `id`: Integer (Primary Key)
- `floorId`: Integer (Foreign Key → Floor)
- `roomNumber`: String
- `capacity`: Integer
- `isAvailable`: Boolean

### Friendship
- `id`: Integer (Primary Key)
- `userId`: Integer (Foreign Key → User)
- `friendId`: Integer (Foreign Key → User)
- `status`: Enum (pending, accepted, rejected)

### Preference
- `id`: Integer (Primary Key)
- `userId`: Integer (Foreign Key → User)
- `sessionId`: Integer (Foreign Key → CounsellingSession)
- `roomId`: Integer (Foreign Key → Room)
- `priority`: Integer
- `roommateUserIds`: Array of Integers

### RoommateApproval
- `id`: Integer (Primary Key)
- `preferenceId`: Integer (Foreign Key → Preference)
- `requesterId`: Integer (Foreign Key → User)
- `approverId`: Integer (Foreign Key → User)
- `status`: Enum (pending, approved, rejected, expired)

### RoomAssignment
- `id`: Integer (Primary Key)
- `roomId`: Integer (Foreign Key → Room)
- `userId`: Integer (Foreign Key → User)
- `sessionId`: Integer (Foreign Key → CounsellingSession)
- `assignedAt`: Timestamp

---

## 🛠️ Development

### Scalable Endpoint Generation

This project includes a scalable endpoint development framework:

```bash
# Generate new endpoints from specifications
python endpoint_generator.py

# Run the complete workflow
python workflow_master.py
```

See `README_DEVELOPMENT.md` for detailed development guidelines.

---

## 🐛 Error Handling

All endpoints return consistent error responses:

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "count": 10
}
```

### Error Response (4xx/5xx)
```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes
- `200 OK`: Successful request
- `404 Not Found`: Resource not found
- `400 Bad Request`: Invalid input data
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server-side error

---

## 📝 Sample Data

The system comes with pre-loaded sample data:
- 4 Hostels
- 12 Blocks
- 48 Floors
- 480 Rooms (10 rooms per floor)
- 60 Users
- 18 Friendships
- 75 Preferences
- 10 Room Assignments

Default password for all sample users: `password123`

---

## 🔐 Authentication

**Note:** Authentication is not yet implemented. All endpoints are currently publicly accessible. 

Planned features:
- JWT-based authentication
- Role-based access control (Student, Admin, Warden)
- Session-based security

---

## 📈 Performance

- **Response Time**: < 100ms for most GET requests
- **Concurrent Users**: Tested with 50+ simultaneous connections
- **Database Pooling**: Automatic connection management

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests to ensure 100% pass rate
5. Submit a pull request

---

## 📄 License

This project is part of the hostel-counselling-backend system.

---

## 📞 Support

For issues or questions:
- GitHub Issues: [hostel-counselling-backend/issues](https://github.com/ved-bankeshwar/hostel-counselling-backend/issues)
- Documentation: See `DEPLOYMENT_SUMMARY.md` for deployment details

---

## 🎯 Roadmap

- [ ] Implement authentication & authorization
- [ ] Add WebSocket support for real-time queue updates
- [ ] Implement room locking mechanism
- [ ] Add email notifications for approvals
- [ ] Create admin dashboard endpoints
- [ ] Add bulk operations for preferences
- [ ] Implement session scheduling system

---

**Built with FastAPI • PostgreSQL • Python 3.12**

*Last Updated: November 1, 2025*
