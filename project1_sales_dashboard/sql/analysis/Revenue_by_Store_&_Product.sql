-- Revenue by Store & Product (Dept) – Pareto stand-in for Tableau
-- Raw Revenue column removed, only formatted revenue shown.

WITH store_product AS (
  SELECT
    s.Store,
    s.Dept                             AS Product,
    SUM(s.Weekly_Sales)                AS Revenue
  FROM sales s
  GROUP BY s.Store, s.Dept
),
ranked AS (
  SELECT
    Store,
    Product,
    Revenue,
    ROW_NUMBER() OVER (PARTITION BY Store ORDER BY Revenue DESC)              AS `Rank`,
    SUM(Revenue) OVER (PARTITION BY Store ORDER BY Revenue DESC
                       ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)      AS CumRevenue,
    SUM(Revenue) OVER (PARTITION BY Store)                                     AS TotalRevenue,
    NTILE(5)    OVER (PARTITION BY Store ORDER BY Revenue DESC)               AS `Quintile`
  FROM store_product
)
SELECT
  Store                                   AS `Store`,
  Product                                 AS `Product`,
  CONCAT('$', FORMAT(Revenue, 2))          AS `Revenue (USD)`,
  CumRevenue / TotalRevenue                AS `Cum Share`,
  CONCAT(FORMAT((CumRevenue / TotalRevenue) * 100, 1), '%') AS `Cum Share %`,
  `Rank`,
  CASE
    WHEN (CumRevenue / TotalRevenue) <= 0.80 THEN 'Top 80%'
    ELSE 'Bottom 20%'
  END                                      AS `Pareto Band`,
  `Quintile`
FROM ranked
ORDER BY `Store`, `Rank`;
