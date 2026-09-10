"""Shared, position-aware error types for every stage of the compiler."""


class MCPPError(Exception):
    """Base class for all compiler errors, carrying source position info."""

    stage = "Error"

    def __init__(self, message: str, line: int = None, column: int = None, source_line: str = None):
        self.message = message
        self.line = line
        self.column = column
        self.source_line = source_line
        super().__init__(self.format())

    def format(self) -> str:
        if self.line is None:
            loc = ""
        elif self.column is None:
            loc = f" (line {self.line})"
        else:
            loc = f" (line {self.line}, col {self.column})"
        out = f"{self.stage}{loc}: {self.message}"
        if self.source_line is not None and self.column is not None:
            pointer = " " * (self.column - 1) + "^"
            out += f"\n    {self.source_line}\n    {pointer}"
        return out

    def __str__(self):
        return self.format()


class LexError(MCPPError):
    stage = "Lexical error"


class ParseError(MCPPError):
    stage = "Syntax error"


class SemanticError(MCPPError):
    stage = "Semantic error"


class MCPPRuntimeError(MCPPError):
    stage = "Runtime error"


class BreakSignal(Exception):
    """Internal control-flow signal used to unwind out of a loop on `break`."""


class ContinueSignal(Exception):
    """Internal control-flow signal used to skip to the next loop iteration."""


class ReturnSignal(Exception):
    """Internal control-flow signal carrying a function's return value."""

    def __init__(self, value=None):
        self.value = value
        super().__init__("return outside function")
