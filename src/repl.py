"""Interactive Lambdora REPL."""

import atexit
import os
import readline
from pathlib import Path
from typing import Optional

from colorama import Fore, Style
from colorama import init as _colorama_init

from .astmodule import Expr, QuasiQuoteExpr
from .builtinsmodule import lambMakeTopEnv
from .errors import LambError, format_lamb_error
from .evaluator import evalQuasiquote, lambEval, trampoline
from .macro import lambMacroExpand
from .parser import lambParse, lambParseAll
from .printer import lambPrint
from .tokenizer import lambTokenize
from .values import Value, nil, valueToString

_colorama_init(autoreset=True)

# One shared top-level environment.
ENV = lambMakeTopEnv()


def setup_readline() -> None:
    """Set up line editing and history."""

    history_file = os.path.join(os.path.dirname(__file__), ".lambdora_history")

    try:
        if hasattr(readline, "read_history_file"):
            try:
                readline.read_history_file(history_file)
            except (FileNotFoundError, AttributeError):
                pass
    except AttributeError:
        pass

    try:
        if hasattr(readline, "set_history_length"):
            try:
                readline.set_history_length(1000)
            except AttributeError:
                pass
    except AttributeError:
        pass

    try:
        if hasattr(readline, "write_history_file"):
            try:
                if callable(readline.write_history_file):
                    def safe_write_history() -> None:
                        try:
                            readline.write_history_file(history_file)
                        except Exception:
                            pass

                    atexit.register(safe_write_history)
            except (AttributeError, TypeError):
                pass
    except AttributeError:
        pass


def colored_prompt() -> str:
    """Return the coloured prompt string."""
    return f"{Fore.CYAN}λ{Style.RESET_ALL}> "


def print_error(message: str) -> None:
    """Print an error message."""
    print(f"{Fore.RED}Error:{Style.RESET_ALL} {message}")


def print_result(result: str) -> None:
    """Print evaluation result."""
    print(f"{Fore.GREEN}=>{Style.RESET_ALL} {result}")


def print_goodbye() -> None:
    """Print farewell message."""
    print(f"{Fore.YELLOW}Goodbye.{Style.RESET_ALL}")


def print_help() -> None:
    """Show built-in help."""
    help_text = """
Available commands:
  exit, quit  - Exit the REPL (also works in multiline mode)
  help        - Show this help message
  clear       - Clear the screen
  \b         - Remove the last line in multiline mode

Lambdora syntax:
  (+ 1 2)                - Function application
  (lambda x. x)          - Lambda expression
  (define f (lambda x. x)) - Define a function / variable
  (let x 1 (+ x 2))      - Let-binding
  (if cond then else)    - Conditional expression
  (defmacro m (x) x)     - Define a macro
  `(a ,b c)              - Quasiquote with unquote
  '(1 2 3)               - Quote shorthand (same as (quote …))
  ; this is a comment    - Semicolon starts a comment to EOL

Multiline input:
  If you enter an incomplete expression (e.g. unbalanced parentheses),
  the REPL will prompt with '...'.
  Type \b to remove the last line, or 'exit'/'quit' to cancel multiline input.
  Press Ctrl+C or Ctrl+D to exit.
"""
    print(f"{Fore.CYAN}{help_text}{Style.RESET_ALL}")


def load_std(stdlib_path: Optional[Path] = None) -> None:
    """Load the standard library into the REPL environment."""
    if stdlib_path is None:
        std = Path(__file__).with_suffix("").parent / "stdlib" / "std.lamb"
    else:
        std = stdlib_path

    if not std.exists():
        if stdlib_path is not None:
            print(
                f"{Fore.YELLOW}Warning: Custom stdlib file "
                f"'{stdlib_path}' not found.{Style.RESET_ALL}"
            )
            print(
                f"{Fore.YELLOW}Falling back to built-in standard "
                f"library...{Style.RESET_ALL}"
            )
            std = Path(__file__).with_suffix("").parent / "stdlib" / "std.lamb"
        if not std.exists():
            return
    try:
        tokens = lambTokenize(std.read_text(encoding="utf-8"))
        for expr in lambParseAll(tokens):
            exp = lambMacroExpand(expr, ENV)
            if exp is not None:
                trampoline(lambEval(exp, ENV, is_tail=True))
    except LambError as err:
        print_error(f"Error loading standard library: {format_lamb_error(err)}")
        print(
            f"{Fore.YELLOW}REPL continuing without standard library...{Style.RESET_ALL}"
        )


def run_expr(src: str) -> Value:
    tokens = lambTokenize(src)
    expr = lambParse(tokens)

    # Handle top-level quasiquotes before macro expansion
    if isinstance(expr, QuasiQuoteExpr):
        return evalQuasiquote(expr.expr, ENV)

    exp = lambMacroExpand(expr, ENV)
    if exp is None:
        return "<macro defined>"
    return trampoline(lambEval(exp, ENV, is_tail=True))


def repl(stdlib_path: Optional[Path] = None) -> None:
    """Start the interactive prompt."""
    setup_readline()
    load_std(stdlib_path)

    print(f"{Fore.MAGENTA}Lambdora REPL{Style.RESET_ALL}")
    if stdlib_path:
        print(f"{Fore.CYAN}Using custom stdlib: {stdlib_path}{Style.RESET_ALL}")
    print(
        f"Type {Fore.CYAN}'exit'{Style.RESET_ALL} or "
        f"{Fore.CYAN}'quit'{Style.RESET_ALL} to exit, "
        f"{Fore.CYAN}'help'{Style.RESET_ALL} for help."
    )

    def _needs_more(src: str) -> bool:
        """Return True if *src* likely needs more lines (unbalanced parens)."""
        depth, in_str = 0, False
        i = 0
        while i < len(src):
            ch = src[i]
            if ch == '"':
                in_str = not in_str
            elif not in_str:
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
            i += 1
        return depth > 0

    while True:
        try:
            src_lines: list[str] = []
            prompt = colored_prompt()
            line = input(prompt)
            src_lines.append(line)
            multiline_cancelled = False
            while _needs_more("\n".join(src_lines)) or src_lines[-1].endswith("\\"):
                if src_lines[-1].endswith("\\"):
                    src_lines[-1] = src_lines[-1][:-1]
                cont = input("... ")

                if cont.strip().lower() in {"exit", "quit"}:
                    print("<multiline cancelled>")
                    multiline_cancelled = True
                    break

                if cont.strip() == "\\b":
                    if len(src_lines) > 1:
                        removed = src_lines.pop()
                        print(f"<removed: {removed}>")
                    else:
                        print("<nothing to remove>")
                    continue

                src_lines.append(cont)

            if multiline_cancelled:
                continue

            if not src_lines:
                continue

            line = "\n".join(src_lines)

            if not line.strip():
                continue

            if line.strip().lower() in {"exit", "quit"}:
                print_goodbye()
                break
            elif line.strip().lower() == "help":
                print_help()
                continue
            elif line.strip().lower() == "clear":
                os.system("cls" if os.name == "nt" else "clear")
                continue

            try:
                out = run_expr(line)
                if out is not nil:
                    result_str = (
                        lambPrint(out) if isinstance(out, Expr) else valueToString(out)
                    )
                    print_result(result_str)
            except LambError as err:
                print_error(format_lamb_error(err))
            except Exception as e:
                error_type = type(e).__name__
                print_error(f"{error_type}: {e}")
                print(
                    (
                        f"{Fore.YELLOW}"
                        "REPL exiting due to unexpected error..."
                        f"{Style.RESET_ALL}"
                    )
                )
                break

        except (EOFError, KeyboardInterrupt, StopIteration):
            print()
            print_goodbye()
            break
        except Exception as e:
            print_error(f"Unexpected error: {e}")
            print(
                f"{Fore.YELLOW}REPL exiting due to unexpected error...{Style.RESET_ALL}"
            )
            break


def main() -> None:
    """Legacy main function for backward compatibility."""
    print("Note: Use 'lambdora repl' for the new CLI interface")
    os.system("clear")
    setup_readline()
    repl()


if __name__ == "__main__":
    main()
