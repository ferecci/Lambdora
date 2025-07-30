"""Macro substitution and expansion utilities."""

from typing import Dict, Optional

from .astmodule import (
    Abstraction,
    Application,
    DefineExpr,
    DefMacroExpr,
    Expr,
    IfExpr,
    LetRec,
    Literal,
    QuoteExpr,
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
    if isinstance(tmpl, QuasiQuoteExpr):
        return QuasiQuoteExpr(_qq_sub(tmpl.expr, mapping))
    return tmpl


def lambMacroSubstitute(expr: Expr, mapping: dict[str, Expr]) -> Expr:
    if isinstance(expr, Variable):
        return mapping.get(expr.name, expr)

    if isinstance(expr, QuasiQuoteExpr):
        return QuasiQuoteExpr(_qq_sub(expr.expr, mapping))

    if isinstance(expr, UnquoteExpr):
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

    if isinstance(expr, QuasiQuoteExpr):
        return qqWalk(expr.expr, env)
        
    if isinstance(expr, DefMacroExpr):
        macro = Macro(expr.params, expr.body)
        env[expr.name] = macro
        return None

    return expr

def _qq_walk(expr: Expr, env: dict[str, Value], depth: int = 0) -> Expr:
    if isinstance(expr, UnquoteExpr):
        if depth == 0:
            inner = _qq_walk(expr.expr, env, depth)
            expanded = lambMacroExpand(inner, env)
            return expanded if expanded is not None else inner
        return UnquoteExpr(_qq_walk(expr.expr, env, depth - 1))

    if isinstance(expr, QuasiQuoteExpr):
        return QuasiQuoteExpr(_qq_walk(expr.expr, env, depth + 1))

    if isinstance(expr, Application):
        return Application(
            _qq_walk(expr.func, env, depth),
            [_qq_walk(a, env, depth) for a in expr.args],
        )
    elif isinstance(expr, Abstraction):
        return Abstraction(expr.param, _qq_walk(expr.body, env, depth))
    elif isinstance(expr, IfExpr):
        return IfExpr(
            _qq_walk(expr.cond, env, depth),
            _qq_walk(expr.then_branch, env, depth),
            _qq_walk(expr.else_branch, env, depth),
        )
    elif isinstance(expr, DefineExpr):
        return DefineExpr(expr.name, _qq_walk(expr.value, env, depth))
    elif isinstance(expr, DefMacroExpr):
        return DefMacroExpr(
            expr.name, expr.params, _qq_walk(expr.body, env, depth)
        )
    elif isinstance(expr, LetRec):
        new_bindings = [(n, _qq_walk(v, env, depth)) for n, v in expr.bindings]
        new_body     = [_qq_walk(b, env, depth) for b in expr.body]
        return LetRec(new_bindings, new_body)

    if isinstance(expr, (QuoteExpr, Variable, Literal)):
        return expr

    return expr

def qqWalk(expr: Expr, env: Dict[str, Value]) -> Expr:
    return _qq_walk(expr, env)
