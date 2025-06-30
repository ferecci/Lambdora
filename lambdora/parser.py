"""Parsing logic converting tokens into AST nodes."""

from astmodule import *
from typing import List, Tuple
import re

def parseExpression(tokens: List[str], i: int) -> Tuple[Expr, int]:
    """Parse an expression from ``tokens`` starting at index ``i``."""
    if i >= len(tokens):
        raise SyntaxError("Unexpected EOF while parsing")
    token = tokens[i]

    if token == '`':                           # Back-quote
        expr, j = parseExpression(tokens, i + 1)
        return QuasiQuoteExpr(expr), j

    if token == ',':                           # Comma
        expr, j = parseExpression(tokens, i + 1)
        return UnquoteExpr(expr), j

    if token == '(':
        i += 1
        if i >= len(tokens):
            raise SyntaxError("Unexpected EOF after '('")

        if tokens[i] == 'λ':
            i += 1
            if i >= len(tokens): raise SyntaxError("Unexpected EOF after λ")
            if tokens[i] == ',':
                i += 1
                if i >= len(tokens):
                    raise SyntaxError("Unexpected EOF after ',' in λ")
            param = tokens[i]
            i += 1
            if i >= len(tokens): raise SyntaxError("Unexpected EOF after lambda param")
            if tokens[i] != '.':
                raise SyntaxError("Expected '.' after lambda param")
            i += 1
            if i >= len(tokens): raise SyntaxError("Unexpected EOF after lambda dot")
            body, i = parseExpression(tokens, i)
            if i >= len(tokens): raise SyntaxError("Unexpected EOF after lambda body")
            if tokens[i] != ')':
                raise SyntaxError("Expected ')' after lambda body")
            return Abstraction(param, body), i + 1

        elif tokens[i] == 'let':
            i += 1
            if i >= len(tokens): raise SyntaxError("Unexpected EOF after let")
            var = tokens[i]
            i += 1
            if i >= len(tokens): raise SyntaxError("Unexpected EOF after let var")
            value_expr, i = parseExpression(tokens, i)
            body_expr, i = parseExpression(tokens, i)
            if i >= len(tokens): raise SyntaxError("Unexpected EOF after let body")
            if tokens[i] != ')':
                raise SyntaxError("Expected ')' after let expression")
            return Application(Abstraction(var, body_expr), [value_expr]), i + 1

        elif tokens[i] == 'define':
            i += 1
            if i + 1 >= len(tokens): raise SyntaxError("Unexpected EOF in define expression, expected name and value")
            name = tokens[i]
            i += 1
            if i >= len(tokens): raise SyntaxError("Unexpected EOF after define name")
            value_expr, i = parseExpression(tokens, i)
            if i >= len(tokens): raise SyntaxError("Unexpected EOF after define value")
            if tokens[i] != ')':
                raise SyntaxError("Expected ')' after define expression")
            return DefineExpr(name, value_expr), i + 1

        elif tokens[i] == 'if':
            i += 1
            if i + 2 >= len(tokens): raise SyntaxError("Unexpected EOF in if expression, expected condition, then, and else branches")
            cond, i = parseExpression(tokens, i)
            then_b, i = parseExpression(tokens, i)
            else_b, i = parseExpression(tokens, i)
            if i >= len(tokens): raise SyntaxError("Unexpected EOF after if expression")
            if tokens[i] != ')':
                raise SyntaxError("Expected ')' after if expression")
            return IfExpr(cond, then_b, else_b), i + 1
        
        elif tokens[i] == 'defmacro':
            i += 1
            if i >= len(tokens): raise SyntaxError("Unexpected EOF after defmacro")
            name = tokens[i]; i += 1
            if i >= len(tokens): raise SyntaxError("Unexpected EOF after defmacro name")
            # parse parameter list
            if tokens[i] != '(':
                raise SyntaxError("Expected '(' after defmacro name")
            i += 1
            params = []
            while i < len(tokens) and tokens[i] != ')':
                params.append(tokens[i]); i += 1
            if i >= len(tokens):
                raise SyntaxError("Unterminated parameter list in defmacro")
            i += 1  # skip the closing ')'
            if i >= len(tokens):
                raise SyntaxError("Unexpected EOF after defmacro parameter list")
            body, i = parseExpression(tokens, i)
            if i >= len(tokens): raise SyntaxError("Unexpected EOF after defmacro body")
            if tokens[i] != ')':
                raise SyntaxError("Expected ')' after defmacro body")
            return DefMacroExpr(name, params, body), i + 1

        elif tokens[i] == 'quasiquote':
            i += 1
            body, i = parseExpression(tokens, i)
            if i >= len(tokens) or tokens[i] != ')':
                raise SyntaxError("Expected ')' after quasiquote")
            return QuasiQuoteExpr(body), i + 1

        elif tokens[i] == 'unquote':
            i += 1
            body, i = parseExpression(tokens, i)
            if i >= len(tokens) or tokens[i] != ')':
                raise SyntaxError("Expected ')' after unquote")
            return UnquoteExpr(body), i + 1

        elif tokens[i] == 'quote':
            i += 1
            quoted, i = parseExpression(tokens, i)
            if i >= len(tokens) or tokens[i] != ')':
                raise SyntaxError("Expected ')' after quote")
            return QuoteExpr(quoted), i + 1

        else:
            func, i = parseExpression(tokens, i)
            args = []
            while i < len(tokens) and tokens[i] != ')':
                arg, i = parseExpression(tokens, i)
                args.append(arg)
            if i >= len(tokens):
                raise SyntaxError("Unexpected EOF: missing ')'")
            return Application(func, args), i + 1

    elif token == "'":
        quoted, i = parseExpression(tokens, i + 1)
        return QuoteExpr(quoted), i

    elif token.isnumeric():
        return Literal(token), i + 1
    
    elif token.startswith('"') and token.endswith('"'):
        return Literal(token[1:-1]), i + 1

    elif re.match(r'^[a-zA-Z0-9_+\-*/=<>!?%_]+$', token):
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
