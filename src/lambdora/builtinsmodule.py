"""Built-in functions and the initial environment."""

from itertools import count
from typing import Dict, cast

from .errors import BuiltinError as TypeError
from .values import Builtin, Pair, Value, nil, valueToString


# Helper to differentiate ints from bools (bool is a subclass of int in Python)
def _is_int(val: Value) -> bool:
    return isinstance(val, int) and not isinstance(val, bool)


# Convert Value to int after validation
def _to_int(val: Value) -> int:
    if not _is_int(val):
        raise TypeError("Expected integer")
    return cast(int, val)


def lambMakeTopEnv() -> dict[str, Value]:
    """Create the top-level environment with Lambdora built-ins."""
    env: Dict[str, Value] = {}

    # Booleans
    env["true"] = True
    env["false"] = False

    # Arithmetic (curried)
    def add(x: Value) -> Value:
        xi = _to_int(x)

        def add_inner(y: Value) -> Value:
            yi = _to_int(y)
            return xi + yi

        return Builtin(add_inner)

    def sub(x: Value) -> Value:
        xi = _to_int(x)

        def sub_inner(y: Value) -> Value:
            yi = _to_int(y)
            return xi - yi

        return Builtin(sub_inner)

    def mul(x: Value) -> Value:
        xi = _to_int(x)

        def mul_inner(y: Value) -> Value:
            yi = _to_int(y)
            return xi * yi

        return Builtin(mul_inner)

    # Integer division (floored)
    def div(x: Value) -> Value:
        xi = _to_int(x)

        def div_inner(y: Value) -> Value:
            yi = _to_int(y)
            return xi // yi

        return Builtin(div_inner)

    env["+"] = Builtin(add)
    env["-"] = Builtin(sub)
    env["*"] = Builtin(mul)
    env["/"] = Builtin(div)

    def mod(x: Value) -> Value:
        xi = _to_int(x)

        def mod_inner(y: Value) -> Value:
            yi = _to_int(y)
            return xi % yi

        return Builtin(mod_inner)

    env["%"] = Builtin(mod)
    env["mod"] = Builtin(mod)  # Alias for consistency

    # Additional comparison operators
    def le(x: Value) -> Value:
        xi = _to_int(x)

        def le_inner(y: Value) -> Value:
            yi = _to_int(y)
            return xi <= yi

        return Builtin(le_inner)

    def gt(x: Value) -> Value:
        xi = _to_int(x)

        def gt_inner(y: Value) -> Value:
            yi = _to_int(y)
            return xi > yi

        return Builtin(gt_inner)

    def ge(x: Value) -> Value:
        xi = _to_int(x)

        def ge_inner(y: Value) -> Value:
            yi = _to_int(y)
            return xi >= yi

        return Builtin(ge_inner)

    def ne(x: Value) -> Value:
        xi = _to_int(x)

        def ne_inner(y: Value) -> Value:
            yi = _to_int(y)
            return xi != yi

        return Builtin(ne_inner)

    env["<="] = Builtin(le)
    env[">"] = Builtin(gt)
    env[">="] = Builtin(ge)
    env["!="] = Builtin(ne)

    # String conversion
    def str_fn(x: Value) -> Value:
        return valueToString(x)

    # String concatenation
    def concat(x: Value) -> Value:
        if not isinstance(x, str):
            raise TypeError("Expected string")

        def concat_inner(y: Value) -> Value:
            if not isinstance(y, str):
                raise TypeError("Expected string")
            return x + y

        return Builtin(concat_inner)

    env["str"] = Builtin(str_fn)
    env["++"] = Builtin(concat)  # String concatenation operator

    # Type checking functions
    def is_number(x: Value) -> Value:
        return _is_int(x)

    def is_boolean(x: Value) -> Value:
        return isinstance(x, bool)

    def is_string(x: Value) -> Value:
        return isinstance(x, str)

    def is_list(x: Value) -> Value:
        return isinstance(x, Pair) or x is nil

    def is_function(x: Value) -> Value:
        return isinstance(x, Builtin)

    env["isNumber"] = Builtin(is_number)
    env["isBoolean"] = Builtin(is_boolean)
    env["isString"] = Builtin(is_string)
    env["isList"] = Builtin(is_list)
    env["isFunction"] = Builtin(is_function)

    # Equality
    def eq(x: Value) -> Value:
        xi = _to_int(x)

        def eq_inner(y: Value) -> Value:
            yi = _to_int(y)
            return xi == yi

        return Builtin(eq_inner)

    env["="] = Builtin(eq)

    # Less-than
    def lt(x: Value) -> Value:
        xi = _to_int(x)

        def lt_inner(y: Value) -> Value:
            yi = _to_int(y)
            return xi < yi

        return Builtin(lt_inner)

    env["<"] = Builtin(lt)

    # Logical negation
    def not_fn(x: Value) -> Value:
        if not isinstance(x, bool):
            raise TypeError("Expected boolean")
        return not x

    env["not"] = Builtin(not_fn)

    # Conjunction / disjunction
    def and_fn(x: Value) -> Value:
        if not isinstance(x, bool):
            raise TypeError("Expected boolean")

        def inner(y: Value) -> Value:
            if not isinstance(y, bool):
                raise TypeError("Expected boolean")
            return x and y

        return Builtin(inner)

    def or_fn(x: Value) -> Value:
        if not isinstance(x, bool):
            raise TypeError("Expected boolean")

        def inner(y: Value) -> Value:
            if not isinstance(y, bool):
                raise TypeError("Expected boolean")
            return x or y

        return Builtin(inner)

    env["and"] = Builtin(and_fn)
    env["or"] = Builtin(or_fn)

    # Printing (returns nil)
    def pr(x: Value) -> Value:
        print(valueToString(x))
        return nil

    env["print"] = Builtin(pr)

    # Lists
    def cons(x: Value) -> Value:
        return Builtin(lambda y: Pair(x, y))

    def head_fn(p: Value) -> Value:
        if not isinstance(p, Pair):
            raise TypeError("head expects a pair")
        return p.head

    def tail_fn(p: Value) -> Value:
        if not isinstance(p, Pair):
            raise TypeError("tail expects a pair")
        return p.tail

    def is_nil(p: Value) -> Value:
        return p is nil

    env["cons"] = Builtin(cons)
    env["head"] = Builtin(head_fn)
    env["tail"] = Builtin(tail_fn)
    env["isNil"] = Builtin(is_nil)
    env["nil"] = nil

    # Gensym for hygienic macros
    _gensym_counter = count()

    def gensym_fn(x: Value) -> Value:
        return f"__gensym_{next(_gensym_counter)}"

    env["gensym"] = Builtin(gensym_fn)

    return env
