# Lambdora Documentation

Welcome to Lambdora, a minimalist Lisp-inspired functional language written in modern Python. Lambdora embodies the philosophy of simplicity and expressiveness, drawing inspiration from both classic functional programming and the minimalist language Toki Pona.

## Philosophy: "pona li lili" (Good is Simple)

Like Toki Pona, Lambdora embraces the principle that **good is simple**. The language is designed to be:

- **Minimal**: Core language fits in ~1,000 lines of code
- **Expressive**: Powerful abstractions through functions and macros
- **Composable**: Everything is built from a few fundamental concepts
- **Clear**: Syntax that reads like natural language

## Quick Start

### Installation
```bash
git clone https://github.com/ferecci/Lambdora.git
cd Lambdora
pip install -e .
```

### Interactive REPL
```bash
python -m lambdora.repl
```

### Running Scripts
```bash
python -m lambdora.runner examples/fizzbuzz.lamb
```

## Language Overview

### Core Principles

1. **Everything is an Expression**: No statements, only expressions
2. **First-Class Functions**: Functions are values like any other
3. **Lexical Scoping**: Variables are bound where they're defined
4. **Tail-Call Optimization**: Efficient recursion without stack overflow
5. **Hygienic Macros**: Safe metaprogramming without variable capture

### Syntax

Lambdora uses S-expressions (parenthesized prefix notation):

```lisp
; Basic expressions
(+ 1 2)                    ; => 3
(define x 42)              ; => 42
(print "Hello, world!")    ; => Hello, world!

; Function definition
(define inc (lambda x. (+ x 1)))
(inc 5)                    ; => 6

; Anonymous functions
((lambda x. (* x x)) 4)    ; => 16

; Conditionals
(if (> 5 3) "yes" "no")   ; => "yes"

; Lists
(cons 1 (cons 2 nil))     ; => (1 2)
```

### Data Types

- **Numbers**: Integers (e.g., `42`, `-17`)
- **Booleans**: `true`, `false`
- **Strings**: `"Hello, world!"`
- **Lists**: `(1 2 3)`, `nil` (empty list)
- **Functions**: First-class, can be passed around

## Functional Programming Features

### Higher-Order Functions

```lisp
; Map: apply function to each element
(map (lambda x. (* x 2)) (range 5))
; => (0 2 4 6 8)

; Filter: keep elements that satisfy predicate
(filter (lambda x. (> x 3)) (range 10))
; => (4 5 6 7 8 9)

; Fold: combine elements with a function
(foldl (lambda acc. (lambda x. (+ acc x))) 0 (range 5))
; => 10
```

### Currying

Functions automatically curry, allowing partial application:

```lisp
(define add (lambda x. (lambda y. (+ x y))))
(define add5 (add 5))
(add5 3)  ; => 8
```

### Tail-Call Optimization

Lambdora optimizes tail calls via trampoline, making recursion efficient:

```lisp
(define factorial
  (lambda n.
    (letrec ((fact (lambda n acc.
                     (if (= n 0)
                         acc
                         (fact (- n 1) (* n acc))))))
      (fact n 1))))
```

## Macro System

Lambdora features a hygienic macro system for metaprogramming:

```lisp
; Basic control flow macros
(defmacro when (cond body)
  `(if ,cond ,body nil))

(defmacro unless (cond body)
  `(if (not ,cond) ,body nil))

; Let-binding macro
(defmacro let (var val body)
  `((lambda ,var . ,body) ,val))

; Usage
(when (> 5 3) (print "Five is greater than three"))
(let x 42 (print "x is " x))
```

### Macro Hygiene

Macros are hygienic, preventing variable capture using `gensym`:

```lisp
(defmacro safe-let (var val body)
  `((lambda ,var . ,body) ,val))

; This works correctly even if 'x' is used in 'val'
(safe-let x 5 (+ x 1))  ; => 6
```

### Quoting and Quasiquoting

```lisp
; Quote: prevent evaluation
'(+ 1 2)  ; => (+ 1 2) (unevaluated)

; Quasiquote: selective evaluation
(define x 5)
`(+ 1 ,x)  ; => (+ 1 5)

; Unquote: evaluate inside quasiquote
(define y 10)
`(list ,y ,(+ y 1))  ; => (list 10 11)
```

## Recursive Definitions

### LetRec

Define mutually recursive functions:

```lisp
(letrec ((fact (lambda n.
                 (if (= n 0)
                     1
                     (* n (fact (- n 1))))))
  (fact 5))
```

## Design Philosophy

### Inspired by Toki Pona

Like Toki Pona's 120 words, Lambdora aims for **minimalism without loss of expressiveness**:

- **Simple syntax**: S-expressions are universal
- **Few primitives**: Everything built from functions
- **Composable**: Complex ideas from simple parts
- **Clear semantics**: No hidden complexity

### Functional Programming Principles

- **Immutability**: Values don't change, new values are created
- **Referential transparency**: Same input always gives same output
- **Higher-order functions**: Functions that take/return functions
- **Pattern matching**: Elegant control flow

### Implementation Goals

- **Readable**: Code should be self-documenting
- **Testable**: Every feature has comprehensive tests
- **Extensible**: Easy to add new features

## Performance Features

- **Tail-call optimization**: Via trampoline for efficient recursion
- **Macro expansion**: At compile time for performance
- **Gensym**: Unique symbol generation for macro hygiene
- **Memory management**: Automatic garbage collection

## Examples

### FizzBuzz
```lisp
(define fizzbuzz
  (lambda n.
    (cond (= (mod n 15) 0) "FizzBuzz"
          (= (mod n 3) 0)  "Fizz"
          (= (mod n 5) 0)  "Buzz"
          true             (str n))))
```

### Church Numerals
```lisp
(define zero  (lambda f. (lambda x. x)))
(define succ  (lambda n. (lambda f. (lambda x. (f ((n f) x))))))
(define add   (lambda n. (lambda m. (lambda f. (lambda x. ((n f) ((m f) x)))))))
```

### Y-Combinator
```lisp
(define Y
  (lambda f.
    ((lambda x. (f (x x)))
     (lambda x. (f (x x))))))
```

## Next Steps

- Explore the [examples](examples/) directory
- Check out the [API reference](api.md) for detailed function documentation
- Try the interactive [REPL guide](repl.md)
- Read about [advanced features](advanced.md) for implementation details
- Read the [contributing guide](../CONTRIBUTING.md)

---

*"pona li lili" - Good is simple* 🐑 