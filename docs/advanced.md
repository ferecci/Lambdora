# Advanced Features

This document covers advanced features and implementation details of Lambdora.

## Trampoline and Tail-Call Optimization

Lambdora implements tail-call optimization using a trampoline pattern. This allows for efficient recursion without stack overflow.

### How It Works

The trampoline works by:
1. Detecting tail calls during evaluation
2. Wrapping tail calls in `Thunk` objects
3. Using a trampoline loop to execute thunks iteratively

```lisp
; This recursive function won't cause stack overflow
(define factorial
  (lambda n.
    (letrec ((fact (lambda n acc.
                     (if (= n 0)
                         acc
                         (fact (- n 1) (* n acc))))))
      (fact n 1))))

(factorial 1000)  ; Works without stack overflow
```

### Implementation Details

The trampoline is implemented in `evaluator.py`:

```python
def trampoline(result: Value) -> Value:
    while isinstance(result, Thunk):
        result = result.func()
    return result
```

Tail calls are detected by the `is_tail` parameter in `lambEval()`.

## Macro System Internals

### Hygienic Macro Expansion

Lambdora's macro system prevents variable capture through hygienic expansion:

1. **Gensym Generation**: Unique symbols are generated for each macro expansion
2. **Environment Isolation**: Macro bodies are expanded in isolated environments
3. **Symbol Renaming**: Variables are renamed to avoid conflicts

### Macro Expansion Process

```lisp
(defmacro safe-let (var val body)
  `((lambda ,var . ,body) ,val))

; This expands to something like:
; ((lambda x . (+ x 1)) 5)
; Where 'x' is a gensym-generated unique symbol
```

### Quasiquote Implementation

Quasiquotes are processed in two phases:

1. **Parsing**: `QuasiQuoteExpr` nodes are created during parsing
2. **Evaluation**: `evalQuasiquote()` processes quasiquotes during evaluation

```lisp
; Quasiquote with nested evaluation
(define x 5)
(define y 10)
`(+ ,x ,(+ y 1))  ; => (+ 5 11)
```

## Advanced Macro Patterns

### List Comprehension

```lisp
(defmacro list-comp (expr var list pred)
  `(filter (lambda ,var . ,pred) (map (lambda ,var . ,expr) ,list)))

; Usage
(define numbers (range 10))
(define evens (list-comp x x numbers (> x 5)))
```

### Loop Macros

```lisp
(defmacro while (cond body)
  `(letrec ((loop (lambda __.
                    (if ,cond
                        (begin ,body (loop nil))
                        nil))))
     (loop nil)))

(defmacro for (var start end body)
  `(letrec ((loop (lambda ,var.
                    (if (< ,var ,end)
                        (begin ,body (loop (+ ,var 1)))
                        nil))))
     (loop ,start)))
```

### Multiple Let Bindings

```lisp
(defmacro let2 (x y xval yval body)
  `((lambda ,x . ((lambda ,y . ,body) ,yval)) ,xval))

; Usage
(let2 x 1 y 2 (print (++ "x = " (str x) ", y = " (str y))))
```

## Recursive Definitions

### LetRec Implementation

`letrec` allows mutually recursive definitions:

```lisp
(letrec ((even? (lambda n.
                   (if (= n 0)
                       true
                       (odd? (- n 1))))
         (odd? (lambda n.
                  (if (= n 0)
                      false
                      (even? (- n 1))))))
  (even? 4))
```

### Recursion Placeholder

The implementation uses a placeholder system to handle recursive references:

1. **Placeholder Binding**: Names are bound to `_REC_PLACEHOLDER` initially
2. **Evaluation**: Each binding is evaluated in the same environment
3. **Environment Patching**: Closure environments are patched with final values

## Error Handling System

### Error Hierarchy

```
LambError (base)
├── TokenizeError (lexical errors)
├── ParseError (syntax errors)
├── EvalError (runtime errors)
├── BuiltinError (built-in function errors)
├── MacroExpansionError (macro errors)
└── RecursionInitError (recursive binding errors)
```

### Error Location

Errors include precise location information:

```
ParseError: Unexpected token: @
<unknown>:1:1
@
^
```

### Error Formatting

The `format_lamb_error()` function provides colored, formatted error output with:
- Stack traces (dimmed)
- Error type and message (bold red)
- Code snippets with carets
- Location information

## Performance Optimizations

### Tail-Call Detection

The evaluator detects tail calls by:
- Tracking `is_tail` parameter through evaluation
- Identifying tail positions in function applications
- Wrapping tail calls in `Thunk` objects

### Macro Expansion

Macros are expanded:
- At compile time (before evaluation)
- Recursively (macros can expand to other macros)
- Hygienically (preventing variable capture)

### Memory Management

- **Automatic garbage collection**: Python's GC handles memory
- **Environment sharing**: Closures share environment references
- **Thunk recycling**: Thunks are created and destroyed as needed

## Advanced Usage Patterns

### Church Encoding

```lisp
; Church numerals
(define zero  (lambda f. (lambda x. x)))
(define succ  (lambda n. (lambda f. (lambda x. (f ((n f) x))))))
(define add   (lambda n. (lambda m. (lambda f. (lambda x. ((n f) ((m f) x)))))))

; Church booleans
(define true  (lambda x. (lambda y. x)))
(define false (lambda x. (lambda y. y)))
```

### Continuation-Passing Style

```lisp
(define factorial-cps
  (lambda n.
    (letrec ((fact (lambda n k.
                     (if (= n 0)
                         (k 1)
                         (fact (- n 1) (lambda result. (k (* n result))))))))
      (fact n (lambda x. x)))))
```

### Monadic Patterns

```lisp
; Maybe monad
(define just (lambda x. (lambda f. (f x))))
(define nothing (lambda f. nothing))

(define bind (lambda m. (lambda f. (m f))))
```

## Debugging and Development

### REPL Features

The REPL provides:
- **Multiline input**: Automatic continuation for unbalanced parentheses
- **History**: Command history with readline
- **Error formatting**: Colored error messages
- **Help system**: Built-in help command

### Development Tools

- **Test coverage**: Comprehensive test suite
- **Error tracking**: Detailed error information
- **Macro debugging**: Macro expansion tracing
- **Performance profiling**: Tail-call optimization verification

## Implementation Notes

### Code Organization

```
src/lambdora/
├── tokenizer.py      # Lexical analysis
├── parser.py         # S-expression parsing
├── evaluator.py      # Evaluation with trampoline
├── macro.py          # Macro expansion
├── builtinsmodule.py # Built-in functions
├── values.py         # Value representations
├── errors.py         # Error handling
└── stdlib/           # Standard library
```

### Key Design Decisions

1. **S-expression syntax**: Universal, simple parsing
2. **Trampoline evaluation**: Efficient recursion
3. **Hygienic macros**: Safe metaprogramming
4. **Lexical scoping**: Predictable variable binding
5. **First-class functions**: Full functional programming support

---

*For more information, see the [API reference](api.md) and [examples](../examples/).* 