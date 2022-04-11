from __future__ import annotations

from typing import Callable, Dict, Generic, TypeVar

from conjuntos.parser.parser import Parser, ParseResult

# Type Alias
_T = TypeVar("_T")
_U = TypeVar("_U")
_parse_handler_c = Callable[[ParseResult[_T]], None]


class ParseHandler(Generic[_T]):
    """ Represents a Handler able to act on determined inputs. """

    def __init__(self, parser: Parser[_T], default_handler: _parse_handler_c | None = None):
        self.parser: Parser[_T] = parser
        self.handlers: Dict[str, _parse_handler_c] = {}
        self.default_handler: _parse_handler_c = default_handler

    def add(self, kind: str) -> Callable[[_parse_handler_c], _parse_handler_c]:
        def decorator(func: _parse_handler_c) -> _parse_handler_c:
            self.handlers[kind] = func

            def wrapper(r: ParseResult[_T]) -> None:
                func(r)

            return wrapper

        return decorator

    def resolve(self, expr: str) -> None:
        result: ParseResult[_T] = self.parser.parse(expr)
        if result.kind in self.handlers:
            self.handlers[result.kind](result)
        else:
            if self.default_handler:
                self.default_handler(result)
