from astmodule import Expr, Abstraction, Variable
from dataclasses import dataclass
from typing import Callable, Union, List

Value = Union[int, str, bool, 'Closure', 'Builtin', 'Pair', 'Nil', 'Macro']

@dataclass
class Closure:
    param: str
    body: Expr
    env: dict[str, Value]

@dataclass
class Builtin:
    func: Callable[[Value], Value]

@dataclass
class Pair:
    head: Value
    tail: Value

@dataclass
class Macro:
    params: List[str]
    body: Expr

class Nil:
    def __repr__(self):
        return "nil"

nil = Nil()

def isChurchTrue(c: Closure) -> bool:
    return (
        isinstance(c.body, Abstraction) and
        isinstance(c.body.body, Variable) and
        c.body.body.name == c.param
    )

def isChurchFalse(c: Closure) -> bool:
    return (
        isinstance(c.body, Abstraction) and
        isinstance(c.body.body, Variable) and
        c.body.body.name == c.body.param
    )

def valueToString(val: Value) -> str:
    if isinstance(val, Closure):
        if isChurchTrue(val):
            return "true"
        if isChurchFalse(val):
            return "false"
        return f"<closure λ{val.param}. …>"
    elif isinstance(val, bool):
        return 'true' if val else 'false'
    elif isinstance(val, int):
        return str(val)
    elif isinstance(val, str):
        return f"{val}"
    elif isinstance(val, Builtin):
        return "<builtin fn>"
    elif isinstance(val, Pair):
        # Print as (a b c)
        elems = []
        p = val
        while isinstance(p, Pair):
            elems.append(valueToString(p.head))
            p = p.tail
        if p is not nil:
            elems.append(".")
            elems.append(valueToString(p))
        return f"({' '.join(elems)})"
    elif val is nil:
        return "nil"
    else:
        return f"<unknown value: {val}>"
