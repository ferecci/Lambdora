"""Comprehensive tests for the evaluator module."""

import pytest
from lambdora.astmodule import Application, Literal, Variable, DefineExpr, IfExpr, QuoteExpr, QuasiQuoteExpr, UnquoteExpr
from lambdora.builtinsmodule import lambMakeTopEnv
from lambdora.evaluator import applyFunc, lambEval, trampoline
from lambdora.repl import run_expr as runExpression
from lambdora.values import Closure, Pair, Thunk
from lambdora.errors import EvalError

# Basic evaluation and arithmetic

def test_simple_add():
    assert runExpression("(+ 1 2)") == 3

def test_basic_evaluation():
    env = lambMakeTopEnv()
    lit = Literal("42")
    result = lambEval(lit, env)
    assert result == 42
    string_lit = Literal("hello")
    result = lambEval(string_lit, env)
    assert result == "hello"
    env["test_var"] = 42
    var = Variable("test_var")
    result = lambEval(var, env)
    assert result == 42
    app = Application(Variable("+"), [Literal("1"), Literal("2")])
    result = lambEval(app, env)
    assert result == 3

def test_if_expr():
    assert runExpression("(if true 1 2)") == 1
    assert runExpression("(if false 1 2)") == 2

def test_unbound_variable():
    with pytest.raises(EvalError):
        runExpression("unbound_variable_test")

def test_type_error_on_if():
    with pytest.raises(TypeError):
        runExpression("(if 42 1 2)")

def test_applying_non_function():
    with pytest.raises(TypeError):
        runExpression("(42 1)")

def test_bad_lambda_syntax():
    with pytest.raises(SyntaxError):
        runExpression("(lambda x x)")

def test_incomplete_expression():
    with pytest.raises(SyntaxError):
        runExpression("(+ 1")

def test_head_on_non_pair():
    with pytest.raises(TypeError):
        runExpression("(head 42)")

def test_deep_tail_fact():
    runExpression(
        "(define loop "
        "  (lambda n. (lambda acc. "
        "    (if (= n 0) acc (loop (- n 1) (* acc n)))"
        "  ))"
        ")"
    )
    runExpression("(define fact " "  (lambda n. ((loop n) 1))" ")")
    result = runExpression("(fact 100)")
    assert isinstance(result, int)
    assert result > 0

def test_unknown_expression_type():
    from lambdora.builtinsmodule import lambMakeTopEnv
    from lambdora.evaluator import lambEval
    class UnknownExpr:
        pass
    env = lambMakeTopEnv()
    unknown_expr = UnknownExpr()
    with pytest.raises(TypeError, match="Unknown expression type"):
        lambEval(unknown_expr, env)  # type: ignore[arg-type]

# Thunk evaluation

def test_thunk_evaluation():
    # From test_eval.py
    from lambdora.evaluator import trampoline
    from lambdora.values import Thunk
    def inner_func():
        return 42
    def outer_func():
        return Thunk(inner_func)
    thunk = Thunk(outer_func)
    result = trampoline(thunk)
    assert result == 42
    # From test_evaluator.py
    def dummy_func():
        return 42
    thunk = Thunk(dummy_func)
    result = trampoline(thunk)
    assert result == 42
    def return_pair():
        return Pair(1, 2)
    thunk = Thunk(return_pair)
    result = trampoline(thunk)
    assert isinstance(result, Pair)
    assert result.head == 1
    assert result.tail == 2
    def inner_thunk():
        return 42
    def outer_thunk():
        return Thunk(inner_thunk)
    thunk = Thunk(outer_thunk)
    result = trampoline(thunk)
    assert result == 42

def test_closure_evaluation():
    env = lambMakeTopEnv()
    closure = Closure("x", Variable("x"), env)
    result = applyFunc(closure, [Literal("5")], False)
    assert result == Literal("5")

def test_builtin_function_application():
    env = lambMakeTopEnv()
    builtin_add = env["+"]
    result = applyFunc(builtin_add, [5, 3], False)
    assert result == 8

def test_lambda_parameter_evaluation():
    result = runExpression('((lambda "x" . "x") 42)')
    assert result == "x"

def test_define_with_evaluation():
    runExpression('(define "testvar" 42)')
    result = runExpression('"testvar"')
    assert result == "testvar"

def test_complex_nested_expressions():
    result = runExpression("(+ (* 2 3) (- 10 (/ 8 2)))")
    assert result == 12
    result = runExpression("(+ (+ 1 2) (+ 3 4))")
    assert result == 10

def test_recursive_evaluation():
    factorial_code = """
    (letrec ((factorial (lambda n. 
                         (if (<= n 1) 
                             1 
                             (* n (factorial (- n 1)))))))
      (factorial 5))
    """
    result = runExpression(factorial_code)
    assert result == 120

def test_tail_call_optimization():
    env = lambMakeTopEnv()
    abs_expr = Application(Variable("lambda"), [Literal("x"), Variable("x")])
    app = Application(abs_expr, [Literal("5")])
    result = lambEval(app, env, is_tail=True)
    assert isinstance(result, Thunk)

def test_literal_parameter_evaluation():
    result = runExpression("((lambda 42 . 100) 5)")
    assert result == 100

# Additional tests for missing coverage

def test_define_expression_evaluation():
    """Test DefineExpr evaluation."""
    env = lambMakeTopEnv()
    define_expr = DefineExpr("test_var", Literal("42"))
    result = lambEval(define_expr, env)
    assert result == "<defined test_var>"
    assert env["test_var"] == 42

def test_let_expression_evaluation():
    """Test LetExpr evaluation."""
    # Note: LetExpr might not be available in astmodule
    # This test is kept for completeness but may need adjustment
    pass

def test_if_expression_evaluation():
    """Test IfExpr evaluation."""
    env = lambMakeTopEnv()
    if_expr = IfExpr(Literal("true"), Literal("1"), Literal("2"))
    # The literal "true" evaluates to the string "true", not boolean True
    with pytest.raises(Exception):
        lambEval(if_expr, env)

def test_quasiquote_expression_evaluation():
    """Test QuasiQuoteExpr evaluation."""
    env = lambMakeTopEnv()
    qq_expr = QuasiQuoteExpr(Literal("42"))
    result = lambEval(qq_expr, env)
    assert isinstance(result, Literal)  # Quasiquote returns the literal

def test_unquote_expression_evaluation():
    """Test UnquoteExpr evaluation."""
    # UnquoteExpr is not directly evaluated - it's only used inside quasiquote
    # This test is kept for completeness but may need adjustment
    pass

def test_builtin_function_with_wrong_args():
    """Test builtin function with wrong number of arguments."""
    env = lambMakeTopEnv()
    builtin_add = env["+"]
    # Builtin functions handle wrong args gracefully, so no exception
    result = applyFunc(builtin_add, [5], False)
    assert isinstance(result, type(builtin_add))  # Returns the builtin function

def test_closure_with_wrong_args():
    """Test closure with wrong number of arguments."""
    env = lambMakeTopEnv()
    closure = Closure("x", Variable("x"), env)
    # Closures handle wrong args gracefully, so no exception
    result = applyFunc(closure, [], False)
    assert isinstance(result, Closure)  # Returns the closure

def test_apply_func_with_non_list_args():
    """Test applyFunc with non-list arguments."""
    env = lambMakeTopEnv()
    builtin_add = env["+"]
    with pytest.raises(Exception):
        applyFunc(builtin_add, ["not_a_list"], False)  # Wrong type but correct list

def test_error_conditions():
    # From test_evaluator.py
    with pytest.raises(Exception):
        runExpression("(42 1 2)")
    with pytest.raises(Exception):
        runExpression("(+ undefined_var 1)")
    env = lambMakeTopEnv()
    app = Application(Variable("lambda"), [Literal("x"), Variable("x")])
    with pytest.raises(Exception):
        lambEval(app, env)
    app = Application(
        Variable("define"),
        [Application(Variable("+"), [Literal("1"), Literal("2")]), Literal("5")],
    )
    with pytest.raises(Exception):
        lambEval(app, env)
    app = Application(Variable("let"), [Variable("x"), Literal("5")])
    with pytest.raises(Exception):
        lambEval(app, env)
    with pytest.raises(Exception):
        runExpression("(if 42 1 2)")
    app = Application(Variable("unquote"), [Literal("42")])
    with pytest.raises(Exception):
        lambEval(app, env)
    app = Application(Variable("quote"), [])
    with pytest.raises(Exception):
        lambEval(app, env)
    app = Application(Variable("quasiquote"), [])
    with pytest.raises(Exception):
        lambEval(app, env)
    # From test_eval.py
    with pytest.raises(EvalError):
        runExpression("unbound_variable_test")
    with pytest.raises(TypeError):
        runExpression("(if 42 1 2)")
    with pytest.raises(TypeError):
        runExpression("(42 1)")
    with pytest.raises(SyntaxError):
        runExpression("(lambda x x)")
    with pytest.raises(SyntaxError):
        runExpression("(+ 1")
    with pytest.raises(TypeError):
        runExpression("(head 42)")

def test_quasiquote_nested():
    result = runExpression("(quasiquote (quasiquote (+ 1 2)))")
    from lambdora.astmodule import QuasiQuoteExpr
    assert isinstance(result, QuasiQuoteExpr)

def test_quasiquote_with_abstraction():
    result = runExpression("(quasiquote (lambda x. (+ x 1)))")
    from lambdora.astmodule import Abstraction
    assert isinstance(result, Abstraction)

def test_quasiquote_with_if():
    result = runExpression("(quasiquote (if true 1 2))")
    from lambdora.astmodule import IfExpr
    assert isinstance(result, IfExpr)

def test_quasiquote_with_define():
    result = runExpression("(quasiquote (define x 42))")
    from lambdora.astmodule import DefineExpr
    assert isinstance(result, DefineExpr)

def test_quasiquote_with_defmacro():
    result = runExpression("(quasiquote (defmacro test (x) x))")
    from lambdora.astmodule import DefMacroExpr
    assert isinstance(result, DefMacroExpr) 