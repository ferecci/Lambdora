6/26/2025

# Lexicon

For now, we support:

* (, )
* λ (lambda character)
* . (dot separates param from body)
* Identifiers (like x, f, foo)
* Whitespace is ignored
* Semicolons ; and everything after them on the line are comments
* 'if' expressions
* 'let' and 'define' expressions

# Grammar

* expr      ::= atom | application | abstraction
* atom      ::= identifier | ( expr )
* abstraction ::= ( λ identifier . expr )
* application ::= ( expr expr+ )

# Running The REPL

* 'exit' in the terminal exits the application.

-> building lists based on modern set theory: start with nil, cons on that
