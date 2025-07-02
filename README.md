# 🐑 Lambdora

A minimal Lisp-inspired functional language implemented in ~1 kLOC of Python.

[![codecov](https://codecov.io/gh/ferecci/Lambdora/graph/badge.svg?token=ORV38HH7J7)](https://codecov.io/gh/ferecci/Lambdora)

## Features

- First-class lambdas & currying
- Lexical closures (static scope)
- Macro system (`defmacro`) for metaprogramming
- Tail-call optimization (trampoline)
- Built-in types: numbers, booleans, pairs/lists, `nil`
- Lightweight functional standard library
- Interactive REPL & script runner

## Quick Start

Requirements: **Python ≥ 3.10**

```bash
# from repository root
pip install -e .
python -m lambdora.repl   # launch REPL
```

Run a program:

```bash
python -m lambdora.runner path/to/code.lamb
```

## Example

```lisp
(define inc   (λx. (+ x 1)))
(define twice (λf. (λx. (f (f x)))))
((twice inc) 3)        ; => 5

(defmacro when (cond body)
  (if cond body nil))
(when true (print "hi")) ; => hi
```

## Language Essentials

Special forms   | `define` · `λ`/`lambda` · `if` · `quote` · `defmacro`
--------------- | -----------------------------------------------------------------
Arithmetic       | `+  -  *  /  =  <  >  <=  >=`
Lists            | `cons` · `head` · `tail` · `isNil`
Logic            | `and` · `or` · `not`

The standard library (autoloaded) provides `map`, `filter`, `foldl`, `range`, `reverse`, tail-recursive `fact`/`fib`, and helper macros like `when`, `unless`, `cond`, `let`.

## Directory Layout

```
src/lambdora/
  tokenizer.py       # lexer
  parser.py          # S-expr → AST
  evaluator.py       # evaluator with TCO
  macro.py           # macros
  builtinsmodule.py  # built-in functions
  stdlib/std.lamb    # standard library
```

## Contributing

```bash
# optional: create & activate a virtual environment first
pip install -e .[dev]
pytest               # run test-suite
```

## License

MIT © Felipe Tancredo (ferecci)
