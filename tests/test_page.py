import pytest

from pydb.storage.page import PAGE_SIZE, Page


def test_page_has_correct_size():
    page = Page(page_id=0)

    assert len(page.data) == PAGE_SIZE


def test_write_and_read_data():
    page = Page(page_id=0)

    page.write(0, b"hello")

    assert page.read(0, 5) == b"hello"


def test_write_at_offset():
    page = Page(page_id=1)

    page.write(100, b"pydb")

    assert page.read(100, 4) == b"pydb"


def test_write_outside_page_raises_error():
    page = Page(page_id=0)

    with pytest.raises(ValueError):
        page.write(PAGE_SIZE - 2, b"hello")


def test_read_outside_page_raises_error():
    page = Page(page_id=0)

    with pytest.raises(ValueError):
        page.read(PAGE_SIZE - 2, 10)


def test_clear_page():
    page = Page(page_id=0)

    page.write(0, b"hello")
    page.clear()

    assert page.read(0, 5) == b"\x00\x00\x00\x00\x00"