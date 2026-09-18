import struct


class RecordSerializer:
    TYPE_INT = 1
    TYPE_TEXT = 2

    @classmethod
    def serialize(cls, values: tuple) -> bytes:
        result = bytearray()

        result.extend(struct.pack(">H", len(values)))

        for value in values:
            if isinstance(value, int):
                result.append(cls.TYPE_INT)
                result.extend(struct.pack(">q", value))

            elif isinstance(value, str):
                encoded = value.encode("utf-8")

                result.append(cls.TYPE_TEXT)
                result.extend(struct.pack(">I", len(encoded)))
                result.extend(encoded)

            else:
                raise TypeError(
                    f"Unsupported type: {type(value).__name__}"
                )

        return bytes(result)

    @classmethod
    def deserialize(cls, data: bytes) -> tuple:
        offset = 0

        column_count = struct.unpack_from(">H", data, offset)[0]
        offset += 2

        values = []

        for _ in range(column_count):
            value_type = data[offset]
            offset += 1

            if value_type == cls.TYPE_INT:
                value = struct.unpack_from(">q", data, offset)[0]
                offset += 8
                values.append(value)

            elif value_type == cls.TYPE_TEXT:
                length = struct.unpack_from(">I", data, offset)[0]
                offset += 4

                value = data[offset:offset + length].decode("utf-8")
                offset += length

                values.append(value)

            else:
                raise ValueError(
                    f"Unknown value type: {value_type}"
                )

        return tuple(values)