"""Interactive prompt for Lambdora."""

from pathlib import Path
try:
    import readline  # Enhanced input editing (Unix/macOS built-in, pyreadline3 on Windows)
except ImportError:
    pass  # Fallback to basic input() on Windows without pyreadline3
from .tokenizer import lambTokenize
from .parser import lambParse, lambParseAll
from .evaluator import lambEval, trampoline, evalQuasiquote
from .printer import lambPrint
from .macro import lambMacroExpand
from .builtinsmodule import lambMakeTopEnv
from .values import valueToString, nil
from .astmodule import Expr, QuasiQuoteExpr

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

def run_expr(src: str):
    tokens = lambTokenize(src)
    expr  = lambParse(tokens)
    
    # Handle top-level quasiquotes before macro expansion
    if isinstance(expr, QuasiQuoteExpr):
        return evalQuasiquote(expr.expr, ENV)
    
    exp   = lambMacroExpand(expr, ENV)
    if exp is None:
        return "<macro defined>"
    return trampoline(lambEval(exp, ENV, is_tail=True))

def repl() -> None:
    load_std()
    while True:
        try:
            line = input("λ> ")
            if line.strip() in {"exit", "quit"}:
                print("Goodbye."); break
            out = run_expr(line)
            if out is not nil:
                print("=>", lambPrint(out) if isinstance(out, Expr) else valueToString(out))
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye."); break
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    repl()