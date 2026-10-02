import sqlite3

import pytest

from quality_automation.data import assert_no_rows, assert_scalar


@pytest.mark.data
def test_sql_assertions_validate_reconciliation_rules() -> None:
    connection = sqlite3.connect(":memory:")
    connection.execute("create table payments (amount integer, status text)")
    connection.executemany("insert into payments values (?, ?)", [(100, "settled"), (50, "settled")])
    assert_scalar(connection, "select sum(amount) from payments", 150)
    assert_no_rows(connection, "select * from payments where status != 'settled'")
