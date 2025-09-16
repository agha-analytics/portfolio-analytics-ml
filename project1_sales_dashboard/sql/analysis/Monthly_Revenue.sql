-- Monthly Revenue: Aggregated by Year-Month (formatted for Tableau export)
-- Useful for trend lines and KPI cards (e.g., Revenue Growth %).

SELECT
    DATE_FORMAT(DATE(s.`Date`), '%Y-%m-01')       AS `Month Start`,   -- first day of each month
    CONCAT('$', FORMAT(SUM(s.Weekly_Sales), 2))   AS `Revenue (USD)`
FROM sales s
GROUP BY DATE_FORMAT(DATE(s.`Date`), '%Y-%m-01')
ORDER BY `Month Start`;
