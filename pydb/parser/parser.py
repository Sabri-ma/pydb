from pydb.parser.ast import (
    ColumnDefinition,
    Condition,
    CreateIndexStatement,
    CreateTableStatement,
    ExplainStatement,
    InsertStatement,
    SelectStatement,
)
from pydb.parser.tokens import (
    Token,
    TokenType,
)


class Parser:
    def __init__(
        self,
        tokens: list[Token],
    ):
        self.tokens = tokens
        self.position = 0

    @property
    def current(self) -> Token:
        return self.tokens[
            self.position
        ]

    def advance(self) -> Token:
        token = self.current
        self.position += 1
        return token

    def expect(
        self,
        value: str,
    ) -> Token:
        if (
            self.current.value.upper()
            != value.upper()
        ):
            raise ValueError(
                f"Expected {value}, "
                f"got {self.current.value}"
            )

        return self.advance()

    def parse(self):
        if self.current.value == "SELECT":
            return self.parse_select()

        if self.current.value == "INSERT":
            return self.parse_insert()

        if self.current.value == "EXPLAIN":
            return self.parse_explain()

        if self.current.value == "CREATE":
            if (
                self.position + 1
                >= len(self.tokens)
            ):
                raise ValueError(
                    "Incomplete CREATE statement"
                )

            next_token = self.tokens[
                self.position + 1
            ]

            if next_token.value == "TABLE":
                return self.parse_create_table()

            if next_token.value == "INDEX":
                return self.parse_create_index()

        raise ValueError(
            f"Unsupported statement: "
            f"{self.current.value}"
        )

    def parse_select(
        self,
    ) -> SelectStatement:
        self.expect("SELECT")

        columns = []

        if self.current.value == "*":
            columns.append("*")
            self.advance()

        else:
            columns.append(
                self.advance().value
            )

            while self.current.value == ",":
                self.advance()

                columns.append(
                    self.advance().value
                )

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

    def parse_where(
        self,
    ) -> Condition:
        self.expect("WHERE")

        column = self.advance().value
        operator = self.advance().value
        value_token = self.advance()

        if value_token.type == TokenType.NUMBER:
            value = int(
                value_token.value
            )

        elif value_token.type == TokenType.STRING:
            value = value_token.value

        else:
            raise ValueError(
                "Invalid WHERE value"
            )

        return Condition(
            column=column,
            operator=operator,
            value=value,
        )

    def parse_insert(
        self,
    ) -> InsertStatement:
        self.expect("INSERT")
        self.expect("INTO")

        table = self.advance().value

        self.expect("VALUES")
        self.expect("(")

        values = []

        while self.current.value != ")":
            token = self.advance()

            if token.type == TokenType.NUMBER:
                values.append(
                    int(token.value)
                )

            elif token.type == TokenType.STRING:
                values.append(
                    token.value
                )

            else:
                raise ValueError(
                    f"Invalid value: "
                    f"{token.value}"
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

    def parse_create_table(
        self,
    ) -> CreateTableStatement:
        self.expect("CREATE")
        self.expect("TABLE")

        table = self.advance().value

        self.expect("(")

        columns = []

        while self.current.value != ")":
            column_name = (
                self.advance().value
            )

            column_type = (
                self.advance()
                .value
                .upper()
            )

            if column_type not in {
                "INT",
                "TEXT",
            }:
                raise ValueError(
                    f"Unsupported column type: "
                    f"{column_type}"
                )

            columns.append(
                ColumnDefinition(
                    name=column_name,
                    type=column_type,
                )
            )

            if self.current.value == ",":
                self.advance()

        self.expect(")")

        if self.current.value == ";":
            self.advance()

        return CreateTableStatement(
            table=table,
            columns=columns,
        )

    def parse_create_index(
        self,
    ) -> CreateIndexStatement:
        self.expect("CREATE")
        self.expect("INDEX")

        index_name = (
            self.advance().value
        )

        self.expect("ON")

        table = (
            self.advance().value
        )

        self.expect("(")

        column = (
            self.advance().value
        )

        self.expect(")")

        if self.current.value == ";":
            self.advance()

        return CreateIndexStatement(
            name=index_name,
            table=table,
            column=column,
        )

    def parse_explain(
        self,
    ) -> ExplainStatement:
        self.expect("EXPLAIN")

        if self.current.value != "SELECT":
            raise ValueError(
                "EXPLAIN currently supports "
                "SELECT only"
            )

        statement = self.parse_select()

        return ExplainStatement(
            statement=statement
        )