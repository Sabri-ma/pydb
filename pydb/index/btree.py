from dataclasses import dataclass, field


@dataclass
class BTreeNode:
    leaf: bool = True
    keys: list[int] = field(default_factory=list)
    values: list = field(default_factory=list)
    children: list["BTreeNode"] = field(default_factory=list)
    next_leaf: "BTreeNode | None" = None


class BPlusTree:
    def __init__(self, order: int = 4):
        if order < 3:
            raise ValueError("Order must be at least 3")

        self.order = order
        self.root = BTreeNode()

    def search(self, key: int):
        node = self.root

        while not node.leaf:
            index = 0

            while (
                index < len(node.keys)
                and key >= node.keys[index]
            ):
                index += 1

            node = node.children[index]

        for index, existing_key in enumerate(node.keys):
            if existing_key == key:
                return node.values[index]

        return None

    def insert(self, key: int, value):
        root = self.root

        if len(root.keys) >= self.order - 1:
            new_root = BTreeNode(
                leaf=False,
                children=[root],
            )

            self._split_child(
                new_root,
                0,
            )

            self.root = new_root

        self._insert_non_full(
            self.root,
            key,
            value,
        )

    def _insert_non_full(
        self,
        node: BTreeNode,
        key: int,
        value,
    ):
        if node.leaf:
            index = 0

            while (
                index < len(node.keys)
                and node.keys[index] < key
            ):
                index += 1

            if (
                index < len(node.keys)
                and node.keys[index] == key
            ):
                node.values[index] = value
                return

            node.keys.insert(
                index,
                key,
            )

            node.values.insert(
                index,
                value,
            )

            return

        index = 0

        while (
            index < len(node.keys)
            and key >= node.keys[index]
        ):
            index += 1

        child = node.children[index]

        if len(child.keys) >= self.order - 1:
            self._split_child(
                node,
                index,
            )

            if key >= node.keys[index]:
                index += 1

        self._insert_non_full(
            node.children[index],
            key,
            value,
        )

    def _split_child(
        self,
        parent: BTreeNode,
        index: int,
    ):
        child = parent.children[index]

        if child.leaf:
            self._split_leaf(
                parent,
                index,
                child,
            )

        else:
            self._split_internal(
                parent,
                index,
                child,
            )

    def _split_leaf(
        self,
        parent: BTreeNode,
        index: int,
        child: BTreeNode,
    ):
        midpoint = len(child.keys) // 2

        right = BTreeNode(
            leaf=True,
            keys=child.keys[midpoint:],
            values=child.values[midpoint:],
        )

        child.keys = child.keys[:midpoint]
        child.values = child.values[:midpoint]

        right.next_leaf = child.next_leaf
        child.next_leaf = right

        parent.keys.insert(
            index,
            right.keys[0],
        )

        parent.children.insert(
            index + 1,
            right,
        )

    def _split_internal(
        self,
        parent: BTreeNode,
        index: int,
        child: BTreeNode,
    ):
        midpoint = len(child.keys) // 2

        promoted_key = child.keys[midpoint]

        right = BTreeNode(
            leaf=False,
            keys=child.keys[midpoint + 1:],
            children=child.children[midpoint + 1:],
        )

        child.keys = child.keys[:midpoint]
        child.children = child.children[:midpoint + 1]

        parent.keys.insert(
            index,
            promoted_key,
        )

        parent.children.insert(
            index + 1,
            right,
        )