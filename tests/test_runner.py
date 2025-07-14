"""Comprehensive tests for the runner module."""

import pytest
from pathlib import Path
from lambdora.runner import run_file, load_std

def test_run_file_error_handling():
    """Test run_file error handling."""
    # Test with non-existent file
    with pytest.raises(FileNotFoundError):
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
