import time

from typing import Iterable, TypeVar

from conjuntos.model.evaluator import power_set, set_element_t
from conjuntos.model.wrapper import Set
from conjuntos.model.resolve import ParseHandler

from conjuntos.parser.exceptions import ParseError, EvaluateError
from conjuntos.parser.parser import Parser, SetParser, ParseResult
from conjuntos.parser.tokenizer import Tokenizer, SetTokenizer


# Type Aliases
_T = TypeVar("_T")
_U = TypeVar("_U")


def reverse_symbols(mapped: dict[_T, Iterable[_U]]) -> dict[_U, _T]:
    """ Makes a list of values point to a key. """
    reversed_mapped: dict[str, str] = dict()
    for k, v in mapped.items():
        for item in v:
            reversed_mapped[item] = k
    return reversed_mapped


def main() -> None:
    kind_to_symbols: dict[str, list[str]] = {
        "SET_OPEN": ["{"], "SET_CLOSE": ["}"],
        "OPEN": ["("], "CLOSE": [")"],
        "SEP": [","],
        "DEFINE": ["="],
        "UNION": ["⋃", "∪", "UNION"],
        "INTERSECT": ["⋂", "∩", "^", "INTERSECT", "INTERSECTION"],
        "DIFFERENCE": ["-", "DIFFERENCE"],
        "BELONG": ["∈", "e"],
        "NOT_BELONG": ["∉"],
        "IMPROPER_SUBSET": ["⊆"],
        "PROPER_SUBSET": ["⊂"],
        "NOT_SUBSET": ["⊄"],
        "SYMMETRIC_DIFFERENCE": ["⊖", "⊕", "^", "SYMMETRIC_DIFFERENCE"],
        "CARTESIAN": ["X", "x"],
        "COMPLEMENT": ["'"]
    }
    symbol_to_kind: dict[str, str] = reverse_symbols(kind_to_symbols)
    set_tokenizer: Tokenizer = SetTokenizer(symbol_to_kind)

    parser: Parser[set_element_t] = SetParser(
        tokenizer=set_tokenizer,
        variables={
            "∅": Set(), "PI": 3.1415, "π": 3.1415
        },
        functions={"P": power_set}
    )

    handler: ParseHandler = ParseHandler(
        parser=parser,
        default_handler=lambda x: print("Unexpected Result.")
    )

    print(" [Set Calculator] ".center(40, '-'))
    print("Operations: " + ", ".join("∪ ∩ - ⊕ X ' ⊂ ⊆ ∈".split()))
    print("You can define variables. \nExample: \n> A = {1, 2}")
    print("Get the powerset of a set by calling P(A) or P({...})")
    print("You can also enter 'exit' to close program.")
    print("".center(40, '-'))

    exprs: list[str] = [
        "A = {3, 5, 7, 9}",
        "B = {2, 3, 4, 5, 6}",
        "A ⊕ B",
        "(A ∪ B) - (A ∩ B)",
        "A ⊕ A",
        "∅ ⊕ A"
    ]

    is_running: bool = True

    @handler.add("NONE")
    def _value(r: ParseResult[set_element_t]) -> None:
        pass

    @handler.add("EXIT")
    def _exit(r: ParseResult[set_element_t]) -> None:
        nonlocal is_running
        is_running = False
        print("Successful exit.")

    @handler.add("VALUE")
    def _value(r: ParseResult[set_element_t]) -> None:
        print(r.value)

    for expr in exprs:
        print(">", expr)
        handler.resolve(expr)
        time.sleep(1)

    while is_running:
        expr: str = input("> ")
        try:
            handler.resolve(expr)
        except (ParseError, EvaluateError) as e:
            print("[ERROR]", str(e))


if __name__ == "__main__":
    main()
