"""Utilities for pretty-printing Lambdora expressions."""

from .astmodule import (
    Abstraction,
    Application,
    DefineExpr,
    DefMacroExpr,
    Expr,
    IfExpr,
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
    elif isinstance(expr, IfExpr):
        cond = lambPrint(expr.cond)
        then_branch = lambPrint(expr.then_branch)
        else_branch = lambPrint(expr.else_branch)
        return f"(if {cond} {then_branch} {else_branch})"
    elif isinstance(expr, DefineExpr):
        return f"(define {expr.name} {lambPrint(expr.value)})"
    elif isinstance(expr, DefMacroExpr):
        params = " ".join(expr.params)
        return f"(defmacro {expr.name} ({params}) {lambPrint(expr.body)})"
    else:
        raise TypeError(f"Unknown expression type: {expr}")
