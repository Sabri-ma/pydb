import pytest

from pydb.storage.record import RecordSerializer
from pydb.storage.slotted_page import SlottedPage


def test_insert_and_read_record():
    page = SlottedPage(page_id=0)

    record = RecordSerializer.serialize(
        (1, "Massine", 24)
    )

    slot_id = page.insert(record)

    stored = page.read(slot_id)

    assert RecordSerializer.deserialize(stored) == (
        1,
        "Massine",
        24,
    )


def test_multiple_records():
    page = SlottedPage(page_id=0)

    first = RecordSerializer.serialize(
        (1, "Massine")
    )

    second = RecordSerializer.serialize(
        (2, "Alice")
    )

    first_slot = page.insert(first)
    second_slot = page.insert(second)

    assert RecordSerializer.deserialize(
        page.read(first_slot)
    ) == (1, "Massine")

    assert RecordSerializer.deserialize(
        page.read(second_slot)
    ) == (2, "Alice")


def test_slot_ids_increment():
    page = SlottedPage(page_id=0)

    first = page.insert(b"hello")
    second = page.insert(b"world")

    assert first == 0
    assert second == 1


def test_invalid_slot():
    page = SlottedPage(page_id=0)

    with pytest.raises(IndexError):
        page.read(0)


def test_page_runs_out_of_space():
    page = SlottedPage(page_id=0)

    huge_record = b"x" * 4090

    with pytest.raises(ValueError):
        page.insert(huge_record)