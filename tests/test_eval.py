import pytest

from lambdora.repl import run_expr as runExpression


def test_simple_add():
    assert runExpression("(+ 1 2)") == 3


def test_if_expr():
    assert runExpression("(if true 1 2)") == 1
    assert runExpression("(if false 1 2)") == 2


def test_unbound_variable():
    with pytest.raises(NameError):
        runExpression("x")


def test_type_error_on_if():
    with pytest.raises(TypeError):
        runExpression("(if 42 1 2)")


def test_applying_non_function():
    with pytest.raises(TypeError):
        runExpression("(42 1)")


def test_bad_lambda_syntax():
    with pytest.raises(SyntaxError):
        runExpression("(λx x)")


def test_incomplete_expression():
    with pytest.raises(SyntaxError):
        runExpression("(+ 1")


def test_head_on_non_pair():
    with pytest.raises(TypeError):
        runExpression("(head 42)")


def test_deep_tail_fact():
    # Tail-recursive loop function
    runExpression(
        "(define loop "
        "  (λn. (λacc. "
        "    (if (= n 0) acc (loop (- n 1) (* acc n)))"
        "  ))"
        ")"
    )
    # Define fact in terms of loop
    runExpression("(define fact " "  (λn. ((loop n) 1))" ")")
    result = runExpression("(fact 100)")
    assert isinstance(result, int)
    assert result > 0


def test_unknown_expression_type():
    """Test error handling for unknown expression types."""
    from lambdora.builtinsmodule import lambMakeTopEnv
    from lambdora.evaluator import lambEval

    # Create a mock expression type that doesn't exist
    class UnknownExpr:
        pass

    env = lambMakeTopEnv()
    unknown_expr = UnknownExpr()

    with pytest.raises(TypeError, match="Unknown expression type"):
        lambEval(unknown_expr, env)


def test_thunk_evaluation():
    """Test trampoline function with nested thunks."""
    from lambdora.evaluator import trampoline
    from lambdora.values import Thunk

    # Create nested thunks to test the trampoline
    def inner_func():
        return 42

    def outer_func():
        return Thunk(inner_func)

    thunk = Thunk(outer_func)
    result = trampoline(thunk)
    assert result == 42


def test_quasiquote_nested():
    """Test nested quasiquotes."""
    result = runExpression("(quasiquote (quasiquote (+ 1 2)))")
    from lambdora.astmodule import QuasiQuoteExpr

    assert isinstance(result, QuasiQuoteExpr)


def test_quasiquote_with_abstraction():
    """Test quasiquote containing abstractions."""
    result = runExpression("(quasiquote (λx. (+ x 1)))")
    from lambdora.astmodule import Abstraction

    assert isinstance(result, Abstraction)


def test_quasiquote_with_if():
    """Test quasiquote containing if expressions."""
    result = runExpression("(quasiquote (if true 1 2))")
    from lambdora.astmodule import IfExpr

    assert isinstance(result, IfExpr)


def test_quasiquote_with_define():
    """Test quasiquote containing define expressions."""
    result = runExpression("(quasiquote (define x 42))")
    from lambdora.astmodule import DefineExpr

    assert isinstance(result, DefineExpr)


def test_quasiquote_with_defmacro():
    """Test quasiquote containing defmacro expressions."""
    result = runExpression("(quasiquote (defmacro test (x) x))")
    from lambdora.astmodule import DefMacroExpr

    assert isinstance(result, DefMacroExpr)
