from typing import Iterable, TypeVar

from model.evaluator import power_set, set_element_t
from model.wrapper import Set
from parser.exceptions import ParseError, EvaluateError
from parser.parser import Parser, SetParser, ParseResult
from parser.tokenizer import Tokenizer, SetTokenizer


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
        "IMPROPER_SUBSET": ["⊆"],
        "PROPER_SUBSET": ["⊂"],
        "SYMMETRIC_DIFFERENCE": ["⊖", "⊕", "^", "SYMMETRIC_DIFFERENCE"],
        "CARTESIAN": ["X"],
        "COMPLEMENT": ["'"]
    }
    symbol_to_kind: dict[str, str] = reverse_symbols(kind_to_symbols)
    set_tokenizer: Tokenizer = SetTokenizer(symbol_to_kind)

    parser: Parser[set_element_t] = SetParser(
        tokenizer=set_tokenizer,
        variables={
            "∅": Set(), "PI": 3.1415, "π": 3.1415, "A": Set.to_set((3, 5, 7, 9)), "S": Set.to_set(range(0, 10)),
            "B": Set.to_set(range(2, 7))
        },
        functions={"P": power_set}
    )

    print(" [Set Calculator] ".center(40, '-'))
    print("Operations: " + ", ".join("∪ ∩ - ⊕ X ' ⊂ ⊆ ∈".split()))
    print("You can define variables. \nExample: \n> A = {1, 2}")
    print("Get the powerset of a set by calling P(A) or P({...})")
    print("You can also enter 'exit' to close program.")
    print("".center(40, '-'))

    is_running: bool = True
    while is_running:
        expr: str = input("> ")
        try:
            result: ParseResult[set_element_t] = parser.parse(expr)
            if result.kind == "EXIT":
                print("Saida efetuada com sucesso.")
                is_running = False
            elif result.kind == "VALUE":
                print(result.value)
            elif result.kind == "NONE":
                pass
            else:
                print("Resultado inesperado.")
        except (ParseError, EvaluateError) as e:
            print("[ERROR]", str(e))


if __name__ == "__main__":
    main()
