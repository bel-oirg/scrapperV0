from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterator

from .config import DEFAULT_CACHE_TTL_SECONDS, DEFAULT_DB_PATH
from .models import JobPosting


class SQLiteCache:
    def __init__(self, db_path: Path = DEFAULT_DB_PATH, ttl_seconds: int = DEFAULT_CACHE_TTL_SECONDS) -> None:
        self.db_path = Path(db_path)
        self.ttl_seconds = ttl_seconds
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def _init_db(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS responses (
                    cache_key TEXT PRIMARY KEY,
                    url TEXT NOT NULL,
                    body TEXT NOT NULL,
                    status_code INTEGER NOT NULL,
                    fetched_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS seen_jobs (
                    job_key TEXT PRIMARY KEY,
                    source TEXT NOT NULL,
                    title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    url TEXT NOT NULL,
                    first_seen TEXT NOT NULL,
                    last_seen TEXT NOT NULL
                )
                """
            )

    def prune(self) -> None:
        threshold = (datetime.utcnow() - timedelta(seconds=self.ttl_seconds)).isoformat()
        with self._connect() as connection:
            connection.execute("DELETE FROM responses WHERE fetched_at < ?", (threshold,))

    def get_response(self, cache_key: str) -> str | None:
        threshold = (datetime.utcnow() - timedelta(seconds=self.ttl_seconds)).isoformat()
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT body FROM responses
                WHERE cache_key = ? AND fetched_at >= ?
                """,
                (cache_key, threshold),
            ).fetchone()
        return None if row is None else str(row["body"])

    def set_response(self, cache_key: str, url: str, body: str, status_code: int) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO responses (cache_key, url, body, status_code, fetched_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(cache_key) DO UPDATE SET
                    body = excluded.body,
                    status_code = excluded.status_code,
                    fetched_at = excluded.fetched_at
                """,
                (cache_key, url, body, status_code, datetime.utcnow().isoformat()),
            )

    def mark_job_seen(self, job: JobPosting) -> bool:
        now = datetime.utcnow().isoformat()
        with self._connect() as connection:
            existing = connection.execute(
                "SELECT job_key FROM seen_jobs WHERE job_key = ?",
                (job.dedup_key,),
            ).fetchone()
            if existing:
                connection.execute(
                    """
                    UPDATE seen_jobs
                    SET last_seen = ?, url = ?, title = ?, company = ?, source = ?
                    WHERE job_key = ?
                    """,
                    (now, job.application_url, job.title, job.company, job.source, job.dedup_key),
                )
                return False
            connection.execute(
                """
                INSERT INTO seen_jobs (job_key, source, title, company, url, first_seen, last_seen)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job.dedup_key,
                    job.source,
                    job.title,
                    job.company,
                    job.application_url,
                    now,
                    now,
                ),
            )
            return True
