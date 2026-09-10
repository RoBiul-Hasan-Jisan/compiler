# Architecture

`mcpp` follows the classic front-end compiler pipeline, with each stage
implemented in its own module so it can be read, tested, and explained
independently.

```
source text (.mcpp)
        │
        ▼
 ┌─────────────┐     mcpp/lexer.py
 │    Lexer     │     Converts raw text into a flat list of Tokens,
 │              │     tracking line/column for every one.
 └──────┬──────┘
        │ List[Token]
        ▼
 ┌─────────────┐     mcpp/parser.py
 │    Parser    │     Recursive-descent parser. Consumes tokens and
 │              │     builds an AST (mcpp/ast_nodes.py) using standard
 │              │     precedence-climbing for expressions.
 └──────┬──────┘
        │ Program (AST root)
        ▼
 ┌─────────────┐     mcpp/interpreter.py
 │ Interpreter  │     Tree-walking evaluator. Executes the AST directly,
 │              │     using mcpp/environment.py for scoped variable
 │              │     storage (one Environment per block/call frame).
 └──────┬──────┘
        │
        ▼
   program output
```

## Why a tree-walking interpreter instead of "real" codegen?

The project's goal is to demonstrate the *front end* of a compiler
(lexing, parsing, AST construction) clearly. Rather than emitting
another language's source (which just moves the interesting work into
a second language's runtime) or bytecode, the interpreter executes the
AST directly. This keeps every stage inspectable in Python and makes
it straightforward to extend the pipeline later with a real
code-generation backend (e.g. emitting C, LLVM IR, or Python bytecode)
without having to touch the lexer or parser.

## Module map

| Module | Responsibility |
|--------|-----------------|
| `mcpp/tokens.py` | `TokenType` enum and the `Token` dataclass |
| `mcpp/lexer.py` | Source text → tokens |
| `mcpp/ast_nodes.py` | Dataclasses for every AST node |
| `mcpp/parser.py` | Tokens → AST (recursive descent, see the grammar in the module docstring) |
| `mcpp/environment.py` | Scoped variable storage (`Environment` is a linked chain of scopes) |
| `mcpp/interpreter.py` | AST → program output; one `_exec_*`/`_eval_*` method per node type |
| `mcpp/errors.py` | Shared, position-aware error types for every stage |
| `mcpp/cli.py` | Command-line entry point (`python -m mcpp.cli file.mcpp`) |
| `web/app.py` | Optional Flask front end (browser playground) |

## Error handling philosophy

Every stage raises a subclass of `MCPPError` (`LexError`, `ParseError`,
`MCPPRuntimeError`) carrying a line, column, and the offending source
line, so a single `except MCPPError` in the CLI or the web API can
report any failure with a `file:line:col` style message and a `^`
pointer — the same shape of message a real C/C++ compiler gives.

## Control flow without a bytecode VM

`break`, `continue`, and `return` are implemented as Python exceptions
(`BreakSignal`, `ContinueSignal`, `ReturnSignal`) that unwind the
interpreter's own call stack up to the nearest loop or function call.
This keeps the interpreter's structure a direct mirror of the AST's
structure, rather than needing an explicit instruction pointer.

## Extending the project

Natural follow-ups for a course project or portfolio piece:

- **Static type checking** — walk the AST once before interpreting it
  to catch type errors (`int a = "hi";`) ahead of time. `mcpp/errors.py`
  already has a `SemanticError` type ready for this.
- **Arrays as function parameters** — currently arrays must be global
  or local to the function using them; passing them by reference is a
  natural extension of `environment.py`.
- **A real codegen backend** — walk the same AST and emit C or LLVM IR
  instead of interpreting it directly.
