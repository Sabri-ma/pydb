from pydb.parser.ast import (
    CreateTableStatement,
    InsertStatement,
    SelectStatement,
)
from pydb.storage.schema import Column, ColumnType, Schema
from pydb.storage.table import Table


class Database:
    def __init__(self):
        self.tables: dict[str, Table] = {}

    def create_table(self, name: str, schema: Schema) -> None:
        if name in self.tables:
            raise ValueError(f"Table already exists: {name}")

        self.tables[name] = Table(schema)

    def execute(self, statement):
        if isinstance(statement, CreateTableStatement):
            return self._execute_create_table(statement)

        if isinstance(statement, InsertStatement):
            return self._execute_insert(statement)

        if isinstance(statement, SelectStatement):
            return self._execute_select(statement)

        raise ValueError(
            f"Unsupported statement type: {type(statement).__name__}"
        )

    def _execute_create_table(
        self,
        statement: CreateTableStatement,
    ):
        columns = []

        for column in statement.columns:
            if column.type == "INT":
                column_type = ColumnType.INT

            elif column.type == "TEXT":
                column_type = ColumnType.TEXT

            else:
                raise ValueError(
                    f"Unsupported column type: {column.type}"
                )

            columns.append(
                Column(
                    name=column.name,
                    type=column_type,
                )
            )

        schema = Schema(columns)

        self.create_table(
            statement.table,
            schema,
        )

    def _execute_insert(self, statement: InsertStatement):
        if statement.table not in self.tables:
            raise ValueError(
                f"Table does not exist: {statement.table}"
            )

        table = self.tables[statement.table]

        return table.insert(
            tuple(statement.values)
        )

    def _execute_select(self, statement: SelectStatement):
        if statement.table not in self.tables:
            raise ValueError(
                f"Table does not exist: {statement.table}"
            )

        table = self.tables[statement.table]

        rows = list(table.scan())

        if statement.where is not None:
            condition = statement.where

            if condition.operator != "=":
                raise ValueError(
                    f"Unsupported operator: {condition.operator}"
                )

            index = table.schema.column_index(
                condition.column
            )

            rows = [
                row
                for row in rows
                if row[index] == condition.value
            ]

        return rows