-- Monthly Revenue by Region (Store Type) – ready for CSV → Tableau
-- Includes both numeric [Revenue] for calcs and formatted [Revenue (USD)] for display.

SELECT
    DATE_FORMAT(DATE(s.`Date`), '%Y-%m-01')        AS `Month Start`,   -- first day of month
    st.Type                                        AS `Region`,        -- proxy for region (A/B/C)
    SUM(s.Weekly_Sales)                            AS `Revenue`,       -- numeric (use this in calcs)
    CONCAT('$', FORMAT(SUM(s.Weekly_Sales), 2))    AS `Revenue (USD)`  -- pretty string (labels)
FROM sales s
JOIN stores st USING (Store)
GROUP BY DATE_FORMAT(DATE(s.`Date`), '%Y-%m-01'), st.Type
ORDER BY `Month Start`, `Region`;
