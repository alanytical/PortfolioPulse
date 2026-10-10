import sys
from common import db_connect
SQL={
    'prices': 'select count(*) from raw.stock_prices',
    'trades': 'select count(*) from raw.trade_log',
    'airbyte_fx': 'select count(*) from raw.exchange_rates',
    'portfolio': 'select count(*) from analytics.mart_portfolio_value',
}
if __name__=='__main__':
    failed = False
    with db_connect() as conn, conn.cursor() as cur:
        for name,query in SQL.items():
            try:
                cur.execute(query); count=cur.fetchone()[0]; print(f'{name}: {count} rows')
                if count == 0: failed = True
            except Exception as exc:
                conn.rollback(); failed = True; print(f'{name}: NOT READY - {type(exc).__name__}: {exc}')
    if failed: raise SystemExit('ERROR: one or more required sources/marts are missing or empty')
    print('PASS: all four required source and mart tables contain data')
