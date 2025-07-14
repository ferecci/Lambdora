# Interactive REPL

Welcome to the Lambdora REPL (Read-Eval-Print Loop)! This guide covers the interactive environment where you can experiment with the language.

## Starting the REPL

**New CLI command:**
```bash
lambdora repl
```

**Legacy command (still supported):**
```bash
python -m lambdora.repl
```

You should see a prompt like:
```
Lambdora REPL
Type 'exit' or 'quit' to exit, 'help' for help.
λ>
```

## REPL Features

### Multi-line Input
Lambdora's REPL lets you write expressions that span several lines.

* **Automatic** – If you press <kbd>Enter</kbd> while the parentheses are unbalanced the prompt switches to `...` and keeps collecting lines until the form is complete.
* **Manual** – End a line with a backslash (`\`) to force a new continuation line even if the parens already balance (handy when your editor sends *Shift + Enter*).
* **Edit / cancel** while in `...` mode
  * Type `\b` on its own line to delete the previous continuation line.
  * Type `exit` or `quit` to abandon the current multi-line entry and return to `λ>`.

Example:
```lisp
>>> (let x 1 \
...     y 2 \
...     (+ x y))
3
```
Or simply rely on auto-balancing:
```lisp
>>> (define long-fn
...   (lambda n.
...     (if (= n 0)
...         0
...         (+ n (long-fn (- n 1))))))
(lambda n. (if (= n 0) 0 (+ n (long-fn (- n 1)))))
```

### History
- Use up/down arrows to navigate command history
- History is saved between sessions

### Quitting
```lisp
>>> (exit)
```
Or press `Ctrl+C` or `Ctrl+D`.

## Interactive Examples

### Basic Expressions
Start with simple arithmetic:

```lisp
>>> (+ 1 2)
3
>>> (* 3 4)
12
>>> (- 10 3)
7
```

### Variables and Definitions
Define variables and functions:

```lisp
>>> (define x 42)
42
>>> x
42
>>> (define inc (lambda x. (+ x 1)))
(lambda x. (+ x 1))
>>> (inc 5)
6
```

### Lists and Data Structures
Work with lists:

```lisp
>>> (cons 1 (cons 2 nil))
(1 2)
>>> (head (cons 1 (cons 2 nil)))
1
>>> (tail (cons 1 (cons 2 nil)))
(2)
>>> (isNil nil)
true
>>> (isNil (cons 1 nil))
false
```

### Conditionals
Use if expressions:

```lisp
>>> (if (> 5 3) "yes" "no")
"yes"
>>> (if (= 2 3) "equal" "not equal")
"not equal"
```

### Higher-Order Functions
Try the standard library functions:

```lisp
>>> (range 5)
(0 1 2 3 4)
>>> (map (lambda x. (* x 2)) (range 5))
(0 2 4 6 8)
>>> (filter (lambda x. (> x 3)) (range 10))
(4 5 6 7 8 9)
>>> (foldl (lambda acc. (lambda x. (+ acc x))) 0 (range 5))
10
```

### Macros
Experiment with macros:

```lisp
>>> (defmacro when (cond body) `(if ,cond ,body nil))
(lambda cond body. (if cond body nil))
>>> (when true (print "Hello!"))
Hello!
nil
>>> (defmacro let (var val body) `((lambda ,var . ,body) ,val))
(lambda var val body. ((lambda var . body) val))
>>> (let x 42 (print (++ "x is " (str x))))
x is 42
nil
```

### Recursion
Define recursive functions:

```lisp
>>> (letrec ((fact (lambda n.
                     (if (= n 0)
                         1
                         (* n (fact (- n 1)))))))
    (fact 5))
120
```

### Error Handling
See how errors are handled:

```lisp
>>> (+ 1 "hello")
Error: Type error - expected number, got string
>>> (head nil)
Error: Cannot take head of empty list
>>> undefined-variable
Error: Unbound variable: undefined-variable
```

## Interactive Examples

### Fibonacci Sequence
```lisp
>>> (letrec ((fib (lambda n.
                    (if (< n 2)
                        n
                        (+ (fib (- n 1)) (fib (- n 2)))))))
    (map fib (range 10)))
(0 1 1 2 3 5 8 13 21 34)
```

### List Manipulation
```lisp
>>> (define numbers (range 10))
(0 1 2 3 4 5 6 7 8 9)
>>> (filter (lambda x. (= (mod x 2) 0)) numbers)
(0 2 4 6 8)
>>> (map (lambda x. (* x x)) (filter (lambda x. (= (mod x 2) 0)) numbers))
(0 4 16 36 64)
```

### Church Numerals
```lisp
>>> (define zero (lambda f. (lambda x. x)))
(lambda f. (lambda x. x))
>>> (define succ (lambda n. (lambda f. (lambda x. (f ((n f) x))))))
(lambda n. (lambda f. (lambda x. (f ((n f) x)))))
>>> (define churchToNum (lambda n. ((n (lambda x. (+ x 1))) 0)))
(lambda n. ((n (lambda x. (+ x 1))) 0))
>>> (churchToNum zero)
0
>>> (churchToNum (succ zero))
1
>>> (churchToNum (succ (succ zero)))
2
```

## Tips for REPL Usage

### 1. Start Simple
Begin with basic expressions to understand the syntax.

### 2. Use `print` for Side Effects
```lisp
>>> (print "Hello, world!")
Hello, world!
nil
```

### 3. Check Types
```lisp
>>> (isNumber 42)
true
>>> (isList (cons 1 nil))
true
>>> (isFunction (lambda x. x))
true
```

### 4. Experiment with Macros
Macros are powerful - try defining your own control structures.

### 5. Use `let` for Temporary Variables
```lisp
>>> (let x 5 (let y 3 (+ x y)))
8
```

### 6. Explore the Standard Library
```lisp
>>> (fact 5)
120
>>> (fib 8)
21
>>> (sum (range 10))
45
```

## Common Patterns

### Function Composition
```lisp
>>> (define compose (lambda f. (lambda g. (lambda x. (f (g x))))))
(lambda f. (lambda g. (lambda x. (f (g x)))))
>>> (define inc (lambda x. (+ x 1)))
(lambda x. (+ x 1))
>>> (define square (lambda x. (* x x)))
(lambda x. (* x x))
>>> ((compose inc square) 4)
17
```

### Partial Application
```lisp
>>> (define add (lambda x. (lambda y. (+ x y))))
(lambda x. (lambda y. (+ x y)))
>>> (define add5 (add 5))
(lambda y. (+ 5 y))
>>> (add5 3)
8
```

## Next Steps

1. **Try the examples**: Run the example files
2. **Read the API**: Check the [API reference](api.md)
3. **Write your own**: Create your own functions and macros
4. **Explore the source**: Look at the implementation

---

*Happy coding in Lambdora!* 🐑 