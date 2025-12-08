"""
Real-world Compiler Implementation
"""

class Compiler:
    def __init__(self, lexer, parser, problem_tracker, stl_library):
        self.lexer = lexer
        self.parser = parser
        self.problem_tracker = problem_tracker
        self.stl_library = stl_library
        self.output = []
    
    def compile(self, input_file: str):
        """Main compilation process"""
        print(f"Compiling: {input_file}")
        
        try:
            # Read source code
            with open(input_file, 'r') as f:
                source_code = f.read()
            
            # Lexical analysis
            print("\n=== LEXICAL ANALYSIS ===")
            tokens = self.lexer.tokenize(source_code, input_file)
            
            # Display tokens
            for token in tokens:
                self.output.append(f"{token.type}: {token.value} (line:{token.line})")
                print(f"{token.type}: {token.value} (line:{token.line})")
            
            # Syntax analysis
            print("\n=== SYNTAX ANALYSIS ===")
            self.parser.parse(tokens)
            
            # Generate output file
            self.generate_output()
            
        except FileNotFoundError:
            print(f"Error: File {input_file} not found")
        except Exception as e:
            print(f"Compilation error: {e}")
    
    def generate_output(self):
        """Generate compilation output with enhanced formatting"""
        try:
            with open('compiler_output.txt', 'w', encoding='utf-8') as f:
                f.write("COMPILER OUTPUT\n")
                f.write("=" * 50 + "\n\n")
                
                f.write("TOKENS:\n")
                f.write("-" * 20 + "\n")
                for line in self.output:
                    f.write(line + '\n')
                
                f.write("\n" + "=" * 60 + "\n")
                f.write("REAL-WORLD PROBLEMS IDENTIFIED\n")
                f.write("=" * 60 + "\n\n")
                
                if not self.problem_tracker.problems:
                    f.write(" No problems identified! Code follows modern C++ best practices.\n")
                else:
                    # Group problems by category for better organization
                    categories = {}
                    for problem in self.problem_tracker.problems:
                        category = problem['category']
                        if category not in categories:
                            categories[category] = []
                        categories[category].append(problem)
                    
                    # Write problems by category
                    for category, problems in categories.items():
                        category_name = self.problem_tracker.get_category_display_name(category)
                        f.write(f" {category_name}:\n")
                        
                        # Sort problems by line number
                        problems.sort(key=lambda x: x['line'])
                        
                        for problem in problems:
                            severity_icon = {
                                'HIGH': 'HI',
                                'MEDIUM': 'ME', 
                                'LOW': 'LO',
                                'INFO': 'IN '
                            }.get(problem['severity'], '  ')
                            
                            f.write(f"  {severity_icon} Line {problem['line']}: {problem['problem']}\n")
                            f.write(f"      Solution: {problem['solution']}\n\n")
                    
                    # Quick fixes summary
                    quick_fixes = self.problem_tracker.get_quick_fixes()
                    if quick_fixes:
                        f.write("🚀 QUICK FIXES SUMMARY:\n")
                        for i, fix in enumerate(quick_fixes, 1):
                            f.write(f"   {i}. {fix}\n")
                        f.write("\n")
                    
                    # Compilation summary
                    summary = self.problem_tracker.get_summary()
                    f.write(" COMPILATION SUMMARY:\n")
                    f.write(f"    Total unique problems: {summary['total_problems']}\n")
                    f.write(f"    High severity issues: {summary['high_severity']}\n")
                    f.write(f"     Medium severity issues: {summary['medium_severity']}\n")
                    f.write(f"    Low severity issues: {summary['low_severity']}\n")
                    f.write(f"     Information items: {summary['info_severity']}\n")
                    f.write(f"    Categories affected: {summary['categories_affected']}\n")
                    f.write(f"    Solutions provided: {summary['solutions_provided']}\n\n")
                    
                    # Overall code quality assessment
                    total_issues = summary['total_problems']
                    if total_issues == 0:
                        f.write(" STATUS: EXCELLENT - Code follows modern C++ best practices!\n")
                    elif total_issues <= 5:
                        f.write(" STATUS: GOOD - Minor improvements suggested\n")
                    elif total_issues <= 15:
                        f.write(" STATUS: MODERATE - Several areas for modernization\n")
                    else:
                        f.write(" STATUS: NEEDS WORK - Significant modernization opportunities\n")
                
                f.write(f"\n" + "=" * 50 + "\n")
                f.write(f"Generated by: Python Regex Compiler\n")
                f.write(f"File: compiler_output.txt\n")
                f.write(f"Timestamp: {self._get_timestamp()}\n")
            
            print(f" Output successfully saved to: compiler_output.txt")
            
        except Exception as e:
            print(f" Error writing to compiler_output.txt: {e}")
    
    def _get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def display_results(self):
        """Display compilation results with improved organization"""
        print("\n" + "=" * 60)
        print(" COMPILATION RESULTS")
        print("=" * 60)
        
        # Show STL capabilities
        #self.stl_library.display_capabilities()
        
        # Show problems with better organization
        self.problem_tracker.display_problems()
        
        # Show quick fixes
        quick_fixes = self.problem_tracker.get_quick_fixes()
        if quick_fixes:
            print(f"\n QUICK FIXES SUMMARY:")
            for i, fix in enumerate(quick_fixes, 1):
                print(f"   {i}. {fix}")
        
        # Detailed summary
        summary = self.problem_tracker.get_summary()
        print(f"\n COMPILATION SUMMARY:")
        print(f"    Total unique problems: {summary['total_problems']}")
        print(f"    High severity issues: {summary['high_severity']}")
        print(f"     Medium severity issues: {summary['medium_severity']}") 
        print(f"    Low severity issues: {summary['low_severity']}")
        print(f"     Information items: {summary['info_severity']}")
        print(f"   Categories affected: {summary['categories_affected']}")
        print(f"    Solutions provided: {summary['solutions_provided']}")
        
        # Overall code quality assessment
        total_issues = summary['total_problems']
        if total_issues == 0:
            print(f"\n STATUS: EXCELLENT - Code follows modern C++ best practices!")
        elif total_issues <= 5:
            print(f"\n STATUS: GOOD - Minor improvements suggested")
        elif total_issues <= 15:
            print(f"\n STATUS: MODERATE - Several areas for modernization")
        else:
            print(f"\n STATUS: NEEDS WORK - Significant modernization opportunities")
        
        print(f"\n Output written to: compiler_output.txt")