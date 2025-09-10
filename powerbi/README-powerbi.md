# Power BI setup

1) **Connect to data**
   - Option A (SQLite): Install an SQLite ODBC driver and connect to `data/osrs.db`.
   - Option B (CSV): Export tables using `sqlite3` or Python and import into Power BI.

2) **Model**
   - Import: `items`, `prices_daily`, `market_index_daily`, `game_events`.
   - Create measures:
     - Daily Return
     - Rolling Volatility (30)
     - Max Drawdown
     - Beta vs Market
     - Median Return on Crisis Days
     - Composite Safe Haven Score

3) **Pages**
   - Overview (leaderboard + slicers)
   - Item deep dive (price, drawdown, rolling vol, event markers)
   - Market stress analyzer (filter on market down days)
   - Correlation matrix (item vs market, item vs item)

4) **Formatting**
   - Use conditional formatting (reds/greens) for drawdown and returns
   - Add tooltips with quick stats


---

## Starter Pack (use these in Power BI)
- **Theme.json**: View → Themes → Browse for themes → select this file.
- **PowerQuery-Queries.pq**: Power Query → New Source → Blank Query → Advanced Editor → paste contents. Replace `BasePath` with your local repo path to `/data/exports`.
- **DAX-Measures.dax**: Create measures in the Model view and paste definitions here. Add a simple Date table and relationships (see comments at the top of the file).

> Tip: After running `export_csvs.py`, point the queries to `data/exports/` and refresh. Then add visuals using the measures.
