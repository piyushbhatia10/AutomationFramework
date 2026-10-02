"""Portable SQL assertions and optional warehouse connection factory."""

from __future__ import annotations

import os
import subprocess
from contextlib import closing
from typing import Any, Protocol


class DbApiConnection(Protocol):
    def cursor(self) -> Any: ...


def query_rows(connection: DbApiConnection, query: str, parameters: Any = None) -> list[tuple[Any, ...]]:
    """Execute a read-only validation query using bind parameters where supported."""
    with closing(connection.cursor()) as cursor:
        cursor.execute(query, parameters) if parameters is not None else cursor.execute(query)
        return list(cursor.fetchall())


def assert_scalar(connection: DbApiConnection, query: str, expected: Any, parameters: Any = None) -> None:
    rows = query_rows(connection, query, parameters)
    assert len(rows) == 1 and len(rows[0]) == 1, "Validation query must return exactly one value"
    actual = rows[0][0]
    assert actual == expected, f"Expected {expected!r}, received {actual!r}. Query: {query}"


def assert_no_rows(connection: DbApiConnection, query: str, parameters: Any = None) -> None:
    rows = query_rows(connection, query, parameters)
    assert not rows, f"Expected no invalid rows; found {len(rows)}. Query: {query}"


def warehouse_connection(warehouse: str):
    """Create an optional warehouse connection from environment-held credentials."""
    provider = warehouse.lower()
    if provider == "snowflake":
        import snowflake.connector  # type: ignore[import-not-found]

        return snowflake.connector.connect(
            account=os.environ["SNOWFLAKE_ACCOUNT"],
            user=os.environ["SNOWFLAKE_USER"],
            password=os.environ["SNOWFLAKE_PASSWORD"],
            warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
            database=os.getenv("SNOWFLAKE_DATABASE"),
            schema=os.getenv("SNOWFLAKE_SCHEMA"),
        )
    if provider == "redshift":
        import redshift_connector  # type: ignore[import-not-found]

        return redshift_connector.connect(
            host=os.environ["REDSHIFT_HOST"],
            database=os.environ["REDSHIFT_DATABASE"],
            user=os.environ["REDSHIFT_USER"],
            password=os.environ["REDSHIFT_PASSWORD"],
        )
    if provider == "databricks":
        from databricks import sql  # type: ignore[import-not-found]

        return sql.connect(
            server_hostname=os.environ["DATABRICKS_SERVER_HOSTNAME"],
            http_path=os.environ["DATABRICKS_HTTP_PATH"],
            access_token=os.environ["DATABRICKS_TOKEN"],
        )
    raise ValueError("Unsupported warehouse. Choose snowflake, redshift, or databricks.")


def run_dbt_test(select: str | None = None) -> subprocess.CompletedProcess[str]:
    command = ["dbt", "test"]
    if select:
        command.extend(["--select", select])
    return subprocess.run(command, capture_output=True, text=True, check=False)
