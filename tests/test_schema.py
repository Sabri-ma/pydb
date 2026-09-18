import pytest

from pydb.storage.schema import Column, ColumnType, Schema


def test_column_index():
    schema = Schema(
        [
            Column("id", ColumnType.INT),
            Column("name", ColumnType.TEXT),
        ]
    )

    assert schema.column_index("id") == 0
    assert schema.column_index("name") == 1


def test_unknown_column():
    schema = Schema(
        [
            Column("id", ColumnType.INT),
        ]
    )

    with pytest.raises(ValueError):
        schema.column_index("email")


def test_validate_correct_values():
    schema = Schema(
        [
            Column("id", ColumnType.INT),
            Column("name", ColumnType.TEXT),
        ]
    )

    schema.validate((1, "Massine"))


def test_validate_wrong_value_count():
    schema = Schema(
        [
            Column("id", ColumnType.INT),
            Column("name", ColumnType.TEXT),
        ]
    )

    with pytest.raises(ValueError):
        schema.validate((1,))


def test_validate_wrong_type():
    schema = Schema(
        [
            Column("id", ColumnType.INT),
        ]
    )

    with pytest.raises(TypeError):
        schema.validate(("one",))