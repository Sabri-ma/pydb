import pytest

from pydb.storage.schema import Column, ColumnType, Schema
from pydb.storage.table import RowID, Table


def users_schema():
    return Schema(
        [
            Column("id", ColumnType.INT),
            Column("name", ColumnType.TEXT),
        ]
    )


def users_schema_with_age():
    return Schema(
        [
            Column("id", ColumnType.INT),
            Column("name", ColumnType.TEXT),
            Column("age", ColumnType.INT),
        ]
    )


def test_insert_and_get_row():
    table = Table(users_schema_with_age())

    row_id = table.insert((1, "Massine", 24))

    assert row_id == RowID(page_id=0, slot_id=0)
    assert table.get(row_id) == (1, "Massine", 24)


def test_multiple_rows():
    table = Table(users_schema())

    row1 = table.insert((1, "Massine"))
    row2 = table.insert((2, "Alice"))

    assert table.get(row1) == (1, "Massine")
    assert table.get(row2) == (2, "Alice")


def test_scan_rows():
    table = Table(users_schema())

    table.insert((1, "Massine"))
    table.insert((2, "Alice"))
    table.insert((3, "Bob"))

    rows = list(table.scan())

    assert rows == [
        (1, "Massine"),
        (2, "Alice"),
        (3, "Bob"),
    ]


def test_invalid_page_id():
    table = Table(users_schema())

    with pytest.raises(IndexError):
        table.get(RowID(page_id=99, slot_id=0))


def test_creates_multiple_pages_when_full():
    table = Table(users_schema())

    large_text = "x" * 2000

    row1 = table.insert((1, large_text))
    row2 = table.insert((2, large_text))
    row3 = table.insert((3, large_text))

    assert row1.page_id == 0
    assert row2.page_id == 0
    assert row3.page_id == 1


def test_rejects_wrong_value_count():
    table = Table(users_schema())

    with pytest.raises(ValueError):
        table.insert((1,))


def test_rejects_wrong_value_type():
    table = Table(users_schema())

    with pytest.raises(TypeError):
        table.insert(("not-an-int", "Massine"))