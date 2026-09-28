import json
from pathlib import Path

from .schema import (
    Column,
    ColumnType,
    Schema,
)


class Catalog:
    def __init__(
        self,
        file_path: str,
    ):
        self.file_path = Path(
            file_path
        )

        if not self.file_path.exists():
            self._write_data(
                {
                    "tables": {},
                    "indexes": {},
                }
            )
        else:
            data = self._read_data()

            if "tables" not in data:
                data["tables"] = {}

            if "indexes" not in data:
                data["indexes"] = {}

            self._write_data(
                data
            )

    def _read_data(self) -> dict:
        return json.loads(
            self.file_path.read_text(
                encoding="utf-8"
            )
        )

    def _write_data(
        self,
        data: dict,
    ) -> None:
        self.file_path.write_text(
            json.dumps(
                data,
                indent=2,
            ),
            encoding="utf-8",
        )

    def load(
        self,
    ) -> dict[str, Schema]:
        data = self._read_data()

        result = {}

        for (
            table_name,
            columns,
        ) in data["tables"].items():
            schema_columns = []

            for column in columns:
                column_type = (
                    ColumnType[
                        column["type"]
                    ]
                )

                schema_columns.append(
                    Column(
                        column["name"],
                        column_type,
                    )
                )

            result[
                table_name
            ] = Schema(
                schema_columns
            )

        return result

    def save_table(
        self,
        table_name: str,
        schema: Schema,
    ) -> None:
        data = self._read_data()

        data["tables"][
            table_name
        ] = [
            {
                "name": column.name,
                "type": column.type.name,
            }
            for column
            in schema.columns
        ]

        self._write_data(
            data
        )

    def save_index(
        self,
        index_name: str,
        table_name: str,
        column_name: str,
    ) -> None:
        data = self._read_data()

        data["indexes"][
            index_name
        ] = {
            "table": table_name,
            "column": column_name,
        }

        self._write_data(
            data
        )

    def load_indexes(
        self,
    ) -> dict[str, dict]:
        data = self._read_data()

        return data.get(
            "indexes",
            {},
        )

    def index_exists(
        self,
        index_name: str,
    ) -> bool:
        indexes = (
            self.load_indexes()
        )

        return (
            index_name
            in indexes
        )