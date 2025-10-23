from copy import deepcopy
from .interpreter import Interpreter
from ast_nodes import FunctionCall, ReturnStmt, IfStmt, WhileStmt, ForStmt

class ReturnException(Exception):
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
        except ReturnException as ret:
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

        # Evaluate arguments
        arg_values = [self.eval_expr(arg, env) for arg in node.args]

        # Create isolated local environment
        local_env = deepcopy(env) if env else {}
        for (p_type, p_name), val in zip(func.params, arg_values):
            local_env[p_name] = (p_type, val)

        # Execute function body
        try:
            self.exec_block(func.body, local_env)
        except ReturnException as ret:
            return ret.value

        return None

    # ---------------- Return Statement ----------------
    def eval_ReturnStmt(self, node, env=None):
        value = self.eval_expr(node.expr, env)
        raise ReturnException(value)

    # ---------------- Override eval_expr ----------------
    def eval_expr(self, expr, env=None):
        if isinstance(expr, FunctionCall):
            return self.eval_FunctionCall(expr, env)
        return super().eval_expr(expr, env)

    # ---------------- Override exec_stmt ----------------
    def exec_stmt(self, stmt, env):
        if isinstance(stmt, ReturnStmt):
            self.eval_ReturnStmt(stmt, env)
        elif isinstance(stmt, IfStmt):
            self.eval_IfStmt(stmt, env)
        elif isinstance(stmt, WhileStmt):
            self.eval_WhileStmt(stmt, env)
        elif isinstance(stmt, ForStmt):
            self.eval_ForStmt(stmt, env)
        else:
            super().exec_stmt(stmt, env)

    # ---------------- Boolean-safe IfStmt ----------------
    def eval_IfStmt(self, node, env):
        cond = self._unwrap(self.eval_expr(node.cond, env))
        if cond:  # nonzero -> True
            self.exec_block(node.then_block, env)
        elif node.else_block:
            self.exec_block(node.else_block, env)

    # ---------------- Boolean-safe WhileStmt ----------------
    def eval_WhileStmt(self, node, env):
        while True:
            cond = self._unwrap(self.eval_expr(node.cond, env))
            if not cond:
                break
            self.exec_block(node.body, env)

    # ---------------- Boolean-safe ForStmt ----------------
    def eval_ForStmt(self, node, env):
        if node.init:
            self.exec_stmt(node.init, env)
        while True:
            cond_val = True
            if node.cond:
                cond_val = self._unwrap(self.eval_expr(node.cond, env))
            if not cond_val:
                break
            self.exec_block(node.body, env)
            if node.update:
                self.eval_stmt_or_expr(node.update, env)

    # ---------------- Helper: unwrap (type,value) ----------------
    def _unwrap(self, val):
        if isinstance(val, tuple) and len(val) == 2:
            return val[1]
        return val
