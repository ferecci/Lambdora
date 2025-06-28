from astmodule import *
from values import *

def lambEval(expr: Expr, env: dict[str, Value]) -> Value:
    if isinstance(expr, Variable):
        if expr.name in env:
            return env[expr.name]
        else:
            raise NameError(f"Unbound variable: {expr.name}")

    elif isinstance(expr, Literal):
        if expr.value.isdigit():
            return int(expr.value)
        return expr.value

    elif isinstance(expr, Abstraction):
        return Closure(expr.param, expr.body, env.copy())

    elif isinstance(expr, Application):
        func_val = lambEval(expr.func, env)
        args = [lambEval(arg, env) for arg in expr.args]

        result = func_val
        for arg in args:
            if isinstance(result, Closure):
                new_env = result.env.copy()
                new_env[result.param] = arg
                result = lambEval(result.body, new_env)

            elif isinstance(result, Builtin):
                result = result.func(arg)

            else:
                raise TypeError("Cannot apply non-function value")

        return result

    elif isinstance(expr, IfExpr):
        cond = lambEval(expr.cond, env)
        if not isinstance(cond, bool):
            raise TypeError("Condition in 'if' must be a Python bool")
        return (lambEval(expr.then_branch, env)
                if cond else
                lambEval(expr.else_branch, env))
    
    elif isinstance(expr, DefineExpr):
        # For recursion: make a placeholder so that closures can refer to 'name'
        env[expr.name] = None
        # Evaluate the right-hand side with that placeholder in scope
        value = lambEval(expr.value, env)
        # If it's a Closure, inject its own name into its env for self-calls
        if isinstance(value, Closure):
            value.env[expr.name] = value
        # Update the binding
        env[expr.name] = value
        return f"<defined {expr.name}>"

    elif isinstance(expr, DefMacroExpr):
        # Store macro definition in environment
        env[expr.name] = Macro(expr.params, expr.body)
        return f"<defined macro {expr.name}>"

    else:
        raise TypeError(f"Unknown expression type: {expr}")