-- Base View: Weekly Revenue by Store and Dept (formatted for Tableau export)
-- Updates:
--   • Is Holiday → 'N' / 'Y'
--   • Store Size → Store Size (sq ft)

SELECT
    s.Store                                AS `Store`,
    s.Dept                                 AS `Dept`,
    DATE(s.`Date`)                         AS `Week Start`,
    CONCAT('$', FORMAT(SUM(s.Weekly_Sales), 2)) AS `Revenue (USD)`,
    CASE WHEN s.IsHoliday = 1 THEN 'Y' ELSE 'N' END AS `Is Holiday`,
    st.Type                                AS `Region`,
    FORMAT(st.Size, 0)                     AS `Store Size (sq ft)`
FROM sales s
JOIN stores st USING (Store)
GROUP BY s.Store, s.Dept, DATE(s.`Date`), s.IsHoliday, st.Type, st.Size
ORDER BY s.Store, `Week Start`, s.Dept;
