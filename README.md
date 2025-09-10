# ⚔️ Oldschool RuneScape Safe Haven Assets
### 🪙 Measuring Volatility and Drawdowns in the Grand Exchange
<br>
Which Old School RuneScape items behave like gold during a market crash?  
This project identifies items that act as safe haven assets, holding or gaining value during market stress, using financial analysis techniques.
<br><br>

![Dashboard Screenshot](docs/dashboard.png)

---

## 📄 Project Description
**OSRS Safe Haven Assets** is a full-stack data analytics project built on a fun dataset: the Grand Exchange prices from Old School RuneScape.  

- **Python** — pulls item prices via the OSRS Wiki API, stores them in SQLite.  
- **SQL** — creates tables and views for returns, drawdowns, and market indexes.  
- **Power BI** — interactive dashboard for rolling volatility, drawdowns, and leaderboards.  
- **DAX** — measures for volatility, max drawdown, and a composite Safe Haven Score.  

This project demonstrates:  
- Data engineering (ETL and pipeline design)  
- Time-series & financial-style analysis  
- Data visualization & storytelling with Power BI  
- A creative crossover between **gaming economics** and **financial analytics**  

---

## ❓ Problem
In financial markets, investors look for “safe haven assets” like gold or bonds that hold value during downturns.  
Could similar behavior be found in **RuneScape’s Grand Exchange** — a player-driven economy with thousands of tradeable items?

---

## 🔎 Approach
1. **Data ingestion**  
   - Pulled item mappings and daily price time series from the [OSRS Wiki API](https://prices.runescape.wiki/).  
   - Stored ~500+ high-volume items in a local SQLite database.  

2. **Data modeling**  
   - SQL views for returns, rolling volatility, drawdowns, and a market index.  
   - Exported cleaned CSVs for easy import into Power BI.  

3. **Analysis & scoring**  
   - DAX measures for:  
     - Rolling 30-day volatility  
     - Max drawdown  
     - Composite Safe Haven Score (low volatility + shallow drawdown = safer)  

4. **Visualization**  
   - Power BI dashboard with slicers, time-series charts, and leaderboards.  
   - Users can filter to a specific item and instantly compare stability.  

---

## 📊 Solution (Dashboard)
The final dashboard includes:  
- **Interactive slicer** → choose any tradeable item.  
- **Rolling volatility chart** → see how stable prices are over time.  
- **Drawdown analysis** → measure worst peak-to-trough declines.  
- **Leaderboard** → rank items by Safe Haven Score.  

![Leaderboard Screenshot](docs/leaderboard.png)

---

## 🛠️ Tech Stack
- **Python** — requests, pandas, sqlite3  
- **SQL** — schema, views, and metrics  
- **Power BI** — dashboard visuals  
- **DAX** — financial measures  
- **GitHub Actions** — simple CI linting  

---

## 🚀 Quickstart
```bash
# Clone repo
git clone https://github.com/YOURUSERNAME/osrs-safe-havens.git
cd osrs-safe-havens

# Set up environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Ingest data
python src/ingest.py --db data/osrs.db --items top200 --build-index

# Export for Power BI
python src/export_csvs.py --db data/osrs.db --out data/exports
