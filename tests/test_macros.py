"""Comprehensive tests for macro functionality."""

import pytest

from lambdora.astmodule import *
from lambdora.builtinsmodule import lambMakeTopEnv
from lambdora.errors import MacroExpansionError
from lambdora.macro import lambMacroExpand, lambMacroSubstitute, qqWalk
from lambdora.repl import run_expr as runExpression
from lambdora.values import Macro, Value


def test_basic_macro_definition():
    """Test basic macro definition and usage."""
    # Define a simple macro
    runExpression("(defmacro double (x) (+ x x))")
    result = runExpression("(double 5)")
    assert result == 10

    # Test macro with multiple parameters
    runExpression("(defmacro add3 (x y z) (+ x (+ y z)))")
    result = runExpression("(add3 1 2 3)")
    assert result == 6


def test_macro_expansion_with_variables():
    """Test macro expansion with variable substitution."""
    runExpression("(defmacro testmacro (x) (+ x 1))")
    result = runExpression("(testmacro 5)")
    assert result == 6


def test_macro_edge_cases():
    """Test macro edge cases."""
    # Test macro with wrong number of arguments
    runExpression("(defmacro simple_macro (x) x)")
    with pytest.raises(MacroExpansionError):
        runExpression("(simple_macro 1 2 3)")


def test_macro_expansion_internals():
    """Test macro expansion internal functions."""
    env = {}

    # Test macro expansion with non-variable function
    lit_func = Application(Literal("42"), [])
    result = lambMacroExpand(lit_func, env)
    assert result == lit_func

    # Test macro substitution with simple mapping
    mapping: dict[str, Expr] = {"x": Literal("42")}
    var_x = Variable("x")
    result = lambMacroSubstitute(var_x, mapping)
    assert result == Literal("42")

    # Test macro substitution with complex expressions
    complex_mapping: dict[str, Expr] = {
        "x": Application(Variable("+"), [Literal("1"), Literal("2")])
    }
    var_x = Variable("x")
    result = lambMacroSubstitute(var_x, complex_mapping)
    assert isinstance(result, Application)

    # Test macro substitution with nested structures
    nested_app = Application(Variable("f"), [Variable("x")])
    nested_mapping: dict[str, Expr] = {"x": Literal("42")}
    result = lambMacroSubstitute(nested_app, nested_mapping)
    assert isinstance(result, Application)
    assert result.args[0] == Literal("42")


def test_macro_complex_expansion():
    """Test complex macro expansion scenarios."""
    env = {}

    # Test macro with nested applications
    macro = Macro(
        ["x", "y"], Application(Variable("+"), [Variable("x"), Variable("y")])
    )
    env["test_macro"] = macro

    app = Application(Variable("test_macro"), [Literal("1"), Literal("2")])
    result = lambMacroExpand(app, env)
    assert isinstance(result, Application)

    # Test macro substitution with nested variables
    mapping: dict[str, Expr] = {"x": Variable("y"), "y": Literal("42")}
    var_x = Variable("x")
    result = lambMacroSubstitute(var_x, mapping)
    assert isinstance(result, Variable)


def test_macro_expansion_errors():
    """Test macro expansion error conditions."""
    from lambdora.values import Value

    env: dict[str, Value] = {"m": Macro(["x", "y"], Variable("x"))}
    app = Application(Variable("m"), [Literal("1")])
    with pytest.raises(Exception):
        lambMacroExpand(app, env)


def test_defmacro_expression():
    """Test DefMacroExpr evaluation."""
    env = {}
    expr = DefMacroExpr("foo", ["x"], Variable("x"))
    result = lambMacroExpand(expr, env)
    assert result is None
    assert "foo" in env


def test_nested_macro_expansion():
    """Test nested macro expansion."""
    from lambdora.values import Value

    env: dict[str, Value] = {
        "m": Macro(["x"], Application(Variable("n"), [Variable("x")])),
        "n": Macro(["y"], Variable("y")),
    }
    app = Application(Variable("m"), [Literal("42")])
    result = lambMacroExpand(app, env)
    assert isinstance(result, Literal)


def test_quasiquote_macro_integration():
    """Test quasiquote integration with macros."""
    # Test quasiquote with nested structures
    runExpression("(define x 42)")
    result = runExpression("(quasiquote (list (unquote x) (+ 1 2)))")
    # Should be an application representing the list call
    assert isinstance(result, Application)

    # Test nested quasiquotes
    result = runExpression("(quasiquote (quasiquote (+ 1 2)))")
    assert isinstance(result, QuasiQuoteExpr)


def test_quasiquote_walk():
    """Test quasiquote walk functionality."""
    env = {}
    expr = QuasiQuoteExpr(Literal("42"))
    result = qqWalk(expr.expr, env)
    assert isinstance(result, Literal)


def test_macro_with_quasiquotes():
    """Test macros that use quasiquotes."""
    runExpression("(defmacro double (x) `(+ ,x ,x))")
    result = runExpression("(double 5)")
    assert result == 10


def test_macro_return_value():
    """Test that macro definition returns correct message."""
    result = runExpression("(defmacro testdef (x) x)")
    assert result == "<macro defined>"


def test_macro_with_complex_body():
    """Test macros with complex body expressions."""
    runExpression("(defmacro complex_macro (x y) (if (> x y) x y))")
    result = runExpression("(complex_macro 10 5)")
    assert result == 10
    result = runExpression("(complex_macro 3 7)")
    assert result == 7

# Additional tests for missing coverage

def test_macro_expand_literal():
    """Test macro expansion of literal expressions."""
    env = {}
    lit = Literal("42")
    result = lambMacroExpand(lit, env)
    assert result == lit

def test_macro_expand_variable():
    """Test macro expansion of variable expressions."""
    env = {}
    var = Variable("x")
    result = lambMacroExpand(var, env)
    assert result == var

def test_macro_expand_abstraction():
    """Test macro expansion of abstraction expressions."""
    env = {}
    abs_expr = Abstraction("x", Variable("x"))
    result = lambMacroExpand(abs_expr, env)
    assert result == abs_expr

def test_macro_expand_define():
    """Test macro expansion of define expressions."""
    env = {}
    define_expr = DefineExpr("x", Literal("42"))
    result = lambMacroExpand(define_expr, env)
    assert result == define_expr

def test_macro_expand_if():
    """Test macro expansion of if expressions."""
    env = {}
    if_expr = IfExpr(Literal("true"), Literal("1"), Literal("2"))
    result = lambMacroExpand(if_expr, env)
    assert result == if_expr

def test_macro_expand_quote():
    """Test macro expansion of quote expressions."""
    env = {}
    quote_expr = QuoteExpr(Literal("42"))
    result = lambMacroExpand(quote_expr, env)
    assert result == quote_expr

def test_macro_expand_quasiquote():
    """Test macro expansion of quasiquote expressions."""
    env = {}
    qq_expr = QuasiQuoteExpr(Literal("42"))
    result = lambMacroExpand(qq_expr, env)
    assert isinstance(result, Literal)  # Quasiquote returns the literal

def test_macro_expand_unquote():
    """Test macro expansion of unquote expressions."""
    env = {}
    unq_expr = UnquoteExpr(Literal("42"))
    result = lambMacroExpand(unq_expr, env)
    assert result == unq_expr

def test_macro_substitute_literal():
    """Test macro substitution of literal expressions."""
    mapping: dict[str, Expr] = {"x": Literal("42")}
    lit = Literal("hello")
    result = lambMacroSubstitute(lit, mapping)
    assert result == lit

def test_macro_substitute_abstraction():
    """Test macro substitution of abstraction expressions."""
    mapping: dict[str, Expr] = {"x": Literal("42")}
    abs_expr = Abstraction("y", Variable("y"))
    result = lambMacroSubstitute(abs_expr, mapping)
    assert result == abs_expr

def test_macro_substitute_define():
    """Test macro substitution of define expressions."""
    mapping: dict[str, Expr] = {"x": Literal("42")}
    define_expr = DefineExpr("y", Literal("10"))
    result = lambMacroSubstitute(define_expr, mapping)
    assert result == define_expr

def test_macro_substitute_if():
    """Test macro substitution of if expressions."""
    mapping: dict[str, Expr] = {"x": Literal("42")}
    if_expr = IfExpr(Literal("true"), Literal("1"), Literal("2"))
    result = lambMacroSubstitute(if_expr, mapping)
    assert result == if_expr

def test_macro_substitute_quote():
    """Test macro substitution of quote expressions."""
    mapping: dict[str, Expr] = {"x": Literal("42")}
    quote_expr = QuoteExpr(Literal("10"))
    result = lambMacroSubstitute(quote_expr, mapping)
    assert result == quote_expr

def test_macro_substitute_quasiquote():
    """Test macro substitution of quasiquote expressions."""
    mapping: dict[str, Expr] = {"x": Literal("42")}
    qq_expr = QuasiQuoteExpr(Literal("10"))
    result = lambMacroSubstitute(qq_expr, mapping)
    assert result == qq_expr

def test_macro_substitute_unquote():
    """Test macro substitution of unquote expressions."""
    mapping: dict[str, Expr] = {"x": Literal("42")}
    unq_expr = UnquoteExpr(Literal("10"))
    result = lambMacroSubstitute(unq_expr, mapping)
    assert result == unq_expr

def test_qq_walk_with_variable():
    """Test qqWalk with variable expressions."""
    env = {}
    var = Variable("x")
    result = qqWalk(var, env)
    assert result == var

def test_qq_walk_with_literal():
    """Test qqWalk with literal expressions."""
    env = {}
    lit = Literal("42")
    result = qqWalk(lit, env)
    assert result == lit

def test_qq_walk_with_abstraction():
    """Test qqWalk with abstraction expressions."""
    env = {}
    abs_expr = Abstraction("x", Variable("x"))
    result = qqWalk(abs_expr, env)
    assert result == abs_expr

def test_qq_walk_with_define():
    """Test qqWalk with define expressions."""
    env = {}
    define_expr = DefineExpr("x", Literal("42"))
    result = qqWalk(define_expr, env)
    assert result == define_expr

def test_qq_walk_with_if():
    """Test qqWalk with if expressions."""
    env = {}
    if_expr = IfExpr(Literal("true"), Literal("1"), Literal("2"))
    result = qqWalk(if_expr, env)
    assert result == if_expr

def test_qq_walk_with_quote():
    """Test qqWalk with quote expressions."""
    env = {}
    quote_expr = QuoteExpr(Literal("42"))
    result = qqWalk(quote_expr, env)
    assert result == quote_expr

def test_qq_walk_with_unquote():
    """Test qqWalk with unquote expressions."""
    env = {}
    unq_expr = UnquoteExpr(Literal("42"))
    result = qqWalk(unq_expr, env)
    assert isinstance(result, Literal)  # Unquote returns the literal
