class Parser:
    def __init__(self, problem_tracker, stl_library):
        self.problem_tracker = problem_tracker
        self.stl_library = stl_library
        self.current_token_index = 0
        self.tokens = []
    
    def parse(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.parse_program()
    
    def parse_program(self):
        """Parse entire program"""
        while self.current_token_index < len(self.tokens):
            token = self.current_token()
            
            if token.type in ['FUNCTION_DEFINITION', 'FUNCTION_DEFINITION_NO_ARGS']:
                self.parse_function()
            elif token.type == 'LIBRARY_INCLUDE':
                self.parse_include()
            elif token.type == 'PREPROCESSOR_DEFINE':
                self.parse_define()
            else:
                self.advance()
    
    def parse_function(self):
        """Parse function definitions"""
        func_token = self.current_token()
        print(f"Parsing function: {func_token.value} at line {func_token.line}")
        
        # Real-world function analysis
        if 'void' in func_token.value:
            self.problem_tracker.add_problem(
                func_token.line,
                f"Void function defined: {func_token.value}",
                "Ensure function has proper side effects or consider returning a value"
            )
        
        self.advance()
        self.parse_function_body()
    
    def parse_function_body(self):
        """Parse function body"""
        brace_count = 1
        while self.current_token_index < len(self.tokens) and brace_count > 0:
            token = self.current_token()
            
            if token.type == 'SYMBOL_OPEN_BRACE':
                brace_count += 1
            elif token.type == 'SYMBOL_CLOSE_BRACE':
                brace_count -= 1
            
            # Check for STL function usage
            if token.type == 'FUNCTION_CALL':
                self.check_stl_usage(token)
            
            self.advance()
    
    def check_stl_usage(self, token):
        """Check if custom STL can be used"""
        func_name = token.value.strip().split('(')[0]
        if func_name in ['sort', 'swap', 'reverse', 'find', 'copy']:
            self.problem_tracker.add_problem(
                token.line,
                f"Standard function call: {func_name}",
                f"Consider using custom STL: self.stl_library.{func_name}()"
            )
    
    def parse_include(self):
        """Parse include directives"""
        token = self.current_token()
        print(f"Library include: {token.value}")
        self.advance()
    
    def parse_define(self):
        """Parse macro definitions"""
        token = self.current_token()
        self.problem_tracker.add_problem(
            token.line,
            f"Macro definition: {token.value}",
            "Replace with constexpr or inline function for type safety"
        )
        self.advance()
    
    def current_token(self):
        return self.tokens[self.current_token_index] if self.current_token_index < len(self.tokens) else None
    
    def advance(self):
        self.current_token_index += 1