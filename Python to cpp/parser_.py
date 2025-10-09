from ast_nodes import *

class Parser:
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

    # ---------------- Function ----------------
    def parse_function(self):
        ret_type = self.next()[0]
        tok = self.expect('ID')
        name = tok[1]
        self.expect('LPAREN')
        self.expect('RPAREN')
        body = self.parse_block()
        return FunctionDecl(name, body)

    # ---------------- Block ----------------
    def parse_block(self):
        self.expect('LBRACE')
        stmts = []
        while self.peek()[0] != 'RBRACE':
            stmts.append(self.parse_statement())
        self.expect('RBRACE')
        return Block(stmts)

    # ---------------- Statement ----------------
    def parse_statement(self):
        tok = self.peek()

        # Variable or array declaration
        if tok[0] in ('INT','FLOAT','DOUBLE','LONG','CHAR','STRING'):
            nxt = self.tokens[self.pos+2] if self.pos+2 < len(self.tokens) else ('EOF','','',-1)
            if nxt[0]=='LBRACKET':
                return self.parse_array_decl()
            return self.parse_var_decl()

        # Control statements
        if tok[0] == 'PRINT':
            return self.parse_print_stmt()
        if tok[0] == 'RETURN':
            return self.parse_return_stmt()
        if tok[0] == 'IF':
            return self.parse_if_stmt()
        if tok[0] == 'WHILE':
            return self.parse_while_stmt()
        if tok[0] == 'FOR':
            return self.parse_for_stmt()

        # Expression / assignment / increment
        if tok[0] == 'ID':
            nxt = self.tokens[self.pos+1] if self.pos+1 < len(self.tokens) else ('EOF','','',-1)

            if nxt[0] == 'ASSIGN':
                return self.parse_assignment()
            if nxt[0] == 'LBRACKET':
                return self.parse_assignment_array()
            if nxt[0] in ('PLUSPLUS','MINUSMINUS'):
                var_tok = self.next()
                op_tok = self.next()
                self.expect('SEMI')
                return UnaryOp(op_tok[0], VarRef(var_tok[1]), postfix=True)

            expr = self.parse_expr()
            self.expect('SEMI')
            return ExprStmt(expr)

        expr = self.parse_expr()
        self.expect('SEMI')
        return ExprStmt(expr)

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

    # For assignment inside for-loop (no semicolon)
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

    # ---------------- Print/Return ----------------
    def parse_print_stmt(self):
        self.expect('PRINT')
        self.expect('LPAREN')
        expr = self.parse_expr()
        self.expect('RPAREN')
        self.expect('SEMI')
        return PrintStmt(expr)

    def parse_return_stmt(self):
        self.expect('RETURN')
        expr = self.parse_expr()
        self.expect('SEMI')
        return ReturnStmt(expr)

    # ---------------- Control Flow ----------------
    def parse_if_stmt(self):
        self.expect('IF')
        self.expect('LPAREN')
        cond = self.parse_expr()
        self.expect('RPAREN')
        then_block = self.parse_block()
        else_block = None
        if self.peek()[0] == 'ELSE':
            self.next()
            else_block = self.parse_block()
        return IfStmt(cond, then_block, else_block)

    def parse_while_stmt(self):
        self.expect('WHILE')
        self.expect('LPAREN')
        cond = self.parse_expr()
        self.expect('RPAREN')
        body = self.parse_block()
        return WhileStmt(cond, body)

    # ---------------- For loop ----------------
    def parse_for_stmt(self):
        self.expect('FOR')
        self.expect('LPAREN')

        # Initialization
        if self.peek()[0] in ('INT','FLOAT','DOUBLE','LONG','CHAR','STRING'):
            init = self.parse_var_decl()
        elif self.peek()[0] != 'SEMI':
            init = self.parse_assignment_no_semi()
            self.expect('SEMI')
        else:
            init = None
            self.next()

        # Condition
        if self.peek()[0] != 'SEMI':
            cond = self.parse_expr()
        else:
            cond = None
        self.expect('SEMI')

        # Update
        if self.peek()[0] != 'RPAREN':
            tok = self.peek()
            if tok[0] == 'ID' and self.tokens[self.pos+1][0] == 'ASSIGN':
                update = self.parse_assignment_no_semi()
            else:
                update = self.parse_expr()
        else:
            update = None

        self.expect('RPAREN')
        body = self.parse_block()
        return ForStmt(init, cond, update, body)

    # ---------------- Expressions ----------------
    def parse_expr(self):
        return self.parse_logic_or()

    def parse_logic_or(self):
        node = self.parse_logic_and()
        while self.peek()[0] == 'OR':
            op = self.next()[0]
            right = self.parse_logic_and()
            node = BinaryOp(op, node, right)
        return node

    def parse_logic_and(self):
        node = self.parse_equality()
        while self.peek()[0] == 'AND':
            op = self.next()[0]
            right = self.parse_equality()
            node = BinaryOp(op, node, right)
        return node

    def parse_equality(self):
        node = self.parse_relational()
        while self.peek()[0] in ('EQ','NE'):
            op = self.next()[0]
            right = self.parse_relational()
            node = BinaryOp(op, node, right)
        return node

    def parse_relational(self):
        node = self.parse_additive()
        while self.peek()[0] in ('GT','LT','GE','LE'):
            op = self.next()[0]
            right = self.parse_additive()
            node = BinaryOp(op, node, right)
        return node

    def parse_additive(self):
        node = self.parse_term()
        while self.peek()[0] in ('PLUS','MINUS'):
            op = self.next()[0]
            right = self.parse_term()
            node = BinaryOp(op, node, right)
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.peek()[0] in ('MULT','DIV'):
            op = self.next()[0]
            right = self.parse_factor()
            node = BinaryOp(op, node, right)
        return node

    # ---------------- Factor ----------------
    def parse_factor(self):
        tok = self.peek()

        # literals
        if tok[0] == 'NUMBER':
            self.next()
            return Number(tok[1])
        if tok[0] == 'STRING_LIT':
            self.next()
            return String(tok[1][1:-1])
        if tok[0] == 'CHAR_LIT':
            self.next()
            return Char(tok[1][1])

        # identifier
        if tok[0] == 'ID':
            self.next()
            name = tok[1]

            # Array reference
            if self.peek()[0] == 'LBRACKET':
                indices = []
                while self.peek()[0] == 'LBRACKET':
                    self.next()
                    indices.append(self.parse_expr())
                    self.expect('RBRACKET')
                return ArrayRef(name, indices)

            # Postfix ++ / --
            if self.peek()[0] in ('PLUSPLUS','MINUSMINUS'):
                op_tok = self.next()
                return UnaryOp(op_tok[0], VarRef(name), postfix=True)

            return VarRef(name)

        # Parentheses
        if tok[0] == 'LPAREN':
            self.next()
            node = self.parse_expr()
            self.expect('RPAREN')
            return node

        # Prefix ++ / --
        if tok[0] in ('PLUSPLUS','MINUSMINUS'):
            op_tok = self.next()
            node = self.parse_factor()
            return UnaryOp(op_tok[0], node, postfix=False)

        raise SyntaxError(f"Unexpected token {tok[0]} at line {tok[3]}")
