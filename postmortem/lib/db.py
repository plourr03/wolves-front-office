"""
Postgres connection helper for the nba_warehouse.

Reads connection details from POSTGRES_* environment variables. The pipeline in
../nba-warehouse uses the same convention, so a single set of env vars works
for both repos.

Required env vars:
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

The connection sets search_path to the `nba` schema so queries can omit the
schema prefix.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

import psycopg2
import pandas as pd

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


_REQUIRED = ("POSTGRES_HOST", "POSTGRES_PORT", "POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD")


def _hydrate_from_windows_user_env() -> None:
    """
    On Windows, env vars set via [Environment]::SetEnvironmentVariable(name, val, 'User')
    are persisted in HKCU\\Environment but only become visible to processes launched
    after the change. If Claude Code (or any parent process) was launched before the
    user set their POSTGRES_* vars, this function backfills them from the registry
    so the current Python process behaves as if it were freshly launched.

    Values move directly registry -> os.environ. They are not printed or written
    to disk.
    """
    if os.name != "nt":
        return
    try:
        import winreg
    except ImportError:
        return
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            for name in _REQUIRED:
                if os.environ.get(name):
                    continue
                try:
                    value, _ = winreg.QueryValueEx(key, name)
                except FileNotFoundError:
                    continue
                if value:
                    os.environ[name] = str(value)
    except OSError:
        return


_hydrate_from_windows_user_env()


def _conn_kwargs() -> dict:
    missing = [v for v in _REQUIRED if not os.environ.get(v)]
    if missing:
        raise RuntimeError(
            f"Missing required env vars: {', '.join(missing)}. "
            "Set them at User scope with [Environment]::SetEnvironmentVariable, "
            "or put them in a .env file at the repo root."
        )
    return dict(
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ["POSTGRES_PORT"]),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )


@contextmanager
def connect() -> Iterator[psycopg2.extensions.connection]:
    """Yield a psycopg2 connection with search_path set to the nba schema."""
    conn = psycopg2.connect(**_conn_kwargs())
    try:
        with conn.cursor() as cur:
            cur.execute("SET search_path TO nba, public")
        yield conn
    finally:
        conn.close()


def query(sql: str, params: tuple | dict | None = None) -> pd.DataFrame:
    """Run a SELECT and return a DataFrame. Uses cursor + manual frame build to
    avoid pandas' SQLAlchemy nag on raw psycopg2 connections."""
    with connect() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
    return pd.DataFrame(rows, columns=cols)


def scalar(sql: str, params: tuple | dict | None = None):
    """Run a SELECT that returns a single value."""
    with connect() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        row = cur.fetchone()
        return row[0] if row else None
