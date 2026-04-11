-- Migration: Add allocatedRoomId field to User table
-- This allows us to directly track which room a user has been allocated

-- Step 1: Add allocatedRoomId column to User table
ALTER TABLE "User" 
ADD COLUMN "allocatedRoomId" INTEGER REFERENCES "Rooms"(id) ON DELETE SET NULL;

-- Step 2: Add allocatedAt timestamp to track when room was allocated
ALTER TABLE "User"
ADD COLUMN "allocatedAt" TIMESTAMP;

-- Step 3: Create index for faster queries on allocated rooms
CREATE INDEX idx_user_allocated_room ON "User"("allocatedRoomId") WHERE "allocatedRoomId" IS NOT NULL;

-- Step 4: Backfill existing allocations from RoomAssignments table
UPDATE "User" u
SET "allocatedRoomId" = ra."roomId",
    "allocatedAt" = ra."assignedAt"
FROM "RoomAssignments" ra
WHERE u.id = ra."userId";

-- Migration complete
-- Now the User table directly tracks room allocation for easier queries
