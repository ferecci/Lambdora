# 🐑 Lambdora

[![codecov](https://codecov.io/gh/ferecci/Lambdora/graph/badge.svg?token=ORV38HH7J7)](https://codecov.io/gh/ferecci/Lambdora)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A **1-kLOC Lisp-inspired functional language** written in modern Python. Lambdora implements a full interpreter—lexer, parser, evaluator, and macro system in a compact codebase.

![Lambdora REPL](docs/lambdora-demo.gif)

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
# Install from PyPI
$ pip install lambdora

# OR install from source
$ git clone https://github.com/ferecci/Lambdora.git && cd Lambdora
$ pip install -e .
# OR
$ make install

# launch REPL
$ lambdora repl

# run a script
$ lambdora run examples/fizzbuzz.lamb

# check version and help
$ lambdora --version
$ lambdora --help
```

**Legacy commands still work:**
```bash
$ python -m lambdora.repl
$ python -m lambdora.runner examples/fizzbuzz.lamb
```

## Hello World
```lisp
(print "Hello, Lambdora!") ; => Hello, Lambdora!
```

## Usage Examples
```lisp
(define inc   (lambda x. (+ x 1)))
(define twice (lambda f. (lambda x. (f (f x)))))
((twice inc) 3)               ; => 5

(defmacro when (cond body)
  (if cond body nil))
(when true (print "hi"))      ; => hi
```

## Examples

Try the included examples:
- **[FizzBuzz](examples/fizzbuzz.lamb)** - Classic programming problem
- **[Church Numerals](examples/church_numerals.lamb)** - Functional programming concepts
- **[Macro Examples](examples/macro_demos.lamb)** - Hygienic macro system

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

## Documentation

- **[Language Guide](docs/index.md)** - Complete language overview and philosophy
- **[API Reference](docs/api.md)** - Built-in functions and standard library
- **[REPL Guide](docs/repl.md)** - Interactive development guide

## Contributing
Open an issue or pull request, everyone's welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License
MIT © Felipe Tancredo (ferecci)
