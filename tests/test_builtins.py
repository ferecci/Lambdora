import pytest
from main import runExpression

def test_not_type_error():
    with pytest.raises(TypeError):
        runExpression("(not 42)")

def test_and_type_error():
    with pytest.raises(TypeError):
        runExpression("((and true) 42)")

def test_or_type_error():
    with pytest.raises(TypeError):
        runExpression("((or false) 99)")