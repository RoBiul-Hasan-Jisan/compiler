from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Token:
    type: str
    value: str
    line: int
    column: int
    filename: str

class Lexer:
    def __init__(self, problem_tracker):
        self.problem_tracker = problem_tracker
        self.tokens = []
        self.line_num = 1
        self.column_num = 1
        self.filename = "input.txt"
        
        # Keywords and their token types
        self.keywords = {
            'if': 'KEYWORD_IF',
            'else': 'KEYWORD_ELSE', 
            'for': 'KEYWORD_FOR',
            'while': 'KEYWORD_WHILE',
            'do': 'KEYWORD_DO',
            'return': 'KEYWORD_RETURN',
            'class': 'KEYWORD_CLASS',
            'struct': 'KEYWORD_STRUCT',
            'public': 'KEYWORD_PUBLIC',
            'private': 'KEYWORD_PRIVATE',
            'protected': 'KEYWORD_PROTECTED',
            'static': 'KEYWORD_STATIC',
            'const': 'KEYWORD_CONST',
            'virtual': 'KEYWORD_VIRTUAL',
            'new': 'KEYWORD_NEW',
            'delete': 'KEYWORD_DELETE',
            'sizeof': 'KEYWORD_SIZEOF',
            'true': 'BOOLEAN_LITERAL',
            'false': 'BOOLEAN_LITERAL',
            'nullptr': 'NULL_LITERAL',
            'NULL': 'NULL_LITERAL'
        }
        
        # Data types
        self.types = {
            'int': 'TYPE_INT',
            'float': 'TYPE_FLOAT', 
            'double': 'TYPE_DOUBLE',
            'char': 'TYPE_CHAR',
            'void': 'TYPE_VOID',
            'bool': 'TYPE_BOOL',
            'long': 'TYPE_LONG',
            'short': 'TYPE_SHORT',
            'signed': 'TYPE_SIGNED',
            'unsigned': 'TYPE_UNSIGNED'
        }
        
        # Multi-character operators
        self.multi_char_ops = {
            '++': 'OPERATOR_INCREMENT',
            '--': 'OPERATOR_DECREMENT',
            '+=': 'OPERATOR_ADD_ASSIGN',
            '-=': 'OPERATOR_SUB_ASSIGN',
            '*=': 'OPERATOR_MUL_ASSIGN',
            '/=': 'OPERATOR_DIV_ASSIGN',
            '==': 'OPERATOR_EQUAL',
            '!=': 'OPERATOR_NOT_EQUAL',
            '<=': 'OPERATOR_LESS_EQUAL',
            '>=': 'OPERATOR_GREATER_EQUAL',
            '&&': 'OPERATOR_AND',
            '||': 'OPERATOR_OR',
            '<<': 'OPERATOR_LEFT_SHIFT',
            '>>': 'OPERATOR_RIGHT_SHIFT',
            '->': 'OPERATOR_ARROW',
            '::': 'OPERATOR_SCOPE'
        }
        
        # Single character symbols
        self.symbols = {
            '{': 'SYMBOL_OPEN_BRACE',
            '}': 'SYMBOL_CLOSE_BRACE',
            '(': 'SYMBOL_OPEN_PAREN',
            ')': 'SYMBOL_CLOSE_PAREN',
            '[': 'SYMBOL_OPEN_BRACKET',
            ']': 'SYMBOL_CLOSE_BRACKET',
            ';': 'SYMBOL_SEMICOLON',
            ',': 'SYMBOL_COMMA',
            '.': 'SYMBOL_DOT',
            ':': 'SYMBOL_COLON',
            '?': 'SYMBOL_QUESTION'
        }
        
        # Arithmetic operators
        self.arithmetic_ops = '+-*/%'
        
        # Other operators
        self.other_ops = '=<>!&|~^'

    def tokenize(self, code: str, filename: str = "input.txt") -> List[Token]:
        self.tokens = []
        self.line_num = 1
        self.column_num = 1
        self.filename = filename
        self.code = code
        self.pos = 0
        self.length = len(code)
        
        while self.pos < self.length:
            self.skip_whitespace()
            if self.pos >= self.length:
                break
                
            char = self.code[self.pos]
            
            # Try to match different token types in order of precedence
            if self.match_multi_line_comment():
                continue
            elif self.match_single_line_comment():
                continue
            elif self.match_preprocessor():
                continue
            elif self.match_string_literal():
                continue
            elif self.match_char_literal():
                continue
            elif self.match_multi_char_operator():
                continue
            elif self.match_number():
                continue
            elif self.match_identifier_or_keyword():
                continue
            elif self.match_symbol():
                continue
            elif self.match_operator():
                continue
            else:
                # Unrecognized character
                self.problem_tracker.add_problem(
                    self.line_num, 
                    f"Unrecognized character: '{char}'",
                    "Remove or fix the unrecognized character"
                )
                self.advance()

        return self.tokens

    def advance(self, n=1):
        """Advance the position by n characters"""
        for _ in range(n):
            if self.pos < self.length:
                if self.code[self.pos] == '\n':
                    self.line_num += 1
                    self.column_num = 1
                else:
                    self.column_num += 1
                self.pos += 1

    def skip_whitespace(self):
        """Skip whitespace characters"""
        while self.pos < self.length and self.code[self.pos].isspace():
            self.advance()

    def match_multi_line_comment(self) -> bool:
        """Match /* ... */ comments"""
        if self.pos + 1 < self.length and self.code[self.pos:self.pos+2] == '/*':
            start_line = self.line_num
            start_col = self.column_num
            
            # Find the closing */
            end_pos = self.pos + 2
            while end_pos < self.length - 1:
                if self.code[end_pos:end_pos+2] == '*/':
                    comment = self.code[self.pos:end_pos+2]
                    token = Token('MULTI_LINE_COMMENT', comment, start_line, start_col, self.filename)
                    self.tokens.append(token)
                    
                    # Update position
                    lines = comment.count('\n')
                    if lines > 0:
                        self.line_num += lines
                        last_newline = comment.rfind('\n')
                        self.column_num = len(comment) - last_newline
                    else:
                        self.column_num += len(comment)
                    
                    self.pos = end_pos + 2
                    return True
                end_pos += 1
            
            # If we get here, comment wasn't closed
            self.problem_tracker.add_problem(start_line, "Unclosed multi-line comment", "Add */ to close the comment")
            return False
        return False

    def match_single_line_comment(self) -> bool:
        """Match // comments"""
        if self.pos + 1 < self.length and self.code[self.pos:self.pos+2] == '//':
            start_line = self.line_num
            start_col = self.column_num
            
            # Find the end of line
            end_pos = self.pos + 2
            while end_pos < self.length and self.code[end_pos] != '\n':
                end_pos += 1
            
            comment = self.code[self.pos:end_pos]
            token = Token('SINGLE_LINE_COMMENT', comment, start_line, start_col, self.filename)
            self.tokens.append(token)
            
            self.pos = end_pos
            return True
        return False

    def match_preprocessor(self) -> bool:
        """Match preprocessor directives"""
        if self.code[self.pos] == '#':
            start_line = self.line_num
            start_col = self.column_num
            
            # Find the end of the preprocessor line
            end_pos = self.pos
            while end_pos < self.length and self.code[end_pos] != '\n':
                end_pos += 1
            
            directive = self.code[self.pos:end_pos].strip()
            
            # Determine the type of preprocessor directive
            if directive.startswith('#include'):
                token_type = 'LIBRARY_INCLUDE'
            elif directive.startswith('#define'):
                if '(' in directive and ')' in directive:
                    token_type = 'PREPROCESSOR_MACRO_FUNC'
                else:
                    token_type = 'PREPROCESSOR_DEFINE'
            elif directive.startswith('#ifdef'):
                token_type = 'PREPROCESSOR_IFDEF'
            elif directive.startswith('#ifndef'):
                token_type = 'PREPROCESSOR_IFNDEF'
            elif directive.startswith('#endif'):
                token_type = 'PREPROCESSOR_ENDIF'
            else:
                token_type = 'PREPROCESSOR'
            
            token = Token(token_type, directive, start_line, start_col, self.filename)
            self.tokens.append(token)
            self.identify_problems(token, directive)
            
            self.pos = end_pos
            return True
        return False

    def match_string_literal(self) -> bool:
        """Match string literals"""
        if self.code[self.pos] == '"':
            start_line = self.line_num
            start_col = self.column_num
            
            string_content = '"'
            pos = self.pos + 1
            escaped = False
            
            while pos < self.length:
                char = self.code[pos]
                string_content += char
                
                if escaped:
                    escaped = False
                elif char == '\\':
                    escaped = True
                elif char == '"':
                    # Found the closing quote
                    token = Token('STRING_LITERAL', string_content, start_line, start_col, self.filename)
                    self.tokens.append(token)
                    self.pos = pos + 1
                    return True
                elif char == '\n':
                    # String literal spans multiple lines
                    self.line_num += 1
                    self.column_num = 1
                
                pos += 1
            
            # If we get here, string wasn't closed
            self.problem_tracker.add_problem(start_line, "Unclosed string literal", 'Add " to close the string')
            return False
        return False

    def match_char_literal(self) -> bool:
        """Match character literals"""
        if self.code[self.pos] == "'":
            start_line = self.line_num
            start_col = self.column_num
            
            char_content = "'"
            pos = self.pos + 1
            escaped = False
            
            while pos < self.length:
                char = self.code[pos]
                char_content += char
                
                if escaped:
                    escaped = False
                elif char == '\\':
                    escaped = True
                elif char == "'":
                    # Found the closing quote
                    token = Token('CHAR_LITERAL', char_content, start_line, start_col, self.filename)
                    self.tokens.append(token)
                    self.pos = pos + 1
                    return True
                
                pos += 1
            
            # If we get here, char literal wasn't closed
            self.problem_tracker.add_problem(start_line, "Unclosed character literal", "Add ' to close the character")
            return False
        return False

    def match_multi_char_operator(self) -> bool:
        """Match multi-character operators"""
        for op, token_type in self.multi_char_ops.items():
            if self.code[self.pos:self.pos+len(op)] == op:
                token = Token(token_type, op, self.line_num, self.column_num, self.filename)
                self.tokens.append(token)
                self.advance(len(op))
                return True
        return False

    def match_number(self) -> bool:
        """Match numeric literals"""
        char = self.code[self.pos]
        
        if not char.isdigit() and not (char == '.' and self.pos + 1 < self.length and self.code[self.pos+1].isdigit()):
            return False
        
        start_line = self.line_num
        start_col = self.column_num
        start_pos = self.pos
        
        # Hex literal
        if char == '0' and self.pos + 1 < self.length and self.code[self.pos+1] in 'xX':
            self.pos += 2
            while self.pos < self.length and (self.code[self.pos].isdigit() or 
                   self.code[self.pos].lower() in 'abcdef'):
                self.pos += 1
            value = self.code[start_pos:self.pos]
            token = Token('HEX_LITERAL', value, start_line, start_col, self.filename)
            self.tokens.append(token)
            return True
        
        # Binary literal
        if char == '0' and self.pos + 1 < self.length and self.code[self.pos+1] in 'bB':
            self.pos += 2
            while self.pos < self.length and self.code[self.pos] in '01':
                self.pos += 1
            value = self.code[start_pos:self.pos]
            token = Token('BINARY_LITERAL', value, start_line, start_col, self.filename)
            self.tokens.append(token)
            return True
        
        # Octal literal or regular number
        self.pos = start_pos
        has_dot = False
        has_exponent = False
        
        while self.pos < self.length:
            char = self.code[self.pos]
            
            if char.isdigit():
                self.pos += 1
            elif char == '.' and not has_dot:
                has_dot = True
                self.pos += 1
            elif char.lower() == 'e' and not has_exponent:
                has_exponent = True
                self.pos += 1
                # Check for exponent sign
                if self.pos < self.length and self.code[self.pos] in '+-':
                    self.pos += 1
            else:
                break
        
        value = self.code[start_pos:self.pos]
        
        if has_dot or has_exponent:
            token_type = 'FLOAT_LITERAL'
        elif value.startswith('0') and len(value) > 1 and value not in ['0', '0b', '0x']:
            token_type = 'OCTAL_LITERAL'
        else:
            token_type = 'INTEGER_LITERAL'
        
        token = Token(token_type, value, start_line, start_col, self.filename)
        self.tokens.append(token)
        return True

    def match_identifier_or_keyword(self) -> bool:
        """Match identifiers and keywords"""
        char = self.code[self.pos]
        
        if not (char.isalpha() or char == '_'):
            return False
        
        start_line = self.line_num
        start_col = self.column_num
        start_pos = self.pos
        
        # Read the identifier
        while self.pos < self.length and (self.code[self.pos].isalnum() or self.code[self.pos] == '_'):
            self.pos += 1
        
        value = self.code[start_pos:self.pos]
        
        # Check if it's a keyword
        if value in self.keywords:
            token_type = self.keywords[value]
        elif value in self.types:
            token_type = self.types[value]
        else:
            token_type = 'IDENTIFIER'
        
        token = Token(token_type, value, start_line, start_col, self.filename)
        self.tokens.append(token)
        
        # Check for namespace resolution
        if self.pos + 1 < self.length and self.code[self.pos:self.pos+2] == '::':
            self.advance(2)  # Skip ::
            # Read the next identifier
            next_start = self.pos
            while self.pos < self.length and (self.code[self.pos].isalnum() or self.code[self.pos] == '_'):
                self.pos += 1
            next_value = self.code[next_start:self.pos]
            full_value = value + '::' + next_value
            token = Token('NAMESPACE_RESOLUTION', full_value, start_line, start_col, self.filename)
            # Replace the last token
            self.tokens[-1] = token
            self.identify_problems(token, full_value)
        
        return True

    def match_symbol(self) -> bool:
        """Match single character symbols"""
        char = self.code[self.pos]
        if char in self.symbols:
            token = Token(self.symbols[char], char, self.line_num, self.column_num, self.filename)
            self.tokens.append(token)
            self.advance()
            return True
        return False

    def match_operator(self) -> bool:
        """Match single character operators"""
        char = self.code[self.pos]
        if char in self.arithmetic_ops:
            token = Token('OPERATOR_ARITHMETIC', char, self.line_num, self.column_num, self.filename)
            self.tokens.append(token)
            self.advance()
            return True
        elif char in self.other_ops:
            token = Token('OPERATOR', char, self.line_num, self.column_num, self.filename)
            self.tokens.append(token)
            self.advance()
            return True
        return False
    
   
    
    
    #Its Allow  only my own stl  lib 
    def identify_problems(self, token: Token, value: str):
        """Identify real-world problems in code with better specificity for custom compiler."""

        allowed_libs = {'iostream', 'stl_library.py',''}  # Only allow these

        if token.type == 'LIBRARY_INCLUDE':
            if '<' in value:
                lib = value[value.find('<')+1:value.find('>')].strip()
            elif '"' in value:
                lib = value[value.find('"')+1:value.rfind('"')].strip()
            else:
                lib = value.split()[-1].strip() if ' ' in value else value.strip()

            if lib not in allowed_libs:
                self.problem_tracker.add_problem(
                    token.line,
                    f"Unauthorized library include: {value.strip()}",
                    f"Only <iostream> and 'stl_library.py' are allowed"
                )

        elif token.type == 'FUNCTION_DEFINITION':
            pass

        elif token.type in ['PREPROCESSOR_DEFINE', 'PREPROCESSOR_MACRO_FUNC']:
            if '(' in value:
                self.problem_tracker.add_problem(
                    token.line,
                    f"Function-like macro: {value.strip()}",
                    "Replace with: constexpr function or template for type safety and debugging"
                )
            else:
                self.problem_tracker.add_problem(
                    token.line,
                    f"Constant macro: {value.strip()}",
                    "Replace with: constexpr variable for better scope and type safety"
                )

        elif token.type == 'IDENTIFIER' and '(' in value:
            func_name = value.split('(')[0].strip()
            restricted_funcs = {'printf': 'STLLibrary.printf()', 
                                'scanf': 'STLLibrary.scanf()',
                                'malloc': 'STLLibrary.malloc()', 
                                'free': 'STLLibrary.free()'}

            if func_name in restricted_funcs:
                self.problem_tracker.add_problem(
                    token.line,
                    f"Direct call to '{func_name}' is not allowed",
                    f"Use {restricted_funcs[func_name]} instead"
                )

        elif token.type == 'NAMESPACE_RESOLUTION':
            if 'std::' in value:
                algo_name = value.split('::')[-1]
                self.problem_tracker.add_problem(
                    token.line,
                    f"Standard algorithm used: {value}",
                    f"Learning exercise: Create your own {algo_name} implementation in custom STL"
                )
