import subprocess
import sys
from unittest.mock import patch

# Test runner.py CLI using subprocess


def test_runner_main_file_not_found():
    result = subprocess.run(
        [sys.executable, "-m", "lambdora.runner", "nonexistent_file.lamb"],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert (
        "No such file or directory" in result.stderr
        or "not found" in result.stderr
        or "not found" in result.stdout
    )


def test_runner_main_bad_args():
    result = subprocess.run(
        [sys.executable, "-m", "lambdora.runner"], capture_output=True, text=True
    )
    assert result.returncode != 0
    assert "Usage:" in result.stderr or "Usage:" in result.stdout


# Test REPL (simulate exit, help, clear, error)
def test_repl_exit():
    with (
        patch("builtins.input", side_effect=["exit"]),
        patch("builtins.print") as mock_print,
    ):
        from lambdora.repl import repl

        repl()
        assert any("Goodbye" in str(call) for call in mock_print.call_args_list)


def test_repl_help():
    with (
        patch("builtins.input", side_effect=["help", "exit"]),
        patch("builtins.print") as mock_print,
    ):
        from lambdora.repl import repl

        repl()
        assert any("help" in str(call) for call in mock_print.call_args_list)


def test_repl_clear():
    with (
        patch("builtins.input", side_effect=["clear", "exit"]),
        patch("os.system") as mock_system,
        patch("builtins.print"),
    ):
        from lambdora.repl import repl

        repl()
        mock_system.assert_called()


def test_repl_error():
    with (
        patch("builtins.input", side_effect=['(+ 1 "a")', "exit"]),
        patch("builtins.print") as mock_print,
    ):
        from lambdora.repl import repl

        repl()
        assert any("Error:" in str(call) for call in mock_print.call_args_list)
