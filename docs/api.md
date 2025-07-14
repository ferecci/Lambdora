# API Reference

This document provides a comprehensive reference for Lambdora's built-in functions, standard library, and language constructs.

## Built-in Functions

### Arithmetic
- `(+ a b)`: Addition
- `(- a b)`: Subtraction  
- `(* a b)`: Multiplication
- `(/ a b)`: Division
- `(mod a b)`: Modulo (can also use %)
- `(< a b)`: Less than
- `(<= a b)`: Less than or equal
- `(> a b)`: Greater than
- `(>= a b)`: Greater than or equal
- `(= a b)`: Equality
- `(!= a b)`: Inequality

### Logic
- `(and a b)`: Logical AND
- `(or a b)`: Logical OR
- `(not x)`: Logical NOT

### Lists
- `(cons head tail)`: Create pair/list
- `(head list)`: Get first element
- `(tail list)`: Get rest of list
- `(isNil x)`: Check if nil/empty list

### I/O
- `(print expr)`: Print expression (accepts any value, converts to string)
- `(str expr)`: Convert to string
- `(++ str1 str2)`: String concatenation

### Type Checking
- `(isNumber x)`: Check if number
- `(isBoolean x)`: Check if boolean
- `(isString x)`: Check if string
- `(isList x)`: Check if list
- `(isFunction x)`: Check if function

### Macro System
- `(gensym _)`: Generate unique symbol for hygienic macros
- `(quote expr)`: Quote expression (prevent evaluation)
- `(quasiquote expr)`: Quasiquote with unquote support
- `(unquote expr)`: Unquote (only inside quasiquote)

## Standard Library

### List Operations

#### `map`
```lisp
(map function list)
```
Apply function to each element of list.

```lisp
(map (lambda x. (* x 2)) (range 5))
; => (0 2 4 6 8)
```

#### `filter`
```lisp
(filter predicate list)
```
Keep elements that satisfy predicate.

```lisp
(filter (lambda x. (> x 3)) (range 10))
; => (4 5 6 7 8 9)
```

#### `foldl`
```lisp
(foldl function initial list)
```
Left fold (reduce) with function.

```lisp
(foldl (lambda acc. (lambda x. (+ acc x))) 0 (range 5))
; => 10
```

#### `foldr`
```lisp
(foldr function initial list)
```
Right fold with function.

```lisp
(foldr (lambda x. (lambda acc. (cons x acc))) nil (range 3))
; => (0 1 2)
```

#### `length`
```lisp
(length list)
```
Get length of list.

```lisp
(length (range 10))
; => 10
```

#### `sum`
```lisp
(sum list)
```
Sum all numbers in list.

```lisp
(sum (range 5))
; => 10
```

#### `reverse`
```lisp
(reverse list)
```
Reverse list.

```lisp
(reverse (range 3))
; => (2 1 0)
```

#### `append`
```lisp
(append list1 list2)
```
Concatenate two lists.

```lisp
(append (range 3) (range 3))
; => (0 1 2 0 1 2)
```

### List Generation

#### `range`
```lisp
(range n)
```
Generate list 0 to n-1.

```lisp
(range 5)
; => (0 1 2 3 4)
```

#### `ones`
```lisp
(ones n)
```
Generate list of n ones.

```lisp
(ones 3)
; => (1 1 1)
```

### Mathematical

#### `fact`
```lisp
(fact n)
```
Factorial of n.

```lisp
(fact 5)
; => 120
```

#### `fib`
```lisp
(fib n)
```
Fibonacci number at position n.

```lisp
(fib 8)
; => 21
```

#### `double`
```lisp
(double x)
```
Double a number.

```lisp
(double 7)
; => 14
```

#### `triple`
```lisp
(triple x)
```
Triple a number.

```lisp
(triple 3)
; => 9
```

### Control Flow Macros

#### `when`
```lisp
(when condition body)
```
Execute body if condition is true.

```lisp
(when (> 5 3) (print "Five is greater than three"))
```

#### `unless`
```lisp
(unless condition body)
```
Execute body if condition is false.

```lisp
(unless (= 2 3) (print "Two is not three"))
```

#### `begin`
```lisp
(begin expr1 expr2)
```
Execute expressions in sequence.

```lisp
(begin (print "First") (print "Second"))
```

#### `let`
```lisp
(let variable value body)
```
Bind variable to value in body.

```lisp
(let x 42 (print (++ "x is " (str x))))
; => x is 42
```

#### `cond`
```lisp
(cond test1 result1 test2 result2)
```
Two-branch conditional.

```lisp
(cond (= x 0) "zero"
      (= x 1) "one"
      true     "other")
```

### Logic Macros

#### `and2`
```lisp
(and2 a b)
```
Short-circuit AND.

```lisp
(and2 true (print "evaluated"))
```

#### `or2`
```lisp
(or2 a b)
```
Short-circuit OR.

```lisp
(or2 false (print "evaluated"))
```

## Language Constructs

### Function Definition
```lisp
(define name (lambda params. body))
```
Define a function.

```lisp
(define inc (lambda x. (+ x 1)))
```

### Anonymous Functions
```lisp
(lambda params. body)
```
Create anonymous function.

```lisp
((lambda x. (* x x)) 4)
; => 16
```

### Recursive Definitions
```lisp
(letrec ((name (lambda params. body))) expr)
```
Define recursive function.

```lisp
(letrec ((fact (lambda n.
                 (if (= n 0)
                     1
                     (* n (fact (- n 1)))))))
  (fact 5))
```

### Conditionals
```lisp
(if condition then-expr else-expr)
```
Conditional expression.

```lisp
(if (> 5 3) "yes" "no")
; => "yes"
```

### Macros
```lisp
(defmacro name (params) template)
```
Define a macro.

```lisp
(defmacro when (cond body)
  `(if ,cond ,body nil))
```

## Quoting and Quasiquoting

### Quote
```lisp
'expression
```
Quote expression (prevent evaluation).

```lisp
'(+ 1 2)  ; => (+ 1 2) (unevaluated)
```

### Quasiquote
```lisp
`expression
```
Quasiquote with unquote support.

```lisp
(define x 5)
`(+ 1 ,x)  ; => (+ 1 5)
```

### Unquote
```lisp
,expression
```
Unquote (only inside quasiquote).

```lisp
(define y 10)
`(list ,y ,(+ y 1))  ; => (list 10 11)
```

## Macro System

### Gensym
```lisp
(gensym)
```
Generate unique symbol for hygienic macros.

```lisp
(gensym)  ; => __gensym_0
(gensym)  ; => __gensym_1
```

### Hygienic Macros
Macros automatically use gensym to prevent variable capture:

```lisp
(defmacro safe-let (var val body)
  `((lambda ,var . ,body) ,val))

; This works correctly even if 'x' is used in 'val'
(safe-let x 5 (+ x 1))  ; => 6
```

## Data Types

### Numbers
- Integers: `42`, `-17`, `0`
- Arithmetic: `+`, `-`, `*`, `/`, `mod`
- Comparison: `<`, `<=`, `>`, `>=`, `=`, `!=`

### Booleans
- Values: `true`, `false`
- Logic: `and`, `or`, `not`

### Strings
- Literals: `"Hello, world!"`
- Conversion: `str`

### Lists
- Constructor: `cons`
- Accessors: `head`, `tail`
- Empty list: `nil`
- Predicate: `isNil`

### Functions
- First-class values
- Can be passed as arguments
- Can be returned from functions
- Support currying

## Evaluation Rules

### Application
```lisp
(function arg1 arg2 ...)
```
Apply function to arguments.

### Quoting
```lisp
'expression
```
Quote expression (prevent evaluation).

### Quasiquoting
```lisp
`expression
```
Quasiquote with unquote `,` for selective evaluation.

## Tail-Call Optimization

Lambdora implements tail-call optimization via trampoline:

```lisp
(define factorial
  (lambda n.
    (letrec ((fact (lambda n acc.
                     (if (= n 0)
                         acc
                         (fact (- n 1) (* n acc))))))
      (fact n 1))))
```

The trampoline ensures efficient recursion without stack overflow.

## Error Handling

### Error Types

#### `TokenizeError`
Lexical analysis errors (invalid characters, unterminated strings).

#### `ParseError`
Syntactic errors (unbalanced parentheses, invalid syntax).

#### `EvalError`
Runtime evaluation errors (unbound variables, type errors).

#### `BuiltinError`
Built-in function usage errors (wrong argument types).

#### `MacroExpansionError`
Macro expansion errors (wrong arity, syntax errors).

#### `RecursionInitError`
Accessing recursive bindings before initialization.

### Error Formatting
Errors include location information and code snippets:

```
ParseError: Unexpected token: @
<unknown>:1:1
@
^
```

## Performance Notes

- **Tail-call optimization**: Recursive functions are optimized via trampoline
- **Lazy evaluation**: Not supported (strict evaluation)
- **Memory**: Automatic garbage collection
- **Macros**: Expanded at compile time
- **Gensym**: Unique symbol generation for macro hygiene

---

*For more examples, see the [examples](../examples/) directory.* 