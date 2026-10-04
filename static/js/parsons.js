/* Parsons board: build a function from shuffled lines. The pool holds the unused tiles; "Your code"
   is the ordered list with an indent level per line. Every change is turned into code and handed to
   onChange, so Run, Check and Debug work on the arrangement like on typed code. */
import { esc } from "./core.js";

const INDENT = "    ";
const MAX_INDENT = 5;

export function mountParsons(host, { tiles, code = "", onChange }) {
  const all = tiles.map((text, id) => ({ id, text }));
  let placed = restore(code);
  let focusAfter = null;

  function restore(text) {
    const free = [...all];
    const out = [];
    for (const line of (text || "").split("\n")) {
      if (!line.trim()) continue;
      const k = free.findIndex((t) => t.text === line.trim());
      if (k < 0) continue;
      out.push({ id: free[k].id, indent: Math.min(MAX_INDENT, Math.floor((line.length - line.trimStart().length) / 4)) });
      free.splice(k, 1);
    }
    return out;
  }

  const toCode = () => placed.length ? placed.map((p) => INDENT.repeat(p.indent) + all[p.id].text).join("\n") + "\n" : "";

  function changed(focus) {
    focusAfter = focus;
    draw();
    onChange(toCode());
  }

  function act(i, what) {
    const p = placed[i];
    if (!p) return;
    if (what === "in") p.indent = Math.min(MAX_INDENT, p.indent + 1);
    else if (what === "out") p.indent = Math.max(0, p.indent - 1);
    else if (what === "up" && i > 0) { [placed[i - 1], placed[i]] = [placed[i], placed[i - 1]]; i -= 1; }
    else if (what === "down" && i < placed.length - 1) { [placed[i + 1], placed[i]] = [placed[i], placed[i + 1]]; i += 1; }
    else if (what === "rm") { placed.splice(i, 1); i = Math.min(i, placed.length - 1); }
    changed(i >= 0 ? { row: i } : null);
  }

  function add(id, at = placed.length) {
    const prev = placed[at - 1];
    placed.splice(at, 0, { id, indent: prev ? prev.indent : 0 });
    changed({ row: at });
  }

  function draw() {
    const used = new Set(placed.map((p) => p.id));
    const pool = all.filter((t) => !used.has(t.id));
    host.innerHTML = `<div class="pz">
      <section class="pz-col"><h4>Lines <span class="faint">click or drag to add</span></h4>
        <ul class="pz-pool" data-zone="pool">${pool.map((t) => `<li><button type="button" class="pz-tile" draggable="true" data-add="${t.id}"><code>${esc(t.text)}</code></button></li>`).join("")
          || `<li class="faint small pz-empty">All lines used.</li>`}</ul></section>
      <section class="pz-col"><h4>Your code</h4>
        <ol class="pz-sol" data-zone="sol">${placed.map((p, i) => `<li class="pz-row" tabindex="0" draggable="true" data-i="${i}" style="--ind:${p.indent}">
          <code>${esc(all[p.id].text)}</code>
          <span class="pz-ctl">
            <button type="button" data-act="out" title="Indent less (←)" aria-label="Indent less">⇤</button>
            <button type="button" data-act="in" title="Indent more (→)" aria-label="Indent more">⇥</button>
            <button type="button" data-act="up" title="Move up (↑)" aria-label="Move up">↑</button>
            <button type="button" data-act="down" title="Move down (↓)" aria-label="Move down">↓</button>
            <button type="button" data-act="rm" title="Remove (Delete)" aria-label="Remove">✕</button>
          </span></li>`).join("") || `<li class="faint small pz-empty">Add lines here, in order.</li>`}</ol>
        <p class="faint small">On a selected line: ↑ ↓ move it, ← → change its indentation, Delete removes it.</p></section></div>`;
    if (focusAfter?.row != null) host.querySelector(`.pz-row[data-i="${focusAfter.row}"]`)?.focus();
    focusAfter = null;
  }

  host.addEventListener("click", (e) => {
    const addBtn = e.target.closest("[data-add]");
    if (addBtn) return add(+addBtn.dataset.add);
    const btn = e.target.closest("[data-act]");
    if (btn) act(+btn.closest(".pz-row").dataset.i, btn.dataset.act);
  });
  host.addEventListener("keydown", (e) => {
    const row = e.target.closest?.(".pz-row");
    if (!row || e.target !== row || e.ctrlKey || e.metaKey || e.altKey) return;
    const map = { ArrowUp: "up", ArrowDown: "down", ArrowLeft: "out", ArrowRight: "in", Delete: "rm", Backspace: "rm" };
    if (map[e.key]) { e.preventDefault(); act(+row.dataset.i, map[e.key]); }
  });

  // Drag and drop: tiles from the pool into a position in the code, rows to a new position or back to the pool.
  let drag = null;
  host.addEventListener("dragstart", (e) => {
    const tile = e.target.closest("[data-add]"), row = e.target.closest(".pz-row");
    drag = tile ? { tile: +tile.dataset.add } : row ? { row: +row.dataset.i } : null;
    if (drag) e.dataTransfer.effectAllowed = "move";
  });
  host.addEventListener("dragover", (e) => { if (drag && e.target.closest("[data-zone]")) e.preventDefault(); });
  host.addEventListener("drop", (e) => {
    const zone = e.target.closest("[data-zone]");
    if (!drag || !zone) return;
    e.preventDefault();
    if (zone.dataset.zone === "pool") {
      if (drag.row != null) act(drag.row, "rm");
    } else {
      const over = e.target.closest(".pz-row");
      let at = over ? +over.dataset.i + (e.offsetY > over.offsetHeight / 2 ? 1 : 0) : placed.length;
      if (drag.tile != null) add(drag.tile, at);
      else {
        const [moved] = placed.splice(drag.row, 1);
        if (drag.row < at) at -= 1;
        placed.splice(at, 0, moved);
        changed({ row: at });
      }
    }
    drag = null;
  });

  draw();
  return {
    reset() { placed = []; changed(null); },
    get code() { return toCode(); },
  };
}
