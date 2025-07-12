"""AST node definitions for the Lambdora language."""

from dataclasses import dataclass
from typing import List


@dataclass
class Expr:
    pass


@dataclass
class Variable(Expr):
    name: str


@dataclass
class Literal(Expr):
    value: str


@dataclass
class Abstraction(Expr):
    param: str
    body: Expr


@dataclass
class Application(Expr):
    func: Expr
    args: List[Expr]


@dataclass
class DefineExpr(Expr):
    name: str
    value: Expr


@dataclass
class IfExpr(Expr):
    cond: Expr
    then_branch: Expr
    else_branch: Expr


@dataclass
class DefMacroExpr(Expr):
    name: str
    params: List[str]
    body: Expr


@dataclass
class QuoteExpr(Expr):
    value: Expr


@dataclass
class QuasiQuoteExpr(Expr):
    expr: Expr


@dataclass
class UnquoteExpr(Expr):
    expr: Expr


@dataclass
class LetRec(Expr):
    bindings: List[tuple[str, Expr]]
    body: List[Expr]
