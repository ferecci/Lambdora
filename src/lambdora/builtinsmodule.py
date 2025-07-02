"""Built-in functions and the initial environment."""

from itertools import count
from typing import Dict

from .values import Builtin, Pair, Value, nil, valueToString


def lambMakeTopEnv() -> dict[str, Value]:
    """Create the top-level environment with Lambdora built-ins."""
    env: Dict[str, Value] = {}

    # Booleans
    env["true"] = True
    env["false"] = False

    # Arithmetic (curried)
    def add(x: Value) -> Value:
        if not isinstance(x, int):
            raise TypeError("Expected integer")

        def add_inner(y: Value) -> Value:
            if not isinstance(y, int):
                raise TypeError("Expected integer")
            return x + y

        return Builtin(add_inner)

    def sub(x: Value) -> Value:
        if not isinstance(x, int):
            raise TypeError("Expected integer")

        def sub_inner(y: Value) -> Value:
            if not isinstance(y, int):
                raise TypeError("Expected integer")
            return x - y

        return Builtin(sub_inner)

    def mul(x: Value) -> Value:
        if not isinstance(x, int):
            raise TypeError("Expected integer")

        def mul_inner(y: Value) -> Value:
            if not isinstance(y, int):
                raise TypeError("Expected integer")
            return x * y

        return Builtin(mul_inner)

    # Integer division (floored)
    def div(x: Value) -> Value:
        if not isinstance(x, int):
            raise TypeError("Expected integer")

        def div_inner(y: Value) -> Value:
            if not isinstance(y, int):
                raise TypeError("Expected integer")
            return x // y

        return Builtin(div_inner)

    env["+"] = Builtin(add)
    env["-"] = Builtin(sub)
    env["*"] = Builtin(mul)
    env["/"] = Builtin(div)

    def mod(x: Value) -> Value:
        if not isinstance(x, int):
            raise TypeError("Expected integer")

        def mod_inner(y: Value) -> Value:
            if not isinstance(y, int):
                raise TypeError("Expected integer")
            return x % y

        return Builtin(mod_inner)

    env["%"] = Builtin(mod)

    # Equality
    def eq(x: Value) -> Value:
        if not isinstance(x, int):
            raise TypeError("Expected integer")
        return Builtin(lambda y: x == y)

    env["="] = Builtin(eq)

    # Less-than
    def lt(x: Value) -> Value:
        if not isinstance(x, int):
            raise TypeError("Expected integer")

        def lt_inner(y: Value) -> Value:
            if not isinstance(y, int):
                raise TypeError("Expected integer")
            return x < y

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
