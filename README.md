# ⚔️ Oldschool RuneScape Safe Haven Assets
### 🪙 Measuring Volatility and Drawdowns in the Grand Exchange

Which Old School RuneScape items behave like gold during a market crash?  
This project identifies items that act as safe haven assets, holding or gaining value during market stress, using financial analysis techniques.

![Dashboard Screenshot](docs/dashboard.png)

---

## Project Description
**OSRS Safe Haven Assets** is a full-stack data analytics project built on a fun dataset: the Grand Exchange prices from Old School RuneScape.  

- **Python** for data ingestion, storing OSRS Wiki API data in SQLite  
- **SQL** for returns, drawdowns, and market index modeling  
- **Power BI** for an interactive dashboard with volatility charts and leaderboards  
- **DAX** for volatility, max drawdown, and a composite Safe Haven Score  

This project demonstrates:  
- Data engineering through ETL and pipeline design  
- Time-series and financial-style analysis  
- Data visualization and storytelling with Power BI  
- A creative crossover between gaming economics and financial analytics

---

## Problem
In financial markets, investors look for “safe haven assets” like gold or bonds that hold value during downturns.  
Could similar behavior be found in RuneScape’s Grand Exchange, a player-driven economy with thousands of tradeable items?

---

## Financial Analysis Context
In finance, a market downturn is typically defined as a sustained decline in asset prices, often measured by peak-to-trough drawdowns or broad index losses over time. Downturns can be triggered by many factors, such as shifts in supply and demand, macroeconomic events, or sudden shocks that reduce investor confidence. The result is increased volatility and sharper drawdowns as market participants sell off riskier assets.  

The purpose of this project was to apply those same concepts to a virtual economy, Old School RuneScape’s Grand Exchange. By calculating volatility and drawdowns on in-game items, the analysis highlights which assets behave like safe havens, retaining value when the broader market weakens. This demonstrates how financial analysis techniques can be adapted to unconventional datasets and provides a practical way to connect data engineering, SQL modeling, and visualization skills to real-world economic principles.  

---

## Approach

1. **Data ingestion**  
   The project starts with collecting live item data from the [OSRS Wiki API](https://prices.runescape.wiki/). Item mappings and daily price histories were pulled and written into a local SQLite database, which provides a lightweight but reliable backend for time-series storage. Instead of tracking every single item in the game, the pipeline focuses on ~500 of the most actively traded items to balance coverage and performance. This dataset is refreshed in batches and normalized for downstream analysis.  

2. **Data modeling**  
   Once the raw data was captured, SQL was used to transform it into structured views. These views calculate daily returns, rolling volatility windows, drawdowns, and an equal-weighted market index that acts as a benchmark. By centralizing the business logic in SQL, the project ensures consistency and reusability across exports and visualizations. Cleaned tables and views were exported to CSVs so that Power BI could consume them directly.  

3. **Analysis and scoring**  
   In Power BI, DAX measures were defined to quantify financial metrics at the item level. Key measures included:  
   - **Rolling 30-day volatility**: standard deviation of daily returns across a 30-day window  
   - **Max drawdown**: largest peak-to-trough price decline over the dataset  
   - **Safe Haven Score**: a composite rank that rewards low volatility and shallow drawdowns  
   This scoring framework allows items to be compared fairly across categories and trading volumes.  

4. **Visualization**  
   The analysis is surfaced in a Power BI dashboard designed for exploration. Users can:  
   - Filter with slicers to isolate specific items  
   - View time-series charts that track volatility and price stability  
   - Compare items side by side in a leaderboard ranked by Safe Haven Score  
   These visuals connect financial theory with game data, turning raw numbers into insights about how RuneScape’s economy mirrors real-world market behavior.  

---

## Solution (Dashboard)
The final dashboard includes:  
- Interactive slicer to choose any tradeable item  
- Rolling volatility chart to see how stable prices are over time  
- Drawdown analysis to measure worst peak-to-trough declines  
- Leaderboard to rank items by Safe Haven Score  

![Leaderboard Screenshot](docs/leaderboard.png)  
*Safe Haven Leaderboard, ranking items by volatility and drawdowns*

---

## Tech Stack
- **Python** — requests, pandas, sqlite3  
- **SQL** — schema, views, and metrics  
- **Power BI** — dashboard visuals  
- **DAX** — financial measures  
- **GitHub Actions** — simple CI linting  

---

## Quickstart
```bash
# Clone repo
git clone https://github.com/YOURUSERNAME/osrs-safe-havens.git
cd osrs-safe-havens

# Set up environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Ingest data (top 100 most-traded items by default)
python src/ingest.py --db data/osrs.db --items topN --top-n 100 --build-index

# Export for Power BI
python src/export_csvs.py --db data/osrs.db --out data/exports
```
---

## Lessons Learned

- Even in a virtual economy, traditional financial metrics such as volatility and drawdown provide valuable insights. They highlight which assets behave defensively and which are more speculative, reinforcing that the principles of market analysis can extend beyond real-world finance.  

- Certain items, like runes and feathers, consistently acted as safe havens because of constant in-game demand. This mirrors the way commodities such as gold or bonds maintain value during economic downturns, showing how player-driven economies often reflect real economic forces.  

- Designing a clean pipeline — from Python ingestion, to SQL modeling, to BI visualization — made the project maintainable and reusable. Each stage had a clear role, and by separating concerns it became much easier to iterate and scale the analysis.  

- Translating financial concepts into a gaming context proved to be a powerful way to practice analytics. It made technical skills like ETL, DAX, and visualization more engaging while also strengthening the ability to explain complex ideas in a simple, relatable way.  

- The project also emphasized the importance of storytelling in analytics. Numbers alone don’t capture attention, but framing them around the idea of “safe havens” in RuneScape connected the data to a narrative that anyone familiar with finance or gaming could appreciate.  

---

## Attribution
- Price data: [OSRS Wiki Prices API](https://prices.runescape.wiki/)  
- RuneScape © Jagex Ltd. This is a fan-made educational project.

---

[LICENSE](https://github.com/SparkerData/OSRS-Safe-Haven-Assets/blob/5c47b7030404697ce8249e71fd264c9d358e4c76/LICENSE)
