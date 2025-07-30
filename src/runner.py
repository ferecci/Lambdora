"""Run a .lamb source file."""

import sys
from pathlib import Path
from typing import Optional

from .builtinsmodule import lambMakeTopEnv
from .errors import LambError, format_lamb_error
from .evaluator import lambEval, trampoline
from .macro import lambMacroExpand
from .parser import lambParseAll
from .tokenizer import lambTokenize
from .values import nil, valueToString

ENV = lambMakeTopEnv()


def load_std(stdlib_path: Optional[Path] = None) -> None:
    """Load the standard library into the environment."""
    if stdlib_path is None:
        std = Path(__file__).with_suffix("").parent / "stdlib" / "std.lamb"
    else:
        std = stdlib_path

    if not std.exists():
        if stdlib_path is not None:
            print(
                f"Warning: Custom stdlib file '{stdlib_path}' not found.",
                file=sys.stderr,
            )
            print("Falling back to built-in standard library...", file=sys.stderr)
            std = Path(__file__).with_suffix("").parent / "stdlib" / "std.lamb"
        if not std.exists():
            return
    try:
        tokens = lambTokenize(std.read_text(encoding="utf-8"))
        for e in lambParseAll(tokens):
            exp = lambMacroExpand(e, ENV)
            if exp is not None:
                trampoline(lambEval(exp, ENV, is_tail=True))
    except LambError as err:
        print(
            f"Error loading standard library: {format_lamb_error(err)}", file=sys.stderr
        )
        sys.exit(1)


def run_file(path: Path, stdlib_path: Optional[Path] = None) -> None:
    """Execute a Lambdora script file."""
    # Load the standard library first. We guard this call so that *any* unexpected
    # error coming from stdlib loading is reported consistently and terminates
    # the process with the same exit semantics the tests expect.
    try:
        load_std(stdlib_path)
    except Exception as e:  # pragma: no cover – unexpected failures should abort
        print(f"Unexpected error while loading standard library: {e}", file=sys.stderr)
        print(
            "Tip: This might be a bug in Lambdora. Please report it.", file=sys.stderr
        )
        sys.exit(1)

    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        print(f"Error reading file '{path}': {e}", file=sys.stderr)
        if isinstance(e, UnicodeDecodeError):
            print("Tip: Make sure the file is encoded in UTF-8.", file=sys.stderr)
        sys.exit(1)

    try:
        tokens = lambTokenize(content)
        for expr in lambParseAll(tokens):
            exp = lambMacroExpand(expr, ENV)
            if exp is None:
                continue
            out = trampoline(lambEval(exp, ENV, is_tail=True))
            # Only print user-visible results.  Definitions like `(define x …)`
            # evaluate to a sentinel string such as "<defined x>" which we do
            # not want to show to the end-user (and tests explicitly assert
            # that nothing is printed in that case).  Anything that is *not*
            # nil and does *not* start with "<defined " should be displayed.
            if out is not nil and not (
                isinstance(out, str) and out.startswith("<defined ")
            ):
                print(valueToString(out))
    except LambError as err:
        print(format_lamb_error(err), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        print(
            "Tip: This might be a bug in Lambdora. Please report it.", file=sys.stderr
        )
        sys.exit(1)


def main() -> None:
    """Legacy main function for backward compatibility."""
    if len(sys.argv) != 2:
        print("Usage: python -m lambdora.runner <file.lamb>", file=sys.stderr)
        print(
            "Note: Use 'lambdora run <file.lamb>' for the new CLI interface",
            file=sys.stderr,
        )
        sys.exit(1)
    run_file(Path(sys.argv[1]))


if __name__ == "__main__":
    main()
