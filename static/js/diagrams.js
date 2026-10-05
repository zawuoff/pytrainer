import { $$ } from "./core.js";

/* ---------------------------------------------------------------- interactive lesson diagrams
   A lesson can contain a fenced block tagged `diagram` holding JSON: {"type": "...", ...}.
   Markdown turns it into <pre><code class="language-diagram">, DOMPurify leaves that alone,
   and enhanceDiagrams() swaps each block for a widget built with DOM calls only (no innerHTML
   from lesson data), so nothing in the JSON can inject markup. */
export const SVG_NS = "http://www.w3.org/2000/svg";
export let dgSeq = 0;

export function dgNode(ns, tag, attrs, kids) {
  const n = ns ? document.createElementNS(ns, tag) : document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v === null || v === undefined || v === false) continue;
    if (k === "text") n.textContent = v;
    else if (k.startsWith("on")) n.addEventListener(k.slice(2), v);
    else n.setAttribute(k, v === true ? "" : v);
  }
  return dgAdd(n, kids);
}
/* append() that accepts nested arrays and skips null/false, so widgets can use map() and conditionals inline. */
export function dgAdd(parent, ...kids) {
  for (const kid of kids.flat(Infinity)) if (kid !== null && kid !== undefined && kid !== false) parent.append(kid);
  return parent;
}
export const dgEl = (tag, attrs, ...kids) => dgNode(null, tag, attrs, kids);
export const dgSvg = (tag, attrs, ...kids) => dgNode(SVG_NS, tag, attrs, kids);
export const dgClear = (n) => { while (n.firstChild) n.firstChild.remove(); return n; };
export const dgClamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));

/* A JSON value written the way Python's repr() prints it. {"raw": "1.0"} passes text through. */
export function pyRepr(v) {
  if (v === null || v === undefined) return "None";
  if (v === true) return "True";
  if (v === false) return "False";
  if (typeof v === "number") return String(v);
  if (typeof v === "string") {
    const q = v.includes("'") && !v.includes('"') ? '"' : "'";
    return q + v.replace(/\\/g, "\\\\").replace(/\n/g, "\\n").replace(/\t/g, "\\t").split(q).join("\\" + q) + q;
  }
  if (Array.isArray(v)) return "[" + v.map(pyRepr).join(", ") + "]";
  if (typeof v === "object") {
    if (typeof v.raw === "string" && Object.keys(v).length === 1) return v.raw;
    return "{" + Object.entries(v).map(([k, x]) => `${pyRepr(k)}: ${pyRepr(x)}`).join(", ") + "}";
  }
  return String(v);
}
/* What a learner types in a widget input, read as a Python literal where it obviously is one. */
export function pyParse(text) {
  const t = text.trim();
  if (/^-?\d+$/.test(t)) return Number(t);
  if (/^-?\d+\.\d+$/.test(t)) return Number(t) % 1 === 0 ? { raw: t } : Number(t);
  if (t === "True") return true;
  if (t === "False") return false;
  if (t === "None") return null;
  const m = t.match(/^(["'])(.*)\1$/);
  return m ? m[2] : t;
}
export const pyEq = (a, b) => JSON.stringify(a) === JSON.stringify(b);

/* One line of "code  ->  result" in a diagram's output area. */
export function dgLine(code, result, kind) {
  return dgEl("div", { class: "dg-line" + (kind ? " " + kind : "") },
    dgEl("code", { text: code }), result === undefined ? null : dgEl("span", { class: "dg-arrow", text: "gives" }),
    result === undefined ? null : dgEl("code", { class: "dg-res", text: result }));
}
export const dgNote = (text, kind) => dgEl("div", { class: "dg-note" + (kind ? " " + kind : ""), text });
export const dgBtn = (label, onclick, cls = "") => dgEl("button", { type: "button", class: "dg-btn " + cls, text: label, onclick });

export function dgFrame(spec, help) {
  const out = dgEl("div", { class: "dg-out", "aria-live": "polite" });
  const body = dgEl("div", { class: "dg-body" });
  const fig = dgEl("figure", { class: "dg", role: "group", "aria-label": "Interactive diagram: " + (spec.title || spec.type) },
    dgEl("figcaption", { class: "dg-cap" }, dgEl("span", { class: "dg-tag", text: "Interactive" }), dgEl("span", { text: spec.title || "" })),
    body, out, help ? dgEl("p", { class: "dg-help", text: help }) : null);
  return { fig, body, out };
}

/* ---- list-index / string-index: click a cell, read its positive and negative index */
export function dgSeqItems(spec) {
  const isStr = typeof spec.value === "string";
  return { isStr, items: isStr ? [...spec.value] : (spec.items || []), name: spec.name || (isStr ? "text" : "items") };
}
export function dgIndex(spec) {
  const { isStr, items, name } = dgSeqItems(spec);
  const kind = isStr ? "string" : "list";
  const f = dgFrame(spec, "Click a cell or move with the arrow keys. Type any index, including a negative one or one that is out of range.");
  const n = items.length;
  let sel = dgClamp(spec.index ?? 0, 0, Math.max(0, n - 1));
  const input = dgEl("input", { type: "number", class: "dg-in", value: sel, "aria-label": "Index to read" });
  const cells = items.map((v, i) => dgEl("button", { type: "button", class: "dg-cell", "aria-label": `index ${i}, value ${pyRepr(v)}`,
    onclick: () => show(i, true),
    onkeydown: (e) => {
      const d = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[e.key];
      if (!d) return;
      e.preventDefault();
      const j = dgClamp(i + d, 0, n - 1);
      show(j, true); cells[j].focus();
    } },
    dgEl("span", { class: "dg-idx", text: i }), dgEl("span", { class: "dg-val", text: isStr ? v : pyRepr(v) }), dgEl("span", { class: "dg-idx neg", text: i - n })));
  function show(raw, sync) {
    const i = raw < 0 ? raw + n : raw;
    const ok = Number.isInteger(raw) && i >= 0 && i < n;
    cells.forEach((c, j) => c.classList.toggle("on", ok && j === i));
    if (sync) input.value = raw;
    dgClear(f.out);
    if (!Number.isInteger(raw)) return void dgAdd(f.out, dgNote("Type a whole number."));
    if (!ok) {
      dgAdd(f.out, dgLine(`${name}[${raw}]`, `IndexError: ${kind} index out of range`, "bad"),
        dgNote(`len(${name}) is ${n}, so valid indexes are ${n ? `0 to ${n - 1} and -1 to ${-n}` : "none"}.`));
      return;
    }
    sel = i;
    dgAdd(f.out, dgLine(`${name}[${i}]`, pyRepr(items[i])), dgLine(`${name}[${i - n}]`, pyRepr(items[i])),
      dgNote(`Index ${i} and index ${i - n} are the same position: ${i} - len(${name}) is ${i} - ${n} = ${i - n}.`));
  }
  input.addEventListener("input", () => show(input.value === "" ? NaN : Number(input.value), false));
  dgAdd(f.body, dgEl("div", { class: "dg-code", text: `${name} = ${isStr ? pyRepr(spec.value) : pyRepr(items)}` }),
    dgEl("div", { class: "dg-cells" + (!isStr && items.some((v) => pyRepr(v).length > 18) ? " tall" : "") }, dgEl("span", { class: "dg-rowlabels" }, dgEl("span", { text: "index" }), dgEl("span", { text: "value" }), dgEl("span", { text: "negative" })), cells),
    dgEl("label", { class: "dg-field" }, dgEl("span", { text: `${name}[` }), input, dgEl("span", { text: "]" })));
  show(sel, true);
  return f.fig;
}

/* ---- slice: two draggable handles on the boundaries between cells */
export function dgSlice(spec) {
  const { isStr, items, name } = dgSeqItems(spec);
  const n = items.length;
  const f = dgFrame(spec, "Drag the start and stop handles, or focus one and press the arrow keys. Change the step with the buttons.");
  let start = dgClamp(spec.start ?? 1, 0, n), stop = dgClamp(spec.stop ?? n, 0, n), step = dgClamp(spec.step ?? 1, 1, 4);
  const cw = isStr ? 44 : Math.max(64, ...items.map((v) => pyRepr(v).length * 9 + 22)), padX = 34, top = 44, ch = 46;
  const W = padX * 2 + cw * n, H = top + ch + 62;
  const svg = dgSvg("svg", { class: "dg-svg", viewBox: `0 0 ${W} ${H}`, style: `max-width:${W}px`, role: "img", "aria-label": `Slice of ${name}` });
  const bx = (b) => padX + b * cw;
  const rects = items.map((v, i) => {
    const g = dgSvg("g", { class: "dg-scell" },
      dgSvg("rect", { x: bx(i) + 2, y: top, width: cw - 4, height: ch, rx: 6 }),
      dgSvg("text", { x: bx(i) + cw / 2, y: top + ch / 2 + 5, "text-anchor": "middle", class: "dg-t-val", text: isStr ? v : pyRepr(v) }),
      dgSvg("text", { x: bx(i) + cw / 2, y: top + ch + 18, "text-anchor": "middle", class: "dg-t-idx", text: i }));
    dgAdd(svg, g);
    return g;
  });
  const band = dgSvg("rect", { class: "dg-band", y: top - 5, height: ch + 10, rx: 8 });
  svg.prepend(band);
  function handle(label, isStart) {
    const y0 = isStart ? 8 : H - 8;
    const g = dgSvg("g", { class: "dg-handle" + (isStart ? " start" : " stop"), tabindex: 0, role: "slider", "aria-label": `${label} boundary`, "aria-valuemin": 0, "aria-valuemax": n },
      dgSvg("line", { x1: 0, x2: 0, y1: isStart ? 26 : top - 6, y2: isStart ? top + ch + 6 : H - 26 }),
      dgSvg("rect", { x: -26, y: isStart ? y0 - 4 : y0 - 18, width: 52, height: 22, rx: 6 }),
      dgSvg("text", { x: 0, y: isStart ? y0 + 12 : y0 - 2, "text-anchor": "middle" }));
    const set = (v) => { if (isStart) start = dgClamp(v, 0, n); else stop = dgClamp(v, 0, n); draw(); };
    const fromEvent = (e) => {
      const r = svg.getBoundingClientRect();
      set(Math.round(((e.clientX - r.left) * (W / r.width) - padX) / cw));
    };
    g.addEventListener("pointerdown", (e) => { e.preventDefault(); g.setPointerCapture(e.pointerId); g.focus(); g.classList.add("drag"); });
    g.addEventListener("pointermove", (e) => { if (g.hasPointerCapture(e.pointerId)) fromEvent(e); });
    g.addEventListener("pointerup", (e) => { g.releasePointerCapture(e.pointerId); g.classList.remove("drag"); });
    g.addEventListener("keydown", (e) => {
      const cur = isStart ? start : stop;
      const v = { ArrowLeft: cur - 1, ArrowDown: cur - 1, ArrowRight: cur + 1, ArrowUp: cur + 1, Home: 0, End: n }[e.key];
      if (v === undefined) return;
      e.preventDefault(); set(v);
    });
    dgAdd(svg, g);
    return g;
  }
  const hStart = handle("start", true), hStop = handle("stop", false);
  const stepLabel = dgEl("code", { class: "dg-steplabel" });
  function draw() {
    const picked = [];
    for (let i = start; i < stop; i += step) picked.push(i);
    rects.forEach((g, i) => { g.classList.toggle("on", picked.includes(i)); g.classList.toggle("skip", i >= start && i < stop && !picked.includes(i)); });
    band.setAttribute("x", bx(Math.min(start, stop)));
    band.setAttribute("width", Math.max(0, bx(stop) - bx(start)));
    for (const [g, v, lab] of [[hStart, start, "start"], [hStop, stop, "stop"]]) {
      g.setAttribute("transform", `translate(${bx(v)} 0)`);
      g.setAttribute("aria-valuenow", v);
      g.querySelector("text").textContent = `${lab} ${v}`;
    }
    stepLabel.textContent = `step ${step}`;
    const expr = `${name}[${start}:${stop}${step === 1 ? "" : ":" + step}]`;
    const val = isStr ? pyRepr(picked.map((i) => items[i]).join("")) : pyRepr(picked.map((i) => items[i]));
    dgAdd(dgClear(f.out), dgLine(expr, val));
    if (start >= stop) dgAdd(f.out, dgNote(`start (${start}) is not less than stop (${stop}), so no index is selected. The result is empty. It is not an error.`));
    else {
      dgAdd(f.out, dgNote(`Selected indexes: ${picked.join(", ")}. Index ${stop} (stop) is not included.${step > 1 ? ` With step ${step}, Python takes every ${step === 2 ? "2nd" : step === 3 ? "3rd" : "4th"} index starting at ${start}.` : ""}`));
      if (start < n) dgAdd(f.out, dgLine(`${name}[${start - n}:${stop === n ? "" : stop - n}${step === 1 ? "" : ":" + step}]`, val));
    }
  }
  dgAdd(f.body, dgEl("div", { class: "dg-code", text: `${name} = ${isStr ? pyRepr(spec.value) : pyRepr(items)}` }), svg,
    dgEl("div", { class: "dg-row" }, dgBtn("step - 1", () => { step = dgClamp(step - 1, 1, 4); draw(); }), stepLabel, dgBtn("step + 1", () => { step = dgClamp(step + 1, 1, 4); draw(); }),
      dgBtn("Reset", () => { start = dgClamp(spec.start ?? 1, 0, n); stop = dgClamp(spec.stop ?? n, 0, n); step = dgClamp(spec.step ?? 1, 1, 4); draw(); }, "ghost")));
  draw();
  return f.fig;
}

/* ---- alias-copy: two names, one or two list objects */
export function dgAlias(spec) {
  const A = spec.a || "a", B = spec.b || "b", init = spec.items || [1, 2, 3];
  const f = dgFrame(spec, `Choose how ${B} is created, then run statements and watch which list object changes.`);
  let mode, la, lb, log, next;
  const svgHost = dgEl("div", {}), actions = dgEl("div", { class: "dg-row" });
  const modeBtns = [["alias", `${B} = ${A}`], ["copy", `${B} = ${A}.copy()`]].map(([m, label]) => dgBtn(label, () => reset(m), "seg"));
  function reset(m) {
    mode = m; la = [...init]; lb = m === "alias" ? la : [...la];
    log = [`${A} = ${pyRepr(init)}`, m === "alias" ? `${B} = ${A}` : `${B} = ${A}.copy()`];
    next = typeof spec.append === "number" ? spec.append : 99;
    draw();
  }
  function listBox(x, y, list, label) {
    const cw = Math.max(46, ...list.map((v) => pyRepr(v).length * 9 + 18));
    return dgSvg("g", { class: "dg-obj" },
      dgSvg("text", { x, y: y - 8, class: "dg-t-idx", text: label }),
      list.length ? null : dgSvg("rect", { x, y, width: 60, height: 38, rx: 6, class: "empty" }),
      list.map((v, i) => [dgSvg("rect", { x: x + i * cw, y, width: cw - 3, height: 38, rx: 6 }),
        dgSvg("text", { x: x + i * cw + (cw - 3) / 2, y: y + 24, "text-anchor": "middle", class: "dg-t-val", text: pyRepr(v) })]));
  }
  function draw() {
    const same = la === lb, id = "dgah" + (++dgSeq);
    const longest = Math.max(la.length, lb.length, 1), cw = Math.max(46, ...[...la, ...lb].map((v) => pyRepr(v).length * 9 + 18));
    const nw = Math.max(62, Math.max(A.length, B.length) * 9 + 20), ox = nw + 98;
    const W = ox + longest * cw + 20, H = 150;
    const svg = dgSvg("svg", { class: "dg-svg", viewBox: `0 0 ${W} ${H}`, style: `max-width:${W}px`, role: "img",
      "aria-label": same ? `${A} and ${B} refer to the same list object` : `${A} and ${B} refer to two separate list objects` },
      dgSvg("defs", {}, dgSvg("marker", { id, viewBox: "0 0 10 10", refX: 9, refY: 5, markerWidth: 7, markerHeight: 7, orient: "auto" }, dgSvg("path", { d: "M0 0L10 5L0 10z", class: "dg-arrowhead" }))),
      [[A, 34], [B, 104]].map(([nm, y]) => [dgSvg("rect", { x: 10, y: y - 16, width: nw, height: 32, rx: 6, class: "dg-name" }),
        dgSvg("text", { x: 10 + nw / 2, y: y + 5, "text-anchor": "middle", class: "dg-t-val", text: nm })]),
      listBox(ox, same ? 50 : 15, la, same ? "one list object" : "list object 1"),
      same ? null : listBox(ox, 85, lb, "list object 2"),
      dgSvg("line", { x1: nw + 12, y1: 34, x2: ox - 4, y2: same ? 62 : 34, class: "dg-ref", "marker-end": `url(#${id})` }),
      dgSvg("line", { x1: nw + 12, y1: 104, x2: ox - 4, y2: same ? 76 : 104, class: "dg-ref", "marker-end": `url(#${id})` }));
    dgAdd(dgClear(svgHost), svg);
    modeBtns.forEach((b, i) => { const on = (i === 0) === (mode === "alias"); b.classList.toggle("on", on); b.setAttribute("aria-pressed", on); });
    const full = Math.max(la.length, lb.length) >= 6;
    dgAdd(dgClear(actions), 
      dgEl("button", { type: "button", class: "dg-btn", text: `${B}.append(${next})`, disabled: full, onclick: () => { lb.push(next); log.push(`${B}.append(${next})`); next += 1; draw(); } }),
      dgEl("button", { type: "button", class: "dg-btn", text: `${A}[0] = 0`, disabled: !la.length, onclick: () => { la[0] = 0; log.push(`${A}[0] = 0`); draw(); } }),
      dgEl("button", { type: "button", class: "dg-btn", text: `${B}.pop()`, disabled: !lb.length, onclick: () => { lb.pop(); log.push(`${B}.pop()`); draw(); } }),
      dgBtn("Reset", () => reset(mode), "ghost"));
    dgAdd(dgClear(f.out), dgEl("pre", { class: "dg-code", text: log.join("\n") }),
      dgLine(`print(${A})`, pyRepr(la)), dgLine(`print(${B})`, pyRepr(lb)), dgLine(`${A} is ${B}`, same ? "True" : "False"),
      dgNote(same ? `${B} = ${A} does not create a list. It makes the name ${B} refer to the list object that ${A} already refers to, so every change shows up under both names.`
        : `${A}.copy() creates a second list object with the same items. ${A} and ${B} refer to different objects, so changing one list does not change the other.`));
  }
  dgAdd(f.body, dgEl("div", { class: "dg-row" }, modeBtns), svgHost, actions);
  reset(spec.mode === "copy" ? "copy" : "alias");
  return f.fig;
}

/* ---- dict: look up, set and delete keys */
export function dgDict(spec) {
  const name = spec.name || "d";
  const f = dgFrame(spec, "Click a row to read that key. Type a key and a value, then run a statement. Try a key that does not exist.");
  let entries, last = null;
  const keyIn = dgEl("input", { type: "text", class: "dg-in wide", "aria-label": "Key", placeholder: "key" });
  const valIn = dgEl("input", { type: "text", class: "dg-in wide", "aria-label": "Value", placeholder: "value" });
  const table = dgEl("div", { class: "dg-dict" });
  const find = (k) => entries.findIndex(([x]) => pyEq(x, k));
  function run(op, k = pyParse(keyIn.value)) {
    const i = find(k), kr = pyRepr(k);
    let line;
    if (op === "get") line = i < 0 ? dgLine(`${name}[${kr}]`, `KeyError: ${kr}`, "bad") : dgLine(`${name}[${kr}]`, pyRepr(entries[i][1]));
    if (op === "dotget") line = dgLine(`${name}.get(${kr})`, i < 0 ? "None" : pyRepr(entries[i][1]));
    if (op === "in") line = dgLine(`${kr} in ${name}`, i < 0 ? "False" : "True");
    if (op === "set") {
      const v = pyParse(valIn.value);
      line = dgLine(`${name}[${kr}] = ${pyRepr(v)}`);
      if (i < 0) entries.push([k, v]); else entries[i][1] = v;
      last = { note: i < 0 ? `${kr} was not a key, so Python added a new key-value pair at the end.` : `${kr} was already a key, so Python replaced its value. The key keeps its position.` };
    }
    if (op === "del") {
      line = i < 0 ? dgLine(`del ${name}[${kr}]`, `KeyError: ${kr}`, "bad") : dgLine(`del ${name}[${kr}]`);
      if (i >= 0) entries.splice(i, 1);
    }
    draw(k);
    dgAdd(dgClear(f.out), line);
    if (op === "set") dgAdd(f.out, dgNote(last.note));
    if (op === "get" && i < 0) dgAdd(f.out, dgNote(`${kr} is not a key in ${name}. Square brackets raise KeyError for a missing key. ${name}.get(${kr}) returns None instead.`));
    dgAdd(f.out, dgLine(`print(${name})`, "{" + entries.map(([a, b]) => `${pyRepr(a)}: ${pyRepr(b)}`).join(", ") + "}"), dgLine(`len(${name})`, String(entries.length)));
  }
  function draw(hot) {
    dgAdd(dgClear(table), dgEl("div", { class: "dg-drow head" }, dgEl("span", { text: "key" }), dgEl("span", { text: "value" })),
      entries.map(([k, v]) => dgEl("button", { type: "button", class: "dg-drow" + (hot !== undefined && pyEq(hot, k) ? " on" : ""),
        onclick: () => { keyIn.value = typeof k === "string" ? k : pyRepr(k); run("get", k); } }, dgEl("code", { text: pyRepr(k) }), dgEl("code", { text: pyRepr(v) }))),
      entries.length ? null : dgEl("div", { class: "dg-drow empty", text: "{} (empty dict)" }));
  }
  const reset = () => { entries = (spec.entries || []).map(([k, v]) => [k, v]); keyIn.value = ""; valIn.value = ""; draw(); dgAdd(dgClear(f.out), dgNote("Click a row, or type a key and choose a statement.")); };
  dgAdd(f.body, table, dgEl("div", { class: "dg-row" }, keyIn, valIn),
    dgEl("div", { class: "dg-row" }, dgBtn(`${name}[key]`, () => run("get")), dgBtn(`${name}.get(key)`, () => run("dotget")), dgBtn(`key in ${name}`, () => run("in")),
      dgBtn(`${name}[key] = value`, () => run("set")), dgBtn(`del ${name}[key]`, () => run("del")), dgBtn("Reset", reset, "ghost")));
  reset();
  return f.fig;
}

/* ---- stack-queue: add at the end, remove from the end (stack) or the front (queue) */
export function dgStackQueue(spec) {
  const both = spec.mode === "both" || !spec.mode;
  let mode = spec.mode === "queue" ? "queue" : "stack";
  const f = dgFrame(spec, "Add values and remove them. Compare which item each structure removes first.");
  let items, log;
  const pushes = spec.push || ["d", "e", "f", "g"];
  let pushN = 0;
  const valIn = dgEl("input", { type: "text", class: "dg-in wide", "aria-label": "Value to add" });
  const row = dgEl("div", { class: "dg-cells" }), ctl = dgEl("div", { class: "dg-row" }), codeEl = dgEl("pre", { class: "dg-code" });
  const modeBtns = both ? [["stack", "Stack (list)"], ["queue", "Queue (deque)"]].map(([m, l]) => dgBtn(l, () => { mode = m; reset(); }, "seg")) : [];
  const nm = () => spec.name || (mode === "stack" ? "stack" : "queue");
  const show = () => mode === "stack" ? pyRepr(items) : `deque(${pyRepr(items)})`;
  function reset() { items = [...(spec.items || ["a", "b", "c"])]; pushN = 0; valIn.value = String(pushes[0] ?? "x"); log = []; draw(); }
  function act(op) {
    if (op === "push") {
      const v = pyParse(valIn.value);
      items.push(v); log = [dgLine(`${nm()}.append(${pyRepr(v)})`), dgNote("append adds the value at the right end.")];
      pushN += 1; valIn.value = String(pushes[pushN % pushes.length] ?? "x");
    } else if (!items.length) {
      log = [dgLine(mode === "stack" ? `${nm()}.pop()` : `${nm()}.popleft()`, mode === "stack" ? "IndexError: pop from empty list" : "IndexError: pop from an empty deque", "bad")];
    } else if (mode === "stack") {
      const v = items.pop();
      log = [dgLine(`${nm()}.pop()`, pyRepr(v)), dgNote("pop() removes and returns the last item, which is the one added most recently. This order is called last in, first out (LIFO).")];
    } else {
      const v = items.shift();
      log = [dgLine(`${nm()}.popleft()`, pyRepr(v)), dgNote("popleft() removes and returns the first item, which is the one that has been in the queue longest. This order is called first in, first out (FIFO).")];
    }
    draw();
  }
  function draw() {
    const first = pyRepr(spec.items || ["a", "b", "c"]);
    codeEl.textContent = mode === "stack" ? `${nm()} = ${first}` : `from collections import deque\n${nm()} = deque(${first})`;
    modeBtns.forEach((b, i) => { const on = (i === 0) === (mode === "stack"); b.classList.toggle("on", on); b.setAttribute("aria-pressed", on); });
    dgAdd(dgClear(row), items.map((v, i) => {
      const mark = mode === "stack" ? (i === items.length - 1 ? "top: pop() removes this" : "") : (i === 0 ? "front: popleft() removes this" : i === items.length - 1 ? "back" : "");
      return dgEl("div", { class: "dg-cell static" + (mark && !mark.startsWith("back") ? " on" : "") }, dgEl("span", { class: "dg-idx", text: i }), dgEl("span", { class: "dg-val", text: pyRepr(v) }), dgEl("span", { class: "dg-idx neg", text: mark.split(":")[0] }));
    }), items.length ? null : dgEl("div", { class: "dg-note", text: "(empty)" }));
    dgAdd(dgClear(ctl), valIn, dgBtn(`${nm()}.append(value)`, () => act("push")), dgBtn(mode === "stack" ? `${nm()}.pop()` : `${nm()}.popleft()`, () => act("pop")), dgBtn("Reset", reset, "ghost"));
    dgAdd(dgClear(f.out), log, dgLine(`print(${nm()})`, show()), dgLine(`len(${nm()})`, String(items.length)));
  }
  dgAdd(f.body, both ? dgEl("div", { class: "dg-row" }, modeBtns) : null, codeEl, row, ctl);
  reset();
  return f.fig;
}

/* ---- shared step controls (trace, recursion, flow) */
export function dgStepper(count, onStep, start = 0) {
  let i = start, timer = null;
  const label = dgEl("span", { class: "dg-count" });
  const range = dgEl("input", { type: "range", min: 0, max: count - 1, value: i, class: "dg-range", "aria-label": "Step" });
  const back = dgBtn("Back", () => go(i - 1)), fwd = dgBtn("Next", () => go(i + 1), "primary");
  const play = dgBtn("Play", () => { if (timer) return stop(); if (i >= count - 1) go(0); play.textContent = "Pause"; timer = setInterval(() => { if (i >= count - 1) stop(); else go(i + 1, true); }, 900); });
  function stop() { clearInterval(timer); timer = null; play.textContent = "Play"; }
  function go(j, keep) {
    if (!keep) stop();
    i = dgClamp(j, 0, count - 1);
    range.value = i; back.disabled = i === 0; fwd.disabled = i === count - 1;
    label.textContent = `Step ${i + 1} of ${count}`;
    onStep(i);
  }
  range.addEventListener("input", () => go(Number(range.value)));
  const bar = dgEl("div", { class: "dg-row dg-stepper" }, back, fwd, play, dgBtn("Reset", () => go(0), "ghost"), range, label);
  return { bar, go, get i() { return i; } };
}

/* ---- trace: step through code one line at a time (used for loops and any other control flow) */
export function dgTrace(spec) {
  const lines = Array.isArray(spec.code) ? spec.code : String(spec.code || "").split("\n");
  const steps = spec.steps || [];
  const f = dgFrame(spec, "Press Next to run one line. The highlighted line is the line Python runs next. Changed variables are marked.");
  const code = dgEl("ol", { class: "dg-src" }, lines.map((l) => dgEl("li", {}, dgEl("code", { text: l || " " }))));
  const vars = dgEl("div", { class: "dg-vars" }), outBox = dgEl("pre", { class: "dg-stdout" });
  const st = dgStepper(Math.max(1, steps.length), (i) => {
    const s = steps[i] || {}, prev = steps[i - 1] || { vars: {} };
    [...code.children].forEach((li, n) => { li.classList.toggle("on", n + 1 === s.line); if (n + 1 === s.line) li.setAttribute("aria-current", "step"); else li.removeAttribute("aria-current"); });
    const names = Object.keys(s.vars || {});
    dgAdd(dgClear(vars), dgEl("div", { class: "dg-vhead", text: "Variables" }),
      names.length ? names.map((k) => dgEl("div", { class: "dg-var" + (i > 0 && (prev.vars || {})[k] !== s.vars[k] ? " changed" : "") }, dgEl("code", { text: k }), dgEl("code", { text: s.vars[k] })))
        : dgEl("div", { class: "dg-note", text: "No variables yet." }));
    outBox.textContent = s.out || "";
    outBox.classList.toggle("empty", !s.out);
    dgAdd(dgClear(f.out), s.error ? dgLine("the program stops with", s.error, "bad") : dgNote(s.note || (s.line ? `Next: line ${s.line}.` : "The program has finished.")));
  });
  dgAdd(f.body, dgEl("div", { class: "dg-trace" }, code, dgEl("div", {}, vars, dgEl("div", { class: "dg-vhead", text: "Output so far" }), outBox)), st.bar);
  st.go(0);
  return f.fig;
}

/* ---- recursion: a call tree that fills in as calls start and return */
export function dgRecursion(spec) {
  const f = dgFrame(spec, "Press Next to follow the calls in the order Python makes them. Click a call to jump to the moment it starts.");
  const nodes = [], events = [];
  (function walk(n, depth, parent) {
    const node = { call: n.call, ret: n.ret, depth, parent, kids: [], w: Math.max(76, Math.max(String(n.call).length, String(n.ret ?? "").length + 9) * 8 + 18) };
    nodes.push(node);
    node.callAt = events.push({ node, kind: "call" }) - 1;
    for (const c of n.children || []) node.kids.push(walk(c, depth + 1, node));
    node.retAt = events.push({ node, kind: "ret" }) - 1;
    return node;
  })(spec.root || { call: "f()", ret: "None" }, 0, null);
  let cursor = 12;
  (function place(n) {
    if (!n.kids.length) { n.x = cursor + n.w / 2; cursor += n.w + 14; return; }
    const before = cursor;
    n.kids.forEach(place);
    n.x = (n.kids[0].x + n.kids[n.kids.length - 1].x) / 2;
    if (cursor - before < n.w + 14) { const shift = (n.w + 14 - (cursor - before)) / 2; (function mv(k) { k.x += shift; k.kids.forEach(mv); })(n); n.x = before + (n.w + 14) / 2; cursor = before + n.w + 14; }
  })(nodes[0]);
  const rowH = 78, W = cursor + 12, H = (Math.max(...nodes.map((n) => n.depth)) + 1) * rowH + 6;
  const svg = dgSvg("svg", { class: "dg-svg", viewBox: `0 0 ${W} ${H}`, style: `max-width:${Math.max(W, 260)}px`, role: "group", "aria-label": "Call tree" });
  for (const n of nodes) if (n.parent) n.edge = svg.appendChild(dgSvg("line", { class: "dg-edge", x1: n.parent.x, y1: n.parent.depth * rowH + 50, x2: n.x, y2: n.depth * rowH + 8 }));
  for (const n of nodes) {
    n.retText = dgSvg("text", { x: n.x, y: n.depth * rowH + 42, "text-anchor": "middle", class: "dg-t-idx" });
    n.g = svg.appendChild(dgSvg("g", { class: "dg-call", tabindex: 0, role: "button", "aria-label": `${n.call}, returns ${n.ret}`,
      onclick: () => st.go(n.callAt), onkeydown: (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); st.go(n.callAt); } } },
      dgSvg("rect", { x: n.x - n.w / 2, y: n.depth * rowH + 8, width: n.w, height: 42, rx: 8 }),
      dgSvg("text", { x: n.x, y: n.depth * rowH + 26, "text-anchor": "middle", class: "dg-t-val", text: n.call }), n.retText));
  }
  const st = dgStepper(events.length, (i) => {
    const ev = events[i], stack = [];
    for (const n of nodes) {
      const started = n.callAt <= i, done = n.retAt <= i;
      n.g.classList.toggle("pending", !started); n.g.classList.toggle("active", started && !done); n.g.classList.toggle("done", done); n.g.classList.toggle("now", ev.node === n);
      if (n.edge) n.edge.classList.toggle("pending", !started);
      n.retText.textContent = done ? `returns ${n.ret}` : started ? "running" : "";
      if (started && !done) stack.push(n.call);
    }
    dgAdd(dgClear(f.out), 
      dgNote(ev.kind === "call" ? `Python calls ${ev.node.call}.${ev.node.kids.length ? " It cannot return until the calls it makes have returned." : " This call makes no further calls."}` : `${ev.node.call} returns ${ev.node.ret}.${ev.node.parent ? ` Control goes back to ${ev.node.parent.call}.` : " This is the final result."}`),
      dgNote(stack.length ? `Calls that have started and not yet returned: ${stack.join(", then ")}.` : "Every call has returned."));
  });
  dgAdd(f.body, svg, st.bar);
  st.go(0);
  return f.fig;
}

/* ---- set-ops: two sets, five operators */
export function dgSetOps(spec) {
  const A = spec.a || { name: "a", items: [1, 2, 3] }, B = spec.b || { name: "b", items: [3, 4] };
  const an = A.name || "a", bn = B.name || "b";
  const inB = (v) => B.items.some((x) => pyEq(x, v)), inA = (v) => A.items.some((x) => pyEq(x, v));
  const uniq = (xs) => xs.filter((v, i) => xs.findIndex((x) => pyEq(x, v)) === i);
  const regions = { left: uniq(A.items.filter((v) => !inB(v))), mid: uniq(A.items.filter(inB)), right: uniq(B.items.filter((v) => !inA(v))) };
  const ops = [
    { expr: `${an} | ${bn}`, word: "union", parts: ["left", "mid", "right"], why: `every value that is in ${an}, in ${bn}, or in both` },
    { expr: `${an} & ${bn}`, word: "intersection", parts: ["mid"], why: `only the values that are in both ${an} and ${bn}` },
    { expr: `${an} - ${bn}`, word: "difference", parts: ["left"], why: `the values in ${an} that are not in ${bn}` },
    { expr: `${bn} - ${an}`, word: "difference", parts: ["right"], why: `the values in ${bn} that are not in ${an}` },
    { expr: `${an} ^ ${bn}`, word: "symmetric difference", parts: ["left", "right"], why: `the values that are in exactly one of the two sets` },
  ];
  const f = dgFrame(spec, "Choose an operator, or click a region of the diagram to select the operator that produces it.");
  const id = "dgclip" + (++dgSeq), W = 440, H = 230, r = 92, ax = 160, bx = 280, cy = 118;
  const col = (xs, x) => xs.slice(0, 6).map((v, i) => dgSvg("text", { x, y: cy - (Math.min(xs.length, 6) - 1) * 11 + i * 22 + 5, "text-anchor": "middle", class: "dg-t-val", text: pyRepr(v) }));
  const part = (name, attrs, pick) => dgSvg("circle", { ...attrs, class: "dg-region", "data-part": name, tabindex: 0, role: "button", "aria-label": `Region: ${pick.why}`,
    onclick: () => choose(ops.indexOf(pick)), onkeydown: (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); choose(ops.indexOf(pick)); } } });
  const svg = dgSvg("svg", { class: "dg-svg", viewBox: `0 0 ${W} ${H}`, style: `max-width:${W}px`, role: "group", "aria-label": `Sets ${an} and ${bn}` },
    dgSvg("defs", {}, dgSvg("clipPath", { id }, dgSvg("circle", { cx: ax, cy, r }))),
    part("left", { cx: ax, cy, r }, ops[2]), part("right", { cx: bx, cy, r }, ops[3]),
    dgSvg("circle", { cx: bx, cy, r, "clip-path": `url(#${id})`, class: "dg-erase" }),
    part("mid", { cx: bx, cy, r, "clip-path": `url(#${id})` }, ops[1]),
    dgSvg("circle", { cx: ax, cy, r, class: "dg-ring" }), dgSvg("circle", { cx: bx, cy, r, class: "dg-ring" }),
    dgSvg("text", { x: ax - 50, y: 20, "text-anchor": "middle", class: "dg-t-name", text: an }), dgSvg("text", { x: bx + 50, y: 20, "text-anchor": "middle", class: "dg-t-name", text: bn }),
    col(regions.left, ax - 42), col(regions.mid, (ax + bx) / 2), col(regions.right, bx + 42));
  const btns = ops.map((o, i) => dgBtn(o.expr, () => choose(i), "seg"));
  const sorted = (xs) => [...xs].sort((p, q) => (typeof p === "number" && typeof q === "number" ? p - q : pyRepr(p) < pyRepr(q) ? -1 : 1));
  function choose(i) {
    const o = ops[i];
    btns.forEach((b, j) => { b.classList.toggle("on", i === j); b.setAttribute("aria-pressed", i === j); });
    svg.querySelectorAll(".dg-region").forEach((c) => c.classList.toggle("on", o.parts.includes(c.dataset.part)));
    const result = sorted(o.parts.flatMap((p) => regions[p]));
    dgAdd(dgClear(f.out), dgLine(`sorted(${o.expr})`, pyRepr(result)), dgLine(`len(${o.expr})`, String(result.length)),
      dgNote(`${o.expr} is the ${o.word}: ${o.why}.${result.length ? "" : " No value qualifies, so the result is the empty set, which Python prints as set()."} A set has no order, so sorted() is used here to print the values in a fixed order.`));
  }
  dgAdd(f.body, dgEl("pre", { class: "dg-code", text: `${an} = {${uniq(A.items).map(pyRepr).join(", ")}}\n${bn} = {${uniq(B.items).map(pyRepr).join(", ")}}` }), svg, dgEl("div", { class: "dg-row" }, btns));
  choose(dgClamp(spec.op ?? 0, 0, ops.length - 1));
  return f.fig;
}

/* ---- flow: a sequence of stages, each with an explanation and optional data */
export function dgFlow(spec) {
  const steps = spec.steps || [];
  const f = dgFrame(spec, "Click a stage, or use Next and Back, to see what happens at each stage and what the data looks like there.");
  const detail = dgEl("div", { class: "dg-detail" });
  const boxes = steps.map((s, i) => dgEl("button", { type: "button", class: "dg-stage", onclick: () => st.go(i) }, dgEl("span", { class: "dg-num", text: i + 1 }), dgEl("span", { text: s.label })));
  const loop = spec.loop && steps[spec.loop.to] ? dgEl("div", { class: "dg-loop", text: `After stage ${(spec.loop.from ?? steps.length - 1) + 1}: ${spec.loop.label || "repeat"}, go back to stage ${spec.loop.to + 1} (${steps[spec.loop.to].label}).` }) : null;
  const st = dgStepper(Math.max(1, steps.length), (i) => {
    boxes.forEach((b, j) => { b.classList.toggle("on", i === j); b.classList.toggle("past", j < i); if (i === j) b.setAttribute("aria-current", "step"); else b.removeAttribute("aria-current"); });
    const s = steps[i] || {};
    dgAdd(dgClear(detail), dgEl("div", { class: "dg-vhead", text: `Stage ${i + 1}: ${s.label || ""}` }), dgEl("p", { text: s.detail || "" }), s.code ? dgEl("pre", { class: "dg-code", text: s.code }) : null);
  });
  dgAdd(f.body, dgEl("div", { class: "dg-flow" }, boxes.flatMap((b, i) => i ? [dgEl("span", { class: "dg-sep", "aria-hidden": "true", text: ">" }), b] : [b])), loop, detail, st.bar);
  f.out.remove();
  st.go(0);
  return f.fig;
}

/* ---- vectors: drag two 2D vectors, read dot product and cosine similarity */
export function dgVectors(spec) {
  const f = dgFrame(spec, "Drag the end of a vector, or focus it and press the arrow keys. The numbers below are recomputed each time.");
  const v = { a: [...(spec.a || [3, 1])], b: [...(spec.b || [1, 3])] }, lim = 5, S = 300, u = S / (lim * 2 + 1), o = S / 2;
  const px = ([x, y]) => [o + x * u, o - y * u];
  const svg = dgSvg("svg", { class: "dg-svg", viewBox: `0 0 ${S} ${S}`, style: `max-width:${S}px`, role: "group", "aria-label": "Two vectors on a grid" });
  for (let i = -lim; i <= lim; i++) dgAdd(svg, dgSvg("line", { class: i ? "dg-grid" : "dg-axis", x1: o + i * u, x2: o + i * u, y1: o - lim * u, y2: o + lim * u }), dgSvg("line", { class: i ? "dg-grid" : "dg-axis", y1: o + i * u, y2: o + i * u, x1: o - lim * u, x2: o + lim * u }));
  const parts = {};
  for (const k of ["a", "b"]) {
    const line = dgSvg("line", { class: "dg-vec " + k, x1: o, y1: o }), label = dgSvg("text", { class: "dg-t-name " + k });
    const tip = dgSvg("circle", { class: "dg-tip " + k, r: 9, tabindex: 0, role: "slider", "aria-label": `End of vector ${k}` });
    const set = (x, y) => { v[k] = [dgClamp(Math.round(x), -lim, lim), dgClamp(Math.round(y), -lim, lim)]; draw(); };
    tip.addEventListener("pointerdown", (e) => { e.preventDefault(); tip.setPointerCapture(e.pointerId); tip.focus(); });
    tip.addEventListener("pointermove", (e) => {
      if (!tip.hasPointerCapture(e.pointerId)) return;
      const r = svg.getBoundingClientRect(), sc = S / r.width;
      set(((e.clientX - r.left) * sc - o) / u, (o - (e.clientY - r.top) * sc) / u);
    });
    tip.addEventListener("pointerup", (e) => tip.releasePointerCapture(e.pointerId));
    tip.addEventListener("keydown", (e) => {
      const d = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, 1], ArrowDown: [0, -1] }[e.key];
      if (!d) return;
      e.preventDefault(); set(v[k][0] + d[0], v[k][1] + d[1]);
    });
    dgAdd(svg, line, label, tip);
    parts[k] = { line, label, tip };
  }
  const fmt = (x) => String(Math.round(x * 1000) / 1000);
  function draw() {
    for (const k of ["a", "b"]) {
      const [x, y] = px(v[k]);
      parts[k].line.setAttribute("x2", x); parts[k].line.setAttribute("y2", y);
      parts[k].tip.setAttribute("cx", x); parts[k].tip.setAttribute("cy", y);
      parts[k].tip.setAttribute("aria-valuetext", `${k} = [${v[k]}]`);
      parts[k].label.setAttribute("x", x + 12); parts[k].label.setAttribute("y", y - 10); parts[k].label.textContent = k;
    }
    const dot = v.a[0] * v.b[0] + v.a[1] * v.b[1], na = Math.hypot(...v.a), nb = Math.hypot(...v.b);
    dgAdd(dgClear(f.out), dgLine(`a = [${v.a.join(", ")}]`), dgLine(`b = [${v.b.join(", ")}]`),
      dgLine("dot = a[0]*b[0] + a[1]*b[1]", String(dot)), dgLine("norm_a = math.sqrt(a[0]**2 + a[1]**2)", fmt(na)), dgLine("norm_b = math.sqrt(b[0]**2 + b[1]**2)", fmt(nb)));
    if (!na || !nb) dgAdd(f.out, dgLine("dot / (norm_a * norm_b)", "ZeroDivisionError: division by zero", "bad"), dgNote("A vector of all zeros has length 0, so the formula divides by zero. Code must check for this case."));
    else {
      const cos = dot / (na * nb);
      dgAdd(f.out, dgLine("dot / (norm_a * norm_b)", fmt(cos)),
        dgNote(`The angle between a and b is ${fmt(Math.acos(dgClamp(cos, -1, 1)) * 180 / Math.PI)} degrees. Cosine similarity is 1 when the vectors point in the same direction, 0 when they are at 90 degrees, and -1 when they point in opposite directions. It does not depend on the lengths. Results are rounded to 3 decimal places here.`));
    }
  }
  dgAdd(f.body, svg);
  draw();
  return f.fig;
}

/* ---- chunks: fixed-size chunks with overlap over a text */
export function dgChunks(spec) {
  const words = spec.unit === "words";
  const units = words ? String(spec.text || "").split(/\s+/).filter(Boolean) : [...String(spec.text || "")];
  const f = dgFrame(spec, "Move the sliders to change the chunk size and the overlap. Click a chunk to highlight the part of the text it covers.");
  let size = dgClamp(spec.size ?? 8, 2, Math.max(2, units.length)), overlap = dgClamp(spec.overlap ?? 2, 0, size - 1), sel = 0;
  const maxSize = Math.min(units.length, spec.max_size ?? (words ? 20 : 60));
  const sizeIn = dgEl("input", { type: "range", class: "dg-range", min: 2, max: maxSize, value: size, "aria-label": "Chunk size" });
  const ovIn = dgEl("input", { type: "range", class: "dg-range", min: 0, value: overlap, "aria-label": "Overlap" });
  const sizeLab = dgEl("code", {}), ovLab = dgEl("code", {}), text = dgEl("div", { class: "dg-text" + (words ? " words" : "") }), list = dgEl("div", { class: "dg-chunks" });
  function draw() {
    overlap = dgClamp(overlap, 0, size - 1);
    ovIn.max = size - 1; ovIn.value = overlap; sizeIn.value = size;
    sizeLab.textContent = `size = ${size}`; ovLab.textContent = `overlap = ${overlap}`;
    const step = size - overlap, starts = [];
    for (let s = 0; s < units.length; s += step) starts.push(s);
    sel = dgClamp(sel, 0, starts.length - 1);
    const s0 = starts[sel], prevEnd = sel > 0 ? starts[sel - 1] + size : -1;
    dgAdd(dgClear(text), units.map((c, i) => dgEl("span", { class: i >= s0 && i < s0 + size ? (i < prevEnd ? "shared" : "on") : "", text: words ? c + " " : c })));
    const piece = (s) => words ? units.slice(s, s + size).join(" ") : units.slice(s, s + size).join("");
    dgAdd(dgClear(list), starts.map((s, i) => dgEl("button", { type: "button", class: "dg-chunk" + (i === sel ? " on" : ""), "aria-pressed": i === sel, onclick: () => { sel = i; draw(); list.children[sel]?.focus(); } },
      dgEl("span", { class: "dg-num", text: i }), dgEl("code", { text: `[${s}:${s + size}]` }), dgEl("code", { class: "dg-res", text: pyRepr(piece(s)) }))));
    dgAdd(dgClear(f.out), dgLine("step = size - overlap", String(step)), dgLine("len(chunks)", String(starts.length)),
      dgNote(`Chunk ${sel} starts at ${words ? "word" : "index"} ${s0}. Each chunk starts ${step} ${words ? "word" : "character"}${step === 1 ? "" : "s"} after the previous one${overlap ? `, so it repeats the last ${overlap} ${words ? "word" : "character"}${overlap === 1 ? "" : "s"} of the previous chunk (shown in the second colour)` : ", so chunks do not share any text"}. A slice that runs past the end is cut short. It does not raise an error.`));
  }
  sizeIn.addEventListener("input", () => { size = Number(sizeIn.value); draw(); });
  ovIn.addEventListener("input", () => { overlap = Number(ovIn.value); draw(); });
  dgAdd(f.body, dgEl("pre", { class: "dg-code", text: words
    ? "words = text.split()\nstep = size - overlap\nchunks = [\" \".join(words[i:i + size]) for i in range(0, len(words), step)]"
    : "step = size - overlap\nchunks = [text[i:i + size] for i in range(0, len(text), step)]" }),
    dgEl("div", { class: "dg-row" }, dgEl("label", { class: "dg-field" }, sizeLab, sizeIn), dgEl("label", { class: "dg-field" }, ovLab, ovIn)), text, list);
  draw();
  return f.fig;
}

export const DIAGRAMS = {
  "list-index": dgIndex, "string-index": dgIndex, slice: dgSlice, "alias-copy": dgAlias, dict: dgDict, "stack-queue": dgStackQueue,
  trace: dgTrace, "loop-trace": dgTrace, recursion: dgRecursion, "set-ops": dgSetOps, flow: dgFlow, vectors: dgVectors, chunks: dgChunks,
};

/* Runs after DOMPurify: replace every ```diagram block under root with its widget. */
export function enhanceDiagrams(root) {
  $$("pre > code.language-diagram", root).forEach((codeEl) => {
    const pre = codeEl.parentElement;
    let widget;
    try {
      const spec = JSON.parse(codeEl.textContent);
      if (!DIAGRAMS[spec.type]) throw new Error(`unknown diagram type "${spec.type}"`);
      widget = DIAGRAMS[spec.type](spec);
    } catch (err) {
      widget = dgEl("div", { class: "dg dg-broken", text: "This diagram could not be shown: " + err.message });
    }
    pre.replaceWith(widget);
  });
}
