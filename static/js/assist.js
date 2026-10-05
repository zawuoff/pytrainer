/* Editor help for CodeMirror: inline errors (a syntax error, or a name that's never defined) and an
   autocomplete popup. Both come from the server (pytrainer/assist.py: the standard library, or Jedi
   when it's installed). Ctrl+Space opens completions; typing a "." or a couple of letters does too. */
import { S, api, esc } from "./core.js";

const KIND = { function: "fn", class: "cls", module: "mod", keyword: "kw", value: "var", instance: "var", statement: "var", param: "arg", property: "prop", path: "path" };

export function attachAssist(cm, isPython = () => true) {
  if (!S?.settings?.editor_assist) return () => {};
  let diagTimer = null, diagSeq = 0, marks = [], widgets = [];
  let popup = null, items = [], sel = 0, from = null, compSeq = 0, compTimer = null;

  /* ------------------------------------------------------------ inline errors */
  const clearDiag = () => { marks.forEach((m) => m.clear()); widgets.forEach((w) => w.clear()); marks = []; widgets = []; };
  async function diagnose() {
    const seq = ++diagSeq, doc = cm.getDoc();
    if (!isPython()) { clearDiag(); return; }
    const code = cm.getValue();
    if (code.length > 100000) return;
    let r;
    try { r = await api("assist/diagnose", { code }); } catch { return; }
    if (seq !== diagSeq || cm.getDoc() !== doc) return;
    clearDiag();
    for (const p of r.problems) {
      const line = p.line - 1;
      if (line >= cm.lineCount()) continue;
      const len = cm.getLine(line).length;
      const a = { line, ch: Math.min(p.col, len) }, b = { line, ch: Math.min(Math.max(p.end_col, p.col + 1), Math.max(len, p.col + 1)) };
      if (a.ch === b.ch && len) a.ch = Math.max(0, b.ch - 1);
      marks.push(cm.markText(a, b, { className: p.severity === "error" ? "cm-diag-error" : "cm-diag-warn", attributes: { title: p.message } }));
      if (p.severity === "error") {
        const el = document.createElement("div");
        el.className = "cm-diag-msg";
        el.textContent = p.message;
        widgets.push(cm.addLineWidget(line, el, { coverGutter: false, noHScroll: true }));
      }
    }
  }
  const scheduleDiag = () => { clearTimeout(diagTimer); diagTimer = setTimeout(diagnose, 700); };

  /* ------------------------------------------------------------ completions */
  function close() {
    if (!popup) return;
    popup.remove(); popup = null; items = []; from = null;
    cm.removeKeyMap(keys);
  }
  function accept(i = sel) {
    const it = items[i];
    if (!it || !from) return close();
    cm.replaceRange(it.text, from, cm.getCursor(), "+complete");
    close();
  }
  const typedSoFar = () => (from ? cm.getRange(from, cm.getCursor()) : "");
  function move(d) {
    if (!items.length) return;
    sel = (sel + d + items.length) % items.length;
    draw();
  }
  const keys = {
    Up: () => move(-1), Down: () => move(1), PageUp: () => move(-8), PageDown: () => move(8),
    // Enter on a word that's already typed in full is a newline, not a completion.
    Enter: () => { if (typedSoFar() === items[sel]?.text) { close(); return CodeMirror.Pass; } accept(); },
    Tab: () => accept(), Esc: () => close(),
  };
  function draw() {
    if (!popup) {
      popup = document.createElement("ul");
      popup.className = "cm-hints";
      popup.setAttribute("role", "listbox");
      popup.addEventListener("mousedown", (e) => {
        const li = e.target.closest("li");
        if (li) { e.preventDefault(); accept(+li.dataset.i); }
      });
      document.body.appendChild(popup);
      cm.addKeyMap(keys);
    }
    popup.innerHTML = items.map((it, i) => `<li role="option" data-i="${i}" class="${i === sel ? "on" : ""}" aria-selected="${i === sel}">
      <span class="k k-${esc(KIND[it.kind] || "var")}">${esc(KIND[it.kind] || it.kind || "")}</span><b>${esc(it.text)}</b>${it.detail ? `<small>${esc(it.detail)}</small>` : ""}</li>`).join("");
    const pos = cm.cursorCoords(from || cm.getCursor(), "window");
    const below = innerHeight - pos.bottom > 220;
    popup.style.left = `${Math.max(8, Math.min(pos.left, innerWidth - 340))}px`;
    popup.style.top = below ? `${pos.bottom + 2}px` : "";
    popup.style.bottom = below ? "" : `${innerHeight - pos.top + 2}px`;
    popup.querySelector("li.on")?.scrollIntoView({ block: "nearest" });
  }
  async function complete(manual = false) {
    if (!isPython()) return;
    const seq = ++compSeq, cur = cm.getCursor();
    let r;
    try { r = await api("assist/complete", { code: cm.getValue(), line: cur.line + 1, ch: cur.ch }); } catch { return; }
    const now = cm.getCursor();
    if (seq !== compSeq) return;
    // The learner may have kept typing letters while we waited: keep the answer and narrow it.
    const ahead = now.line === cur.line && now.ch >= cur.ch && /^\w*$/.test(cm.getRange(cur, now));
    if (!ahead) return;
    if (!r.items.length) { close(); return; }
    // One exact match the learner already typed in full isn't worth a popup.
    if (!manual && r.items.length === 1 && r.items[0].text === r.prefix) { close(); return; }
    items = r.items; sel = 0;
    from = { line: cur.line, ch: cur.ch - r.prefix.length };
    if (now.ch > cur.ch) { if (!popup) draw(); refilter(); } else draw();
  }
  /* Narrow the open list as the learner keeps typing, without another round trip. */
  function refilter() {
    const cur = cm.getCursor();
    if (!popup || !from || cur.line !== from.line || cur.ch < from.ch) return close();
    const typed = cm.getRange(from, cur);
    if (!/^\w*$/.test(typed)) return close();
    const left = items.filter((it) => it.text.toLowerCase().startsWith(typed.toLowerCase()));
    if (!left.length || (left.length === 1 && left[0].text === typed)) return close();
    if (left.length !== items.length) { items = left; sel = 0; }
    draw();
  }

  const schedule = (ms) => { clearTimeout(compTimer); compTimer = setTimeout(() => complete(), ms); };
  const onInput = (_cm, change) => {
    if (change.origin === "+complete" || change.origin === "setValue") return;
    const text = change.text.join("\n");
    if (popup) {
      if (/^\w+$/.test(text)) refilter(); else close();
      return;
    }
    const cur = cm.getCursor(), before = cm.getLine(cur.line).slice(0, cur.ch);
    if (inStringOrComment(cur)) return;
    if (text === "." && /[\w)\]]\.$/.test(before) && !/(^|[^\w])\d+\.$/.test(before)) schedule(80);
    else if (/^\w$/.test(text) && /[A-Za-z_\])]\.\w+$/.test(before)) schedule(120);  // still typing after a dot
    else if (/^\w$/.test(text) && /(^|[^\w.])[A-Za-z_]\w$/.test(before)) schedule(200);  // two letters of a name
  };
  const inStringOrComment = (cur) => /string|comment/.test(cm.getTokenTypeAt(cur) || "");
  const onKey = (_cm, e) => { if ((e.ctrlKey || e.metaKey) && e.code === "Space") { e.preventDefault(); complete(true); } };
  const onCursor = () => { if (popup) { const c = cm.getCursor(); if (!from || c.line !== from.line || c.ch < from.ch) close(); } };

  cm.on("change", scheduleDiag);
  cm.on("inputRead", onInput);
  cm.on("keydown", onKey);
  cm.on("cursorActivity", onCursor);
  cm.on("blur", close);
  cm.on("swapDoc", () => { close(); clearDiag(); scheduleDiag(); });
  scheduleDiag();
  return () => {
    clearTimeout(diagTimer); clearTimeout(compTimer); close(); clearDiag();
    cm.off("change", scheduleDiag); cm.off("inputRead", onInput); cm.off("keydown", onKey);
    cm.off("cursorActivity", onCursor); cm.off("blur", close);
  };
}
