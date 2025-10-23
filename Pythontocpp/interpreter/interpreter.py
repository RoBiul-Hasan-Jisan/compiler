from ast_nodes import *
import copy

# ---------------- Exceptions ----------------
class RuntimeErrorWithLine(Exception):
    pass

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

# ---------------- Interpreter ----------------
class Interpreter:
    def __init__(self, program):
        self.program = program
        # Collect functions
        self.functions = {fn.name: fn for fn in getattr(program, 'functions', [])}
        # Built-in stubs
        self.functions.setdefault('bfs', None)
        self.functions.setdefault('dfs', None)
        if 'main' not in self.functions:
            raise RuntimeError("No main() function found")

    # ---------------- Run Program ----------------
    def run(self):
        return self.exec_function(self.functions['main'])

    def exec_function(self, fn, env=None):
        local_env = copy.deepcopy(env) if env else {}
        try:
            self.exec_block(fn.body, local_env)
        except ReturnException as re:
            return re.value
        return 0

    # ---------------- Block ----------------
    def exec_block(self, block, env):
        for stmt in block.stmts:
            self.exec_stmt(stmt, env)

    # ---------------- Statements ----------------
    def exec_stmt(self, stmt, env):
        if stmt is None: return
        try:
            # Variable declaration
            if isinstance(stmt, VarDecl):
                if stmt.name in env:
                    raise RuntimeErrorWithLine(f"Variable '{stmt.name}' redeclared")
                val = self.eval_expr(stmt.init, env) if stmt.init else self.default_value(stmt.vtype)
                env[stmt.name] = (stmt.vtype, val)
                return

            # Array declaration
            if isinstance(stmt, ArrayDecl):
                if stmt.name in env:
                    raise RuntimeErrorWithLine(f"Array '{stmt.name}' redeclared")
                val = self.init_array(stmt.dims)
                env[stmt.name] = (stmt.vtype, val)
                return

            # Assignment
            if isinstance(stmt, Assignment):
                if isinstance(stmt.name, ArrayRef):
                    self.assign_array(stmt.name, self.eval_expr(stmt.expr, env), env)
                else:
                    if stmt.name not in env:
                        raise RuntimeErrorWithLine(f"Variable '{stmt.name}' not declared")
                    vtype, _ = env[stmt.name]
                    val = self.eval_expr(stmt.expr, env)
                    env[stmt.name] = (vtype, val)
                return

            # Print
            if isinstance(stmt, PrintStmt):
                val = self.eval_expr(stmt.expr, env)
                print(val)
                return

            # Unary operation
            if isinstance(stmt, UnaryOp):
                self.eval_expr(stmt, env)
                return

            # Return
            if isinstance(stmt, ReturnStmt):
                val = self.eval_expr(stmt.expr, env)
                raise ReturnException(val)

            # Expression statement
            if isinstance(stmt, ExprStmt):
                self.eval_expr(stmt.expr, env)
                return

            # If statement
            if isinstance(stmt, IfStmt):
                cond = self.eval_expr(stmt.cond, env)
                if cond:
                    self.exec_block(stmt.then_block, env)
                elif stmt.else_block:
                    self.exec_block(stmt.else_block, env)
                return

            # While loop
            if isinstance(stmt, WhileStmt):
                while self.eval_expr(stmt.cond, env):
                    self.exec_block(stmt.body, env)
                return

            # For loop
            if isinstance(stmt, ForStmt):
                if stmt.init:
                    self.exec_stmt(stmt.init, env)
                while True:
                    cond_val = True
                    if stmt.cond:
                        cond_val = self.eval_expr(stmt.cond, env)
                    if not cond_val:
                        break
                    self.exec_block(stmt.body, env)
                    if stmt.update:
                        self.eval_stmt_or_expr(stmt.update, env)
                return

        except RuntimeErrorWithLine as e:
            raise RuntimeErrorWithLine(f"{e} at statement {stmt}")
        except ReturnException:
            raise
        except Exception as e:
            raise RuntimeErrorWithLine(f"{e} at statement {stmt}")

    # ---------------- Helpers ----------------
    def eval_stmt_or_expr(self, stmt_or_expr, env):
        if isinstance(stmt_or_expr, (Assignment, UnaryOp, ExprStmt)):
            self.exec_stmt(stmt_or_expr, env)
        else:
            self.eval_expr(stmt_or_expr, env)

    def default_value(self, vtype):
        if vtype in ('INT','LONG','DOUBLE','FLOAT','LONG LONG'): return 0
        if vtype=='CHAR': return '\0'
        if vtype=='STRING': return ""
        if vtype=='BOOL': return 0
        return None

    def init_array(self, dims):
        if not dims: return 0
        return [self.init_array(dims[1:]) for _ in range(dims[0])]

    def assign_array(self, array_ref, value, env):
        _, arr = env[array_ref.name]
        ref = arr
        for idx in array_ref.indices[:-1]:
            i = self.eval_expr(idx, env)
            if i < 0 or i >= len(ref):
                raise RuntimeErrorWithLine(f"Array index {i} out of bounds")
            ref = ref[i]
        i = self.eval_expr(array_ref.indices[-1], env)
        if i < 0 or i >= len(ref):
            raise RuntimeErrorWithLine(f"Array index {i} out of bounds")
        ref[i] = value

    def eval_array_ref(self, array_ref, env):
        _, arr = env[array_ref.name]
        ref = arr
        for idx in array_ref.indices:
            i = self.eval_expr(idx, env)
            if i < 0 or i >= len(ref):
                raise RuntimeErrorWithLine(f"Array index {i} out of bounds")
            ref = ref[i]
        return ref

    # ---------------- Expression Evaluation ----------------
    def eval_expr(self, expr, env):
        if expr is None: return 0
        if isinstance(expr, Number): return expr.value
        if isinstance(expr, String): return expr.value
        if isinstance(expr, Char): return expr.value

        if isinstance(expr, VarRef):
            if expr.name in ('TRUE','FALSE'):
                return 1 if expr.name=='TRUE' else 0
            if expr.name not in env:
                raise RuntimeErrorWithLine(f"Variable '{expr.name}' not declared")
            return env[expr.name][1]

        if isinstance(expr, ArrayRef):
            return self.eval_array_ref(expr, env)

        if isinstance(expr, BinaryOp):
            l = self.eval_expr(expr.left, env)
            r = self.eval_expr(expr.right, env)
            return self._apply_binary_op(expr.op, l, r)

        if isinstance(expr, UnaryOp):
            return self._apply_unary(expr, env)

        if isinstance(expr, FunctionCall):
            return self.eval_function_call(expr, env)

        raise RuntimeErrorWithLine(f"Unknown expression {expr} of type {type(expr)}")

    # ---------------- Function Support ----------------
    def eval_function_call(self, node, env):
        func = self.functions.get(node.name)
        if not func:
            raise RuntimeError(f"Function '{node.name}' not defined")
        if len(func.params) != len(node.args):
            raise RuntimeError(f"Function '{node.name}' expects {len(func.params)} args, got {len(node.args)}")

        # Evaluate arguments
        arg_values = [self.eval_expr(arg, env or {}) for arg in node.args]

        # Local environment
        local_env = copy.deepcopy(env) if env else {}
        for (p_type, p_name), val in zip(func.params, arg_values):
            local_env[p_name] = (p_type, val)

        # Execute function
        try:
            self.exec_block(func.body, local_env)
        except ReturnException as ret:
            return ret.value
        return None

    # ---------------- Operators ----------------
    def _apply_binary_op(self, op, l, r):
        if op=='PLUS': return l+r
        if op=='MINUS': return l-r
        if op=='MULT': return l*r
        if op=='DIV': return l//r if isinstance(l,int) and isinstance(r,int) else l/r
        if op=='EQ': return int(l==r)
        if op=='NE': return int(l!=r)
        if op=='GT': return int(l>r)
        if op=='LT': return int(l<r)
        if op=='GE': return int(l>=r)
        if op=='LE': return int(l<=r)
        if op=='AND': return int(bool(l) and bool(r))
        if op=='OR': return int(bool(l) or bool(r))
        raise RuntimeErrorWithLine(f"Unknown binary operator {op}")

    def _apply_unary(self, expr, env):
        if expr.op in ('PLUSPLUS','MINUSMINUS'):
            if isinstance(expr.operand, VarRef):
                return self._apply_unary_var(expr, env)
            elif isinstance(expr.operand, ArrayRef):
                return self._apply_unary_array(expr, env)
            else:
                raise RuntimeErrorWithLine(f"Invalid unary operation {expr.op}")
        if expr.op=='PLUS': return +self.eval_expr(expr.operand, env)
        if expr.op=='MINUS': return -self.eval_expr(expr.operand, env)
        raise RuntimeErrorWithLine(f"Unknown unary operator {expr.op}")

    def _apply_unary_var(self, expr, env):
        vtype, old = env[expr.operand.name]
        if expr.op=='PLUSPLUS':
            env[expr.operand.name] = (vtype, old+1)
            return old if getattr(expr,'postfix',False) else old+1
        if expr.op=='MINUSMINUS':
            env[expr.operand.name] = (vtype, old-1)
            return old if getattr(expr,'postfix',False) else old-1

    def _apply_unary_array(self, expr, env):
        arr_ref = expr.operand
        old = self.eval_array_ref(arr_ref, env)
        new_val = old+1 if expr.op=='PLUSPLUS' else old-1
        self.assign_array(arr_ref, new_val, env)
        return old if getattr(expr,'postfix',False) else new_val
