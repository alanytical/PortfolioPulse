# PortfolioPulse — One-page design decisions

**Purpose.** Answer: What is a chosen investment portfolio worth in USD and NGN through time? The demonstration holds 5 US equities (AAPL, MSFT, NVDA, GOOGL, AMZN) using clearly labelled **simulated purchase-only trades**; prices and exchange rates come from external market sources.

**Ingestion.** Yahoo Finance historical daily closes are fetched with Python (`yfinance`) and idempotently UPSERTed into Neon `raw.stock_prices`. An Airbyte Google Sheets source ingests a manually maintained trade log into `raw.trade_log`, configured full-refresh overwrite so edits are reflected without duplicates. A custom Airbyte connector reads a USD/NGN daily exchange rate and appends to `raw.exchange_rates`. Optional historical FX backfill is held separately in `raw.exchange_rate_history` and is not claimed to be a daily Airbyte sync.

**Warehouse.** Neon Postgres holds raw inputs and downstream analytical views. dbt Core defines one staging model for each source and marts for daily per-ticker valuations, daily portfolio totals, and the latest allocation. Tests catch null keys, duplicate positions and invalid trade sizes.

**Valuation method.** At each available stock closing date, shares held equals purchases dated on/before that date. Historical cost is the sum of shares times trade price paid. Market value in USD = shares × latest close for that date. Unrealized USD gain/loss = market value − cost. NGN value = USD market value × most recent actual USD/NGN rate observed no later than the stock date. Historical dates lacking an FX observation show NULL rather than a fabricated number. US market/non-trading days and changing FX quote conventions can cause gaps.

**Orchestration.** GitHub Actions sequentially ingests quotes, triggers & polls two Airbyte jobs, and runs dbt models + tests. It fails on errors. Because Airbyte Core is hosted locally, the workflow is configured for a self-hosted GitHub runner on the same network, and requires that computer to be online at scheduled times.

**Visualization & scope.** Self-hosted Metabase connects read-only to Neon and plots time series, position gain/loss, allocation and USD/NGN comparison. It tracks market value, not realized performance or returns including fees, dividends, taxes, stock splits, corporate actions, or actual brokerage balances. Trades are demo data and are not financial advice.
