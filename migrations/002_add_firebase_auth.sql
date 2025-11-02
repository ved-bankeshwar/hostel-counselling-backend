-- Migration: Add Firebase Authentication Fields
-- Created: 2025-11-01
-- Description: Adds Firebase authentication support to User table

-- Add new columns for Firebase authentication
ALTER TABLE "User" 
ADD COLUMN IF NOT EXISTS "firebaseUid" VARCHAR(255) UNIQUE,
ADD COLUMN IF NOT EXISTS "displayName" VARCHAR(255),
ADD COLUMN IF NOT EXISTS "photoUrl" TEXT,
ADD COLUMN IF NOT EXISTS "provider" VARCHAR(50) DEFAULT 'google',
ADD COLUMN IF NOT EXISTS "lastLoginAt" TIMESTAMP,
ADD COLUMN IF NOT EXISTS "updatedAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Make passwordHash optional (nullable) since Firebase users won't have passwords
ALTER TABLE "User" 
ALTER COLUMN "passwordHash" DROP NOT NULL;

-- Make registrationNumber optional initially (can be filled later)
ALTER TABLE "User"
ALTER COLUMN "registrationNumber" DROP NOT NULL;

-- Update displayName from existing name field for current users
UPDATE "User" 
SET "displayName" = name 
WHERE "displayName" IS NULL;

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_firebase_uid ON "User"("firebaseUid");
CREATE INDEX IF NOT EXISTS idx_users_email ON "User"(email);
CREATE INDEX IF NOT EXISTS idx_users_provider ON "User"("provider");

-- Add comment to table
COMMENT ON COLUMN "User"."firebaseUid" IS 'Unique Firebase user ID from Firebase Auth';
COMMENT ON COLUMN "User"."displayName" IS 'User display name from Google Sign-In';
COMMENT ON COLUMN "User"."photoUrl" IS 'User profile photo URL from Google';
COMMENT ON COLUMN "User"."provider" IS 'Authentication provider (google, email, etc.)';
COMMENT ON COLUMN "User"."lastLoginAt" IS 'Timestamp of last successful login';
COMMENT ON COLUMN "User"."updatedAt" IS 'Timestamp of last profile update';
