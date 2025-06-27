from astmodule import Expr
from dataclasses import dataclass
from typing import Callable, Union

@dataclass
class Closure:
    param: str
    body: Expr
    env: dict[str, 'Value']

Value = Union[int, str, bool, Closure, 'Builtin']

@dataclass
class Builtin:
    func: Callable[[Value], Value]

def valueToString(val: Value) -> str:
    if isinstance(val, bool):
        return 'true' if val else 'false'
    elif isinstance(val, int):
        return str(val)
    elif isinstance(val, str):
        return f'"{val}"'
    elif isinstance(val, Closure):
        return f"<closure λ{val.param}. ...>"
    elif isinstance(val, Builtin):
        return "<builtin fn>"
    else:
        return f"<unknown value: {val}>"
