from dataclasses import dataclass

from pydb.index.btree import BPlusTree

from .disk import DiskManager
from .record import RecordSerializer
from .schema import ColumnType, Schema
from .slotted_page import SlottedPage


@dataclass(frozen=True)
class RowID:
    page_id: int
    slot_id: int


class Table:
    def __init__(
        self,
        schema: Schema,
        file_path: str | None = None,
    ):
        self.schema = schema
        self.pages: list[SlottedPage] = []

        self.disk: DiskManager | None = None

        self.indexes: dict[str, BPlusTree] = {}

        if file_path is not None:
            self.disk = DiskManager(file_path)
            self._load_pages()

    def _load_pages(self) -> None:
        if self.disk is None:
            return

        for page_id in range(
            self.disk.page_count()
        ):
            page = self.disk.read_page(
                page_id
            )

            slotted_page = (
                SlottedPage.from_page(
                    page
                )
            )

            self.pages.append(
                slotted_page
            )

    def _create_page(self) -> SlottedPage:
        page = SlottedPage(
            page_id=len(self.pages)
        )

        self.pages.append(page)

        return page

    def _persist_page(
        self,
        page: SlottedPage,
    ) -> None:
        if self.disk is None:
            return

        self.disk.write_page(
            page.page
        )

    def create_index(
        self,
        column_name: str,
    ) -> None:
        column_index = (
            self.schema.column_index(
                column_name
            )
        )

        column = self.schema.columns[
            column_index
        ]

        if column.type != ColumnType.INT:
            raise TypeError(
                "B+ Tree indexes currently "
                "support INT columns only"
            )

        if column_name in self.indexes:
            raise ValueError(
                f"Index already exists "
                f"for column: {column_name}"
            )

        tree = BPlusTree()

        for row_id, row in (
            self.scan_with_row_ids()
        ):
            key = row[column_index]

            tree.insert(
                key,
                row_id,
            )

        self.indexes[column_name] = tree

    def has_index(
        self,
        column_name: str,
    ) -> bool:
        return column_name in self.indexes

    def lookup_by_index(
        self,
        column_name: str,
        value: int,
    ) -> tuple | None:
        if column_name not in self.indexes:
            raise ValueError(
                f"No index exists for column: "
                f"{column_name}"
            )

        tree = self.indexes[
            column_name
        ]

        row_id = tree.search(
            value
        )

        if row_id is None:
            return None

        return self.get(
            row_id
        )

    def insert(
        self,
        values: tuple,
    ) -> RowID:
        self.schema.validate(
            values
        )

        record = (
            RecordSerializer.serialize(
                values
            )
        )

        row_id = None

        for page in self.pages:
            try:
                slot_id = page.insert(
                    record
                )

                self._persist_page(
                    page
                )

                row_id = RowID(
                    page_id=page.page.page_id,
                    slot_id=slot_id,
                )

                break

            except ValueError:
                continue

        if row_id is None:
            page = self._create_page()

            slot_id = page.insert(
                record
            )

            self._persist_page(
                page
            )

            row_id = RowID(
                page_id=page.page.page_id,
                slot_id=slot_id,
            )

        self._update_indexes(
            values,
            row_id,
        )

        return row_id

    def _update_indexes(
        self,
        values: tuple,
        row_id: RowID,
    ) -> None:
        for (
            column_name,
            tree,
        ) in self.indexes.items():
            column_index = (
                self.schema.column_index(
                    column_name
                )
            )

            key = values[
                column_index
            ]

            tree.insert(
                key,
                row_id,
            )

    def get(
        self,
        row_id: RowID,
    ) -> tuple:
        if (
            row_id.page_id < 0
            or row_id.page_id
            >= len(self.pages)
        ):
            raise IndexError(
                "Invalid page id"
            )

        page = self.pages[
            row_id.page_id
        ]

        record = page.read(
            row_id.slot_id
        )

        return (
            RecordSerializer.deserialize(
                record
            )
        )

    def scan(self):
        for _, row in (
            self.scan_with_row_ids()
        ):
            yield row

    def scan_with_row_ids(self):
        for page in self.pages:
            for slot_id in range(
                page.slot_count
            ):
                record = page.read(
                    slot_id
                )

                row = (
                    RecordSerializer.deserialize(
                        record
                    )
                )

                row_id = RowID(
                    page_id=page.page.page_id,
                    slot_id=slot_id,
                )

                yield row_id, row