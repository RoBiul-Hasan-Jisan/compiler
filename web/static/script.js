const sourceEl = document.getElementById("source");
const runBtn = document.getElementById("run");
const examplesSelect = document.getElementById("examples");

const stdoutView = document.getElementById("stdout-view");
const tokensView = document.getElementById("tokens-view");
const astView = document.getElementById("ast-view");
const views = { stdout: stdoutView, tokens: tokensView, ast: astView };

const tabs = document.querySelectorAll(".tab");

let currentTab = "stdout";

tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    tabs.forEach((t) => t.classList.remove("active"));
    tab.classList.add("active");
    Object.values(views).forEach((v) => v.classList.add("hidden"));
    currentTab = tab.dataset.tab;
    views[currentTab].classList.remove("hidden");
    if (currentTab !== "stdout") {
      inspect();
    }
  });
});

function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function statusLine(ok) {
  const dot = ok ? "ok" : "err";
  const label = ok ? "Program finished" : "Compilation failed";
  return `<div class="status-line"><span class="status-dot ${dot}"></span>${label}</div>`;
}

async function runProgram() {
  runBtn.disabled = true;
  runBtn.textContent = "Running…";
  stdoutView.innerHTML = "";

  try {
    const res = await fetch("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source: sourceEl.value }),
    });
    const data = await res.json();

    let html = statusLine(data.ok);
    if (data.output) {
      html += data.output
        .split("\n")
        .map((line) => `<div class="line">${escapeHtml(line)}</div>`)
        .join("");
    } else if (data.ok) {
      html += `<div class="empty">(no output)</div>`;
    }
    if (data.error) {
      html += `<div class="error-block">${escapeHtml(data.error)}</div>`;
    }
    if (data.ok && data.return_value !== undefined && data.return_value !== null) {
      html += `<div class="return-value">main() returned ${escapeHtml(String(data.return_value))}</div>`;
    }
    stdoutView.innerHTML = html;
  } catch (e) {
    stdoutView.innerHTML = `<div class="error-block">Network error: ${escapeHtml(String(e))}</div>`;
  } finally {
    runBtn.disabled = false;
    runBtn.textContent = "▶ Run";
  }
}

async function inspect() {
  if (currentTab === "tokens") {
    tokensView.innerHTML = "loading…";
  } else if (currentTab === "ast") {
    astView.innerHTML = "loading…";
  }

  try {
    const res = await fetch("/api/inspect", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source: sourceEl.value }),
    });
    const data = await res.json();

    if (!data.ok) {
      const msg = `<div class="error-block">${escapeHtml(data.error || "Could not parse program")}</div>`;
      tokensView.innerHTML = msg;
      astView.innerHTML = msg;
      return;
    }

    tokensView.innerHTML =
      "<table>" +
      data.tokens
        .map(
          (t) =>
            `<tr><td class="tok-type">${t.type}</td><td>${escapeHtml(t.value)}</td>` +
            `<td class="tok-pos">${t.line}:${t.col}</td></tr>`
        )
        .join("") +
      "</table>";

    astView.innerHTML = `<pre>${escapeHtml(data.ast)}</pre>`;
  } catch (e) {
    const msg = `<div class="error-block">Network error: ${escapeHtml(String(e))}</div>`;
    tokensView.innerHTML = msg;
    astView.innerHTML = msg;
  }
}

runBtn.addEventListener("click", runProgram);

sourceEl.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    e.preventDefault();
    runProgram();
  }
  // Basic tab-key support inside the editor
  if (e.key === "Tab") {
    e.preventDefault();
    const start = sourceEl.selectionStart;
    const end = sourceEl.selectionEnd;
    sourceEl.value = sourceEl.value.slice(0, start) + "    " + sourceEl.value.slice(end);
    sourceEl.selectionStart = sourceEl.selectionEnd = start + 4;
  }
});

examplesSelect.addEventListener("change", async () => {
  const name = examplesSelect.value;
  if (!name) return;
  const res = await fetch(`/examples/${name}`);
  if (res.ok) {
    sourceEl.value = await res.text();
  }
});
