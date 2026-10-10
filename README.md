# PortfolioPulse — Global Investment Analytics Platform

> **Status:** project *starter*, not a deployed or verified end-to-end system. Configure Neon, Google Sheets, both Airbyte connections, the self-hosted GitHub runner, and Metabase before describing it as working. Strictly **no paid tools**: use free-tier Neon and locally hosted Airbyte/Metabase.

## Pipeline

- **Sources:** Yahoo Finance daily closes for AAPL, MSFT, NVDA, GOOGL, AMZN; simulated trades in Google Sheets; Frankfurter USD/NGN API (custom Airbyte source).
- **Warehouse:** Neon Postgres, `raw` tables.
- **Transformation:** dbt Core staging and marts (`analytics`), with schema and custom tests.
- **Orchestration:** GitHub Actions on a daily UTC cron, run by an online **self-hosted** Linux runner with access to your local Airbyte.
- **Dashboard:** local Metabase Docker app connected to Neon.

### Critical prerequisite: local vs hosted GitHub runners

If Airbyte runs at `http://localhost:8000` **on your Windows/WSL machine**, the ordinary GitHub-hosted Ubuntu runner cannot reach it. `.github/workflows/pipeline.yml` therefore targets a **self-hosted** Linux runner in the same environment/network. See `docs/setup_steps.md`. The machine must stay on for scheduled runs. Do **not** make unauthenticated local Airbyte publicly reachable.

## Quickstart (Ubuntu WSL)

```bash
unzip PortfolioPulse_Starter.zip       # only if downloaded as zip
cd PortfolioPulse_Starter
uv python install 3.11                 # if you have uv installed; one-time download
uv venv --python 3.11 .venv
source .venv/bin/activate
uv pip install -r requirements.txt
cp .env.example .env
# Edit .env and set real NEON_DATABASE_URL locally. NEVER upload this file.
```

Run `sql/01_initialize.sql` in Neon SQL Editor. Then:

```bash
python scripts/ingest_prices.py --days 110
# Configure Google Sheet and BOTH Airbyte connectors; run each sync first.
python scripts/run_airbyte.py
python scripts/run_dbt.py debug
python scripts/run_dbt.py run
python scripts/run_dbt.py test
python scripts/check_data.py
pytest -q
```

Optional: `python scripts/backfill_fx.py --days 110` to obtain daily historical rates. This may make many external requests; check the provider response and terms. It is NOT the required daily Airbyte FX sync.

Read **`docs/setup_steps.md`** for every setup screen, scripts and checks.

## Source schema contract

Airbyte destination needs two final tables and these exact columns:

```
raw.trade_log: trade_id, trade_date, ticker, shares_bought, price_paid
raw.exchange_rates: date, base, quote, rate
```

The Google Sheet must have a tab named `trade_log` and exactly those headers (copy `data/trade_log.csv` into a Sheet, then set column conversion on). Airbyte needs destination namespace `raw` and no stream prefix. If Airbyte displays different table names/schema (possible with current Direct Load versions), inspect them and adjust the dbt sources or stream name mappings before `dbt run`; do NOT invent data. Google Sheets `trade_log` must be **Full Refresh / Overwrite**. FX must be **Full Refresh / Append** (to preserve daily historical rates).

The sheet data is simulated. It does not mean you bought these securities.

## Core dbt marts

- `mart_portfolio_value`: position/day, USD close, shares, cost, gain/loss, FX, NGN value.
- `mart_portfolio_daily`: aggregated USD and NGN portfolio value over time.
- `mart_latest_positions`: latest allocation % and gain/loss.

`dbt_project.yml` uses schema aliases by default, and may create `public_staging` and `public_analytics` under dbt's usual Postgres schema naming policy. For this starter we REQUIRE the final marts in `analytics` and staging in `staging`. **See the custom schema macro in `dbt/macros/generate_schema_name.sql`.**

## Quality controls

- Schema tests: not_null, unique.
- Singular dbt tests: no negative trades; unique dated ticker positions; no future purchases in earlier valuations.
- Workflow stops on non-zero exit codes from price ingestion, either Airbyte sync, or dbt.

## 4 Metabase visualizations

1. Time-series line: `analytics.mart_portfolio_daily.price_date` vs `total_value_usd`.
2. Position gain/loss bar: ticker vs unrealized gain/loss from `mart_latest_positions`.
3. Allocation pie/donut: ticker vs position USD value from `mart_latest_positions`.
4. Table: latest ticker value USD and NGN side-by-side (or two dashboard number cards).

If historical NGN values are missing, run optional historical FX backfill and re-run dbt. Do not fill gaps with made-up FX rates.

## Deliverables

- GitHub: this repository (sans `.env`) and successful workflow run.
- Google Drive: `Capstone Project` folder in the cohort general assignment folder containing ER diagram, design decisions, and real Metabase screenshots.
- 3–5 minute video showing **actual live pipeline** and dashboard.
- Live Neon DB and a properly constrained read-only reviewer login.
- Email all links to pspanalytics20@gmail.com **by Saturday 2026-10-10**; verify in incognito.

## Data-source caveats

Yahoo Finance data can be delayed, revised and unavailable. The demo's purchase prices are synthetic, and historic market values need real historical FX prices. The `Frankfurter` service is a free public API but check NGN coverage and response before configuring the connector. There is no order-book or broker reconciliation.
