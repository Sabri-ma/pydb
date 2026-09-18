import pytest

from pydb.parser.lexer import Lexer
from pydb.parser.tokens import TokenType


def test_select_statement():
    tokens = Lexer(
        "SELECT * FROM users;"
    ).tokenize()

    assert tokens[0].value == "SELECT"
    assert tokens[1].value == "*"
    assert tokens[2].value == "FROM"
    assert tokens[3].value == "users"


def test_insert_statement():
    tokens = Lexer(
        "INSERT INTO users VALUES (1, 'Massine');"
    ).tokenize()

    values = [token.value for token in tokens]

    assert values == [
        "INSERT",
        "INTO",
        "users",
        "VALUES",
        "(",
        "1",
        ",",
        "Massine",
        ")",
        ";",
        "",
    ]


def test_keyword_case_insensitive():
    tokens = Lexer(
        "select * from users"
    ).tokenize()

    assert tokens[0].value == "SELECT"
    assert tokens[2].value == "FROM"


def test_identifier():
    tokens = Lexer(
        "SELECT username FROM users"
    ).tokenize()

    assert tokens[1].type == TokenType.IDENTIFIER
    assert tokens[1].value == "username"


def test_number():
    tokens = Lexer(
        "WHERE id = 42"
    ).tokenize()

    assert tokens[3].type == TokenType.NUMBER
    assert tokens[3].value == "42"


def test_string():
    tokens = Lexer(
        "WHERE name = 'Massine'"
    ).tokenize()

    assert tokens[3].type == TokenType.STRING
    assert tokens[3].value == "Massine"


def test_invalid_character():
    with pytest.raises(ValueError):
        Lexer("SELECT @ FROM users").tokenize()