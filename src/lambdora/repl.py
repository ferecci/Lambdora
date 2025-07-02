"""Interactive Lambdora REPL."""

import os
import readline
from pathlib import Path

from colorama import Fore, Style
from colorama import init as _colorama_init

from .astmodule import Expr, QuasiQuoteExpr
from .builtinsmodule import lambMakeTopEnv
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

    history_file = os.path.expanduser("~/.lambdora_history")

    # Load existing history, if any.
    try:
        if hasattr(readline, "read_history_file"):
            readline.read_history_file(history_file)
    except FileNotFoundError:
        pass  # First run – no history yet.

    # Keep a reasonably long history and ensure it is saved on exit.
    if hasattr(readline, "set_history_length"):
        readline.set_history_length(1000)

    import atexit

    if hasattr(readline, "write_history_file"):
        atexit.register(readline.write_history_file, history_file)


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
  exit, quit  - Exit the REPL
  help        - Show this help message
  clear       - Clear the screen
  
Lambdora syntax:
  (+ 1 2)                - Function application
  (λx. x)                - Lambda expression
  (define f (λx. x))     - Define a function / variable
  (let x 1 (+ x 2))      - Let-binding
  (if cond then else)    - Conditional expression
  (defmacro m (x) x)     - Define a macro
  `(a ,b c)              - Quasiquote with unquote
  '(1 2 3)               - Quote shorthand (same as (quote …))
  ; this is a comment    - Semicolon starts a comment to EOL
  
Press Ctrl+C or Ctrl+D to exit.
"""
    print(f"{Fore.CYAN}{help_text}{Style.RESET_ALL}")


def load_std() -> None:
    std = Path(__file__).with_suffix("").parent / "stdlib" / "std.lamb"
    if not std.exists():
        return
    tokens = lambTokenize(std.read_text(encoding="utf-8"))
    for expr in lambParseAll(tokens):
        exp = lambMacroExpand(expr, ENV)
        if exp is not None:
            trampoline(lambEval(exp, ENV, is_tail=True))


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


def repl() -> None:
    """Start the interactive prompt."""
    setup_readline()  # Initialise readline/history support
    load_std()

    # Print welcome message
    print(f"{Fore.MAGENTA}Lambdora REPL{Style.RESET_ALL}")
    print(
        f"Type {Fore.CYAN}'exit'{Style.RESET_ALL} or "
        f"{Fore.CYAN}'quit'{Style.RESET_ALL} to exit, "
        f"{Fore.CYAN}'help'{Style.RESET_ALL} for help."
    )

    while True:
        try:
            line = input(colored_prompt())

            # Handle empty input
            if not line.strip():
                continue

            # Handle special commands
            if line.strip().lower() in {"exit", "quit"}:
                print_goodbye()
                break
            elif line.strip().lower() == "help":
                print_help()
                continue
            elif line.strip().lower() == "clear":
                os.system("cls" if os.name == "nt" else "clear")
                continue

            # Evaluate expression with enhanced error recovery
            try:
                out = run_expr(line)
                if out is not nil:
                    result_str = (
                        lambPrint(out) if isinstance(out, Expr) else valueToString(out)
                    )
                    print_result(result_str)
            except Exception as e:
                # Enhanced error reporting with error type
                error_type = type(e).__name__
                print_error(f"{error_type}: {e}")

        except (EOFError, KeyboardInterrupt):
            print()  # New line after ^C or ^D
            print_goodbye()
            break
        except Exception as e:
            # Catch-all for unexpected errors to keep REPL running
            print_error(f"Unexpected error: {e}")
            print(f"{Fore.YELLOW}REPL continuing...{Style.RESET_ALL}")


if __name__ == "__main__":
    setup_readline()
    repl()
