import sys

from tokenizer import lambTokenize
from parser import lambParse, lambParseAll
from evaluator import lambEval
from printer import lambPrint
from builtinsmodule import lambMakeTopEnv

env = lambMakeTopEnv()

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
        print("=>", result)

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
                print("=>", result)
            except Exception as e:
                print("Error:", e)