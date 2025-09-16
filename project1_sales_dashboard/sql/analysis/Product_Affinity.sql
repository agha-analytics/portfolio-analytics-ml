-- Product Affinity (Market Basket Style) by Store-Week

SELECT
    s1.Store                               AS `Store`,
    s1.Dept                                AS `Product A`,
    s2.Dept                                AS `Product B`,
    CONCAT('$', FORMAT(SUM(s1.Weekly_Sales + s2.Weekly_Sales), 2)) AS `Combined Revenue (USD)`
FROM sales s1
JOIN sales s2
  ON s1.Store = s2.Store
 AND s1.Date  = s2.Date
 AND s1.Dept  < s2.Dept   -- avoid duplicates and self-joins
GROUP BY s1.Store, s1.Dept, s2.Dept
ORDER BY SUM(s1.Weekly_Sales + s2.Weekly_Sales) DESC
LIMIT 20;
