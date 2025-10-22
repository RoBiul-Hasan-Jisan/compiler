from ast_nodes import *
from parser import Parser  # your main root parser

class ParserWithParams(Parser):  # inherit your existing Parser
    # ---------------- Function Parsing ----------------
    def parse_function(self):
        ret_type = self.next()[0]        # return type
        name = self.expect('ID')[1]      # function name
        self.expect('LPAREN')
        
        # --- Parse parameters ---
        params = []
        while self.peek()[0] != 'RPAREN':
            p_type = self.next()[0]        # param type
            p_name = self.expect('ID')[1]  # param name
            params.append((p_type, p_name))
            if self.peek()[0] == 'COMMA':
                self.next()  # skip comma
        self.expect('RPAREN')
        
        body = self.parse_block()
        return FunctionDecl(name, body, params=params)

    # ---------------- Factor Parsing (Function Call Support) ----------------
    def parse_factor(self):
        tok = self.peek()

        # --- Number ---
        if tok[0] == 'NUMBER':
            self.next()
            return Number(tok[1])

        # --- String ---
        if tok[0] == 'STRING_LIT':
            self.next()
            return String(tok[1][1:-1])

        # --- Char ---
        if tok[0] == 'CHAR_LIT':
            self.next()
            return Char(tok[1][1])

        # --- Identifier / Variable / Function Call ---
        if tok[0] == 'ID':
            # Check if it's a function call
            if self.tokens[self.pos+1][0] == 'LPAREN':
                func_name = self.next()[1]
                self.expect('LPAREN')
                args = []
                if self.peek()[0] != 'RPAREN':
                    while True:
                        args.append(self.parse_expr())
                        if self.peek()[0] == 'COMMA':
                            self.next()
                        else:
                            break
                self.expect('RPAREN')
                return FunctionCall(func_name, args)
            else:
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

        # --- Parentheses ---
        if tok[0] == 'LPAREN':
            self.next()
            node = self.parse_expr()
            self.expect('RPAREN')
            return node

        # --- Prefix ++ / -- ---
        if tok[0] in ('PLUSPLUS','MINUSMINUS'):
            op_tok = self.next()
            node = self.parse_factor()
            return UnaryOp(op_tok[0], node, postfix=False)

        raise SyntaxError(f"Unexpected token {tok[0]} at line {tok[3]}")
