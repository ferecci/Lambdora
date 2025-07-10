from lambdora.repl import run_expr as runExpression
from lambdora.values import nil, valueToString


def test_list_sum():
    # sum (range 5) = 0 + 1 + 2 + 3 + 4
    assert runExpression("(sum (range 5))") == 10


def test_range_and_sum():
    assert runExpression("(sum (range 5))") == 10


def test_map_double():
    runExpression("(define double (lambda x. (* 2 x)))")
    assert valueToString(runExpression("(map double (range 4))")) == "(0 2 4 6)"


def test_filter_even():
    runExpression("(define even (lambda x. (= 0 (% x 2))))")
    assert valueToString(runExpression("(filter even (range 6))")) == "(0 2 4)"


def test_foldl_sum():
    runExpression("(define add (lambda x. (lambda y. (+ x y))))")
    assert runExpression("(foldl add 0 (range 4))") == 6


def test_reverse():
    assert valueToString(runExpression("(reverse (range 4))")) == "(3 2 1 0)"


def test_isZero():
    assert runExpression("(isZero 0)") is True
    assert runExpression("(isZero 1)") is False


def test_factorial_tail():
    assert runExpression("(fact 5)") == 120


def test_fibonacci():
    assert runExpression("(fib 7)") == 13


def test_fizzbuzz_sample():
    runExpression(
        """
    (define fizzbuzz
      (lambda n.
        (if (= (% n 15) 0) "FizzBuzz"
          (if (= (% n 3) 0) "Fizz"
            (if (= (% n 5) 0) "Buzz" n)))))
    """
    )
    assert runExpression("(fizzbuzz 3)") == "Fizz"
    assert runExpression("(fizzbuzz 5)") == "Buzz"
    assert runExpression("(fizzbuzz 15)") == "FizzBuzz"
    assert runExpression("(fizzbuzz 7)") == 7


def test_when_macro():
    assert runExpression("(when true 42)") == 42
    assert runExpression("(when false 42)") is nil


def test_unless_macro():
    assert runExpression("(unless false 42)") == 42
    assert runExpression("(unless true 42)") is nil


def test_let_macro():
    assert runExpression("(let x 10 (+ x 2))") == 12


def test_and_or_macros():
    assert runExpression("(and2 true true)") is True
    assert runExpression("(and2 false true)") is False
    assert runExpression("(or2 false true)") is True
    assert runExpression("(or2 false false)") is False
