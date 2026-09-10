# mcpp Language Reference

`mcpp` is a small, C++-flavoured language designed for learning how a
compiler pipeline works. Every program is a set of functions; execution
starts at `main()`.

## 1. Types

| Type     | Example              | Default value |
|----------|-----------------------|--------------|
| `int`    | `int a = 5;`           | `0`          |
| `float`  | `float f = 3.14;`      | `0.0`        |
| `char`   | `char c = 'x';`        | `'\0'`       |
| `string` | `string s = "hello";`  | `""`         |
| `bool`   | `bool flag = true;`    | `false`      |
| `void`   | function return type only | — |

Variables must be declared with a type before use, and only once per
scope.

## 2. Arrays

Arrays are fixed-size and declared with an integer literal size:

```c
int arr[3];
arr[0] = 10;
print(arr[0]);
```

Indexing starts at `0`. Reading or writing outside `[0, size)` is a
runtime error. Arrays are not passed to functions in this version of
the language — keep them global or local to the function that uses
them.

## 3. Operators

| Category    | Operators |
|-------------|-----------|
| Arithmetic  | `+  -  *  /  %` |
| Unary       | `-` (negate), `!` (logical not), `++`, `--` (prefix and postfix) |
| Comparison  | `==  !=  <  <=  >  >=` |
| Logical     | `&&  \|\|` (short-circuit) |
| Assignment  | `=` |

Integer division truncates toward zero, like C++. Dividing by zero
(integer or float) is a runtime error. `%` requires integer operands.

## 4. Conditionals

```c
if (a > b) {
    // ...
} else if (a == b) {
    // ...
} else {
    // ...
}
```

`else if` chains are fully supported.

## 5. Loops

```c
while (condition) { ... }

do { ... } while (condition);   // body runs at least once

for (int i = 0; i < 5; i = i + 1) { ... }
```

`break` exits the nearest loop or `switch`; `continue` skips to the
next iteration of the nearest loop.

## 6. Functions

```c
int add(int x, int y) {
    return x + y;
}

void greet() {
    print("hello");
}
```

- A return type is required: one of `int`, `float`, `char`, `string`,
  `bool`, or `void`.
- Every parameter needs an explicit type.
- Non-`void` functions must return a value on every path that can be
  reached; `void` functions must not return a value.
- Functions may call themselves or each other (recursion is supported).
- Functions must be declared before they can be *parsed as part of a
  program*, but forward calls between two functions both defined in the
  file work fine, since the whole program is parsed before anything runs.

## 7. `print`

```c
print(expression, expression, ...);
```

`print` accepts one or more comma-separated expressions and writes
them to the output with no automatic separators — similar to chaining
`std::cout <<` in C++. Add spaces inside your string literals where
you want them:

```c
print("Sum = ", a + b);   // "Sum = 15"
```

Booleans print as `1` / `0`.

## 8. `switch` / `case`

```c
switch (option) {
    case 1:
        print("one");
        break;
    case 2:
        print("two");
        break;
    default:
        print("other");
}
```

Cases fall through if you omit `break`, exactly like C++.

## 9. Comments

```c
// a single-line comment
/* a
   multi-line comment */
```

## 10. A complete example

```c
int add(int x, int y) {
    return x + y;
}

int main() {
    int a = 5;
    int b = 10;
    bool flag = true;
    int arr[3];
    arr[0] = 1;
    arr[1] = 2;
    arr[2] = 3;

    int sum = add(a, b);
    print("sum = ", sum);

    if (a < b) {
        print("a is less than b");
    } else {
        print("a is greater or equal to b");
    }

    print(flag && (a < b));
    print(flag || (a > b));

    return sum;
}
```

See the `examples/` folder for more runnable programs.
