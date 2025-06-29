from tokenizer import lambTokenize
from parser import lambParse
from astmodule import *

def test_parse_lambda():
    tokens = lambTokenize("(λx. x)")
    expr = lambParse(tokens)
    assert isinstance(expr, Abstraction)
    assert expr.param == 'x'
    assert isinstance(expr.body, Variable)
