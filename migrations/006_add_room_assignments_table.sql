-- Migration: Add RoomAssignments table to track multiple users per room
-- This fixes the issue where assignedUserId was being overwritten

-- Step 1: Create RoomAssignments table to track all users assigned to each room
CREATE TABLE "RoomAssignments" (
    id SERIAL PRIMARY KEY,
    "roomId" INTEGER NOT NULL REFERENCES "Rooms"(id) ON DELETE CASCADE,
    "userId" INTEGER NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
    "assignedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure a user can only be assigned to one room and cannot be assigned twice to same room
    UNIQUE("userId"),
    UNIQUE("roomId", "userId")
);

-- Create indexes for faster queries
CREATE INDEX idx_room_assignments_room ON "RoomAssignments"("roomId");
CREATE INDEX idx_room_assignments_user ON "RoomAssignments"("userId");

-- Step 2: Migrate existing assignments from Rooms table to RoomAssignments
-- (Only if there are any existing assignments)
INSERT INTO "RoomAssignments" ("roomId", "userId", "assignedAt")
SELECT id, "assignedUserId", "assignedAt"
FROM "Rooms"
WHERE "assignedUserId" IS NOT NULL;

-- Step 3: Keep assignedUserId and assignedAt in Rooms for backward compatibility
-- but they are now deprecated in favor of RoomAssignments table
-- Future: Can remove these fields after all code is updated

-- Migration complete
