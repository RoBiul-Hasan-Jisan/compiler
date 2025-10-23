from .expressions import ExpressionParser
from .declarations import DeclarationParser
from ast_nodes import *

class StatementParser(ExpressionParser, DeclarationParser):

    # ---------------- Statement ----------------
    def parse_statement(self):
        tok = self.peek()

        # Variable or array declaration
        if tok[0] in ('INT','FLOAT','DOUBLE','LONG','CHAR','STRING','BOOL'):
            nxt = self.tokens[self.pos+2] if self.pos+2 < len(self.tokens) else ('EOF','','',-1)
            if nxt[0] == 'LBRACKET':
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
        if tok[0] == 'BREAK':
            self.next()
            self.expect('SEMI')
            return BreakStmt()
        if tok[0] == 'CONTINUE':
            self.next()
            self.expect('SEMI')
            return ContinueStmt()
        if tok[0] == 'SWITCH':
            return self.parse_switch_stmt()

        # Assignment / expression
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
            return self.parse_expr_stmt()

        return self.parse_expr_stmt()

    # ---------------- Block ----------------
    def parse_block(self):
        self.expect('LBRACE')
        stmts = []
        while self.peek()[0] != 'RBRACE':
            stmts.append(self.parse_statement())
        self.expect('RBRACE')
        return Block(stmts)

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
            if self.peek()[0] == 'IF':
                else_block = Block([self.parse_if_stmt()])  # else-if chain
            else:
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
        if self.peek()[0] in ('INT','FLOAT','DOUBLE','LONG','CHAR','STRING','BOOL'):
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

    # ---------------- Expression Statement ----------------
    def parse_expr_stmt(self):
        expr = self.parse_expr()
        self.expect('SEMI')
        return ExprStmt(expr)

    # ---------------- Switch Statement ----------------
    def parse_switch_stmt(self):
        self.expect('SWITCH')
        self.expect('LPAREN')
        expr = self.parse_expr()
        self.expect('RPAREN')
        self.expect('LBRACE')

        cases = []
        default_case = None

        while self.peek()[0] != 'RBRACE':
            tok = self.peek()
            if tok[0] == 'CASE':
                self.next()
                value = self.parse_expr()
                self.expect('COLON')
                stmts = []
                while self.peek()[0] not in ('CASE','DEFAULT','RBRACE'):
                    stmts.append(self.parse_statement())
                cases.append(CaseStmt(value, Block(stmts)))
            elif tok[0] == 'DEFAULT':
                self.next()
                self.expect('COLON')
                stmts = []
                while self.peek()[0] != 'RBRACE':
                    stmts.append(self.parse_statement())
                default_case = DefaultStmt(Block(stmts))
            else:
                raise SyntaxError(f"Unexpected token {tok[0]} in switch at line {tok[3]}")

        self.expect('RBRACE')
        return SwitchStmt(expr, cases, default_case)
