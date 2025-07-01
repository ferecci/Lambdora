"""Tests for lambdora.repl module."""

from pathlib import Path
from unittest.mock import patch

from lambdora.repl import load_std, run_expr


def test_run_expr_basic():
    """Test basic run_expr functionality."""
    result = run_expr("(+ 1 2)")
    assert result == 3


def test_run_expr_macro_defined():
    """Test run_expr with macro definition."""
    result = run_expr("(defmacro test (x) x)")
    assert result == "<macro defined>"


def test_load_std():
    """Test load_std function."""
    # This should load without error
    load_std()


def test_load_std_missing_file():
    """Test load_std when std.lamb doesn't exist."""
    # Mock the Path.exists() to return False
    with patch.object(Path, "exists", return_value=False):
        # Should not raise an error, just return early
        load_std()


def test_load_std_with_content():
    """Test load_std with actual standard library content."""
    # Create a temporary std.lamb file with test content
    # (use underscore instead of hyphen)
    test_content = "(define testvar 42)"

    # Mock the file reading
    with patch.object(Path, "exists", return_value=True):
        with patch.object(Path, "read_text", return_value=test_content):
            load_std()
            # After loading, the variable should be available
            result = run_expr("testvar")
            assert result == 42


def test_repl_exit_commands():
    """Test that exit and quit commands work in repl."""
    from lambdora.repl import repl

    # Mock input to return "exit"
    with patch("builtins.input", return_value="exit"):
        with patch("builtins.print") as mock_print:
            repl()
            # Should print "Goodbye." when exiting
            mock_print.assert_called_with("Goodbye.")


def test_repl_quit_command():
    """Test quit command in repl."""
    from lambdora.repl import repl

    # Mock input to return "quit"
    with patch("builtins.input", return_value="quit"):
        with patch("builtins.print") as mock_print:
            repl()
            mock_print.assert_called_with("Goodbye.")


def test_repl_keyboard_interrupt():
    """Test keyboard interrupt handling in repl."""
    from lambdora.repl import repl

    # Mock input to raise KeyboardInterrupt
    with patch("builtins.input", side_effect=KeyboardInterrupt):
        with patch("builtins.print") as mock_print:
            repl()
            mock_print.assert_called_with("\nGoodbye.")


def test_repl_eof_error():
    """Test EOF error handling in repl."""
    from lambdora.repl import repl

    # Mock input to raise EOFError
    with patch("builtins.input", side_effect=EOFError):
        with patch("builtins.print") as mock_print:
            repl()
            mock_print.assert_called_with("\nGoodbye.")


def test_repl_expression_error():
    """Test error handling in repl for bad expressions."""
    from lambdora.repl import repl

    # Mock input sequence: bad expression, then exit
    inputs = ["(bad syntax", "exit"]
    with patch("builtins.input", side_effect=inputs):
        with patch("builtins.print") as mock_print:
            repl()
            # Should print error message and then goodbye
            calls = mock_print.call_args_list
            assert any("Error:" in str(call) for call in calls)
            assert any("Goodbye." in str(call) for call in calls)


def test_repl_expression_output():
    """Test repl printing expression results."""
    from lambdora.repl import repl

    # Mock input sequence: expression that returns non-nil, then exit
    inputs = ["(+ 1 2)", "exit"]
    with patch("builtins.input", side_effect=inputs):
        with patch("builtins.print") as mock_print:
            repl()
            # Should print the result "=> 3"
            calls = mock_print.call_args_list
            assert any("=>" in str(call) and "3" in str(call) for call in calls)
            assert any("Goodbye." in str(call) for call in calls)


def test_repl_nil_result():
    """Test that nil results are not printed in repl."""
    from lambdora.repl import repl

    # Mock input sequence: expression that returns nil, then exit
    inputs = ["(print 42)", "exit"]  # print returns nil
    with patch("builtins.input", side_effect=inputs):
        with patch("builtins.print") as mock_print:
            repl()
            # Should print "42" from the print function and "Goodbye." but not "=> nil"
            calls = mock_print.call_args_list
            assert any("42" in str(call) for call in calls)
            assert any("Goodbye." in str(call) for call in calls)
            # Should not have "=>" with nil
            assert not any("=>" in str(call) and "nil" in str(call) for call in calls)
