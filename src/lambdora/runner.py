"""Run a .lamb source file."""

import sys
from pathlib import Path

from .builtinsmodule import lambMakeTopEnv
from .errors import LambError, format_lamb_error
from .evaluator import lambEval, trampoline
from .macro import lambMacroExpand
from .parser import lambParseAll
from .tokenizer import lambTokenize
from .values import nil, valueToString

ENV = lambMakeTopEnv()


def load_std() -> None:
    """Load the standard library into the environment."""
    std = Path(__file__).with_suffix("").parent / "stdlib" / "std.lamb"
    if std.exists():
        try:
            tokens = lambTokenize(std.read_text(encoding="utf-8"))
            for e in lambParseAll(tokens):
                exp = lambMacroExpand(e, ENV)
                if exp is not None:
                    trampoline(lambEval(exp, ENV, is_tail=True))
        except LambError as err:
            print(f"Error loading standard library: {format_lamb_error(err)}", file=sys.stderr)
            sys.exit(1)


def run_file(path: Path) -> None:
    """Execute a Lambdora script file."""
    load_std()
    
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        print(f"Error reading file '{path}': {e}", file=sys.stderr)
        sys.exit(1)
    
    try:
        tokens = lambTokenize(content)
        for expr in lambParseAll(tokens):
            exp = lambMacroExpand(expr, ENV)
            if exp is None:
                continue
            out = trampoline(lambEval(exp, ENV, is_tail=True))
            if out is not nil:
                print(valueToString(out))
    except LambError as err:
        print(format_lamb_error(err), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Legacy main function for backward compatibility."""
    if len(sys.argv) != 2:
        print("Usage: python -m lambdora.runner <file.lamb>", file=sys.stderr)
        print("Note: Use 'lambdora run <file.lamb>' for the new CLI interface", file=sys.stderr)
        sys.exit(1)
    run_file(Path(sys.argv[1]))


if __name__ == "__main__":
    main()
