let pyodide = null;
let codeMirror = null;

const examples = {
    hello: `(print "Hello, World!")
(print "Welcome to Lambdora!")`,
    
    fizzbuzz: `; FizzBuzz in Lambdora
(define fizzbuzz
  (lambda n.
    (if (= (mod n 15) 0) "FizzBuzz"
        (if (= (mod n 3) 0) "Fizz"
            (if (= (mod n 5) 0) "Buzz"
                (str n))))))

; Helper to print numbers 1 to n
(define printRange
  (lambda n.
    (letrec ((loop (lambda i.
                     (if (> i n)
                         nil
                         (let __temp (print (fizzbuzz i))
                           (loop (+ i 1)))))))
      (loop 1))))

; Run FizzBuzz for numbers 1-20
(print "FizzBuzz 1-20:")
(printRange 20)`,
    
    church: `; Church Numerals - Functional Programming Concepts
; Church numeral constructors
(define zero (lambda f. (lambda x. x)))
(define one (lambda f. (lambda x. (f x))))
(define two (lambda f. (lambda x. (f (f x)))))

; Successor function
(define succ (lambda n. (lambda f. (lambda x. (f ((n f) x))))))

; Convert Church numeral to integer
(define churchToNum (lambda n. ((n (lambda x. (+ x 1))) 0)))

; Addition of Church numerals
(define add (lambda n. (lambda m. (lambda f. (lambda x. ((n f) ((m f) x)))))))

; Test Church numerals
(print "Church numerals:")
(print (++ "zero = " (str (churchToNum zero))))
(print (++ "one = " (str (churchToNum one))))
(print (++ "two = " (str (churchToNum two))))

(define three (succ two))
(print (++ "three = " (str (churchToNum three))))

(define four ((add two) two))
(print (++ "two + two = " (str (churchToNum four))))`,
    
    macros: `; Hygienic Macro Examples
(defmacro when (cond body)
  \`(if ,cond ,body nil))

(defmacro unless (cond body)
  \`(if (not ,cond) ,body nil))

(defmacro and2 (a b)
  \`(if ,a ,b false))

(defmacro or2 (a b)
  \`(if ,a true ,b))

; Test macros
(print "Macro examples:")
(when true (print "This should print"))
(unless false (print "This should also print"))
(print (++ "and2(true, false) = " (str (and2 true false))))
(print (++ "or2(false, true) = " (str (or2 false true))))`
};

async function init() {
    try {
        pyodide = await loadPyodideModule();
        await loadLambdora();
        initCodeMirror();
        setupEventListeners();
        document.getElementById('loading').style.display = 'none';

    } catch (error) {
        console.error('Initialization failed:', error);
        showError('Failed to initialize Lambdora. Please refresh the page.');
    }
}

async function loadPyodideModule() {
    console.log('Loading Pyodide...');
    const pyodide = await globalThis.loadPyodide({
        indexURL: "https://cdn.jsdelivr.net/pyodide/v0.24.1/full/"
    });
    console.log('Pyodide loaded successfully');
    return pyodide;
}

async function loadLambdora() {
    console.log('Loading Lambdora...');
    
    try {
        const files = [
            'astmodule.py',
            'values.py',
            'errors.py', 
            'tokenizer.py',
            'parser.py',
            'evaluator.py',
            'macro.py',
            'builtinsmodule.py',
            'printer.py'
        ];
        
        let allCode = '';
        let futureImports = '';
        
        for (const file of files) {
            console.log(`Loading ${file}...`);
            const response = await fetch(`/src/lambdora/${file}`);
            if (!response.ok) {
                throw new Error(`Failed to load ${file}: ${response.status}`);
            }
            let code = await response.text();
            console.log(`Loaded ${file}, size: ${code.length} chars`);
            
            const futureMatch = code.match(/from __future__ import .*?(?=\n)/);
            if (futureMatch) {
                futureImports += futureMatch[0] + '\n';
                code = code.replace(/from __future__ import .*?\n/, '');
            }
            

            code = code.replace(/from \.[a-zA-Z0-9_]+ import\s*\([\s\S]*?\)\s*\n/g, '');
            code = code.replace(/from \.[a-zA-Z0-9_]+ import.*?\n/g, '');
            code = code.replace(/from src\.[a-zA-Z0-9_]+ import\s*\([\s\S]*?\)\s*\n/g, '');
            code = code.replace(/from src\.[a-zA-Z0-9_]+ import.*?\n/g, '');

            if (file === 'errors.py') {
                code = code.replace(/from colorama import.*?\n/g, '');
                code = code.replace(/_colorama_init\(.*?\)/g, '');
                code = code.replace(
                    /from colorama import Fore, Style\nfrom colorama import init as _colorama_init\n\n_colorama_init\(autoreset=True\)/,
                    `# colorama is not available in Pyodide/web, so we stub out color constants
class _Stub:
    def __getattr__(self, name):
        return ''

Fore = Style = _Stub()

def _colorama_init(*args, **kwargs):
    pass`
                );
                
                code = code.replace(
                    /f"\{Style\.BRIGHT \+ Fore\.RED\}\{type\(err\)\.__name__\}\{Style\.RESET_ALL\}: \{err\}"/,
                    'f"{type(err).__name__}: {err}"'
                );
                code = code.replace(
                    /f"\{Style\.DIM\}\{err\.snippet\}\{Style\.RESET_ALL\}\\n"/,
                    'f"{err.snippet}\\n"'
                );
                code = code.replace(
                    /f"\{Style\.DIM\}\{caret\}\{Style\.RESET_ALL\}"/,
                    'f"{caret}"'
                );
                code = code.replace(
                    /f"invalid syntax\.\{Style\.RESET_ALL\}"/,
                    'f"invalid syntax."'
                );
                code = code.replace(
                    /f"closed with quotes\.\{Style\.RESET_ALL\}"/,
                    'f"closed with quotes."'
                );
                code = code.replace(
                    /f"parentheses\.\{Style\.RESET_ALL\}"/,
                    'f"parentheses."'
                );
                code = code.replace(
                    /f"before use\.\{Style\.RESET_ALL\}"/,
                    'f"before use."'
                );
                code = code.replace(
                    /f"variables\.\{Style\.RESET_ALL\}"/,
                    'f"variables."'
                );
                code = code.replace(
                    /f"body\)\{Style\.RESET_ALL\}"/,
                    'f"body)"'
                );
            }
            
            allCode += `\n# ============================================================================\n`;
            allCode += `# ${file}\n`;
            allCode += `# ============================================================================\n`;
            allCode += code + '\n';
        }
        
        if (futureImports) {
            allCode = futureImports + '\n' + allCode;
        }
        
        console.log('Executing all code together...');
        console.log('Combined code length:', allCode.length);
        console.log('First 1000 chars of combined code:', allCode.substring(0, 1000));
        try {
            await pyodide.runPythonAsync(allCode);
            console.log('Successfully executed all files');
        } catch (error) {
            console.error('Error executing combined code:', error);
            console.error('Error details:', error.message);
            throw new Error(`Failed to execute combined code: ${error.message}`);
        }
        
        console.log('Loading standard library...');
        const stdlibResponse = await fetch('/src/lambdora/stdlib/std.lamb');
        let stdlibCode = '';
        if (stdlibResponse.ok) {
            stdlibCode = await stdlibResponse.text();
            console.log(`Loaded stdlib, size: ${stdlibCode.length} chars`);
            try {
                await pyodide.runPythonAsync(`
# Load standard library
stdlib_content = """${stdlibCode.replace(/"/g, '\\"').replace(/\n/g, '\\n')}"""
tokens = lambTokenize(stdlib_content)
for expr in lambParseAll(tokens):
    expanded = lambMacroExpand(expr, lambMakeTopEnv())
    if expanded is not None:
        trampoline(lambEval(expanded, lambMakeTopEnv(), is_tail=True))
`);
                console.log('Successfully loaded stdlib');
            } catch (error) {
                console.error('Error loading stdlib:', error);
            }
        }
        
        await pyodide.runPythonAsync(`
import sys
from io import StringIO

# Get the stdlib content from JavaScript
stdlib_content = """${stdlibCode.replace(/"/g, '\\"').replace(/\n/g, '\\n')}"""

class LambdoraWebREPL:
    def __init__(self):
        self.env = lambMakeTopEnv()
        self.output = StringIO()
        self.original_stdout = sys.stdout
        sys.stdout = self.output
        self._load_stdlib()
    
    def _load_stdlib(self):
        try:
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
                output += "\\n".join(results)
            return output if output else "Code executed successfully (no output)"
        except Exception as e:
            return f"Error: {str(e)}"
        finally:
            sys.stdout = self.original_stdout

repl = LambdoraWebREPL()

def evaluate_code(code: str) -> str:
    return repl.evaluate(code)
`);
        
        console.log('Lambdora loaded successfully');
    } catch (error) {
        console.error('Failed to load Lambdora:', error);
        throw new Error('Failed to load Lambdora. Please check the console for details.');
    }
}

function initCodeMirror() {
    const textarea = document.getElementById('code-editor');
    codeMirror = CodeMirror.fromTextArea(textarea, {
        mode: 'commonlisp',
        theme: 'monokai',
        lineNumbers: true,
        autoCloseBrackets: true,
        matchBrackets: true,
        indentUnit: 2,
        tabSize: 2,
        lineWrapping: true,
        extraKeys: {
            'Ctrl-Enter': runCode,
            'Cmd-Enter': runCode
        }
    });
}

function setupEventListeners() {
    document.getElementById('run-btn').addEventListener('click', runCode);
    document.getElementById('clear-btn').addEventListener('click', clearCode);
    document.getElementById('clear-output-btn').addEventListener('click', clearOutput);
    document.getElementById('examples-select').addEventListener('change', handleExampleSelect);
    document.getElementById('upload-btn').addEventListener('click', () => {
        document.getElementById('file-upload').click();
    });
    document.getElementById('file-upload').addEventListener('change', handleFileUpload);
}

async function runCode() {
    const code = codeMirror.getValue();
    if (!code.trim()) {
        showError('Please enter some code to run.');
        return;
    }
    
    try {
        showOutput('Running...', 'info');
        
        const result = await pyodide.runPythonAsync(`
result = evaluate_code("""${code.replace(/"/g, '\\"')}""")
result
`);
        
        if (result && result.trim()) {
            showOutput(result, 'success');
        } else {
            showOutput('Code executed successfully (no output)', 'info');
        }
        
    } catch (error) {
        console.error('Execution error:', error);
        showError(`Execution error: ${error.message}`);
    }
}

function clearCode() {
    codeMirror.setValue('');
}

function clearOutput() {
    const output = document.getElementById('output');
    output.textContent = '';
    output.className = 'output-content';
}

function showOutput(message, type = 'info') {
    const output = document.getElementById('output');
    output.textContent = message;
    output.className = `output-content ${type}`;
}

function showError(message) {
    showOutput(message, 'error');
}


function handleExampleSelect(event) {
    const example = event.target.value;
    if (example && examples[example]) {
        loadExample(example);
    }
}

function loadExample(exampleName) {
    if (examples[exampleName]) {
        codeMirror.setValue(examples[exampleName]);
        document.getElementById('examples-select').value = exampleName;
    }
}

function handleFileUpload(event) {
    const file = event.target.files[0];
    if (file && file.name.endsWith('.lamb')) {
        const reader = new FileReader();
        reader.onload = function(e) {
            codeMirror.setValue(e.target.result);
            document.getElementById('examples-select').value = '';
            showOutput('File loaded successfully: ' + file.name, 'success');
        };
        reader.readAsText(file);
    } else {
        showError('Please select a .lamb file');
    }
    // Reset the file input
    event.target.value = '';
}

document.addEventListener('DOMContentLoaded', init); 