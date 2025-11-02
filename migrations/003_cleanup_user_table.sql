-- Migration: Clean up User table for Firebase-only authentication
-- Created: 2025-11-02
-- Description: Remove redundant fields and optimize for Firebase Google Sign-In

-- Step 1: Copy name to displayName for existing users who don't have it
UPDATE "User" 
SET "displayName" = name 
WHERE "displayName" IS NULL AND name IS NOT NULL;

-- Step 2: Drop redundant columns
ALTER TABLE "User" DROP COLUMN IF EXISTS name;
ALTER TABLE "User" DROP COLUMN IF EXISTS "passwordHash";
ALTER TABLE "User" DROP COLUMN IF EXISTS "photoUrl";
ALTER TABLE "User" DROP COLUMN IF EXISTS provider;

-- Step 3: Make firebaseUid NOT NULL (required for Firebase auth)
-- First, delete existing users without firebaseUid (sample data)
DELETE FROM "User" WHERE "firebaseUid" IS NULL;

-- Now make it NOT NULL
ALTER TABLE "User" ALTER COLUMN "firebaseUid" SET NOT NULL;

-- Step 4: Make displayName NOT NULL (required from Google Sign-In)
ALTER TABLE "User" ALTER COLUMN "displayName" SET NOT NULL;

-- Step 5: Add comments to table
COMMENT ON TABLE "User" IS 'User accounts authenticated via Firebase Google Sign-In';
COMMENT ON COLUMN "User"."firebaseUid" IS 'Unique Firebase user ID from Google Sign-In';
COMMENT ON COLUMN "User"."displayName" IS 'User full name from Google account';
COMMENT ON COLUMN "User"."registrationNumber" IS 'Student registration number (set after login)';
COMMENT ON COLUMN "User".email IS 'User email from Google account';

-- Display success message
SELECT 'User table cleaned up successfully! Now optimized for Firebase authentication.' AS status;
