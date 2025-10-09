import re

# ---------------- Token Specification ----------------
TOKEN_SPEC = [
    # Literals
    ('NUMBER',      r'\b\d+(\.\d+)?\b'),
    ('STRING_LIT',  r'"([^"\\\n]|\\.)*"'),   # avoid newline in string
    ('CHAR_LIT',    r"'([^'\\\n]|\\.)'"),   # avoid newline in char

    # Keywords
    ('INT',         r'\bint\b'), ('FLOAT', r'\bfloat\b'), ('DOUBLE', r'\bdouble\b'),
    ('LONG',        r'\blong\b'), ('CHAR', r'\bchar\b'), ('STRING', r'\bstring\b'),
    ('RETURN',      r'\breturn\b'), ('PRINT', r'\bprint\b'),
    ('IF',          r'\bif\b'), ('ELSE', r'\belse\b'), ('WHILE', r'\bwhile\b'), ('FOR', r'\bfor\b'),

    # Operators
    ('EQ', '=='), ('NE', '!='), ('GE', '>='), ('LE', '<='), ('GT', '>'), ('LT', '<'),
    ('AND', r'&&'), ('OR', r'\|\|'),
    ('PLUSPLUS', r'\+\+'), ('MINUSMINUS', r'--'),
    ('ASSIGN', '='), ('PLUS', r'\+'), ('MINUS', '-'), ('MULT', r'\*'), ('DIV', '/'),

    # Delimiters
    ('LPAREN', r'\('), ('RPAREN', r'\)'), ('LBRACE', r'\{'), ('RBRACE', r'\}'),
    ('LBRACKET', r'\['), ('RBRACKET', r'\]'), ('SEMI', ';'), ('COMMA', ','),

    # Identifiers
    ('ID', r'\b[A-Za-z_][A-Za-z0-9_]*\b'),

    # Skip whitespace
    ('SKIP', r'[ \t]+'),

    # Comments
    ('COMMENT', r'//[^\n]*|/\*.*?\*/'),

    # Newline
    ('NEWLINE', r'\n'),

    # Catch-all
    ('MISMATCH', r'.')
]

# Compile regex
TOKEN_REGEX = '|'.join('(?P<%s>%s)' % pair for pair in TOKEN_SPEC)
Token = tuple  # (type, value, pos, line)

# ---------------- Tokenizer ----------------
def tokenize(code):
    line_num = 1
    for m in re.finditer(TOKEN_REGEX, code, re.DOTALL):
        kind = m.lastgroup
        val = m.group()

        if kind == 'NUMBER':
            yield ('NUMBER', float(val) if '.' in val else int(val), m.start(), line_num)
        elif kind in ('INT','FLOAT','DOUBLE','LONG','CHAR','STRING','RETURN','PRINT','IF','ELSE','WHILE','FOR'):
            yield (kind, val, m.start(), line_num)
        elif kind in ('ID','EQ','NE','GE','LE','GT','LT','AND','OR','ASSIGN','PLUS','MINUS','MULT','DIV',
                      'LPAREN','RPAREN','LBRACE','RBRACE','LBRACKET','RBRACKET','SEMI','COMMA',
                      'STRING_LIT','CHAR_LIT','PLUSPLUS','MINUSMINUS'):
            # Check unterminated strings or chars
            if kind == 'STRING_LIT' and not (val.startswith('"') and val.endswith('"')):
                raise SyntaxError(f"Unterminated string literal at line {line_num}")
            if kind == 'CHAR_LIT' and not (val.startswith("'") and val.endswith("'")):
                raise SyntaxError(f"Unterminated char literal at line {line_num}")
            yield (kind, val, m.start(), line_num)
        elif kind == 'COMMENT' or kind == 'SKIP':
            pass  # ignore
        elif kind == 'NEWLINE':
            line_num += 1
        elif kind == 'MISMATCH':
            raise SyntaxError(f"Unexpected {val!r} at line {line_num}")
