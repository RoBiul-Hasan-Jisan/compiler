import os
import sys
import time

from flask import Flask, request, jsonify, render_template, abort, Response

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mcpp.lexer import Lexer
from mcpp.parser import parse
from mcpp.interpreter import Interpreter
from mcpp.errors import MCPPError

app = Flask(__name__)

EXAMPLES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "examples"))
EXAMPLE_FILES = sorted(f for f in os.listdir(EXAMPLES_DIR) if f.endswith(".mcpp")) if os.path.isdir(EXAMPLES_DIR) else []

DEFAULT_SOURCE = """int factorial(int n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

int main() {
    int a = 5;
    int b = 10;
    print("a + b = ", a + b);
    print("5! = ", factorial(5));

    for (int i = 0; i < 3; i++) {
        print("i = ", i);
    }

    return 0;
}
"""

MAX_SOURCE_LEN = 20_000
TIME_LIMIT_SECONDS = 5


@app.route("/")
def index():
    return render_template("index.html", default_source=DEFAULT_SOURCE, examples=EXAMPLE_FILES)


@app.route("/examples/<name>")
def get_example(name):
    if name not in EXAMPLE_FILES:
        abort(404)
    path = os.path.join(EXAMPLES_DIR, name)
    with open(path, "r", encoding="utf-8") as f:
        return Response(f.read(), mimetype="text/plain")


@app.route("/api/run", methods=["POST"])
def api_run():
    data = request.get_json(silent=True) or {}
    source = data.get("source", "")

    if len(source) > MAX_SOURCE_LEN:
        return jsonify(ok=False, error=f"Source too long (max {MAX_SOURCE_LEN} characters)."), 400

    lines = []
    started = time.monotonic()
    try:
        tokens = Lexer(source).tokenize()
        program = parse(tokens, source)

        def collect(text):
            if time.monotonic() - started > TIME_LIMIT_SECONDS:
                raise TimeoutError("Program exceeded the time limit")
            lines.append(text)

        result = Interpreter(output=collect).run(program)
        return jsonify(ok=True, output="\n".join(lines), return_value=result)

    except TimeoutError as e:
        return jsonify(ok=False, output="\n".join(lines), error=str(e))
    except MCPPError as e:
        return jsonify(ok=False, output="\n".join(lines), error=str(e))
    except RecursionError:
        return jsonify(ok=False, output="\n".join(lines), error="Stack overflow (infinite recursion?)")


@app.route("/api/inspect", methods=["POST"])
def api_inspect():
    """Return the token stream and a pretty-printed AST without running the program."""
    data = request.get_json(silent=True) or {}
    source = data.get("source", "")

    if len(source) > MAX_SOURCE_LEN:
        return jsonify(ok=False, error=f"Source too long (max {MAX_SOURCE_LEN} characters)."), 400

    try:
        tokens = Lexer(source).tokenize()
        token_list = [
            {"type": t.type.name, "value": "" if t.value is None else str(t.value), "line": t.line, "col": t.column}
            for t in tokens
        ]
        import pprint
        program = parse(tokens, source)
        ast_text = pprint.pformat(program, width=100)
        return jsonify(ok=True, tokens=token_list, ast=ast_text)
    except MCPPError as e:
        return jsonify(ok=False, error=str(e))


if __name__ == "__main__":
    app.run(debug=True)
