from __future__ import annotations

from collections import defaultdict
from itertools import combinations
from typing import Union, Callable

from conjuntos.parser.exceptions import EvaluateError
from conjuntos.model.wrapper import Set, Number

# Type Aliases
set_element_t = Union[Number, bool, str, Set["set_element_t"], tuple["set_element_t", "set_element_t"]]
set_t = Union[Set[set_element_t]]
set_function = Callable[[list[set_element_t]], set_element_t]

# Operators
_UNARY_OPERATORS: set[str] = {"COMPLEMENT"}
_SET_OPERATORS: set[str] = {"UNION", "INTERSECT", "DIFFERENCE", "SYMMETRIC_DIFFERENCE", "CARTESIAN"}.union(_UNARY_OPERATORS)
_BOOL_OPERATORS: set[str] = {"BELONG", "NOT_BELONG", "PROPER_SUBSET", "IMPROPER_SUBSET", "NOT_SUBSET"}
_OPERATORS: set[str] = {"END", "DEFINE"}.union(_SET_OPERATORS.union(_BOOL_OPERATORS))

_priorities: defaultdict[str, int] = defaultdict(lambda: 0)
_priorities.update(dict(END=-1, VAR=1, NUMBER=1, COMPLEMENT=2))


def get_priority(kind: str) -> int:
    return _priorities[kind]


def power_set(args: list[Set[set_element_t]]) -> Set[set_element_t]:
    s = args[0]
    ps: Set = Set()
    # Empty
    ps.add(Set())

    # Individual
    for e in s:
        ps.add(Set({e}))

    # Combinations
    for i in range(2, len(s)):
        for comb in combinations(s, r=i):
            ps.add(Set(comb))
    ps.add(s)
    return ps


def is_proper_subset(left: Set, right: Set):
    if not right or len(left) == len(right): return False
    for i in left:
        if i not in right: return False
    return True


def is_proper_subset2(left: Set, right: Set):
    return len(left) != len(right) and len(right.intersection(left)) == len(left)


def cartesian_product(left: Set[set_element_t], right: Set[set_element_t]) -> Set[set_element_t]:
    result: Set[set_element_t] = Set()
    for x in left:
        for y in right:
            result.add((x, y))

    return result


_evaluations: dict[str, Callable[[set_element_t, set_element_t], set_element_t]] = {
    # Return Set
    "UNION": lambda l, r: Set(l.union(r)),
    "INTERSECT": lambda l, r: Set(l.intersection(r)),
    "DIFFERENCE": lambda l, r: Set(l.difference(r)),
    "SYMMETRIC_DIFFERENCE": lambda l, r: Set(l.symmetric_difference(r)),
    "CARTESIAN": cartesian_product,

    # Return Boolean
    "BELONG": lambda l, r: l in r,
    "NOT_BELONG": lambda l, r: l not in r,
    "PROPER_SUBSET": is_proper_subset,
    "IMPROPER_SUBSET": lambda l, r: l == r,
    "NOT_SUBSET": lambda l, r: not is_proper_subset(l, r)
}


def evaluate(op: str, left: set_element_t, right: set_element_t) -> set_element_t:
    # Invalid Operations
    if op in _SET_OPERATORS and (type(left) != Set or type(right) != Set):
        return False

    if op in _BOOL_OPERATORS and (type(left) in (Number, bool) and type(right) in (Number, bool)):
        return False

    if op in ("PROPER_SUBSET", "IMPROPER_SUBSET"):
        if Set not in (type(left), type(right)):
            return False

    # Evaluations
    if op in _evaluations:
        return _evaluations[op](left, right)
    raise EvaluateError(f"Invalid Operation: {left} {op} {right}")
