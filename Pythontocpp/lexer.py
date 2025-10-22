##bool  switch  break continue  not  work  hare  just  mantion
# Tokenizer 
KEYWORDS = {
    'int', 'float', 'double', 'long', 'char', 'string', 'bool',
    'return', 'print', 'if', 'else', 'while', 'for',
    'break', 'continue', 'switch', 'case', 'default', 'true', 'false'
}

OPERATORS = {
    '==': 'EQ', '!=': 'NE', '>=': 'GE', '<=': 'LE', 
    '>': 'GT', '<': 'LT', '&&': 'AND', '||': 'OR',
    '++': 'PLUSPLUS', '--': 'MINUSMINUS', '=': 'ASSIGN',
    '+': 'PLUS', '-': 'MINUS', '*': 'MULT', '/': 'DIV'
}

DELIMITERS = {
    '(': 'LPAREN', ')': 'RPAREN', '{': 'LBRACE', '}': 'RBRACE',
    '[': 'LBRACKET', ']': 'RBRACKET', ';': 'SEMI', ',': 'COMMA', ':': 'COLON'
}

def tokenize(code):
    i = 0
    line_num = 1
    length = len(code)
    
    while i < length:
        ch = code[i]

        # --- Skip whitespace ---
        if ch in ' \t':
            i += 1
            continue

        # --- Newline ---
        if ch == '\n':
            line_num += 1
            i += 1
            continue

        # --- Comments ---
        if ch == '/' and i + 1 < length:
            if code[i+1] == '/':  # single-line comment
                while i < length and code[i] != '\n':
                    i += 1
                continue
            elif code[i+1] == '*':  # multi-line comment
                i += 2
                while i + 1 < length and not (code[i] == '*' and code[i+1] == '/'):
                    if code[i] == '\n':
                        line_num += 1
                    i += 1
                i += 2  # skip closing */
                continue

        # --- Numbers ---
        if ch.isdigit():
            num = ch
            i += 1
            has_dot = False
            while i < length and (code[i].isdigit() or (code[i] == '.' and not has_dot)):
                if code[i] == '.':
                    has_dot = True
                num += code[i]
                i += 1
            yield ('NUMBER', float(num) if '.' in num else int(num), i-len(num), line_num)
            continue

        # --- Strings ---
        if ch == '"':
            start = i
            i += 1
            string_val = ''
            while i < length and code[i] != '"':
                if code[i] == '\\' and i + 1 < length:
                    string_val += code[i] + code[i+1]
                    i += 2
                else:
                    string_val += code[i]
                    i += 1
            if i >= length or code[i] != '"':
                raise SyntaxError(f"Unterminated string literal at line {line_num}")
            i += 1
            yield ('STRING_LIT', '"' + string_val + '"', start, line_num)
            continue

        # --- Characters ---
        if ch == "'":
            start = i
            i += 1
            char_val = ''
            if i < length and code[i] != "'":
                if code[i] == '\\' and i + 1 < length:
                    char_val = code[i] + code[i+1]
                    i += 2
                else:
                    char_val = code[i]
                    i += 1
            if i >= length or code[i] != "'":
                raise SyntaxError(f"Unterminated char literal at line {line_num}")
            i += 1
            yield ('CHAR_LIT', "'" + char_val + "'", start, line_num)
            continue

        # --- Identifiers and Keywords ---
        if ch.isalpha() or ch == '_':
            start = i
            ident = ch
            i += 1
            while i < length and (code[i].isalnum() or code[i] == '_'):
                ident += code[i]
                i += 1
            if ident in KEYWORDS:
                yield (ident.upper(), ident, start, line_num)
            else:
                yield ('ID', ident, start, line_num)
            continue

        # --- Operators ---
        matched = False
        for op_len in (2,1):
            if i + op_len <= length:
                substr = code[i:i+op_len]
                if substr in OPERATORS:
                    yield (OPERATORS[substr], substr, i, line_num)
                    i += op_len
                    matched = True
                    break
        if matched:
            continue

        # --- Delimiters ---
        if ch in DELIMITERS:
            yield (DELIMITERS[ch], ch, i, line_num)
            i += 1
            continue

        # --- Unexpected character ---
        raise SyntaxError(f"Unexpected {ch!r} at line {line_num}")
