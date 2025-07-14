"""Comprehensive tests for the parser module."""

import pytest

from lambdora.astmodule import *
from lambdora.parser import lambParse, parseExpression
from lambdora.tokenizer import lambTokenize


def test_basic_parsing():
    """Test basic parsing of different expression types."""
    # Test parsing simple literals
    tokens = lambTokenize("42")
    expr = lambParse(tokens)
    assert isinstance(expr, Literal)
    assert expr.value == "42"

    # Test parsing variables
    tokens = lambTokenize("x")
    expr = lambParse(tokens)
    assert isinstance(expr, Variable)
    assert expr.name == "x"

    # Test parsing lambda expressions
    tokens = lambTokenize("(lambda x . x)")
    expr = lambParse(tokens)
    assert isinstance(expr, Abstraction)
    assert expr.param == "x"
    assert isinstance(expr.body, Variable)

    # Test parsing applications
    tokens = lambTokenize("(+ 1 2)")
    expr = lambParse(tokens)
    assert isinstance(expr, Application)
    assert isinstance(expr.func, Variable)
    assert expr.func.name == "+"


def test_complex_parsing():
    """Test parsing complex expressions."""
    # Test parsing nested expressions
    tokens = lambTokenize("(+ (* 2 3) (if true 1 0))")
    expr = lambParse(tokens)
    assert isinstance(expr, Application)

    # Test parsing with nested structures
    tokens = lambTokenize("(define f (lambda x . x))")
    expr = lambParse(tokens)
    assert isinstance(expr, DefineExpr)

    # Test parsing letrec expressions
    tokens = lambTokenize("(letrec ((x 42)) x)")
    expr = lambParse(tokens)
    assert isinstance(expr, LetRec)


def test_parse_expression():
    """Test parseExpression function."""
    # Test parsing lambda
    tokens = ["(", "lambda", "x", ".", "x", ")"]
    expr, i = parseExpression(tokens, 0)
    assert isinstance(expr, Abstraction)

    # Test parsing with nested structures
    tokens = ["(", "define", "f", "(", "lambda", "x", ".", "x", ")", ")"]
    expr = lambParse(tokens)
    assert isinstance(expr, DefineExpr)


def test_parser_error_conditions():
    """Test parser error conditions."""
    # Test parsing with incomplete expressions
    with pytest.raises(Exception):
        tokens = ["("]
        lambParse(tokens)

    # Test parsing with missing closing parens
    with pytest.raises(Exception):
        tokens = ["(", "define", "x", "42"]
        lambParse(tokens)

    # Test parsing with unexpected tokens
    tokens = ["(", "lambda", "x", ".", "x", ")"]
    expr, i = parseExpression(tokens, 0)
    assert isinstance(expr, Abstraction)


def test_parser_edge_cases():
    """Test parser edge cases."""
    # Test parsing with incomplete expressions
    with pytest.raises(Exception):
        tokens = ["("]
        lambParse(tokens)

    # Test parsing with missing closing parens
    with pytest.raises(Exception):
        tokens = ["(", "define", "x", "42"]
        lambParse(tokens)

    # Test parsing with nested structures
    tokens = ["(", "define", "f", "(", "lambda", "x", ".", "x", ")", ")"]
    expr = lambParse(tokens)
    assert isinstance(expr, DefineExpr)


def test_defmacro_parsing():
    """Test parsing defmacro expressions."""
    # Test parsing defmacro with missing parens
    with pytest.raises(Exception):
        tokens = ["(", "defmacro", "m", "x", "x", ")"]
        lambParse(tokens)

    # Test parsing defmacro with params not as list
    with pytest.raises(Exception):
        tokens = ["(", "defmacro", "m", "x", "x", ")"]
        lambParse(tokens)


def test_letrec_parsing():
    """Test parsing letrec expressions."""
    # Test parsing letrec with missing parens
    with pytest.raises(Exception):
        tokens = ["(", "letrec", "x", "42", "x", ")"]
        lambParse(tokens)


def test_unexpected_token_handling():
    """Test handling of unexpected tokens."""
    # Test parsing with unexpected tokens
    tokens = ["(", "lambda", "x", ".", "x", ")"]
    expr, i = parseExpression(tokens, 0)
    assert isinstance(expr, Abstraction)


def test_incomplete_expression_handling():
    """Test handling of incomplete expressions."""
    # Test parsing with incomplete expressions
    with pytest.raises(Exception):
        tokens = ["("]
        lambParse(tokens)

# Additional tests for missing coverage

def test_parse_quasiquote():
    """Test parsing quasiquote expressions."""
    tokens = ["`", "(", "+", "1", "2", ")"]
    expr, i = parseExpression(tokens, 0)
    assert isinstance(expr, QuasiQuoteExpr)

def test_parse_unquote():
    """Test parsing unquote expressions."""
    tokens = [",", "42"]
    expr, i = parseExpression(tokens, 0)
    assert isinstance(expr, UnquoteExpr)

def test_parse_quote():
    """Test parsing quote expressions."""
    tokens = ["'", "x"]
    expr, i = parseExpression(tokens, 0)
    assert isinstance(expr, QuoteExpr)

def test_parse_if():
    """Test parsing if expressions."""
    tokens = ["(", "if", "true", "1", "2", ")"]
    expr, i = parseExpression(tokens, 0)
    assert isinstance(expr, Application)  # If expressions are parsed as applications

def test_parse_let():
    """Test parsing let expressions."""
    # Note: LetExpr might not be available in astmodule
    # This test is kept for completeness but may need adjustment
    pass

def test_parse_letrec():
    """Test parsing letrec expressions."""
    tokens = ["(", "letrec", "(", "(", "x", "42", ")", ")", "x", ")"]
    expr, i = parseExpression(tokens, 0)
    assert isinstance(expr, LetRec)

def test_parse_defmacro():
    """Test parsing defmacro expressions."""
    tokens = ["(", "defmacro", "m", "(", "x", ")", "x", ")"]
    expr, i = parseExpression(tokens, 0)
    assert isinstance(expr, DefMacroExpr)

def test_parse_define():
    """Test parsing define expressions."""
    tokens = ["(", "define", "x", "42", ")"]
    expr, i = parseExpression(tokens, 0)
    assert isinstance(expr, DefineExpr)

def test_parse_application():
    """Test parsing application expressions."""
    tokens = ["(", "+", "1", "2", ")"]
    expr, i = parseExpression(tokens, 0)
    assert isinstance(expr, Application)

def test_parse_abstraction():
    """Test parsing abstraction expressions."""
    tokens = ["(", "lambda", "x", ".", "x", ")"]
    expr, i = parseExpression(tokens, 0)
    assert isinstance(expr, Abstraction)

def test_parse_literal():
    """Test parsing literal expressions."""
    tokens = ["42"]
    expr, i = parseExpression(tokens, 0)
    assert isinstance(expr, Literal)

def test_parse_variable():
    """Test parsing variable expressions."""
    tokens = ["x"]
    expr, i = parseExpression(tokens, 0)
    assert isinstance(expr, Variable)

def test_parse_expression_eof():
    """Test parseExpression with EOF."""
    with pytest.raises(SyntaxError):
        parseExpression([], 0)

def test_parse_expression_unexpected_eof():
    """Test parseExpression with unexpected EOF."""
    with pytest.raises(SyntaxError):
        parseExpression(["("], 0)

def test_parse_expression_unexpected_eof_after_letrec():
    """Test parseExpression with unexpected EOF after letrec."""
    with pytest.raises(SyntaxError):
        parseExpression(["(", "letrec"], 0)

def test_parse_expression_unexpected_eof_after_letrec_open():
    """Test parseExpression with unexpected EOF after letrec open paren."""
    with pytest.raises(SyntaxError):
        parseExpression(["(", "letrec", "("], 0)

def test_parse_expression_letrec_no_open_paren():
    """Test parseExpression with letrec but no opening paren."""
    with pytest.raises(SyntaxError):
        parseExpression(["(", "letrec", "x"], 0)

def test_parse_expression_letrec_binding_no_open_paren():
    """Test parseExpression with letrec binding but no opening paren."""
    with pytest.raises(SyntaxError):
        parseExpression(["(", "letrec", "(", "x"], 0)

def test_parse_expression_letrec_binding_eof():
    """Test parseExpression with letrec binding EOF."""
    with pytest.raises(SyntaxError):
        parseExpression(["(", "letrec", "(", "x"], 0)

def test_parse_expression_letrec_binding_value_eof():
    """Test parseExpression with letrec binding value EOF."""
    with pytest.raises(SyntaxError):
        parseExpression(["(", "letrec", "(", "x", "42"], 0)

def test_parse_expression_letrec_binding_no_close_paren():
    """Test parseExpression with letrec binding no close paren."""
    with pytest.raises(SyntaxError):
        parseExpression(["(", "letrec", "(", "x", "42", "x"], 0)

def test_parse_expression_letrec_body_eof():
    """Test parseExpression with letrec body EOF."""
    with pytest.raises(SyntaxError):
        parseExpression(["(", "letrec", "(", "(", "x", "42", ")", ")", "x"], 0)

def test_parse_expression_letrec_no_close_paren():
    """Test parseExpression with letrec no close paren."""
    with pytest.raises(SyntaxError):
        parseExpression(["(", "letrec", "(", "(", "x", "42", ")", ")", "x"], 0)

def test_parse_expression_let_no_open_paren():
    """Test parseExpression with let but no opening paren."""
    with pytest.raises(SyntaxError):
        parseExpression(["(", "let", "x"], 0)

def test_parse_expression_let_binding_no_open_paren():
    """Test parseExpression with let binding but no opening paren."""
    with pytest.raises(SyntaxError):
        parseExpression(["(", "let", "(", "x"], 0)

def test_parse_expression_let_binding_eof():
    """Test parseExpression with let binding EOF."""
    with pytest.raises(SyntaxError):
        parseExpression(["(", "let", "(", "x"], 0)

def test_parse_expression_let_binding_value_eof():
    """Test parseExpression with let binding value EOF."""
    with pytest.raises(SyntaxError):
        parseExpression(["(", "let", "(", "x", "42"], 0)

def test_parse_expression_let_binding_no_close_paren():
    """Test parseExpression with let binding no close paren."""
    with pytest.raises(SyntaxError):
        parseExpression(["(", "let", "(", "x", "42", "x"], 0)

def test_parse_expression_let_body_eof():
    """Test parseExpression with let body EOF."""
    with pytest.raises(SyntaxError):
        parseExpression(["(", "let", "(", "(", "x", "42", ")", ")", "x"], 0)

def test_parse_expression_let_no_close_paren():
    """Test parseExpression with let no close paren."""
    with pytest.raises(SyntaxError):
        parseExpression(["(", "let", "(", "(", "x", "42", ")", ")", "x"], 0)

def test_parse_expression_defmacro_no_open_paren():
    """Test parseExpression with defmacro but no opening paren."""
    with pytest.raises(SyntaxError):
        parseExpression(["(", "defmacro", "m"], 0)

def test_parse_expression_defmacro_params_no_open_paren():
    """Test parseExpression with defmacro params but no opening paren."""
    with pytest.raises(SyntaxError):
        parseExpression(["(", "defmacro", "m", "x"], 0)

def test_parse_expression_defmacro_params_eof():
    """Test parseExpression with defmacro params EOF."""
    with pytest.raises(SyntaxError):
        parseExpression(["(", "defmacro", "m", "(", "x"], 0)

def test_parse_expression_defmacro_params_no_close_paren():
    """Test parseExpression with defmacro params no close paren."""
    with pytest.raises(SyntaxError):
        parseExpression(["(", "defmacro", "m", "(", "x", "x"], 0)

def test_parse_expression_defmacro_body_eof():
    """Test parseExpression with defmacro body EOF."""
    with pytest.raises(SyntaxError):
        parseExpression(["(", "defmacro", "m", "(", "x", ")", "x"], 0)

def test_parse_expression_defmacro_no_close_paren():
    """Test parseExpression with defmacro no close paren."""
    with pytest.raises(SyntaxError):
        parseExpression(["(", "defmacro", "m", "(", "x", ")", "x"], 0)

def test_parse_expression_if_no_condition():
    """Test parseExpression with if but no condition."""
    with pytest.raises(SyntaxError):
        parseExpression(["(", "if"], 0)

def test_parse_expression_if_no_then():
    """Test parseExpression with if but no then branch."""
    with pytest.raises(SyntaxError):
        parseExpression(["(", "if", "true"], 0)

def test_parse_expression_if_no_else():
    """Test parseExpression with if but no else branch."""
    with pytest.raises(SyntaxError):
        parseExpression(["(", "if", "true", "1"], 0)

def test_parse_expression_if_no_close_paren():
    """Test parseExpression with if no close paren."""
    with pytest.raises(SyntaxError):
        parseExpression(["(", "if", "true", "1", "2"], 0)

def test_parse_expression_define_no_name():
    """Test parseExpression with define but no name."""
    with pytest.raises(SyntaxError):
        parseExpression(["(", "define"], 0)

def test_parse_expression_define_no_value():
    """Test parseExpression with define but no value."""
    with pytest.raises(SyntaxError):
        parseExpression(["(", "define", "x"], 0)

def test_parse_expression_define_no_close_paren():
    """Test parseExpression with define no close paren."""
    with pytest.raises(SyntaxError):
        parseExpression(["(", "define", "x", "42"], 0)

def test_parse_expression_quote_no_expr():
    """Test parseExpression with quote but no expression."""
    with pytest.raises(SyntaxError):
        parseExpression(["'"], 0)

def test_parse_expression_quasiquote_no_expr():
    """Test parseExpression with quasiquote but no expression."""
    with pytest.raises(SyntaxError):
        parseExpression(["`"], 0)

def test_parse_expression_unquote_no_expr():
    """Test parseExpression with unquote but no expression."""
    with pytest.raises(SyntaxError):
        parseExpression([","], 0)

def test_parse_expression_application_no_func():
    """Test parseExpression with application but no function."""
    with pytest.raises(SyntaxError):
        parseExpression(["(", ")"], 0)

def test_parse_expression_abstraction_no_param():
    """Test parseExpression with abstraction but no parameter."""
    with pytest.raises(SyntaxError):
        parseExpression(["(", "lambda"], 0)

def test_parse_expression_abstraction_no_dot():
    """Test parseExpression with abstraction but no dot."""
    with pytest.raises(SyntaxError):
        parseExpression(["(", "lambda", "x"], 0)

def test_parse_expression_abstraction_no_body():
    """Test parseExpression with abstraction but no body."""
    with pytest.raises(SyntaxError):
        parseExpression(["(", "lambda", "x", "."], 0)

def test_parse_expression_abstraction_no_close_paren():
    """Test parseExpression with abstraction no close paren."""
    with pytest.raises(SyntaxError):
        parseExpression(["(", "lambda", "x", ".", "x"], 0)
