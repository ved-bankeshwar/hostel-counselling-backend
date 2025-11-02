# Hostel Sample Data

This document describes the sample hostel data loaded into the database.

## Summary Statistics

- **Total Hostels:** 11
- **Total Blocks:** 41
- **Total Floors:** 197
- **Total Rooms:** 7,600
- **Total Bed Capacity:** 22,879 beds

## Hostels

### Men's Hostels (7)
1. **Mens Hostel Block A** (Original)
2. **Mens Hostel Block B** (Original)
3. **Vivekananda Hostel (Men)** - Named after Swami Vivekananda
4. **Ramanujan Hostel (Men)** - Named after mathematician Srinivasa Ramanujan
5. **Tagore Hostel (Men)** - Named after Rabindranath Tagore
6. **APJ Abdul Kalam Hostel (Men)** - Named after Dr. APJ Abdul Kalam
7. **Bhabha Hostel (Men)** *(If added in future)*

### Women's Hostels (4)
1. **Ladies Hostel Block A** (Original)
2. **Ladies Hostel Block B** (Original)
3. **Sarojini Naidu Hostel (Women)** - Named after Sarojini Naidu
4. **Indira Gandhi Hostel (Women)** - Named after Indira Gandhi
5. **Rani Lakshmibai Hostel (Women)** - Named after Rani Lakshmibai

## Block Types

Each hostel typically has 3-4 blocks with different amenities:

### Block A - Standard Non-AC
- Basic amenities
- Non-air conditioned
- Most affordable
- Capacity: 40 rooms per floor

### Block B - AC Standard
- Air conditioned rooms
- Standard facilities
- Mid-range pricing
- Capacity: 40 rooms per floor

### Block C - AC Deluxe
- Air conditioned
- Enhanced facilities
- Better furnishings
- Capacity: 40 rooms per floor

### Block D - AC Apartment Style
- Air conditioned
- Apartment-style living
- Premium facilities
- Smaller capacity: 20 rooms per floor
- More spacious rooms

## Room Configuration

Rooms are distributed with varying capacities:

- **Double Rooms (2-bed):** ~31% (2,377 rooms)
- **Triple Rooms (3-bed):** ~36% (2,767 rooms)
- **Quad Rooms (4-bed):** ~32% (2,456 rooms)

**Note:** Database constraint requires capacity between 2-6 persons per room.

## Floor Structure

- Each standard block has 4-5 floors
- Apartment-style blocks have 4 floors
- Each floor typically has 40 rooms (standard) or 20 rooms (apartment-style)

## Room Numbering Convention

Room numbers follow the format: `[Floor Number][Room Number]`

Examples:
- Floor 1, Room 5 → Room **105**
- Floor 2, Room 12 → Room **212**
- Floor 3, Room 30 → Room **330**

## Scripts Available

### 1. `load_hostel_data.py`
Main script to load hostel, block, floor, and room data.
```bash
python load_hostel_data.py
```

### 2. `check_hostel_data.py`
Quick count of records in each table.
```bash
python check_hostel_data.py
```

### 3. `check_detailed_hostel_data.py`
Detailed view of hostel structure with samples.
```bash
python check_detailed_hostel_data.py
```

### 4. `check_schemas.py`
View table schemas and column definitions.
```bash
python check_schemas.py
```

## Database Schema

### Hostel Table
```sql
CREATE TABLE "Hostel" (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL UNIQUE
);
```

### Block Table
```sql
CREATE TABLE "Block" (
    id SERIAL PRIMARY KEY,
    "hostelId" INTEGER NOT NULL REFERENCES "Hostel"(id),
    "blockName" VARCHAR NOT NULL,
    "isAC" BOOLEAN NOT NULL DEFAULT false,
    "isDeluxe" BOOLEAN NOT NULL DEFAULT false,
    "isApartment" BOOLEAN NOT NULL DEFAULT false
);
```

### Floor Table
```sql
CREATE TABLE "Floor" (
    id SERIAL PRIMARY KEY,
    "blockId" INTEGER NOT NULL REFERENCES "Block"(id),
    "floorNumber" INTEGER NOT NULL,
    "totalRooms" INTEGER
);
```

### Room Table
```sql
CREATE TABLE "Room" (
    id SERIAL PRIMARY KEY,
    "floorId" INTEGER NOT NULL REFERENCES "Floor"(id),
    "roomNumber" VARCHAR NOT NULL,
    capacity INTEGER NOT NULL CHECK (capacity >= 2 AND capacity <= 6),
    occupied INTEGER DEFAULT 0,
    "isLocked" BOOLEAN DEFAULT false,
    UNIQUE("floorId", "roomNumber")
);
```

## Adding More Data

To add more hostels, blocks, floors, or rooms:

1. Edit `load_hostel_data.py`
2. Add entries to the respective functions:
   - `add_hostels()` - Add new hostel names
   - `add_blocks()` - Modify block configurations
   - `add_floors()` - Adjust floor counts
   - `add_rooms()` - Change room capacity distributions
3. Run the script: `python load_hostel_data.py`

The script uses `ON CONFLICT DO NOTHING` so it won't create duplicates if run multiple times.

## Notes for Admins

- All hostel data is admin-managed (not user-provided)
- Room capacity constraint: 2-6 persons per room
- Occupied count must not exceed capacity
- Use the allocation system to assign rooms to students
- Lock rooms using `isLocked` flag to prevent selection during allocation

## Test Allocation Session

A test allocation session has been created with ID 26:
- Current Rank: 1
- Total Users: 2
- Time per Rank: 60 seconds
- Status: Active

Use test endpoints (remove in production):
- `POST /api/allocation/session/start-test`
- `POST /api/allocation/session/stop-test`
- `GET /api/allocation/session/current-test`
