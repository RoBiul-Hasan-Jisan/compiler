#!/usr/bin/env python3
"""
Pure-Python Lexical Analyzer (no regex).
Scans a C-like source file and writes tokens to an output file.
"""

from typing import Optional, Tuple, List

# ---------- Configuration ----------
KEYWORDS = {
    # control flow
    "if", "else", "switch", "case", "for", "while", "do", "break", "continue", "return",
    # declarations & types
    "int", "float", "double", "char", "class", "struct", "enum", "typedef", "using",
    # access & modifiers
    "public", "private", "protected", "static", "const", "volatile", "mutable",
    # concurrency & exceptions
    "async", "await", "throw", "try", "catch", "finally",
    # modules / imports
    "import", "export", "module", "include", "require",
    # boolean / null
    "true", "false", "null", "nullptr", "None",
}

SINGLE_CHAR_OPS = set("+-*/%=&|!<>.,;:()[]{}#@")  # punctuation & operators (single-char)
MULTI_CHAR_OPS = {
    "++", "--", "==", "!=", ">=", "<=", "+=", "-=", "*=", "/=", "%=", "&&", "||",
    "::", "->", "...",
}

# ---------- Data classes ----------
class Token:
    def __init__(self, ttype: str, lexeme: str, filename: str, line: int, col: int):
        self.ttype = ttype
        self.lexeme = lexeme
        self.filename = filename
        self.line = line
        self.col = col

    def __str__(self):
        # Example: Keyword: if (line:10,col:5)
        return f"{self.ttype}: {self.lexeme} (line:{self.line},col:{self.col})"


# ---------- Scanner ----------
class Scanner:
    def __init__(self, text: str, filename: str = "<input>"):
        self.text = text
        self.filename = filename
        self.pos = 0
        self.line = 1
        self.col = 1
        self.length = len(text)

    # -- Basic character helpers --
    def eof(self) -> bool:
        return self.pos >= self.length

    def peek(self, offset: int = 0) -> Optional[str]:
        i = self.pos + offset
        if i >= self.length:
            return None
        return self.text[i]

    def next_char(self) -> Optional[str]:
        if self.eof():
            return None
        ch = self.text[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def make_token(self, ttype: str, lexeme: str, line: int, col: int) -> Token:
        return Token(ttype, lexeme, self.filename, line, col)

    # -- Scanning actions --
    def skip_whitespace(self):
        while not self.eof() and self.peek() is not None and self.peek().isspace():
            self.next_char()

    def scan(self) -> List[Token]:
        tokens: List[Token] = []
        while not self.eof():
            self.skip_whitespace()
            if self.eof():
                break
            ch = self.peek()
            start_line, start_col = self.line, self.col

            # Preprocessor / library include starting with #
            if ch == '#':
                lex = self.read_preprocessor()
                tokens.append(self.make_token("Preprocessor", lex, start_line, start_col))
                continue

            # Comments or divide operator
            if ch == '/':
                nxt = self.peek(1)
                if nxt == '/':
                    lex = self.read_single_line_comment()
                    tokens.append(self.make_token("Comment", lex, start_line, start_col))
                    continue
                elif nxt == '*':
                    lex = self.read_multi_line_comment()
                    tokens.append(self.make_token("Comment", lex, start_line, start_col))
                    continue
                else:
                    # could be operator '/'
                    op = self.read_operator()
                    tokens.append(self.make_token("Operator", op, start_line, start_col))
                    continue

            # Strings
            if ch == '"' or ch == 'r' and self.peek(1) == '"' :
                # treat possible raw strings started with r"...
                lex = self.read_string()
                tokens.append(self.make_token("String", lex, start_line, start_col))
                continue

            # Character literal
            if ch == '\'':
                lex = self.read_char_literal()
                tokens.append(self.make_token("Char", lex, start_line, start_col))
                continue

            # Identifier or keyword or function (identifier followed by '(')
            if ch.isalpha() or ch == '_' :
                ident = self.read_identifier()
                # if it's an include/library directive like #include "stdio.h", we already handled '#'
                # Check for function call: next non-space char is '(' -> capture full function call content
                save_pos = self.pos
                save_line, save_col = self.line, self.col
                self.skip_whitespace()
                if self.peek() == '(':
                    # capture function call including arguments up to matching ')'
                    func_call = self.read_function_call(ident)
                    tokens.append(self.make_token("Function", func_call, start_line, start_col))
                else:
                    # revert any skip_whitespace effect by not changing pos (we saved above but skip_whitespace advanced pos)
                    # We cannot easily revert internal state; instead we've already consumed whitespace — that's fine.
                    # Decide type: keyword or identifier
                    if ident in KEYWORDS:
                        tokens.append(self.make_token("Keyword", ident, start_line, start_col))
                    else:
                        tokens.append(self.make_token("Identifier", ident, start_line, start_col))
                continue

            # Numbers (start with digit or dot followed by digit for float)
            if ch.isdigit() or (ch == '.' and self.peek(1) and self.peek(1).isdigit()):
                num = self.read_number()
                tokens.append(self.make_token("Number", num, start_line, start_col))
                continue

            # Operators and punctuation
            if ch in SINGLE_CHAR_OPS:
                # try multi-char operator first
                op = self.read_operator()
                # classify symbols vs operators vs punctuation
                if op in MULTI_CHAR_OPS or any(c in "+-*/%=&|!<>^" for c in op):
                    tokens.append(self.make_token("Operator", op, start_line, start_col))
                else:
                    tokens.append(self.make_token("Symbol", op, start_line, start_col))
                continue

            # Anything else: consume as unknown token
            # consume a single char to avoid infinite loop
            unknown = self.next_char() or ""
            tokens.append(self.make_token("Unknown", unknown, start_line, start_col))

        return tokens

    # ---------- Readers for token types ----------
    def read_preprocessor(self) -> str:
        # Read from '#' to end of line, but especially extract include "stdio.h" or <stdio.h>
        buf = ""
        ch = self.next_char()
        if ch:
            buf += ch
        # read until newline
        while not self.eof():
            ch = self.peek()
            if ch == '\n':
                break
            buf += self.next_char()
        # If it contains include "..." or <...> try to return Library File token specially
        if 'include' in buf:
            # attempt to extract quoted name or <name>
            if '"' in buf:
                first = buf.find('"')
                last = buf.rfind('"')
                if first != last:
                    lib = buf[first+1:last]
                    return f'Library File: {lib}'
            if '<' in buf and '>' in buf:
                first = buf.find('<')
                last = buf.find('>')
                if first < last:
                    lib = buf[first+1:last]
                    return f'Library File: {lib}'
        return buf

    def read_single_line_comment(self) -> str:
        buf = ""
        # consume //
        buf += self.next_char() or ""
        buf += self.next_char() or ""
        while not self.eof():
            ch = self.peek()
            if ch == '\n':
                break
            buf += self.next_char() or ""
        return buf

    def read_multi_line_comment(self) -> str:
        buf = ""
        # consume /*
        buf += self.next_char() or ""
        buf += self.next_char() or ""
        while not self.eof():
            ch = self.next_char()
            if ch is None:
                break
            buf += ch
            # check for */
            if buf.endswith("*/"):
                break
        return buf

    def read_string(self) -> str:
        # handle normal and raw strings (r"..." or "...")
        buf = ""
        # detect optional r prefix
        if self.peek() == 'r' and self.peek(1) == '"':
            buf += self.next_char() or ""
        if self.peek() == '"':
            delim = self.next_char() or '"'
            buf += delim
            escaped = False
            while not self.eof():
                ch = self.next_char()
                if ch is None:
                    break
                buf += ch
                if escaped:
                    escaped = False
                    continue
                if ch == '\\':
                    escaped = True
                    continue
                if ch == '"':
                    break
        return buf

    def read_char_literal(self) -> str:
        buf = ""
        # consume opening '
        buf += self.next_char() or ""
        escaped = False
        while not self.eof():
            ch = self.next_char()
            if ch is None:
                break
            buf += ch
            if escaped:
                escaped = False
                continue
            if ch == '\\':
                escaped = True
                continue
            if ch == '\'':
                break
        return buf

    def read_identifier(self) -> str:
        buf = ""
        while not self.eof():
            ch = self.peek()
            if ch is None:
                break
            if ch.isalnum() or ch == '_':
                buf += self.next_char()
            else:
                break
        return buf

    def read_function_call(self, name: str) -> str:
        # We assume name already read, current pos at char after name (possibly whitespace)
        buf = name
        # read whitespace then opening '('
        while not self.eof() and self.peek() and self.peek().isspace():
            buf += self.next_char()
        if self.peek() != '(':
            return buf
        # Now capture parentheses balanced (naively handle strings and nested parentheses)
        depth = 0
        in_string = False
        escaped = False
        while not self.eof():
            ch = self.next_char()
            if ch is None:
                break
            buf += ch
            if in_string:
                if escaped:
                    escaped = False
                    continue
                if ch == '\\':
                    escaped = True
                    continue
                if ch == '"':
                    in_string = False
                continue
            else:
                if ch == '"':
                    in_string = True
                    continue
                if ch == '(':
                    depth += 1
                elif ch == ')':
                    depth -= 1
                    if depth <= 0:
                        break
        return buf

    def read_number(self) -> str:
        # Recognize 0x.., 0b.., 0o.., decimals, floats with exponent
        buf = ""
        ch = self.peek()
        # optional leading dot for floats like .5
        if ch == '.':
            buf += self.next_char()
            # read digits
            while self.peek() and self.peek().isdigit():
                buf += self.next_char()
            # optional exponent
            if self.peek() in ('e', 'E'):
                buf += self.read_exponent()
            return buf

        # Read initial digits, or 0 for special prefixes
        if ch == '0' and self.peek(1) in ('x', 'X', 'b', 'B', 'o', 'O'):
            buf += self.next_char()  # 0
            buf += self.next_char()  # x/b/o
            base_char = buf[-1].lower()
            # read appropriate digits
            if base_char == 'x':
                while self.peek() and (self.peek().isdigit() or 'a' <= self.peek().lower() <= 'f'):
                    buf += self.next_char()
            elif base_char == 'b':
                while self.peek() and self.peek() in '01':
                    buf += self.next_char()
            elif base_char == 'o':
                while self.peek() and self.peek() in '01234567':
                    buf += self.next_char()
            return buf
        else:
            # decimal or float
            while self.peek() and self.peek().isdigit():
                buf += self.next_char()
            if self.peek() == '.':
                buf += self.next_char()
                while self.peek() and self.peek().isdigit():
                    buf += self.next_char()
            if self.peek() in ('e', 'E'):
                buf += self.read_exponent()
            return buf

    def read_exponent(self) -> str:
        buf = ""
        ch = self.next_char()  # 'e' or 'E'
        if ch is None:
            return ""
        buf += ch
        # optional sign
        if self.peek() in ('+', '-'):
            buf += self.next_char()
        while self.peek() and self.peek().isdigit():
            buf += self.next_char()
        return buf

    def read_operator(self) -> str:
        # Attempt to match multi-char operators first
        # Lookahead up to 3 chars (for '...')
        max_look = 3
        for L in range(max_look, 0, -1):
            candidate = "".join((self.peek(i) or "") for i in range(L))
            if candidate in MULTI_CHAR_OPS:
                # consume L chars
                out = ""
                for _ in range(L):
                    out += self.next_char() or ""
                return out
        # else single char
        return (self.next_char() or "")


# ---------- Utility: write tokens to output ----------
def write_tokens(tokens: List[Token], outpath: str):
    with open(outpath, "w", encoding="utf-8") as f:
        for tok in tokens:
            # For clarity, do special formatting for Library File tokens we returned from read_preprocessor
            if tok.ttype == "Preprocessor" and tok.lexeme.startswith("Library File:"):
                f.write(f"{tok.lexeme}\n")
                continue
            # Print types like "Keyword: int" or "Identifier: x"
            # If token lexeme contains newlines (like multi-line comment), preserve it as single-line in file with replacement
            lex = tok.lexeme.replace("\n", "\\n")
            f.write(f"{tok.ttype}: {lex}\n")


# ---------- CLI ----------
def main():
    import sys
    if len(sys.argv) < 3:
        print("Usage: python lexer.py <input-file> <output-file>")
        return
    inp = sys.argv[1]
    out = sys.argv[2]
    with open(inp, "r", encoding="utf-8") as f:
        src = f.read()
    sc = Scanner(src, filename=inp)
    tokens = sc.scan()
    # Post-process tokens to match example: turn certain Preprocessor entries into Library File and place Keyword/Identifier ordering
    # Our scanner already marks Library in Preprocessor token's lexeme. So just write tokens.
    write_tokens(tokens, out)
    print(f"Wrote {len(tokens)} tokens to {out}")

if __name__ == "__main__":
    main()
