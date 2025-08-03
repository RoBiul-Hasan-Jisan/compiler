import tkinter as tk
from tkinter import scrolledtext
from interpreter import execute_block, variables

def run_code(input_widget, output_widget):
    global variables
    variables = {}
    output_widget.delete(1.0, tk.END)
    code = input_widget.get(1.0, tk.END).strip()
    if code.startswith("{") and code.endswith("}"):
        body = code[1:-1].strip()
        execute_block(body, lambda s: output_widget.insert(tk.END, str(s) + "\n"))
    else:
        execute_block(code, lambda s: output_widget.insert(tk.END, str(s) + "\n"))

def create_gui():
    window = tk.Tk()
    window.title("Natural Language  Compiler")

    tk.Label(window, text="Write your code:").pack()
    input_box = scrolledtext.ScrolledText(window, height=15, width=70)
    input_box.pack()

    tk.Label(window, text="Output:").pack()
    output_box = scrolledtext.ScrolledText(window, height=10, width=70, bg="black", fg="white")
    output_box.pack()

    run_button = tk.Button(window, text="Run", command=lambda: run_code(input_box, output_box))
    run_button.pack(pady=10)

    window.mainloop()
