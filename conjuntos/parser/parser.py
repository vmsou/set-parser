from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass
from enum import Enum, auto
from typing import TypeVar, Generic

from conjuntos.parser.exceptions import ParseError, EvaluateError
from conjuntos.parser.tokenizer import Tokenizer, Token
from conjuntos.model.evaluator import evaluate, set_element_t, set_function, get_priority, _OPERATORS, _UNARY_OPERATORS
from conjuntos.model.wrapper import Set, Number

# Type Alias
_T = TypeVar("_T")


class ParseState(Enum):
    OPERAND = auto()
    OPERATOR = auto()
    END = auto()


@dataclass(frozen=True)
class ParseResult(Generic[_T]):
    kind: str = "NONE"
    value: _T = None


class Parser(ABC, Generic[_T]):
    """ Represents an Abstract Parser Class. """
    @abstractmethod
    def parse(self, expression: str) -> ParseResult[_T]: ...


class SetParser(Parser):
    """ Parses and Evaluates Set Expressions. """
    def __init__(self, tokenizer: Tokenizer, variables: dict[str, set_element_t] = None, functions: dict[str, set_function] = None):
        self.tokenizer: Tokenizer = tokenizer
        self.variables: dict[str, set_element_t] = {} if (variables is None) else variables
        self.functions: dict[str, set_function] = {} if (functions is None) else functions

    def parse(self, expression: str) -> ParseResult[_T]:
        """ Reads the expression and returns its evaluation. """
        if expression.strip().lower() in ("sair", "quit", "exit"):
            return ParseResult(kind="EXIT")
        if expression.strip() == '':
            return ParseResult(kind="NONE")

        state: ParseState = ParseState.OPERAND
        tokens: list[Token] = self.tokenizer.tokenize(expression)

        stack: deque[Token] = deque()
        operands: deque[set_element_t] = deque()

        for t in tokens:
            if state == ParseState.OPERAND:
                if t.kind == "NUMBER":
                    operands.append(Number(t.value))
                    state = ParseState.OPERATOR
                elif t.kind == "VAR":
                    stack.append(t)
                    state = ParseState.OPERATOR
                elif t.kind == "OPEN":
                    stack.append(t)
                elif t.kind == "SET_OPEN":
                    stack.append(t)
                    stack.append(Token(kind="SEP", text=','))
                elif t.kind == "SET_CLOSE":
                    stack.pop()  # sep
                    should_open: Token = stack.pop()  # open
                    if should_open.kind != "SET_OPEN": raise ParseError(f"Error at '{should_open.text}' missing element.")
                    operands.append(Set())
                    state = ParseState.OPERATOR
                else:
                    raise ParseError(f"Unexpected Token: '{t.text}'")

            elif state == ParseState.OPERATOR:
                if t.kind in _OPERATORS:
                    while stack:
                        temp: Token = stack.pop()
                        stack.append(temp)  # stack.top()

                        if (temp.kind == "OPEN") or (get_priority(temp.kind) < get_priority(t.kind)):
                            break

                        if temp.kind == "VAR":
                            if t.kind == "DEFINE":
                                break
                            else:
                                var: Token = stack.pop()
                                if var.text not in self.variables:
                                    operands.append(var.text)
                                else:
                                    operands.append(self.variables[var.text])
                                    if t.kind != "END":
                                        break

                        elif temp.kind == "DEFINE":
                            stack.pop()  # define
                            var: Token = stack.pop()
                            if var.kind != "VAR":
                                raise ParseError(f"Expected Variable Name. Instead got: '{var.text}'")
                            value: set_element_t = operands.pop()
                            self.variables[var.text] = value

                        elif temp.kind in _UNARY_OPERATORS:
                            unary_op: Token = stack.pop()
                            unary_target: set_element_t = operands.pop()
                            if unary_op.kind == "COMPLEMENT":
                                if type(unary_target) != Set: raise ParseError("Complement expects a Set.")
                                if "S" not in self.variables: raise ParseError("Universal Set ('S') must be defined for complement.")
                                operands.append(evaluate("DIFFERENCE", self.variables["S"], unary_target))

                        elif temp.kind in _OPERATORS:
                            op: Token = stack.pop()
                            right: set_element_t = operands.pop()
                            left: set_element_t = operands.pop()
                            operands.append(evaluate(op.kind, left, right))

                    stack.append(t)
                    if t.kind in _UNARY_OPERATORS: continue  # Unary is treated like an operand; skips to Another Operator
                    state = ParseState.OPERAND
                    if t.kind == "END":
                        break

                elif t.kind in ("SEP", "OPEN"):
                    stack.append(t)
                    state = ParseState.OPERAND

                elif t.kind == "CLOSE":
                    args_count: int = 0
                    while stack:
                        arg_token: Token = stack.pop()
                        if arg_token.kind == "OPEN":
                            if stack:
                                should_var: Token = stack.pop()
                                if should_var.kind == "VAR":
                                    args: list[set_element_t] = []
                                    if args_count == 0 and operands:
                                        args.append(operands.pop())
                                    else:
                                        for _ in range(args_count): args.append(operands.pop())
                                    operands.append(self.functions[should_var.text](args[::-1]))
                                elif should_var.kind in _OPERATORS:
                                    stack.append(should_var)
                                    break
                                elif should_var.kind == "SEP":
                                    pass
                                else:
                                    raise ParseError(f"Expected Function. Instead got '{should_var.text}'.")
                            else:
                                break

                        if arg_token.kind == "VAR":
                            args_count += 1
                            if arg_token.text not in self.variables:
                                operands.append(arg_token.text)
                            else:
                                operands.append(self.variables[arg_token.text])

                        elif arg_token.kind in _UNARY_OPERATORS:
                            unary_target: set_element_t = operands.pop()
                            if arg_token.kind == "COMPLEMENT":
                                if type(unary_target) != Set: raise ParseError("Complement expects a Set.")
                                if "S" not in self.variables: raise ParseError("Universal Set ('S') must be defined for complement.")
                                operands.append(evaluate("DIFFERENCE", self.variables["S"], unary_target))

                        elif arg_token.kind in _OPERATORS:
                            right: set_element_t = operands.pop()
                            left: set_element_t = operands.pop()
                            result: set_element_t = evaluate(arg_token.kind, left, right)
                            operands.append(result)
                            args_count += 1

                elif t.kind == "SET_CLOSE":
                    group_set: Set[set_element_t] = Set()
                    while stack:
                        set_token: Token = stack.pop()
                        if set_token.kind == "SET_OPEN":
                            break
                        elif set_token.kind == "VAR":
                            if set_token.text not in self.variables:
                                operands.append(set_token.text)
                            else:
                                operands.append(self.variables[set_token.text])
                        elif set_token.kind == "SEP":
                            group_set.add(operands.pop())
                    operands.append(group_set)
                else:
                    raise ParseError(f"Undefined behavior for: '{t.text}'")

        should_end: Token = stack.pop()
        assert should_end.kind == "END", f"Expected END token. Instead got: '{should_end.text}'."

        if operands:
            return ParseResult(kind="VALUE", value=operands.pop())
        return ParseResult(kind="NONE")
