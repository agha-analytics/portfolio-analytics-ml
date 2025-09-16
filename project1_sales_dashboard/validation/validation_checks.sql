-- Total rows per table
SELECT 'sales'    AS table_name, COUNT(*) AS total_rows FROM sales
UNION ALL
SELECT 'stores'   AS table_name, COUNT(*) AS total_rows FROM stores
UNION ALL
SELECT 'features' AS table_name, COUNT(*) AS total_rows FROM features;

-- sales: should be unique by (Store, Dept, Date)
SELECT Store, Dept, Date, COUNT(*) AS cnt
FROM sales
GROUP BY Store, Dept, Date
HAVING COUNT(*) > 1
ORDER BY cnt DESC, Store, Dept, Date
LIMIT 50;

-- stores: should be unique by (Store)
SELECT Store, COUNT(*) AS cnt
FROM stores
GROUP BY Store
HAVING COUNT(*) > 1
LIMIT 50;

-- features: should be unique by (Store, Date)
SELECT Store, Date, COUNT(*) AS cnt
FROM features
GROUP BY Store, Date
HAVING COUNT(*) > 1
LIMIT 50;

-- Key columns must be NOT NULL
SELECT COUNT(*) AS sales_null_keys
FROM sales
WHERE Store IS NULL OR Dept IS NULL OR Date IS NULL;

SELECT COUNT(*) AS stores_null_keys
FROM stores
WHERE Store IS NULL;

SELECT COUNT(*) AS features_null_keys
FROM features
WHERE Store IS NULL OR Date IS NULL;

-- Business columns sanity
SELECT
  SUM(Weekly_Sales IS NULL) AS null_weekly_sales,
  SUM(Weekly_Sales < 0)     AS negative_weekly_sales
FROM sales;

-- If IsHoliday should be 0/1:
SELECT COUNT(*) AS invalid_IsHoliday
FROM sales
WHERE IsHoliday NOT IN (0,1);


-- Every sales.Store must exist in stores
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

-- Summary stats
SELECT
  MIN(Weekly_Sales) AS min_sales,
  AVG(Weekly_Sales) AS avg_sales,
  MAX(Weekly_Sales) AS max_sales
FROM sales;


-- How many *extra* rows duplicates add in sales (expect 0)
SELECT COALESCE(SUM(cnt - 1), 0) AS extra_rows_due_to_dupes
FROM (
  SELECT COUNT(*) AS cnt
  FROM sales
  GROUP BY Store, Dept, Date
  HAVING COUNT(*) > 1
) x;


-- Sales unique key
SHOW INDEX FROM sales WHERE Key_name = 'uq_sales_store_dept_date';

-- Features unique key
SHOW INDEX FROM features WHERE Key_name = 'uq_features_store_date';

-- Stores primary key on Store
SHOW INDEX FROM stores WHERE Non_unique = 0 AND Column_name = 'Store';
