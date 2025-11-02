-- Migration: Add role field to User table
-- Created: 2025-11-02
-- Description: Add role enum (user/admin) to User table for access control

-- Step 1: Create Role enum type
CREATE TYPE "UserRole" AS ENUM ('user', 'admin');

-- Step 2: Add role column with default 'user'
ALTER TABLE "User" 
ADD COLUMN role "UserRole" DEFAULT 'user' NOT NULL;

-- Step 3: Add index for faster role-based queries
CREATE INDEX idx_user_role ON "User"(role);

-- Step 4: Add comment to column
COMMENT ON COLUMN "User".role IS 'User role: user (default) or admin (can manage sessions)';

-- Step 5: Optional - Set first user as admin (if exists)
-- Uncomment the next line if you want the first user to be admin
-- UPDATE "User" SET role = 'admin' WHERE id = (SELECT MIN(id) FROM "User");

-- Display success message
SELECT 'Role field added to User table successfully!' AS status;
