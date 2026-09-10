
from mcpp.lexer import Lexer
from mcpp.parser import parse
from mcpp.interpreter import Interpreter


def run(source: str):
    """Compile and run `source`, returning (captured_output_lines, return_value)."""
    lines = []
    tokens = Lexer(source).tokenize()
    program = parse(tokens, source)
    result = Interpreter(output=lines.append).run(program)
    return lines, result
