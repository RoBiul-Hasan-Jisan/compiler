# server.py
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from compiler import compile_and_run as original_compile_and_run  # your existing compiler function
import uvicorn
import os
import io
import sys

app = FastAPI()

# ---------------- Serve frontend ----------------
frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/", response_class=HTMLResponse)
def get_index():
    index_file = os.path.join(frontend_path, "index.html")
    with open(index_file, "r", encoding="utf-8") as f:
        return f.read()

# ---------------- Capture output ----------------
def compile_and_run_capture_output(source_code):
    """
    Runs the compiler and captures all print statements as a string.
    Ignores the return value of the program.
    """
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()
    try:
        _ = original_compile_and_run(source_code)  # ignore return value
        printed_output = buffer.getvalue()
        return printed_output  # only prints, no return value appended
    finally:
        sys.stdout = old_stdout

# ---------------- API to run code ----------------
class CodeRequest(BaseModel):
    code: str

@app.post("/run")
def run_code(req: CodeRequest):
    try:
        output = compile_and_run_capture_output(req.code)
        return JSONResponse(content={"output": output})
    except Exception as e:
        return JSONResponse(content={"error": str(e)})

# ---------------- Run the server ----------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
