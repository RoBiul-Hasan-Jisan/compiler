class Node:
    pass

# ---------------- Program & Functions ----------------
class Program(Node):
    def __init__(self, functions):
        self.functions = functions

class FunctionDecl(Node):
    def __init__(self, name, body, params=None):
        self.name = name
        self.body = body
        self.params = params or []

class Block(Node):
    def __init__(self, stmts):
        self.stmts = stmts

# ---------------- Variables & Arrays ----------------
class VarDecl(Node):
    def __init__(self, vtype, name, init=None):
        self.vtype = vtype
        self.name = name
        self.init = init

class ArrayDecl(Node):
    def __init__(self, vtype, name, dims):
        self.vtype = vtype
        self.name = name
        self.dims = dims

class Assignment(Node):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

class ArrayRef(Node):
    def __init__(self, name, indices):
        self.name = name
        self.indices = indices

# ---------------- Expressions ----------------
class PrintStmt(Node):
    def __init__(self, expr):
        self.expr = expr

class ReturnStmt(Node):
    def __init__(self, expr):
        self.expr = expr

class ExprStmt(Node):
    def __init__(self, expr):
        self.expr = expr

class BinaryOp(Node):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

class UnaryOp(Node):
    def __init__(self, op, operand, postfix=False):
        """
        op: 'PLUSPLUS', 'MINUSMINUS', etc.
        operand: the variable or expression
        postfix: True if postfix operator (i++, i--), False if prefix (++i, --i)
        """
        self.op = op
        self.operand = operand
        self.postfix = postfix

class Number(Node):
    def __init__(self, value):
        self.value = value

class String(Node):
    def __init__(self, value):
        self.value = value

class Char(Node):
    def __init__(self, value):
        self.value = value

class VarRef(Node):
    def __init__(self, name):
        self.name = name

class Bool(Node):
    """Represents boolean literals: true or false"""
    def __init__(self, value: bool):
        self.value = value

# ---------------- Control Flow ----------------
class IfStmt(Node):
    def __init__(self, cond, then_block, else_block=None):
        self.cond = cond
        self.then_block = then_block
        self.else_block = else_block

class WhileStmt(Node):
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

class ForStmt(Node):
    def __init__(self, init, cond, update, body):
        self.init = init
        self.cond = cond
        self.update = update
        self.body = body

class BreakStmt(Node):
    """Represents 'break;' inside loops or switch"""
    pass

class ContinueStmt(Node):
    """Represents 'continue;' inside loops"""
    pass

# ---------------- Functions ----------------
class FunctionCall(Node):
    def __init__(self, name, args):
        self.name = name
        self.args = args

# ---------------- Graph Support ----------------
class GraphInit(Node):
    """Represents: graph g(5);"""
    def __init__(self, num_vertices):
        self.num_vertices = num_vertices

class MethodCall(Node):
    """Represents: g.addEdge(0, 1);"""
    def __init__(self, obj, method, args):
        self.obj = obj
        self.method = method
        self.args = args

# ---------------- Switch Statement ----------------
class SwitchStmt(Node):
    """Represents a switch statement"""
    def __init__(self, expr, cases, default=None):
        """
        expr: expression being switched on
        cases: list of CaseStmt objects
        default: DefaultStmt or None
        """
        self.expr = expr
        self.cases = cases
        self.default = default

class CaseStmt(Node):
    """Represents a case inside switch"""
    def __init__(self, value, body):
        self.value = value
        self.body = body

class DefaultStmt(Node):
    """Represents default case inside switch"""
    def __init__(self, body):
        self.body = body
