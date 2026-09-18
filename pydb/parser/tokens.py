from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    KEYWORD = auto()
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()
    SYMBOL = auto()
    EOF = auto()


@dataclass(frozen=True)
class Token:
    type: TokenType
    value: str