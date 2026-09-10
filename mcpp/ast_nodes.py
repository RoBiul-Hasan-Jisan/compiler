"""AST node definitions.

Every node is a plain dataclass carrying a `line` number for error
reporting. Nodes are grouped into expressions (produce a value) and
statements (perform an action).
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any


class Node:
    """Base marker class for every AST node."""


# ---------------------------------------------------------------- program
@dataclass
class Program(Node):
    functions: List["FunctionDecl"]
    globals: List["VarDecl"]


# --------------------------------------------------------------- declares
@dataclass
class Param(Node):
    type: str
    name: str
    line: int = 0


@dataclass
class FunctionDecl(Node):
    return_type: str
    name: str
    params: List[Param]
    body: "Block"
    line: int = 0


@dataclass
class VarDecl(Node):
    var_type: str
    name: str
    value: Optional[Node]
    line: int = 0


@dataclass
class ArrayDecl(Node):
    elem_type: str
    name: str
    size: int
    line: int = 0


# -------------------------------------------------------------- statements
@dataclass
class Block(Node):
    statements: List[Node]
    line: int = 0


@dataclass
class If(Node):
    condition: Node
    then_branch: Block
    else_branch: Optional[Node]  # Block or another If (else-if chain)
    line: int = 0


@dataclass
class While(Node):
    condition: Node
    body: Block
    line: int = 0


@dataclass
class DoWhile(Node):
    body: Block
    condition: Node
    line: int = 0


@dataclass
class For(Node):
    init: Optional[Node]
    condition: Optional[Node]
    update: Optional[Node]
    body: Block
    line: int = 0


@dataclass
class SwitchCase(Node):
    value: Optional[Node]  # None means `default`
    statements: List[Node]
    line: int = 0


@dataclass
class Switch(Node):
    expr: Node
    cases: List[SwitchCase]
    line: int = 0


@dataclass
class Break(Node):
    line: int = 0


@dataclass
class Continue(Node):
    line: int = 0


@dataclass
class Return(Node):
    value: Optional[Node]
    line: int = 0


@dataclass
class Print(Node):
    args: List[Node]
    line: int = 0


@dataclass
class ExprStatement(Node):
    expr: Node
    line: int = 0


# ------------------------------------------------------------- expressions
@dataclass
class Literal(Node):
    value: Any
    literal_type: str  # 'int' | 'float' | 'char' | 'string' | 'bool'
    line: int = 0


@dataclass
class Identifier(Node):
    name: str
    line: int = 0


@dataclass
class ArrayAccess(Node):
    name: str
    index: Node
    line: int = 0


@dataclass
class Assign(Node):
    target: Node  # Identifier or ArrayAccess
    value: Node
    line: int = 0


@dataclass
class BinOp(Node):
    op: str
    left: Node
    right: Node
    line: int = 0


@dataclass
class UnaryOp(Node):
    op: str
    operand: Node
    line: int = 0


@dataclass
class PostfixOp(Node):
    op: str  # '++' or '--'
    operand: Node
    line: int = 0


@dataclass
class FunctionCall(Node):
    name: str
    args: List[Node]
    line: int = 0
