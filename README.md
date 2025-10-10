#  Python to C++ Compiler

A custom compiler built in **Python** that parses and translates simplified **C++ like syntax** into **Python-executable code**.  
This project demonstrates **lexical analysis**, **parsing**, **AST construction**, and **code generation** — all implemented from scratch.

---

##  Features

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

##  Project Structure

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

```

##  Run Command

```bash
python compiler.py example.cpp

```
##  Supported Syntax

Your compiler supports a wide range of **custom** and **C++-style** syntax.  
Below is the complete list of supported constructs 

| **Category** | **Syntax Example** | **Description** |
|---------------|--------------------|-----------------|
| **Program Entry** | `int main() { ... }` | Starting point of execution |
| **Variable Declaration** | `int a = 5;` | Integer variable |
|  | `float f = 3.14;` | Floating point variable |
|  | `string s = "Hello";` | String variable |
|  | `char c = 'A';` | Character variable |
| **Arithmetic Operations** | `a + b - c * d / e % f` | Basic arithmetic operations |
| **Assignment** | `a = 10;` | Assigns value to variable |
| **Comparison Operators** | `==`, `!=`, `>`, `<`, `>=`, `<=` | Used in conditions |
| **Logical Operators** | `&&`, `||`, `!` | Logical AND, OR, NOT |
| **Conditional Statements** | `if (a > b) { ... }` | If block |
|  | `if (a > b) { ... } else { ... }` | If-else block |
|  | `if (a > b) { ... } else if (a == b) { ... } else { ... }` | Nested conditions |
| **Loop - Custom `loop`** | `loop (i = 0; i < 5; i++) { print(i); }` | For-loop equivalent |
| **Loop - Custom `jakon`** | `jakon (x < 10) { print(x); x++; }` | While-loop equivalent |
| **Loop - Custom `gurer somoi`** | `gurer somoi { print(x); } jokon(x < 5);` | Do-while equivalent |
| **Printing** | `print(a);` | Prints variable or expression |
| **String Concatenation** | `print("Hi " + s);` | Combines strings |
| **Character Operations** | `char c1 = 'a'; char c2 = 'b'; print(c1 + c2);` | Combines or compares characters |
| **Comments** | `// This is a comment` | Single-line comment |
| **Blocks** | `{ ... }` | Encloses multiple statements |
| **End of Statement** | `;` | Marks statement termination |

## Clone this repository
```bash
https://github.com/RoBiul-Hasan-Jisan/compiler/tree/main/Python%20to%20cpp

Move into the project folder
cd python-to-cpp-compiler

Run compiler on your test file
python compiler.py example.cpp
```


