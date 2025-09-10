#!/usr/bin/env python3
"""
OSRS Safe Havens — data ingestor

- Pulls item master and timeseries prices from OSRS Wiki Prices API
- Stores to SQLite (default) or Postgres if DATABASE_URL provided
- Designed to run daily (Task Scheduler/cron)

Docs: https://prices.runescape.wiki/
"""
import argparse
import os
import sys
import time
import json
import sqlite3
import datetime as dt
from typing import Iterable, Dict, Any, List, Optional

try:
    import requests
except ImportError:
    print("Please install dependencies: pip install -r requirements.txt", file=sys.stderr)
    sys.exit(1)

BASE = "https://prices.runescape.wiki/api/v1/osrs"
UA = {"User-Agent": "sean-parker-osrs-safe-havens/1.0 (contact: seanryanparker@gmail.com)"}

def connect_sqlite(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def ensure_schema(conn: sqlite3.Connection) -> None:
    schema_path = os.path.join(os.path.dirname(__file__), "..", "sql", "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()

def fetch_items() -> Dict[str, Any]:
    url = f"{BASE}/mapping"
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    data = r.json()
    return data

def upsert_items(conn: sqlite3.Connection, mapping: List[Dict[str, Any]]) -> None:
    cur = conn.cursor()
    for m in mapping:
        cur.execute(
            """
            INSERT INTO items(item_id, name, category, tradeable, noted)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(item_id) DO UPDATE SET
              name=excluded.name,
              category=excluded.category,
              tradeable=excluded.tradeable,
              noted=excluded.noted
            """,
            (
                m.get("id"),
                m.get("name"),
                m.get("examine") or None,  # category placeholder (mapping lacks a strong category field)
                int(bool(m.get("tradeable", True))),
                int(bool(m.get("noted", False))),
            ),
        )
    conn.commit()

def fetch_timeseries(item_id: int, timestep: str = "day") -> Dict[str, Any]:
    url = f"{BASE}/timeseries?timestep={timestep}&id={item_id}"
    r = requests.get(url, headers=UA, timeout=60)
    r.raise_for_status()
    return r.json()

def upsert_prices(conn: sqlite3.Connection, item_id: int, rows: List[Dict[str, Any]]) -> None:
    cur = conn.cursor()
    for r in rows:
        # API uses epoch seconds
        d = dt.datetime.utcfromtimestamp(r["timestamp"]).date().isoformat()
        avg = r.get("avgHighPrice") or r.get("avgPrice") or None
        vol = r.get("highPriceVolume") or r.get("lowPriceVolume") or None
        cur.execute(
            """
            INSERT INTO prices_daily(item_id, price_date, avg_price_gp, volume)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(item_id, price_date) DO UPDATE SET
              avg_price_gp=COALESCE(excluded.avg_price_gp, prices_daily.avg_price_gp),
              volume=COALESCE(excluded.volume, prices_daily.volume)
            """,
            (item_id, d, avg, vol),
        )
    conn.commit()

TOP200_PLACEHOLDER = [995, 12934, 11840, 3140, 314, 385, 2434, 561, 563, 561, 560, 9075, 554, 555, 556, 557, 562, 564, 565, 566, 892, 11212]

def resolve_items_arg(items_arg: str, mapping: List[Dict[str, Any]]) -> List[int]:
    if items_arg == "top200":
        # Placeholder: supply a curated list or pick by volume once you have enough data.
        return list(dict.fromkeys(TOP200_PLACEHOLDER))  # unique + preserve order
    # Comma-separated ids or names
    ids = []
    names_to_id = {m["name"].lower(): m["id"] for m in mapping if "name" in m}
    for token in items_arg.split(","):
        token = token.strip()
        if not token:
            continue
        if token.isdigit():
            ids.append(int(token))
        else:
            if token.lower() in names_to_id:
                ids.append(names_to_id[token.lower()])
            else:
                print(f"[warn] Could not resolve item name: {token}", file=sys.stderr)
    return ids

def build_equal_weight_index(conn: sqlite3.Connection, basket_ids: List[int]) -> None:
    # Simple equal-weight: average normalized price across basket by base = first available price
    cur = conn.cursor()
    # Create temp table of base prices per item (first non-null price)
    cur.execute("DROP TABLE IF EXISTS tmp_base")
    cur.execute("""
        CREATE TEMP TABLE tmp_base AS
        SELECT p.item_id, MIN(price_date) AS first_date
        FROM prices_daily p
        WHERE p.item_id IN (%s)
        GROUP BY p.item_id
    """ % ",".join("?"*len(basket_ids)), basket_ids)
    cur.execute("""
        CREATE TEMP TABLE tmp_base_price AS
        SELECT p.item_id, p.avg_price_gp AS base_price
        FROM prices_daily p
        JOIN tmp_base b ON b.item_id = p.item_id AND b.first_date = p.price_date
    """)
    # Build normalized series
    cur.execute("DROP TABLE IF EXISTS tmp_norm")
    cur.execute(f"""
        CREATE TEMP TABLE tmp_norm AS
        SELECT p.price_date,
               p.item_id,
               CASE WHEN bp.base_price IS NULL OR p.avg_price_gp IS NULL
                    THEN NULL
                    ELSE p.avg_price_gp / bp.base_price
               END AS norm_price
        FROM prices_daily p
        LEFT JOIN tmp_base_price bp ON bp.item_id = p.item_id
        WHERE p.item_id IN ({",".join("?"*len(basket_ids))})
    """, basket_ids)
    # Aggregate to index
    cur.execute("""
        INSERT OR REPLACE INTO market_index_daily(price_date, mkt_index_gp)
        SELECT price_date, AVG(norm_price)
        FROM tmp_norm
        GROUP BY price_date
        HAVING COUNT(norm_price) >= 3  -- require some coverage
    """)
    conn.commit()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="data/osrs.db", help="SQLite database file path")
    ap.add_argument("--items", default="top200", help="Comma-separated ids or names, or 'top200' placeholder")
    ap.add_argument("--timestep", default="24h", choices=["5m","1h","6h","24h"])
    ap.add_argument("--build-index", action="store_true", help="Timeseries granularity per OSRS Wiki API")
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.db), exist_ok=True)
    conn = connect_sqlite(args.db)
    ensure_schema(conn)

    print("[info] Fetching item mapping...")
    mapping = fetch_items()
    if isinstance(mapping, dict) and "data" in mapping:
        mapping = mapping["data"]
    upsert_items(conn, mapping)
    print(f"[info] Loaded {len(mapping)} items into 'items'")

    ids = resolve_items_arg(args.items, mapping)
    if not ids:
        print("[error] No items resolved. Exiting.")
        sys.exit(2)

    for i, item_id in enumerate(ids, 1):
        try:
            ts = fetch_timeseries(item_id, timestep=args.timestep)
            rows = ts.get("data") or ts.get("daily") or ts.get("prices") or []
            upsert_prices(conn, item_id, rows)
            print(f"[{i}/{len(ids)}] item_id={item_id} ok (rows={len(rows)})")
            time.sleep(0.25)  # be polite
        except Exception as e:
            print(f"[warn] item_id={item_id} failed: {e}", file=sys.stderr)

    if args.build_index:
        print("[info] Building equal-weight market index...")
        build_equal_weight_index(conn, ids)
        print("[info] Market index updated.")

    print("[done] Ingestion complete.")

if __name__ == "__main__":
    main()
