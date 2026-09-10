import pytest

from .helpers import run
from mcpp.errors import MCPPRuntimeError


def test_arithmetic_and_print():
    out, ret = run("int main() { print(2 + 3 * 4); return 0; }")
    assert out == ["14"]


def test_integer_division_truncates():
    out, _ = run("int main() { print(7 / 2); return 0; }")
    assert out == ["3"]


def test_float_division():
    out, _ = run("int main() { print(7.0 / 2.0); return 0; }")
    assert out == ["3.5"]


def test_bool_prints_as_1_or_0():
    out, _ = run("int main() { print(true); print(false); return 0; }")
    assert out == ["1", "0"]


def test_if_else():
    out, _ = run("""
    int main() {
        int a = 5; int b = 10;
        if (a > b) { print("bigger"); } else { print("smaller"); }
        return 0;
    }
    """)
    assert out == ["smaller"]


def test_while_loop():
    out, _ = run("""
    int main() {
        int i = 0;
        while (i < 3) { print(i); i++; }
        return 0;
    }
    """)
    assert out == ["0", "1", "2"]


def test_for_loop():
    out, _ = run("""
    int main() {
        for (int i = 0; i < 3; i = i + 1) { print(i); }
        return 0;
    }
    """)
    assert out == ["0", "1", "2"]


def test_do_while_runs_at_least_once():
    out, _ = run("""
    int main() {
        int i = 10;
        do { print(i); i++; } while (i < 5);
        return 0;
    }
    """)
    assert out == ["10"]


def test_break_and_continue():
    out, _ = run("""
    int main() {
        int i = 0;
        while (i < 5) {
            i++;
            if (i == 2) { continue; }
            if (i == 4) { break; }
            print(i);
        }
        return 0;
    }
    """)
    assert out == ["1", "3"]


def test_function_call_and_recursion():
    out, ret = run("""
    int factorial(int n) {
        if (n <= 1) { return 1; }
        return n * factorial(n - 1);
    }
    int main() {
        print(factorial(5));
        return 0;
    }
    """)
    assert out == ["120"]


def test_arrays():
    out, _ = run("""
    int main() {
        int arr[3];
        arr[0] = 10; arr[1] = 20; arr[2] = 30;
        print(arr[0] + arr[1] + arr[2]);
        return 0;
    }
    """)
    assert out == ["60"]


def test_array_out_of_bounds_raises():
    with pytest.raises(MCPPRuntimeError):
        run("int main() { int arr[2]; print(arr[5]); return 0; }")


def test_switch_case():
    out, _ = run("""
    int main() {
        int x = 2;
        switch (x) {
            case 1: print("one"); break;
            case 2: print("two"); break;
            default: print("other");
        }
        return 0;
    }
    """)
    assert out == ["two"]


def test_switch_fallthrough_without_break():
    out, _ = run("""
    int main() {
        int x = 1;
        switch (x) {
            case 1: print("a");
            case 2: print("b"); break;
            case 3: print("c");
        }
        return 0;
    }
    """)
    assert out == ["a", "b"]


def test_logical_operators_short_circuit():
    out, _ = run("""
    int sideEffect() { print("called"); return 1; }
    int main() {
        bool r = false && (sideEffect() == 1);
        print(r);
        return 0;
    }
    """)
    # sideEffect() must NOT be called because of short-circuit evaluation
    assert out == ["0"]


def test_string_concatenation():
    out, _ = run('int main() { string s = "Hi " + "there"; print(s); return 0; }')
    assert out == ["Hi there"]


def test_division_by_zero_raises():
    with pytest.raises(MCPPRuntimeError):
        run("int main() { print(1 / 0); return 0; }")


def test_undefined_variable_raises():
    with pytest.raises(MCPPRuntimeError):
        run("int main() { print(x); return 0; }")


def test_return_value_from_main():
    _, ret = run("int main() { return 42; }")
    assert ret == 42
