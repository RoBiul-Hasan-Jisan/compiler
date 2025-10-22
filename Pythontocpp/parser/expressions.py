from ast_nodes import *

class ExpressionParser:
    def parse_expr_stmt(self):
        expr = self.parse_expr()
        self.expect('SEMI')
        return ExprStmt(expr)

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

    def parse_factor(self):
        tok = self.peek()
        if tok[0] == 'NUMBER':
            self.next()
            return Number(tok[1])
        if tok[0] == 'STRING_LIT':
            self.next()
            return String(tok[1][1:-1])
        if tok[0] == 'CHAR_LIT':
            self.next()
            return Char(tok[1][1])
        if tok[0] == 'ID':
            self.next()
            name = tok[1]
            if self.peek()[0] == 'LBRACKET':
                indices = []
                while self.peek()[0] == 'LBRACKET':
                    self.next()
                    indices.append(self.parse_expr())
                    self.expect('RBRACKET')
                return ArrayRef(name, indices)
            if self.peek()[0] in ('PLUSPLUS','MINUSMINUS'):
                op_tok = self.next()
                return UnaryOp(op_tok[0], VarRef(name), postfix=True)
            return VarRef(name)
        if tok[0] == 'LPAREN':
            self.next()
            node = self.parse_expr()
            self.expect('RPAREN')
            return node
        if tok[0] in ('PLUSPLUS','MINUSMINUS'):
            op_tok = self.next()
            node = self.parse_factor()
            return UnaryOp(op_tok[0], node, postfix=False)
        raise SyntaxError(f"Unexpected token {tok[0]} at line {tok[3]}")
