"""Comprehensive tests for the REPL module."""

from unittest.mock import patch, MagicMock

import pytest

from lambdora.repl import print_help, repl, run_expr as runExpression, setup_readline, load_std, colored_prompt, print_error, print_result, print_goodbye, format_lamb_error
from lambdora.errors import TokenizeError
from lambdora.astmodule import QuasiQuoteExpr, Expr
from pathlib import Path
from readline import read_history_file, set_history_length, write_history_file
import os


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
        patch("builtins.input", side_effect=["(+ 1", "quit", "exit"]),
        patch("builtins.print") as mock_print,
    ):
        repl()
        assert any("multiline cancelled" in str(call) for call in mock_print.call_args_list)


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


def test_setup_readline_no_history_file():
    """Test setup_readline when history file doesn't exist."""
    with patch('os.path.dirname', return_value='/tmp'):
        with patch('readline.read_history_file', side_effect=FileNotFoundError()):
            # Should not raise an error
            setup_readline()


def test_setup_readline_no_readline_attributes():
    """Test setup_readline when readline attributes don't exist."""
    with patch('readline.read_history_file', side_effect=AttributeError()):
        with patch('readline.set_history_length', side_effect=AttributeError()):
            with patch('readline.write_history_file', side_effect=AttributeError()):
                # Should not raise an error
                setup_readline()


def test_colored_prompt():
    """Test colored_prompt function."""
    prompt = colored_prompt()
    assert "λ" in prompt
    assert ">" in prompt


def test_print_error():
    """Test print_error function."""
    with patch('builtins.print') as mock_print:
        print_error("Test error")
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0][0]
        assert "Error:" in call_args
        assert "Test error" in call_args


def test_print_result():
    """Test print_result function."""
    with patch('builtins.print') as mock_print:
        print_result("Test result")
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0][0]
        assert "=>" in call_args
        assert "Test result" in call_args


def test_print_goodbye():
    """Test print_goodbye function."""
    with patch('builtins.print') as mock_print:
        print_goodbye()
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0][0]
        assert "Goodbye" in call_args


def test_print_help():
    """Test print_help function."""
    with patch('builtins.print') as mock_print:
        print_help()
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0][0]
        assert "Available commands:" in call_args
        assert "exit, quit" in call_args
        assert "help" in call_args


def test_load_std_with_custom_path_not_found():
    """Test load_std with custom stdlib path that doesn't exist."""
    with patch('pathlib.Path.exists', return_value=False):
        with patch('builtins.print') as mock_print:
            load_std(Path("/nonexistent/std.lamb"))
            # Should print warning messages
            assert mock_print.call_count >= 2


def test_load_std_with_custom_path_exists():
    """Test load_std with custom stdlib path that exists."""
    with patch('pathlib.Path.exists', return_value=True):
        with patch('pathlib.Path.read_text', return_value="(define test 42)"):
            with patch('lambdora.repl.lambTokenize') as mock_tokenize:
                with patch('lambdora.repl.lambParseAll') as mock_parse:
                    with patch('lambdora.repl.lambMacroExpand') as mock_macro:
                        with patch('lambdora.repl.trampoline') as mock_trampoline:
                            mock_parse.return_value = [MagicMock()]
                            mock_macro.return_value = MagicMock()
                            load_std(Path("/custom/std.lamb"))
                            mock_tokenize.assert_called_once()
                            mock_parse.assert_called_once()


def test_load_std_with_lamb_error():
    """Test load_std with LambError during loading."""
    with patch('pathlib.Path.exists', return_value=True):
        with patch('pathlib.Path.read_text', return_value="invalid code"):
            with patch('lambdora.repl.lambTokenize', side_effect=TokenizeError("Test error")):
                with patch('builtins.print') as mock_print:
                    load_std()
                    # Should print error messages
                    assert mock_print.call_count >= 2


def test_run_expr_with_quasiquote():
    """Test run_expr with quasiquote expression."""
    with patch('lambdora.repl.lambTokenize') as mock_tokenize:
        with patch('lambdora.repl.lambParse') as mock_parse:
            with patch('lambdora.repl.evalQuasiquote') as mock_eval:
                mock_parse.return_value = QuasiQuoteExpr(MagicMock())
                mock_eval.return_value = "quasiquote result"
                result = runExpression("`(1 2 3)")
                assert result == "quasiquote result"
                mock_eval.assert_called_once()


def test_run_expr_with_macro_expansion_none():
    """Test run_expr when macro expansion returns None."""
    with patch('lambdora.repl.lambTokenize') as mock_tokenize:
        with patch('lambdora.repl.lambParse') as mock_parse:
            with patch('lambdora.repl.lambMacroExpand') as mock_macro:
                mock_parse.return_value = MagicMock()
                mock_macro.return_value = None
                result = runExpression("(defmacro m (x) x)")
                assert result == "<macro defined>"


def test_needs_more_unbalanced_parens():
    """Test _needs_more with unbalanced parentheses."""
    # This tests the inner function _needs_more
    with patch('builtins.input', return_value="exit"):
        with patch('builtins.print') as mock_print:
            # Mock the repl function to test _needs_more
            with patch('lambdora.repl.setup_readline'):
                with patch('lambdora.repl.load_std'):
                    with patch('lambdora.repl.colored_prompt', return_value="λ> "):
                        # Test with unbalanced parentheses
                        with patch('builtins.input', side_effect=["(define x 42", "exit"]):
                            repl()


def test_needs_more_with_backslash():
    """Test _needs_more with backslash continuation."""
    with patch('builtins.input', side_effect=["(+ 1 \\", "2)", "exit"]):
        with patch('builtins.print') as mock_print:
            with patch('lambdora.repl.setup_readline'):
                with patch('lambdora.repl.load_std'):
                    with patch('lambdora.repl.colored_prompt', return_value="λ> "):
                        with patch('lambdora.repl.run_expr') as mock_run:
                            mock_run.return_value = 3
                            repl()


def test_repl_multiline_cancel():
    """Test repl with multiline cancellation."""
    with patch('builtins.input', side_effect=["(define x", "exit"]):
        with patch('builtins.print') as mock_print:
            with patch('lambdora.repl.setup_readline'):
                with patch('lambdora.repl.load_std'):
                    with patch('lambdora.repl.colored_prompt', return_value="λ> "):
                        repl()
                        # Should print cancellation message
                        assert any("multiline cancelled" in str(call) for call in mock_print.call_args_list)


def test_repl_backslash_backspace():
    """Test repl with backslash backspace command."""
    with patch('builtins.input', side_effect=["(+ 1", "2", "\\b", "exit"]):
        with patch('builtins.print') as mock_print:
            with patch('lambdora.repl.setup_readline'):
                with patch('lambdora.repl.load_std'):
                    with patch('lambdora.repl.colored_prompt', return_value="λ> "):
                        with patch('lambdora.repl.run_expr') as mock_run:
                            mock_run.return_value = 3
                            repl()
    # Debug: print all the mock calls
    print("Mock print calls:")
    for call in mock_print.call_args_list:
        print(f"  {call}")
    # Check for the <removed: ...> message in any print call
    assert any("removed:" in str(call) for call in mock_print.call_args_list)


def test_repl_help_command():
    """Test repl with help command."""
    with patch('builtins.input', side_effect=["help", "exit"]):
        with patch('builtins.print') as mock_print:
            with patch('lambdora.repl.setup_readline'):
                with patch('lambdora.repl.load_std'):
                    with patch('lambdora.repl.colored_prompt', return_value="λ> "):
                        with patch('lambdora.repl.print_help') as mock_help:
                            repl()
                        mock_help.assert_called_once()


def test_repl_clear_command():
    """Test repl with clear command."""
    with patch('builtins.input', side_effect=["clear", "exit"]):
        with patch('builtins.print') as mock_print:
            with patch('lambdora.repl.setup_readline'):
                with patch('lambdora.repl.load_std'):
                    with patch('lambdora.repl.colored_prompt', return_value="λ> "):
                        with patch('os.system') as mock_system:
                            repl()
                            mock_system.assert_called_once()


def test_repl_with_expr_result():
    """Test repl with expression that returns a result."""
    with patch('builtins.input', side_effect=["(+ 1 2)", "exit"]):
        with patch('builtins.print') as mock_print:
            with patch('lambdora.repl.setup_readline'):
                with patch('lambdora.repl.load_std'):
                    with patch('lambdora.repl.colored_prompt', return_value="λ> "):
                        with patch('lambdora.repl.run_expr') as mock_run:
                            with patch('lambdora.repl.valueToString') as mock_to_string:
                                mock_run.return_value = 3
                                mock_to_string.return_value = "3"
                                repl()
                                mock_to_string.assert_called_once_with(3)


def test_repl_with_expr_object():
    """Test repl with expression that returns an Expr object."""
    class DummyExpr(Expr):
        pass
    with patch('builtins.input', side_effect=["(+ 1 2)", "exit"]):
        with patch('builtins.print') as mock_print:
            with patch('lambdora.repl.setup_readline'):
                with patch('lambdora.repl.load_std'):
                    with patch('lambdora.repl.colored_prompt', return_value="λ> "):
                        with patch('lambdora.repl.run_expr') as mock_run:
                            with patch('lambdora.repl.lambPrint') as mock_print_expr:
                                mock_run.return_value = DummyExpr()
                                mock_print_expr.return_value = "expr result"
                                repl()
                            mock_print_expr.assert_called_once()


def test_repl_with_lamb_error():
    """Test repl with LambError during evaluation."""
    with patch('builtins.input', side_effect=["invalid code", "exit"]):
        with patch('builtins.print') as mock_print:
            with patch('lambdora.repl.setup_readline'):
                with patch('lambdora.repl.load_std'):
                    with patch('lambdora.repl.colored_prompt', return_value="λ> "):
                        with patch('lambdora.repl.run_expr', side_effect=TokenizeError("Test error")):
                            with patch('lambdora.repl.format_lamb_error') as mock_format:
                                mock_format.return_value = "formatted error"
                                repl()
                                mock_format.assert_called_once()


def test_repl_with_general_exception():
    """Test repl with general exception during evaluation."""
    with patch('builtins.input', side_effect=["problematic code", "exit"]):
        with patch('builtins.print') as mock_print:
            with patch('lambdora.repl.setup_readline'):
                with patch('lambdora.repl.load_std'):
                    with patch('lambdora.repl.colored_prompt', return_value="λ> "):
                        with patch('lambdora.repl.run_expr', side_effect=RuntimeError("Test error")):
                            repl()
                        # Should print error message
                        assert any("RuntimeError" in str(call) for call in mock_print.call_args_list)


def test_repl_eof_error():
    """Test repl with EOFError."""
    with patch('builtins.input', side_effect=EOFError()):
        with patch('builtins.print') as mock_print:
            with patch('lambdora.repl.setup_readline'):
                with patch('lambdora.repl.load_std'):
                    with patch('lambdora.repl.colored_prompt', return_value="λ> "):
                        repl()
                        # Should print goodbye message
                        assert any("Goodbye" in str(call) for call in mock_print.call_args_list)


def test_repl_keyboard_interrupt():
    """Test repl with KeyboardInterrupt."""
    with patch('builtins.input', side_effect=KeyboardInterrupt()):
        with patch('builtins.print') as mock_print:
            with patch('lambdora.repl.setup_readline'):
                with patch('lambdora.repl.load_std'):
                    with patch('lambdora.repl.colored_prompt', return_value="λ> "):
                        repl()
                        # Should print goodbye message
                        assert any("Goodbye" in str(call) for call in mock_print.call_args_list)


def test_repl_unexpected_exception():
    """Test repl with unexpected exception."""
    with patch('builtins.input', side_effect=Exception("Unexpected")):
        with patch('builtins.print') as mock_print:
            with patch('lambdora.repl.setup_readline'):
                with patch('lambdora.repl.load_std'):
                    with patch('lambdora.repl.colored_prompt', return_value="λ> "):
                        repl()
                        # Should print error message
                        assert any("Unexpected error" in str(call) for call in mock_print.call_args_list)


def test_repl_with_custom_stdlib():
    """Test repl with custom stdlib path."""
    with patch('builtins.input', side_effect=["exit"]):
        with patch('builtins.print') as mock_print:
            with patch('lambdora.repl.setup_readline'):
                with patch('lambdora.repl.load_std'):
                    with patch('lambdora.repl.colored_prompt', return_value="λ> "):
                        repl(Path("/custom/std.lamb"))
                        # Should print custom stdlib message
                        assert any("custom stdlib" in str(call) for call in mock_print.call_args_list)


def test_main_function():
    """Test the legacy main function."""
    with patch('builtins.print') as mock_print:
        with patch('os.system') as mock_system:
            with patch('lambdora.repl.setup_readline'):
                with patch('lambdora.repl.repl'):
                    from lambdora.repl import main
                    main()
                    mock_print.assert_called_once()
                    mock_system.assert_called_once()
