"""Macro substitution and expansion utilities."""

from typing import Dict, Optional

from .astmodule import (
    Abstraction,
    Application,
    DefineExpr,
    DefMacroExpr,
    Expr,
    IfExpr,
    QuasiQuoteExpr,
    UnquoteExpr,
    Variable,
)
from .errors import MacroExpansionError
from .values import Macro, Value


def _qq_sub(tmpl: Expr, mapping: dict[str, Expr]) -> Expr:
    if isinstance(tmpl, UnquoteExpr):
        return UnquoteExpr(lambMacroSubstitute(tmpl.expr, mapping))
    if isinstance(tmpl, Application):
        return Application(
            _qq_sub(tmpl.func, mapping), [_qq_sub(a, mapping) for a in tmpl.args]
        )
    if isinstance(tmpl, Abstraction):
        return Abstraction(tmpl.param, _qq_sub(tmpl.body, mapping))
    if isinstance(tmpl, IfExpr):
        return IfExpr(
            _qq_sub(tmpl.cond, mapping),
            _qq_sub(tmpl.then_branch, mapping),
            _qq_sub(tmpl.else_branch, mapping),
        )
    # literals, vars, nested quasi-quotes stay untouched
    if isinstance(tmpl, QuasiQuoteExpr):
        return QuasiQuoteExpr(_qq_sub(tmpl.expr, mapping))
    return tmpl


def lambMacroSubstitute(expr: Expr, mapping: dict[str, Expr]) -> Expr:
    if isinstance(expr, Variable):
        return mapping.get(expr.name, expr)

    if isinstance(expr, QuasiQuoteExpr):
        return QuasiQuoteExpr(_qq_sub(expr.expr, mapping))

    if isinstance(expr, UnquoteExpr):  # (still useful if ever top-level)
        return UnquoteExpr(lambMacroSubstitute(expr.expr, mapping))

    if isinstance(expr, Application):
        return Application(
            lambMacroSubstitute(expr.func, mapping),
            [lambMacroSubstitute(a, mapping) for a in expr.args],
        )
    if isinstance(expr, Abstraction):
        return Abstraction(expr.param, lambMacroSubstitute(expr.body, mapping))
    if isinstance(expr, IfExpr):
        return IfExpr(
            lambMacroSubstitute(expr.cond, mapping),
            lambMacroSubstitute(expr.then_branch, mapping),
            lambMacroSubstitute(expr.else_branch, mapping),
        )
    if isinstance(expr, DefineExpr):
        return DefineExpr(expr.name, lambMacroSubstitute(expr.value, mapping))
    if isinstance(expr, DefMacroExpr):
        return DefMacroExpr(
            expr.name, expr.params, lambMacroSubstitute(expr.body, mapping)
        )
    return expr


def lambMacroExpand(expr: Expr, env: Dict[str, Value]) -> Optional[Expr]:
    """Expand macros in ``expr`` using definitions stored in ``env``."""

    # Expand application
    if isinstance(expr, Application) and isinstance(expr.func, Variable):
        macro = env.get(expr.func.name)
        if isinstance(macro, Macro):
            args = expr.args
            if len(args) != len(macro.params):
                raise MacroExpansionError(
                    f"Macro '{expr.func.name}' expects {len(macro.params)} "
                    f"args but got {len(args)}"
                )
            mapping = dict(zip(macro.params, args))
            expanded = lambMacroSubstitute(macro.body, mapping)
            return lambMacroExpand(expanded, env)
    # Recursively expand children
    if isinstance(expr, Application):
        new_func = lambMacroExpand(expr.func, env)
        if new_func is None:
            new_func = expr.func
        new_args = []
        for arg in expr.args:
            ea = lambMacroExpand(arg, env)
            new_args.append(ea if ea is not None else arg)
        return Application(new_func, new_args)
    if isinstance(expr, Abstraction):
        new_body = lambMacroExpand(expr.body, env)
        if new_body is None:
            new_body = expr.body
        return Abstraction(expr.param, new_body)
    if isinstance(expr, DefineExpr):
        new_value = lambMacroExpand(expr.value, env)
        if new_value is None:
            new_value = expr.value
        return DefineExpr(expr.name, new_value)
    if isinstance(expr, IfExpr):
        new_cond = lambMacroExpand(expr.cond, env)
        if new_cond is None:
            new_cond = expr.cond
        new_then = lambMacroExpand(expr.then_branch, env)
        if new_then is None:
            new_then = expr.then_branch
        new_else = lambMacroExpand(expr.else_branch, env)
        if new_else is None:
            new_else = expr.else_branch
        return IfExpr(new_cond, new_then, new_else)
    # Handle quasiquote that results from macro expansion
    if isinstance(expr, QuasiQuoteExpr):
        return qqWalk(expr.expr, env)

    # Handle macro definition
    if isinstance(expr, DefMacroExpr):
        macro = Macro(expr.params, expr.body)
        env[expr.name] = macro
        return None

    return expr


def qqWalk(expr: Expr, env: Dict[str, Value]) -> Expr:
    """Process a QuasiQuoteExpr template, splicing the result of any UnquoteExprs."""
    if isinstance(expr, UnquoteExpr):
        expanded = lambMacroExpand(expr.expr, env)
        return expanded if expanded is not None else expr.expr

    # Recurse structurally
    if isinstance(expr, Application):
        return Application(qqWalk(expr.func, env), [qqWalk(a, env) for a in expr.args])
    if isinstance(expr, Abstraction):
        return Abstraction(expr.param, qqWalk(expr.body, env))
    if isinstance(expr, IfExpr):
        return IfExpr(
            qqWalk(expr.cond, env),
            qqWalk(expr.then_branch, env),
            qqWalk(expr.else_branch, env),
        )
    if isinstance(expr, QuasiQuoteExpr):
        return QuasiQuoteExpr(qqWalk(expr.expr, env))
    return expr
