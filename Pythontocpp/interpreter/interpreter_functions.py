from .interpreter import Interpreter  # relative import
from ast_nodes import FunctionCall, ReturnStmt, IfStmt, WhileStmt

class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value

class InterpreterWithFunctions(Interpreter):
    def __init__(self, program):
        super().__init__(program)
        # Collect all functions in a dictionary
        self.functions = {f.name: f for f in getattr(program, 'functions', [])}
        if 'main' not in self.functions:
            raise RuntimeError("No main() function found")

    # ---------------- Run Program ----------------
    def run(self):
        try:
            return super().run()
        except ReturnValue as ret:
            return ret.value

    # ---------------- Function Call ----------------
    def eval_FunctionCall(self, node, env=None):
        func = self.functions.get(node.name)
        if not func:
            raise RuntimeError(f"Function '{node.name}' not defined")

        if len(func.params) != len(node.args):
            raise RuntimeError(
                f"Function '{node.name}' expects {len(func.params)} args, got {len(node.args)}"
            )

        arg_values = [self.eval_expr(arg, env) for arg in node.args]

        local_env = {} if env is None else dict(env)
        for (p_type, p_name), val in zip(func.params, arg_values):
            local_env[p_name] = (p_type, val)

        try:
            for stmt in func.body.stmts:
                self.exec_stmt(stmt, local_env)
        except ReturnValue as ret:
            return ret.value

        return None

    # ---------------- Return Statement ----------------
    def eval_ReturnStmt(self, node, env=None):
        value = self.eval_expr(node.expr, env)
        raise ReturnValue(value)

    # ---------------- Override eval_expr to handle FunctionCall ----------------
    def eval_expr(self, expr, env=None):
        if isinstance(expr, FunctionCall):
            return self.eval_FunctionCall(expr, env)
        return super().eval_expr(expr, env)

    # ---------------- Override exec_stmt to handle ReturnStmt ----------------
    def exec_stmt(self, stmt, env):
        if isinstance(stmt, ReturnStmt):
            self.eval_ReturnStmt(stmt, env)
        elif isinstance(stmt, IfStmt):
            self.eval_IfStmt(stmt, env)
        elif isinstance(stmt, WhileStmt):
            self.eval_WhileStmt(stmt, env)
        else:
            super().exec_stmt(stmt, env)

    # ---------------- Boolean-safe IfStmt ----------------
    def eval_IfStmt(self, node, env):
        cond = self.eval_expr(node.cond, env)
        # If stored as (type, value), take value
        if isinstance(cond, tuple):
            cond = cond[1]
        if cond:  # 0 -> False, nonzero -> True
            self.exec_block(node.then_block, env)
        elif node.else_block:
            self.exec_block(node.else_block, env)

    # ---------------- Boolean-safe WhileStmt ----------------
    def eval_WhileStmt(self, node, env):
        while True:
            cond = self.eval_expr(node.cond, env)
            if isinstance(cond, tuple):
                cond = cond[1]
            if not cond:
                break
            self.exec_block(node.body, env)
