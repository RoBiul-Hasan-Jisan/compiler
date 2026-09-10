"""Lexical analyzer: turns mcpp source text into a stream of Tokens."""

from .tokens import Token, TokenType, KEYWORDS
from .errors import LexError

_SIMPLE_TOKENS = {
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    "{": TokenType.LBRACE,
    "}": TokenType.RBRACE,
    "[": TokenType.LBRACKET,
    "]": TokenType.RBRACKET,
    ";": TokenType.SEMICOLON,
    ",": TokenType.COMMA,
    ":": TokenType.COLON,
    "%": TokenType.PERCENT,
}

_ESCAPES = {"n": "\n", "t": "\t", "r": "\r", "\\": "\\", '"': '"', "'": "'", "0": "\0"}


class Lexer:
    """Converts source text into a flat list of Token objects.

    Usage:
        tokens = Lexer(source).tokenize()
    """

    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens = []

    # -- low level cursor helpers -----------------------------------
    def _peek(self, offset=0):
        i = self.pos + offset
        return self.source[i] if i < len(self.source) else "\0"

    def _advance(self):
        ch = self.source[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def _match(self, expected):
        if self._peek() == expected:
            self._advance()
            return True
        return False

    def _error(self, message, line=None, col=None):
        line = self.line if line is None else line
        col = self.col if col is None else col
        source_line = self.source.splitlines()[line - 1] if 0 < line <= len(self.source.splitlines()) else ""
        raise LexError(message, line, col, source_line)

    # -- public API ----------------------------------------------------
    def tokenize(self):
        while self.pos < len(self.source):
            self._skip_whitespace_and_comments()
            if self.pos >= len(self.source):
                break
            start_line, start_col = self.line, self.col
            ch = self._peek()

            if ch.isdigit():
                self._read_number(start_line, start_col)
            elif ch.isalpha() or ch == "_":
                self._read_identifier(start_line, start_col)
            elif ch == '"':
                self._read_string(start_line, start_col)
            elif ch == "'":
                self._read_char(start_line, start_col)
            elif ch in _SIMPLE_TOKENS:
                self._advance()
                self.tokens.append(Token(_SIMPLE_TOKENS[ch], ch, start_line, start_col))
            else:
                self._read_operator(start_line, start_col)

        self.tokens.append(Token(TokenType.EOF, None, self.line, self.col))
        return self.tokens

    # -- whitespace / comments -----------------------------------------
    def _skip_whitespace_and_comments(self):
        while self.pos < len(self.source):
            ch = self._peek()
            if ch in " \t\r\n":
                self._advance()
            elif ch == "/" and self._peek(1) == "/":
                while self.pos < len(self.source) and self._peek() != "\n":
                    self._advance()
            elif ch == "/" and self._peek(1) == "*":
                self._advance()
                self._advance()
                while self.pos < len(self.source) and not (self._peek() == "*" and self._peek(1) == "/"):
                    self._advance()
                if self.pos >= len(self.source):
                    self._error("Unterminated block comment")
                self._advance()
                self._advance()
            else:
                break

    # -- literals --------------------------------------------------------
    def _read_number(self, line, col):
        start = self.pos
        is_float = False
        while self._peek().isdigit():
            self._advance()
        if self._peek() == "." and self._peek(1).isdigit():
            is_float = True
            self._advance()
            while self._peek().isdigit():
                self._advance()
        text = self.source[start:self.pos]
        if is_float:
            self.tokens.append(Token(TokenType.FLOAT_LIT, float(text), line, col))
        else:
            self.tokens.append(Token(TokenType.INT_LIT, int(text), line, col))

    def _read_identifier(self, line, col):
        start = self.pos
        while self._peek().isalnum() or self._peek() == "_":
            self._advance()
        text = self.source[start:self.pos]
        token_type = KEYWORDS.get(text, TokenType.IDENTIFIER)
        if token_type == TokenType.TRUE:
            self.tokens.append(Token(TokenType.TRUE, True, line, col))
        elif token_type == TokenType.FALSE:
            self.tokens.append(Token(TokenType.FALSE, False, line, col))
        else:
            self.tokens.append(Token(token_type, text, line, col))

    def _read_escape(self):
        self._advance()  # consume backslash
        esc = self._peek()
        if esc not in _ESCAPES:
            self._error(f"Unknown escape sequence '\\{esc}'")
        self._advance()
        return _ESCAPES[esc]

    def _read_string(self, line, col):
        self._advance()  # opening quote
        chars = []
        while self._peek() != '"':
            if self.pos >= len(self.source) or self._peek() == "\n":
                self._error("Unterminated string literal", line, col)
            if self._peek() == "\\":
                chars.append(self._read_escape())
            else:
                chars.append(self._advance())
        self._advance()  # closing quote
        self.tokens.append(Token(TokenType.STRING_LIT, "".join(chars), line, col))

    def _read_char(self, line, col):
        self._advance()  # opening quote
        if self._peek() == "\\":
            value = self._read_escape()
        else:
            if self._peek() == "'" or self.pos >= len(self.source):
                self._error("Empty character literal", line, col)
            value = self._advance()
        if not self._match("'"):
            self._error("Unterminated character literal (expected closing ')", line, col)
        self.tokens.append(Token(TokenType.CHAR_LIT, value, line, col))

    # -- operators -----------------------------------------------------
    def _read_operator(self, line, col):
        ch = self._advance()
        two = ch + self._peek()

        double_map = {
            "==": TokenType.EQ, "!=": TokenType.NEQ,
            "<=": TokenType.LTE, ">=": TokenType.GTE,
            "&&": TokenType.AND, "||": TokenType.OR,
            "++": TokenType.PLUS_PLUS, "--": TokenType.MINUS_MINUS,
        }
        if two in double_map:
            self._advance()
            self.tokens.append(Token(double_map[two], two, line, col))
            return

        single_map = {
            "+": TokenType.PLUS, "-": TokenType.MINUS,
            "*": TokenType.STAR, "/": TokenType.SLASH,
            "=": TokenType.ASSIGN, "<": TokenType.LT,
            ">": TokenType.GT, "!": TokenType.NOT,
        }
        if ch in single_map:
            self.tokens.append(Token(single_map[ch], ch, line, col))
            return

        self._error(f"Unexpected character '{ch}'", line, col)
