# 🐑 Lambdora &nbsp; [![codecov](https://codecov.io/gh/ferecci/Lambdora/graph/badge.svg?token=ORV38HH7J7)](https://codecov.io/gh/ferecci/Lambdora)

**Lambdora** is a minimal functional programming language inspired by Lisp and lambda calculus, implemented in Python. It supports first-class functions, lexical closures, macros, tail-call optimization, and a simple REPL — all in fewer than 1000 lines of code.

> A tiny lambda-powered language with big functional features.

---

## ✨ Features

- First-class lambdas (`λx. ...`) and currying  
- Lexical scoping with closures  
- Built-in types: numbers, booleans, pairs/lists, nil  
- Powerful macro system (`defmacro`)  
- Tail-call optimization via trampoline  
- Minimal standard library (`std.lamb`)  
- REPL and file runner  
- Testable and extensible structure

---

## 📦 Getting Started

### ✅ Requirements
- Python 3.10+

### ▶️ Run the REPL

```
python -m main.py
```

### 📂 Run a program

```
python -m main.py examples/fizzbuzz.lamb
```

---

## 🧪 Example

```lisp
(define inc (λx. (+ x 1)))
(define twice (λf. (λx. (f (f x)))))
((twice inc) 3)      ; => 5

(defmacro when (cond body)
  (if cond body nil))

(when true (print "Hello, macros!")) ; => Hello, macros!
```

---

## 📁 Project Structure

```
lambdora/
├── tokenizer.py       # Lexer
├── parser.py          # S-expression to AST
├── astmodule.py       # AST node classes
├── evaluator.py       # Core evaluator with TCO
├── builtinsmodule.py  # Built-in functions and values
├── macro.py           # Macro expansion logic
├── values.py          # Runtime value representations
├── printer.py         # Pretty-printer
├── main.py            # REPL and file runner
└── stdlib/std.lamb    # Standard library (loaded at launch)
```

---

## 🛣️ Roadmap

- [x] Core language & REPL
- [x] Macros
- [x] Tail-call optimization
- [x] `quote` special form
- [ ] Macro hygiene
- [ ] Range/loop helpers
- [ ] LLVM backend (stretch goal)

---

## ⚖️ License

MIT License. Created by Felipe Tancredo (ferecci).
