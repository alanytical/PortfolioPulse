"""Optional one-off historical USD/NGN rates (NOT a substitute for the required Airbyte daily sync)."""
import argparse
from datetime import date, timedelta
from decimal import Decimal
import requests
from common import db_connect

URL='https://api.frankfurter.dev/v2/rate/usd/ngn'

def fetch(start_days):
    session=requests.Session(); items=[]
    for n in range(start_days, -1, -1):
        day=date.today()-timedelta(days=n)
        if day.weekday()>=5: continue
        response=session.get(URL,params={'date':day.isoformat()},timeout=20)
        response.raise_for_status()
        data=response.json()
        rate=Decimal(str(data['rate']))
        if data.get('base') != 'USD' or data.get('quote') != 'NGN' or rate <= 0:
            raise RuntimeError(f'Unexpected FX API response: {data}')
        items.append((data['date'],'USD','NGN',rate))
    return items

def load(items):
    with db_connect() as conn, conn.cursor() as cur:
        cur.execute('CREATE SCHEMA IF NOT EXISTS raw')
        cur.execute("""CREATE TABLE IF NOT EXISTS raw.exchange_rate_history
            (date date, base varchar(3), quote varchar(3), rate numeric(20,8) NOT NULL CHECK(rate>0),
             PRIMARY KEY(date,base,quote))""")
        cur.executemany("""INSERT INTO raw.exchange_rate_history(date,base,quote,rate)
            VALUES(%s,%s,%s,%s) ON CONFLICT(date,base,quote) DO UPDATE SET rate=EXCLUDED.rate""",items)
    print(f'Backfilled {len(items)} USD/NGN historical FX rates')

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--days',type=int,default=110)
    args=ap.parse_args()
    if args.days<1: raise ValueError('--days must be positive')
    load(fetch(args.days))
