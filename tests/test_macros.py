from main import runExpression
from values import nil

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