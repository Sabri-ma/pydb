from pathlib import Path

from pydb.parser.ast import (
    CreateIndexStatement,
    CreateTableStatement,
    InsertStatement,
    SelectStatement,
)
from pydb.storage.catalog import Catalog
from pydb.storage.schema import (
    Column,
    ColumnType,
    Schema,
)
from pydb.storage.table import Table


class Database:
    def __init__(
        self,
        data_dir: str | None = None,
    ):
        self.tables: dict[
            str,
            Table,
        ] = {}

        self.data_dir: Path | None = None
        self.catalog: Catalog | None = None

        if data_dir is not None:
            self.data_dir = Path(
                data_dir
            )

            self.data_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            catalog_path = (
                self.data_dir
                / "catalog.json"
            )

            self.catalog = Catalog(
                str(catalog_path)
            )

            self._load_tables()
            self._load_indexes()

    def _load_tables(
        self,
    ) -> None:
        if (
            self.catalog is None
            or self.data_dir is None
        ):
            return

        schemas = (
            self.catalog.load()
        )

        for (
            table_name,
            schema,
        ) in schemas.items():
            table_file = (
                self.data_dir
                / f"{table_name}.pydb"
            )

            self.tables[
                table_name
            ] = Table(
                schema,
                str(table_file),
            )

    def _load_indexes(
        self,
    ) -> None:
        if self.catalog is None:
            return

        indexes = (
            self.catalog.load_indexes()
        )

        for (
            index_name,
            index_data,
        ) in indexes.items():
            table_name = (
                index_data["table"]
            )

            column_name = (
                index_data["column"]
            )

            if table_name not in self.tables:
                raise ValueError(
                    f"Index {index_name} "
                    f"references missing table "
                    f"{table_name}"
                )

            table = self.tables[
                table_name
            ]

            if not table.has_index(
                column_name
            ):
                table.create_index(
                    column_name
                )

    def create_table(
        self,
        name: str,
        schema: Schema,
    ) -> None:
        if name in self.tables:
            raise ValueError(
                f"Table already exists: "
                f"{name}"
            )

        if self.data_dir is None:
            self.tables[
                name
            ] = Table(
                schema
            )

            return

        table_file = (
            self.data_dir
            / f"{name}.pydb"
        )

        self.tables[
            name
        ] = Table(
            schema,
            str(table_file),
        )

        if self.catalog is not None:
            self.catalog.save_table(
                name,
                schema,
            )

    def create_index(
        self,
        table_name: str,
        column_name: str,
        index_name: str | None = None,
    ) -> None:
        if table_name not in self.tables:
            raise ValueError(
                f"Table does not exist: "
                f"{table_name}"
            )

        if (
            index_name is not None
            and self.catalog is not None
            and self.catalog.index_exists(
                index_name
            )
        ):
            raise ValueError(
                f"Index already exists: "
                f"{index_name}"
            )

        table = self.tables[
            table_name
        ]

        table.create_index(
            column_name
        )

        if (
            index_name is not None
            and self.catalog is not None
        ):
            self.catalog.save_index(
                index_name,
                table_name,
                column_name,
            )

    def execute(
        self,
        statement,
    ):
        if isinstance(
            statement,
            CreateTableStatement,
        ):
            return (
                self._execute_create_table(
                    statement
                )
            )

        if isinstance(
            statement,
            CreateIndexStatement,
        ):
            return (
                self._execute_create_index(
                    statement
                )
            )

        if isinstance(
            statement,
            InsertStatement,
        ):
            return (
                self._execute_insert(
                    statement
                )
            )

        if isinstance(
            statement,
            SelectStatement,
        ):
            return (
                self._execute_select(
                    statement
                )
            )

        raise ValueError(
            f"Unsupported statement type: "
            f"{type(statement).__name__}"
        )

    def _execute_create_table(
        self,
        statement: CreateTableStatement,
    ):
        columns = []

        for column in statement.columns:
            if column.type == "INT":
                column_type = (
                    ColumnType.INT
                )

            elif column.type == "TEXT":
                column_type = (
                    ColumnType.TEXT
                )

            else:
                raise ValueError(
                    f"Unsupported column type: "
                    f"{column.type}"
                )

            columns.append(
                Column(
                    name=column.name,
                    type=column_type,
                )
            )

        schema = Schema(
            columns
        )

        self.create_table(
            statement.table,
            schema,
        )

    def _execute_create_index(
        self,
        statement: CreateIndexStatement,
    ):
        self.create_index(
            statement.table,
            statement.column,
            statement.name,
        )

    def _execute_insert(
        self,
        statement: InsertStatement,
    ):
        if statement.table not in self.tables:
            raise ValueError(
                f"Table does not exist: "
                f"{statement.table}"
            )

        table = self.tables[
            statement.table
        ]

        return table.insert(
            tuple(
                statement.values
            )
        )

    def _execute_select(
        self,
        statement: SelectStatement,
    ):
        if statement.table not in self.tables:
            raise ValueError(
                f"Table does not exist: "
                f"{statement.table}"
            )

        table = self.tables[
            statement.table
        ]

        if (
            statement.where is not None
            and
            statement.where.operator == "="
            and
            table.has_index(
                statement.where.column
            )
        ):
            row = (
                table.lookup_by_index(
                    statement.where.column,
                    statement.where.value,
                )
            )

            rows = (
                []
                if row is None
                else [row]
            )

        else:
            rows = list(
                table.scan()
            )

            if statement.where is not None:
                rows = (
                    self._filter_rows(
                        table,
                        rows,
                        statement.where,
                    )
                )

        if statement.columns == ["*"]:
            return rows

        column_indexes = [
            table.schema.column_index(
                column
            )
            for column
            in statement.columns
        ]

        return [
            tuple(
                row[index]
                for index
                in column_indexes
            )
            for row in rows
        ]

    def _filter_rows(
        self,
        table: Table,
        rows: list[tuple],
        condition,
    ) -> list[tuple]:
        index = (
            table.schema.column_index(
                condition.column
            )
        )

        operator = condition.operator

        if operator == "=":
            return [
                row
                for row in rows
                if row[index]
                == condition.value
            ]

        if operator == "!=":
            return [
                row
                for row in rows
                if row[index]
                != condition.value
            ]

        if operator == ">":
            return [
                row
                for row in rows
                if row[index]
                > condition.value
            ]

        if operator == "<":
            return [
                row
                for row in rows
                if row[index]
                < condition.value
            ]

        if operator == ">=":
            return [
                row
                for row in rows
                if row[index]
                >= condition.value
            ]

        if operator == "<=":
            return [
                row
                for row in rows
                if row[index]
                <= condition.value
            ]

        raise ValueError(
            f"Unsupported operator: "
            f"{operator}"
        )