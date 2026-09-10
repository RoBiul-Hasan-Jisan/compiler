import pytest

from mcpp.lexer import Lexer
from mcpp.parser import parse
from mcpp import ast_nodes as A
from mcpp.errors import ParseError


def parse_src(source):
    return parse(Lexer(source).tokenize(), source)


def test_empty_function():
    program = parse_src("int main() { return 0; }")
    assert len(program.functions) == 1
    fn = program.functions[0]
    assert fn.name == "main" and fn.return_type == "int"
    assert isinstance(fn.body.statements[0], A.Return)


def test_function_with_params():
    program = parse_src("int add(int x, int y) { return x + y; }")
    fn = program.functions[0]
    assert [p.name for p in fn.params] == ["x", "y"]
    assert [p.type for p in fn.params] == ["int", "int"]


def test_var_decl_with_initializer():
    program = parse_src("int main() { int a = 5; return a; }")
    decl = program.functions[0].body.statements[0]
    assert isinstance(decl, A.VarDecl) and decl.name == "a"
    assert isinstance(decl.value, A.Literal) and decl.value.value == 5


def test_array_decl():
    program = parse_src("int main() { int arr[3]; return 0; }")
    decl = program.functions[0].body.statements[0]
    assert isinstance(decl, A.ArrayDecl) and decl.size == 3


def test_if_else_if_chain():
    src = """
    int main() {
        if (a > b) { print(1); }
        else if (a == b) { print(2); }
        else { print(3); }
        return 0;
    }
    """
    stmt = parse_src(src).functions[0].body.statements[0]
    assert isinstance(stmt, A.If)
    assert isinstance(stmt.else_branch, A.If)
    assert isinstance(stmt.else_branch.else_branch, A.Block)


def test_operator_precedence():
    # a + b * c should parse as a + (b * c)
    program = parse_src("int main() { int r = a + b * c; return 0; }")
    value = program.functions[0].body.statements[0].value
    assert isinstance(value, A.BinOp) and value.op == "+"
    assert isinstance(value.right, A.BinOp) and value.right.op == "*"


def test_for_loop_structure():
    src = "int main() { for (int i = 0; i < 5; i = i + 1) { print(i); } return 0; }"
    stmt = parse_src(src).functions[0].body.statements[0]
    assert isinstance(stmt, A.For)
    assert isinstance(stmt.init, A.VarDecl)
    assert isinstance(stmt.condition, A.BinOp)


def test_switch_with_default():
    src = """
    int main() {
        switch (x) {
            case 1: print(1); break;
            default: print(0);
        }
        return 0;
    }
    """
    stmt = parse_src(src).functions[0].body.statements[0]
    assert isinstance(stmt, A.Switch)
    assert stmt.cases[-1].value is None


def test_missing_semicolon_raises_parse_error():
    with pytest.raises(ParseError):
        parse_src("int main() { int a = 5 return 0; }")


def test_invalid_assignment_target_raises():
    with pytest.raises(ParseError):
        parse_src("int main() { 5 = a; return 0; }")
