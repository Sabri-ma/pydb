from pydb.parser.ast import (
    Condition,
    InsertStatement,
    SelectStatement,
)
from pydb.parser.lexer import Lexer
from pydb.parser.parser import Parser
from pydb.parser.ast import ColumnDefinition, CreateTableStatement

def parse(sql: str):
    tokens = Lexer(sql).tokenize()
    return Parser(tokens).parse()


def test_select_all():
    statement = parse(
        "SELECT * FROM users;"
    )

    assert statement == SelectStatement(
        columns=["*"],
        table="users",
        where=None,
    )


def test_select_specific_columns():
    statement = parse(
        "SELECT id, name FROM users;"
    )

    assert statement == SelectStatement(
        columns=["id", "name"],
        table="users",
        where=None,
    )


def test_select_with_where_number():
    statement = parse(
        "SELECT * FROM users WHERE id = 1;"
    )

    assert statement == SelectStatement(
        columns=["*"],
        table="users",
        where=Condition(
            column="id",
            operator="=",
            value=1,
        ),
    )


def test_select_with_where_string():
    statement = parse(
        "SELECT * FROM users WHERE name = 'Massine';"
    )

    assert statement.where == Condition(
        column="name",
        operator="=",
        value="Massine",
    )


def test_insert():
    statement = parse(
        "INSERT INTO users VALUES (1, 'Massine', 24);"
    )

    assert statement == InsertStatement(
        table="users",
        values=[1, "Massine", 24],
    )

def test_create_table():
    statement = parse(
        """
        CREATE TABLE users (
            id INT,
            name TEXT,
            age INT
        );
        """
    )

    assert statement == CreateTableStatement(
        table="users",
        columns=[
            ColumnDefinition("id", "INT"),
            ColumnDefinition("name", "TEXT"),
            ColumnDefinition("age", "INT"),
        ],
    )