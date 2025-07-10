"""Utilities for pretty-printing Lambdora expressions."""

from .astmodule import (
    Abstraction,
    Application,
    Expr,
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
    else:
        raise TypeError(f"Unknown expression type: {expr}")
