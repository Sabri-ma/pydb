from pydb.index.btree import BPlusTree
from pydb.storage.table import RowID


def test_insert_and_search():
    tree = BPlusTree()

    row_id = RowID(
        page_id=0,
        slot_id=0,
    )

    tree.insert(
        10,
        row_id,
    )

    assert tree.search(10) == row_id


def test_missing_key():
    tree = BPlusTree()

    assert tree.search(99) is None


def test_multiple_keys():
    tree = BPlusTree()

    tree.insert(10, "row10")
    tree.insert(5, "row5")
    tree.insert(20, "row20")

    assert tree.search(5) == "row5"
    assert tree.search(10) == "row10"
    assert tree.search(20) == "row20"


def test_tree_splits():
    tree = BPlusTree(order=4)

    for key in range(20):
        tree.insert(
            key,
            f"row-{key}",
        )

    for key in range(20):
        assert tree.search(key) == f"row-{key}"


def test_duplicate_key_updates_value():
    tree = BPlusTree()

    tree.insert(
        10,
        "old",
    )

    tree.insert(
        10,
        "new",
    )

    assert tree.search(10) == "new"