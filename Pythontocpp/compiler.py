import sys
import traceback
from lexer import tokenize
from parser.parser_functions import ParserWithParams
from interpreter.interpreter_functions import InterpreterWithFunctions
from interpreter.interpreter import RuntimeErrorWithLine

def compile_and_run(source_code):
    # ---------------- Tokenize ----------------
    tokens = list(tokenize(source_code))
    tokens.append(('EOF', '', len(source_code), source_code.count('\n') + 1))

    # ---------------- Parse ----------------
    parser = ParserWithParams(tokens)
    program = parser.parse_program()

    # ---------------- Interpret ----------------
    interp = InterpreterWithFunctions(program)
    return interp.run()

def main():
    if len(sys.argv) < 2:
        print("Usage: python compiler.py <source.cpp>")
        return

    path = sys.argv[1]

    # ---------------- Read source file ----------------
    try:
        with open(path, 'r', encoding='utf-8') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"File not found: {path}")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # ---------------- Compile and Run ----------------
    try:
        result = compile_and_run(code)
        if result is not None:
            print(f"Program returned: {result}")
        else:
            print("Program completed without return value.")
    except RuntimeErrorWithLine as e:
        print(f"Runtime Error: {e}")
    except SyntaxError as e:
        print(f"Syntax Error: {e}")
    except Exception as e:
        print(f"Unknown Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
