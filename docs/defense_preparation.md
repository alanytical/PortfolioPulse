# PortfolioPulse defense — use only after actually running and verifying components

**30-second overview.** PortfolioPulse is an end-to-end data engineering platform that ingests daily stock closes from Yahoo Finance, a simulated trade history from Google Sheets via Airbyte, and USD/NGN FX from a custom Airbyte connector. The data lives in Neon Postgres, dbt Core transforms and tests it, GitHub Actions orchestrates the workflow, and Metabase visualizes daily portfolio values.

**Why use dbt?** SQL transformations are version-controlled, testable, documented, and separated into staging and marts.

**Why three sources?** Prices tell us market price; the trade log tells us how many shares and at what cost; exchange rates convert USD valuations to NGN.

**What is unrealized gain?** (Current shares × closing price) − sum(shares bought × price paid). The position is not sold, so the gain is not realized.

**How are re-runs handled?** Python UPSERTs prices on (date,ticker); Google Sheet sync is overwrite; FX observations are appended and deduplicated by rate date in dbt.

**What if an Airbyte sync fails?** Polling detects a failed terminal state and exits non-zero. GitHub Actions fails before dbt runs.

**Why self-hosted GitHub runner?** Local Airbyte at localhost cannot be reached by a GitHub-hosted runner. A runner on the Airbyte machine can connect without making the service publicly accessible.

**What if FX is missing?** We leave NGN historical value null for days without a prior actual rate. An optional history loader fills older dates without inventing rates.

**Trade limitations?** Purchase-only demo; selling, dividends, FX spreads, fees, and realized P&L are explicitly outside this capstone model.

**Demo flow (3–5 min).** (1) architecture & trade sheet (30 sec), (2) show price/FX/Sheet raw tables and counts (45 sec), (3) show Airbyte connection history (45 sec), (4) trigger/display green GitHub workflow with dbt tests (60 sec), (5) four Metabase dashboard cards (60 sec), (6) briefly explain cost basis & NGN conversion (30 sec). Do not claim green if it has not succeeded.
