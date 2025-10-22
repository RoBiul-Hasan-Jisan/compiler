class Node: pass

class Program(Node):
    def __init__(self, functions):
        self.functions = functions

class FunctionDecl(Node):
    def __init__(self, name, body):
        self.name = name
        self.body = body

class Block(Node):
    def __init__(self, stmts):
        self.stmts = stmts

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
        postfix: True if it's a postfix operator (i++, i--), False for prefix (++i, --i)
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

