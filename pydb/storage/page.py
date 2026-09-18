PAGE_SIZE = 4096


class Page:
    def __init__(self, page_id: int):
        self.page_id = page_id
        self.data = bytearray(PAGE_SIZE)

    def write(self, offset: int, data: bytes) -> None:
        if offset < 0:
            raise ValueError("Offset cannot be negative")

        end = offset + len(data)

        if end > PAGE_SIZE:
            raise ValueError("Data exceeds page boundary")

        self.data[offset:end] = data

    def read(self, offset: int, size: int) -> bytes:
        if offset < 0:
            raise ValueError("Offset cannot be negative")

        if size < 0:
            raise ValueError("Size cannot be negative")

        end = offset + size

        if end > PAGE_SIZE:
            raise ValueError("Read exceeds page boundary")

        return bytes(self.data[offset:end])

    def clear(self) -> None:
        self.data = bytearray(PAGE_SIZE)