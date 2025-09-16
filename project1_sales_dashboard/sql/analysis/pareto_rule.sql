-- Purpose: Identify the “vital few” contributors to revenue (Pareto / 80–20).
-- What you get:
--   1) Overall Pareto by Dept, returning rows until cumulative revenue share reaches 80%.
--   2) Same concept per Store.
--   3) NTILE(5) tagging (1 = top 20% by rank; note this is by rank, not contribution).
-- Formatting: includes both raw $ and readable $.

-- 1) Overall Pareto by Dept (stop when cumulative share <= 80%)
WITH dept_sales AS (
  SELECT Dept, SUM(Weekly_Sales) AS revenue
  FROM sales
  GROUP BY Dept
),
ranked AS (
  SELECT
    Dept,
    revenue,
    SUM(revenue) OVER (ORDER BY revenue DESC
                       ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cum_revenue,
    SUM(revenue) OVER ()                                                  AS total_revenue
  FROM dept_sales
)
SELECT
  Dept,
  revenue                                                   AS revenue_raw,
  CONCAT('$', FORMAT(revenue, 2))                           AS revenue_usd,
  cum_revenue / total_revenue                               AS cum_share_raw,
  CONCAT(FORMAT((cum_revenue / total_revenue) * 100, 1), '%') AS cum_share_pct
FROM ranked
WHERE (cum_revenue / total_revenue) <= 0.80
ORDER BY revenue_raw DESC;

-- 2) Pareto per Store (top-contributing Depts within each store until 80%)
WITH dept_sales AS (
  SELECT Store, Dept, SUM(Weekly_Sales) AS revenue
  FROM sales
  GROUP BY Store, Dept
),
ranked AS (
  SELECT
    Store,
    Dept,
    revenue,
    SUM(revenue) OVER (PARTITION BY Store ORDER BY revenue DESC
                       ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cum_rev,
    SUM(revenue) OVER (PARTITION BY Store)                                AS tot_rev
  FROM dept_sales
)
SELECT
  Store,
  Dept,
  revenue                                                   AS revenue_raw,
  CONCAT('$', FORMAT(revenue, 2))                           AS revenue_usd,
  cum_rev / tot_rev                                         AS cum_share_raw,
  CONCAT(FORMAT((cum_rev / tot_rev) * 100, 1), '%')         AS cum_share_pct
FROM ranked
WHERE (cum_rev / tot_rev) <= 0.80
ORDER BY Store, revenue_raw DESC;

-- 3) NTILE(5): tag top 20% by rank (not by cumulative contribution)
WITH dept_sales AS (
  SELECT Dept, SUM(Weekly_Sales) AS revenue
  FROM sales
  GROUP BY Dept
)
SELECT
  Dept,
  revenue                                                   AS revenue_raw,
  CONCAT('$', FORMAT(revenue, 2))                           AS revenue_usd,
  NTILE(5) OVER (ORDER BY revenue DESC)                     AS quintile  -- 1 = top 20%
FROM dept_sales
ORDER BY revenue DESC;
