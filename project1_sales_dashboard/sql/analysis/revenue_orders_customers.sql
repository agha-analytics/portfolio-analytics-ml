-- Purpose: Total revenue for this Walmart-style dataset, plus simple “order” proxies.
-- Notes:
--   • Revenue = SUM(Weekly_Sales).
--   • This dataset has no explicit orders/customers tables; each row is a Store–Dept–Week record.
--   • Returns both raw numbers and formatted strings (easier to read in BI tools).

SELECT
  SUM(s.Weekly_Sales)                                        AS revenue_raw,
  CONCAT('$', FORMAT(SUM(s.Weekly_Sales), 2))                AS revenue_usd,
  COUNT(*)                                                   AS row_count_raw,      -- proxy for “orders”
  FORMAT(COUNT(*), 0)                                        AS row_count_fmt,
  COUNT(DISTINCT s.Store)                                    AS distinct_stores,
  COUNT(DISTINCT s.Dept)                                     AS distinct_products
FROM sales s;
