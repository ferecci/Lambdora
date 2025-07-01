from lambdora.astmodule import Application, Literal, Variable
from lambdora.repl import run_expr as runExpression


def test_quote_literal():
    result = runExpression("'42")
    assert isinstance(result, Literal)
    assert result.value == "42"  # returned as string, unevaluated


def test_quote_expr():
    result = runExpression("'(+ 1 2)")
    assert isinstance(result, Application)
    assert isinstance(result.func, Variable)
    assert result.func.name == "+"


def test_quote_prevents_eval():
    result = runExpression("'(+ 1 2)")
    assert result != 3


def test_quasiquote_unquote():
    runExpression("(define x 99)")
    result = runExpression("(quasiquote (+ 1 (unquote x)))")
    assert isinstance(result, Application)
    assert result.func.name == "+"
    assert result.args[1] == 99
