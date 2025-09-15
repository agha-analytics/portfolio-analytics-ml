/*
==========================================================
 File: clean_stores.sql
 Purpose: Data Integrity Check for retail_sales.stores
 Author: Agha Al Agha
==========================================================
*/

-- 1. Backup table
CREATE TABLE IF NOT EXISTS stores_backup AS
SELECT * FROM stores;

-- 2. Check for duplicate Store IDs
SELECT Store, COUNT(*) AS cnt
FROM stores
GROUP BY Store
HAVING COUNT(*) > 1;

-- ✅ Result: No duplicates found

-- 3. Enforce uniqueness (future-proofing)
ALTER TABLE stores
ADD PRIMARY KEY (Store);
