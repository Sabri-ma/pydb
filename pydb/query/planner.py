from dataclasses import dataclass

from pydb.parser.ast import (
    SelectStatement,
)
from pydb.storage.table import Table


@dataclass(frozen=True)
class SequentialScanPlan:
    table: str

    def __str__(self) -> str:
        return (
            f"SequentialScan("
            f"table={self.table}"
            f")"
        )


@dataclass(frozen=True)
class IndexLookupPlan:
    table: str
    column: str
    value: int | str

    def __str__(self) -> str:
        return (
            f"IndexLookup("
            f"table={self.table}, "
            f"column={self.column}, "
            f"value={self.value}"
            f")"
        )


class QueryPlanner:
    def plan(
        self,
        statement: SelectStatement,
        table: Table,
    ):
        condition = statement.where

        if (
            condition is not None
            and condition.operator == "="
            and table.has_index(
                condition.column
            )
        ):
            return IndexLookupPlan(
                table=statement.table,
                column=condition.column,
                value=condition.value,
            )

        return SequentialScanPlan(
            table=statement.table
        )