import pytest

from lambdora.errors import (
    BuiltinError,
    EvalError,
    LambError,
    MacroExpansionError,
    ParseError,
    TokenizeError,
)
from lambdora.repl import run_expr as runExpression
from lambdora.tokenizer import lambTokenize


def test_tokenize_error():
    """Unexpected characters should raise TokenizeError with location info."""
    with pytest.raises(TokenizeError) as exc:
        lambTokenize("@")

    err: LambError = exc.value  # type: ignore[assignment]
    assert err.line == 1
    assert err.column == 1
    assert err.snippet is not None


def test_parse_error():
    """Broken syntax should produce ParseError via the high-level API."""
    with pytest.raises(ParseError):
        runExpression("(lambda x x)")


def test_macro_expansion_error():
    """Arity mismatches when calling a macro must raise MacroExpansionError."""
    # Define a simple one-arg macro first
    runExpression("(defmacro m (x) x)")
    # Call with the wrong number of arguments
    with pytest.raises(MacroExpansionError):
        runExpression("(m)")


def test_builtin_error():
    """Incorrect usage of built-ins (e.g. head on int) raises BuiltinError."""
    with pytest.raises(BuiltinError):
        runExpression("(head 42)")


def test_eval_error():
    """Unbound variables should raise EvalError that still subclasses NameError."""
    with pytest.raises(EvalError):
        runExpression("unknown_var")


def test_builtin_add_type_error():
    """Passing non-ints to + should raise BuiltinError."""
    with pytest.raises(BuiltinError):
        runExpression("(+ true 1)")


def test_format_lamb_error_snippet():
    """format_lamb_error should include caret under column in message."""
    from lambdora.errors import format_lamb_error

    try:
        lambTokenize("@")
    except TokenizeError as err:
        formatted = format_lamb_error(err)
        assert "^" in formatted and "Unexpected character" in formatted
    else:
        pytest.fail("TokenizeError not raised")
