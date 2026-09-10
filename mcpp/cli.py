"""Command-line entry point for the mcpp compiler.

Usage:
    python -m mcpp.cli path/to/program.mcpp
    python -m mcpp.cli path/to/program.mcpp --tokens     # dump the token stream
    python -m mcpp.cli path/to/program.mcpp --ast        # dump the AST
"""

import argparse
import sys

from .lexer import Lexer
from .parser import parse
from .interpreter import Interpreter
from .errors import MCPPError


def run_source(source: str, show_tokens=False, show_ast=False, output=None) -> int:
    """Run one mcpp program end-to-end. Returns a process-style exit code."""
    try:
        tokens = Lexer(source).tokenize()
        if show_tokens:
            for tok in tokens:
                print(tok)

        program = parse(tokens, source)
        if show_ast:
            import pprint
            pprint.pprint(program)

        result = Interpreter(output=output).run(program)
        return int(result) if isinstance(result, (int, float)) and not isinstance(result, bool) else 0

    except MCPPError as err:
        print(str(err), file=sys.stderr)
        return 1


def main(argv=None):
    parser = argparse.ArgumentParser(prog="mcpp", description="Compile and run an mcpp (.mcpp) source file")
    parser.add_argument("file", help="path to the .mcpp source file")
    parser.add_argument("--tokens", action="store_true", help="print the token stream before running")
    parser.add_argument("--ast", action="store_true", help="print the parsed AST before running")
    args = parser.parse_args(argv)

    try:
        with open(args.file, "r", encoding="utf-8") as f:
            source = f.read()
    except OSError as e:
        print(f"Could not read '{args.file}': {e}", file=sys.stderr)
        return 1

    return run_source(source, show_tokens=args.tokens, show_ast=args.ast)


if __name__ == "__main__":
    sys.exit(main())
