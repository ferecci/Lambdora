"""
Lambdora - A Lisp-inspired functional language
Bundled for Pyodide web deployment
"""

import sys
from io import StringIO
from typing import Optional, Any, List, Union, Callable, Dict
from collections import defaultdict
from dataclasses import dataclass

# ============================================================================
# AST Module (needed for Expr type)
# ============================================================================

from typing import Union, List

@dataclass
class Expr:
    pass

@dataclass
class Variable(Expr):
    name: str

@dataclass
class Literal(Expr):
    value: str

@dataclass
class Abstraction(Expr):
    param: str
    body: Expr

@dataclass
class Application(Expr):
    func: Expr
    args: List[Expr]

@dataclass
class DefineExpr(Expr):
    name: str
    value: Expr

@dataclass
class IfExpr(Expr):
    cond: Expr
    then_branch: Expr
    else_branch: Expr

@dataclass
class DefMacroExpr(Expr):
    name: str
    params: List[str]
    body: Expr

@dataclass
class QuoteExpr(Expr):
    value: Expr

@dataclass
class QuasiQuoteExpr(Expr):
    expr: Expr

@dataclass
class UnquoteExpr(Expr):
    expr: Expr

@dataclass
class LetRec(Expr):
    bindings: List[tuple[str, Expr]]
    body: List[Expr]

# ============================================================================
# Values and Types
# ============================================================================
# ============================================================================
# values.py
# ============================================================================
Value = Union[
    int, str, bool, "Closure", "Builtin", "Pair", "Nil", "Macro", "Thunk", Expr
]


@dataclass
class Closure:
    param: str
    body: Expr
    env: dict[str, Value]


@dataclass
class Builtin:
    func: Callable[[Value], Value]


@dataclass
class Pair:
    head: Value
    tail: Value


@dataclass
class Macro:
    params: List[str]
    body: Expr


@dataclass
class Thunk:
    func: Callable[[], Value]


class Nil:
    def __repr__(self) -> str:
        return "nil"


nil = Nil()


def valueToString(val: Value) -> str:
    if isinstance(val, Closure):
        return f"<closure lambda {val.param}. …>"
    elif isinstance(val, bool):
        return "true" if val else "false"
    elif isinstance(val, int):
        return str(val)
    elif isinstance(val, str):
        return f"{val}"
    elif isinstance(val, Builtin):
        return "<builtin fn>"
    elif isinstance(val, Pair):
        # Print as (a b c)
        elems = []
        p: Value = val
        while isinstance(p, Pair):
            elems.append(valueToString(p.head))
            p = p.tail
        if p is not nil:
            elems.append(".")
            elems.append(valueToString(p))
        return f"({' '.join(elems)})"
    elif val is nil:
        return "nil"
    elif isinstance(val, Expr):
        # Handle AST nodes as values (code as data)
        from .printer import lambPrint

        return lambPrint(val)
    else:
        return f"<unknown value: {val}>"


# ============================================================================
# errors.py
# ============================================================================
    def __init__(
        self,
        message: str,
        *,
        file: Optional[str] = None,
        line: Optional[int] = None,
        column: Optional[int] = None,
        snippet: Optional[str] = None,
        cause: Optional[BaseException] = None,
    ) -> None:
        super().__init__(message)
        self.file = file
        self.line = line
        self.column = column
        self.snippet = snippet.rstrip("\n") if snippet else None
        # Preserve original traceback while allowing pretty presentation
        if cause is not None:
            self.__cause__ = cause

    def _loc(self) -> str:
        if self.line is None or self.column is None:
            return ""
        location = f"{self.file or '<unknown>'}:{self.line}:{self.column}"
        return location

    def __str__(self) -> str:
        loc = self._loc()
        return f"{loc + ': ' if loc else ''}{super().__str__()}"


class TokenizeError(LambError, SyntaxError):
    """Thrown by the tokenizer when it cannot produce a valid token stream."""


class ParseError(LambError, SyntaxError):
    """Raised by the parser upon syntactic mistakes at the token level."""


class MacroExpansionError(LambError, RuntimeError):
    """Problems occurring during macro expansion (wrong arity, etc.)."""


class EvalError(LambError, NameError, TypeError):
    """Catch-all for runtime evaluation mistakes inside ``evaluator.py``."""


class BuiltinError(LambError, TypeError):
    """Invalid usage of built-in functions."""


class RecursionInitError(LambError, RuntimeError):
    """Accessing a recursive binding before it is initialised."""


__all__ = [
    "LambError",
    "TokenizeError",
    "ParseError",
    "MacroExpansionError",
    "EvalError",
    "BuiltinError",
    "RecursionInitError",
    "format_lamb_error",
]


def format_lamb_error(err: LambError) -> str:
    """Return a colourised traceback + message for *err*."""

    # Grey/dim stack frames, excluding the very last (the user-facing one)
    grey = Style.DIM + Fore.WHITE
    frames: list[str] = (
        traceback.format_tb(err.__traceback__) if err.__traceback__ else []
    )
    pretty_frames = [grey + f for f in frames[:-1]]  # dim all but last frame

    # Bold red bullet for the error header
    header = f"{Style.BRIGHT + Fore.RED}{type(err).__name__}{Style.RESET_ALL}: {err}"

    # Show code snippet if we have one
    snippet = ""
    if err.snippet:
        caret = " " * (err.column - 1 if err.column and err.column > 0 else 0) + "^"
        snippet = (
            f"{Style.DIM}{err.snippet}{Style.RESET_ALL}\n"
            f"{Style.DIM}{caret}{Style.RESET_ALL}"
        )

    # Add helpful suggestions based on error type
    suggestion = ""
    if isinstance(err, TokenizeError):
        if "unexpected token" in str(err).lower():
            suggestion = (
                f"\n{Fore.YELLOW}Tip: Check for unmatched parentheses or "
                f"invalid syntax.{Style.RESET_ALL}"
            )
        elif "unterminated string" in str(err).lower():
            suggestion = (
                f"\n{Fore.YELLOW}Tip: Make sure all strings are properly "
                f"closed with quotes.{Style.RESET_ALL}"
            )
    elif isinstance(err, ParseError):
        if "unexpected eof" in str(err).lower():
            suggestion = (
                f"\n{Fore.YELLOW}Tip: Check for missing closing "
                f"parentheses.{Style.RESET_ALL}"
            )
        elif "unbound variable" in str(err).lower():
            suggestion = (
                f"\n{Fore.YELLOW}Tip: Make sure the variable is defined "
                f"before use.{Style.RESET_ALL}"
            )
    elif isinstance(err, EvalError):
        if "unbound variable" in str(err).lower():
            suggestion = (
                f"\n{Fore.YELLOW}Tip: Use (define var value) to define "
                f"variables.{Style.RESET_ALL}"
            )
        elif "lambda syntax" in str(err).lower():
            suggestion = (
                f"\n{Fore.YELLOW}Tip: Lambda syntax is (lambda param . "
                f"body){Style.RESET_ALL}"
            )

    return (
        "".join(pretty_frames)
        + header
        + ("\n" + snippet if snippet else "")
        + suggestion
    )


# ============================================================================
# tokenizer.py
# ============================================================================
    return src.splitlines()[line_no - 1]


def lambTokenize(source: str, *, filename: str | None = None) -> list[str]:
    """Tokenise *source*. *filename* is used only in error messages."""

    tokens: list[str] = []
    i = 0  # absolute index into *source*
    line_no = 1
    col_no = 1  # 1-based column index

    while i < len(source):
        char = source[i]

        # Newline
        if char == "\n":
            i += 1
            line_no += 1
            col_no = 1
            continue

        # Skip ';' comments
        if char == ";":
            while i < len(source) and source[i] != "\n":
                i += 1
                col_no += 1
            continue  # newline (if any) handled on next loop iteration

        # Whitespace
        if char.isspace():
            i += 1
            col_no += 1
            continue

        # Multi-char operators (check before single-char tokens)
        if i + 1 < len(source):
            two_char = source[i : i + 2]
            if two_char in ["++", "!=", "<=", ">="]:
                tokens.append(two_char)
                i += 2
                col_no += 2
                continue

        # Single-char tokens
        if char in "().+-*/%=<>',`":
            tokens.append(char)
            i += 1
            col_no += 1
            continue

        # Identifiers
        if char.isalpha() or char == "_":
            start = i
            while i < len(source) and (
                source[i].isalnum() or source[i] == "_" or source[i] == "-" or source[i] == "?"
            ):
                i += 1
                col_no += 1
            tokens.append(source[start:i])
            continue

        # Integers
        if char.isdigit():
            start = i
            while i < len(source) and source[i].isdigit():
                i += 1
                col_no += 1
            tokens.append(source[start:i])
            continue

        # Strings
        if char == '"':
            i += 1
            col_no += 1
            start_idx = i
            str_line, str_col = line_no, col_no

            while i < len(source) and source[i] != '"':
                if source[i] == "\n":
                    line_no += 1
                    col_no = 0  # will be incremented at end of loop
                i += 1
                col_no += 1

            if i >= len(source):  # reached EOF
                snippet = _line_at(source, str_line)
                raise TokenizeError(
                    "Unterminated string literal",
                    file=filename,
                    line=str_line,
                    column=str_col,
                    snippet=snippet,
                )

            # Slice out the contents (excluding the quotes)
            literal = source[start_idx:i]
            tokens.append(f'"{literal}"')

            # Skip the closing quote
            i += 1
            col_no += 1
            continue

        # Unknown char
        snippet = _line_at(source, line_no)
        raise TokenizeError(
            f"Unexpected character: {char}",
            file=filename,
            line=line_no,
            column=col_no,
            snippet=snippet,
        )

    return tokens


# ============================================================================
# parser.py
# ============================================================================
    if i >= len(tokens):
        raise SyntaxError("Unexpected EOF while parsing")
    token = tokens[i]

    if token == "`":  # Back-quote
        expr, j = parseExpression(tokens, i + 1, in_quasiquote=True)
        return QuasiQuoteExpr(expr), j

    if token == ",":  # Comma
        expr, j = parseExpression(tokens, i + 1, in_quasiquote=in_quasiquote)
        return UnquoteExpr(expr), j

    if token == "(":
        i += 1
        if i >= len(tokens):
            raise SyntaxError("Unexpected EOF after '('")

        elif tokens[i] == "letrec":
            i += 1
            if i >= len(tokens):
                raise SyntaxError("Unexpected EOF after letrec")

            # Parse bindings - expect ((name1 value1) (name2 value2) ...)
            if tokens[i] != "(":
                raise SyntaxError("Expected '(' after letrec")
            i += 1

            bindings = []
            while i < len(tokens) and tokens[i] != ")":
                if tokens[i] != "(":
                    raise SyntaxError("Expected '(' for letrec binding")
                i += 1

                if i >= len(tokens):
                    raise SyntaxError("Unexpected EOF in letrec binding")

                # Parse binding name
                name = tokens[i]
                i += 1

                if i >= len(tokens):
                    raise SyntaxError("Unexpected EOF after letrec binding name")

                # Parse binding value
                value, i = parseExpression(tokens, i, in_quasiquote=in_quasiquote)

                if i >= len(tokens):
                    raise SyntaxError("Unexpected EOF after letrec binding value")

                if tokens[i] != ")":
                    raise SyntaxError("Expected ')' after letrec binding")
                i += 1

                bindings.append((name, value))

            if i >= len(tokens):
                raise SyntaxError("Unexpected EOF after letrec bindings")

            if tokens[i] != ")":
                raise SyntaxError("Expected ')' after letrec bindings")
            i += 1

            # Parse body expressions
            letrec_body = []
            while i < len(tokens) and tokens[i] != ")":
                body_expr, i = parseExpression(tokens, i, in_quasiquote=in_quasiquote)
                letrec_body.append(body_expr)

            if i >= len(tokens):
                raise SyntaxError("Unexpected EOF after letrec body")

            if tokens[i] != ")":
                raise SyntaxError("Expected ')' after letrec body")

            return LetRec(bindings, letrec_body), i + 1

        elif tokens[i] == "define":
            i += 1
            if i >= len(tokens):
                raise SyntaxError("Unexpected EOF after define")

            # Parse name
            name = tokens[i]
            i += 1

            if i >= len(tokens):
                raise SyntaxError("Unexpected EOF after define name")

            # Parse value
            value, i = parseExpression(tokens, i, in_quasiquote=in_quasiquote)

            if i >= len(tokens):
                raise SyntaxError("Unexpected EOF after define value")

            if tokens[i] != ")":
                raise SyntaxError("Expected ')' after define value")

            return DefineExpr(name, value), i + 1

        elif tokens[i] == "defmacro":
            i += 1
            if i >= len(tokens):
                raise SyntaxError("Unexpected EOF after defmacro")

            # Parse name
            name = tokens[i]
            i += 1

            if i >= len(tokens):
                raise SyntaxError("Unexpected EOF after defmacro name")

            # Parse parameters - expect (param1 param2 ...)
            if tokens[i] != "(":
                raise SyntaxError("Expected '(' after defmacro name")
            i += 1

            params = []
            while i < len(tokens) and tokens[i] != ")":
                params.append(tokens[i])
                i += 1

            if i >= len(tokens):
                raise SyntaxError("Unexpected EOF after defmacro params")

            if tokens[i] != ")":
                raise SyntaxError("Expected ')' after defmacro params")
            i += 1

            if i >= len(tokens):
                raise SyntaxError("Unexpected EOF after defmacro params")

            # Parse body (should be a single Expr)
            macro_body, i = parseExpression(tokens, i, in_quasiquote=in_quasiquote)

            if i >= len(tokens):
                raise SyntaxError("Unexpected EOF after defmacro body")

            if tokens[i] != ")":
                raise SyntaxError("Expected ')' after defmacro body")

            return DefMacroExpr(name, params, macro_body), i + 1

        elif tokens[i] == "lambda" and not in_quasiquote:
            i += 1
            if i >= len(tokens):
                raise SyntaxError("Unexpected EOF after lambda")

            # Parse parameter
            param = tokens[i]
            i += 1

            if i >= len(tokens):
                raise SyntaxError("Unexpected EOF after lambda param")

            # Expect dot
            if tokens[i] != ".":
                raise SyntaxError("Expected '.' after lambda param")
            i += 1

            if i >= len(tokens):
                raise SyntaxError("Unexpected EOF after lambda dot")

            # Parse body (should be a single Expr)
            lambda_body, i = parseExpression(tokens, i, in_quasiquote=in_quasiquote)

            if i >= len(tokens):
                raise SyntaxError("Unexpected EOF after lambda body")

            if tokens[i] != ")":
                raise SyntaxError("Expected ')' after lambda body")

            return Abstraction(param, lambda_body), i + 1

        elif tokens[i] == "quote":
            i += 1
            if i >= len(tokens):
                raise SyntaxError("Unexpected EOF after quote")

            # Parse the quoted expression
            quoted_expr, i = parseExpression(tokens, i, in_quasiquote=in_quasiquote)

            if i >= len(tokens):
                raise SyntaxError("Unexpected EOF after quote expression")

            if tokens[i] != ")":
                raise SyntaxError("Expected ')' after quote expression")

            return QuoteExpr(quoted_expr), i + 1

        func, i = parseExpression(tokens, i, in_quasiquote=in_quasiquote)
        args = []
        while i < len(tokens) and tokens[i] != ")":
            arg, i = parseExpression(tokens, i, in_quasiquote=in_quasiquote)
            args.append(arg)
        if i >= len(tokens):
            raise SyntaxError("Unexpected EOF: missing ')'")
        return Application(func, args), i + 1

    elif token == "'":
        quoted, i = parseExpression(tokens, i + 1, in_quasiquote=in_quasiquote)
        return QuoteExpr(quoted), i

    elif token.isnumeric():
        return Literal(token), i + 1

    elif token.startswith('"') and token.endswith('"'):
        return Literal(token[1:-1]), i + 1

    elif token == ".":
        return Literal("."), i + 1

    elif re.match(r"^[a-zA-Z0-9_+\-*/=<>!?%_]+$", token):
        return Variable(token), i + 1

    else:
        raise SyntaxError(f"Unexpected token: {token}")


# Parse for a single expr
def lambParse(tokens: List[str]) -> Expr:
    expr, final_i = parseExpression(tokens, 0, in_quasiquote=False)
    if final_i != len(tokens):
        raise SyntaxError("Unexpected extra tokens")
    return expr


# ParseAll for many top-level exprs
def lambParseAll(tokens: List[str]) -> List[Expr]:
    exprs = []
    i = 0
    while i < len(tokens):
        expr, i = parseExpression(tokens, i, in_quasiquote=False)
        exprs.append(expr)
    return exprs


# ============================================================================
# evaluator.py
# ============================================================================
    # Variables
    if isinstance(expr, Variable):
        if expr.name in env:
            val = env[expr.name]
            if val is _REC_PLACEHOLDER:
                raise RecursionInitError(
                    f"recursive binding '{expr.name}' accessed before initialisation"
                )
            return val
        else:
            raise EvalError(f"unbound variable: {expr.name}")

    # Literals
    if isinstance(expr, Literal):
        if expr.value.isdigit():
            return int(expr.value)
        return expr.value

    # Abstraction
    if isinstance(expr, Abstraction):
        return Closure(expr.param, expr.body, env.copy())

    # Quote expressions
    if isinstance(expr, QuoteExpr):
        return expr.value

    # Quasiquote expressions
    if isinstance(expr, QuasiQuoteExpr):
        result_expr = evalQuasiquote(expr.expr, env)
        return lambEval(result_expr, env, is_tail)

    # Unquote expressions
    if isinstance(expr, UnquoteExpr):
        raise EvalError("unquote can only be used inside quasiquote")

    # Application
    if isinstance(expr, Application):
        if isinstance(expr.func, Variable):
            fname = expr.func.name
            if fname == "lambda":
                if (
                    len(expr.args) != 3
                    or not isinstance(expr.args[1], Literal)
                    or expr.args[1].value != "."
                ):
                    raise EvalError("lambda syntax: (lambda param . body)")
                param_ast = expr.args[0]
                if isinstance(param_ast, Variable):
                    param = param_ast.name
                elif isinstance(param_ast, Literal) and isinstance(
                    param_ast.value, str
                ):
                    param = param_ast.value
                else:
                    param_val = lambEval(param_ast, env, False)
                    if not isinstance(param_val, str):
                        raise EvalError("lambda param must be string identifier")
                    param = param_val
                body = expr.args[2]
                return Closure(param, body, env.copy())
            elif fname == "if":
                if len(expr.args) != 3:
                    raise ParseError("if requires condition, then, else")
                cond = lambEval(expr.args[0], env, False)
                if not isinstance(cond, bool):
                    raise EvalError("if condition must be boolean")
                branch = expr.args[1] if cond else expr.args[2]
                return lambEval(branch, env, is_tail)
            elif fname == "define":
                if len(expr.args) != 2:
                    raise EvalError("define requires name and value")
                name_ast = expr.args[0]
                if isinstance(name_ast, Variable):
                    name = name_ast.name
                elif isinstance(name_ast, Literal) and isinstance(name_ast.value, str):
                    name = name_ast.value
                else:
                    name_val = lambEval(name_ast, env, False)
                    if not isinstance(name_val, str):
                        raise EvalError("define name must be string identifier")
                    name = name_val
                value = lambEval(expr.args[1], env, False)
                env[name] = value
                if isinstance(value, Closure):
                    value.env[name] = value
                return f"<defined {name}>"
            elif fname == "let":
                if len(expr.args) < 3 or not isinstance(expr.args[0], Variable):
                    raise EvalError("let syntax: (let var val body...)")
                var = expr.args[0].name
                val = lambEval(expr.args[1], env, False)
                new_env = env.copy()
                new_env[var] = val
                bodies = expr.args[2:]
                if not bodies:
                    raise EvalError("let requires at least one body")
                let_result: Value = nil
                for idx, b in enumerate(bodies):
                    is_last = idx == len(bodies) - 1
                    let_result = lambEval(b, new_env, is_tail and is_last)
                return let_result
            elif fname == "defmacro":
                if len(expr.args) != 3:
                    raise EvalError("defmacro requires name, params, body")
                name_ast = expr.args[0]
                if not isinstance(name_ast, Variable):
                    raise EvalError("defmacro name must be identifier")
                name = name_ast.name
                params_ast = expr.args[1]
                body = expr.args[2]
                params = []
                if isinstance(params_ast, Application) and isinstance(
                    params_ast.func, Variable
                ):
                    params.append(params_ast.func.name)
                    for p in params_ast.args:
                        if not isinstance(p, Variable):
                            raise EvalError("defmacro params must be identifiers")
                        params.append(p.name)
                elif isinstance(params_ast, Variable):
                    params = [params_ast.name]
                else:
                    raise EvalError("defmacro params must be list of identifiers")
                env[name] = Macro(params, body)
                return "<macro defined>"

            # Add letrec if needed
        # General case
        def retire() -> Value:
            func_val = lambEval(expr.func, env, False)
            args = [lambEval(a, env, False) for a in expr.args]
            return applyFunc(func_val, args, is_tail)

        if is_tail:
            return Thunk(retire)
        else:
            return retire()

    # If-expression
    if isinstance(expr, IfExpr):
        cond = lambEval(expr.cond, env)
        if not isinstance(cond, bool):
            raise EvalError("condition in 'if' must be a boolean")
        branch = expr.then_branch if cond else expr.else_branch
        return lambEval(branch, env, is_tail)

    # Define-expression
    if isinstance(expr, DefineExpr):
        env[expr.name] = None  # type: ignore
        value = lambEval(expr.value, env)
        if isinstance(value, Closure):
            value.env[expr.name] = value
        env[expr.name] = value
        return f"<defined {expr.name}>"

    # LetRec-expression
    if isinstance(expr, LetRec):
        new_env = env.copy()

        # Pre-bind names to placeholder
        for name, _ in expr.bindings:
            new_env[name] = _REC_PLACEHOLDER

        # Evaluate each binding RHS in the same env
        for name, rhs in expr.bindings:
            val = lambEval(rhs, new_env)
            new_env[name] = val
            if isinstance(val, Closure):
                val.env[name] = val

        # Patch mutually recursive closure envs
        for item in new_env.values():
            if isinstance(item, Closure):
                for bind_name, _ in expr.bindings:
                    item.env[bind_name] = new_env[bind_name]

        result: Value = nil
        for idx, body_expr in enumerate(expr.body):
            is_last = idx == len(expr.body) - 1
            result = lambEval(body_expr, new_env, is_tail and is_last)
        return result

    # DefMacro-expression
    if isinstance(expr, DefMacroExpr):
        env[expr.name] = Macro(expr.params, expr.body)
        return "<macro defined>"

    raise EvalError(f"Unknown expression type: {expr}")


def trampoline(result: Value) -> Value:
    while isinstance(result, Thunk):
        result = result.func()
    return result


def applyFunc(func_val: Value, args: list[Value], is_tail: bool = False) -> Value:
    if isinstance(func_val, Closure):
        result: Value = func_val
        for i, arg in enumerate(args):
            if not isinstance(result, Closure):
                return result
            new_env = result.env.copy()
            new_env[result.param] = arg
            # If this is the last argument and we're in tail position,
            # use tail call optimization
            is_last_arg = i == len(args) - 1
            result = lambEval(result.body, new_env, is_tail and is_last_arg)
            if not isinstance(result, Closure):
                return result
        return result
    if isinstance(func_val, Builtin):
        builtin_result: Value = func_val
        for arg in args:
            if not isinstance(builtin_result, Builtin):
                return builtin_result
            builtin_result = builtin_result.func(arg)
        # Handle 0-argument builtins
        if len(args) == 0:
            if isinstance(builtin_result, Builtin):
                # 0-argument builtins still need a dummy argument
                return builtin_result.func(nil)
            return builtin_result
        return builtin_result
    if isinstance(func_val, Macro):
        # This should not happen - macros should be expanded before evaluation
        raise EvalError("tried to apply a macro as a function - macro expansion failed")
    raise EvalError("tried to apply a non-function value")

def _qq_eval(expr: Expr, env: dict[str, Value], depth: int) -> Expr:
    if isinstance(expr, QuasiQuoteExpr):
        return QuasiQuoteExpr(_qq_eval(expr.expr, env, depth + 1))

    if isinstance(expr, UnquoteExpr):
        if depth == 0:
            return _qq_eval(expr.expr, env, depth)
        return UnquoteExpr(_qq_eval(expr.expr, env, depth - 1))

    if isinstance(expr, Application):
        return Application(
            _qq_eval(expr.func, env, depth),
            [_qq_eval(a, env, depth) for a in expr.args],
        )

    if isinstance(expr, Abstraction):
        return Abstraction(expr.param, _qq_eval(expr.body, env, depth))

    if isinstance(expr, IfExpr):
        return IfExpr(
            _qq_eval(expr.cond, env, depth),
            _qq_eval(expr.then_branch, env, depth),
            _qq_eval(expr.else_branch, env, depth),
        )
        
    return expr

def evalQuasiquote(expr: Expr, env: dict[str, Value]) -> Value:
    rewritten = _qq_eval(expr.expr, env, depth=0)
    if not isinstance(rewritten, Expr):
        return rewritten
    return lambEval(rewritten, env)


# ============================================================================
# macro.py
# ============================================================================
    # Expand application
    if isinstance(expr, Application) and isinstance(expr.func, Variable):
        macro = env.get(expr.func.name)
        if isinstance(macro, Macro):
            args = expr.args
            if len(args) != len(macro.params):
                raise MacroExpansionError(
                    f"Macro '{expr.func.name}' expects {len(macro.params)} "
                    f"args but got {len(args)}"
                )
            mapping = dict(zip(macro.params, args))
            expanded = lambMacroSubstitute(macro.body, mapping)
            return lambMacroExpand(expanded, env)

    if isinstance(expr, Application):
        new_func = lambMacroExpand(expr.func, env)
        if new_func is None:
            new_func = expr.func
        new_args = []
        for arg in expr.args:
            ea = lambMacroExpand(arg, env)
            new_args.append(ea if ea is not None else arg)
        return Application(new_func, new_args)
    if isinstance(expr, Abstraction):
        new_body = lambMacroExpand(expr.body, env)
        if new_body is None:
            new_body = expr.body
        return Abstraction(expr.param, new_body)
    if isinstance(expr, DefineExpr):
        new_value = lambMacroExpand(expr.value, env)
        if new_value is None:
            new_value = expr.value
        return DefineExpr(expr.name, new_value)
    if isinstance(expr, IfExpr):
        new_cond = lambMacroExpand(expr.cond, env)
        if new_cond is None:
            new_cond = expr.cond
        new_then = lambMacroExpand(expr.then_branch, env)
        if new_then is None:
            new_then = expr.then_branch
        new_else = lambMacroExpand(expr.else_branch, env)
        if new_else is None:
            new_else = expr.else_branch
        return IfExpr(new_cond, new_then, new_else)

    if isinstance(expr, QuasiQuoteExpr):
        return qqWalk(expr.expr, env)
        
    if isinstance(expr, DefMacroExpr):
        macro = Macro(expr.params, expr.body)
        env[expr.name] = macro
        return None

    return expr

def _qq_walk(expr: Expr, env: dict[str, Value], depth: int = 0) -> Expr:
    if isinstance(expr, UnquoteExpr):
        if depth == 0:
            inner = _qq_walk(expr.expr, env, depth)
            expanded = lambMacroExpand(inner, env)
            return expanded if expanded is not None else inner
        return UnquoteExpr(_qq_walk(expr.expr, env, depth - 1))

    if isinstance(expr, QuasiQuoteExpr):
        return QuasiQuoteExpr(_qq_walk(expr.expr, env, depth + 1))

    if isinstance(expr, Application):
        return Application(
            _qq_walk(expr.func, env, depth),
            [_qq_walk(a, env, depth) for a in expr.args],
        )
    elif isinstance(expr, Abstraction):
        return Abstraction(expr.param, _qq_walk(expr.body, env, depth))
    elif isinstance(expr, IfExpr):
        return IfExpr(
            _qq_walk(expr.cond, env, depth),
            _qq_walk(expr.then_branch, env, depth),
            _qq_walk(expr.else_branch, env, depth),
        )
    elif isinstance(expr, DefineExpr):
        return DefineExpr(expr.name, _qq_walk(expr.value, env, depth))
    elif isinstance(expr, DefMacroExpr):
        return DefMacroExpr(
            expr.name, expr.params, _qq_walk(expr.body, env, depth)
        )
    elif isinstance(expr, LetRec):
        new_bindings = [(n, _qq_walk(v, env, depth)) for n, v in expr.bindings]
        new_body     = [_qq_walk(b, env, depth) for b in expr.body]
        return LetRec(new_bindings, new_body)

    if isinstance(expr, (QuoteExpr, Variable, Literal)):
        return expr

    return expr

def qqWalk(expr: Expr, env: Dict[str, Value]) -> Expr:
    return _qq_walk(expr, env)


# ============================================================================
# builtinsmodule.py
# ============================================================================
    env: Dict[str, Value] = {}

    # Booleans
    env["true"] = True
    env["false"] = False

    # Arithmetic (curried)
    def add(x: Value) -> Value:
        xi = _to_int(x)

        def add_inner(y: Value) -> Value:
            yi = _to_int(y)
            return xi + yi

        return Builtin(add_inner)

    def sub(x: Value) -> Value:
        xi = _to_int(x)

        def sub_inner(y: Value) -> Value:
            yi = _to_int(y)
            return xi - yi

        return Builtin(sub_inner)

    def mul(x: Value) -> Value:
        xi = _to_int(x)

        def mul_inner(y: Value) -> Value:
            yi = _to_int(y)
            return xi * yi

        return Builtin(mul_inner)

    # Integer division (floored)
    def div(x: Value) -> Value:
        xi = _to_int(x)

        def div_inner(y: Value) -> Value:
            yi = _to_int(y)
            return xi // yi

        return Builtin(div_inner)

    env["+"] = Builtin(add)
    env["-"] = Builtin(sub)
    env["*"] = Builtin(mul)
    env["/"] = Builtin(div)

    def mod(x: Value) -> Value:
        xi = _to_int(x)

        def mod_inner(y: Value) -> Value:
            yi = _to_int(y)
            return xi % yi

        return Builtin(mod_inner)

    env["%"] = Builtin(mod)
    env["mod"] = Builtin(mod)  # Alias for consistency

    # Additional comparison operators
    def le(x: Value) -> Value:
        xi = _to_int(x)

        def le_inner(y: Value) -> Value:
            yi = _to_int(y)
            return xi <= yi

        return Builtin(le_inner)

    def gt(x: Value) -> Value:
        xi = _to_int(x)

        def gt_inner(y: Value) -> Value:
            yi = _to_int(y)
            return xi > yi

        return Builtin(gt_inner)

    def ge(x: Value) -> Value:
        xi = _to_int(x)

        def ge_inner(y: Value) -> Value:
            yi = _to_int(y)
            return xi >= yi

        return Builtin(ge_inner)

    def ne(x: Value) -> Value:
        xi = _to_int(x)

        def ne_inner(y: Value) -> Value:
            yi = _to_int(y)
            return xi != yi

        return Builtin(ne_inner)

    env["<="] = Builtin(le)
    env[">"] = Builtin(gt)
    env[">="] = Builtin(ge)
    env["!="] = Builtin(ne)

    # String conversion
    def str_fn(x: Value) -> Value:
        return valueToString(x)

    # String concatenation
    def concat(x: Value) -> Value:
        if not isinstance(x, str):
            raise TypeError("Expected string")

        def concat_inner(y: Value) -> Value:
            if not isinstance(y, str):
                raise TypeError("Expected string")
            return x + y

        return Builtin(concat_inner)

    env["str"] = Builtin(str_fn)
    env["++"] = Builtin(concat)  # String concatenation operator

    # Type checking functions
    def is_number(x: Value) -> Value:
        return _is_int(x)

    def is_boolean(x: Value) -> Value:
        return isinstance(x, bool)

    def is_string(x: Value) -> Value:
        return isinstance(x, str)

    def is_list(x: Value) -> Value:
        return isinstance(x, Pair) or x is nil

    def is_function(x: Value) -> Value:
        return isinstance(x, Builtin)

    env["isNumber"] = Builtin(is_number)
    env["isBoolean"] = Builtin(is_boolean)
    env["isString"] = Builtin(is_string)
    env["isList"] = Builtin(is_list)
    env["isFunction"] = Builtin(is_function)

    # Equality
    def eq(x: Value) -> Value:
        xi = _to_int(x)

        def eq_inner(y: Value) -> Value:
            yi = _to_int(y)
            return xi == yi

        return Builtin(eq_inner)

    env["="] = Builtin(eq)

    # Less-than
    def lt(x: Value) -> Value:
        xi = _to_int(x)

        def lt_inner(y: Value) -> Value:
            yi = _to_int(y)
            return xi < yi

        return Builtin(lt_inner)

    env["<"] = Builtin(lt)

    # Logical negation
    def not_fn(x: Value) -> Value:
        if not isinstance(x, bool):
            raise TypeError("Expected boolean")
        return not x

    env["not"] = Builtin(not_fn)

    # Conjunction / disjunction
    def and_fn(x: Value) -> Value:
        if not isinstance(x, bool):
            raise TypeError("Expected boolean")

        def inner(y: Value) -> Value:
            if not isinstance(y, bool):
                raise TypeError("Expected boolean")
            return x and y

        return Builtin(inner)

    def or_fn(x: Value) -> Value:
        if not isinstance(x, bool):
            raise TypeError("Expected boolean")

        def inner(y: Value) -> Value:
            if not isinstance(y, bool):
                raise TypeError("Expected boolean")
            return x or y

        return Builtin(inner)

    env["and"] = Builtin(and_fn)
    env["or"] = Builtin(or_fn)

    # Printing (returns nil)
    def pr(x: Value) -> Value:
        print(valueToString(x))
        return nil

    env["print"] = Builtin(pr)

    # Lists
    def cons(x: Value) -> Value:
        return Builtin(lambda y: Pair(x, y))

    def head_fn(p: Value) -> Value:
        if not isinstance(p, Pair):
            raise TypeError("head expects a pair")
        return p.head

    def tail_fn(p: Value) -> Value:
        if not isinstance(p, Pair):
            raise TypeError("tail expects a pair")
        return p.tail

    def is_nil(p: Value) -> Value:
        return p is nil

    env["cons"] = Builtin(cons)
    env["head"] = Builtin(head_fn)
    env["tail"] = Builtin(tail_fn)
    env["isNil"] = Builtin(is_nil)
    env["nil"] = nil

    # Gensym for hygienic macros
    _gensym_counter = count()

    def gensym_fn(x: Value) -> Value:
        return f"__gensym_{next(_gensym_counter)}"

    env["gensym"] = Builtin(gensym_fn)

    def quote_fn(x: Value) -> Value:
        return x

    env["quote"] = Builtin(quote_fn)

    return env


# ============================================================================
# printer.py
# ============================================================================
    Abstraction,
    Application,
    DefineExpr,
    DefMacroExpr,
    Expr,
    IfExpr,
    LetRec,
    Literal,
    QuasiQuoteExpr,
    QuoteExpr,
    UnquoteExpr,
    Variable,
)


def lambPrint(expr: Expr) -> str:
    if isinstance(expr, Variable):
        return expr.name
    elif isinstance(expr, Literal):
        return expr.value
    elif isinstance(expr, Abstraction):
        return f"(lambda {expr.param}. {lambPrint(expr.body)})"
    elif isinstance(expr, Application):
        parts = [lambPrint(expr.func)] + [lambPrint(arg) for arg in expr.args]
        return f"({' '.join(parts)})"
    elif isinstance(expr, QuasiQuoteExpr):
        return f"`({lambPrint(expr.expr)})"
    elif isinstance(expr, UnquoteExpr):
        return f",({lambPrint(expr.expr)})"
    elif isinstance(expr, QuoteExpr):
        return f"'({lambPrint(expr.value)})"
    elif isinstance(expr, LetRec):
        binds = " ".join([f"({name} {lambPrint(val)})" for name, val in expr.bindings])
        bodies = " ".join([lambPrint(b) for b in expr.body])
        return f"(letrec ({binds}) {bodies})"
    elif isinstance(expr, IfExpr):
        cond = lambPrint(expr.cond)
        then_branch = lambPrint(expr.then_branch)
        else_branch = lambPrint(expr.else_branch)
        return f"(if {cond} {then_branch} {else_branch})"
    elif isinstance(expr, DefineExpr):
        return f"(define {expr.name} {lambPrint(expr.value)})"
    elif isinstance(expr, DefMacroExpr):
        params = " ".join(expr.params)
        return f"(defmacro {expr.name} ({params}) {lambPrint(expr.body)})"
    else:
        raise TypeError(f"Unknown expression type: {expr}")


# ============================================================================
# Web Interface
# ============================================================================

class LambdoraWebREPL:
    def __init__(self):
        self.env = lambMakeTopEnv()
        self.output = StringIO()
        self.error_output = StringIO()
        self.original_stdout = sys.stdout
        sys.stdout = self.output
        self._load_stdlib()
    
    def _load_stdlib(self):
        try:
            stdlib_content = """
; std.lamb — Lambdora Standard Library\n\n; === Basic helpers ===\n(define id       (lambda x. x))\n(define const    (lambda x. (lambda y. x)))\n\n; === Predicates ===\n(define isZero   (lambda n. (= n 0)))\n\n; === Arithmetic shortcuts ===\n(define double   (lambda x. (+ x x)))\n(define triple   (lambda x. (+ x (double x))))\n\n; === Recursive definitions using letrec ===\n; Factorial\n(define fact\n  (letrec ((fact (lambda n.\n                   (if (= n 0)\n                       1\n                       (* n (fact (- n 1)))))))\n    fact))\n\n; Fibonacci\n(define fib\n  (letrec ((fib (lambda n.\n                  (if (< n 2)\n                      n\n                      (+ (fib (- n 1)) (fib (- n 2)))))))\n    fib))\n\n; === Fold and variants ===\n(define foldlHelper\n  (lambda f. (lambda acc. (lambda lst.\n    (if (isNil lst)\n        acc\n        (foldlHelper f (f acc (head lst)) (tail lst)))))))\n\n(define foldl\n  (lambda f. (lambda acc. (lambda lst.\n    (foldlHelper f acc lst)))))\n\n; === Higher-order helpers ===\n(define compose\n  (lambda f. (lambda g. (lambda x. (f (g x))))))\n\n; Right fold\n(define foldr\n  (lambda f. (lambda acc. (lambda lst.\n    (if (isNil lst)\n        acc\n        (f (head lst) (((foldr f) acc) (tail lst))))))))\n\n; List append\n(define append\n  (lambda xs. (lambda ys.\n    (if (isNil xs)\n        ys\n        (cons (head xs) ((append (tail xs)) ys))))))\n\n; === Basic list operations ===\n(define reverse\n  (lambda lst. ((foldl (lambda acc. (lambda x. (cons x acc))) nil) lst)))\n\n; === Range generation (tail-recursive) ===\n(define rangeHelper\n  (lambda i. (lambda acc.\n    (if (< i 0)\n        acc\n        (rangeHelper (- i 1) (cons i acc))))))\n\n(define range\n  (lambda n.\n    (rangeHelper (- n 1) nil)))\n\n; === List operations ===\n(define map\n  (lambda f. (lambda lst.\n    (if (isNil lst)\n        nil\n        (cons (f (head lst))\n              ((map f) (tail lst)))))))\n\n(define filter\n  (lambda pred. (lambda lst.\n    (if (isNil lst)\n        nil\n        (let h (head lst)\n          (let t ((filter pred) (tail lst))\n            (if (pred h)\n                (cons h t)\n                t)))))))\n\n(define length\n  (lambda lst. ((foldl (lambda n. (lambda _. (+ n 1))) 0) lst)))\n\n(define sum\n  (lambda lst. ((foldl (lambda a. (lambda b. (+ a b))) 0) lst)))\n\n; === List generation ===\n(define ones\n  (lambda n.\n    ((foldl (lambda acc. (lambda _. (cons 1 acc))) nil) (range n))))\n\n; === Simple sums of ones ===\n(define sumOnes\n  (lambda n.\n    ((foldl (lambda a. (lambda b. (+ a b))) 0) (ones n))))\n\n; === Let-binding macros ===\n(defmacro let  (var val body)\n  `((lambda ,var . ,body) ,val))\n\n; === Control-flow macros ===\n(defmacro when   (cond body)       `(if ,cond ,body nil))\n(defmacro unless (cond body)       `(if (not ,cond) ,body nil))\n(defmacro begin  (a b)             `(let __ignore ,a ,b))\n\n; === Short-circuit logic ===\n(defmacro and2 (a b)               `(if ,a ,b false))\n(defmacro or2  (a b)               `(if ,a true ,b))\n\n; === Cond macro (supports up to 4 branches + default) ===\n(defmacro cond (a1 b1 a2 b2 a3 b3 a4 b4 default)\n  `(if ,a1 ,b1\n    (if ,a2 ,b2\n      (if ,a3 ,b3\n        (if ,a4 ,b4\n          ,default)))))\n; Usage: (cond test1 result1 test2 result2 ... [default])\n; For more branches, nest conds or extend this macro.\n
"""
            tokens = lambTokenize(stdlib_content)
            for expr in lambParseAll(tokens):
                expanded = lambMacroExpand(expr, self.env)
                if expanded is not None:
                    trampoline(lambEval(expanded, self.env, is_tail=True))
        except Exception as e:
            print(f"Warning: Could not load standard library: {e}")
    
    def evaluate(self, code: str) -> str:
        try:
            self.output = StringIO()
            self.error_output = StringIO()
            sys.stdout = self.output
            tokens = lambTokenize(code)
            expressions = list(lambParseAll(tokens))
            if not expressions:
                return "No expressions to evaluate."
            results = []
            for expr in expressions:
                expanded = lambMacroExpand(expr, self.env)
                if expanded is None:
                    continue
                result = trampoline(lambEval(expanded, self.env, is_tail=True))
                if result is not nil and not (
                    isinstance(result, str) and result.startswith("<defined ")
                ):
                    results.append(valueToString(result))
            output = self.output.getvalue()
            if results:
                output += "\n".join(results)
            return output if output else "Code executed successfully (no output)"
        except LambError as err:
            error_msg = format_lamb_error(err)
            return f"Error: {error_msg}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
        finally:
            sys.stdout = self.original_stdout
    
    def get_environment(self) -> dict:
        return {k: v for k, v in self.env.items() if not k.startswith("__")}
    
    def reset_environment(self):
        self.env = lambMakeTopEnv()
        self._load_stdlib()

repl = LambdoraWebREPL()

def evaluate_code(code: str) -> str:
    return repl.evaluate(code)

def reset_repl():
    repl.reset_environment()
    return "REPL environment reset."

def get_help() -> str:
    return """
Lambdora Web REPL Help:

Basic Syntax:
- (define name value)     # Define a variable
- (lambda param. body)    # Create a function
- (if cond then else)     # Conditional
- (print expr)            # Print expression

Examples:
- (print "Hello, World!")
- (define inc (lambda x. (+ x 1)))
- ((lambda x. (* x x)) 5)

Use Ctrl+Enter or Cmd+Enter to run code.
"""