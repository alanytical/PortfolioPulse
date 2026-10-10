-- Execute once on Neon as the owner via Neon SQL Editor or psql.
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE TABLE IF NOT EXISTS raw.stock_prices (
    price_date date NOT NULL,
    ticker varchar(16) NOT NULL,
    close_usd numeric(18,6) NOT NULL CHECK (close_usd > 0),
    volume bigint,
    ingested_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (price_date, ticker)
);
-- Optional historical backfill, separated from Airbyte's daily connector.
CREATE TABLE IF NOT EXISTS raw.exchange_rate_history (
    date date NOT NULL,
    base varchar(3) NOT NULL DEFAULT 'USD',
    quote varchar(3) NOT NULL DEFAULT 'NGN',
    rate numeric(20,8) NOT NULL CHECK (rate > 0),
    PRIMARY KEY (date, base, quote)
);
-- Airbyte creates raw.trade_log and raw.exchange_rates when connections run.
-- Do not pre-create those: Airbyte Direct Load owns their schemas.
