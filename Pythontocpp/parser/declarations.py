from ast_nodes import *

class DeclarationParser:
    # ---------------- Variable Declaration ----------------
    def parse_var_decl(self):
        vtype = self.next()[0]          # type keyword (INT, FLOAT, BOOL, etc.)
        name = self.expect('ID')[1]     # variable name
        init = None
        if self.peek()[0] == 'ASSIGN':
            self.next()
            init = self.parse_expr()
        self.expect('SEMI')
        return VarDecl(vtype, name, init)

    # ---------------- Array Declaration ----------------
    def parse_array_decl(self):
        vtype = self.next()[0]          # type keyword
        name = self.expect('ID')[1]     # array name
        dims = []
        while self.peek()[0] == 'LBRACKET':
            self.next()
            dims.append(self.expect('NUMBER')[1])
            self.expect('RBRACKET')
        self.expect('SEMI')
        return ArrayDecl(vtype, name, dims)

    # ---------------- Assignment to variable ----------------
    def parse_assignment(self):
        name = self.expect('ID')[1]
        self.expect('ASSIGN')
        expr = self.parse_expr()
        self.expect('SEMI')
        return Assignment(name, expr)

    # Assignment without trailing semicolon (used in for-loop init/update)
    def parse_assignment_no_semi(self):
        name = self.expect('ID')[1]
        self.expect('ASSIGN')
        expr = self.parse_expr()
        return Assignment(name, expr)

    # ---------------- Assignment to array element ----------------
    def parse_assignment_array(self):
        name = self.expect('ID')[1]
        indices = []
        while self.peek()[0] == 'LBRACKET':
            self.next()
            indices.append(self.parse_expr())
            self.expect('RBRACKET')
        self.expect('ASSIGN')
        expr = self.parse_expr()
        self.expect('SEMI')
        return Assignment(ArrayRef(name, indices), expr)
