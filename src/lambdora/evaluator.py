"""Expression evaluation for Lambdora."""

from typing import cast

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
from .errors import EvalError, ParseError, RecursionInitError
from .values import Builtin, Closure, Macro, Thunk, Value, nil


class _RecPlaceholder:  # noqa: D401 – sentinel class
    def __repr__(self) -> str:  # pragma: no cover
        return "<rec-placeholder>"


_REC_PLACEHOLDER: Value = cast(Value, _RecPlaceholder())


def lambEval(expr: Expr, env: dict[str, Value], is_tail: bool = False) -> Value:
    """Evaluate ``expr`` in ``env``."""
    # Variables
    if isinstance(expr, Variable):
        if expr.name in env:
            val = env[expr.name]
            if val is _REC_PLACEHOLDER:
                raise RecursionInitError(
                    f"recursive binding '{expr.name}' accessed before initialisation"
                )
            return val
        else:
            raise EvalError(f"unbound variable: {expr.name}")

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
        if isinstance(expr.func, Variable):
            fname = expr.func.name
            if fname == "lambda":
                if (
                    len(expr.args) != 3
                    or not isinstance(expr.args[1], Literal)
                    or expr.args[1].value != "."
                ):
                    raise EvalError("lambda syntax: (lambda param . body)")
                param_ast = expr.args[0]
                if isinstance(param_ast, Variable):
                    param = param_ast.name
                elif isinstance(param_ast, Literal) and isinstance(
                    param_ast.value, str
                ):
                    param = param_ast.value
                else:
                    param_val = lambEval(param_ast, env, False)
                    if not isinstance(param_val, str):
                        raise EvalError("lambda param must be string identifier")
                    param = param_val
                body = expr.args[2]
                return Closure(param, body, env.copy())
            elif fname == "quasiquote":
                if len(expr.args) != 1:
                    raise EvalError("quasiquote requires exactly one argument")
                return evalQuasiquote(expr.args[0], env)
            elif fname == "quote":
                if len(expr.args) != 1:
                    raise EvalError("quote requires exactly one argument")
                return expr.args[0]
            elif fname == "unquote":
                if len(expr.args) != 1:
                    raise EvalError("unquote requires exactly one argument")
                # Unquote should only be used inside quasiquote
                raise EvalError("unquote can only be used inside quasiquote")
            elif fname == "if":
                if len(expr.args) != 3:
                    raise ParseError("if requires condition, then, else")
                cond = lambEval(expr.args[0], env, False)
                if not isinstance(cond, bool):
                    raise EvalError("if condition must be boolean")
                branch = expr.args[1] if cond else expr.args[2]
                return lambEval(branch, env, is_tail)
            elif fname == "define":
                if len(expr.args) != 2:
                    raise EvalError("define requires name and value")
                name_ast = expr.args[0]
                if isinstance(name_ast, Variable):
                    name = name_ast.name
                elif isinstance(name_ast, Literal) and isinstance(name_ast.value, str):
                    name = name_ast.value
                else:
                    name_val = lambEval(name_ast, env, False)
                    if not isinstance(name_val, str):
                        raise EvalError("define name must be string identifier")
                    name = name_val
                value = lambEval(expr.args[1], env, False)
                env[name] = value
                if isinstance(value, Closure):
                    value.env[name] = value
                return f"<defined {name}>"
            elif fname == "let":
                if len(expr.args) < 3 or not isinstance(expr.args[0], Variable):
                    raise EvalError("let syntax: (let var val body...)")
                var = expr.args[0].name
                val = lambEval(expr.args[1], env, False)
                new_env = env.copy()
                new_env[var] = val
                bodies = expr.args[2:]
                if not bodies:
                    raise EvalError("let requires at least one body")
                let_result: Value = nil
                for idx, b in enumerate(bodies):
                    is_last = idx == len(bodies) - 1
                    let_result = lambEval(b, new_env, is_tail and is_last)
                return let_result
            elif fname == "defmacro":
                if len(expr.args) != 3:
                    raise EvalError("defmacro requires name, params, body")
                name_ast = expr.args[0]
                if not isinstance(name_ast, Variable):
                    raise EvalError("defmacro name must be identifier")
                name = name_ast.name
                params_ast = expr.args[1]
                body = expr.args[2]
                params = []
                if isinstance(params_ast, Application) and isinstance(
                    params_ast.func, Variable
                ):
                    params.append(params_ast.func.name)
                    for p in params_ast.args:
                        if not isinstance(p, Variable):
                            raise EvalError("defmacro params must be identifiers")
                        params.append(p.name)
                elif isinstance(params_ast, Variable):
                    params = [params_ast.name]
                else:
                    raise EvalError("defmacro params must be list of identifiers")
                env[name] = Macro(params, body)
                return "<macro defined>"

            # Add letrec if needed
        # General case
        def retire() -> Value:
            func_val = lambEval(expr.func, env, False)
            args = [lambEval(a, env, False) for a in expr.args]
            return applyFunc(func_val, args, is_tail)

        if is_tail:
            return Thunk(retire)
        else:
            return retire()

    # If-expression
    if isinstance(expr, IfExpr):
        cond = lambEval(expr.cond, env)
        if not isinstance(cond, bool):
            raise EvalError("condition in 'if' must be a boolean")
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

    # LetRec-expression
    if isinstance(expr, LetRec):
        new_env = env.copy()

        # Pre-bind names to placeholder
        for name, _ in expr.bindings:
            new_env[name] = _REC_PLACEHOLDER

        # Evaluate each binding RHS in the same env
        for name, rhs in expr.bindings:
            val = lambEval(rhs, new_env)
            new_env[name] = val
            if isinstance(val, Closure):
                val.env[name] = val

        # Patch mutually recursive closure envs
        for item in new_env.values():
            if isinstance(item, Closure):
                for bind_name, _ in expr.bindings:
                    item.env[bind_name] = new_env[bind_name]

        result: Value = nil
        for idx, body_expr in enumerate(expr.body):
            is_last = idx == len(expr.body) - 1
            result = lambEval(body_expr, new_env, is_tail and is_last)
        return result

    # Quasiquote
    if isinstance(expr, QuasiQuoteExpr):
        return evalQuasiquote(expr.expr, env)

    # Quote (do not evaluate)
    if isinstance(expr, QuoteExpr):
        return expr.value

    # DefMacro-expression
    if isinstance(expr, DefMacroExpr):
        env[expr.name] = Macro(expr.params, expr.body)
        return "<macro defined>"

    raise EvalError(f"Unknown expression type: {expr}")


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
    if isinstance(func_val, Macro):
        # This should not happen - macros should be expanded before evaluation
        raise EvalError("tried to apply a macro as a function - macro expansion failed")
    raise EvalError("tried to apply a non-function value")


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
        # Handle quasiquote applications specially
        if isinstance(expr.func, Variable) and expr.func.name == "quasiquote":
            if len(expr.args) == 1:
                return QuasiQuoteExpr(evalQuasiquote(expr.args[0], env))
            else:
                raise EvalError("quasiquote requires exactly one argument")

        # Handle unquote applications specially
        if isinstance(expr.func, Variable) and expr.func.name == "unquote":
            if len(expr.args) == 1:
                # Evaluate the unquoted expression and return the result
                return lambEval(expr.args[0], env)  # type: ignore
            else:
                raise EvalError("unquote requires exactly one argument")

        # Handle if applications specially
        if isinstance(expr.func, Variable) and expr.func.name == "if":
            if len(expr.args) == 3:
                return IfExpr(
                    evalQuasiquote(expr.args[0], env),
                    evalQuasiquote(expr.args[1], env),
                    evalQuasiquote(expr.args[2], env),
                )
            else:
                raise EvalError("if requires condition, then, else")

        # Handle define applications specially
        if isinstance(expr.func, Variable) and expr.func.name == "define":
            if len(expr.args) == 2:
                return DefineExpr(
                    (
                        expr.args[0].name
                        if isinstance(expr.args[0], Variable)
                        else str(expr.args[0])
                    ),
                    evalQuasiquote(expr.args[1], env),
                )
            else:
                raise EvalError("define requires name and value")

        # Handle defmacro applications specially
        if isinstance(expr.func, Variable) and expr.func.name == "defmacro":
            if len(expr.args) >= 3:
                # Extract name
                name = (
                    expr.args[0].name
                    if isinstance(expr.args[0], Variable)
                    else str(expr.args[0])
                )
                # Extract parameters - should be a list of variables
                if (
                    isinstance(expr.args[1], Application)
                    and isinstance(expr.args[1].func, Variable)
                    and expr.args[1].func.name == "list"
                ):
                    params = [
                        arg.name if isinstance(arg, Variable) else str(arg)
                        for arg in expr.args[1].args
                    ]
                else:
                    params = []
                # Extract body
                body = evalQuasiquote(expr.args[2], env)
                return DefMacroExpr(name, params, body)
            else:
                raise EvalError("defmacro requires name, params, and body")

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
