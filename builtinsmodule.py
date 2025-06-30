"""Definitions of built-in functions and the initial environment."""

from typing import Dict
from values import Builtin, Value, Pair, nil, valueToString

def lambMakeTopEnv() -> dict[str, Value]:
    """Create the top-level environment with Lambdora built-ins."""
    env: Dict[str, Value] = {}
    
    # Boolean literals
    env['true']  = True
    env['false'] = False

    # Curried arithmetic operators
    def add(x: int) -> Value:
        return Builtin(lambda y: x + y)
    def sub(x: int) -> Value:
        return Builtin(lambda y: x - y)
    def mul(x: int) -> Value:
        return Builtin(lambda y: x * y)
    # Integer division (rounds down)
    def div(x: int) -> Value:
        return Builtin(lambda y: x // y)
    env['+'] = Builtin(add)
    env['-'] = Builtin(sub)
    env['*'] = Builtin(mul)
    env['/'] = Builtin(div)

    def mod(x: int) -> Value:
        return Builtin(lambda y: x % y)
    env['%'] = Builtin(mod)

    # Equality
    def eq(x: int) -> Value:
        return Builtin(lambda y: x == y)
    env['='] = Builtin(eq)

    # Less-than: the only inequality operator you need!
    def lt(x: int) -> Value:
        return Builtin(lambda y: x < y)
    env['<'] = Builtin(lt)

    # Negation
    def not_fn(x: bool) -> Value:
        if not isinstance(x, bool):
            raise TypeError("Expected boolean")
        return not x
    env['not'] = Builtin(not_fn)

    # Logical AND & OR
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
    env['and'] = Builtin(and_fn)
    env['or']  = Builtin(or_fn)

    # Printing (always prints the pretty-printed value, returns nil)
    def pr(x: Value) -> Value:
        print(valueToString(x))
        return nil
    env['print'] = Builtin(pr)

    # List ADT
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
    def is_nil(p: Value) -> bool:
        return p is nil
    env['cons']  = Builtin(cons)
    env['head']  = Builtin(head_fn)
    env['tail']  = Builtin(tail_fn)
    env['isNil'] = Builtin(is_nil)
    env['nil']   = nil

    return env
