# 🐑 Lambdora

[![codecov](https://codecov.io/gh/ferecci/Lambdora/graph/badge.svg?token=ORV38HH7J7)](https://codecov.io/gh/ferecci/Lambdora)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A **1-kLOC Lisp-inspired functional language** written in modern Python. Lambdora showcases a full interpreter—lexer, parser, evaluator, and macro system in a compact codebase.

## Features
- First-class anonymous functions with currying
- Lexical closures (static scope)
- Tail-call optimization via trampoline
- Hygienic macro system (`defmacro`) for metaprogramming
- Built-in data types: numbers, booleans, pairs/lists, `nil`
- Expressive functional standard library (`map`, `foldl`, `range`, …)
- Interactive REPL & script runner
- ~85% test coverage with pytest and Codecov integration

## Quick Start
```bash
# clone repository
$ git clone https://github.com/ferecci/Lambdora.git && cd Lambdora

# install (editable) with runtime deps only
$ pip install -e .

# launch REPL
$ python -m lambdora.repl

# run a script
$ python -m lambdora.runner examples/hello.lamb
```

## Hello World
```lisp
(print "Hello, Lambdora!") ; => Hello, Lambdora!
```

## Showcase
```lisp
(define inc   (λx. (+ x 1)))
(define twice (λf. (λx. (f (f x)))))
((twice inc) 3)               ; => 5

(defmacro when (cond body)
  (if cond body nil))
(when true (print "hi"))      ; => hi
```

## Architecture Overview
```
src/lambdora/
  tokenizer.py       # lexical analysis
  parser.py          # S-expression → AST
  evaluator.py       # evaluator with tail-call optimisation
  macro.py           # macro expander & hygiene
  builtinsmodule.py  # built-in functions
  stdlib/std.lamb    # functional standard library
```
Each module is <200 LOC and unit-tested, making the codebase easy to navigate and extend.

## Testing
```bash
# install dev dependencies
$ pip install -e .[dev]

# run test-suite & watch coverage
$ pytest --cov  # reports to terminal
```
A GitHub Action uploads coverage to Codecov (badge above).

## Contributing
Open an issue or pull request, everyone’s welcome! Just keep comments clear and check that tests pass.

## License
MIT © Felipe Tancredo (ferecci)
