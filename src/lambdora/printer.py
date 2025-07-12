"""Utilities for pretty-printing Lambdora expressions."""

from .astmodule import (
    Abstraction,
    Application,
    Expr,
    LetRec,
    Literal,
    QuasiQuoteExpr,
    QuoteExpr,
    UnquoteExpr,
    Variable,
)


def lambPrint(expr: Expr) -> str:
    if isinstance(expr, Variable):
        return expr.name
    elif isinstance(expr, Literal):
        return expr.value
    elif isinstance(expr, Abstraction):
        return f"(lambda {expr.param}. {lambPrint(expr.body)})"
    elif isinstance(expr, Application):
        parts = [lambPrint(expr.func)] + [lambPrint(arg) for arg in expr.args]
        return f"({' '.join(parts)})"
    elif isinstance(expr, QuasiQuoteExpr):
        return f"`({lambPrint(expr.expr)})"
    elif isinstance(expr, UnquoteExpr):
        return f",({lambPrint(expr.expr)})"
    elif isinstance(expr, QuoteExpr):
        return f"'({lambPrint(expr.value)})"
    elif isinstance(expr, LetRec):
        binds = " ".join([f"({name} {lambPrint(val)})" for name, val in expr.bindings])
        bodies = " ".join([lambPrint(b) for b in expr.body])
        return f"(letrec ({binds}) {bodies})"
    else:
        raise TypeError(f"Unknown expression type: {expr}")
