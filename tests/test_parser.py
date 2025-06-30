from lambdora.tokenizer import lambTokenize
from lambdora.parser import lambParse
from lambdora.astmodule import *
import pytest
from lambdora.main import runExpression

def test_parse_lambda():
    tokens = lambTokenize("(λx. x)")
    expr = lambParse(tokens)
    assert isinstance(expr, Abstraction)
    assert expr.param == 'x'
    assert isinstance(expr.body, Variable)

def test_unclosed_if():
    with pytest.raises(SyntaxError):
        runExpression("(if true 1 2")

def test_lambda_missing_dot():
    with pytest.raises(SyntaxError):
        runExpression("(λx x)")

def test_lambda_missing_closing_paren():
    with pytest.raises(SyntaxError):
        runExpression("(λx. x")

def test_malformed_define():
    with pytest.raises(SyntaxError):
        runExpression("(define x)")

def test_incomplete_if():
    with pytest.raises(SyntaxError):
        runExpression("(if true 1)")

def test_defmacro_missing_parens():
    with pytest.raises(SyntaxError):
        runExpression("(defmacro m x x)")

def test_lambda_requires_dot():
    with pytest.raises(SyntaxError):
        runExpression("(λx x)")