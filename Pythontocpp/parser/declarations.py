from ast_nodes import *

class DeclarationParser:
    # ---------------- Declarations ----------------
    def parse_var_decl(self):
        vtype = self.next()[0]
        name = self.expect('ID')[1]
        init = None
        if self.peek()[0] == 'ASSIGN':
            self.next()
            init = self.parse_expr()
        self.expect('SEMI')
        return VarDecl(vtype, name, init)

    def parse_array_decl(self):
        vtype = self.next()[0]
        name = self.expect('ID')[1]
        dims = []
        while self.peek()[0] == 'LBRACKET':
            self.next()
            dims.append(self.expect('NUMBER')[1])
            self.expect('RBRACKET')
        self.expect('SEMI')
        return ArrayDecl(vtype, name, dims)

    # ---------------- Assignment ----------------
    def parse_assignment(self):
        name = self.expect('ID')[1]
        self.expect('ASSIGN')
        expr = self.parse_expr()
        self.expect('SEMI')
        return Assignment(name, expr)

    def parse_assignment_no_semi(self):
        name = self.expect('ID')[1]
        self.expect('ASSIGN')
        expr = self.parse_expr()
        return Assignment(name, expr)

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
