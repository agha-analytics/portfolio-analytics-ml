/*
==========================================================
 Validation:
 Project: project1_sales_dashboard
 Purpose: Data validation for the cleaned `retail_sales` schema
 Author: Agha Al Agha
 Engine: MySQL 8+
==========================================================
 Contents
  0) Schema
  1) Row counts (baseline)
  2) Duplicate checks (business keys)
  3) Null / invalid value checks
  4) Referential integrity checks
  5) Summary statistics (for records / cross-tool compare)
  6) Constraint validation (keys & uniques present)
  7) (Optional) Sampling helpers
==========================================================
*/

-- 0) Use the schema
USE retail_sales;

-- -------------------------------------------------------
-- 1) Row counts (baseline)
-- -------------------------------------------------------
SELECT 'sales'    AS table_name, COUNT(*) AS total_rows FROM sales
UNION ALL
SELECT 'stores'   AS table_name, COUNT(*) AS total_rows FROM stores
UNION ALL
SELECT 'features' AS table_name, COUNT(*) AS total_rows FROM features;

-- -------------------------------------------------------
-- 2) Duplicate checks (by business keys)
--    Expect: zero rows from each query
-- -------------------------------------------------------

-- sales should be unique by (Store, Dept, Date)
SELECT Store, Dept, Date, COUNT(*) AS cnt
FROM sales
GROUP BY Store, Dept, Date
HAVING COUNT(*) > 1
ORDER BY cnt DESC, Store, Dept, Date;

-- How many *extra* rows due to duplicates in sales (should be 0)
SELECT COALESCE(SUM(cnt - 1), 0) AS extra_rows_due_to_dupes
FROM (
  SELECT COUNT(*) AS cnt
  FROM sales
  GROUP BY Store, Dept, Date
  HAVING COUNT(*) > 1
) AS d;

-- stores should be unique by (Store)
SELECT Store, COUNT(*) AS cnt
FROM stores
GROUP BY Store
HAVING COUNT(*) > 1;

-- features should be unique by (Store, Date)
SELECT Store, Date, COUNT(*) AS cnt
FROM features
GROUP BY Store, Date
HAVING COUNT(*) > 1
ORDER BY Date DESC, Store;

-- -------------------------------------------------------
-- 3) Null / invalid value checks
-- -------------------------------------------------------

-- Key columns should not be NULL
SELECT COUNT(*) AS sales_null_keys
FROM sales
WHERE Store IS NULL OR Dept IS NULL OR Date IS NULL;

SELECT COUNT(*) AS stores_null_keys
FROM stores
WHERE Store IS NULL;

SELECT COUNT(*) AS features_null_keys
FROM features
WHERE Store IS NULL OR Date IS NULL;

-- Business column sanity for sales
SELECT
  SUM(Weekly_Sales IS NULL) AS null_weekly_sales,
  SUM(Weekly_Sales < 0)     AS negative_weekly_sales
FROM sales;

-- If IsHoliday is encoded as 0/1
SELECT COUNT(*) AS invalid_IsHoliday
FROM sales
WHERE IsHoliday NOT IN (0,1);

-- -------------------------------------------------------
-- 4) Referential integrity checks
--    Expect: zero orphans
-- -------------------------------------------------------

-- Every sales.Store should exist in stores
SELECT COUNT(*) AS orphan_sales_store
FROM sales s
LEFT JOIN stores t ON t.Store = s.Store
WHERE t.Store IS NULL;

-- For each (Store, Date) in sales, there should be a features row
SELECT COUNT(*) AS sales_without_features
FROM sales s
LEFT JOIN features f
  ON f.Store = s.Store AND f.Date = s.Date
WHERE f.Store IS NULL;

-- -------------------------------------------------------
-- 5) Summary statistics (for records / Excel compare)
-- -------------------------------------------------------
SELECT
  MIN(Weekly_Sales) AS min_sales,
  AVG(Weekly_Sales) AS avg_sales,
  MAX(Weekly_Sales) AS max_sales
FROM sales;

-- row counts per store/department (sanity)
SELECT Store, Dept, COUNT(*) AS rows_per_store_dept
FROM sales
GROUP BY Store, Dept
ORDER BY Store, Dept;

-- -------------------------------------------------------
-- 6) Constraint validation (ensure keys exist)
-- -------------------------------------------------------

-- Sales unique key on (Store, Dept, Date)
SHOW INDEX FROM sales WHERE Key_name = 'uq_sales_store_dept_date';

-- Features unique key on (Store, Date)
SHOW INDEX FROM features WHERE Key_name = 'uq_features_store_date';

-- Stores primary key on Store (Key_name should be 'PRIMARY')
SHOW INDEX FROM stores WHERE Non_unique = 0 AND Column_name = 'Store';

-- -------------------------------------------------------
-- 7) Sampling helpers
-- -------------------------------------------------------

-- Random sample of sales rows (visual spot checks)
SELECT *
FROM sales
ORDER BY RAND()
LIMIT 10;

-- Latest dates present (timeline sanity)
SELECT MIN(Date) AS min_date, MAX(Date) AS max_date FROM sales;
SELECT MIN(Date) AS min_date, MAX(Date) AS max_date FROM features;
