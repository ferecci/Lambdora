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
    RecursionInitError,
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


def test_format_lamb_error_with_cause():
    """Test format_lamb_error with error that has a cause."""
    from lambdora.errors import LambError
    
    # Create an error with a cause
    cause = ValueError("Original error")
    err = LambError("Test error", cause=cause)
    
    formatted = format_lamb_error(err)
    assert "Test error" in formatted
    assert "LambError" in formatted


def test_format_lamb_error_with_snippet_and_column():
    """Test format_lamb_error with snippet and column information."""
    err = LambError("Test error", snippet="(+ 1 2)", column=3)
    formatted = format_lamb_error(err)
    assert "Test error" in formatted
    assert "(+ 1 2)" in formatted
    assert "  ^" in formatted  # Caret should be at column 3


def test_format_lamb_error_with_snippet_column_zero():
    """Test format_lamb_error with snippet and column 0."""
    err = LambError("Test error", snippet="(+ 1 2)", column=0)
    formatted = format_lamb_error(err)
    assert "Test error" in formatted
    assert "(+ 1 2)" in formatted
    assert "^" in formatted  # Caret should be at start


def test_format_lamb_error_with_snippet_column_one():
    """Test format_lamb_error with snippet and column 1."""
    err = LambError("Test error", snippet="(+ 1 2)", column=1)
    formatted = format_lamb_error(err)
    assert "Test error" in formatted
    assert "(+ 1 2)" in formatted
    assert "^" in formatted  # Caret should be at start


def test_format_lamb_error_tokenize_unexpected_token():
    """Test format_lamb_error with TokenizeError containing 'unexpected token'."""
    err = TokenizeError("Unexpected token ')'", snippet="(+ 1 2))", column=7)
    formatted = format_lamb_error(err)
    assert "Unexpected token" in formatted
    assert "Check for unmatched parentheses" in formatted


def test_format_lamb_error_tokenize_unterminated_string():
    """Test format_lamb_error with TokenizeError containing 'unterminated string'."""
    err = TokenizeError("Unterminated string", snippet='"hello', column=6)
    formatted = format_lamb_error(err)
    assert "Unterminated string" in formatted
    assert "Make sure all strings are properly closed" in formatted


def test_format_lamb_error_parse_unexpected_eof():
    """Test format_lamb_error with ParseError containing 'unexpected eof'."""
    err = ParseError("Unexpected EOF", snippet="(define x 42", column=13)
    formatted = format_lamb_error(err)
    assert "Unexpected EOF" in formatted
    assert "Check for missing closing parentheses" in formatted


def test_format_lamb_error_parse_unbound_variable():
    """Test format_lamb_error with ParseError containing 'unbound variable'."""
    err = ParseError("Unbound variable x", snippet="(+ x 1)", column=3)
    formatted = format_lamb_error(err)
    assert "Unbound variable" in formatted
    assert "Make sure the variable is defined before use" in formatted


def test_format_lamb_error_eval_unbound_variable():
    """Test format_lamb_error with EvalError containing 'unbound variable'."""
    err = EvalError("Unbound variable x", snippet="(+ x 1)", column=3)
    formatted = format_lamb_error(err)
    assert "Unbound variable" in formatted
    assert "Use (define var value) to define variables" in formatted


def test_format_lamb_error_eval_lambda_syntax():
    """Test format_lamb_error with EvalError containing 'lambda syntax'."""
    err = EvalError("Lambda syntax error", snippet="(lambda x x)", column=8)
    formatted = format_lamb_error(err)
    assert "Lambda syntax error" in formatted
    assert "Lambda syntax is (lambda param . body)" in formatted


def test_format_lamb_error_no_traceback():
    """Test format_lamb_error with error that has no traceback."""
    err = LambError("Test error")
    # Remove traceback
    err.__traceback__ = None
    formatted = format_lamb_error(err)
    assert "Test error" in formatted
    assert "LambError" in formatted


def test_format_lamb_error_empty_traceback():
    """Test format_lamb_error with empty traceback."""
    err = LambError("Test error")
    # Create a mock traceback that's empty
    formatted = format_lamb_error(err)
    assert "Test error" in formatted
    assert "LambError" in formatted


def test_lamb_error_with_snippet_none():
    """Test LambError with snippet=None."""
    err = LambError("Test error", snippet=None)
    assert err.snippet is None
    assert str(err) == "Test error"


def test_lamb_error_with_snippet_with_newline():
    """Test LambError with snippet containing newline."""
    err = LambError("Test error", snippet="(+ 1\n2)")
    assert err.snippet == "(+ 1\n2)"  # Should not strip newlines from middle


def test_lamb_error_with_snippet_trailing_newlines():
    """Test LambError with snippet containing trailing newlines."""
    err = LambError("Test error", snippet="(+ 1 2)\n\n")
    assert err.snippet == "(+ 1 2)"  # Should strip trailing newlines


def test_lamb_error_location_with_file():
    """Test LambError location string with file."""
    err = LambError("Test error", file="test.lamb", line=5, column=10)
    assert "test.lamb:5:10" in str(err)


def test_lamb_error_location_without_file():
    """Test LambError location string without file."""
    err = LambError("Test error", line=5, column=10)
    assert "<unknown>:5:10" in str(err)


def test_lamb_error_location_without_line():
    """Test LambError location string without line."""
    err = LambError("Test error", file="test.lamb", column=10)
    assert str(err) == "Test error"


def test_lamb_error_location_without_column():
    """Test LambError location string without column."""
    err = LambError("Test error", file="test.lamb", line=5)
    assert str(err) == "Test error"


def test_lamb_error_location_both_none():
    """Test LambError location string with both line and column None."""
    err = LambError("Test error", file="test.lamb", line=None, column=None)
    assert str(err) == "Test error"


def test_recursion_init_error():
    """Test RecursionInitError creation."""
    err = RecursionInitError("Recursive binding not initialized")
    assert isinstance(err, RecursionInitError)
    assert isinstance(err, LambError)
    assert isinstance(err, RuntimeError)
    assert str(err) == "Recursive binding not initialized" 