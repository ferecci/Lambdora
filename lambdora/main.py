"""Command line interface and REPL for the Lambdora interpreter."""

import sys
from os.path import join, dirname, abspath
from .tokenizer import lambTokenize
from .parser import lambParse, lambParseAll
from .evaluator import lambEval, trampoline
from .printer import lambPrint
from .builtinsmodule import lambMakeTopEnv
from .values import valueToString, nil
from .macro import lambMacroExpand

env = lambMakeTopEnv()

def format_error(e: Exception) -> str:
    if isinstance(e, NameError):
        return str(e).replace("Unbound variable", "unbound variable")
    if isinstance(e, SyntaxError):
        return str(e).replace("SyntaxError", "").strip()
    if isinstance(e, TypeError):
        return str(e).replace("TypeError", "").strip()
    return str(e)

def load_std():
    std_path = join(dirname(abspath(__file__)), "stdlib", "std.lamb")
    with open(std_path, encoding='utf-8') as f:
        source = f.read()
    tokens = lambTokenize(source)
    exprs = lambParseAll(tokens)
    for expr in exprs:
        raw = lambEval(expr, env, is_tail=True)
        trampoline(raw)

def runExpression(source: str):
    tokens = lambTokenize(source)
    expr = lambParse(tokens)
    exp = lambMacroExpand(expr, env)
    if exp is None:
        return "<macro defined>"
    raw = lambEval(exp, env, is_tail=True)
    return trampoline(raw)

def runFile(filename: str):
    with open(filename, encoding='utf-8') as f:
        source = f.read()
    tokens = lambTokenize(source)
    exprs = lambParseAll(tokens)
    for expr in exprs:
        exp = lambMacroExpand(expr, env)
        if exp is None:
            continue
        raw = lambEval(exp, env, is_tail=True)
        result = trampoline(raw)
        if result is not nil:
            print(valueToString(result))

if __name__ == "__main__":
    load_std()
    if len(sys.argv) > 1:
        runFile(sys.argv[1])
    else:
        while True:
            try:
                source = input("λ> ")
                if source.strip() in ("exit", "quit"):
                    print("Goodbye.")
                    break
                result = runExpression(source)
                if result is not nil:
                    print("=>", valueToString(result))
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye.")
                break
            except Exception as e:
                print("Error:", format_error(e))

