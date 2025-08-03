import tkinter as tk
from tkinter import scrolledtext
import re

variables = {}

def evaluate_expression(expr):
    expr = expr.strip()
    for var in variables:
        expr = re.sub(rf'\b{var}\b', variables[var], expr)
    try:
        return str(eval(expr))
    except:
        return expr

def execute_block(block, output_widget):
    block = block.replace(";", ";\n")  # ensure each line ends properly
    lines = [line.strip() for line in block.splitlines() if line.strip()]
    
    i = 0
    while i < len(lines):
        line = lines[i]

        # Variable declaration
        if line.startswith("daro "):
            match = re.match(r"daro\s+(\w+)\s*=\s*(.+);", line)
            if match:
                var, val = match.groups()
                variables[var] = evaluate_expression(val.strip())

        # Print
        elif line.startswith("deko "):
            match = re.match(r"deko\s+(.+);", line)
            if match:
                msg = match.group(1)
                output_widget.insert(tk.END, evaluate_expression(msg) + "\n")

        # If condition
        elif line.startswith("jodi "):
            match = re.match(r"jodi\s+(.+?)\s*{", line)
            if match:
                condition = match.group(1)
                if_body = ""
                i += 1
                while i < len(lines) and not lines[i].startswith("}"):
                    if_body += lines[i] + "\n"
                    i += 1
                # skip `}`
                i += 1

                # Check for optional 'kinto'
                else_body = ""
                if i < len(lines) and lines[i].startswith("kinto"):
                    i += 1
                    if lines[i].startswith("{"):
                        i += 1
                    while i < len(lines) and not lines[i].startswith("}"):
                        else_body += lines[i] + "\n"
                        i += 1
                    i += 1

                if evaluate_expression(condition) == "True":
                    execute_block(if_body, output_widget)
                else:
                    execute_block(else_body, output_widget)
                continue  # skip normal i++

        i += 1

def run_code(input_widget, output_widget):
    global variables
    variables = {}
    output_widget.delete(1.0, tk.END)
    code = input_widget.get(1.0, tk.END).strip()
    if code.startswith("{") and code.endswith("}"):
        body = code[1:-1].strip()
        execute_block(body, output_widget)
    else:
        execute_block(code, output_widget)

def create_gui():
    window = tk.Tk()
    window.title("Natural Language Toy Compiler")

    # Input area
    tk.Label(window, text="Write your code:").pack()
    input_box = scrolledtext.ScrolledText(window, height=15, width=70)
    input_box.pack()

    # Output area
    tk.Label(window, text="Output:").pack()
    output_box = scrolledtext.ScrolledText(window, height=10, width=70, bg="black", fg="white")
    output_box.pack()

    # Run button
    run_button = tk.Button(window, text="Run", command=lambda: run_code(input_box, output_box))
    run_button.pack(pady=10)

    window.mainloop()

if __name__ == "__main__":
    create_gui()
