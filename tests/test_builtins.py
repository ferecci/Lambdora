import pytest

from lambdora.repl import run_expr as runExpression


def test_not_type_error():
    with pytest.raises(TypeError):
        runExpression("(not 42)")


def test_and_type_error():
    with pytest.raises(TypeError):
        runExpression("((and true) 42)")


def test_or_type_error():
    with pytest.raises(TypeError):
        runExpression("((or false) 99)")


def test_division():
    """Test division builtin."""
    assert runExpression("(/ 10 2)") == 5
    assert runExpression("(/ 7 2)") == 3  # Integer division


def test_modulo():
    """Test modulo builtin."""
    assert runExpression("(% 10 3)") == 1
    assert runExpression("(% 8 4)") == 0


def test_less_than():
    """Test less-than comparison."""
    assert runExpression("(< 1 2)") is True
    assert runExpression("(< 2 1)") is False
    assert runExpression("(< 1 1)") is False


def test_equality():
    """Test equality comparison."""
    assert runExpression("(= 1 1)") is True
    assert runExpression("(= 1 2)") is False


def test_arithmetic_operators():
    """Test all arithmetic operators."""
    assert runExpression("(+ 3 4)") == 7
    assert runExpression("(- 5 3)") == 2
    assert runExpression("(* 3 4)") == 12


def test_head_tail_operations():
    """Test head and tail operations on pairs."""
    runExpression("(define pair (cons 1 2))")
    assert runExpression("(head pair)") == 1
    assert runExpression("(tail pair)") == 2


def test_isnil_predicate():
    """Test isNil predicate."""
    assert runExpression("(isNil nil)") is True
    assert runExpression("(isNil (cons 1 2))") is False


def test_print_function():
    """Test print function returns nil."""
    from lambdora.values import nil

    result = runExpression("(print 42)")
    assert result is nil


def test_gensym_function():
    """Test gensym function generates unique symbols."""
    sym1 = runExpression("(gensym)")
    sym2 = runExpression("(gensym)")
    assert isinstance(sym1, str)
    assert isinstance(sym2, str)
    assert sym1 != sym2
    assert sym1.startswith("__gensym_")
    assert sym2.startswith("__gensym_")
