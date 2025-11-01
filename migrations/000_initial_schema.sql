-- Initial database schema creation for room counselling system
-- This creates all tables from scratch

-- Create enum types
CREATE TYPE "Gender" AS ENUM ('male', 'female');
CREATE TYPE "HostelType" AS ENUM ('mens', 'ladies');
CREATE TYPE "SelectionStatus" AS ENUM ('waiting', 'active', 'completed', 'skipped', 'timed_out');
CREATE TYPE "FriendStatus" AS ENUM ('pending', 'accepted', 'rejected');
CREATE TYPE "ApprovalStatus" AS ENUM ('pending', 'approved', 'rejected', 'expired');
CREATE TYPE "SessionStatus" AS ENUM ('not_started', 'active', 'paused', 'completed');
CREATE TYPE "TurnStatus" AS ENUM ('pending', 'active', 'completed', 'skipped', 'timed_out');
CREATE TYPE "ProcessingStatus" AS ENUM ('queued', 'processing', 'completed', 'failed');

-- Create User table
CREATE TABLE "User" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    "passwordHash" VARCHAR(255) NOT NULL,
    "registrationNumber" VARCHAR(255) UNIQUE NOT NULL,
    gender "Gender" NOT NULL,
    rank INTEGER UNIQUE NOT NULL,
    hostel "HostelType" NOT NULL,
    "isActive" BOOLEAN DEFAULT true,
    "isApproved" BOOLEAN DEFAULT true,
    "selectionStatus" "SelectionStatus" DEFAULT 'waiting',
    "currentTurnStartTime" TIMESTAMP,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_rank ON "User"(rank);

-- Create Friendship table
CREATE TABLE "Friendship" (
    id SERIAL PRIMARY KEY,
    "userId" INTEGER NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
    "friendId" INTEGER NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
    status "FriendStatus" NOT NULL,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE("userId", "friendId")
);

-- Create Hostel table
CREATE TABLE "Hostel" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
);

-- Create Block table
CREATE TABLE "Block" (
    id SERIAL PRIMARY KEY,
    "hostelId" INTEGER NOT NULL REFERENCES "Hostel"(id) ON DELETE CASCADE,
    "blockName" VARCHAR(255) NOT NULL,
    "isAC" BOOLEAN NOT NULL,
    "isDeluxe" BOOLEAN NOT NULL,
    "isApartment" BOOLEAN NOT NULL,
    UNIQUE("hostelId", "blockName")
);

-- Create Floor table
CREATE TABLE "Floor" (
    id SERIAL PRIMARY KEY,
    "blockId" INTEGER NOT NULL REFERENCES "Block"(id) ON DELETE CASCADE,
    "floorNumber" INTEGER NOT NULL,
    "totalRooms" INTEGER DEFAULT 40,
    UNIQUE("blockId", "floorNumber")
);

-- Create Room table
CREATE TABLE "Room" (
    id SERIAL PRIMARY KEY,
    "floorId" INTEGER NOT NULL REFERENCES "Floor"(id) ON DELETE CASCADE,
    "roomNumber" VARCHAR(255) NOT NULL,
    capacity INTEGER NOT NULL CHECK (capacity >= 2 AND capacity <= 6),
    occupied INTEGER DEFAULT 0,
    "isLocked" BOOLEAN DEFAULT false,
    UNIQUE("floorId", "roomNumber")
);

-- Create Preference table
CREATE TABLE "Preference" (
    id SERIAL PRIMARY KEY,
    "userId" INTEGER NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
    "preferenceRank" INTEGER NOT NULL CHECK ("preferenceRank" >= 1 AND "preferenceRank" <= 5),
    "roomId" INTEGER REFERENCES "Room"(id) ON DELETE SET NULL,
    "isAnyRoom" BOOLEAN DEFAULT false,
    "roomType" VARCHAR(255),
    "isLocked" BOOLEAN DEFAULT false,
    "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE("userId", "preferenceRank")
);

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

-- Create RoomAssignment table
CREATE TABLE "RoomAssignment" (
    id SERIAL PRIMARY KEY,
    "roomId" INTEGER NOT NULL REFERENCES "Room"(id) ON DELETE CASCADE,
    "userId" INTEGER NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
    "groupId" UUID DEFAULT gen_random_uuid(),
    "isConfirmed" BOOLEAN DEFAULT false,
    "assignedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    "confirmedAt" TIMESTAMP
);

CREATE INDEX idx_roomassignment_groupid ON "RoomAssignment"("groupId");
CREATE INDEX idx_roomassignment_userid ON "RoomAssignment"("userId");

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
    RAISE NOTICE 'Database schema created successfully!';
    RAISE NOTICE 'All tables and types have been created';
END $$;
