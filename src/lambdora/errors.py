"""Error hierarchy and colourised pretty-printer for Lambdora."""

from __future__ import annotations

import traceback
from typing import Optional

from colorama import Fore, Style
from colorama import init as _colorama_init

_colorama_init(autoreset=True)


class LambError(Exception):
    """Base error with optional location info (file, line, column, snippet)."""

    def __init__(
        self,
        message: str,
        *,
        file: Optional[str] = None,
        line: Optional[int] = None,
        column: Optional[int] = None,
        snippet: Optional[str] = None,
        cause: Optional[BaseException] = None,
    ) -> None:
        super().__init__(message)
        self.file = file
        self.line = line
        self.column = column
        self.snippet = snippet.rstrip("\n") if snippet else None
        # Preserve original traceback while allowing pretty presentation
        if cause is not None:
            self.__cause__ = cause

    def _loc(self) -> str:
        if self.line is None or self.column is None:
            return ""
        location = f"{self.file or '<unknown>'}:{self.line}:{self.column}"
        return location

    def __str__(self) -> str:
        loc = self._loc()
        return f"{loc + ': ' if loc else ''}{super().__str__()}"


class TokenizeError(LambError, SyntaxError):
    """Thrown by the tokenizer when it cannot produce a valid token stream."""


class ParseError(LambError, SyntaxError):
    """Raised by the parser upon syntactic mistakes at the token level."""


class MacroExpansionError(LambError, RuntimeError):
    """Problems occurring during macro expansion (wrong arity, etc.)."""


class EvalError(LambError, NameError, TypeError):
    """Catch-all for runtime evaluation mistakes inside ``evaluator.py``."""


class BuiltinError(LambError, TypeError):
    """Invalid usage of built-in functions."""


class RecursionInitError(LambError, RuntimeError):
    """Accessing a recursive binding before it is initialised."""


__all__ = [
    "LambError",
    "TokenizeError",
    "ParseError",
    "MacroExpansionError",
    "EvalError",
    "BuiltinError",
    "RecursionInitError",
    "format_lamb_error",
]


def format_lamb_error(err: LambError) -> str:
    """Return a colourised traceback + message for *err*."""

    # Grey/dim stack frames, excluding the very last (the user-facing one)
    grey = Style.DIM + Fore.WHITE
    frames: list[str] = (
        traceback.format_tb(err.__traceback__) if err.__traceback__ else []
    )
    pretty_frames = [grey + f for f in frames[:-1]]  # dim all but last frame

    # Bold red bullet for the error header
    header = f"{Style.BRIGHT + Fore.RED}{type(err).__name__}{Style.RESET_ALL}: {err}"

    # Show code snippet if we have one
    snippet = ""
    if err.snippet:
        caret = " " * (err.column - 1 if err.column and err.column > 0 else 0) + "^"
        snippet = (
            f"{Style.DIM}{err.snippet}{Style.RESET_ALL}\n"
            f"{Style.DIM}{caret}{Style.RESET_ALL}"
        )

    # Add helpful suggestions based on error type
    suggestion = ""
    if isinstance(err, TokenizeError):
        if "unexpected token" in str(err).lower():
            suggestion = (
                f"\n{Fore.YELLOW}Tip: Check for unmatched parentheses or "
                f"invalid syntax.{Style.RESET_ALL}"
            )
        elif "unterminated string" in str(err).lower():
            suggestion = (
                f"\n{Fore.YELLOW}Tip: Make sure all strings are properly "
                f"closed with quotes.{Style.RESET_ALL}"
            )
    elif isinstance(err, ParseError):
        if "unexpected eof" in str(err).lower():
            suggestion = (
                f"\n{Fore.YELLOW}Tip: Check for missing closing "
                f"parentheses.{Style.RESET_ALL}"
            )
        elif "unbound variable" in str(err).lower():
            suggestion = (
                f"\n{Fore.YELLOW}Tip: Make sure the variable is defined "
                f"before use.{Style.RESET_ALL}"
            )
    elif isinstance(err, EvalError):
        if "unbound variable" in str(err).lower():
            suggestion = (
                f"\n{Fore.YELLOW}Tip: Use (define var value) to define "
                f"variables.{Style.RESET_ALL}"
            )
        elif "lambda syntax" in str(err).lower():
            suggestion = (
                f"\n{Fore.YELLOW}Tip: Lambda syntax is (lambda param . "
                f"body){Style.RESET_ALL}"
            )

    return (
        "".join(pretty_frames)
        + header
        + ("\n" + snippet if snippet else "")
        + suggestion
    )
