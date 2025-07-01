"""Expression evaluation for Lambdora."""

from .astmodule import (
    Abstraction,
    Application,
    DefineExpr,
    DefMacroExpr,
    Expr,
    IfExpr,
    Literal,
    QuasiQuoteExpr,
    QuoteExpr,
    UnquoteExpr,
    Variable,
)
from .values import Builtin, Closure, Thunk, Value, nil


def lambEval(expr: Expr, env: dict[str, Value], is_tail: bool = False) -> Value:
    """Evaluate ``expr`` in ``env`` with optional tail-call optimization."""
    # Variables
    if isinstance(expr, Variable):
        if expr.name in env:
            return env[expr.name]
        else:
            raise NameError(f"unbound variable: {expr.name}")

    # Literals
    if isinstance(expr, Literal):
        if expr.value.isdigit():
            return int(expr.value)
        return expr.value

    # Abstraction
    if isinstance(expr, Abstraction):
        return Closure(expr.param, expr.body, env.copy())

    # Application
    if isinstance(expr, Application):

        def retire() -> Value:
            func_val = lambEval(expr.func, env)
            args = [lambEval(arg, env) for arg in expr.args]
            return applyFunc(func_val, args, is_tail)

        if is_tail:
            return Thunk(retire)
        else:
            return retire()

    # If-expression
    if isinstance(expr, IfExpr):
        cond = lambEval(expr.cond, env)
        if not isinstance(cond, bool):
            raise TypeError("condition in 'if' must be a boolean")
        branch = expr.then_branch if cond else expr.else_branch
        return lambEval(branch, env, is_tail)

    # Define-expression
    if isinstance(expr, DefineExpr):
        env[expr.name] = None  # type: ignore
        value = lambEval(expr.value, env)
        if isinstance(value, Closure):
            value.env[expr.name] = value
        env[expr.name] = value
        return f"<defined {expr.name}>"

    # Quasiquote
    if isinstance(expr, QuasiQuoteExpr):
        return evalQuasiquote(expr.expr, env)

    # Quote (do not evaluate)
    if isinstance(expr, QuoteExpr):
        return expr.value

    raise TypeError(f"Unknown expression type: {expr}")


def trampoline(result: Value) -> Value:
    while isinstance(result, Thunk):
        result = result.func()
    return result


def applyFunc(func_val: Value, args: list[Value], is_tail: bool = False) -> Value:
    if isinstance(func_val, Closure):
        result: Value = func_val
        for i, arg in enumerate(args):
            if not isinstance(result, Closure):
                return result
            new_env = result.env.copy()
            new_env[result.param] = arg
            # If this is the last argument and we're in tail position,
            # use tail call optimization
            is_last_arg = i == len(args) - 1
            result = lambEval(result.body, new_env, is_tail and is_last_arg)
            if not isinstance(result, Closure):
                return result
        return result
    if isinstance(func_val, Builtin):
        builtin_result: Value = func_val
        for arg in args:
            if not isinstance(builtin_result, Builtin):
                return builtin_result
            builtin_result = builtin_result.func(arg)
        # Handle 0-argument builtins
        if len(args) == 0:
            if isinstance(builtin_result, Builtin):
                # 0-argument builtins still need a dummy argument
                return builtin_result.func(nil)
            return builtin_result
        return builtin_result
    raise TypeError("tried to apply a non-function value")


def evalQuasiquote(expr: Expr, env: dict[str, Value]) -> Expr:
    # If we see an unquote, evaluate its contents immediately and embed the value
    if isinstance(expr, UnquoteExpr):
        value = lambEval(expr.expr, env)
        # Return the evaluated value directly - it will be embedded in the AST
        return value  # type: ignore

    # Nested quasiquotes: treat them as data
    if isinstance(expr, QuasiQuoteExpr):
        return QuasiQuoteExpr(evalQuasiquote(expr.expr, env))

    # Applications: recursively quasiquote func and args
    if isinstance(expr, Application):
        return Application(
            evalQuasiquote(expr.func, env),
            [evalQuasiquote(arg, env) for arg in expr.args],
        )

    # Lambda bodies: quasiquote inside the body
    if isinstance(expr, Abstraction):
        return Abstraction(expr.param, evalQuasiquote(expr.body, env))

    # If-expressions: quad-tree walk
    if isinstance(expr, IfExpr):
        return IfExpr(
            evalQuasiquote(expr.cond, env),
            evalQuasiquote(expr.then_branch, env),
            evalQuasiquote(expr.else_branch, env),
        )

    # Definitions: quasiquote the value
    if isinstance(expr, DefineExpr):
        return DefineExpr(expr.name, evalQuasiquote(expr.value, env))

    # Macro definitions: quasiquote the body
    if isinstance(expr, DefMacroExpr):
        return DefMacroExpr(expr.name, expr.params, evalQuasiquote(expr.body, env))

    # Literal and Variable and QuoteExpr just pass through
    # (QuoteExpr should remain as code data)
    if isinstance(expr, (Literal, Variable, QuoteExpr)):
        return expr

    # Fallback: leave any other node unchanged
    return expr
