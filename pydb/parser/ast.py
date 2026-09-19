from dataclasses import dataclass


@dataclass(frozen=True)
class Condition:
    column: str
    operator: str
    value: int | str


@dataclass(frozen=True)
class SelectStatement:
    columns: list[str]
    table: str
    where: Condition | None = None


@dataclass(frozen=True)
class InsertStatement:
    table: str
    values: list[int | str]

@dataclass(frozen=True)
class ColumnDefinition:
    name: str
    type: str


@dataclass(frozen=True)
class CreateTableStatement:
    table: str
    columns: list[ColumnDefinition]