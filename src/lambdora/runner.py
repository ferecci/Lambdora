"""Run a .lamb source file."""

import sys
from pathlib import Path

from .builtinsmodule import lambMakeTopEnv
from .evaluator import lambEval, trampoline
from .macro import lambMacroExpand
from .parser import lambParseAll
from .tokenizer import lambTokenize
from .values import nil, valueToString

ENV = lambMakeTopEnv()


def load_std() -> None:
    std = Path(__file__).with_suffix("").parent / "stdlib" / "std.lamb"
    if std.exists():
        tokens = lambTokenize(std.read_text(encoding="utf-8"))
        for e in lambParseAll(tokens):
            exp = lambMacroExpand(e, ENV)
            if exp is not None:
                trampoline(lambEval(exp, ENV, is_tail=True))


def run_file(path: Path) -> None:
    load_std()
    tokens = lambTokenize(path.read_text(encoding="utf-8"))
    for expr in lambParseAll(tokens):
        exp = lambMacroExpand(expr, ENV)
        if exp is None:
            continue
        out = trampoline(lambEval(exp, ENV, is_tail=True))
        if out is not nil:
            print(valueToString(out))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python -m lambdora.runner <file.lamb>")
    run_file(Path(sys.argv[1]))
