from pydb.parser.ast import (
    Condition,
    SelectStatement,
)
from pydb.query.planner import (
    IndexLookupPlan,
    QueryPlanner,
    SequentialScanPlan,
)
from pydb.storage.schema import (
    Column,
    ColumnType,
    Schema,
)
from pydb.storage.table import Table


def users_schema():
    return Schema(
        [
            Column(
                "id",
                ColumnType.INT,
            ),
            Column(
                "name",
                ColumnType.TEXT,
            ),
            Column(
                "age",
                ColumnType.INT,
            ),
        ]
    )


def test_planner_uses_sequential_scan_without_where():
    table = Table(
        users_schema()
    )

    planner = QueryPlanner()

    statement = SelectStatement(
        columns=["*"],
        table="users",
        where=None,
    )

    plan = planner.plan(
        statement,
        table,
    )

    assert plan == SequentialScanPlan(
        table="users"
    )


def test_planner_uses_sequential_scan_without_index():
    table = Table(
        users_schema()
    )

    planner = QueryPlanner()

    statement = SelectStatement(
        columns=["*"],
        table="users",
        where=Condition(
            column="id",
            operator="=",
            value=2,
        ),
    )

    plan = planner.plan(
        statement,
        table,
    )

    assert plan == SequentialScanPlan(
        table="users"
    )


def test_planner_uses_index_for_equality():
    table = Table(
        users_schema()
    )

    table.insert(
        (1, "Massine", 24)
    )

    table.insert(
        (2, "Alice", 30)
    )

    table.create_index(
        "id"
    )

    planner = QueryPlanner()

    statement = SelectStatement(
        columns=["*"],
        table="users",
        where=Condition(
            column="id",
            operator="=",
            value=2,
        ),
    )

    plan = planner.plan(
        statement,
        table,
    )

    assert plan == IndexLookupPlan(
        table="users",
        column="id",
        value=2,
    )


def test_planner_does_not_use_index_for_greater_than():
    table = Table(
        users_schema()
    )

    table.create_index(
        "id"
    )

    planner = QueryPlanner()

    statement = SelectStatement(
        columns=["*"],
        table="users",
        where=Condition(
            column="id",
            operator=">",
            value=2,
        ),
    )

    plan = planner.plan(
        statement,
        table,
    )

    assert plan == SequentialScanPlan(
        table="users"
    )


def test_sequential_scan_plan_string():
    plan = SequentialScanPlan(
        table="users"
    )

    assert str(plan) == (
        "SequentialScan(table=users)"
    )


def test_index_lookup_plan_string():
    plan = IndexLookupPlan(
        table="users",
        column="id",
        value=2,
    )

    assert str(plan) == (
        "IndexLookup("
        "table=users, "
        "column=id, "
        "value=2)"
    )