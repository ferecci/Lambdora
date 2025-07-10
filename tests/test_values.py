from lambdora.values import Builtin, Closure, Pair, nil, valueToString


def test_value_to_string_nested_pair():
    p = Pair(1, Pair(2, Pair(3, nil)))
    assert valueToString(p) == "(1 2 3)"


def test_closure_repr():
    c = Closure("x", None, {})  # type: ignore[arg-type]
    assert valueToString(c).startswith("<closure lambda x.")


def test_builtin_repr():
    b = Builtin(lambda x: x)
    assert valueToString(b) == "<builtin fn>"


def test_bool_repr():
    assert valueToString(True) == "true"
    assert valueToString(False) == "false"


def test_int_repr():
    assert valueToString(123) == "123"


def test_str_repr():
    assert valueToString("yo") == "yo"


def test_nil_repr():
    assert valueToString(nil) == "nil"
    assert repr(nil) == "nil"


def test_pair_repr_simple():
    pair = Pair(1, Pair(2, Pair(3, nil)))
    assert valueToString(pair) == "(1 2 3)"


def test_pair_repr_dotted():
    pair = Pair(1, 2)
    assert valueToString(pair) == "(1 . 2)"


def test_unknown_repr():
    class Dummy:
        pass

    assert "<unknown value:" in valueToString(Dummy())  # type: ignore[arg-type]


def test_value_to_string_expr():
    """Ensure valueToString can print AST Expr values via lambPrint."""
    from lambdora.astmodule import Variable

    expr = Variable("x")
    assert valueToString(expr) == "x"
