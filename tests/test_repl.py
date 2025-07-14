"""Comprehensive tests for the REPL module."""

from unittest.mock import patch

import pytest

from lambdora.repl import print_help, repl, run_expr as runExpression


def test_basic_repl_functionality():
    """Test basic REPL functionality."""
    # Test run_expr with macro definition
    result = runExpression("(defmacro test_macro (x) x)")
    assert result == "<macro defined>"


def test_repl_multiline_input():
    """Test REPL with multiline input."""
    with (
        patch("builtins.input", side_effect=["(+ 1", "2)", "exit"]),
        patch("builtins.print") as mock_print,
    ):
        repl()
        assert any("3" in str(call) for call in mock_print.call_args_list)


def test_repl_continuation():
    """Test REPL with continuation."""
    with (
        patch("builtins.input", side_effect=["(+ 1 \\", "2)", "exit"]),
        patch("builtins.print") as mock_print,
    ):
        repl()
        assert any("3" in str(call) for call in mock_print.call_args_list)


def test_repl_backspace():
    """Test REPL with backspace."""
    with (
        patch("builtins.input", side_effect=["(+ 1 2)", "\\b", "exit"]),
        patch("builtins.print") as mock_print,
    ):
        repl()


def test_repl_quit_during_multiline():
    """Test REPL with quit during multiline."""
    with (
        patch("builtins.input", side_effect=["(+ 1", "quit"]),
        patch("builtins.print") as mock_print,
    ):
        repl()
        assert any("Goodbye" in str(call) for call in mock_print.call_args_list)


def test_repl_exit_immediately():
    """Test REPL exit immediately."""
    with (
        patch("builtins.input", side_effect=["exit"]),
        patch("builtins.print") as mock_print,
    ):
        repl()
        assert any("Goodbye" in str(call) for call in mock_print.call_args_list)


def test_repl_empty_input():
    """Test REPL with empty input."""
    with (
        patch("builtins.input", side_effect=["", "exit"]),
        patch("builtins.print") as mock_print,
    ):
        repl()


def test_repl_multiline_continuation():
    """Test REPL with multiline continuation."""
    with (
        patch("builtins.input", side_effect=["(+ 1", "2)", "exit"]),
        patch("builtins.print") as mock_print,
    ):
        repl()
        assert any("3" in str(call) for call in mock_print.call_args_list)


def test_repl_backslash_continuation():
    """Test REPL with backslash continuation."""
    with (
        patch("builtins.input", side_effect=["(+ 1 \\", "2)", "exit"]),
        patch("builtins.print") as mock_print,
    ):
        repl()
        assert any("3" in str(call) for call in mock_print.call_args_list)


def test_repl_backspace_handling():
    """Test REPL backspace handling."""
    with (
        patch("builtins.input", side_effect=["(+ 1 2)", "\\b", "exit"]),
        patch("builtins.print") as mock_print,
    ):
        repl()


def test_print_help():
    """Test print_help function."""
    print_help()


def test_load_std_missing_file():
    """Test load_std with missing file."""
    with patch("pathlib.Path.exists", return_value=False):
        from lambdora.repl import load_std

        load_std()  # Should not raise error


def test_repl_with_complex_expressions():
    """Test REPL with complex expressions."""
    # Test factorial
    factorial_code = """
    (letrec ((factorial (lambda n. 
                         (if (<= n 1) 
                             1 
                             (* n (factorial (- n 1)))))))
      (factorial 5))
    """
    result = runExpression(factorial_code)
    assert result == 120

    # Test with macros and quasiquotes
    runExpression("(defmacro double (x) `(+ ,x ,x))")
    result = runExpression("(double 5)")
    assert result == 10


def test_repl_error_handling():
    """Test REPL error handling."""
    # Test with syntax errors
    with pytest.raises(Exception):
        runExpression("(")  # Incomplete expression

    # Test with undefined variables
    with pytest.raises(Exception):
        runExpression("undefined_var")

    # Test with macro expansion errors
    runExpression("(defmacro test_macro (x) x)")
    with pytest.raises(Exception):
        runExpression("(test_macro 1 2)")  # Wrong number of arguments
