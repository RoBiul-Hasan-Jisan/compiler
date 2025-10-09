import sys
from lexer import tokenize
from parser_ import Parser
from interpreter import Interpreter, RuntimeErrorWithLine

def compile_and_run(source_code):
    tokens = list(tokenize(source_code))
    tokens.append(('EOF','',len(source_code), source_code.count('\n') + 1))
    parser = Parser(tokens)
    program = parser.parse_program()
    interp = Interpreter(program)
    return interp.run()

def main():
    if len(sys.argv) < 2:
        print("Usage: python compiler.py <source.cpp>")
        return

    path = sys.argv[1]
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()

    try:
        result = compile_and_run(code)
        print(f"Program returned: {result}")
    except RuntimeErrorWithLine as e:
        print(f"Runtime Error: {e}")
    except SyntaxError as e:
        print(f"Syntax Error: {e}")
    except Exception as e:
        print(f"Unknown Error: {e}")

if __name__ == "__main__":
    main()
