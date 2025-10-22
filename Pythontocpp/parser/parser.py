from .statements import StatementParser
from .expressions import ExpressionParser
from .declarations import DeclarationParser
from ast_nodes import Program, FunctionDecl

class Parser(StatementParser, ExpressionParser, DeclarationParser):
    def __init__(self, tokens):
        self.tokens = list(tokens)
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else ('EOF','',-1,-1)

    def next(self):
        tok = self.peek()
        self.pos += 1
        return tok

    def expect(self, kind):
        tok = self.peek()
        if tok[0] != kind:
            raise SyntaxError(f"Expected {kind} but got {tok[0]} at line {tok[3]}")
        return self.next()

    # ---------------- Program ----------------
    def parse_program(self):
        funcs = []
        while self.peek()[0] != 'EOF':
            funcs.append(self.parse_function())
        return Program(funcs)

    # ---------------- Function Parsing ----------------
    def parse_function(self):
        ret_type = self.next()[0]            # return type
        name = self.expect('ID')[1]          # function name
        self.expect('LPAREN')

        # --- Parse parameters ---
        params = []
        while self.peek()[0] != 'RPAREN':
            p_type = self.next()[0]
            p_name = self.expect('ID')[1]
            params.append((p_type, p_name))
            if self.peek()[0] == 'COMMA':
                self.next()  # skip comma
        self.expect('RPAREN')

        body = self.parse_block()
        return FunctionDecl(name, body, params=params)
