from astmodule import *
from typing import Dict
from values import Macro, Value

def lambMacroSubstitute(expr: Expr, mapping: Dict[str, Expr]) -> Expr:
    if isinstance(expr, Variable):
        return mapping.get(expr.name, expr)
    if isinstance(expr, Application):
        return Application(
            lambMacroSubstitute(expr.func, mapping),
            [lambMacroSubstitute(arg, mapping) for arg in expr.args]
        )
    if isinstance(expr, Abstraction):
        # Not handling capture; assume safe
        return Abstraction(expr.param, lambMacroSubstitute(expr.body, mapping))
    if isinstance(expr, IfExpr):
        return IfExpr(
            lambMacroSubstitute(expr.cond, mapping),
            lambMacroSubstitute(expr.then_branch, mapping),
            lambMacroSubstitute(expr.else_branch, mapping)
        )
    if isinstance(expr, DefineExpr):
        return DefineExpr(expr.name, lambMacroSubstitute(expr.value, mapping))
    if isinstance(expr, DefMacroExpr):
        return DefMacroExpr(expr.name, expr.params, lambMacroSubstitute(expr.body, mapping))
    # Literal and other types unchanged
    return expr

def lambMacroExpand(expr: Expr, env: Dict[str, Value]) -> Expr:
    # Handle defmacro
    if isinstance(expr, DefMacroExpr):
        env[expr.name] = Macro(expr.params, expr.body)
        return None
    # Expand application
    if isinstance(expr, Application) and isinstance(expr.func, Variable):
        macro = env.get(expr.func.name)
        if isinstance(macro, Macro):
            args = expr.args
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
    return expr