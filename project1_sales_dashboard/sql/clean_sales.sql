/*
==========================================================
 File: clean_sales.sql
 Purpose: Data Cleaning & Deduplication for retail_sales.sales
 Author: Agha Al Agha
==========================================================

 Steps:
 1. Backup the table before making changes
 2. Identify duplicates based on business keys (Store, Dept, Date)
 3. Use ROW_NUMBER() to keep the "best" row (latest UpdatedAt, highest Weekly_Sales)
 4. Delete extra duplicates
 5. Add a UNIQUE constraint to prevent future duplicates
==========================================================
*/

-- 1. Backup table (safety first!)
CREATE TABLE IF NOT EXISTS sales_backup AS
SELECT * FROM sales;

-- 2. Check for duplicates
SELECT Store, Dept, Date, COUNT(*) AS cnt
FROM sales
GROUP BY Store, Dept, Date
HAVING COUNT(*) > 1
ORDER BY cnt DESC;

-- 3. Preview which rows will be kept (rn = 1)
WITH ranked AS (
    SELECT
        s.*,
        ROW_NUMBER() OVER (
            PARTITION BY Store, Dept, Date
            ORDER BY UpdatedAt DESC, Weekly_Sales DESC, id ASC
        ) AS rn
    FROM sales s
)
SELECT *
FROM ranked
WHERE rn = 1
LIMIT 20;

-- 4. Delete duplicates (keep rn = 1, remove rn > 1)
DELETE s
FROM sales s
JOIN (
    SELECT id
    FROM (
        SELECT
            id,
            ROW_NUMBER() OVER (
                PARTITION BY Store, Dept, Date
                ORDER BY UpdatedAt DESC, Weekly_Sales DESC, id ASC
            ) AS rn
        FROM sales
    ) t
    WHERE rn > 1
) d ON s.id = d.id;

-- 5. Verify cleanup (should return 0 rows)
SELECT Store, Dept, Date, COUNT(*) AS cnt
FROM sales
GROUP BY Store, Dept, Date
HAVING COUNT(*) > 1;

-- 6. (Optional) Add unique constraint to prevent future duplicates
ALTER TABLE sales
ADD UNIQUE KEY uq_sales_store_dept_date (Store, Dept, Date);

