import { $, $$, cleanup, esc, lastInteraction, md } from "./core.js";
import { EDITOR_OPTS } from "./shared.js";
import { attachAssist } from "./assist.js";
import { tabIndicator } from "./library.js";

export function makeEditor(host, files, onChange, { focus = true } = {}) {
  const docs = {};
  Object.entries(files).forEach(([name, code]) => { docs[name] = CodeMirror.Doc(code, "python"); });
  let active = Object.keys(files)[0];
  const cm = CodeMirror(host, { ...EDITOR_OPTS });
  cm.swapDoc(docs[active]);
  cm.on("change", () => onChange && onChange());
  setTimeout(() => { cm.refresh(); if (focus) cm.focus(); }, 30);
  let sizeT = null;
  const ro = new ResizeObserver(() => { clearTimeout(sizeT); sizeT = setTimeout(() => cm.refresh(), 60); });
  ro.observe(host);
  const detach = attachAssist(cm, () => /\.py$/.test(active));
  cleanup.push(() => { ro.disconnect(); clearTimeout(sizeT); detach(); });
  return {
    cm,
    get active() { return active; },
    names: () => Object.keys(docs),
    show(name) { active = name; cm.swapDoc(docs[name]); cm.focus(); },
    files() { const o = {}; for (const [n, d] of Object.entries(docs)) o[n] = d.getValue(); return o; },
    set(filesIn) {
      for (const [n, code] of Object.entries(filesIn)) { if (docs[n]) docs[n].setValue(code); else docs[n] = CodeMirror.Doc(code, "python"); }
      cm.swapDoc(docs[active] || docs[Object.keys(docs)[0]]);
    },
  };
}

export function startTimer(el) {
  let secs = 0;
  const id = setInterval(() => {
    if (document.visibilityState === "visible" && Date.now() - lastInteraction < 120000) secs++;
    if (el) el.textContent = `${Math.floor(secs / 60)}:${String(secs % 60).padStart(2, "0")}`;
  }, 1000);
  cleanup.push(() => clearInterval(id));
  return { get secs() { return secs; } };
}

/* The output dock under the editor can be dragged taller or shorter. */
export function makeDock(dock) {
  const grip = $(".dock-grip", dock), col = dock.parentElement;
  if (!grip) return;
  grip.onpointerdown = (e) => {
    e.preventDefault();
    grip.setPointerCapture(e.pointerId);
    grip.classList.add("drag");
    const rect = col.getBoundingClientRect();
    grip.onpointermove = (ev) => col.style.setProperty("--dock", Math.min(80, Math.max(15, ((rect.bottom - ev.clientY) / rect.height) * 100)) + "%");
    grip.onpointerup = grip.onpointercancel = () => { grip.onpointermove = null; grip.classList.remove("drag"); };
  };
}

/* Phones: show the lesson or the code, switched from the top bar. */
export const isNarrow = () => matchMedia("(max-width: 960px)").matches;
export function paneSwitch(ws, cm, labels = ["Lesson", "Code"]) {
  const top = $(".ws-top", ws);
  const sw = document.createElement("div");
  sw.className = "pane-switch";
  sw.innerHTML = `<button data-p="read" class="on">${labels[0]}</button><button data-p="code">${labels[1]}</button>`;
  const back = $(".ttl", top);
  back.after(sw);
  ws.dataset.pane = "read";
  const set = (p) => {
    ws.dataset.pane = p;
    $$("button", sw).forEach((b) => b.classList.toggle("on", b.dataset.p === p));
    if (p === "code" && cm) setTimeout(() => { cm.refresh(); $$(".dock-tabs.has-ind", ws).forEach(tabIndicator); }, 20);
  };
  $$("button", sw).forEach((b) => b.onclick = () => set(b.dataset.p));
  return set;
}

export const burst = () => `<span class="burst">${Array.from({ length: 12 }, (_, i) =>
  `<i style="--r:${i * 30}deg;background:${["var(--amber)", "var(--pass)", "var(--text)"][i % 3]};animation-delay:${(i % 3) * 40}ms"></i>`).join("")}</span>`;
export function resultsHTML(r, extra = "") {
  if (!r) return `<p class="dim">Press <b>Check</b> (Ctrl+Enter) when you're ready. Each check shows exactly what passed and what didn't.</p>`;
  const ok = r.status === "passed";
  const unit = r.tests[0]?.name?.startsWith("line ") ? "lines right" : "checks";
  const fresh = r._fresh; r._fresh = false;
  let html = `<div class="results ${fresh ? "fresh" : ""}"><div class="sum ${ok ? "pass" : "fail"}"><b>${ok ? "Correct" : r.status === "timeout" ? "Timed out" : r.status === "error" ? "Your code didn't run" : "Not yet"}</b>
    <span class="dim">${r.passed}/${r.total} ${unit}</span></div>`;
  if (r.error) html += `<div class="errbox">${esc(r.error)}</div>`;
  html += r.tests.map((t, i) => `<div class="test ${t.passed ? "ok" : "no"}" style="--i:${i}"><span class="ic">${t.passed ? "✓" : "✕"}</span>
      <div>${esc(t.name)}${t.message ? `<pre>${esc(t.message)}</pre>` : ""}</div></div>`).join("");
  html += budgetsHTML(r.budgets);
  if (r.stdout && r.stdout.trim()) html += `<h3 style="margin:16px 0 6px">Printed while checking</h3><pre class="outbox">${esc(r.stdout)}</pre>`;
  return html + extra + "</div>";
}

/* Budget checks (time, cost, calls) measured by the hidden tests, as "used of limit" bars. */
export function budgetsHTML(budgets) {
  if (!budgets?.length) return "";
  return `<h3 style="margin:16px 0 6px">Budgets</h3><div class="budgets">${budgets.map((b) => `<div class="budget ${b.ok ? "ok" : "over"}">
    <span>${esc(b.label)}</span><span class="budget-bar"><i style="width:${Math.min(100, b.limit ? (b.used / b.limit) * 100 : 100)}%"></i></span>
    <span class="budget-val">${esc(b.used)} of ${esc(b.limit)} ${esc(b.unit)}</span></div>`).join("")}</div>`;
}

export const chatHTML = (chat, empty) => !chat.length ? `<p class="dim">${empty}</p>` :
  `<div class="chat">${chat.map((m) => `<div class="msg ${m.role}"><div class="who">${m.role === "tutor" ? "Tutor" : "You"}</div>${m.role === "tutor" ? md(m.content) : esc(m.content).replace(/\n/g, "<br>")}</div>`).join("")}</div>`;

export const QUALITY_NAMES = { readability: "Readability", naming: "Naming", idiomatic: "Pythonic", simplicity: "Simplicity", robustness: "Edge cases" };
export function qualityHTML(q) {
  if (!q) return "";
  return `<div class="review"><div class="row" style="gap:14px;align-items:baseline"><div class="score">${q.overall}<small>/10</small></div><span class="dim small">code quality, scored by Jev</span></div>
    <div style="margin-top:10px">${Object.entries(q.dims).map(([k, v]) => `<div class="qrow"><span>${esc(QUALITY_NAMES[k] || k)}</span>
      <div class="bar" style="--mc:${v.score >= 7 ? "var(--pass)" : v.score >= 4 ? "var(--amber)" : "var(--fail)"}"><i style="width:${v.score * 10}%"></i></div><span class="faint">${v.score}</span></div>`).join("")}</div></div>`;
}

export function reviewHTML(rv) {
  if (!rv) return "";
  return `<div class="review stack">
    <div class="row" style="gap:16px;align-items:baseline"><div class="score">${esc(rv.score)}<small>/10</small></div><div>${esc(rv.summary || "")}</div></div>
    ${rv.strengths?.length ? `<div><h3>Strengths</h3><ul>${rv.strengths.map((s) => `<li>${esc(s)}</li>`).join("")}</ul></div>` : ""}
    ${rv.issues?.length ? `<div><h3>Issues</h3><ul>${rv.issues.map((i) => `<li><span class="sev-${esc(i.severity)}">${esc(i.severity)}</span>${i.line ? ` · line ${esc(i.line)}` : ""}: ${esc(i.comment)}</li>`).join("")}</ul></div>` : ""}
    ${rv.idioms?.length ? `<div><h3>Worth learning</h3><ul>${rv.idioms.map((s) => `<li>${md(s)}</li>`).join("")}</ul></div>` : ""}
    ${rv.interview_note ? `<div class="note">${esc(rv.interview_note)}</div>` : ""}</div>`;
}

export const checksHTML = (checks) => !checks?.length ? "" :
  `<div style="margin-top:16px"><h3 class="small dim" style="margin-bottom:2px">What gets checked</h3>
   <ul class="check-list">${checks.map((c) => `<li><span class="pending">○</span><div>${esc(c)}</div></li>`).join("")}</ul></div>`;

export function researchHTML(r) {
  if (!r) return "";
  return `<div class="research"><b>${r.links?.length ? "Read first" : "Look it up"}</b><div>${md(r.note)}</div>
    ${r.links?.length ? `<ul>${r.links.map((l) => `<li><a href="${esc(l.url)}" target="_blank" rel="noopener">${esc(l.title)}</a></li>`).join("")}</ul>` : ""}</div>`;
}
