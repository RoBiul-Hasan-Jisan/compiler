from simple_lexer import SimpleRegexLexer, Token
from dataclasses import dataclass

@dataclass
class Problem:
    line: int
    message: str
    solution: str

class ProblemTracker:
    def __init__(self):
        self.problems = []
    
    def add_problem(self, line, message, solution):
        self.problems.append(Problem(line, message, solution))

def main():
    print("=" * 80)
    print("🎯 C++ CODE LEXER - TOKEN PRESENTATION WITH LINE NUMBERS")
    print("=" * 80)
    
    # Read the C++ code file
    try:
        with open('text.cpp', 'r') as f:
            code = f.read()
        print("📖 Reading: text.cpp")
        print()
    except FileNotFoundError:
        print("❌ Error: text.cpp file not found!")
        return
    
    # Create problem tracker and lexer
    tracker = ProblemTracker()
    lexer = SimpleRegexLexer(tracker)
    
    # Tokenize the code
    tokens = lexer.tokenize(code, 'text.cpp')
    
    # Display tokens in presentation format with line numbers
    print("🔍 TOKENIZED OUTPUT:")
    print("=" * 80)
    print(f"{'Line':>4} | {'Token Type':20} | {'Value'}")
    print("-" * 80)
    
    current_line = 0
    for token in tokens:
        # Format token type for nice display
        display_type = format_token_type(token.type, token.value)
        display_value = format_token_value(token.value)
        
        # Show line number only when it changes
        if token.line != current_line:
            print(f"{token.line:4} | {display_type:20} | {display_value}")
            current_line = token.line
        else:
            print(f"{'':4} | {display_type:20} | {display_value}")
    
    # Show problems found
    if tracker.problems:
        print("\n" + "=" * 80)
        print("⚠️  CODE ANALYSIS ISSUES FOUND:")
        print("=" * 80)
        for problem in tracker.problems:
            print(f"Line {problem.line:3}: {problem.message}")
            print(f"{'':8}💡 {problem.solution}")
            print()

    # Show summary
    print("=" * 80)
    print(f"📊 SUMMARY: {len(tokens)} tokens processed, {len(tracker.problems)} issues found")
    print("=" * 80)

def format_token_type(token_type: str, value: str) -> str:
    """Format token types for nice presentation"""
    type_map = {
        
        'STANDARD_LIBRARY': 'Library File',
        'OWN_LIBRARY': 'Own Library',
        'PREPROCESSOR': 'CPP Directive',
        'KEYWORD': 'Keyword',
        'TYPE': 'Type',
        'IDENTIFIER': lambda v: 'Function' if '(' in v and ')' in v and not v.startswith('#') else 'Identifier',
        'OPERATOR_1CHAR': 'Operator',
        'OPERATOR_2CHAR': 'Operator',
        'SYMBOL': 'Symbol',
        'COMMENT': 'Comment',
        'STRING': 'String Literal',
        'CHAR': 'Character Literal',
        'INT_NUMBER': 'Number',
        'FLOAT_NUMBER': 'Number',
        'HEX_NUMBER': 'Number',
        'BINARY_NUMBER': 'Number',
        'OCTAL_NUMBER': 'Number',
        'BOOLEAN': 'Boolean',
        'NULL': 'Null',
        'NAMESPACE': 'Namespace'
    }
    
    if token_type in type_map:
        mapper = type_map[token_type]
        if callable(mapper):
            return mapper(value)
        return mapper
    return token_type

def format_token_value(value: str) -> str:
    """Format token values for nice presentation"""
    # Handle comments
    if value.startswith('//'):
        return value[2:].strip()
    elif value.startswith('/*'):
        # For multi-line comments, show first line only
        lines = value[2:-2].split('\n')
        if len(lines) > 1:
            return lines[0].strip() + " ..."
        return lines[0].strip() if lines[0].strip() else "multi-line comment"
    
    # Handle strings - show content without quotes
    if value.startswith('"') and value.endswith('"'):
        content = value[1:-1]
        # Handle escape sequences
        content = content.replace('\\n', '\\\\n').replace('\\t', '\\\\t')
        return f'"{content}"'
    
    # Handle characters
    if value.startswith("'") and value.endswith("'"):
        return f"'{value[1:-1]}'"
    
    # Handle preprocessor
    if value.startswith('#'):
        if 'include' in value:
            lib_match = re.search(r'[<"]([^>"]+)[>"]', value)
            if lib_match:
                return lib_match.group(1)
        return value
    
    return value

# Add regex import for the format function
import re

if __name__ == "__main__":
    main()