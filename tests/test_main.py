"""Tests for the main CLI module."""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from lambdora.__main__ import main, create_parser


def test_create_parser():
    """Test parser creation."""
    parser = create_parser()
    assert parser.prog == "lambdora"
    assert parser.description is not None
    assert "minimalist Lisp-inspired" in parser.description


def test_parser_version():
    """Test version argument."""
    parser = create_parser()
    with patch('sys.argv', ['lambdora', '--version']):
        with pytest.raises(SystemExit) as exc:
            parser.parse_args()
        assert exc.value.code == 0


def test_parser_help():
    """Test help argument."""
    parser = create_parser()
    with patch('sys.argv', ['lambdora', '--help']):
        with pytest.raises(SystemExit) as exc:
            parser.parse_args()
        assert exc.value.code == 0


def test_main_no_args():
    """Test main with no arguments (shows help)."""
    with patch('sys.argv', ['lambdora']):
        with patch('lambdora.__main__.create_parser') as mock_parser:
            mock_parser_instance = MagicMock()
            mock_parser.return_value = mock_parser_instance
            mock_parser_instance.parse_args.return_value = MagicMock(command=None)
            
            result = main()
            assert result == 0
            mock_parser_instance.print_help.assert_called_once()


def test_main_repl_command():
    """Test main with repl command."""
    with patch('sys.argv', ['lambdora', 'repl']):
        with patch('lambdora.__main__.repl') as mock_repl:
            mock_parser = MagicMock()
            mock_args = MagicMock()
            mock_args.command = "repl"
            mock_args.stdlib_path = None
            mock_parser.parse_args.return_value = mock_args
            
            with patch('lambdora.__main__.create_parser', return_value=mock_parser):
                result = main()
                assert result == 0
                mock_repl.assert_called_once_with(stdlib_path=None)


def test_main_run_command_success():
    """Test main with run command and successful execution."""
    with patch('sys.argv', ['lambdora', 'run', 'test.lamb']):
        with patch('lambdora.__main__.run_file') as mock_run_file:
            with patch('pathlib.Path.exists', return_value=True):
                mock_parser = MagicMock()
                mock_args = MagicMock()
                mock_args.command = "run"
                mock_args.file = "test.lamb"
                mock_args.stdlib_path = None
                mock_parser.parse_args.return_value = mock_args
                
                with patch('lambdora.__main__.create_parser', return_value=mock_parser):
                    result = main()
                    assert result == 0
                    mock_run_file.assert_called_once()


def test_main_run_command_file_not_found():
    """Test main with run command when file doesn't exist."""
    with patch('sys.argv', ['lambdora', 'run', 'nonexistent.lamb']):
        with patch('pathlib.Path.exists', return_value=False):
            with patch('sys.stderr') as mock_stderr:
                mock_parser = MagicMock()
                mock_args = MagicMock()
                mock_args.command = "run"
                mock_args.file = "nonexistent.lamb"
                mock_args.stdlib_path = None
                mock_parser.parse_args.return_value = mock_args
                
                with patch('lambdora.__main__.create_parser', return_value=mock_parser):
                    result = main()
                    assert result == 1
                    mock_stderr.write.assert_called()


def test_main_run_command_wrong_extension():
    """Test main with run command when file has wrong extension."""
    with patch('sys.argv', ['lambdora', 'run', 'test.txt']):
        with patch('pathlib.Path.exists', return_value=True):
            with patch('sys.stderr') as mock_stderr:
                with patch('lambdora.__main__.run_file'):
                    mock_parser = MagicMock()
                    mock_args = MagicMock()
                    mock_args.command = "run"
                    mock_args.file = "test.txt"
                    mock_args.stdlib_path = None
                    mock_parser.parse_args.return_value = mock_args
                    
                    with patch('lambdora.__main__.create_parser', return_value=mock_parser):
                        result = main()
                        assert result == 0
                        mock_stderr.write.assert_called()


def test_main_keyboard_interrupt():
    """Test main with keyboard interrupt."""
    with patch('sys.argv', ['lambdora', 'repl']):
        with patch('lambdora.__main__.repl', side_effect=KeyboardInterrupt()):
            with patch('sys.stderr') as mock_stderr:
                mock_parser = MagicMock()
                mock_args = MagicMock()
                mock_args.command = "repl"
                mock_args.stdlib_path = None
                mock_parser.parse_args.return_value = mock_args
                
                with patch('lambdora.__main__.create_parser', return_value=mock_parser):
                    result = main()
                    assert result == 1
                    mock_stderr.write.assert_called()


def test_main_general_exception():
    """Test main with general exception."""
    with patch('sys.argv', ['lambdora', 'repl']):
        with patch('lambdora.__main__.repl', side_effect=Exception("Test error")):
            with patch('sys.stderr') as mock_stderr:
                mock_parser = MagicMock()
                mock_args = MagicMock()
                mock_args.command = "repl"
                mock_args.stdlib_path = None
                mock_parser.parse_args.return_value = mock_args
                
                with patch('lambdora.__main__.create_parser', return_value=mock_parser):
                    result = main()
                    assert result == 1
                    mock_stderr.write.assert_called()


def test_main_with_custom_args():
    """Test main with custom argument list."""
    with patch('lambdora.__main__.repl') as mock_repl:
        mock_parser = MagicMock()
        mock_args = MagicMock()
        mock_args.command = "repl"
        mock_args.stdlib_path = None
        mock_parser.parse_args.return_value = mock_args
        
        with patch('lambdora.__main__.create_parser', return_value=mock_parser):
            result = main(['lambdora', 'repl'])
            assert result == 0
            mock_repl.assert_called_once_with(stdlib_path=None)


def test_main_repl_with_stdlib_path():
    """Test main with repl command and custom stdlib path."""
    with patch('sys.argv', ['lambdora', 'repl', '--stdlib-path', '/custom/std.lamb']):
        with patch('lambdora.__main__.repl') as mock_repl:
            mock_parser = MagicMock()
            mock_args = MagicMock()
            mock_args.command = "repl"
            mock_args.stdlib_path = Path("/custom/std.lamb")
            mock_parser.parse_args.return_value = mock_args
            
            with patch('lambdora.__main__.create_parser', return_value=mock_parser):
                result = main()
                assert result == 0
                mock_repl.assert_called_once_with(stdlib_path=Path("/custom/std.lamb"))


def test_main_run_with_stdlib_path():
    """Test main with run command and custom stdlib path."""
    with patch('sys.argv', ['lambdora', 'run', 'test.lamb', '--stdlib-path', '/custom/std.lamb']):
        with patch('lambdora.__main__.run_file') as mock_run_file:
            with patch('pathlib.Path.exists', return_value=True):
                mock_parser = MagicMock()
                mock_args = MagicMock()
                mock_args.command = "run"
                mock_args.file = "test.lamb"
                mock_args.stdlib_path = Path("/custom/std.lamb")
                mock_parser.parse_args.return_value = mock_args
                
                with patch('lambdora.__main__.create_parser', return_value=mock_parser):
                    result = main()
                    assert result == 0
                    mock_run_file.assert_called_once_with(Path("test.lamb"), stdlib_path=Path("/custom/std.lamb")) 