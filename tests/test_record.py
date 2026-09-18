import pytest

from pydb.storage.record import RecordSerializer


def test_serialize_and_deserialize_integer():
    data = RecordSerializer.serialize((42,))

    result = RecordSerializer.deserialize(data)

    assert result == (42,)


def test_serialize_and_deserialize_text():
    data = RecordSerializer.serialize(("Massine",))

    result = RecordSerializer.deserialize(data)

    assert result == ("Massine",)


def test_serialize_multiple_values():
    record = (1, "Massine", 24)

    data = RecordSerializer.serialize(record)

    result = RecordSerializer.deserialize(data)

    assert result == record


def test_unicode_text():
    record = (1, "Agadir", "مرحبا")

    data = RecordSerializer.serialize(record)

    result = RecordSerializer.deserialize(data)

    assert result == record


def test_unsupported_type():
    with pytest.raises(TypeError):
        RecordSerializer.serialize((3.14,))