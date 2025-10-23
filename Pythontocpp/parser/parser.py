from .statements import StatementParser
from .expressions import ExpressionParser
from .declarations import DeclarationParser
from ast_nodes import *

class Parser(StatementParser, ExpressionParser, DeclarationParser):
    def __init__(self, tokens):
        self.tokens = list(tokens)
        self.pos = 0

    # ---------------- Token Helpers ----------------
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
        # Return type
        ret_type = self.next()[0]
        # Function name
        name = self.expect('ID')[1]
        self.expect('LPAREN')

        # --- Parameters ---
        params = []
        while self.peek()[0] != 'RPAREN':
            p_type = self.next()[0]
            p_name = self.expect('ID')[1]
            params.append((p_type, p_name))
            if self.peek()[0] == 'COMMA':
                self.next()
        self.expect('RPAREN')

        # --- Function body ---
        body = self.parse_block()
        return FunctionDecl(name, body, params=params)

    # ---------------- Block Parsing ----------------
    def parse_block(self):
        self.expect('LBRACE')
        stmts = []
        while self.peek()[0] != 'RBRACE':
            stmts.append(self.parse_statement())
        self.expect('RBRACE')
        return Block(stmts)
