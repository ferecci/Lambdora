"""Comprehensive tests for the runner module."""

import pytest
from pathlib import Path
from lambdora.runner import run_file, load_std
from lambdora.errors import TokenizeError
from unittest.mock import patch

def test_run_file_error_handling():
    """Test run_file error handling."""
    # Test with non-existent file
    with pytest.raises(SystemExit):
        run_file(Path("nonexistent_file.lamb"))

def test_runner_import():
    """Test that runner module can be imported and functions exist."""
    assert callable(run_file)
    assert callable(load_std)

def test_load_std_basic():
    """Test basic load_std functionality."""
    # Should not raise an error
    load_std()

# Additional tests for missing coverage

def test_runner_error_conditions():
    """Test runner error conditions."""
    # Test runner with empty file
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(mode='w', suffix='.lamb', delete=False) as f:
        f.write("")
        f.flush()
        try:
            result = run_file(Path(f.name))
            assert result is None
        finally:
            os.unlink(f.name)

def test_runner_with_valid_file():
    """Test runner with valid file."""
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(mode='w', suffix='.lamb', delete=False) as f:
        f.write("(+ 1 2)")
        f.flush()
        try:
            result = run_file(Path(f.name))
            assert result is None  # run_file returns None but prints the result
        finally:
            os.unlink(f.name)

def test_runner_with_multiple_expressions():
    """Test runner with multiple expressions in file."""
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(mode='w', suffix='.lamb', delete=False) as f:
        f.write("(define x 42)\n(+ x 1)")
        f.flush()
        try:
            result = run_file(Path(f.name))
            assert result is None  # run_file returns None but prints the result
        finally:
            os.unlink(f.name)

def test_runner_with_comments():
    """Test runner with comments in file."""
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(mode='w', suffix='.lamb', delete=False) as f:
        f.write("; This is a comment\n(+ 1 2)")
        f.flush()
        try:
            result = run_file(Path(f.name))
            assert result is None  # run_file returns None but prints the result
        finally:
            os.unlink(f.name)

def test_runner_with_whitespace():
    """Test runner with whitespace in file."""
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(mode='w', suffix='.lamb', delete=False) as f:
        f.write("  \n  (+ 1 2)  \n  ")
        f.flush()
        try:
            result = run_file(Path(f.name))
            assert result is None  # run_file returns None but prints the result
        finally:
            os.unlink(f.name)

def test_runner_with_unicode_decode_error():
    """Test runner with UnicodeDecodeError."""
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.lamb', delete=False) as f:
        f.write(b'\xff\xfe\x00')  # Invalid UTF-8
        f.flush()
        try:
            with pytest.raises(SystemExit):
                run_file(Path(f.name))
        finally:
            os.unlink(f.name)


def test_runner_with_os_error():
    """Test runner with OSError."""
    with pytest.raises(SystemExit):
        run_file(Path("/nonexistent/path/file.lamb"))


def test_load_std_with_custom_path_not_found():
    """Test load_std with custom stdlib path that doesn't exist."""
    import tempfile
    import os
    with tempfile.TemporaryDirectory() as temp_dir:
        custom_std = Path(temp_dir) / "nonexistent.lamb"
        # Should not raise an error, should fall back to built-in
        load_std(custom_std)


def test_load_std_with_custom_path_exists():
    """Test load_std with custom stdlib path that exists."""
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(mode='w', suffix='.lamb', delete=False) as f:
        f.write("(define test-var 42)")
        f.flush()
        try:
            # Should not raise an error
            load_std(Path(f.name))
        finally:
            os.unlink(f.name)


def test_load_std_with_builtin_not_found():
    """Test load_std when built-in stdlib doesn't exist."""
    # This is a bit tricky to test, but we can mock the path
    with patch('pathlib.Path.exists', return_value=False):
        # Should not raise an error
        load_std()


def test_run_file_with_lamb_error():
    """Test run_file with LambError."""
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(mode='w', suffix='.lamb', delete=False) as f:
        f.write("(undefined-function 1 2 3)")
        f.flush()
        try:
            with pytest.raises(SystemExit):
                run_file(Path(f.name))
        finally:
            os.unlink(f.name)


def test_run_file_with_unexpected_exception():
    """Test run_file with unexpected exception."""
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(mode='w', suffix='.lamb', delete=False) as f:
        f.write("(+ 1 2)")
        f.flush()
        try:
            # Mock lambTokenize to raise an unexpected exception
            with patch('lambdora.runner.lambTokenize', side_effect=RuntimeError("Unexpected")):
                with pytest.raises(SystemExit):
                    run_file(Path(f.name))
        finally:
            os.unlink(f.name)


def test_run_file_with_macro_expansion_none():
    """Test run_file when macro expansion returns None."""
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(mode='w', suffix='.lamb', delete=False) as f:
        f.write("(define x 42)")
        f.flush()
        try:
            # Mock lambMacroExpand to return None
            with patch('lambdora.runner.lambMacroExpand', return_value=None):
                result = run_file(Path(f.name))
                assert result is None
        finally:
            os.unlink(f.name)


def test_run_file_with_output():
    """Test run_file with output that should be printed."""
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(mode='w', suffix='.lamb', delete=False) as f:
        f.write("(+ 1 2)")
        f.flush()
        try:
            with patch('builtins.print') as mock_print:
                result = run_file(Path(f.name))
                assert result is None
                mock_print.assert_called_once()
        finally:
            os.unlink(f.name)


def test_run_file_with_nil_output():
    """Test run_file with nil output (should not print)."""
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(mode='w', suffix='.lamb', delete=False) as f:
        f.write("(define x 42)")
        f.flush()
        try:
            with patch('builtins.print') as mock_print:
                result = run_file(Path(f.name))
                assert result is None
                mock_print.assert_not_called()
        finally:
            os.unlink(f.name)


def test_runner_main_function():
    """Test the legacy main function."""
    with patch('sys.argv', ['runner.py', 'test.lamb']):
        with patch('lambdora.runner.run_file') as mock_run_file:
            from lambdora.runner import main
            main()
            mock_run_file.assert_called_once()


def test_runner_main_function_wrong_args():
    """Test the legacy main function with wrong number of arguments."""
    with patch('sys.argv', ['runner.py']):
        with patch('sys.stderr') as mock_stderr:
            with pytest.raises(SystemExit):
                from lambdora.runner import main
                main()
            mock_stderr.write.assert_called()


def test_runner_main_function_too_many_args():
    """Test the legacy main function with too many arguments."""
    with patch('sys.argv', ['runner.py', 'file1.lamb', 'file2.lamb']):
        with patch('sys.stderr') as mock_stderr:
            with pytest.raises(SystemExit):
                from lambdora.runner import main
                main()
            mock_stderr.write.assert_called()


def test_load_std_with_lamb_error():
    """Test load_std with LambError during loading."""
    # Mock lambTokenize to raise a LambError
    with patch('lambdora.runner.lambTokenize', side_effect=TokenizeError("Test error")):
        with pytest.raises(SystemExit):
            load_std()


def test_run_file_with_multiple_expressions_output():
    """Test run_file with multiple expressions that produce output."""
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(mode='w', suffix='.lamb', delete=False) as f:
        f.write("(+ 1 2)\n(+ 3 4)")
        f.flush()
        try:
            with patch('builtins.print') as mock_print:
                result = run_file(Path(f.name))
                assert result is None
                assert mock_print.call_count == 2
        finally:
            os.unlink(f.name)
