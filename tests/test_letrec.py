import pytest
from lambdora.repl import run_expr as runExpression
from lambdora.errors import RecursionInitError

def test_factorial_letrec():
    src = """
    (letrec ((fact (lambda n. (if (= n 0) 1 (* n (fact (- n 1)))))))
      (fact 5))
    """
    assert runExpression(src.strip()) == 120

def test_mutual_even_odd():
    src = """
    (letrec (
        (even (lambda n. (if (= n 0) true (odd (- n 1)))))
        (odd  (lambda n. (if (= n 0) false (even (- n 1)))))
      )
      (and (even 10) (not (even 11))))
    """
    assert runExpression(src.strip()) is True

def test_single_binding_recursion():
    expr = "(letrec ((fact (lambda n. (if (= n 0) 1 (* n (fact (- n 1))))))) (fact 6))"
    assert runExpression(expr) == 720

def test_placeholder_access_error():
    faulty_src = """
    (letrec (
       (x x))
       x)
    """
    with pytest.raises(RecursionInitError):
        runExpression(faulty_src.strip()) 