from dataclasses import dataclass
from enum import Enum, auto


class ColumnType(Enum):
    INT = auto()
    TEXT = auto()


@dataclass(frozen=True)
class Column:
    name: str
    type: ColumnType


class Schema:
    def __init__(self, columns: list[Column]):
        if not columns:
            raise ValueError("Schema must contain at least one column")

        self.columns = columns

    def column_index(self, name: str) -> int:
        for index, column in enumerate(self.columns):
            if column.name == name:
                return index

        raise ValueError(f"Unknown column: {name}")

    def validate(self, values: tuple) -> None:
        if len(values) != len(self.columns):
            raise ValueError(
                f"Expected {len(self.columns)} values, got {len(values)}"
            )

        for column, value in zip(self.columns, values):
            if column.type == ColumnType.INT and not isinstance(value, int):
                raise TypeError(
                    f"Column '{column.name}' expects INT"
                )

            if column.type == ColumnType.TEXT and not isinstance(value, str):
                raise TypeError(
                    f"Column '{column.name}' expects TEXT"
                )