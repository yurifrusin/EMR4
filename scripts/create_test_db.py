import os
from urllib.parse import urlsplit, urlunsplit

import psycopg2
from psycopg2 import sql


test_url = os.getenv("TEST_DATABASE_URL", "postgresql://postgres:postgres@127.0.0.1:5434/gp_pms_test")
parts = urlsplit(test_url)
database_name = parts.path.lstrip("/") or "gp_pms_test"
admin_url = urlunsplit((parts.scheme, parts.netloc, "/postgres", parts.query, parts.fragment))

conn = psycopg2.connect(admin_url)
conn.autocommit = True
cur = conn.cursor()
cur.execute("SELECT 1 FROM pg_database WHERE datname=%s", (database_name,))
if not cur.fetchone():
    cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database_name)))
    print(f"[ok] created {database_name}")
else:
    print(f"[ok] {database_name} already exists")
conn.close()
