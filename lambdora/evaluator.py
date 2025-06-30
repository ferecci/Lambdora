"""Expression evaluation for Lambdora."""

from .astmodule import *
from .values import *

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
        env[expr.name] = None
        value = lambEval(expr.value, env)
        if isinstance(value, Closure):
            value.env[expr.name] = value
        env[expr.name] = value
        return f"<defined {expr.name}>"

    # Quasiquote    
    if isinstance(expr, QuasiquoteExpr):
        return evalQuasiquote(expr.value, env)

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
        result = func_val
        for i, arg in enumerate(args):
            new_env = result.env.copy()
            new_env[result.param] = arg
            # If this is the last argument and we're in tail position, use tail call optimization
            is_last_arg = (i == len(args) - 1)
            result = lambEval(result.body, new_env, is_tail and is_last_arg)
            if not isinstance(result, Closure):
                return result
        return result
    if isinstance(func_val, Builtin):
        result = func_val
        for arg in args:
            result = result.func(arg)
        return result
    raise TypeError("tried to apply a non-function value")

def evalQuasiquote(expr: Expr, env: dict[str, Value]) -> Expr:
    if isinstance(expr, UnquoteExpr):
        return lambEval(expr.value, env)
    if isinstance(expr, Application):
        return Application(
            evalQuasiquote(expr.func, env),
            [evalQuasiquote(arg, env) for arg in expr.args]
        )
    if isinstance(expr, Abstraction):
        return Abstraction(expr.param, evalQuasiquote(expr.body, env))
    if isinstance(expr, IfExpr):
        return IfExpr(
            evalQuasiquote(expr.cond, env),
            evalQuasiquote(expr.then_branch, env),
            evalQuasiquote(expr.else_branch, env)
        )
    if isinstance(expr, DefineExpr):
        return DefineExpr(expr.name, evalQuasiquote(expr.value, env))
    if isinstance(expr, DefMacroExpr):
        return DefMacroExpr(expr.name, expr.params, evalQuasiquote(expr.body, env))
    if isinstance(expr, QuasiquoteExpr):
        return QuasiquoteExpr(evalQuasiquote(expr.value, env))
    return expr