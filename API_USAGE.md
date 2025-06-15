# Hostel Counselling API Usage Examples

This file demonstrates how to use the Hostel Counselling API endpoints.

## Running the API

```bash
python hostel_app.py
```

The API will be available at: http://localhost:8000

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Example API Calls

### Users API

#### Create User
```bash
curl -X POST "http://localhost:8000/users/create" \
-H "Content-Type: application/json" \
-d '{
  "email": "student@example.com",
  "registration_number": "REG123",
  "name": "John Doe",
  "group": 1,
  "course": "Computer Science",
  "year_of_study": 2,
  "mobile_number": "1234567890"
}'
```

#### Read Users
```bash
curl -X POST "http://localhost:8000/users/read" \
-H "Content-Type: application/json" \
-d '{
  "course": "Computer Science",
  "limit": 10
}'
```

#### Update User
```bash
curl -X PUT "http://localhost:8000/users/update" \
-H "Content-Type: application/json" \
-d '{
  "user_id": "some-uuid-here",
  "is_alloted": true,
  "mobile_number": "9876543210"
}'
```

#### Delete User
```bash
curl -X DELETE "http://localhost:8000/users/delete" \
-H "Content-Type: application/json" \
-d '{
  "user_id": "some-uuid-here"
}'
```

### Blocks API

#### Create Block
```bash
curl -X POST "http://localhost:8000/blocks/create" \
-H "Content-Type: application/json" \
-d '{
  "block_letter": "A",
  "block_name": "Block A",
  "is_deluxe": false,
  "is_ac": true
}'
```

#### Read Blocks
```bash
curl -X POST "http://localhost:8000/blocks/read" \
-H "Content-Type: application/json" \
-d '{
  "is_ac": true
}'
```

### Rooms API

#### Create Room
```bash
curl -X POST "http://localhost:8000/rooms/create" \
-H "Content-Type: application/json" \
-d '{
  "room_number": "101",
  "block_name": "Block A",
  "block_letter": "A",
  "total_beds": 2,
  "floor_id": 1
}'
```

### Friends API

#### Create Friend Relationship
```bash
curl -X POST "http://localhost:8000/friends/create" \
-H "Content-Type: application/json" \
-d '{
  "user_id": "user1-uuid",
  "friend_id": "user2-uuid"
}'
```

### Allotments API

#### Create Allotment
```bash
curl -X POST "http://localhost:8000/allotments/create" \
-H "Content-Type: application/json" \
-d '{
  "user_id": "user1-uuid",
  "block_letter": "A",
  "room_number": "101",
  "is_alloted": true
}'
```

### Tenants API

#### Create Tenant
```bash
curl -X POST "http://localhost:8000/tenants/create" \
-H "Content-Type: application/json" \
-d '{
  "user_id": "user1-uuid",
  "room_number": "101",
  "block_letter": "A",
  "allotment_id": 1
}'
```

## Response Format

All endpoints return responses in this format:

```json
{
  "success": true,
  "data": {...},
  "error": null,
  "message": null
}
```

For errors:

```json
{
  "success": false,
  "data": null,
  "error": "Error message here",
  "message": null
}
```

## Available Endpoints

### Users (`/users`)
- POST `/users/create` - Create a new user
- POST `/users/read` - Read users with filters
- PUT `/users/update` - Update a user
- DELETE `/users/delete` - Delete a user

### Blocks (`/blocks`)
- POST `/blocks/create` - Create a new block
- POST `/blocks/read` - Read blocks with filters
- PUT `/blocks/update` - Update a block
- DELETE `/blocks/delete` - Delete a block

### Floors (`/floors`)
- POST `/floors/create` - Create a new floor
- POST `/floors/read` - Read floors with filters
- PUT `/floors/update` - Update a floor
- DELETE `/floors/delete` - Delete a floor

### Rooms (`/rooms`)
- POST `/rooms/create` - Create a new room
- POST `/rooms/read` - Read rooms with filters
- PUT `/rooms/update` - Update a room
- DELETE `/rooms/delete` - Delete a room

### Friends (`/friends`)
- POST `/friends/create` - Create a friend relationship
- POST `/friends/read` - Read friend relationships with filters
- PUT `/friends/update` - Update a friend relationship
- DELETE `/friends/delete` - Delete a friend relationship

### Allotments (`/allotments`)
- POST `/allotments/create` - Create a new allotment
- POST `/allotments/read` - Read allotments with filters
- PUT `/allotments/update` - Update an allotment
- DELETE `/allotments/delete` - Delete an allotment

### Tenants (`/tenants`)
- POST `/tenants/create` - Create a new tenant
- POST `/tenants/read` - Read tenants with filters
- PUT `/tenants/update` - Update a tenant
- DELETE `/tenants/delete` - Delete a tenant

## Health Check

```bash
curl -X GET "http://localhost:8000/health"
```

This will test the database connection and return the service status.
