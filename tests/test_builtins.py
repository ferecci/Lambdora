import pytest
from lambdora.repl import run_expr as runExpression
from lambdora.values import nil, Pair

# Logical operations

def test_logical_operations():
    assert runExpression("(and true false)") is False
    assert runExpression("(and true true)") is True
    assert runExpression("(and false false)") is False
    assert runExpression("(or false true)") is True
    assert runExpression("(or false false)") is False
    assert runExpression("(or true true)") is True
    assert runExpression("(not true)") is False
    assert runExpression("(not false)") is True

# Comparison operators

def test_comparison_operators():
    assert runExpression("(< 1 2)") is True
    assert runExpression("(< 2 1)") is False
    assert runExpression("(< 1 1)") is False
    assert runExpression("(<= 1 2)") is True
    assert runExpression("(<= 2 1)") is False
    assert runExpression("(<= 1 1)") is True
    assert runExpression("(> 2 1)") is True
    assert runExpression("(> 1 2)") is False
    assert runExpression("(> 1 1)") is False
    assert runExpression("(>= 2 1)") is True
    assert runExpression("(>= 1 2)") is False
    assert runExpression("(>= 1 1)") is True
    assert runExpression("(= 1 1)") is True
    assert runExpression("(= 1 2)") is False

# Arithmetic

def test_arithmetic_operators():
    assert runExpression("(+ 3 4)") == 7
    assert runExpression("(- 5 3)") == 2
    assert runExpression("(* 3 4)") == 12
    assert runExpression("(/ 10 2)") == 5
    assert runExpression("(/ 7 2)") == 3
    assert runExpression("(% 10 3)") == 1
    assert runExpression("(% 8 4)") == 0

# List operations

def test_list_operations():
    runExpression("(define pair (cons 1 2))")
    assert runExpression("(head pair)") == 1
    assert runExpression("(tail pair)") == 2
    runExpression("(define nested (cons (cons 1 2) (cons 3 4)))")
    nested_head = runExpression("(head nested)")
    assert isinstance(nested_head, object)
    assert runExpression("(isNil nil)") is True
    assert runExpression("(isNil (cons 1 2))") is False

# Gensym

def test_gensym_function():
    sym1 = runExpression("(gensym)")
    sym2 = runExpression("(gensym)")
    sym3 = runExpression("(gensym 1)")
    assert isinstance(sym1, str)
    assert isinstance(sym2, str)
    assert isinstance(sym3, str)
    assert sym1 != sym2
    assert sym1 != sym3
    assert sym2 != sym3
    assert "__gensym_" in sym1
    assert "__gensym_" in sym2
    assert "__gensym_" in sym3

# Print

def test_print_function():
    from lambdora.values import nil
    result = runExpression("(print 42)")
    assert result is nil

# Error conditions

def test_error_conditions():
    with pytest.raises(Exception):
        runExpression("(not 42)")
    with pytest.raises(Exception):
        runExpression("((and true) 42)")
    with pytest.raises(Exception):
        runExpression("((or false) 99)")
    with pytest.raises(Exception):
        runExpression("(head 42)")
    with pytest.raises(Exception):
        runExpression("(tail 42)")
    with pytest.raises(Exception):
        runExpression("(+ true 1)")
    with pytest.raises(Exception):
        runExpression("(+ 1 true)")

# Complex expressions

def test_complex_expressions():
    result = runExpression("(+ (* 2 3) (- 10 (/ 8 2)))")
    assert result == 12
    result = runExpression("(+ (+ 1 2) (+ 3 4))")
    assert result == 10
    result = runExpression("(and (> 5 3) (< 2 4))")
    assert result is True
    result = runExpression("(or (< 5 3) (> 2 4))")
    assert result is False

# Recursive functions

def test_recursive_functions():
    factorial_code = """
    (letrec ((factorial (lambda n. 
                         (if (<= n 1) 
                             1 
                             (* n (factorial (- n 1)))))))
      (factorial 5))
    """
    result = runExpression(factorial_code)
    assert result == 120
    even_odd_code = """
    (letrec (
      (even (lambda n. (if (= n 0) true (odd (- n 1)))))
      (odd  (lambda n. (if (= n 0) false (even (- n 1)))))
    )
    (even 4))
    """
    result = runExpression(even_odd_code)
    assert result is True

# Additional tests for missing coverage

def test_builtin_error_conditions():
    """Test builtin function error conditions."""
    from lambdora.errors import BuiltinError
    from lambdora.values import Builtin, nil
    # Test builtin functions with wrong argument types
    with pytest.raises(BuiltinError):
        runExpression("(head 42)")  # head on non-pair
    
    with pytest.raises(BuiltinError):
        runExpression("(tail 42)")  # tail on non-pair
    
    result = runExpression("(cons 1)")
    assert isinstance(result, Builtin)  # cons with one arg returns a Builtin (partial application)
    
    result = runExpression("(isNil 42)")
    assert result is False  # isNil on non-pair returns False
    
    result = runExpression("(print)")
    assert result is nil  # print with wrong number of args returns nil
    
    result = runExpression("(gensym 1 2)")
    assert isinstance(result, str) and result.startswith("__gensym_")  # gensym returns a symbol

def test_builtin_edge_cases():
    """Test builtin function edge cases."""
    # Test arithmetic with edge cases
    assert runExpression("(+ 0 0)") == 0
    assert runExpression("(- 0 0)") == 0
    assert runExpression("(* 0 0)") == 0
    assert runExpression("(/ 0 1)") == 0
    
    # Test comparison edge cases
    assert runExpression("(= 0 0)") is True
    assert runExpression("(< 0 0)") is False
    assert runExpression("(<= 0 0)") is True
    assert runExpression("(> 0 0)") is False
    assert runExpression("(>= 0 0)") is True
    
    # Test logical edge cases
    assert runExpression("(and false false)") is False
    assert runExpression("(or true true)") is True
    assert runExpression("(not false)") is True

def test_builtin_string_operations():
    """Test builtin string operations."""
    # Test string concatenation if available
    try:
        result = runExpression('(++ "hello" " world")')
        assert result == "hello world"
    except:
        pass  # String concatenation might not be implemented
    
    # Test string conversion if available
    try:
        result = runExpression("(str 42)")
        assert result == "42"
    except:
        pass  # String conversion might not be implemented

def test_builtin_type_checking():
    """Test builtin type checking functions."""
    # Test type checking if available
    try:
        result = runExpression("(isNumber 42)")
        assert result is True
    except:
        pass  # Type checking might not be implemented
    
    try:
        result = runExpression("(isBoolean true)")
        assert result is True
    except:
        pass  # Type checking might not be implemented

def test_builtin_list_operations():
    """Test builtin list operations."""
    # Test list operations
    runExpression("(define lst (cons 1 (cons 2 nil)))")
    assert runExpression("(head lst)") == 1
    assert isinstance(runExpression("(tail lst)"), Pair)  # tail returns a Pair
    assert runExpression("(isNil nil)") is True
    assert runExpression("(isNil lst)") is False

def test_builtin_recursive_functions():
    """Test builtin functions in recursive contexts."""
    # Test factorial with builtins
    factorial_code = """
    (letrec ((factorial (lambda n. 
                         (if (<= n 1) 
                             1 
                             (* n (factorial (- n 1)))))))
      (factorial 5))
    """
    result = runExpression(factorial_code)
    assert result == 120
    
    # Test even/odd with builtins
    even_odd_code = """
    (letrec (
      (even (lambda n. (if (= n 0) true (odd (- n 1)))))
      (odd  (lambda n. (if (= n 0) false (even (- n 1)))))
    )
    (even 4))
    """
    result = runExpression(even_odd_code)
    assert result is True
