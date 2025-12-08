#!/usr/bin/env python3
"""
Main Compiler Entry Point
Real-world compiler with problem tracking and custom STL
"""

import re
import sys
from lexer import Lexer
from parser import Parser
from problem_tracker import ProblemTracker
from stl_library import STLLibrary
from compiler import Compiler

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <input_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # Initialize components
    problem_tracker = ProblemTracker()
    stl_library = STLLibrary()
    lexer = Lexer(problem_tracker)
    parser = Parser(problem_tracker, stl_library)
    compiler = Compiler(lexer, parser, problem_tracker, stl_library)
    
    # Compile the input file
    compiler.compile(input_file)
    
    # Display results
    compiler.display_results()

if __name__ == "__main__":
    main()