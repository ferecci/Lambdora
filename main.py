import sys

from os.path import join, dirname

from tokenizer import lambTokenize
from parser import lambParse, lambParseAll
from evaluator import lambEval
from printer import lambPrint
from builtinsmodule import lambMakeTopEnv
from values import valueToString

env = lambMakeTopEnv()

def load_std():
    std_path = join(dirname(__file__), "stdlib", "std.lamb")
    with open(std_path, encoding='utf-8') as f:
        source = f.read()
    tokens = lambTokenize(source)
    exprs = lambParseAll(tokens)
    for expr in exprs:
        lambEval(expr, env)

load_std()

def runExpression(source: str):
    tokens = lambTokenize(source)
    expr = lambParse(tokens)
    result = lambEval(expr, env)
    return result

def runFile(filename: str):
    with open(filename, encoding='utf-8') as f:
        source = f.read()
    tokens = lambTokenize(source)
    exprs = lambParseAll(tokens)
    for expr in exprs:
        result = lambEval(expr, env)
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
                print("=>", valueToString(result))
            except Exception as e:
                print("Error:", e)