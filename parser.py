from astmodule import *
from typing import List
import re

def parseExpression(tokens: List[str], i: int):
    token = tokens[i]

    if token == '(':
        i += 1
        if tokens[i] == 'λ':
            i += 1
            param = tokens[i]
            i += 1
            if tokens[i] != '.':
                raise SyntaxError("Expected '.' after lambda param")
            i += 1
            body, i = parseExpression(tokens, i)
            if tokens[i] != ')':
                raise SyntaxError("Expected ')' after lambda body")
            return Abstraction(param, body), i + 1

        elif tokens[i] == 'let':
            i += 1
            var = tokens[i]
            i += 1
            value_expr, i = parseExpression(tokens, i)
            body_expr, i = parseExpression(tokens, i)
            if tokens[i] != ')':
                raise SyntaxError("Expected ')' after let expression")
            return Application(Abstraction(var, body_expr), [value_expr]), i + 1

        elif tokens[i] == 'define':
            i += 1
            name = tokens[i]
            i += 1
            value_expr, i = parseExpression(tokens, i)
            if tokens[i] != ')':
                raise SyntaxError("Expected ')' after define expression")
            return DefineExpr(name, value_expr), i + 1

        elif tokens[i] == 'if':
            i += 1
            cond, i = parseExpression(tokens, i)
            then_b, i = parseExpression(tokens, i)
            else_b, i = parseExpression(tokens, i)
            if tokens[i] != ')':
                raise SyntaxError("Expected ')' after if")
            return IfExpr(cond, then_b, else_b), i + 1

        else:
            func, i = parseExpression(tokens, i)
            args = []
            while tokens[i] != ')':
                arg, i = parseExpression(tokens, i)
                args.append(arg)
            return Application(func, args), i + 1

    elif token.isnumeric():
        return Literal(token), i + 1

    elif re.match(r'^[a-zA-Z0-9_+\-*/=<>!?]+$', token):
        return Variable(token), i + 1

    else:
        raise SyntaxError(f"Unexpected token: {token}")

# Parse for a single expr
def lambParse(tokens: List[str]) -> Expr:
    expr, final_i = parseExpression(tokens, 0)
    if final_i != len(tokens):
        raise SyntaxError("Unexpected extra tokens")
    return expr

# ParseAll for many top-level exprs
def lambParseAll(tokens: List[str]) -> List[Expr]:
    exprs = []
    i = 0
    while i < len(tokens):
        expr, i = parseExpression(tokens, i)
        exprs.append(expr)
    return exprs
