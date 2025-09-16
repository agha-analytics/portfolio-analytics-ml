-- Purpose: Revenue by “region” and product.
-- Notes:
--   • No explicit region in this dataset, so we use stores.Type (A/B/C) as a region proxy.
--   • Product = Dept.
--   • Includes a Top 10 products per region section.

-- All region × product totals
SELECT
  st.Type                                                   AS region,     -- proxy region
  s.Dept                                                    AS product,
  SUM(s.Weekly_Sales)                                       AS revenue_raw,
  CONCAT('$', FORMAT(SUM(s.Weekly_Sales), 2))               AS revenue_usd
FROM sales s
JOIN stores st USING (Store)
GROUP BY st.Type, s.Dept
ORDER BY region, revenue_raw DESC;

-- Top 10 products per region (by revenue)
WITH region_product AS (
  SELECT
    st.Type                         AS region,
    s.Dept                          AS product,
    SUM(s.Weekly_Sales)             AS revenue
  FROM sales s
  JOIN stores st USING (Store)
  GROUP BY st.Type, s.Dept
),
ranked AS (
  SELECT
    region,
    product,
    revenue,
    ROW_NUMBER() OVER (PARTITION BY region ORDER BY revenue DESC) AS rn
  FROM region_product
)
SELECT
  region,
  product,
  revenue                                                AS revenue_raw,
  CONCAT('$', FORMAT(revenue, 2))                        AS revenue_usd
FROM ranked
WHERE rn <= 10
ORDER BY region, rn;
