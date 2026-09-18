from pydb.parser.ast import InsertStatement, SelectStatement
from pydb.storage.table import Table


class Database:
    def __init__(self):
        self.tables: dict[str, Table] = {}

    def create_table(self, name: str) -> None:
        if name in self.tables:
            raise ValueError(f"Table already exists: {name}")

        self.tables[name] = Table()

    def execute(self, statement):
        if isinstance(statement, InsertStatement):
            return self._execute_insert(statement)

        if isinstance(statement, SelectStatement):
            return self._execute_select(statement)

        raise ValueError(
            f"Unsupported statement type: {type(statement).__name__}"
        )

    def _execute_insert(self, statement: InsertStatement):
        if statement.table not in self.tables:
            raise ValueError(
                f"Table does not exist: {statement.table}"
            )

        table = self.tables[statement.table]

        return table.insert(tuple(statement.values))

    def _execute_select(self, statement: SelectStatement):
        if statement.table not in self.tables:
            raise ValueError(
                f"Table does not exist: {statement.table}"
            )

        table = self.tables[statement.table]

        rows = list(table.scan())

        if statement.where is None:
            return rows

        condition = statement.where

        # Temporary assumption:
        # column names map to fixed positions.
        column_positions = {
            "id": 0,
            "name": 1,
            "age": 2,
        }

        if condition.column not in column_positions:
            raise ValueError(
                f"Unknown column: {condition.column}"
            )

        index = column_positions[condition.column]

        if condition.operator != "=":
            raise ValueError(
                f"Unsupported operator: {condition.operator}"
            )

        return [
            row
            for row in rows
            if row[index] == condition.value
        ]