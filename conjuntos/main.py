import sys
import time

from typing import Iterable, TypeVar

from conjuntos.model.evaluator import power_set, set_element_t
from conjuntos.model.wrapper import Set

from conjuntos.parser.exceptions import ParseError, EvaluateError
from conjuntos.parser.parser import Parser, SetParser, ParseResult
from conjuntos.parser.resolve import ParseHandler
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


def write_print(text: str, delay: float = 0.1, end='\n', end_delay: float = 1) -> None:
    for c in text:
        sys.stdout.write(c)
        time.sleep(delay)
        sys.stdout.flush()
    time.sleep(end_delay)
    sys.stdout.write(end)


def simulate(handler: ParseHandler[_T], exprs: Iterable[str]) -> None:
    print("Simulating...")
    for expr in exprs:
        print(">", end=' ', flush=True)
        time.sleep(1)
        write_print(expr, delay=0.1, end_delay=1)
        handler.resolve(expr)
    print("Simulation Finished.")


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
        "CARTESIAN": ["X"],
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

    handler: ParseHandler[set_element_t] = ParseHandler(
        parser=parser,
        default_handler=lambda x: print("Unexpected Result.")
    )

    print(" [Set Calculator] ".center(40, '-'))
    print("Operations: " + ", ".join("∪ ∩ - ⊕ X ' ⊂ ⊆ ∈".split()))
    print("You can define variables. \nExample: \n> A = {1, 2}")
    print("You can do operations. \nExample: \n> 1 ∈ {1, 2}")
    print("Get the powerset of a set by calling P(A) or P({...})")
    print("You can also enter 'exit' to close program.")
    print("".center(40, '-'))

    is_running: bool = True

    @handler.add("NONE")
    def _value(r: ParseResult[set_element_t]) -> None:
        pass

    @handler.add("EXIT")
    def _exit(r: ParseResult[set_element_t]) -> None:
        nonlocal is_running
        is_running = False
        print(f"Successful exit with code={r.value}.")

    @handler.add("VALUE")
    def _value(r: ParseResult[set_element_t]) -> None:
        print(r.value)

    exprs: list[str] = [
        "A = {3, 5, 7, 9}",
        "B = {2, 3, 4, 5, 6}",
        "A ⊕ B",
        "(A ∪ B) - (A ∩ B)",
        "A ⊕ A",
        "∅ ⊕ A"
    ]
    simulate(handler, exprs)

    while is_running:
        expr: str = input("> ")
        try:
            handler.resolve(expr)
        except (ParseError, EvaluateError) as e:
            print("[ERROR]", str(e))


if __name__ == "__main__":
    main()
