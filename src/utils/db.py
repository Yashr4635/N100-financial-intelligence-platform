"""
Database loader skeleton.

This module will eventually provide a reusable way for dashboard pages
to obtain a database connection / engine so they can query the
analytics produced in Sprints 1-3.

IMPORTANT (Milestone 1 scope):
    No SQL or analytics logic is implemented here yet. This is purely
    a structural skeleton to be filled in during a later milestone.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class DBConfig:
    """
    Placeholder configuration container for database connection details.

    Fields are intentionally left generic. They will be populated /
    refined once the actual data source (e.g. SQLite, Postgres, DuckDB)
    is decided for the dashboard's read layer.
    """
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None
    path: Optional[str] = None  # for file-based DBs (e.g. sqlite/duckdb)


class DBLoader:
    """
    Reusable database loader skeleton.

    Later milestones will implement:
      - establishing a real connection/engine
      - connection pooling / caching (e.g. via st.cache_resource)
      - query helper methods used by the individual dashboard pages

    For now, this class only defines the interface so pages and other
    utilities can be written against a stable contract.
    """

    def __init__(self, config: Optional[DBConfig] = None) -> None:
        self.config = config or DBConfig()
        self._connection: Optional[Any] = None

    def connect(self) -> Any:
        """
        Establish (or return a cached) database connection.

        NOTE: Not implemented in this milestone.
        """
        raise NotImplementedError(
            "DBLoader.connect() will be implemented in a later milestone."
        )

    def get_engine(self) -> Any:
        """
        Return a database engine/connection object for use by pages.

        NOTE: Not implemented in this milestone.
        """
        raise NotImplementedError(
            "DBLoader.get_engine() will be implemented in a later milestone."
        )

    def close(self) -> None:
        """
        Close the underlying database connection, if open.

        NOTE: Not implemented in this milestone.
        """
        self._connection = None


def get_db_loader() -> DBLoader:
    """
    Convenience factory used by pages/app.py to obtain a DBLoader
    instance.

    This will later be wrapped with Streamlit caching
    (e.g. @st.cache_resource) once the real connection logic exists.
    """
    return DBLoader()