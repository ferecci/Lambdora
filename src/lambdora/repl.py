"""Interactive prompt for Lambdora."""

from pathlib import Path

from .astmodule import Expr, QuasiQuoteExpr
from .builtinsmodule import lambMakeTopEnv
from .evaluator import evalQuasiquote, lambEval, trampoline
from .macro import lambMacroExpand
from .parser import lambParse, lambParseAll
from .printer import lambPrint
from .tokenizer import lambTokenize
from .values import Value, nil, valueToString

# One shared top-level environment
ENV = lambMakeTopEnv()


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
    load_std()
    while True:
        try:
            line = input("λ> ")
            if line.strip() in {"exit", "quit"}:
                print("Goodbye.")
                break
            out = run_expr(line)
            if out is not nil:
                print(
                    "=>",
                    lambPrint(out) if isinstance(out, Expr) else valueToString(out),
                )
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break
        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    repl()
