"""Idempotent, real Yahoo Finance daily close ingestion for 5 tickers."""
import argparse
from datetime import date, timedelta
from decimal import Decimal
import yfinance as yf
from common import db_connect

TICKERS = ['AAPL','MSFT','NVDA','GOOGL','AMZN']


def fetch_prices(tickers, days):
    start = date.today() - timedelta(days=days)
    end = date.today() + timedelta(days=1)
    rows = []
    for ticker in tickers:
        history = yf.Ticker(ticker).history(start=start.isoformat(),end=end.isoformat(), auto_adjust=False, actions=False)
        if history.empty:
            raise RuntimeError(f'No market data returned for {ticker}')
        for idx, bar in history.iterrows():
            close = bar.get('Close')
            if close is None or str(close) == 'nan' or float(close) <= 0:
                continue
            vol = bar.get('Volume')
            rows.append((idx.date(),ticker,Decimal(str(float(close))),int(vol) if vol is not None and str(vol) != 'nan' else None))
        print(f'{ticker}: {len(history)} daily price bars')
    if not rows: raise RuntimeError('No valid stock prices fetched')
    return rows


def load(rows):
    with db_connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""CREATE SCHEMA IF NOT EXISTS raw""")
            cur.execute("""CREATE TABLE IF NOT EXISTS raw.stock_prices (
                price_date date NOT NULL, ticker varchar(16) NOT NULL,
                close_usd numeric(18,6) NOT NULL CHECK(close_usd>0),
                volume bigint, ingested_at timestamptz NOT NULL DEFAULT now(),
                PRIMARY KEY(price_date,ticker))""")
            cur.executemany("""INSERT INTO raw.stock_prices(price_date,ticker,close_usd,volume)
                VALUES (%s,%s,%s,%s)
                ON CONFLICT(price_date,ticker) DO UPDATE
                SET close_usd=EXCLUDED.close_usd, volume=EXCLUDED.volume, ingested_at=now()""",rows)
    print(f'UPSERT complete: {len(rows)} date/ticker records')

if __name__ == '__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--days',type=int,default=110)
    args=ap.parse_args()
    if args.days < 1: raise ValueError('--days must be positive')
    load(fetch_prices(TICKERS,args.days))
