"""Utilities for pretty-printing Lambdora expressions."""

from .astmodule import *

def lambPrint(expr: Expr) -> str:
    if isinstance(expr, Variable):
        return expr.name
    elif isinstance(expr, Literal):
        return expr.value
    elif isinstance(expr, Abstraction):
        return f"(λ{expr.param}. {lambPrint(expr.body)})"
    elif isinstance(expr, Application):
        parts = [lambPrint(expr.func)] + [lambPrint(arg) for arg in expr.args]
        return f"({' '.join(parts)})"
    elif isinstance(expr, QuasiquoteExpr):
        return f"`({lambPrint(expr.value)})"
    elif isinstance(expr, UnquoteExpr):
        return f",({lambPrint(expr.value)})"
    elif isinstance(expr, QuoteExpr):
        return f"'({lambPrint(expr.value)})"
    else:
        raise TypeError(f"Unknown expression type: {expr}")