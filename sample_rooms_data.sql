-- Sample Hostel and Room Data
-- Matches the actual Rooms table structure from migration 005

-- Insert sample rooms
INSERT INTO "Rooms" ("hostelName", "blockName", "floorNumber", "roomNumber", "capacity", "isAC", "isDeluxe", "isApartment") VALUES
-- Hostel A - Standard Boys Hostel
('Hostel A', 'Block 1', 1, '101', 2, false, false, false),
('Hostel A', 'Block 1', 1, '102', 2, false, false, false),
('Hostel A', 'Block 1', 1, '103', 3, false, false, false),
('Hostel A', 'Block 1', 2, '201', 2, true, false, false),
('Hostel A', 'Block 1', 2, '202', 2, true, false, false),
('Hostel A', 'Block 1', 2, '203', 3, false, false, false),
('Hostel A', 'Block 2', 1, '101', 2, false, false, false),
('Hostel A', 'Block 2', 1, '102', 3, false, false, false),
('Hostel A', 'Block 2', 2, '201', 2, true, false, false),

-- Hostel B - Girls Hostel with AC rooms
('Hostel B', 'North Wing', 1, 'N101', 2, true, false, false),
('Hostel B', 'North Wing', 1, 'N102', 2, true, false, false),
('Hostel B', 'North Wing', 2, 'N201', 2, true, true, false),
('Hostel B', 'North Wing', 2, 'N202', 2, true, true, false),
('Hostel B', 'South Wing', 1, 'S101', 2, false, false, false),
('Hostel B', 'South Wing', 1, 'S102', 3, false, false, false),
('Hostel B', 'South Wing', 2, 'S201', 2, true, false, false),

-- Hostel C - Mixed capacity
('Hostel C', 'Main Block', 1, '101', 2, false, false, false),
('Hostel C', 'Main Block', 1, '102', 2, false, false, false),
('Hostel C', 'Main Block', 1, '103', 3, false, false, false),
('Hostel C', 'Main Block', 1, '104', 4, false, false, false),
('Hostel C', 'Main Block', 2, '201', 2, true, false, false),
('Hostel C', 'Main Block', 2, '202', 3, true, false, false),
('Hostel C', 'Main Block', 3, '301', 2, true, true, false),

-- Hostel D - Premium Deluxe Hostel
('Hostel D', 'Tower A', 1, 'A101', 2, true, true, false),
('Hostel D', 'Tower A', 1, 'A102', 2, true, true, false),
('Hostel D', 'Tower A', 2, 'A201', 2, true, true, true),
('Hostel D', 'Tower A', 2, 'A202', 2, true, true, true),
('Hostel D', 'Tower B', 1, 'B101', 2, true, true, false),
('Hostel D', 'Tower B', 2, 'B201', 2, true, true, true),

-- Hostel E - Economy Hostel
('Hostel E', 'Block 1', 1, '101', 3, false, false, false),
('Hostel E', 'Block 1', 1, '102', 3, false, false, false),
('Hostel E', 'Block 1', 1, '103', 4, false, false, false),
('Hostel E', 'Block 1', 2, '201', 3, false, false, false),
('Hostel E', 'Block 1', 2, '202', 4, false, false, false),
('Hostel E', 'Block 2', 1, '101', 3, false, false, false),
('Hostel E', 'Block 2', 1, '102', 4, false, false, false);

-- Verify insertions
SELECT 
    "hostelName", 
    COUNT(*) as total_rooms,
    SUM("capacity") as total_capacity,
    SUM(occupied) as currently_occupied,
    COUNT(CASE WHEN "isAC" = true THEN 1 END) as ac_rooms,
    COUNT(CASE WHEN "isDeluxe" = true THEN 1 END) as deluxe_rooms
FROM "Rooms"
GROUP BY "hostelName"
ORDER BY "hostelName";

-- Summary
SELECT 
    COUNT(*) as total_rooms,
    SUM("capacity") as total_capacity,
    COUNT(CASE WHEN "isAC" = true THEN 1 END) as ac_rooms,
    COUNT(CASE WHEN "isDeluxe" = true THEN 1 END) as deluxe_rooms,
    COUNT(CASE WHEN "isApartment" = true THEN 1 END) as apartments
FROM "Rooms";
