import struct

from .page import PAGE_SIZE, Page


HEADER_SIZE = 4
SLOT_SIZE = 4


class SlottedPage:
    def __init__(self, page_id: int):
        self.page = Page(page_id)

        self.slot_count = 0
        self.free_space_pointer = PAGE_SIZE

        self._write_header()

    def _write_header(self) -> None:
        struct.pack_into(
            ">HH",
            self.page.data,
            0,
            self.slot_count,
            self.free_space_pointer,
        )

    def _write_slot(self, slot_id: int, offset: int, size: int) -> None:
        slot_offset = HEADER_SIZE + slot_id * SLOT_SIZE

        struct.pack_into(
            ">HH",
            self.page.data,
            slot_offset,
            offset,
            size,
        )

    def _read_slot(self, slot_id: int) -> tuple[int, int]:
        if slot_id < 0 or slot_id >= self.slot_count:
            raise IndexError("Invalid slot id")

        slot_offset = HEADER_SIZE + slot_id * SLOT_SIZE

        return struct.unpack_from(
            ">HH",
            self.page.data,
            slot_offset,
        )

    def insert(self, record: bytes) -> int:
        required_space = len(record) + SLOT_SIZE

        free_space_start = HEADER_SIZE + self.slot_count * SLOT_SIZE
        available_space = self.free_space_pointer - free_space_start

        if required_space > available_space:
            raise ValueError("Not enough space in page")

        self.free_space_pointer -= len(record)

        self.page.write(
            self.free_space_pointer,
            record,
        )

        slot_id = self.slot_count

        self._write_slot(
            slot_id,
            self.free_space_pointer,
            len(record),
        )

        self.slot_count += 1
        self._write_header()

        return slot_id

    def read(self, slot_id: int) -> bytes:
        offset, size = self._read_slot(slot_id)

        return self.page.read(offset, size)

    def available_space(self) -> int:
        free_space_start = HEADER_SIZE + self.slot_count * SLOT_SIZE

        return self.free_space_pointer - free_space_start