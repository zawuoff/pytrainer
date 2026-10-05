import { $, $$, anim, api, busy, cleanup, flip, highlight, motionOK, toast } from "./core.js";
import { EDITOR_OPTS, enhanceCode } from "./shared.js";
import { dgAdd, dgBtn, dgClear, dgEl, enhanceDiagrams } from "./diagrams.js";

/* ---------------------------------------------------------------- interactive lesson blocks
   A lesson can contain fenced blocks tagged quiz, predict, fill, order, try or match. They are plain
   text (the format is in CONTENT_GUIDE.md, "v6"), so they are easy to write and
   scripts/lesson_tools.py can run the code in them. enhanceBlocks() swaps each one for a small
   activity. Answers are never trusted from the lesson text alone: wherever code is involved the
   activity runs it through /api/run and compares real output. */

export const mdInline = (text) => DOMPurify.sanitize(marked.parseInline(text || ""));
export const lxHtml = (html, cls) => { const d = document.createElement("div"); d.className = cls; d.innerHTML = html; return d; };
export const lxMd = (text, cls) => { const d = lxHtml(DOMPurify.sanitize(marked.parse(text || "")), cls); highlight(d); return d; };
export const lxRun = (code) => api("run", { code });
export const lxNorm = (t) => (t || "").replace(/\r/g, "").split("\n").map((l) => l.replace(/\s+$/, "")).join("\n").replace(/\n+$/, "");
export const lxErr = (r) => (r.timed_out ? "The program ran for too long and was stopped." : (r.stderr || "").trim().split("\n").pop());

export function lxSections(body) {
  const parts = [[]];
  for (const line of body.split("\n")) { if (line.trim() === "---") parts.push([]); else parts[parts.length - 1].push(line); }
  return parts.map((p) => p.join("\n").replace(/^\n+|\n+$/g, ""));
}
/* `- [x] label :: feedback` lines; a line after an option that is not an option continues its feedback. */
export function lxOptions(text) {
  const head = [], opts = [];
  for (const line of text.split("\n")) {
    const m = line.trim().match(/^- \[( |x|X)\] (.*)$/);
    if (m) {
      const i = m[2].indexOf(" :: ");
      opts.push({ ok: m[1] !== " ", label: (i < 0 ? m[2] : m[2].slice(0, i)).trim(), why: i < 0 ? "" : m[2].slice(i + 4).trim() });
    } else if (opts.length) {
      if (line.trim()) opts[opts.length - 1].why = (opts[opts.length - 1].why + " " + line.trim()).trim();
    } else head.push(line);
  }
  return { head: head.join("\n").trim(), opts };
}
/* The same shuffle every time for the same block, and never the order it was written in. */
export function lxShuffle(n, seedText) {
  let h = 2166136261;
  for (let i = 0; i < seedText.length; i++) h = Math.imul(h ^ seedText.charCodeAt(i), 16777619) >>> 0;
  const rnd = () => { h = Math.imul(h ^ (h >>> 15), 2246822507) >>> 0; h = Math.imul(h ^ (h >>> 13), 3266489909) >>> 0; h = (h ^ (h >>> 16)) >>> 0; return h / 4294967296; };
  const out = Array.from({ length: n }, (_, i) => i);
  for (let tries = 0; tries < 6 && out.every((v, i) => v === i); tries++)
    for (let i = n - 1; i > 0; i--) { const j = Math.floor(rnd() * (i + 1)); [out[i], out[j]] = [out[j], out[i]]; }
  if (n > 1 && out.every((v, i) => v === i)) out.push(out.shift());
  return out;
}

export function lxFrame(kind, label) {
  const body = dgEl("div", { class: "lx-body" });
  const foot = dgEl("div", { class: "lx-foot", "aria-live": "polite" });
  const fig = dgEl("figure", { class: `lx lx-${kind}`, role: "group", "aria-label": label },
    dgEl("figcaption", { class: "lx-cap" }, dgEl("span", { class: "lx-tag", text: label }), dgEl("span", { class: "lx-mark", "aria-hidden": "true" })), body, foot);
  const done = (right = true) => {
    if (fig.classList.contains("done")) return;
    fig.classList.add("done");
    fig.classList.toggle("right", right);
    fig.dispatchEvent(new CustomEvent("lx-done", { bubbles: true }));
  };
  return { fig, body, foot, done };
}
/* One feedback message under an activity. kind: good | bad | info. */
export function lxSay(foot, kind, text, ...extra) {
  const box = dgEl("div", { class: "lx-say " + kind }, lxHtml(DOMPurify.sanitize(marked.parse(text || "")), "lx-md"), extra);
  highlight(box);
  dgAdd(dgClear(foot), box);
  anim(box, [{ opacity: 0, transform: "translateY(-6px)" }, { opacity: 1, transform: "none" }], { duration: 260 });
  return box;
}
export const lxShake = (el) => anim(el, [{ transform: "translateX(0)" }, { transform: "translateX(-6px)" }, { transform: "translateX(5px)" }, { transform: "translateX(-3px)" }, { transform: "translateX(0)" }], { duration: 320, easing: "ease-out" });
export const lxPop = (el) => anim(el, [{ transform: "scale(1)" }, { transform: "scale(1.035)" }, { transform: "scale(1)" }], { duration: 320 });
export function lxOut(r, label = "Python printed") {
  const text = (r.stdout || "") + (r.returncode === 0 && !r.timed_out ? "" : (r.stdout && !r.stdout.endsWith("\n") ? "\n" : ""));
  return dgEl("div", { class: "lx-outwrap" }, dgEl("div", { class: "lx-label", text: label }),
    dgEl("pre", { class: "lx-out" }, text || (r.returncode === 0 ? dgEl("span", { class: "faint", text: "(nothing)" }) : null),
      r.returncode !== 0 || r.timed_out ? dgEl("span", { class: "lx-errline", text: lxErr(r) }) : null));
}
export function lxCode(code) {
  const codeEl = dgEl("code", { class: "cm-s-pt" });
  CodeMirror.runMode(code, "python", codeEl);
  codeEl.dataset.hl = "1";
  return dgEl("pre", { class: "lx-code" }, codeEl);
}

/* ---- quiz: one question, pick an option, every option explains itself */
export function lxQuiz(body) {
  const { head, opts } = lxOptions(body);
  const f = lxFrame("quiz", "Quick check");
  const list = dgEl("div", { class: "lx-opts" });
  lxShuffle(opts.length, body).forEach((k, n) => {
    const o = opts[k];
    const btn = dgEl("button", { type: "button", class: "lx-opt" }, dgEl("span", { class: "lx-key", text: "ABCDE"[n] }), lxHtml(mdInline(o.label), "lx-optlabel"));
    btn.onclick = () => {
      if (f.fig.classList.contains("done")) return;
      $$(".lx-opt", list).forEach((b) => b.classList.remove("wrong"));
      if (o.ok) {
        btn.classList.add("right");
        $$(".lx-opt", list).forEach((b) => { if (b !== btn) b.disabled = true; });
        lxPop(btn); lxSay(f.foot, "good", o.why); f.done();
      } else {
        btn.classList.add("wrong", "tried"); lxShake(btn); lxSay(f.foot, "bad", o.why);
      }
    };
    list.append(btn);
  });
  dgAdd(f.body, lxMd(head, "lx-md lx-q"), list);
  return f.fig;
}

/* ---- predict: type what the code prints, then Python runs it */
export function lxPredict(body) {
  const [code, why] = lxSections(body);
  const f = lxFrame("predict", "Predict");
  const guess = dgEl("textarea", { class: "lx-guess", rows: 2, spellcheck: "false", "aria-label": "Your prediction", placeholder: "What will it print? One line for each print." });
  guess.addEventListener("input", () => { guess.rows = Math.min(8, Math.max(2, guess.value.split("\n").length)); });
  const go = dgBtn("Check my guess", () => act(false), "primary"), skip = dgBtn("Show me", () => act(true), "ghost");
  const row = dgEl("div", { class: "lx-row" }, go, skip);
  async function act(reveal) {
    if (!reveal && !guess.value.trim()) { guess.focus(); lxShake(guess); return; }
    busy(go, true); skip.disabled = true;
    try {
      const r = await lxRun(code);
      const actual = lxNorm(r.stdout).split("\n"), mine = lxNorm(guess.value).split("\n");
      const right = !reveal && actual.join("\n") === mine.join("\n");
      guess.readOnly = true; row.remove();
      const table = dgEl("div", { class: "lx-compare" },
        dgEl("div", { class: "lx-label", text: "Python printed" }),
        actual.map((line, i) => dgEl("div", { class: "lx-cmp " + (reveal ? "" : mine[i] === line ? "ok" : "no"), style: `--i:${i}` },
          dgEl("span", { class: "ic", text: reveal ? "" : mine[i] === line ? "✓" : "✕" }), dgEl("code", { text: line || " " }))),
        !reveal && mine.length > actual.length ? dgEl("div", { class: "lx-note", text: `You predicted ${mine.length} lines. The program prints ${actual.length}.` }) : null);
      lxSay(f.foot, right ? "good" : "info", (right ? "**Exactly right.** " : reveal ? "" : "**Not quite.** Compare your lines with what Python printed. ") + why).prepend(table);
      f.done(right);
    } catch (err) { toast(err.message, true); busy(go, false); skip.disabled = false; }
  }
  guess.addEventListener("keydown", (e) => { if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) { e.preventDefault(); act(false); } });
  dgAdd(f.body, lxCode(code), guess, row);
  return f.fig;
}

/* ---- fill: one gap in the code, pick what goes in it */
export function lxFill(body) {
  const [code, optText, why] = lxSections(body);
  const { opts } = lxOptions(optText || "");
  const f = lxFrame("fill", "Fill the gap");
  const pre = lxCode(code), gap = dgEl("span", { class: "lx-gap", text: "?" });
  const walker = document.createTreeWalker(pre, NodeFilter.SHOW_TEXT);
  for (let node = walker.nextNode(); node; node = walker.nextNode()) {
    const i = node.data.indexOf("___");
    if (i < 0) continue;
    const after = node.splitText(i);
    after.data = after.data.slice(3);
    after.parentNode.insertBefore(gap, after);
    break;
  }
  const chips = dgEl("div", { class: "lx-chips" });
  lxShuffle(opts.length, body).forEach((k) => {
    const o = opts[k];
    const chip = dgEl("button", { type: "button", class: "lx-chip", text: o.label });
    chip.onclick = async () => {
      if (f.fig.classList.contains("done")) return;
      gap.textContent = o.label;
      gap.className = "lx-gap " + (o.ok ? "right" : "wrong");
      $$(".lx-chip", chips).forEach((c) => c.classList.remove("wrong"));
      if (!o.ok) { chip.classList.add("wrong", "tried"); lxShake(gap); lxSay(f.foot, "bad", o.why); return; }
      chip.classList.add("right");
      $$(".lx-chip", chips).forEach((c) => { if (c !== chip) c.disabled = true; });
      lxPop(gap); f.done();
      const say = lxSay(f.foot, "good", o.why + (why ? "\n\n" + why : ""));
      try { say.prepend(lxOut(await lxRun(code.replace("___", o.label)))); } catch { /* the feedback stands without the output */ }
    };
    chips.append(chip);
  });
  dgAdd(f.body, pre, chips);
  return f.fig;
}

/* ---- order: put shuffled lines into an order that works. Any order that prints the same counts. */
export function lxOrder(body) {
  const [codeText, why] = lxSections(body);
  const lines = codeText.split("\n").filter((l) => l.trim());
  const f = lxFrame("order", "Put the lines in order");
  const list = dgEl("ol", { class: "lx-lines" });
  let target = null, quiet = 0;
  const move = (li, dir) => {
    const other = dir < 0 ? li.previousElementSibling : li.nextElementSibling;
    if (!other || f.fig.classList.contains("done")) return;
    flip(list, () => (dir < 0 ? list.insertBefore(li, other) : list.insertBefore(other, li)));
    quiet = performance.now() + 170;
  };
  lxShuffle(lines.length, body).forEach((k) => {
    const codeEl = dgEl("code", { class: "cm-s-pt" });
    CodeMirror.runMode(lines[k], "python", codeEl);
    const grip = dgEl("span", { class: "lx-grip", "aria-hidden": "true", text: "⋮⋮" });
    const li = dgEl("li", { class: "lx-line", "data-k": k }, grip, codeEl,
      dgEl("span", { class: "lx-nudge" },
        dgEl("button", { type: "button", "aria-label": "Move this line up", text: "↑", onclick: () => { move(li, -1); li.querySelector("button").focus(); } }),
        dgEl("button", { type: "button", "aria-label": "Move this line down", text: "↓", onclick: () => { move(li, 1); li.querySelectorAll("button")[1].focus(); } })));
    grip.addEventListener("pointerdown", (e) => { if (f.fig.classList.contains("done")) return; e.preventDefault(); grip.setPointerCapture(e.pointerId); li.classList.add("drag"); });
    grip.addEventListener("pointermove", (e) => {
      if (!grip.hasPointerCapture(e.pointerId) || performance.now() < quiet) return;
      const prev = li.previousElementSibling, next = li.nextElementSibling;
      if (prev && e.clientY < prev.getBoundingClientRect().top + prev.offsetHeight / 2) move(li, -1);
      else if (next && e.clientY > next.getBoundingClientRect().top + next.offsetHeight / 2) move(li, 1);
    });
    const drop = () => li.classList.remove("drag");
    grip.addEventListener("pointerup", drop); grip.addEventListener("pointercancel", drop);
    list.append(li);
  });
  const go = dgBtn("Check the order", async () => {
    busy(go, true);
    try {
      target ??= lxNorm((await lxRun(lines.join("\n"))).stdout);
      const r = await lxRun([...list.children].map((li) => lines[+li.dataset.k]).join("\n"));
      if (r.returncode === 0 && !r.timed_out && lxNorm(r.stdout) === target) {
        go.remove(); lxPop(list); f.done();
        lxSay(f.foot, "good", "**That order works.** " + why).prepend(lxOut(r));
      } else {
        lxShake(list);
        lxSay(f.foot, "bad", r.returncode !== 0 || r.timed_out ? "Python stopped before the end. Read the last line of the message, move the lines and check again."
          : "It runs, but it does not print what the finished program should. Move the lines and check again.",
          r.returncode === 0 && !r.timed_out ? dgEl("details", { class: "lx-want" }, dgEl("summary", { text: "What should it print?" }), dgEl("pre", { class: "lx-out", text: target })) : null).prepend(lxOut(r, "In this order, Python printed"));
      }
    } catch (err) { toast(err.message, true); }
    busy(go, false);
  }, "primary");
  dgAdd(f.body, dgEl("p", { class: "lx-note", text: "Drag a line by its handle, or use the arrows." }), list, dgEl("div", { class: "lx-row" }, go));
  return f.fig;
}

/* ---- try: a small editor with a goal. The hidden solution only supplies the output to aim for. */
export function lxTry(body) {
  const [starter, goal, solution, why] = lxSections(body);
  const f = lxFrame("try", "Try it");
  const host = dgEl("div", { class: "lx-editor" });
  let target = null, misses = 0;
  const cm = CodeMirror(host, { ...EDITOR_OPTS, value: starter, lineNumbers: false, viewportMargin: Infinity, autofocus: false,
    extraKeys: { ...EDITOR_OPTS.extraKeys, "Ctrl-Enter": () => run(), "Cmd-Enter": () => run() } });
  cm.setSize(null, "auto");
  new IntersectionObserver((entries, io) => { if (entries.some((e) => e.isIntersecting)) { cm.refresh(); io.disconnect(); } }).observe(host);
  const go = dgBtn("Run", () => run(), "primary");
  const reset = dgBtn("Reset", () => { cm.setValue(starter); cm.focus(); }, "ghost");
  async function run() {
    busy(go, true);
    try {
      target ??= lxNorm((await lxRun(solution)).stdout);
      const r = await lxRun(cm.getValue());
      if (r.returncode === 0 && !r.timed_out && lxNorm(r.stdout) === target) {
        lxPop(host); f.done();
        lxSay(f.foot, "good", "**That is it.** " + (why || "")).prepend(lxOut(r));
      } else {
        misses += 1;
        const want = dgEl("details", { class: "lx-want" }, dgEl("summary", { text: "What should it print?" }), dgEl("pre", { class: "lx-out", text: target }));
        lxSay(f.foot, "info", r.returncode !== 0 || r.timed_out ? "Python stopped with an error. The last line of the message says what went wrong." : "It runs. It does not print what the goal asks for yet.",
          misses >= 2 ? want : null).prepend(lxOut(r));
      }
    } catch (err) { toast(err.message, true); }
    busy(go, false);
  }
  dgAdd(f.body, lxMd(goal, "lx-md lx-goal"), host, dgEl("div", { class: "lx-row" }, go, reset, dgEl("span", { class: "lx-note", text: "Ctrl+Enter runs it" })));
  return f.fig;
}

/* ---- match: pair each item on the left with one on the right */
export function lxMatch(body) {
  const [pairText, why] = lxSections(body);
  const pairs = pairText.split("\n").filter((l) => l.includes(" :: ")).map((l) => { const i = l.indexOf(" :: "); return [l.slice(0, i).trim(), l.slice(i + 4).trim()]; });
  const f = lxFrame("match", "Match the pairs");
  const left = dgEl("div", { class: "lx-col" }), right = dgEl("div", { class: "lx-col" });
  let pick = null, matched = 0;
  const mk = (k, side) => {
    const btn = dgEl("button", { type: "button", class: "lx-pair", "data-k": k }, lxHtml(mdInline(pairs[k][side]), "lx-optlabel"));
    btn.onclick = () => {
      if (btn.classList.contains("matched")) return;
      if (!pick || pick.side === side) { pick?.btn.classList.remove("picked"); pick = pick?.btn === btn ? null : { side, k, btn }; pick?.btn.classList.add("picked"); return; }
      const a = pick.btn; pick = null; a.classList.remove("picked");
      if (+a.dataset.k !== k) { lxShake(a); lxShake(btn); lxSay(f.foot, "bad", "Those two do not belong together. Try another pair."); return; }
      [a, btn].forEach((b) => { b.classList.add("matched"); lxPop(b); });
      // line the right-hand item up with its partner
      const r = right.querySelector(`[data-k="${k}"]`), cur = right.children[[...left.children].findIndex((b) => +b.dataset.k === k)];
      if (cur !== r) flip(right, () => { const mark = document.createComment(""); right.replaceChild(mark, r); right.replaceChild(r, cur); right.replaceChild(cur, mark); });
      matched += 1;
      if (matched === pairs.length) { f.done(); lxSay(f.foot, "good", "**All matched.** " + (why || "")); } else dgClear(f.foot);
    };
    return btn;
  };
  pairs.forEach((_, k) => left.append(mk(k, 0)));
  lxShuffle(pairs.length, body).forEach((k) => right.append(mk(k, 1)));
  dgAdd(f.body, dgEl("p", { class: "lx-note", text: "Pick one on the left, then its partner on the right." }), dgEl("div", { class: "lx-cols" }, left, right));
  return f.fig;
}

export const BLOCKS = { quiz: lxQuiz, predict: lxPredict, fill: lxFill, order: lxOrder, try: lxTry, match: lxMatch };

/* Runs after DOMPurify, before highlight(): replace every activity block under root with its widget. */
export function enhanceBlocks(root) {
  for (const [kind, build] of Object.entries(BLOCKS)) {
    $$(`pre > code.language-${kind}`, root).forEach((codeEl) => {
      let widget;
      try { widget = build(codeEl.textContent.replace(/\n+$/, "")); }
      catch (err) { widget = dgEl("div", { class: "dg dg-broken", text: "This activity could not be shown: " + err.message }); }
      codeEl.parentElement.replaceWith(widget);
    });
  }
}

/* A slim bar over the lesson: how far down the page you are, and one dot per activity in it. */
export function lessonTracker(pane, lesson) {
  const acts = $$(".lx", lesson);
  const bar = dgEl("div", { class: "read-track" }, dgEl("i", { class: "read-fill" }),
    acts.length ? dgEl("span", { class: "read-dots", title: "Activities in this lesson" }, acts.map((a, i) => dgEl("button", { type: "button", class: "read-dot", "aria-label": `Go to activity ${i + 1} of ${acts.length}`,
      onclick: () => a.scrollIntoView({ behavior: motionOK() ? "smooth" : "auto", block: "center" }) }))) : null);
  pane.prepend(bar);
  const fill = bar.firstChild, dots = $$(".read-dot", bar);
  const onScroll = () => { const max = pane.scrollHeight - pane.clientHeight; fill.style.transform = `scaleX(${max > 0 ? Math.min(1, pane.scrollTop / max) : 1})`; };
  pane.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
  lesson.addEventListener("lx-done", (e) => {
    const i = acts.indexOf(e.target);
    if (i >= 0) { dots[i].classList.add("on"); lxPop(dots[i]); }
    if (acts.every((a) => a.classList.contains("done"))) { const task = $(".task", pane); if (task && !task.classList.contains("ready")) { task.classList.add("ready"); bar.classList.add("all"); } }
  });
  // activities and diagrams ease in the first time they scroll into view
  if (motionOK()) {
    const io = new IntersectionObserver((entries) => entries.forEach((e) => { if (e.isIntersecting) { e.target.classList.replace("unseen", "seen"); io.unobserve(e.target); } }), { root: pane, threshold: 0.12 });
    $$(".lx, .dg", lesson).forEach((el) => { el.classList.add("unseen"); io.observe(el); });
    cleanup.push(() => io.disconnect());
  }
}

export function renderRich(root) { enhanceDiagrams(root); enhanceBlocks(root); highlight(root); enhanceCode(root); }
