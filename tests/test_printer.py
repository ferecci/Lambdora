"""Comprehensive tests for the printer module."""

import pytest

from lambdora.astmodule import *
from lambdora.printer import lambPrint


def test_basic_printing():
    """Test basic printing of different expression types."""
    # Test literal printing
    lit = Literal("42")
    result = lambPrint(lit)
    assert result == "42"

    # Test variable printing
    var = Variable("x")
    result = lambPrint(var)
    assert result == "x"

    # Test application printing
    app = Application(Variable("+"), [Literal("1"), Literal("2")])
    result = lambPrint(app)
    assert result == "(+ 1 2)"

    # Test abstraction printing
    abs_expr = Abstraction("x", Variable("x"))
    result = lambPrint(abs_expr)
    assert result == "(lambda x. x)"
    assert "lambda" in result
    assert "x" in result


def test_complex_printing():
    """Test printing of complex expressions."""
    # Test nested applications
    nested = Application(
        Variable("+"),
        [
            Application(Variable("*"), [Literal("2"), Literal("3")]),
            Application(Variable("if"), [Literal("true"), Literal("1"), Literal("0")]),
        ],
    )
    result = lambPrint(nested)
    assert "(" in result
    assert "+" in result
    assert "*" in result


def test_letrec_printing():
    """Test LetRec printing."""
    expr = LetRec([("x", Literal("42"))], [Variable("x")])
    result = lambPrint(expr)
    assert "letrec" in result or "x" in result


def test_application_no_args():
    """Test Application with no args."""
    expr = Application(Variable("f"), [])
    result = lambPrint(expr)
    assert result.startswith("(")


def test_define_printing():
    """Test DefineExpr printing."""
    expr = DefineExpr("x", Literal("42"))
    result = lambPrint(expr)
    assert "define" in result
    assert "x" in result


def test_quasiquote_printing():
    """Test QuasiQuoteExpr printing."""
    expr = QuasiQuoteExpr(Literal("42"))
    result = lambPrint(expr)
    assert "quasiquote" in result or "`" in result


def test_defmacro_printing():
    """Test DefMacroExpr printing."""
    expr = DefMacroExpr("test", ["x"], Variable("x"))
    result = lambPrint(expr)
    assert "defmacro" in result
    assert "test" in result

def test_if_printing():
    """Test IfExpr printing."""
    expr = IfExpr(Literal("true"), Literal("1"), Literal("0"))
    result = lambPrint(expr)
    assert "if" in result


def test_quote_printing():
    """Test QuoteExpr printing."""
    expr = QuoteExpr(Literal("42"))
    result = lambPrint(expr)
    assert "quote" in result or "'" in result


def test_unquote_printing():
    """Test UnquoteExpr printing."""
    expr = UnquoteExpr(Literal("42"))
    result = lambPrint(expr)
    assert "unquote" in result or "," in result


def test_nested_structure_printing():
    """Test printing of deeply nested structures."""
    # Create a complex nested expression
    inner_app = Application(Variable("+"), [Literal("1"), Literal("2")])
    outer_app = Application(Variable("print"), [inner_app])
    result = lambPrint(outer_app)
    assert "(" in result
    assert "print" in result
    assert "+" in result


def test_string_literal_printing():
    """Test printing of string literals."""
    lit = Literal('"hello"')
    result = lambPrint(lit)
    assert result == '"hello"'


def test_boolean_literal_printing():
    """Test printing of boolean literals."""
    true_lit = Literal("true")
    false_lit = Literal("false")
    
    true_result = lambPrint(true_lit)
    false_result = lambPrint(false_lit)
    
    assert true_result == "true"
    assert false_result == "false"


def test_nil_printing():
    """Test printing of nil."""
    nil_lit = Literal("nil")
    result = lambPrint(nil_lit)
    assert result == "nil" 