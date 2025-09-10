#!/usr/bin/env python3
"""
Export key tables/views from the SQLite DB to CSVs for quick Power BI import.
Usage:
  python src/export_csvs.py --db data/osrs.db --out data/exports
"""
import argparse
import os
import sqlite3
import pandas as pd

TABLES = ["items", "prices_daily", "market_index_daily", "game_events"]
VIEWS = ["item_returns", "mkt_returns", "drawdowns"]  # exported if they exist

def export_query(conn, name, query, out_dir):
    df = pd.read_sql_query(query, conn)
    path = os.path.join(out_dir, f"{name}.csv")
    df.to_csv(path, index=False)
    print(f"[ok] {name} -> {path} ({len(df)} rows)")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="data/osrs.db", help="Path to SQLite database")
    ap.add_argument("--out", default="data/exports", help="Output folder for CSVs")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    conn = sqlite3.connect(args.db)

    # Export base tables
    for t in TABLES:
        try:
            export_query(conn, t, f"SELECT * FROM {t}", args.out)
        except Exception as e:
            print(f"[warn] skipping table {t}: {e}")

    # Export views if present
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='view'")
    available_views = {row[0] for row in cur.fetchall()}

    for v in VIEWS:
        if v in available_views:
            try:
                export_query(conn, v, f"SELECT * FROM {v}", args.out)
            except Exception as e:
                print(f"[warn] skipping view {v}: {e}")
        else:
            print(f"[info] view not found, skipping: {v}")

    conn.close()
    print("[done] exports complete.")

if __name__ == "__main__":
    main()
