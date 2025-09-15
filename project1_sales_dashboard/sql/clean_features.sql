/*
==========================================================
 File: clean_features.sql
 Purpose: Data Integrity Check for retail_sales.features
 Author: Agha Al Agha
==========================================================
*/

-- 1. Backup table
CREATE TABLE IF NOT EXISTS features_backup AS
SELECT * FROM features;

-- 2. Check for duplicates by Store + Date
SELECT Store, Date, COUNT(*) AS cnt
FROM features
GROUP BY Store, Date
HAVING COUNT(*) > 1;

-- ✅ Result: No duplicates found

-- 3. Enforce uniqueness (future-proofing)
ALTER TABLE features
ADD UNIQUE KEY uq_features_store_date (Store, Date);
