-- Purpose: Explore seasonality by Month and Quarter, and trends by Year×Month / Year×Quarter.
-- Formatting: returns raw revenue and a readable $ column.

-- By month (all years combined)
SELECT
  EXTRACT(MONTH FROM DATE(`Date`))                          AS month,
  SUM(Weekly_Sales)                                         AS revenue_raw,
  CONCAT('$', FORMAT(SUM(Weekly_Sales), 2))                 AS revenue_usd
FROM sales
GROUP BY EXTRACT(MONTH FROM DATE(`Date`))
ORDER BY month;

-- By quarter (all years combined)
SELECT
  EXTRACT(QUARTER FROM DATE(`Date`))                        AS quarter,
  SUM(Weekly_Sales)                                         AS revenue_raw,
  CONCAT('$', FORMAT(SUM(Weekly_Sales), 2))                 AS revenue_usd
FROM sales
GROUP BY EXTRACT(QUARTER FROM DATE(`Date`))
ORDER BY quarter;

-- Year + month (trend over time)
SELECT
  EXTRACT(YEAR  FROM DATE(`Date`))                          AS year,
  EXTRACT(MONTH FROM DATE(`Date`))                          AS month,
  SUM(Weekly_Sales)                                         AS revenue_raw,
  CONCAT('$', FORMAT(SUM(Weekly_Sales), 2))                 AS revenue_usd
FROM sales
GROUP BY EXTRACT(YEAR FROM DATE(`Date`)), EXTRACT(MONTH FROM DATE(`Date`))
ORDER BY year, month;

-- Year + quarter (trend over time)
SELECT
  EXTRACT(YEAR    FROM DATE(`Date`))                        AS year,
  EXTRACT(QUARTER FROM DATE(`Date`))                        AS quarter,
  SUM(Weekly_Sales)                                         AS revenue_raw,
  CONCAT('$', FORMAT(SUM(Weekly_Sales), 2))                 AS revenue_usd
FROM sales
GROUP BY EXTRACT(YEAR FROM DATE(`Date`)), EXTRACT(QUARTER FROM DATE(`Date`))
ORDER BY year, quarter;
