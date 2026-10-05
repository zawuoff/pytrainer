/* Step through: runs your code one line at a time (server side, under sys.settrace) and lets you
   walk the recorded steps back and forth. The line about to run is highlighted in the editor and
   every variable that changed since the previous step lights up. */
import { $, api, busy, cleanup, esc, toast } from "./core.js";

export function createDebugger({ cm, exerciseId, suggestion = "", predict = false, getFiles, getStdin }) {
  let trace = null, at = 0, stale = false, call = suggestion, host = null, marked = [];

  cm.on("change", () => {
    if (!trace || stale || predict) return;
    stale = true;
    clearMarks();
    if (host?.isConnected) draw();
  });

  function clearMarks() {
    marked.forEach(([line, cls]) => cm.removeLineClass(line, "background", cls));
    marked = [];
    $("#dbg-call")?.classList.remove("dbg-cur-input");
  }

  function mark(step, cls) {
    if (!step || step.file !== "main" || !step.line) return;
    const line = step.line - 1;
    if (line >= cm.lineCount()) return;
    cm.addLineClass(line, "background", cls);
    marked.push([line, cls]);
  }

  function showMarks() {
    clearMarks();
    if (!trace || stale || !trace.steps.length) return;
    const step = trace.steps[at];
    // The line that ran just before this one, so you can see where the jump came from.
    const prev = trace.steps.slice(0, at).reverse().find((s) => s.event === "line" && s.file === "main");
    if (prev && !(prev.line === step.line && step.file === "main")) mark(prev, "dbg-prev");
    mark(step, "dbg-cur");
    if (step.file === "call") $("#dbg-call")?.classList.add("dbg-cur-input");
    if (step.file === "main" && step.line) cm.scrollIntoView({ line: step.line - 1, ch: 0 }, 60);
  }

  async function start() {
    const btn = $("#dbg-start");
    if (btn) busy(btn, true, "Running");
    try {
      const body = predict ? {} : { files: getFiles(), call, stdin: getStdin() };
      trace = await api(`exercise/${exerciseId}/trace`, body);
      at = 0; stale = false;
    } catch (err) { toast(err.message, true); }
    if (host?.isConnected) draw();
  }

  function go(i) {
    if (!trace?.steps.length) return;
    at = Math.max(0, Math.min(trace.steps.length - 1, i));
    drawStep();
  }

  function describe(step) {
    const where = step.file === "call" ? "your call" : `line ${step.line}`;
    if (step.event === "line") return step.file === "call" ? "Your call runs next." : `Line ${step.line} runs next.`;
    if (step.event === "call") {
      const args = (step.stack.at(-1)?.vars || []).map(([n, , v]) => `${n}=${v}`).join(", ");
      return `Calling ${step.func}(${args}).`;
    }
    if (step.event === "return") {
      if (step.func === "<module>") return step.file === "call" ? "Your call finished." : "Your file finished running.";
      return `${step.func}() returns ${step.value} (${where}).`;
    }
    if (step.event === "exception") return `${step.value} (${where}).`;
    return "";
  }

  function changed(step, prevStep) {
    // Names that are new or different since the previous step, per frame (matched by position and name).
    const out = new Set();
    if (!prevStep) return out;
    step.stack.forEach((fr, fi) => {
      const before = prevStep.stack[fi];
      const old = before && before.name === fr.name ? new Map(before.vars.map(([n, , v]) => [n, v])) : new Map();
      fr.vars.forEach(([n, , v]) => { if (old.get(n) !== v) out.add(fi + ":" + n); });
    });
    return out;
  }

  function framesHTML(step) {
    const diff = changed(step, trace.steps[at - 1]);
    if (!step.stack.length) return `<p class="faint small">No variables yet.</p>`;
    return step.stack.map((fr, fi) => `<div class="dbg-frame${fi === step.stack.length - 1 ? " top" : ""}">
      <div class="dbg-fname">${esc(fr.name)}${fr.file === "call" && fr.name === "Global" ? ` <span class="faint">· running your call</span>` : ""}</div>
      ${fr.vars.length ? `<table>${fr.vars.map(([n, type, v]) => `<tr class="${diff.has(fi + ":" + n) ? "chg" : ""}">
        <th>${esc(n)}</th><td><code>${esc(v)}</code></td><td class="ty">${esc(type)}</td></tr>`).join("")}</table>`
        : `<p class="faint small">no variables</p>`}</div>`).join("");
  }

  function drawStep() {
    const body = $("#dbg-step", host);
    if (!body || !trace) return;
    const steps = trace.steps, step = steps[at], n = steps.length;
    $("#dbg-pos", host).textContent = `Step ${at + 1} of ${n}${trace.truncated ? "+" : ""}`;
    $("#dbg-range", host).value = String(at);
    $("#dbg-first", host).disabled = $("#dbg-back", host).disabled = at === 0;
    $("#dbg-next", host).disabled = $("#dbg-last", host).disabled = at === n - 1;
    const last = at === n - 1;
    const printed = trace.stdout.slice(0, step.out);
    body.innerHTML = `<div class="dbg-event ev-${step.event}">${esc(describe(step))}</div>
      <div class="dbg-grid">
        <div class="dbg-frames"><h4>Variables</h4>${framesHTML(step)}</div>
        <div class="dbg-out"><h4>Printed so far</h4><pre>${printed ? esc(printed) : `<span class="faint">(nothing yet)</span>`}</pre></div>
      </div>
      ${last && trace.result != null ? `<div class="good small">Your call returned <code>${esc(trace.result)}</code>.</div>` : ""}
      ${last && trace.error ? `<div class="errbox">${esc(trace.error)}</div>` : ""}
      ${last && trace.truncated ? `<div class="note small">Stopped after ${trace.steps.length} steps. Very long loops are cut short so the page stays fast. Try a smaller input in the call box.</div>` : ""}`;
    showMarks();
  }

  function draw() {
    const callRow = predict ? "" : `<div class="dbg-callrow">
        <label for="dbg-call">Then call</label>
        <input id="dbg-call" type="text" spellcheck="false" placeholder="optional, e.g. my_function(1, 2)" value="${esc(call)}">
        <button class="btn small primary" id="dbg-start" type="button">${trace ? "Restart" : "Start"}</button></div>
        <p class="faint small dbg-help">Your file runs first. If it only defines functions, put a call here to step into one.${suggestion ? " This one comes from the checks." : ""}</p>`;
    let h = `<div class="dbg">${predict ? `<div class="row"><button class="btn small primary" id="dbg-start" type="button">${trace ? "Restart" : "Start"}</button></div>` : callRow}`;
    if (!trace) {
      h += `<p class="dim">Press <b>Start</b> to run your code one line at a time. You can step forwards and backwards, watch each variable change, and see what was printed at every point. <span class="faint">Shortcut: Alt+D. While stepping, ← and → move between steps.</span></p>`;
    } else if (!trace.steps.length) {
      h += `<div class="errbox">${esc(trace.error || "Nothing ran. Is the file empty?")}</div>`;
    } else {
      h += `${stale ? `<div class="note small">Your code changed since you started. Press Restart to step through the new version.</div>` : ""}
        <div class="dbg-controls" role="group" aria-label="Step controls">
          <button class="btn small ghost" id="dbg-first" type="button" title="First step" aria-label="First step">⏮</button>
          <button class="btn small" id="dbg-back" type="button" title="Back (←)">◀ Back</button>
          <button class="btn small" id="dbg-next" type="button" title="Next (→)">Next ▶</button>
          <button class="btn small ghost" id="dbg-last" type="button" title="Last step" aria-label="Last step">⏭</button>
          <input type="range" id="dbg-range" min="0" max="${trace.steps.length - 1}" value="${at}" aria-label="Step">
          <span class="dbg-pos" id="dbg-pos"></span>
        </div>
        <div id="dbg-step"></div>`;
    }
    host.innerHTML = h + "</div>";
    $("#dbg-start", host).onclick = start;
    const input = $("#dbg-call", host);
    if (input) {
      input.oninput = () => { call = input.value; };
      input.onkeydown = (e) => { if (e.key === "Enter") { e.preventDefault(); start(); } };
    }
    if (trace?.steps.length) {
      $("#dbg-first", host).onclick = () => go(0);
      $("#dbg-back", host).onclick = () => go(at - 1);
      $("#dbg-next", host).onclick = () => go(at + 1);
      $("#dbg-last", host).onclick = () => go(trace.steps.length - 1);
      $("#dbg-range", host).oninput = (e) => go(+e.target.value);
      drawStep();
    }
  }

  const keys = (e) => {
    if (!host?.isConnected || !trace?.steps.length || e.altKey || e.ctrlKey || e.metaKey) return;
    const el = document.activeElement;
    if (el && (el.closest(".CodeMirror") || ["INPUT", "TEXTAREA", "SELECT"].includes(el.tagName) && el.type !== "range")) return;
    if (e.key === "ArrowRight") { e.preventDefault(); go(at + 1); }
    else if (e.key === "ArrowLeft") { e.preventDefault(); go(at - 1); }
  };
  document.addEventListener("keydown", keys);
  cleanup.push(() => { document.removeEventListener("keydown", keys); clearMarks(); });

  return {
    render(el) { host = el; draw(); },
    hide() { clearMarks(); host = null; },
    start,
    get running() { return !!trace; },
  };
}
