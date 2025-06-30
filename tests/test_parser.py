from tokenizer import lambTokenize
from parser import lambParse
from astmodule import *

def test_parse_lambda():
    tokens = lambTokenize("(λx. x)")
    expr = lambParse(tokens)
    assert isinstance(expr, Abstraction)
    assert expr.param == 'x'
    assert isinstance(expr.body, Variable)

def test_unclosed_if():
    with pytest.raises(SyntaxError):
        runExpression("(if true 1 2")  # Missing closing paren