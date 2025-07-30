#!/usr/bin/env python3

import os
import sys
from pathlib import Path

def read_file(path: Path) -> str:
    return path.read_text(encoding='utf-8')

def build_lambdora_bundle():
    project_root = Path(__file__).parent.parent
    src_dir = project_root / "src" / "lambdora"
    
    files_to_include = [
        "values.py",
        "errors.py", 
        "tokenizer.py",
        "parser.py",
        "evaluator.py",
        "macro.py",
        "builtinsmodule.py",
        "printer.py",
        "stdlib/std.lamb"
    ]
    
    bundle_content = [
        '"""',
        'Lambdora - A Lisp-inspired functional language',
        'Bundled for Pyodide web deployment',
        '"""',
        '',
        'import sys',
        'from io import StringIO',
        'from typing import Optional, Any, List, Union, Callable, Dict',
        'from collections import defaultdict',
        'from dataclasses import dataclass',
        '',
        '# ============================================================================',
        '# AST Module (needed for Expr type)',
        '# ============================================================================',
        '',
        'from typing import Union, List',
        '',
        '@dataclass',
        'class Expr:',
        '    pass',
        '',
        '@dataclass',
        'class Variable(Expr):',
        '    name: str',
        '',
        '@dataclass',
        'class Literal(Expr):',
        '    value: str',
        '',
        '@dataclass',
        'class Abstraction(Expr):',
        '    param: str',
        '    body: Expr',
        '',
        '@dataclass',
        'class Application(Expr):',
        '    func: Expr',
        '    args: List[Expr]',
        '',
        '@dataclass',
        'class DefineExpr(Expr):',
        '    name: str',
        '    value: Expr',
        '',
        '@dataclass',
        'class IfExpr(Expr):',
        '    cond: Expr',
        '    then_branch: Expr',
        '    else_branch: Expr',
        '',
        '@dataclass',
        'class DefMacroExpr(Expr):',
        '    name: str',
        '    params: List[str]',
        '    body: Expr',
        '',
        '@dataclass',
        'class QuoteExpr(Expr):',
        '    value: Expr',
        '',
        '@dataclass',
        'class QuasiQuoteExpr(Expr):',
        '    expr: Expr',
        '',
        '@dataclass',
        'class UnquoteExpr(Expr):',
        '    expr: Expr',
        '',
        '@dataclass',
        'class LetRec(Expr):',
        '    bindings: List[tuple[str, Expr]]',
        '    body: List[Expr]',
        '',
        '# ============================================================================',
        '# Values and Types',
        '# ============================================================================',
    ]
    
    for file_name in files_to_include:
        file_path = src_dir / file_name
        
        if not file_path.exists():
            print(f"Warning: {file_path} not found, skipping...")
            continue
            
        content = read_file(file_path)
        
        if file_name == "stdlib/std.lamb":  
            continue
            
        lines = content.split('\n')
        start_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('"""') and start_idx == 0:
                start_idx = i + 1
                break
            elif line.strip().startswith("'''") and start_idx == 0:
                start_idx = i + 1
                break
        
        for i in range(start_idx, len(lines)):
            if lines[i].strip().endswith('"""') or lines[i].strip().endswith("'''"):
                start_idx = i + 1
                break
        
        while start_idx < len(lines) and (
            lines[start_idx].strip().startswith('import ') or 
            lines[start_idx].strip().startswith('from ') or
            lines[start_idx].strip() == '' or
            lines[start_idx].strip().startswith('from __future__')
        ):
            start_idx += 1
        
        content = '\n'.join(lines[start_idx:])
        
        if file_name == "printer.py":
            content = content.replace("from .astmodule import (\n    Abstraction,\n    Application,\n    DefineExpr,\n    DefMacroExpr,\n    Expr,\n    IfExpr,\n    LetRec,\n    Literal,\n    QuasiQuoteExpr,\n    QuoteExpr,\n    UnquoteExpr,\n    Variable,\n)", "# AST classes are already defined above")
        
        bundle_content.extend([
            f'# ============================================================================',
            f'# {file_name}',
            f'# ============================================================================',
            content,
            ''
        ])
    
    bundle_content.extend([
        '# ============================================================================',
        '# Web Interface',
        '# ============================================================================',
        '',
        'class LambdoraWebREPL:',
        '    def __init__(self):',
        '        self.env = lambMakeTopEnv()',
        '        self.output = StringIO()',
        '        self.error_output = StringIO()',
        '        self.original_stdout = sys.stdout',
        '        sys.stdout = self.output',
        '        self._load_stdlib()',
        '    ',
        '    def _load_stdlib(self):',
        '        try:',
        '            stdlib_content = """',
    ])
    
    stdlib_path = src_dir / "stdlib" / "std.lamb"
    if stdlib_path.exists():
        stdlib_content = read_file(stdlib_path)
        stdlib_content = stdlib_content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
        bundle_content.append(stdlib_content)
    
    bundle_content.extend([
        '"""',
        '            tokens = lambTokenize(stdlib_content)',
        '            for expr in lambParseAll(tokens):',
        '                expanded = lambMacroExpand(expr, self.env)',
        '                if expanded is not None:',
        '                    trampoline(lambEval(expanded, self.env, is_tail=True))',
        '        except Exception as e:',
        '            print(f"Warning: Could not load standard library: {e}")',
        '    ',
        '    def evaluate(self, code: str) -> str:',
        '        try:',
        '            self.output = StringIO()',
        '            self.error_output = StringIO()',
        '            sys.stdout = self.output',
        '            tokens = lambTokenize(code)',
        '            expressions = list(lambParseAll(tokens))',
        '            if not expressions:',
        '                return "No expressions to evaluate."',
        '            results = []',
        '            for expr in expressions:',
        '                expanded = lambMacroExpand(expr, self.env)',
        '                if expanded is None:',
        '                    continue',
        '                result = trampoline(lambEval(expanded, self.env, is_tail=True))',
        '                if result is not nil and not (',
        '                    isinstance(result, str) and result.startswith("<defined ")',
        '                ):',
        '                    results.append(valueToString(result))',
        '            output = self.output.getvalue()',
        '            if results:',
        '                output += "\\n".join(results)',
        '            return output if output else "Code executed successfully (no output)"',
        '        except LambError as err:',
        '            error_msg = format_lamb_error(err)',
        '            return f"Error: {error_msg}"',
        '        except Exception as e:',
        '            return f"Unexpected error: {str(e)}"',
        '        finally:',
        '            sys.stdout = self.original_stdout',
        '    ',
        '    def get_environment(self) -> dict:',
        '        return {k: v for k, v in self.env.items() if not k.startswith("__")}',
        '    ',
        '    def reset_environment(self):',
        '        self.env = lambMakeTopEnv()',
        '        self._load_stdlib()',
        '',
        'repl = LambdoraWebREPL()',
        '',
        'def evaluate_code(code: str) -> str:',
        '    return repl.evaluate(code)',
        '',
        'def reset_repl():',
        '    repl.reset_environment()',
        '    return "REPL environment reset."',
        '',
        'def get_help() -> str:',
        '    return """',
        'Lambdora Web REPL Help:',
        '',
        'Basic Syntax:',
        '- (define name value)     # Define a variable',
        '- (lambda param. body)    # Create a function',
        '- (if cond then else)     # Conditional',
        '- (print expr)            # Print expression',
        '',
        'Examples:',
        '- (print "Hello, World!")',
        '- (define inc (lambda x. (+ x 1)))',
        '- ((lambda x. (* x x)) 5)',
        '',
        'Use Ctrl+Enter or Cmd+Enter to run code.',
        '"""',
    ])
    
    bundle_path = Path(__file__).parent / "lambdora_bundle.py"
    bundle_path.write_text('\n'.join(bundle_content), encoding='utf-8')
    
    print(f"Bundle created: {bundle_path}")
    print(f"Bundle size: {bundle_path.stat().st_size} bytes")

if __name__ == "__main__":
    build_lambdora_bundle() 