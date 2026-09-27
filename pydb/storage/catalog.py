import json
from pathlib import Path

from .schema import Column, ColumnType, Schema


class Catalog:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

        if not self.file_path.exists():
            self.file_path.write_text(
                json.dumps({"tables": {}}),
                encoding="utf-8",
            )

    def load(self) -> dict[str, Schema]:
        data = json.loads(
            self.file_path.read_text(
                encoding="utf-8"
            )
        )

        result = {}

        for table_name, columns in data["tables"].items():
            schema_columns = []

            for column in columns:
                column_type = ColumnType[
                    column["type"]
                ]

                schema_columns.append(
                    Column(
                        column["name"],
                        column_type,
                    )
                )

            result[table_name] = Schema(
                schema_columns
            )

        return result

    def save_table(
        self,
        table_name: str,
        schema: Schema,
    ) -> None:
        data = json.loads(
            self.file_path.read_text(
                encoding="utf-8"
            )
        )

        data["tables"][table_name] = [
            {
                "name": column.name,
                "type": column.type.name,
            }
            for column in schema.columns
        ]

        self.file_path.write_text(
            json.dumps(
                data,
                indent=2,
            ),
            encoding="utf-8",
        )