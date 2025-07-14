"""Parsing logic converting tokens into AST nodes."""

import re
from typing import List, Tuple

from .astmodule import (
    Abstraction,
    Application,
    DefineExpr,
    DefMacroExpr,
    Expr,
    LetRec,
    Literal,
    QuasiQuoteExpr,
    QuoteExpr,
    UnquoteExpr,
    Variable,
)
from .errors import ParseError as SyntaxError


def parseExpression(
    tokens: List[str], i: int, in_quasiquote: bool = False
) -> Tuple[Expr, int]:
    """Parse an expression from ``tokens`` starting at index ``i``."""
    if i >= len(tokens):
        raise SyntaxError("Unexpected EOF while parsing")
    token = tokens[i]

    if token == "`":  # Back-quote
        expr, j = parseExpression(tokens, i + 1, in_quasiquote=True)
        return QuasiQuoteExpr(expr), j

    if token == ",":  # Comma
        expr, j = parseExpression(tokens, i + 1, in_quasiquote=in_quasiquote)
        return UnquoteExpr(expr), j

    if token == "(":
        i += 1
        if i >= len(tokens):
            raise SyntaxError("Unexpected EOF after '('")

        elif tokens[i] == "letrec":
            i += 1
            if i >= len(tokens):
                raise SyntaxError("Unexpected EOF after letrec")

            # Parse bindings - expect ((name1 value1) (name2 value2) ...)
            if tokens[i] != "(":
                raise SyntaxError("Expected '(' after letrec")
            i += 1

            bindings = []
            while i < len(tokens) and tokens[i] != ")":
                if tokens[i] != "(":
                    raise SyntaxError("Expected '(' for letrec binding")
                i += 1

                if i >= len(tokens):
                    raise SyntaxError("Unexpected EOF in letrec binding")

                # Parse binding name
                name = tokens[i]
                i += 1

                if i >= len(tokens):
                    raise SyntaxError("Unexpected EOF after letrec binding name")

                # Parse binding value
                value, i = parseExpression(tokens, i, in_quasiquote=in_quasiquote)

                if i >= len(tokens):
                    raise SyntaxError("Unexpected EOF after letrec binding value")

                if tokens[i] != ")":
                    raise SyntaxError("Expected ')' after letrec binding")
                i += 1

                bindings.append((name, value))

            if i >= len(tokens):
                raise SyntaxError("Unexpected EOF after letrec bindings")

            if tokens[i] != ")":
                raise SyntaxError("Expected ')' after letrec bindings")
            i += 1

            # Parse body expressions
            letrec_body = []
            while i < len(tokens) and tokens[i] != ")":
                body_expr, i = parseExpression(tokens, i, in_quasiquote=in_quasiquote)
                letrec_body.append(body_expr)

            if i >= len(tokens):
                raise SyntaxError("Unexpected EOF after letrec body")

            if tokens[i] != ")":
                raise SyntaxError("Expected ')' after letrec body")

            return LetRec(bindings, letrec_body), i + 1

        elif tokens[i] == "define":
            i += 1
            if i >= len(tokens):
                raise SyntaxError("Unexpected EOF after define")

            # Parse name
            name = tokens[i]
            i += 1

            if i >= len(tokens):
                raise SyntaxError("Unexpected EOF after define name")

            # Parse value
            value, i = parseExpression(tokens, i, in_quasiquote=in_quasiquote)

            if i >= len(tokens):
                raise SyntaxError("Unexpected EOF after define value")

            if tokens[i] != ")":
                raise SyntaxError("Expected ')' after define value")

            return DefineExpr(name, value), i + 1

        elif tokens[i] == "defmacro":
            i += 1
            if i >= len(tokens):
                raise SyntaxError("Unexpected EOF after defmacro")

            # Parse name
            name = tokens[i]
            i += 1

            if i >= len(tokens):
                raise SyntaxError("Unexpected EOF after defmacro name")

            # Parse parameters - expect (param1 param2 ...)
            if tokens[i] != "(":
                raise SyntaxError("Expected '(' after defmacro name")
            i += 1

            params = []
            while i < len(tokens) and tokens[i] != ")":
                params.append(tokens[i])
                i += 1

            if i >= len(tokens):
                raise SyntaxError("Unexpected EOF after defmacro params")

            if tokens[i] != ")":
                raise SyntaxError("Expected ')' after defmacro params")
            i += 1

            if i >= len(tokens):
                raise SyntaxError("Unexpected EOF after defmacro params")

            # Parse body (should be a single Expr)
            macro_body, i = parseExpression(tokens, i, in_quasiquote=in_quasiquote)

            if i >= len(tokens):
                raise SyntaxError("Unexpected EOF after defmacro body")

            if tokens[i] != ")":
                raise SyntaxError("Expected ')' after defmacro body")

            return DefMacroExpr(name, params, macro_body), i + 1

        elif tokens[i] == "lambda" and not in_quasiquote:
            i += 1
            if i >= len(tokens):
                raise SyntaxError("Unexpected EOF after lambda")

            # Parse parameter
            param = tokens[i]
            i += 1

            if i >= len(tokens):
                raise SyntaxError("Unexpected EOF after lambda param")

            # Expect dot
            if tokens[i] != ".":
                raise SyntaxError("Expected '.' after lambda param")
            i += 1

            if i >= len(tokens):
                raise SyntaxError("Unexpected EOF after lambda dot")

            # Parse body (should be a single Expr)
            lambda_body, i = parseExpression(tokens, i, in_quasiquote=in_quasiquote)

            if i >= len(tokens):
                raise SyntaxError("Unexpected EOF after lambda body")

            if tokens[i] != ")":
                raise SyntaxError("Expected ')' after lambda body")

            return Abstraction(param, lambda_body), i + 1

        func, i = parseExpression(tokens, i, in_quasiquote=in_quasiquote)
        args = []
        while i < len(tokens) and tokens[i] != ")":
            arg, i = parseExpression(tokens, i, in_quasiquote=in_quasiquote)
            args.append(arg)
        if i >= len(tokens):
            raise SyntaxError("Unexpected EOF: missing ')'")
        return Application(func, args), i + 1

    elif token == "'":
        quoted, i = parseExpression(tokens, i + 1, in_quasiquote=in_quasiquote)
        return QuoteExpr(quoted), i

    elif token.isnumeric():
        return Literal(token), i + 1

    elif token.startswith('"') and token.endswith('"'):
        return Literal(token[1:-1]), i + 1

    elif token == ".":
        return Literal("."), i + 1

    elif re.match(r"^[a-zA-Z0-9_+\-*/=<>!?%_]+$", token):
        return Variable(token), i + 1

    else:
        raise SyntaxError(f"Unexpected token: {token}")


# Parse for a single expr
def lambParse(tokens: List[str]) -> Expr:
    expr, final_i = parseExpression(tokens, 0, in_quasiquote=False)
    if final_i != len(tokens):
        raise SyntaxError("Unexpected extra tokens")
    return expr


# ParseAll for many top-level exprs
def lambParseAll(tokens: List[str]) -> List[Expr]:
    exprs = []
    i = 0
    while i < len(tokens):
        expr, i = parseExpression(tokens, i, in_quasiquote=False)
        exprs.append(expr)
    return exprs
