# PortfolioPulse build guide — execute and verify, do NOT skip gates

## 0. Check that you still have a working Airbyte instance

On WSL Ubuntu, start Docker Desktop on Windows. Run:

```bash
abctl local status
abctl local credentials
```

Open `http://localhost:8000` on Windows. The second command displays **secrets**. Never send passwords/client secrets in chat, screenshots, public GitHub or demonstration. If Airbyte is `pending-upgrade`, fix its deployment **before** adding connectors; check `abctl` docs and available resources.

## 1. Project and Neon

1. Create a FREE Neon account/project: https://console.neon.tech/ and a database (usually `neondb`). Copy a Postgres connection URL (SSL required) into `.env` as `NEON_DATABASE_URL`.
2. Run `sql/01_initialize.sql` in Neon SQL Editor.
3. Prefer Python 3.11 for dbt compatibility. If uv is installed: `uv python install 3.11 && uv venv --python 3.11 .venv && source .venv/bin/activate && uv pip install -r requirements.txt`. If not, use a supported local Python 3.11 environment and `pip install -r requirements.txt`.
4. `python scripts/ingest_prices.py --days 110` and confirm `SELECT count(*),min(price_date),max(price_date) FROM raw.stock_prices;` in Neon.

## 2. Google Sheet -> Airbyte -> Neon

1. Google Drive -> new Google Sheet -> rename worksheet/tab **trade_log**. Import `data/trade_log.csv` (File > Import). Those are simulated trades, not real investments.
2. In Google Cloud Console create a project, enable **Google Sheets API**, create a service account, and create a service-account JSON key, using the Airbyte Google Sheets source setup guide: https://docs.airbyte.com/integrations/sources/google-sheets .
3. Share the Google Sheet with that service account EMAIL as Viewer. Do NOT commit the JSON key.
4. In local Airbyte -> Sources -> Google Sheets, use service-account JSON as secure UI input, paste Sheet URL, enable SQL-compliant column names, test.
5. Destinations -> Postgres -> enter Neon **host, port, database, username, password**; SSL mode as required by Neon. You may need the **direct/unpooled** Neon hostname for the connector to work well. Test connection.
6. Create connection -> map Sheet tab stream `trade_log` to namespace `raw`, table `trade_log`, no prefix. **Full Refresh / Overwrite**. Disable its own schedule if GitHub Actions orchestrates it.
7. Press Sync now, WAIT for Succeeded. Verify with `SELECT * FROM raw.trade_log LIMIT 5;`. If table named differently, update Airbyte naming to match or dbt source definition.

## 3. Custom USD->NGN Connector -> Airbyte -> Neon

1. Check `https://api.frankfurter.dev/v2/rate/usd/ngn` in browser. The response is expected to be one JSON record, e.g. `{"date":"YYYY-MM-DD","base":"USD","quote":"NGN","rate":NUMBER}` (values supplied by API, never fabricated). If unavailable, pause and choose another documented free USD/NGN source — data structures and connector settings then must be adapted.
2. Airbyte -> Builder -> New custom connector (or import/test `airbyte/fx_connector.yaml`). Select HTTPS API root `https://api.frankfurter.dev/v2/`, path `rate/usd/ngn`, GET, no authentication, one record in JSON **root**, fields `date`, `base`, `quote`, `rate`; no pagination. Preview/Test should show a real current USD/NGN rate.
3. Publish custom source for your workspace. Create a source from it and connect to your existing Neon destination.
4. Name the destination stream `exchange_rates` in namespace `raw`; use **Full Refresh / Append** (not Overwrite — old daily observations must survive). Disable separate Airbyte scheduling (GitHub handles scheduling).
5. Sync now and confirm in Neon: `SELECT * FROM raw.exchange_rates ORDER BY date DESC LIMIT 5;`.
6. (Optional historical data) `python scripts/backfill_fx.py --days 110` saves actual historical FX observations into a separate source table for dbt. It does not replace the required Airbyte connection.

## 4. dbt Core

```
python scripts/run_dbt.py debug
python scripts/run_dbt.py run
python scripts/run_dbt.py test
python scripts/check_data.py
pytest -q
```

If dbt says relation missing, check in Neon:

```
select table_schema, table_name
from information_schema.tables
where table_schema in ('raw','staging','analytics')
order by table_schema,table_name;
```

Check dbt is really writing to `staging`/`analytics` (macro provided). Data types from Airbyte Google Sheets will initially be strings; staging casts them. If source values contain currency symbols, commas or invalid dates, clean the Sheet.

## 5. GitHub Actions — local Airbyte restriction

1. GitHub: create a **private repository**, push starter project; `.env` excluded via `.gitignore`.
2. Repo Settings -> Secrets and variables -> Actions -> New repository secret: `NEON_DATABASE_URL`, `AIRBYTE_CLIENT_ID`, `AIRBYTE_CLIENT_SECRET`, `AIRBYTE_TRADES_CONNECTION_ID`, `AIRBYTE_FX_CONNECTION_ID`. Get client credentials from `abctl local credentials`; get connection UUIDs from Airbyte connection UI. Don't paste them into chat.
3. Repo Settings -> Actions -> Runners -> New self-hosted runner -> Linux x64. Install/start the runner from your Ubuntu WSL machine following GitHub's own shown commands (its download token is sensitive). Install Python 3.11 if needed. **Do not configure GitHub self-hosted runner on a public repository** for safety.
4. Make sure `http://localhost:8000` is reachable from the same WSL account that runs the runner. If Airbyte URL differs, edit the workflow AIRBYTE_API_URL.
5. GitHub Actions -> PortfolioPulse daily pipeline -> Run workflow. Watch ALL steps. Screenshot the successful run for defense.
6. CRITICAL: the self-hosted runner must stay online, and Airbyte must stay running daily. GitHub cron is UTC. If the machine sleeps, the job may queue or miss execution.

### First manual run / connection API

`python scripts/run_airbyte.py` submits POST to `/api/public/v1/jobs` and polls `/jobs/{id}` to completion. It requests an access token from `/api/public/v1/applications/token`. Your installed Airbyte version may use a slightly different authorization endpoint or API shape; verify with https://docs.airbyte.com/developers/api-documentation and correct after observing an actual API response. No secrets in logs.

## 6. Metabase Docker local dashboard

Start Docker Desktop. On Ubuntu or Windows terminal with Docker CLI:

```
docker run -d --name portfoliopulse-metabase -p 3000:3000 metabase/metabase:latest
```

Open `http://localhost:3000`, complete initial setup, select PostgreSQL and enter Neon credentials. Choose a read-only role if already created. Create four charts from `docs/dashboard_queries.sql`; assemble one `PortfolioPulse` dashboard; screenshot it showing real computed numbers. Metabase local at port 3000 is for visualization; Neon holds data remotely.

## 7. ER diagram and review access

`docs/er_diagram.svg` illustrates logical table relationships. Save or print as PDF/image into the Drive folder as required. Run `docs/readonly_role.sql` *after* creating marts, replacing database name and placeholder password. Connect as reviewer to check a SELECT succeeds and INSERT/CREATE fails. Give reviewer credentials only through the approved secure submission channel — not in a public repo, video, or unprotected Drive document.

## 8. Final submission

In the cohort general assignment Google Drive folder, create a folder named exactly `Capstone Project`. Add the diagram, one-page design decisions (`docs/design_decisions.md`, export as PDF if desired), **actual** dashboard screenshots, and a 3–5 minute screen recording showing actual runs. Confirm all links work in incognito. Email GitHub URL, Drive folder URL, and video URL together to `pspanalytics20@gmail.com` on/before 2026-10-10. Do not describe anything that has not been run as complete.
