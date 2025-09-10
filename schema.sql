-- Create core tables (SQLite syntax)
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS items (
  item_id      INTEGER PRIMARY KEY,
  name         TEXT NOT NULL,
  category     TEXT,
  tradeable    INTEGER,
  noted        INTEGER
);

CREATE TABLE IF NOT EXISTS prices_daily (
  item_id      INTEGER NOT NULL REFERENCES items(item_id),
  price_date   DATE NOT NULL,
  avg_price_gp REAL,
  volume       REAL,
  PRIMARY KEY (item_id, price_date)
);

CREATE TABLE IF NOT EXISTS market_index_daily (
  price_date   DATE PRIMARY KEY,
  mkt_index_gp REAL
);

CREATE TABLE IF NOT EXISTS game_events (
  event_date   DATE,
  label        TEXT,
  details      TEXT
);
