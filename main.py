import sys
from os.path import join, dirname
from tokenizer import lambTokenize
from parser import lambParse, lambParseAll
from evaluator import lambEval, trampoline
from printer import lambPrint
from builtinsmodule import lambMakeTopEnv
from values import valueToString, nil
from macro import lambMacroExpand

env = lambMakeTopEnv()

def load_std():
    std_path = join(dirname(__file__), "stdlib", "std.lamb")
    with open(std_path, encoding='utf-8') as f:
        source = f.read()
    tokens = lambTokenize(source)
    exprs = lambParseAll(tokens)
    for expr in exprs:
        raw = lambEval(expr, env, is_tail=True)
        trampoline(raw)
load_std()

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
        if result is nil:
            continue
        if not (isinstance(result, int) or isinstance(result, bool) or isinstance(result, str)):
            print(valueToString(result))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        runFile(sys.argv[1])
    else:
        while True:
            try:
                source = input("λ> ")
                if source.strip() == "exit":
                    break
                result = runExpression(source)
                if result is not nil:
                    print("=>", valueToString(result))
            except Exception as e:
                print("Error:", e)
