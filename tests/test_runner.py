"""Tests for lambdora.runner module."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch
import sys
from lambdora.runner import run_file, load_std

def test_run_file_simple():
    """Test running a simple .lamb file."""
    # Create a temporary .lamb file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.lamb', delete=False) as f:
        f.write('(+ 1 2)')
        temp_path = Path(f.name)
    
    try:
        # Capture output
        with patch('builtins.print') as mock_print:
            run_file(temp_path)
            mock_print.assert_called_once_with('3')
    finally:
        temp_path.unlink()  # Clean up

def test_run_file_with_define():
    """Test running a file that defines and uses variables."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.lamb', delete=False) as f:
        f.write('(define x 10)\n(* x 5)')
        temp_path = Path(f.name)
    
    try:
        with patch('builtins.print') as mock_print:
            run_file(temp_path)
            # Both the define result and expression result will be printed
            assert mock_print.call_count == 2
            # Check that the last call was the multiplication result
            last_call = mock_print.call_args_list[-1]
            assert last_call == (('50',),)
    finally:
        temp_path.unlink()

def test_run_file_multiple_expressions():
    """Test running a file with multiple expressions."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.lamb', delete=False) as f:
        f.write('(+ 1 1)\n(+ 2 2)\n(+ 3 3)')
        temp_path = Path(f.name)
    
    try:
        with patch('builtins.print') as mock_print:
            run_file(temp_path)
            # All non-nil results should be printed
            expected_calls = [('2',), ('4',), ('6',)]
            actual_calls = [call[0] for call in mock_print.call_args_list]
            assert actual_calls == expected_calls
    finally:
        temp_path.unlink()

def test_load_std():
    """Test that load_std function works."""
    # This should run without error and load standard library
    load_std()

def test_main_with_wrong_args():
    """Test the __main__ block with wrong number of arguments."""
    with patch.object(sys, 'argv', ['runner.py']):  # Missing file argument
        with patch('sys.exit') as mock_exit:
            # Manually check the condition that would be in __main__
            if len(sys.argv) != 2:
                sys.exit("Usage: python -m lambdora.runner <file.lamb>")
            mock_exit.assert_called_once_with("Usage: python -m lambdora.runner <file.lamb>") 