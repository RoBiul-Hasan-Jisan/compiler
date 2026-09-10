"""Tree-walking interpreter: executes an mcpp AST directly (no separate
bytecode stage). This is the "code generation" step of the pipeline in
the sense that it produces the program's actual output.
"""

from . import ast_nodes as A
from .environment import Environment
from .errors import MCPPRuntimeError, BreakSignal, ContinueSignal, ReturnSignal

_DEFAULTS = {"int": 0, "float": 0.0, "char": "\0", "string": "", "bool": False}


class Array:
    """A fixed-size array value."""

    __slots__ = ("elem_type", "items")

    def __init__(self, elem_type: str, size: int):
        self.elem_type = elem_type
        self.items = [_DEFAULTS[elem_type]] * size

    def __repr__(self):
        return f"Array({self.items!r})"


class Function:
    """A user-defined function (its AST plus the scope it closes over)."""

    __slots__ = ("decl", "closure")

    def __init__(self, decl: A.FunctionDecl, closure: Environment):
        self.decl = decl
        self.closure = closure


class Interpreter:
    """Evaluates a Program AST, writing program output through `output`.

    `output` defaults to real stdout via print(); pass a custom callable
    (e.g. a list-appending function) to capture output instead, which is
    how the web UI collects results.
    """

    def __init__(self, output=None):
        self.output = output or (lambda text: print(text))
        self.functions = {}
        self.globals = Environment()

    # -- entry point -----------------------------------------------------
    def run(self, program: A.Program, entry: str = "main", args=None):
        for fn in program.functions:
            self.functions[fn.name] = Function(fn, self.globals)
        for gdecl in program.globals:
            self._exec(gdecl, self.globals)

        if entry not in self.functions:
            raise MCPPRuntimeError(f"No '{entry}' function found; a program needs an entry point")
        return self._call_function(self.functions[entry], args or [])

    # -- statements -------------------------------------------------------
    def _exec_block(self, block: A.Block, env: Environment):
        for stmt in block.statements:
            self._exec(stmt, env)

    def _exec(self, node, env: Environment):
        method = getattr(self, f"_exec_{type(node).__name__}", None)
        if method is None:
            raise MCPPRuntimeError(f"No executor for statement {type(node).__name__}", node.line)
        method(node, env)

    def _exec_VarDecl(self, node: A.VarDecl, env: Environment):
        value = self._eval(node.value, env) if node.value is not None else _DEFAULTS[node.var_type]
        env.declare(node.name, self._coerce(value, node.var_type, node.line))

    def _exec_ArrayDecl(self, node: A.ArrayDecl, env: Environment):
        env.declare(node.name, Array(node.elem_type, node.size))

    def _exec_Block(self, node: A.Block, env: Environment):
        self._exec_block(node, env.child())

    def _exec_ExprStatement(self, node: A.ExprStatement, env: Environment):
        self._eval(node.expr, env)

    def _exec_If(self, node: A.If, env: Environment):
        if self._truthy(self._eval(node.condition, env)):
            self._exec_block(node.then_branch, env.child())
        elif node.else_branch is not None:
            if isinstance(node.else_branch, A.If):
                self._exec(node.else_branch, env)
            else:
                self._exec_block(node.else_branch, env.child())

    def _exec_While(self, node: A.While, env: Environment):
        while self._truthy(self._eval(node.condition, env)):
            try:
                self._exec_block(node.body, env.child())
            except BreakSignal:
                break
            except ContinueSignal:
                continue

    def _exec_DoWhile(self, node: A.DoWhile, env: Environment):
        while True:
            try:
                self._exec_block(node.body, env.child())
            except BreakSignal:
                break
            except ContinueSignal:
                pass
            if not self._truthy(self._eval(node.condition, env)):
                break

    def _exec_For(self, node: A.For, env: Environment):
        loop_env = env.child()
        if node.init is not None:
            self._exec(node.init, loop_env)
        while node.condition is None or self._truthy(self._eval(node.condition, loop_env)):
            try:
                self._exec_block(node.body, loop_env.child())
            except BreakSignal:
                break
            except ContinueSignal:
                pass
            if node.update is not None:
                self._eval(node.update, loop_env)

    def _exec_Switch(self, node: A.Switch, env: Environment):
        value = self._eval(node.expr, env)
        matched = False
        default_index = None
        try:
            for i, case in enumerate(node.cases):
                if case.value is None:
                    default_index = i
                    continue
                if not matched and self._values_equal(value, self._eval(case.value, env)):
                    matched = True
                if matched:
                    for stmt in case.statements:
                        self._exec(stmt, env)
            if not matched and default_index is not None:
                for case in node.cases[default_index:]:
                    for stmt in case.statements:
                        self._exec(stmt, env)
        except BreakSignal:
            pass

    def _exec_Break(self, node: A.Break, env: Environment):
        raise BreakSignal()

    def _exec_Continue(self, node: A.Continue, env: Environment):
        raise ContinueSignal()

    def _exec_Return(self, node: A.Return, env: Environment):
        value = self._eval(node.value, env) if node.value is not None else None
        raise ReturnSignal(value)

    def _exec_Print(self, node: A.Print, env: Environment):
        parts = [self._format(self._eval(arg, env)) for arg in node.args]
        self.output("".join(parts))

    # -- expressions -------------------------------------------------------
    def _eval(self, node, env: Environment):
        method = getattr(self, f"_eval_{type(node).__name__}", None)
        if method is None:
            raise MCPPRuntimeError(f"No evaluator for expression {type(node).__name__}", node.line)
        return method(node, env)

    def _eval_Literal(self, node: A.Literal, env: Environment):
        return node.value

    def _eval_Identifier(self, node: A.Identifier, env: Environment):
        try:
            return env.get(node.name)
        except NameError:
            raise MCPPRuntimeError(f"Undefined variable '{node.name}'", node.line)

    def _eval_ArrayAccess(self, node: A.ArrayAccess, env: Environment):
        arr = self._get_array(node.name, env, node.line)
        index = self._eval(node.index, env)
        self._check_index(arr, index, node.name, node.line)
        return arr.items[index]

    def _eval_Assign(self, node: A.Assign, env: Environment):
        value = self._eval(node.value, env)
        if isinstance(node.target, A.Identifier):
            try:
                current = env.get(node.target.name)
                value = self._coerce_like(value, current)
            except NameError:
                pass
            try:
                env.set(node.target.name, value)
            except NameError:
                raise MCPPRuntimeError(f"Undefined variable '{node.target.name}'", node.line)
        else:  # ArrayAccess
            arr = self._get_array(node.target.name, env, node.line)
            index = self._eval(node.target.index, env)
            self._check_index(arr, index, node.target.name, node.line)
            arr.items[index] = self._coerce(value, arr.elem_type, node.line)
        return value

    def _eval_UnaryOp(self, node: A.UnaryOp, env: Environment):
        if node.op in ("++", "--"):
            return self._apply_incdec(node.operand, env, node.op, node.line, prefix=True)
        value = self._eval(node.operand, env)
        if node.op == "-":
            return -value
        if node.op == "!":
            return not self._truthy(value)
        raise MCPPRuntimeError(f"Unknown unary operator '{node.op}'", node.line)

    def _eval_PostfixOp(self, node: A.PostfixOp, env: Environment):
        return self._apply_incdec(node.operand, env, node.op, node.line, prefix=False)

    def _apply_incdec(self, operand, env, op, line, prefix):
        old = self._eval(operand, env)
        new = old + 1 if op == "++" else old - 1
        assign = A.Assign(operand, A.Literal(new, "int", line), line)
        self._eval(assign, env)
        return new if prefix else old

    def _eval_BinOp(self, node: A.BinOp, env: Environment):
        left = self._eval(node.left, env)
        if node.op == "&&":
            return self._truthy(left) and self._truthy(self._eval(node.right, env))
        if node.op == "||":
            return self._truthy(left) or self._truthy(self._eval(node.right, env))

        right = self._eval(node.right, env)
        op = node.op
        try:
            if op == "+":
                return left + right
            if op == "-":
                return left - right
            if op == "*":
                return left * right
            if op == "/":
                return self._divide(left, right, node.line)
            if op == "%":
                if right == 0:
                    raise MCPPRuntimeError("Modulo by zero", node.line)
                return left % right
            if op == "==":
                return self._values_equal(left, right)
            if op == "!=":
                return not self._values_equal(left, right)
            if op == "<":
                return left < right
            if op == "<=":
                return left <= right
            if op == ">":
                return left > right
            if op == ">=":
                return left >= right
        except TypeError:
            raise MCPPRuntimeError(
                f"Type error applying '{op}' to {self._type_name(left)} and {self._type_name(right)}", node.line
            )
        raise MCPPRuntimeError(f"Unknown operator '{op}'", node.line)

    def _divide(self, left, right, line):
        if right == 0:
            raise MCPPRuntimeError("Division by zero", line)
        if isinstance(left, int) and isinstance(right, int):
            # C-style truncating integer division
            result = left / right
            return int(result) if result >= 0 else -int(-result)
        return left / right

    def _eval_FunctionCall(self, node: A.FunctionCall, env: Environment):
        if node.name not in self.functions:
            raise MCPPRuntimeError(f"Call to undefined function '{node.name}'", node.line)
        fn = self.functions[node.name]
        args = [self._eval(a, env) for a in node.args]
        if len(args) != len(fn.decl.params):
            raise MCPPRuntimeError(
                f"'{node.name}' expects {len(fn.decl.params)} argument(s), got {len(args)}", node.line
            )
        return self._call_function(fn, args)

    def _call_function(self, fn: Function, args):
        call_env = fn.closure.child()
        for param, arg in zip(fn.decl.params, args):
            call_env.declare(param.name, self._coerce(arg, param.type, param.line))
        try:
            self._exec_block(fn.decl.body, call_env)
        except ReturnSignal as ret:
            if fn.decl.return_type == "void":
                return None
            return self._coerce(ret.value, fn.decl.return_type, fn.decl.line)
        if fn.decl.return_type != "void":
            raise MCPPRuntimeError(f"Function '{fn.decl.name}' must return a value", fn.decl.line)
        return None

    # -- helpers -------------------------------------------------------
    def _get_array(self, name, env, line):
        try:
            arr = env.get(name)
        except NameError:
            raise MCPPRuntimeError(f"Undefined variable '{name}'", line)
        if not isinstance(arr, Array):
            raise MCPPRuntimeError(f"'{name}' is not an array", line)
        return arr

    def _check_index(self, arr, index, name, line):
        if not isinstance(index, int) or not (0 <= index < len(arr.items)):
            raise MCPPRuntimeError(f"Index {index} out of bounds for array '{name}' (size {len(arr.items)})", line)

    def _truthy(self, value):
        return bool(value)

    def _values_equal(self, left, right):
        return left == right

    def _type_name(self, value):
        if isinstance(value, bool):
            return "bool"
        if isinstance(value, int):
            return "int"
        if isinstance(value, float):
            return "float"
        if isinstance(value, str):
            return "string"
        if isinstance(value, Array):
            return "array"
        return type(value).__name__

    def _coerce(self, value, target_type, line):
        try:
            if target_type == "int":
                return int(value)
            if target_type == "float":
                return float(value)
            if target_type == "bool":
                return bool(value)
            if target_type in ("string", "char"):
                return value
        except (TypeError, ValueError):
            raise MCPPRuntimeError(f"Cannot convert {self._type_name(value)} to {target_type}", line)
        return value

    def _coerce_like(self, value, existing):
        """Keep a variable's declared type stable across reassignment."""
        if isinstance(existing, bool):
            return bool(value)
        if isinstance(existing, int) and isinstance(value, (int, float)):
            return int(value)
        if isinstance(existing, float) and isinstance(value, (int, float)):
            return float(value)
        return value

    def _format(self, value):
        if isinstance(value, bool):
            return "1" if value else "0"
        if isinstance(value, Array):
            return "[" + ", ".join(self._format(v) for v in value.items) + "]"
        if isinstance(value, float):
            text = f"{value:.6f}".rstrip("0").rstrip(".")
            return text if text else "0"
        return str(value)
