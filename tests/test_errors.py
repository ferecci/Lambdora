"""Comprehensive tests for error handling."""

import pytest

from lambdora.errors import (
    BuiltinError,
    EvalError,
    LambError,
    MacroExpansionError,
    ParseError,
    TokenizeError,
    format_lamb_error,
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
    try:
        lambTokenize("@")
    except TokenizeError as err:
        formatted = format_lamb_error(err)
        assert "^" in formatted and "Unexpected character" in formatted
    else:
        pytest.fail("TokenizeError not raised")


def test_lamb_error_with_location():
    """Test LambError with location information."""
    err = LambError("msg", file="f.lamb", line=1, column=2)
    assert "f.lamb:1:2" in str(err)


def test_lamb_error_without_location():
    """Test LambError without location information."""
    err = LambError("msg")
    assert str(err) == "msg"


def test_tokenizer_unterminated_string():
    """Test tokenizer error for unterminated string."""
    with pytest.raises(TokenizeError):
        lambTokenize('"unterminated')


def test_tokenizer_unexpected_character():
    """Test tokenizer error for unexpected character."""
    with pytest.raises(TokenizeError):
        lambTokenize("unexpected_char_@")


def test_parser_incomplete_expression():
    """Test parser error for incomplete expression."""
    with pytest.raises(Exception):
        runExpression("(")  # Incomplete expression


def test_parser_missing_closing_paren():
    """Test parser error for missing closing parenthesis."""
    with pytest.raises(Exception):
        runExpression("(define x 42")  # Missing closing paren


def test_macro_wrong_argument_count():
    """Test macro expansion error for wrong argument count."""
    runExpression("(defmacro test_macro (x) x)")
    with pytest.raises(MacroExpansionError):
        runExpression("(test_macro 1 2)")  # Wrong number of arguments


def test_builtin_type_errors():
    """Test various builtin type errors."""
    # Test head on non-pair
    with pytest.raises(BuiltinError):
        runExpression("(head 42)")

    # Test tail on non-pair
    with pytest.raises(BuiltinError):
        runExpression("(tail 42)")

    # Test logical operations on non-booleans
    with pytest.raises(Exception):
        runExpression("(not 42)")

    with pytest.raises(Exception):
        runExpression("((and true) 42)")

    with pytest.raises(Exception):
        runExpression("((or false) 99)")


def test_evaluation_errors():
    """Test various evaluation errors."""
    # Test unbound variable
    with pytest.raises(EvalError):
        runExpression("undefined_var")

    # Test invalid function application
    with pytest.raises(Exception):
        runExpression("(42 1 2)")

    # Test unbound variable in complex expression
    with pytest.raises(Exception):
        runExpression("(+ undefined_var 1)")


def test_if_non_boolean_condition():
    """Test if with non-boolean condition."""
    with pytest.raises(Exception):
        runExpression("(if 42 1 2)")


def test_unquote_outside_quasiquote():
    """Test unquote outside quasiquote context."""
    with pytest.raises(Exception):
        runExpression("(unquote 42)")


def test_quote_wrong_arguments():
    """Test quote with wrong number of arguments."""
    with pytest.raises(Exception):
        runExpression("(quote)")


def test_quasiquote_wrong_arguments():
    """Test quasiquote with wrong number of arguments."""
    with pytest.raises(Exception):
        runExpression("(quasiquote)")


def test_lambda_syntax_error():
    """Test lambda with wrong number of arguments."""
    with pytest.raises(Exception):
        runExpression("(lambda x x)")  # Missing dot


def test_define_evaluated_name():
    """Test define with evaluated name."""
    with pytest.raises(Exception):
        runExpression("(define (+ 1 2) 5)")


def test_let_no_body():
    """Test let with no body."""
    with pytest.raises(Exception):
        runExpression("(let x 5)")


def test_defmacro_wrong_params():
    """Test defmacro with wrong parameter format."""
    with pytest.raises(Exception):
        runExpression("(defmacro m notalist x)")


def test_macroexpand_wrong_arg_count():
    """Test macro expansion with wrong argument count."""
    runExpression("(defmacro m (x y) x)")
    with pytest.raises(Exception):
        runExpression("(m 1)")  # Wrong number of arguments


def test_comprehensive_error_scenarios():
    """Test comprehensive error scenarios."""
    # Test multiple error types in sequence
    with pytest.raises(TokenizeError):
        lambTokenize("@")

    with pytest.raises(ParseError):
        runExpression("(lambda x x)")

    with pytest.raises(BuiltinError):
        runExpression("(head 42)")

    with pytest.raises(EvalError):
        runExpression("undefined_var")

    runExpression("(defmacro m (x) x)")
    with pytest.raises(MacroExpansionError):
        runExpression("(m 1 2)") 