from dataclasses import dataclass

from .disk import DiskManager
from .record import RecordSerializer
from .schema import Schema
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

        if file_path is not None:
            self.disk = DiskManager(
                file_path
            )

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

        for page in self.pages:
            try:
                slot_id = page.insert(
                    record
                )

                self._persist_page(
                    page
                )

                return RowID(
                    page_id=page.page.page_id,
                    slot_id=slot_id,
                )

            except ValueError:
                continue

        page = self._create_page()

        slot_id = page.insert(
            record
        )

        self._persist_page(
            page
        )

        return RowID(
            page_id=page.page.page_id,
            slot_id=slot_id,
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
        for page in self.pages:
            for slot_id in range(
                page.slot_count
            ):
                record = page.read(
                    slot_id
                )

                yield (
                    RecordSerializer.deserialize(
                        record
                    )
                )