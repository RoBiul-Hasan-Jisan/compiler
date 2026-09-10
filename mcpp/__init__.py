"""
mcpp - A small compiler/interpreter for a C++-like teaching language.

Pipeline:
    source text -> Lexer -> tokens -> Parser -> AST -> Interpreter -> output

Each stage lives in its own module so the pipeline is easy to read,
test, and extend:

    tokens.py       Token and TokenType definitions
    lexer.py         source text -> list[Token]
    ast_nodes.py      AST node dataclasses
    parser.py         tokens -> AST (recursive descent)
    environment.py    scoped variable storage used at runtime
    interpreter.py    AST -> program output (tree-walking evaluator)
    errors.py          shared, position-aware error types
"""

__version__ = "1.0.0"
