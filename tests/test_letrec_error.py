import pytest

from lambdora.errors import RecursionInitError
from lambdora.repl import run_expr as runExpression


def test_placeholder_access_error():
    faulty_src = """
    (letrec (
       (x x))
       x)
    """
    with pytest.raises(RecursionInitError):
        runExpression(faulty_src.strip())
