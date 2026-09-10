"""Recursive-descent parser: builds an AST from a token stream.

Grammar (informal EBNF)
------------------------
program      -> (funcDecl | varDecl | arrayDecl)*
funcDecl     -> type IDENT '(' params? ')' block
params       -> param (',' param)*
param        -> type IDENT
block        -> '{' statement* '}'

statement    -> varDecl | arrayDecl | ifStmt | whileStmt | doWhileStmt
              | forStmt | switchStmt | 'break' ';' | 'continue' ';'
              | 'return' expr? ';' | printStmt | block | exprStmt

varDecl      -> type IDENT ('=' expr)? ';'
arrayDecl    -> type IDENT '[' INT_LIT ']' ';'
ifStmt       -> 'if' '(' expr ')' block ('else' (ifStmt | block))?
whileStmt    -> 'while' '(' expr ')' block
doWhileStmt  -> 'do' block 'while' '(' expr ')' ';'
forStmt      -> 'for' '(' (varDecl | exprStmt | ';') expr? ';' expr? ')' block
switchStmt   -> 'switch' '(' expr ')' '{' caseClause* '}'
caseClause   -> ('case' expr | 'default') ':' statement*
printStmt    -> 'print' '(' (expr (',' expr)*)? ')' ';'
exprStmt     -> expr ';'

expr         -> assignment
assignment   -> logicalOr ('=' assignment)?
logicalOr    -> logicalAnd ('||' logicalAnd)*
logicalAnd   -> equality ('&&' equality)*
equality     -> comparison (('=='|'!=') comparison)*
comparison   -> term (('<'|'<='|'>'|'>=') term)*
term         -> factor (('+'|'-') factor)*
factor       -> unary (('*'|'/'|'%') unary)*
unary        -> ('!'|'-'|'++'|'--') unary | postfix
postfix      -> primary ('++'|'--')?
primary      -> INT | FLOAT | CHAR | STRING | 'true' | 'false'
              | IDENT | IDENT '(' args? ')' | IDENT '[' expr ']'
              | '(' expr ')'
"""

from .tokens import TokenType
from .errors import ParseError
from . import ast_nodes as A

_TYPE_TOKENS = {
    TokenType.INT: "int", TokenType.FLOAT: "float", TokenType.CHAR: "char",
    TokenType.STRING: "string", TokenType.BOOL: "bool", TokenType.VOID: "void",
}


class Parser:
    """Turns a flat token list into a Program AST via recursive descent."""

    def __init__(self, tokens, source: str = ""):
        self.tokens = tokens
        self.pos = 0
        self.source_lines = source.splitlines()

    # -- cursor helpers --------------------------------------------------
    def _peek(self, offset=0):
        i = min(self.pos + offset, len(self.tokens) - 1)
        return self.tokens[i]

    def _advance(self):
        tok = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return tok

    def _check(self, *types):
        return self._peek().type in types

    def _match(self, *types):
        if self._check(*types):
            return self._advance()
        return None

    def _expect(self, type_, message):
        if self._check(type_):
            return self._advance()
        self._error(message)

    def _error(self, message):
        tok = self._peek()
        src = self.source_lines[tok.line - 1] if 0 < tok.line <= len(self.source_lines) else ""
        raise ParseError(f"{message} (got {tok.type.name} {tok.value!r})", tok.line, tok.column, src)

    def _is_type_start(self):
        return self._peek().type in _TYPE_TOKENS

    # -- entry point -------------------------------------------------------
    def parse(self) -> A.Program:
        functions, globals_ = [], []
        while not self._check(TokenType.EOF):
            if self._is_type_start():
                decl = self._declaration(top_level=True)
                if isinstance(decl, A.FunctionDecl):
                    functions.append(decl)
                else:
                    globals_.append(decl)
            else:
                self._error("Expected a type keyword to start a declaration")
        return A.Program(functions=functions, globals=globals_)

    # -- declarations --------------------------------------------------
    def _declaration(self, top_level=False):
        type_tok = self._advance()
        type_name = _TYPE_TOKENS[type_tok.type]
        name_tok = self._expect(TokenType.IDENTIFIER, "Expected an identifier after type")

        if self._check(TokenType.LPAREN):
            return self._function_decl(type_name, name_tok)
        if self._check(TokenType.LBRACKET):
            return self._array_decl(type_name, name_tok)
        return self._var_decl_rest(type_name, name_tok)

    def _function_decl(self, return_type, name_tok):
        self._expect(TokenType.LPAREN, "Expected '(' after function name")
        params = []
        if not self._check(TokenType.RPAREN):
            params.append(self._param())
            while self._match(TokenType.COMMA):
                params.append(self._param())
        self._expect(TokenType.RPAREN, "Expected ')' after parameters")
        body = self._block()
        return A.FunctionDecl(return_type, name_tok.value, params, body, name_tok.line)

    def _param(self):
        if not self._is_type_start():
            self._error("Expected a parameter type")
        type_tok = self._advance()
        name_tok = self._expect(TokenType.IDENTIFIER, "Expected a parameter name")
        return A.Param(_TYPE_TOKENS[type_tok.type], name_tok.value, name_tok.line)

    def _array_decl(self, elem_type, name_tok):
        self._advance()  # '['
        size_tok = self._expect(TokenType.INT_LIT, "Array size must be an integer literal")
        self._expect(TokenType.RBRACKET, "Expected ']' after array size")
        self._expect(TokenType.SEMICOLON, "Expected ';' after array declaration")
        return A.ArrayDecl(elem_type, name_tok.value, size_tok.value, name_tok.line)

    def _var_decl_rest(self, var_type, name_tok):
        value = None
        if self._match(TokenType.ASSIGN):
            value = self._expression()
        self._expect(TokenType.SEMICOLON, "Expected ';' after variable declaration")
        return A.VarDecl(var_type, name_tok.value, value, name_tok.line)

    # -- statements ---------------------------------------------------
    def _block(self) -> A.Block:
        brace = self._expect(TokenType.LBRACE, "Expected '{' to start a block")
        statements = []
        while not self._check(TokenType.RBRACE, TokenType.EOF):
            statements.append(self._statement())
        self._expect(TokenType.RBRACE, "Expected '}' to close a block")
        return A.Block(statements, brace.line)

    def _statement(self):
        if self._is_type_start():
            return self._declaration()
        if self._check(TokenType.LBRACE):
            return self._block()
        if self._check(TokenType.IF):
            return self._if_stmt()
        if self._check(TokenType.WHILE):
            return self._while_stmt()
        if self._check(TokenType.DO):
            return self._do_while_stmt()
        if self._check(TokenType.FOR):
            return self._for_stmt()
        if self._check(TokenType.SWITCH):
            return self._switch_stmt()
        if self._check(TokenType.PRINT):
            return self._print_stmt()
        if self._check(TokenType.BREAK):
            tok = self._advance()
            self._expect(TokenType.SEMICOLON, "Expected ';' after 'break'")
            return A.Break(tok.line)
        if self._check(TokenType.CONTINUE):
            tok = self._advance()
            self._expect(TokenType.SEMICOLON, "Expected ';' after 'continue'")
            return A.Continue(tok.line)
        if self._check(TokenType.RETURN):
            tok = self._advance()
            value = None
            if not self._check(TokenType.SEMICOLON):
                value = self._expression()
            self._expect(TokenType.SEMICOLON, "Expected ';' after 'return'")
            return A.Return(value, tok.line)
        return self._expr_stmt()

    def _if_stmt(self):
        tok = self._advance()
        self._expect(TokenType.LPAREN, "Expected '(' after 'if'")
        condition = self._expression()
        self._expect(TokenType.RPAREN, "Expected ')' after if condition")
        then_branch = self._block()
        else_branch = None
        if self._match(TokenType.ELSE):
            else_branch = self._if_stmt() if self._check(TokenType.IF) else self._block()
        return A.If(condition, then_branch, else_branch, tok.line)

    def _while_stmt(self):
        tok = self._advance()
        self._expect(TokenType.LPAREN, "Expected '(' after 'while'")
        condition = self._expression()
        self._expect(TokenType.RPAREN, "Expected ')' after while condition")
        body = self._block()
        return A.While(condition, body, tok.line)

    def _do_while_stmt(self):
        tok = self._advance()
        body = self._block()
        self._expect(TokenType.WHILE, "Expected 'while' after do-block")
        self._expect(TokenType.LPAREN, "Expected '(' after 'while'")
        condition = self._expression()
        self._expect(TokenType.RPAREN, "Expected ')' after condition")
        self._expect(TokenType.SEMICOLON, "Expected ';' after do-while statement")
        return A.DoWhile(body, condition, tok.line)

    def _for_stmt(self):
        tok = self._advance()
        self._expect(TokenType.LPAREN, "Expected '(' after 'for'")

        init = None
        if not self._check(TokenType.SEMICOLON):
            init = self._declaration() if self._is_type_start() else self._expr_stmt()
        else:
            self._advance()  # bare ';'

        condition = None
        if not self._check(TokenType.SEMICOLON):
            condition = self._expression()
        self._expect(TokenType.SEMICOLON, "Expected ';' after for-loop condition")

        update = None
        if not self._check(TokenType.RPAREN):
            update = self._expression()
        self._expect(TokenType.RPAREN, "Expected ')' after for-loop clauses")

        body = self._block()
        return A.For(init, condition, update, body, tok.line)

    def _switch_stmt(self):
        tok = self._advance()
        self._expect(TokenType.LPAREN, "Expected '(' after 'switch'")
        expr = self._expression()
        self._expect(TokenType.RPAREN, "Expected ')' after switch expression")
        self._expect(TokenType.LBRACE, "Expected '{' to start switch body")

        cases = []
        while self._check(TokenType.CASE, TokenType.DEFAULT):
            case_tok = self._advance()
            value = None
            if case_tok.type == TokenType.CASE:
                value = self._expression()
            self._expect(TokenType.COLON, "Expected ':' after case label")
            statements = []
            while not self._check(TokenType.CASE, TokenType.DEFAULT, TokenType.RBRACE, TokenType.EOF):
                statements.append(self._statement())
            cases.append(A.SwitchCase(value, statements, case_tok.line))

        self._expect(TokenType.RBRACE, "Expected '}' to close switch body")
        return A.Switch(expr, cases, tok.line)

    def _print_stmt(self):
        tok = self._advance()
        self._expect(TokenType.LPAREN, "Expected '(' after 'print'")
        args = []
        if not self._check(TokenType.RPAREN):
            args.append(self._expression())
            while self._match(TokenType.COMMA):
                args.append(self._expression())
        self._expect(TokenType.RPAREN, "Expected ')' after print arguments")
        self._expect(TokenType.SEMICOLON, "Expected ';' after print statement")
        return A.Print(args, tok.line)

    def _expr_stmt(self):
        expr = self._expression()
        self._expect(TokenType.SEMICOLON, "Expected ';' after expression")
        return A.ExprStatement(expr, expr.line)

    # -- expressions (precedence climbing) ------------------------------
    def _expression(self):
        return self._assignment()

    def _assignment(self):
        expr = self._logical_or()
        if self._check(TokenType.ASSIGN):
            tok = self._advance()
            if not isinstance(expr, (A.Identifier, A.ArrayAccess)):
                self._error("Invalid assignment target")
            value = self._assignment()
            return A.Assign(expr, value, tok.line)
        return expr

    def _binary_level(self, next_level, *op_types):
        expr = next_level()
        while self._check(*op_types):
            tok = self._advance()
            right = next_level()
            expr = A.BinOp(tok.value, expr, right, tok.line)
        return expr

    def _logical_or(self):
        return self._binary_level(self._logical_and, TokenType.OR)

    def _logical_and(self):
        return self._binary_level(self._equality, TokenType.AND)

    def _equality(self):
        return self._binary_level(self._comparison, TokenType.EQ, TokenType.NEQ)

    def _comparison(self):
        return self._binary_level(self._term, TokenType.LT, TokenType.LTE, TokenType.GT, TokenType.GTE)

    def _term(self):
        return self._binary_level(self._factor, TokenType.PLUS, TokenType.MINUS)

    def _factor(self):
        return self._binary_level(self._unary, TokenType.STAR, TokenType.SLASH, TokenType.PERCENT)

    def _unary(self):
        if self._check(TokenType.NOT, TokenType.MINUS, TokenType.PLUS_PLUS, TokenType.MINUS_MINUS):
            tok = self._advance()
            operand = self._unary()
            return A.UnaryOp(tok.value, operand, tok.line)
        return self._postfix()

    def _postfix(self):
        expr = self._primary()
        if self._check(TokenType.PLUS_PLUS, TokenType.MINUS_MINUS):
            tok = self._advance()
            return A.PostfixOp(tok.value, expr, tok.line)
        return expr

    def _primary(self):
        tok = self._peek()

        if self._match(TokenType.INT_LIT):
            return A.Literal(tok.value, "int", tok.line)
        if self._match(TokenType.FLOAT_LIT):
            return A.Literal(tok.value, "float", tok.line)
        if self._match(TokenType.CHAR_LIT):
            return A.Literal(tok.value, "char", tok.line)
        if self._match(TokenType.STRING_LIT):
            return A.Literal(tok.value, "string", tok.line)
        if self._match(TokenType.TRUE):
            return A.Literal(True, "bool", tok.line)
        if self._match(TokenType.FALSE):
            return A.Literal(False, "bool", tok.line)

        if self._check(TokenType.IDENTIFIER):
            name_tok = self._advance()
            if self._match(TokenType.LPAREN):
                args = []
                if not self._check(TokenType.RPAREN):
                    args.append(self._expression())
                    while self._match(TokenType.COMMA):
                        args.append(self._expression())
                self._expect(TokenType.RPAREN, "Expected ')' after arguments")
                return A.FunctionCall(name_tok.value, args, name_tok.line)
            if self._match(TokenType.LBRACKET):
                index = self._expression()
                self._expect(TokenType.RBRACKET, "Expected ']' after array index")
                return A.ArrayAccess(name_tok.value, index, name_tok.line)
            return A.Identifier(name_tok.value, name_tok.line)

        if self._match(TokenType.LPAREN):
            expr = self._expression()
            self._expect(TokenType.RPAREN, "Expected ')' after expression")
            return expr

        self._error("Expected an expression")


def parse(tokens, source: str = "") -> A.Program:
    """Convenience wrapper: tokens -> Program AST."""
    return Parser(tokens, source).parse()
