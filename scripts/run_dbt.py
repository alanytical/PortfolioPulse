"""Pass Neon URL credentials to dbt-postgres without saving secrets in repository."""
import os, subprocess, sys
from urllib.parse import urlsplit, unquote, parse_qs
from common import database_url

def env_for_dbt(url):
    u=urlsplit(url)
    if u.scheme not in ('postgres','postgresql') or not u.hostname or not u.username:
        raise ValueError('Expected postgresql://... Neon connection URL')
    q=parse_qs(u.query)
    env=os.environ.copy()
    env.update(PGHOST=u.hostname,PGPORT=str(u.port or 5432),PGDATABASE=unquote(u.path.lstrip('/')),
               PGUSER=unquote(u.username),PGPASSWORD=unquote(u.password or ''),
               PGSSLMODE=q.get('sslmode',['require'])[0])
    return env

if __name__=='__main__':
    if len(sys.argv)<2 or sys.argv[1] not in ('debug','run','test','build','compile','docs','deps'):
        raise SystemExit('Usage: python scripts/run_dbt.py [debug|run|test|build|compile|docs|deps] [args...]')
    cmd=['dbt',sys.argv[1],'--project-dir','dbt','--profiles-dir','dbt']+sys.argv[2:]
    raise SystemExit(subprocess.call(cmd,env=env_for_dbt(database_url())))
