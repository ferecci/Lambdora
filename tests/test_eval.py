from main import runExpression
import pytest

def test_simple_add():
    assert runExpression("(+ 1 2)") == 3

def test_if_expr():
    assert runExpression("(if true 1 2)") == 1
    assert runExpression("(if false 1 2)") == 2
    
def test_unbound_variable():
    with pytest.raises(NameError):
        runExpression("x")

def test_type_error_on_if():
    with pytest.raises(TypeError):
        runExpression("(if 42 1 2)")

def test_applying_non_function():
    with pytest.raises(TypeError):
        runExpression("(42 1)")

def test_bad_lambda_syntax():
    with pytest.raises(SyntaxError):
        runExpression("(λx x)")

def test_incomplete_expression():
    with pytest.raises(SyntaxError):
        runExpression("(+ 1")
