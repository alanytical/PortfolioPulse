import os
from dotenv import load_dotenv
import psycopg
load_dotenv()

def database_url():
    url = os.environ.get('NEON_DATABASE_URL', '').strip()
    if not url or 'REPLACE_ME' in url or 'PASSWORD@HOST' in url:
        raise RuntimeError('Set NEON_DATABASE_URL in .env or environment (do not commit it).')
    return url

def db_connect():
    return psycopg.connect(database_url(), connect_timeout=25)
