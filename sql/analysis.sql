-- Build daily log returns for items and market
DROP VIEW IF EXISTS item_returns;
CREATE VIEW item_returns AS
SELECT
  item_id,
  price_date,
  (CASE
     WHEN LAG(avg_price_gp) OVER (PARTITION BY item_id ORDER BY price_date) IS NULL
     THEN NULL
     ELSE LOG(avg_price_gp) - LOG(LAG(avg_price_gp) OVER (PARTITION BY item_id ORDER BY price_date))
   END) AS ret
FROM prices_daily;

DROP VIEW IF EXISTS mkt_returns;
CREATE VIEW mkt_returns AS
SELECT
  price_date,
  (CASE
     WHEN LAG(mkt_index_gp) OVER (ORDER BY price_date) IS NULL
     THEN NULL
     ELSE LOG(mkt_index_gp) - LOG(LAG(mkt_index_gp) OVER (ORDER BY price_date))
   END) AS mkt_ret
FROM market_index_daily;

-- Rolling volatility (30-day) — window frames supported on modern SQLite builds
DROP VIEW IF EXISTS rolling_vol_30;
CREATE VIEW rolling_vol_30 AS
SELECT
  item_id,
  price_date,
  -- Approximate rolling stddev via windowed aggregates; SQLite has no STDDEV by default.
  -- For portability, compute in Power BI or export and compute in Python if needed.
  NULL AS vol_30_placeholder
FROM item_returns;

-- Drawdown
DROP VIEW IF EXISTS drawdowns;
CREATE VIEW drawdowns AS
WITH series AS (
  SELECT item_id, price_date, avg_price_gp,
         MAX(avg_price_gp) OVER (PARTITION BY item_id ORDER BY price_date
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS run_peak
  FROM prices_daily
)
SELECT item_id, price_date,
       (avg_price_gp / NULLIF(run_peak, 0.0)) - 1.0 AS drawdown
FROM series;
