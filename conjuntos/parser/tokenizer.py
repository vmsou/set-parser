from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from collections import deque


def is_float(text: str) -> bool:
    try:
        float(text)
        return True
    except ValueError:
        return False


@dataclass(frozen=True)
class Token:
    kind: str = field(init=True, default="NONE")
    value: float = field(init=True, default=0)
    text: str = field(init=True, default="")


class Tokenizer(ABC):
    """ Represents a Tokenizer; converts a string expression to a list of Tokens."""
    def __init__(self):
        self.stream: deque[str] = deque()

    # Methods
    def tokenize(self, expression: str) -> list[Token]:
        tokens: list[Token] = []
        self.stream = deque(expression.strip())

        while self.stream:
            t: Token = self.get()
            tokens.append(t)

        tokens.append(Token(kind="END"))

        return tokens

    @abstractmethod
    def get(self) -> Token: ...


class SetTokenizer(Tokenizer):
    """ Represents a Tokenizer able to read set characters as tokens. """

    def __init__(self, token_kind: dict[str, str]):
        super().__init__()
        self.token_kind: dict[str, str] = token_kind

    def next_char(self) -> str:
        char: str = " "
        while char.isspace():
            char = self.stream.popleft()
        return char

    def find_match(self, word: str) -> str:
        """ Future implementation; Aho-Corasick Algorithm. """
        return word

    def get(self) -> Token:
        char: str = self.next_char()

        if char in self.token_kind:
            return Token(kind=self.token_kind[char], text=char)

        self.stream.appendleft(char)
        num_str: str = ""
        while self.stream:
            char = self.stream.popleft()
            if char.isdigit() or char == '.':
                num_str += char
            else:
                self.stream.appendleft(char)
                break

        if is_float(num_str):
            return Token(kind="NUMBER", value=float(num_str))

        var_str: str = ""
        while self.stream:
            char = self.stream.popleft()
            if char.isspace():
                break
            if char in self.token_kind:
                self.stream.appendleft(char)
                break
            var_str += char
            if var_str in self.token_kind:
                return Token(kind=self.token_kind[var_str], text=var_str)

        return Token(kind="VAR", text=var_str)
