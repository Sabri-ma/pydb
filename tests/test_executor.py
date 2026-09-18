from pydb.parser.lexer import Lexer
from pydb.parser.parser import Parser
from pydb.query.executor import Database


def parse(sql: str):
    tokens = Lexer(sql).tokenize()
    return Parser(tokens).parse()


def test_insert_and_select():
    db = Database()

    db.create_table("users")

    db.execute(
        parse(
            "INSERT INTO users VALUES (1, 'Massine', 24);"
        )
    )

    rows = db.execute(
        parse(
            "SELECT * FROM users;"
        )
    )

    assert rows == [
        (1, "Massine", 24)
    ]


def test_multiple_rows():
    db = Database()
    db.create_table("users")

    db.execute(
        parse(
            "INSERT INTO users VALUES (1, 'Massine', 24);"
        )
    )

    db.execute(
        parse(
            "INSERT INTO users VALUES (2, 'Alice', 27);"
        )
    )

    rows = db.execute(
        parse(
            "SELECT * FROM users;"
        )
    )

    assert rows == [
        (1, "Massine", 24),
        (2, "Alice", 27),
    ]


def test_select_with_where():
    db = Database()
    db.create_table("users")

    db.execute(
        parse(
            "INSERT INTO users VALUES (1, 'Massine', 24);"
        )
    )

    db.execute(
        parse(
            "INSERT INTO users VALUES (2, 'Alice', 27);"
        )
    )

    rows = db.execute(
        parse(
            "SELECT * FROM users WHERE id = 2;"
        )
    )

    assert rows == [
        (2, "Alice", 27)
    ]


def test_select_where_string():
    db = Database()
    db.create_table("users")

    db.execute(
        parse(
            "INSERT INTO users VALUES (1, 'Massine', 24);"
        )
    )

    db.execute(
        parse(
            "INSERT INTO users VALUES (2, 'Alice', 27);"
        )
    )

    rows = db.execute(
        parse(
            "SELECT * FROM users WHERE name = 'Massine';"
        )
    )

    assert rows == [
        (1, "Massine", 24)
    ]