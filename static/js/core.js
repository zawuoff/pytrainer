/* Shared state and helpers used by every module: the cached /api/state, DOM shortcuts, the API
   client, toasts, Markdown and small formatters. */

export const $ = (sel, root = document) => root.querySelector(sel);
export const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
export const main = $("#main");
export let S = null;            // cached /api/state
export let cleanup = [];        // run when leaving a view
let libSeen = null;             // unlocked Library topic ids at the last refreshState, to announce new ones
export let lastInteraction = Date.now(); // the time-on-task clock only runs while you're active
["keydown", "mousedown", "mousemove", "wheel", "touchstart"].forEach((ev) =>
  window.addEventListener(ev, () => { lastInteraction = Date.now(); }, { passive: true }));

export const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

export async function api(path, body) {
  const opts = body === undefined ? {} : {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
  };
  const res = await fetch("/api/" + path, opts);
  let data;
  try { data = await res.json(); } catch { data = { error: `Server returned ${res.status}` }; }
  if (!res.ok) throw new Error(data.error || `Request failed (${res.status})`);
  return data;
}

/* Motion is decoration: every animation started from JS goes through here and is skipped when the
   system asks for reduced motion. */
export const motionOK = () => !matchMedia("(prefers-reduced-motion: reduce)").matches;
export const anim = (el, frames, opts) => (motionOK() && el?.animate ? el.animate(frames, { easing: "cubic-bezier(.2,.8,.2,1)", ...opts }) : null);

/* FLIP: remember where the children are, change the DOM, then slide each child from its old place. */
export function flip(container, mutate, skip) {
  const first = new Map([...container.children].map((el) => [el, el.getBoundingClientRect()]));
  mutate();
  for (const el of container.children) {
    const a = first.get(el), b = el.getBoundingClientRect();
    if (!a || el === skip) continue;
    const dx = a.left - b.left, dy = a.top - b.top;
    if (dx || dy) anim(el, [{ transform: `translate(${dx}px, ${dy}px)` }, { transform: "none" }], { duration: 240 });
  }
}

export function toast(msg, bad = false) {
  let stack = $("#toasts");
  if (!stack) { stack = document.createElement("div"); stack.id = "toasts"; stack.setAttribute("aria-live", "polite"); document.body.appendChild(stack); }
  const t = document.createElement("div");
  t.className = "toast" + (bad ? " bad" : "");
  t.textContent = msg;
  stack.appendChild(t);
  setTimeout(() => {
    const out = anim(t, [{ opacity: 1, transform: "none" }, { opacity: 0, transform: "translateY(8px) scale(.97)" }], { duration: 220, fill: "forwards" });
    if (out) out.onfinish = () => t.remove(); else t.remove();
  }, bad ? 6000 : 3000);
}

marked.setOptions({ gfm: true, breaks: false });
export const md = (text, cls = "prose") => `<div class="${cls}">${DOMPurify.sanitize(marked.parse(text || ""))}</div>`;

export function highlight(root) {
  $$("pre code", root).forEach((el) => {
    if (el.dataset.hl) return;
    const lang = (el.className.match(/language-(\w+)/) || [])[1] || "python";
    if (!["python", "py", ""].includes(lang)) return;
    const text = el.textContent;
    el.innerHTML = "";
    CodeMirror.runMode(text, "python", el);
    el.classList.add("cm-s-pt");
    el.dataset.hl = "1";
  });
}

export const modColor = (id) => `--mc: var(--m-${id || "foundations"})`;
export const diffBars = (d) => `<span class="diff" title="Difficulty ${d} of 3">${[1, 2, 3].map((i) => `<i class="${i <= d ? "on" : ""}"></i>`).join("")}</span>`;
export const ticks = (cells) => `<span class="ticks">${cells.map(([, st]) => `<i class="${st}"></i>`).join("")}</span>`;
export const fmtMin = (m) => m >= 60 ? `${Math.floor(m / 60)}h ${m % 60}m` : `${m}m`;
export const fmtDate = (s) => s ? new Date(s).toLocaleString([], { dateStyle: "medium", timeStyle: "short" }) : "";
export const aiOn = () => S && S.settings.ai.provider !== "none";
export const aiName = () => ({ claude: "Claude Code", codex: "Codex", opencode: "OpenCode" }[S?.settings.ai.provider] || "AI");
export const moduleOf = (id) => S.modules.find((m) => m.id === id);
export const topicOf = (id) => S.topics.find((t) => t.id === id);

export function busy(btn, on, label) {
  if (!btn) return;
  if (on) { btn.dataset.label = btn.innerHTML; btn.innerHTML = `<span class="spin"></span> ${label || ""}`; btn.disabled = true; }
  else { btn.innerHTML = btn.dataset.label || btn.innerHTML; btn.disabled = false; }
}
export const noAI = (what) => `<div class="note">${what} needs an AI connection. <a href="#/settings">Connect Claude Code, Codex or OpenCode in Settings</a>.</div>`;

export function stepKind(e) {
  if (e.mode === "predict") return "Read & predict";
  if (e.mode === "tests") return "Write the tests";
  if (e.difficulty <= 1) return "Lesson + exercise";
  return e.difficulty === 3 ? "Checkpoint" : "Practice";
}

/* Run and forget the cleanup callbacks of the view being left. */
export function runCleanup() {
  cleanup.forEach((fn) => { try { fn(); } catch {} });
  cleanup = [];
}

/* Forget the cached state, so the next route reloads it (after erasing progress). */
export function resetState() { S = null; }

export async function refreshState() {
  S = await api("state");
  const due = S.summary.reviews_due;
  const b = $("#review-badge");
  b.textContent = due; b.classList.toggle("hidden", !due);
  const lc = $("#lib-count");
  if (lc) lc.textContent = `${S.library.unlocked}/${S.library.total}`;
  const got = S.topics.filter((t) => t.library_unlocked);
  if (libSeen) got.filter((t) => !libSeen.has(t.id)).forEach((t) => toast(`Library: ${t.title} unlocked (${S.library.unlocked} of ${S.library.total})`));
  libSeen = new Set(got.map((t) => t.id));
  $("#ai-status").innerHTML = aiOn() ? `AI: ${esc(aiName())}${S.settings.ai.model ? " · " + esc(S.settings.ai.model) : ""}` : `AI: not connected`;
  $("#rail-course").innerHTML = `<div class="lbl">Your course</div>` + S.modules.map((m) => {
    const pct = m.steps_total ? Math.round((m.steps_done / m.steps_total) * 100) : 0;
    return `<a class="rail-mod" style="${modColor(m.id)}" href="#/course/${m.id}" title="${esc(m.title)}: ${pct}%">
      <span class="n">${m.number}</span><span>${esc(m.title)}<div class="rb"><i style="width:${m.complete ? 100 : pct}%"></i></div></span></a>`;
  }).join("");
  return S;
}
