from pydb.parser.lexer import Lexer
from pydb.parser.parser import Parser
from pydb.query.executor import Database
from pydb.storage.schema import Column, ColumnType, Schema


def parse(sql: str):
    tokens = Lexer(sql).tokenize()
    return Parser(tokens).parse()


def users_schema():
    return Schema(
        [
            Column("id", ColumnType.INT),
            Column("name", ColumnType.TEXT),
            Column("age", ColumnType.INT),
        ]
    )


def test_insert_and_select():
    db = Database()
    db.create_table("users", users_schema())

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
    db.create_table("users", users_schema())

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
    db.create_table("users", users_schema())

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
    db.create_table("users", users_schema())

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


def test_create_table_from_sql():
    db = Database()

    db.execute(
        parse(
            """
            CREATE TABLE users (
                id INT,
                name TEXT,
                age INT
            );
            """
        )
    )

    assert "users" in db.tables


def test_select_specific_columns():
    db = Database()

    db.execute(
        parse(
            """
            CREATE TABLE users (
                id INT,
                name TEXT,
                age INT
            );
            """
        )
    )

    db.execute(
        parse(
            "INSERT INTO users VALUES (1, 'Massine', 24);"
        )
    )

    rows = db.execute(
        parse(
            "SELECT name, age FROM users;"
        )
    )

    assert rows == [
        ("Massine", 24)
    ]


def test_select_single_column():
    db = Database()

    db.execute(
        parse(
            """
            CREATE TABLE users (
                id INT,
                name TEXT,
                age INT
            );
            """
        )
    )

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
            "SELECT name FROM users;"
        )
    )

    assert rows == [
        ("Massine",),
        ("Alice",),
    ]


def test_where_greater_than():
    db = Database()

    db.execute(
        parse(
            """
            CREATE TABLE users (
                id INT,
                name TEXT,
                age INT
            );
            """
        )
    )

    db.execute(
        parse(
            "INSERT INTO users VALUES (1, 'Massine', 24);"
        )
    )

    db.execute(
        parse(
            "INSERT INTO users VALUES (2, 'Alice', 30);"
        )
    )

    rows = db.execute(
        parse(
            "SELECT * FROM users WHERE age > 24;"
        )
    )

    assert rows == [
        (2, "Alice", 30)
    ]


def test_where_less_than():
    db = Database()

    db.execute(
        parse(
            """
            CREATE TABLE users (
                id INT,
                name TEXT,
                age INT
            );
            """
        )
    )

    db.execute(
        parse(
            "INSERT INTO users VALUES (1, 'Massine', 24);"
        )
    )

    db.execute(
        parse(
            "INSERT INTO users VALUES (2, 'Alice', 30);"
        )
    )

    rows = db.execute(
        parse(
            "SELECT name FROM users WHERE age < 30;"
        )
    )

    assert rows == [
        ("Massine",)
    ]


def test_where_greater_than_or_equal():
    db = Database()

    db.execute(
        parse(
            """
            CREATE TABLE users (
                id INT,
                name TEXT,
                age INT
            );
            """
        )
    )

    db.execute(
        parse(
            "INSERT INTO users VALUES (1, 'Massine', 24);"
        )
    )

    db.execute(
        parse(
            "INSERT INTO users VALUES (2, 'Alice', 30);"
        )
    )

    rows = db.execute(
        parse(
            "SELECT name FROM users WHERE age >= 24;"
        )
    )

    assert rows == [
        ("Massine",),
        ("Alice",),
    ]


def test_where_less_than_or_equal():
    db = Database()

    db.execute(
        parse(
            """
            CREATE TABLE users (
                id INT,
                name TEXT,
                age INT
            );
            """
        )
    )

    db.execute(
        parse(
            "INSERT INTO users VALUES (1, 'Massine', 24);"
        )
    )

    db.execute(
        parse(
            "INSERT INTO users VALUES (2, 'Alice', 30);"
        )
    )

    rows = db.execute(
        parse(
            "SELECT name FROM users WHERE age <= 24;"
        )
    )

    assert rows == [
        ("Massine",)
    ]


def test_where_not_equal():
    db = Database()

    db.execute(
        parse(
            """
            CREATE TABLE users (
                id INT,
                name TEXT,
                age INT
            );
            """
        )
    )

    db.execute(
        parse(
            "INSERT INTO users VALUES (1, 'Massine', 24);"
        )
    )

    db.execute(
        parse(
            "INSERT INTO users VALUES (2, 'Alice', 30);"
        )
    )

    rows = db.execute(
        parse(
            "SELECT name FROM users WHERE age != 24;"
        )
    )

    assert rows == [
        ("Alice",)
    ]


def test_database_persists_across_restart(tmp_path):
    data_dir = tmp_path / "database"

    db = Database(
        str(data_dir)
    )

    db.execute(
        parse(
            """
            CREATE TABLE users (
                id INT,
                name TEXT,
                age INT
            );
            """
        )
    )

    db.execute(
        parse(
            "INSERT INTO users VALUES (1, 'Massine', 24);"
        )
    )

    reopened_db = Database(
        str(data_dir)
    )

    rows = reopened_db.execute(
        parse(
            "SELECT * FROM users;"
        )
    )

    assert rows == [
        (1, "Massine", 24)
    ]


def test_database_restores_schema(tmp_path):
    data_dir = tmp_path / "database"

    db = Database(
        str(data_dir)
    )

    db.execute(
        parse(
            """
            CREATE TABLE users (
                id INT,
                name TEXT,
                age INT
            );
            """
        )
    )

    reopened_db = Database(
        str(data_dir)
    )

    table = reopened_db.tables["users"]

    assert table.schema.column_index("id") == 0
    assert table.schema.column_index("name") == 1
    assert table.schema.column_index("age") == 2


def test_database_persists_multiple_rows(tmp_path):
    data_dir = tmp_path / "database"

    db = Database(
        str(data_dir)
    )

    db.execute(
        parse(
            """
            CREATE TABLE users (
                id INT,
                name TEXT,
                age INT
            );
            """
        )
    )

    db.execute(
        parse(
            "INSERT INTO users VALUES (1, 'Massine', 24);"
        )
    )

    db.execute(
        parse(
            "INSERT INTO users VALUES (2, 'Alice', 30);"
        )
    )

    reopened_db = Database(
        str(data_dir)
    )

    rows = reopened_db.execute(
        parse(
            "SELECT * FROM users;"
        )
    )

    assert rows == [
        (1, "Massine", 24),
        (2, "Alice", 30),
    ]


def test_persistent_database_where_query(tmp_path):
    data_dir = tmp_path / "database"

    db = Database(
        str(data_dir)
    )

    db.execute(
        parse(
            """
            CREATE TABLE users (
                id INT,
                name TEXT,
                age INT
            );
            """
        )
    )

    db.execute(
        parse(
            "INSERT INTO users VALUES (1, 'Massine', 24);"
        )
    )

    db.execute(
        parse(
            "INSERT INTO users VALUES (2, 'Alice', 30);"
        )
    )

    reopened_db = Database(
        str(data_dir)
    )

    rows = reopened_db.execute(
        parse(
            "SELECT name FROM users WHERE age > 24;"
        )
    )

    assert rows == [
        ("Alice",)
    ]