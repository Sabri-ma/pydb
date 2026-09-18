from pydb.storage.disk import DiskManager
from pydb.storage.page import Page


def test_write_and_read_page(tmp_path):
    db_file = tmp_path / "test.pydb"

    disk = DiskManager(str(db_file))

    page = Page(page_id=0)
    page.write(0, b"hello pydb")

    disk.write_page(page)

    loaded_page = disk.read_page(0)

    assert loaded_page.read(0, 10) == b"hello pydb"


def test_multiple_pages(tmp_path):
    db_file = tmp_path / "test.pydb"

    disk = DiskManager(str(db_file))

    page0 = Page(page_id=0)
    page0.write(0, b"page zero")

    page1 = Page(page_id=1)
    page1.write(0, b"page one")

    disk.write_page(page0)
    disk.write_page(page1)

    assert disk.read_page(0).read(0, 9) == b"page zero"
    assert disk.read_page(1).read(0, 8) == b"page one"


def test_page_count(tmp_path):
    db_file = tmp_path / "test.pydb"

    disk = DiskManager(str(db_file))

    disk.write_page(Page(page_id=0))
    disk.write_page(Page(page_id=1))

    assert disk.page_count() == 2