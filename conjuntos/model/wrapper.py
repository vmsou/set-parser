from __future__ import annotations

from typing import Iterable, TypeVar

_T = TypeVar("_T")


class SetWrapper(set):
    """ Wrapper for built-in set; for representation. """
    def __init__(self, iterable: Iterable[_T] = None):
        super().__init__()
        if iterable:
            for i in iterable:
                if type(i) in (int, float): self.add(Number(i))
                else: self.add(i)

    def __str__(self) -> str:
        if self:
            return '{' + ", ".join(str(i) for i in self) + '}'
        return "∅"

    def __hash__(self) -> int:
        return hash(frozenset(self))

    def __eq__(self, other) -> bool:
        if type(self) != type(other):
            return False
        return super().__eq__(other)

    @staticmethod
    def to_set(iterable: Iterable[_T]) -> SetWrapper[_T]:
        new_set: SetWrapper[_T] = SetWrapper()
        for i in iterable:
            if type(i) in (int, float): new_set.add(Number(i))
            else: new_set.add(i)
        return new_set


class Number:
    """ Wrapper for built-in int and float; for representation. """
    def __init__(self, value: float) -> None:
        self.value: float = value

    def __str__(self) -> str:
        if int(self.value) != self.value:
            return str(self.value)
        return str(int(self.value))

    def __repr__(self) -> str:
        return self.__str__()

    def __hash__(self) -> int:
        return hash(self.value)

    def __eq__(self, other) -> bool:
        if type(self) != type(other):
            return False
        return self.value == other.value
