-- Migration script to update database schema for room counselling system
-- Run this script to add new tables and modify existing ones

-- Add new enum types
CREATE TYPE "SelectionStatus" AS ENUM ('waiting', 'active', 'completed', 'skipped', 'timed_out');
CREATE TYPE "ApprovalStatus" AS ENUM ('pending', 'approved', 'rejected', 'expired');
CREATE TYPE "SessionStatus" AS ENUM ('not_started', 'active', 'paused', 'completed');
CREATE TYPE "TurnStatus" AS ENUM ('pending', 'active', 'completed', 'skipped', 'timed_out');
CREATE TYPE "ProcessingStatus" AS ENUM ('queued', 'processing', 'completed', 'failed');

-- Modify User table - Add new columns
ALTER TABLE "User" 
ADD COLUMN "isApproved" BOOLEAN DEFAULT true,
ADD COLUMN "selectionStatus" "SelectionStatus" DEFAULT 'waiting',
ADD COLUMN "currentTurnStartTime" TIMESTAMP;

-- Modify Room table - Add lock status
ALTER TABLE "Room"
ADD COLUMN "isLocked" BOOLEAN DEFAULT false;

-- Modify Preference table - Add new fields for flexible room selection
ALTER TABLE "Preference"
ADD COLUMN "isAnyRoom" BOOLEAN DEFAULT false,
ADD COLUMN "roomType" VARCHAR(255),
ADD COLUMN "isLocked" BOOLEAN DEFAULT false;

-- Make roomId nullable in Preference table (for "any room" preferences)
ALTER TABLE "Preference" 
ALTER COLUMN "roomId" DROP NOT NULL;

-- Modify RoomAssignment table - Add confirmation tracking
ALTER TABLE "RoomAssignment"
ADD COLUMN "isConfirmed" BOOLEAN DEFAULT false,
ADD COLUMN "confirmedAt" TIMESTAMP;

-- Create CounsellingSession table
CREATE TABLE "CounsellingSession" (
    id SERIAL PRIMARY KEY,
    "sessionName" VARCHAR(255) UNIQUE NOT NULL,
    "currentRank" INTEGER DEFAULT 1,
    "currentUserId" INTEGER,
    "turnStartTime" TIMESTAMP,
    "sessionStatus" "SessionStatus" DEFAULT 'not_started',
    "turnDuration" INTEGER DEFAULT 30,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "startedAt" TIMESTAMP,
    "pausedAt" TIMESTAMP,
    "completedAt" TIMESTAMP
);

-- Create TurnQueue table
CREATE TABLE "TurnQueue" (
    id SERIAL PRIMARY KEY,
    "userId" INTEGER UNIQUE NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
    rank INTEGER UNIQUE NOT NULL,
    "turnStartTime" TIMESTAMP,
    "turnEndTime" TIMESTAMP,
    status "TurnStatus" DEFAULT 'pending',
    "lockedAt" TIMESTAMP,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_turnqueue_rank ON "TurnQueue"(rank);
CREATE INDEX idx_turnqueue_status ON "TurnQueue"(status);

-- Create ProcessingQueue table
CREATE TABLE "ProcessingQueue" (
    id SERIAL PRIMARY KEY,
    "userId" INTEGER NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
    rank INTEGER NOT NULL,
    "queuePosition" INTEGER NOT NULL,
    "lockedAt" TIMESTAMP NOT NULL,
    status "ProcessingStatus" DEFAULT 'queued',
    "processedAt" TIMESTAMP,
    "assignedRoomId" INTEGER,
    "failureReason" VARCHAR(500),
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_processingqueue_position ON "ProcessingQueue"("queuePosition");
CREATE INDEX idx_processingqueue_status ON "ProcessingQueue"(status);
CREATE INDEX idx_processingqueue_userid ON "ProcessingQueue"("userId");

-- Create RoommateApproval table
CREATE TABLE "RoommateApproval" (
    id SERIAL PRIMARY KEY,
    "preferenceId" INTEGER NOT NULL REFERENCES "Preference"(id) ON DELETE CASCADE,
    "requesterId" INTEGER NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
    "approverId" INTEGER NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
    status "ApprovalStatus" DEFAULT 'pending',
    "requestedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "respondedAt" TIMESTAMP,
    UNIQUE("preferenceId", "approverId")
);

CREATE INDEX idx_roommateapproval_approver ON "RoommateApproval"("approverId", status);

-- Create RoomLock table
CREATE TABLE "RoomLock" (
    id SERIAL PRIMARY KEY,
    "roomId" INTEGER NOT NULL REFERENCES "Room"(id) ON DELETE CASCADE,
    "lockedById" INTEGER NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
    "lockedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "expiresAt" TIMESTAMP NOT NULL,
    "isExpired" BOOLEAN DEFAULT false
);

CREATE INDEX idx_roomlock_roomid ON "RoomLock"("roomId");
CREATE INDEX idx_roomlock_expiresat ON "RoomLock"("expiresAt");

-- Add index on RoomAssignment for better query performance
CREATE INDEX idx_roomassignment_userid ON "RoomAssignment"("userId");

-- Add comment for documentation
COMMENT ON TABLE "CounsellingSession" IS 'Tracks the current counselling session state';
COMMENT ON TABLE "TurnQueue" IS 'Sequential queue for 30-second turns by rank';
COMMENT ON TABLE "ProcessingQueue" IS 'Async queue for processing locked preferences';
COMMENT ON TABLE "RoommateApproval" IS 'Tracks roommate approval requests and responses';
COMMENT ON TABLE "RoomLock" IS 'Temporary locks on rooms during selection process';

-- Create a function to auto-update updatedAt timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW."updatedAt" = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for CounsellingSession
CREATE TRIGGER update_counsellingsession_updated_at 
    BEFORE UPDATE ON "CounsellingSession" 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Migration completed successfully!';
    RAISE NOTICE 'New tables created: CounsellingSession, TurnQueue, ProcessingQueue, RoommateApproval, RoomLock';
    RAISE NOTICE 'Updated tables: User, Room, Preference, RoomAssignment';
END $$;
