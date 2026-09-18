from .ast import Condition, InsertStatement, SelectStatement
from .tokens import Token, TokenType


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.position = 0

    @property
    def current(self) -> Token:
        return self.tokens[self.position]

    def advance(self) -> Token:
        token = self.current
        self.position += 1
        return token

    def expect(self, value: str) -> Token:
        if self.current.value.upper() != value.upper():
            raise ValueError(
                f"Expected {value}, got {self.current.value}"
            )

        return self.advance()

    def parse(self):
        if self.current.value == "SELECT":
            return self.parse_select()

        if self.current.value == "INSERT":
            return self.parse_insert()

        raise ValueError(
            f"Unsupported statement: {self.current.value}"
        )

    def parse_select(self) -> SelectStatement:
        self.expect("SELECT")

        columns = []

        if self.current.value == "*":
            columns.append("*")
            self.advance()
        else:
            columns.append(self.advance().value)

            while self.current.value == ",":
                self.advance()
                columns.append(self.advance().value)

        self.expect("FROM")

        table = self.advance().value

        where = None

        if self.current.value == "WHERE":
            where = self.parse_where()

        if self.current.value == ";":
            self.advance()

        return SelectStatement(
            columns=columns,
            table=table,
            where=where,
        )

    def parse_where(self) -> Condition:
        self.expect("WHERE")

        column = self.advance().value
        operator = self.advance().value
        value_token = self.advance()

        if value_token.type == TokenType.NUMBER:
            value = int(value_token.value)
        elif value_token.type == TokenType.STRING:
            value = value_token.value
        else:
            raise ValueError("Invalid WHERE value")

        return Condition(
            column=column,
            operator=operator,
            value=value,
        )

    def parse_insert(self) -> InsertStatement:
        self.expect("INSERT")
        self.expect("INTO")

        table = self.advance().value

        self.expect("VALUES")
        self.expect("(")

        values = []

        while self.current.value != ")":
            token = self.advance()

            if token.type == TokenType.NUMBER:
                values.append(int(token.value))

            elif token.type == TokenType.STRING:
                values.append(token.value)

            else:
                raise ValueError(
                    f"Invalid value: {token.value}"
                )

            if self.current.value == ",":
                self.advance()

        self.expect(")")

        if self.current.value == ";":
            self.advance()

        return InsertStatement(
            table=table,
            values=values,
        )