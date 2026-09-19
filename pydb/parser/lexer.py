from .tokens import Token, TokenType


KEYWORDS = {
    "SELECT",
    "FROM",
    "WHERE",
    "INSERT",
    "INTO",
    "VALUES",
    "CREATE",
    "TABLE",
    "UPDATE",
    "DELETE",
    "INT",
    "TEXT",
}


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.position = 0

    def tokenize(self) -> list[Token]:
        tokens = []

        while self.position < len(self.source):
            char = self.source[self.position]

            if char.isspace():
                self.position += 1
                continue

            if char.isalpha() or char == "_":
                tokens.append(self._read_word())
                continue

            if char.isdigit():
                tokens.append(self._read_number())
                continue

            if char in {"'", '"'}:
                tokens.append(self._read_string())
                continue

            if char in {"(", ")", ",", ";", "*", "=", "<", ">"}:
                tokens.append(
                    Token(TokenType.SYMBOL, char)
                )
                self.position += 1
                continue

            raise ValueError(
                f"Unexpected character: {char}"
            )

        tokens.append(Token(TokenType.EOF, ""))

        return tokens

    def _read_word(self) -> Token:
        start = self.position

        while self.position < len(self.source):
            char = self.source[self.position]

            if not (char.isalnum() or char == "_"):
                break

            self.position += 1

        value = self.source[start:self.position]

        if value.upper() in KEYWORDS:
            return Token(
                TokenType.KEYWORD,
                value.upper(),
            )

        return Token(TokenType.IDENTIFIER, value)

    def _read_number(self) -> Token:
        start = self.position

        while (
            self.position < len(self.source)
            and self.source[self.position].isdigit()
        ):
            self.position += 1

        return Token(
            TokenType.NUMBER,
            self.source[start:self.position],
        )

    def _read_string(self) -> Token:
        quote = self.source[self.position]
        self.position += 1

        start = self.position

        while (
            self.position < len(self.source)
            and self.source[self.position] != quote
        ):
            self.position += 1

        if self.position >= len(self.source):
            raise ValueError("Unterminated string")

        value = self.source[start:self.position]

        self.position += 1

        return Token(TokenType.STRING, value)