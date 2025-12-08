"""
Enhanced Real-world Problem Identification and Tracking
"""

class ProblemTracker:
    def __init__(self):
        self.problems = []
        self.solutions_provided = 0
        self.problem_signatures = set()  # To track duplicates
    
    def add_problem(self, line: int, problem: str, solution: str):
        """Add identified problem with solution, avoiding duplicates"""
        # Create a more specific signature to avoid different problems on same line
        signature = f"{line}:{self._create_problem_signature(problem)}"
        
        if signature not in self.problem_signatures:
            self.problem_signatures.add(signature)
            
            # Categorize and assess severity before adding
            category = self.categorize_problem(problem, solution)
            severity = self.assess_severity(problem, solution)
            
            self.problems.append({
                'line': line,
                'problem': problem,
                'solution': solution,
                'severity': severity,
                'category': category
            })
            self.solutions_provided += 1
    
    def _create_problem_signature(self, problem: str) -> str:
        """Create a unique signature for the problem to avoid duplicates"""
        # Extract key words from the problem description
        problem_lower = problem.lower()
        
        # Identify the main issue type
        if 'include' in problem_lower:
            return 'include'
        elif 'macro' in problem_lower:
            if 'function-like' in problem_lower:
                return 'macro_function'
            else:
                return 'macro_constant'
        elif 'void function' in problem_lower or 'function returns void' in problem_lower:
            if 'processing' in problem_lower:
                return 'void_processing_function'
            else:
                return 'void_function'
        elif 'printf' in problem_lower or 'c-style i/o' in problem_lower:
            return 'c_io'
        elif 'malloc' in problem_lower or 'free' in problem_lower:
            return 'c_memory'
        elif 'std::' in problem_lower or 'standard algorithm' in problem_lower:
            # Extract the algorithm name
            for algo in ['sort', 'reverse', 'swap', 'find', 'copy']:
                if algo in problem_lower:
                    return f'stl_{algo}'
            return 'stl_usage'
        else:
            # Use first 3 words as signature for other problems
            words = problem.split()[:3]
            return '_'.join(words).lower()
    
    def assess_severity(self, problem: str, solution: str) -> str:
        """Assess problem severity with better logic"""
        problem_lower = problem.lower()
        
        if any(word in problem_lower for word in ['memory leak', 'undefined behavior', 'security risk', 'buffer overflow', 'dangling pointer']):
            return 'HIGH'
        elif any(word in problem_lower for word in ['c-style i/o', 'c memory management', 'macro', 'void function', 'deprecated']):
            return 'MEDIUM'
        elif any(word in problem_lower for word in ['standard library', 'include', 'namespace']):
            return 'LOW'
        else:
            return 'INFO'
    
    def categorize_problem(self, problem: str, solution: str) -> str:
        """Categorize problems for better organization"""
        problem_lower = problem.lower()
        
        if any(word in problem_lower for word in ['include', 'import', 'library']):
            return 'MODULE_SYSTEM'
        elif any(word in problem_lower for word in ['macro', 'define', 'preprocessor']):
            return 'MACRO_USAGE'
        elif any(word in problem_lower for word in ['void function', 'function defined', 'function returns']):
            return 'FUNCTION_DESIGN'
        elif any(word in problem_lower for word in ['printf', 'scanf', 'c-style i/o', 'formatted i/o']):
            return 'IO_OPERATIONS'
        elif any(word in problem_lower for word in ['malloc', 'free', 'memory management']):
            return 'MEMORY_MANAGEMENT'
        elif any(word in problem_lower for word in ['std::', 'standard library', 'standard algorithm']):
            return 'STL_USAGE'
        else:
            return 'CODE_QUALITY'
    
    def get_problems_by_line(self, line: int):
        """Get all problems for a specific line"""
        return [p for p in self.problems if p['line'] == line]
    
    def get_problems_by_category(self, category: str):
        """Get problems by category"""
        return [p for p in self.problems if p['category'] == category]
    
    def display_problems(self):
        """Display all identified problems with better organization"""
        if not self.problems:
            print("🎉 No problems identified! Code follows modern C++ best practices.")
            return
        
        print(f"\n🔍 REAL-WORLD PROBLEMS IDENTIFIED ({len(self.problems)} unique issues) ===")
        
        # Group by category
        categories = {}
        for problem in self.problems:
            category = problem['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(problem)
        
        # Display by category with specific advice
        for category, problems in categories.items():
            print(f"\n📁 {self.get_category_display_name(category)}:")
            
            # Sort problems by line number
            problems.sort(key=lambda x: x['line'])
            
            for problem in problems:
                severity_icon = {
                    'HIGH': '🚨',
                    'MEDIUM': '⚠️', 
                    'LOW': '💡',
                    'INFO': 'ℹ️ '
                }.get(problem['severity'], '  ')
                
                print(f"  {severity_icon} Line {problem['line']}: {problem['problem']}")
                print(f"     ✅ Solution: {problem['solution']}")
    
    def get_category_display_name(self, category: str) -> str:
        """Get user-friendly category names"""
        names = {
            'MODULE_SYSTEM': 'Module & Include System',
            'MACRO_USAGE': 'Macro Usage',
            'FUNCTION_DESIGN': 'Function Design',
            'IO_OPERATIONS': 'I/O Operations', 
            'MEMORY_MANAGEMENT': 'Memory Management',
            'STL_USAGE': 'Standard Library Usage',
            'CODE_QUALITY': 'Code Quality'
        }
        return names.get(category, category)
    
    def get_summary(self):
        """Get detailed problem summary"""
        severities = [p['severity'] for p in self.problems]
        categories = [p['category'] for p in self.problems]
        
        return {
            'total_problems': len(self.problems),
            'high_severity': severities.count('HIGH'),
            'medium_severity': severities.count('MEDIUM'),
            'low_severity': severities.count('LOW'),
            'info_severity': severities.count('INFO'),
            'categories_affected': len(set(categories)),
            'solutions_provided': self.solutions_provided
        }
    
    def get_quick_fixes(self):
        """Generate quick fix suggestions"""
        quick_fixes = []
        categories_found = set()
        
        for problem in self.problems:
            category = problem['category']
            if category not in categories_found:
                categories_found.add(category)
                
                if category == 'MODULE_SYSTEM':
                    quick_fixes.append("Replace all #include with C++20 import statements")
                elif category == 'MACRO_USAGE':
                    quick_fixes.append("Convert macros to constexpr/inline functions")
                elif category == 'IO_OPERATIONS':
                    quick_fixes.append("Replace printf/scanf with std::cout/std::cin")
                elif category == 'MEMORY_MANAGEMENT':
                    quick_fixes.append("Use smart pointers instead of malloc/free")
                elif category == 'FUNCTION_DESIGN':
                    quick_fixes.append("Review void functions for better return types")
                elif category == 'STL_USAGE':
                    quick_fixes.append("Implement custom STL algorithms for learning")
        
        return quick_fixes
    
    def get_problem_statistics(self):
        """Get detailed statistics about problems"""
        stats = {
            'total_problems': len(self.problems),
            'by_severity': {
                'HIGH': 0,
                'MEDIUM': 0,
                'LOW': 0,
                'INFO': 0
            },
            'by_category': {},
            'lines_with_issues': set()
        }
        
        for problem in self.problems:
            # Count by severity
            stats['by_severity'][problem['severity']] += 1
            
            # Count by category
            category = problem['category']
            if category not in stats['by_category']:
                stats['by_category'][category] = 0
            stats['by_category'][category] += 1
            
            # Track lines with issues
            stats['lines_with_issues'].add(problem['line'])
        
        stats['total_lines_with_issues'] = len(stats['lines_with_issues'])
        return stats