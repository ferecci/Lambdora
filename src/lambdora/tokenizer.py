"""Tokenizer for Lambdora source code (returns ``list[str]``)."""

from __future__ import annotations

from .errors import TokenizeError


def _line_at(src: str, line_no: int) -> str:
    """Return the given 1-based line from *src*."""

    return src.splitlines()[line_no - 1]


def lambTokenize(source: str, *, filename: str | None = None) -> list[str]:
    """Tokenise *source*. *filename* is used only in error messages."""

    tokens: list[str] = []
    i = 0  # absolute index into *source*
    line_no = 1
    col_no = 1  # 1-based column index

    while i < len(source):
        char = source[i]

        # Newline
        if char == "\n":
            i += 1
            line_no += 1
            col_no = 1
            continue

        # Skip ';' comments
        if char == ";":
            while i < len(source) and source[i] != "\n":
                i += 1
                col_no += 1
            continue  # newline (if any) handled on next loop iteration

        # Whitespace
        if char.isspace():
            i += 1
            col_no += 1
            continue

        # Multi-char operators (check before single-char tokens)
        if i + 1 < len(source):
            two_char = source[i : i + 2]
            if two_char in ["++", "!=", "<=", ">="]:
                tokens.append(two_char)
                i += 2
                col_no += 2
                continue

        # Single-char tokens
        if char in "().+-*/%=<>',`":
            tokens.append(char)
            i += 1
            col_no += 1
            continue

        # Identifiers
        if char.isalpha() or char == "_":
            start = i
            while i < len(source) and (
                source[i].isalnum() or source[i] == "_" or source[i] == "-"
            ):
                i += 1
                col_no += 1
            tokens.append(source[start:i])
            continue

        # Integers
        if char.isdigit():
            start = i
            while i < len(source) and source[i].isdigit():
                i += 1
                col_no += 1
            tokens.append(source[start:i])
            continue

        # Strings
        if char == '"':
            i += 1
            col_no += 1
            start_idx = i
            str_line, str_col = line_no, col_no

            while i < len(source) and source[i] != '"':
                if source[i] == "\n":
                    line_no += 1
                    col_no = 0  # will be incremented at end of loop
                i += 1
                col_no += 1

            if i >= len(source):  # reached EOF
                snippet = _line_at(source, str_line)
                raise TokenizeError(
                    "Unterminated string literal",
                    file=filename,
                    line=str_line,
                    column=str_col,
                    snippet=snippet,
                )

            # Slice out the contents (excluding the quotes)
            literal = source[start_idx:i]
            tokens.append(f'"{literal}"')

            # Skip the closing quote
            i += 1
            col_no += 1
            continue

        # Unknown char
        snippet = _line_at(source, line_no)
        raise TokenizeError(
            f"Unexpected character: {char}",
            file=filename,
            line=line_no,
            column=col_no,
            snippet=snippet,
        )

    return tokens
