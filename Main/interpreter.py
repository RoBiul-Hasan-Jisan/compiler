import re

variables = {}

def evaluate_expression(expr):
    expr = expr.strip()
    for var in variables:
        expr = re.sub(rf'\b{var}\b', str(variables[var]), expr)
    try:
        return eval(expr, {"__builtins__": None}, {})
    except Exception:
        return expr

def eval_bool(expr):
    val = evaluate_expression(expr)
    try:
        return bool(val)
    except Exception:
        return False

def extract_block(lines, start_index):
    block_lines = []
    brace_count = 0
    i = start_index

    # Handle brace on the same line if exists
    if i < len(lines):
        line = lines[i]
        brace_count += line.count("{")
        brace_count -= line.count("}")
        # If there is text after the first '{' on the same line, extract that as first block line
        if "{" in line:
            after_brace = line.split("{", 1)[1]
            if after_brace.strip():
                block_lines.append(after_brace.strip())
        i += 1

    # Continue collecting until braces balanced
    while i < len(lines) and brace_count > 0:
        line = lines[i]
        brace_count += line.count("{")
        brace_count -= line.count("}")
        if brace_count > 0:
            block_lines.append(line)
        i += 1

    return block_lines, i

def execute_block(block, output_callback):
    lines = [line.strip().rstrip(';') for line in block.splitlines() if line.strip()]
    i = 0

    while i < len(lines):
        line = lines[i]

        # Assignment without 'daro'
        match = re.match(r"(\w+)\s*=\s*(.+)", line)
        if match and not line.startswith("daro "):
            var, val = match.groups()
            variables[var] = evaluate_expression(val)
            i += 1
            continue

        # Variable assignment with 'daro'
        if line.startswith("daro "):
            match = re.match(r"daro\s+(\w+)\s*=\s*(.+)", line)
            if match:
                var, val = match.groups()
                variables[var] = evaluate_expression(val)
            i += 1
            continue

        # Output statement
        elif line.startswith("deko "):
            match = re.match(r"deko\s+(.+)", line)
            if match:
                expr = match.group(1)
                output_callback(str(evaluate_expression(expr)))
            i += 1
            continue

        # If-else
        elif line.startswith("jodi "):
            match = re.match(r"jodi\s+(.+)", line)
            if not match:
                i += 1
                continue
            condition = match.group(1)
            i += 1
            if_body, i = extract_block(lines, i)
            else_body = []
            if i < len(lines) and lines[i].startswith("kinto"):
                i += 1
                else_body, i = extract_block(lines, i)
            if eval_bool(condition):
                execute_block("\n".join(if_body), output_callback)
            else:
                execute_block("\n".join(else_body), output_callback)
            continue

        # For loop
        elif line.startswith("loop "):
            match = re.match(r"loop\s+(\w+)\s+from\s+(.+?)\s+to\s+(.+?)(?:\s*\{)?$", line)
            if match:
                var, start_expr, end_expr = match.groups()
                start_val = int(evaluate_expression(start_expr))
                end_val = int(evaluate_expression(end_expr))
                i += 1
                loop_body, i = extract_block(lines, i-1)  # Pass i-1 to include brace on same line
                for j in range(start_val, end_val):
                    variables[var] = j
                    execute_block("\n".join(loop_body), output_callback)
            else:
                output_callback("Syntax error in loop")
            continue

        # While loop
        elif line.startswith("jakon "):
            match = re.match(r"jakon\s+(.+?)(\s*\{)?$", line)
            if match:
                condition = match.group(1).strip()
                has_brace = bool(match.group(2))
                i += 1
                if has_brace:
                    body, i = extract_block(lines, i-1)
                else:
                    if i < len(lines) and lines[i].startswith("{"):
                        body, i = extract_block(lines, i)
                    else:
                        body = []

                max_iterations = 10000
                counter = 0
                while eval_bool(condition):
                    if counter > max_iterations:
                        output_callback("[ERROR] Max iterations reached (possible infinite loop).")
                        break
                    execute_block("\n".join(body), output_callback)
                    counter += 1
            continue

        # Do-while loop
        elif line.startswith("gurer somoi"):
            i += 1
            body, i = extract_block(lines, i-1)
            if i < len(lines) and lines[i].startswith("jotokkhon "):
                cond_match = re.match(r"jotokkhon\s+(.+)", lines[i])
                if cond_match:
                    condition = cond_match.group(1)
                    max_iterations = 10000
                    counter = 0
                    while True:
                        if counter > max_iterations:
                            output_callback("[ERROR] Max iterations reached (possible infinite loop).")
                            break
                        execute_block("\n".join(body), output_callback)
                        if not eval_bool(condition):
                            break
                        counter += 1
                i += 1
            continue

        # Unknown or empty line
        i += 1


# Example usage:

if __name__ == "__main__":
    code = """
    daro i = 0;
    loop i from 0 to 5 {
        deko i;
    }

    daro j = 0;
    jakon j < 3 {
        deko j;
        j = j + 1;
    }

    daro k = 0;
    gurer somoi {
        deko k;
        k = k + 1;
    } jotokkhon k < 3;
    """

    def output(text):
        print(text)

    execute_block(code, output)
