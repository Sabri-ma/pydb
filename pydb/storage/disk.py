from pathlib import Path

from .page import PAGE_SIZE, Page


class DiskManager:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

        if not self.file_path.exists():
            self.file_path.touch()

    def write_page(self, page: Page) -> None:
        offset = page.page_id * PAGE_SIZE

        with self.file_path.open("r+b") as file:
            file.seek(offset)
            file.write(page.data)

    def read_page(self, page_id: int) -> Page:
        offset = page_id * PAGE_SIZE

        with self.file_path.open("rb") as file:
            file.seek(offset)
            data = file.read(PAGE_SIZE)

        if len(data) != PAGE_SIZE:
            raise ValueError(f"Page {page_id} does not exist")

        page = Page(page_id)
        page.data[:] = data

        return page

    def page_count(self) -> int:
        size = self.file_path.stat().st_size
        return size // PAGE_SIZE