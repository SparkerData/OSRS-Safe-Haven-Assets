#!/usr/bin/env python3
"""
Export SQLite tables to CSVs for dead-simple Power BI import.

Usage:
  python src/export_csv.py --db data/osrs.db --outdir data/exports
"""
import argparse
import os
import sqlite3
import pandas as pd

TABLES = ["items", "prices_daily", "market_index_daily", "game_events"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="data/osrs.db", help="Path to SQLite database")
    ap.add_argument("--outdir", default="data/exports", help="Directory to write CSV files")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    conn = sqlite3.connect(args.db)

    for tbl in TABLES:
        try:
            df = pd.read_sql_query(f"SELECT * FROM {tbl}", conn)
            out_path = os.path.join(args.outdir, f"{tbl}.csv")
            df.to_csv(out_path, index=False)
            print(f"[ok] Exported {tbl} -> {out_path} ({len(df)} rows)")
        except Exception as e:
            print(f"[warn] Failed to export {tbl}: {e}")

    conn.close()

if __name__ == "__main__":
    main()
