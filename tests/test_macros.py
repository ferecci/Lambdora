from lambdora.main import runExpression, valueToString
from lambdora.macro import lambMacroExpand, lambMacroSubstitute
from lambdora.astmodule import *
from lambdora.values import Macro, nil
import pytest

def test_when_macro():
    runExpression("(defmacro when (cond body) (if cond body nil))")
    assert runExpression("(when true 42)") == 42
    assert runExpression("(when false 42)") is nil

def test_macro_fails_gracefully():
    runExpression("(defmacro noop () nil)")
    assert runExpression("(noop)") is nil

def test_macro_with_two_args():
    runExpression("(defmacro swap (a b) (cons b (cons a nil)))")
    assert valueToString(runExpression("(swap 1 2)")) == "(2 1)"

def test_macro_substitute_variable():
    expr = Variable("x")
    mapping = {"x": Literal("42")}
    result = lambMacroSubstitute(expr, mapping)
    assert isinstance(result, Literal)
    assert result.value == "42"

def test_macro_substitute_deep():
    expr = Application(Variable("f"), [Variable("x"), Literal("10")])
    mapping = {"x": Literal("5")}
    result = lambMacroSubstitute(expr, mapping)
    assert isinstance(result.args[0], Literal)
    assert result.args[0].value == "5"

def test_macro_expand_simple():
    env = {
        "foo": Macro(["a", "b"], Application(Variable("+"), [Variable("a"), Variable("b")]))
    }
    expr = Application(Variable("foo"), [Literal("1"), Literal("2")])
    expanded = lambMacroExpand(expr, env)
    assert isinstance(expanded, Application)
    assert expanded.func.name == "+"
    assert isinstance(expanded.args[0], Literal)
    assert expanded.args[0].value == "1"

def test_macro_expand_nested_args():
    env = {
        "bar": Macro(["x"], Application(Variable("print"), [Variable("x")]))
    }
    expr = Application(Variable("bar"), [Application(Variable("f"), [Literal("3")])])
    result = lambMacroExpand(expr, env)
    assert isinstance(result, Application)
    assert result.func.name == "print"
    assert isinstance(result.args[0], Application)
    assert result.args[0].func.name == "f"

def test_macro_expand_defmacro_registration():
    env = {}
    expr = DefMacroExpr("foo", ["x"], Variable("x"))
    result = lambMacroExpand(expr, env)
    assert result is None
    assert "foo" in env
    assert isinstance(env["foo"], Macro)

def test_macro_expand_nonmacro_application():
    expr = Application(Variable("notAMacro"), [Literal("1")])
    result = lambMacroExpand(expr, {})
    assert isinstance(result, Application)
    assert result.func.name == "notAMacro"

def test_macro_expand_abstraction():
    abs_expr = Abstraction("x", Application(Variable("print"), [Variable("x")]))
    result = lambMacroExpand(abs_expr, {})
    assert isinstance(result, Abstraction)
    assert isinstance(result.body, Application)

def test_gensym_uniqueness():
    a = runExpression("(gensym)")
    b = runExpression("(gensym)")
    assert isinstance(a, str)
    assert a != b
    assert a.startswith("__gensym_")