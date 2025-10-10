# 🧠 Python to C++ Compiler

A custom compiler built in **Python** that parses and translates simplified **C++-like syntax** into **Python-executable code**.  
This project demonstrates **lexical analysis**, **parsing**, **AST construction**, and **code generation** — all implemented from scratch.

---

## 🚀 Features

- **C++-style syntax** (variables, conditionals, loops, and functions)
- **Custom control flow** (`if`, `else`, `loop`, `jakon`, `gurer somoi`)
- **Complete compilation pipeline**
  - Tokenizer (Lexical Analyzer)
  - Recursive Descent Parser
  - Abstract Syntax Tree (AST)
  - Code Generator / Interpreter
- **Error handling** for syntax and runtime errors
- **Pure Python** — no external dependencies
- Easily extendable for new features (type checking, optimization, etc.)

---

## 🧩 Project Structure

```bash
 compiler/
│
├── lexer.py         # Tokenizer - converts source code into tokens
├── parser_.py       # Recursive descent parser - builds the AST
├── ast_nodes.py     # Defines the Abstract Syntax Tree nodes
├── codegen.py       # Code generator / interpreter for Python output
├── compiler.py      # Main compiler driver script
├── example.cpp      # Example source file using custom C++-like syntax
└── README.md        # Documentation file

---

## ▶️ Run Command

```bash
python compiler.py example.cpp

