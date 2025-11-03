-- Migration: Denormalize all room-related tables into single Rooms table
-- WARNING: This is a destructive change that removes normalized structure

-- Step 1: Create new unified Rooms table
CREATE TABLE "Rooms" (
    -- Room identification
    id SERIAL PRIMARY KEY,
    "roomNumber" VARCHAR(255) NOT NULL,
    
    -- Floor information (denormalized)
    "floorNumber" INTEGER NOT NULL,
    
    -- Block information (denormalized)
    "blockName" VARCHAR(255) NOT NULL,
    "isAC" BOOLEAN NOT NULL DEFAULT false,
    "isDeluxe" BOOLEAN NOT NULL DEFAULT false,
    "isApartment" BOOLEAN NOT NULL DEFAULT false,
    
    -- Hostel information (denormalized)
    "hostelName" VARCHAR(255) NOT NULL,
    
    -- Room capacity and occupancy
    capacity INTEGER NOT NULL CHECK (capacity >= 2 AND capacity <= 6),
    occupied INTEGER DEFAULT 0,
    "availableSlots" INTEGER GENERATED ALWAYS AS (capacity - occupied) STORED,
    
    -- Room assignment (denormalized from RoomAssignment)
    "assignedUserId" INTEGER REFERENCES "User"(id) ON DELETE SET NULL,
    "assignedAt" TIMESTAMP,
    
    -- Room lock (denormalized from RoomLock)
    "isLocked" BOOLEAN DEFAULT false,
    "lockedByUserId" INTEGER REFERENCES "User"(id) ON DELETE SET NULL,
    "lockedAt" TIMESTAMP,
    "lockExpiresAt" TIMESTAMP,
    
    -- Metadata
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Unique constraint on hostel + block + floor + room combination
    UNIQUE("hostelName", "blockName", "floorNumber", "roomNumber")
);

-- Create indexes for common queries
CREATE INDEX idx_rooms_hostel ON "Rooms"("hostelName");
CREATE INDEX idx_rooms_block ON "Rooms"("blockName");
CREATE INDEX idx_rooms_available ON "Rooms"("availableSlots") WHERE "availableSlots" > 0;
CREATE INDEX idx_rooms_locked ON "Rooms"("isLocked", "lockExpiresAt");
CREATE INDEX idx_rooms_assigned ON "Rooms"("assignedUserId") WHERE "assignedUserId" IS NOT NULL;

-- Step 2: Migrate data from old tables to new Rooms table
INSERT INTO "Rooms" (
    "roomNumber", 
    "floorNumber", 
    "blockName", 
    "isAC",
    "isDeluxe",
    "isApartment",
    "hostelName", 
    capacity, 
    occupied,
    "assignedUserId",
    "assignedAt",
    "isLocked",
    "lockedByUserId",
    "lockedAt",
    "lockExpiresAt"
)
SELECT 
    r."roomNumber",
    f."floorNumber",
    b."blockName",
    b."isAC",
    b."isDeluxe",
    b."isApartment",
    h.name as "hostelName",
    r.capacity,
    r.occupied,
    ra."userId" as "assignedUserId",
    ra."assignedAt",
    COALESCE(r."isLocked", false) as "isLocked",
    rl."lockedById" as "lockedByUserId",
    rl."lockedAt",
    rl."expiresAt" as "lockExpiresAt"
FROM "Room" r
JOIN "Floor" f ON r."floorId" = f.id
JOIN "Block" b ON f."blockId" = b.id
JOIN "Hostel" h ON b."hostelId" = h.id
LEFT JOIN "RoomAssignment" ra ON r.id = ra."roomId"
LEFT JOIN "RoomLock" rl ON r.id = rl."roomId";

-- Step 3: Update Preference table to use new Rooms table
-- First add temporary column
ALTER TABLE "Preference" ADD COLUMN "newRoomId" INTEGER REFERENCES "Rooms"(id) ON DELETE SET NULL;

-- Copy room references from old to new
UPDATE "Preference" p
SET "newRoomId" = rooms.id
FROM "Rooms" rooms
JOIN "Room" old_room ON 
    old_room."roomNumber" = rooms."roomNumber"
JOIN "Floor" f ON old_room."floorId" = f.id
JOIN "Block" b ON f."blockId" = b.id
JOIN "Hostel" h ON b."hostelId" = h.id
WHERE p."roomId" = old_room.id
    AND rooms."floorNumber" = f."floorNumber"
    AND rooms."blockName" = b."blockName"
    AND rooms."hostelName" = h.name;

-- Drop old roomId column and rename new one
ALTER TABLE "Preference" DROP COLUMN "roomId";
ALTER TABLE "Preference" RENAME COLUMN "newRoomId" TO "roomId";

-- Step 4: Drop old tables (keeping User, Preference, CounsellingSession, etc.)
DROP TABLE IF EXISTS "RoomLock" CASCADE;
DROP TABLE IF EXISTS "RoomAssignment" CASCADE;
DROP TABLE IF EXISTS "RoommateApproval" CASCADE;
DROP TABLE IF EXISTS "Room" CASCADE;
DROP TABLE IF EXISTS "Floor" CASCADE;
DROP TABLE IF EXISTS "Block" CASCADE;
DROP TABLE IF EXISTS "Hostel" CASCADE;

-- Step 5: Create trigger to auto-update updatedAt
CREATE OR REPLACE FUNCTION update_rooms_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW."updatedAt" = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER rooms_updated_at_trigger
BEFORE UPDATE ON "Rooms"
FOR EACH ROW
EXECUTE FUNCTION update_rooms_updated_at();

-- Migration complete
-- NOTE: This is a destructive change. All normalized structure is now denormalized.
-- Data redundancy is intentional as per requirements.
