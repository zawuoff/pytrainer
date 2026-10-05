import { $, $$, S, anim, api, cleanup, esc, highlight, main, md, modColor, refreshState } from "./core.js";
import { dgEl } from "./diagrams.js";
import { renderRich } from "./blocks.js";
import { isNarrow } from "./workspace.js";

/* ---------------------------------------------------------------- library
   A search engine over the reference cards of the chapters you've finished. A chapter joins once
   its lesson steps are solved (or you tested out of it). Locked chapters never reach the page: the
   server sends only what's unlocked, plus personal signals (what you opened lately, what you've been
   practising and failing, what the chapter you're on builds on) that lift the results you most
   likely want. Anything unlocked can still be found by searching for it.
   The same Library is a page (#/library) and a panel inside every workspace (Ctrl+K). */

export let LIB = null;                 // last /api/library payload
export let libHere = null;             // topic id of the exercise on screen, if any
export const libState = { q: "", open: new Set(), shown: new Set() };

export const libWords = (q) => q.toLowerCase().split(/[\s,]+/).filter(Boolean);
const tokens = (text) => String(text ?? "").toLowerCase().match(/[a-z0-9_]+|[^\sa-z0-9_]/g) || [];

/* esc(text) with every occurrence of a search word wrapped in <mark>. */
export function libMark(text, words) {
  text = String(text ?? "");
  if (!words.length) return esc(text);
  const low = text.toLowerCase(), on = new Array(text.length).fill(false);
  for (const w of words) for (let i = low.indexOf(w); i >= 0; i = low.indexOf(w, i + 1)) on.fill(true, i, i + w.length);
  let out = "", i = 0;
  while (i < text.length) {
    let j = i;
    while (j < text.length && on[j] === on[i]) j++;
    out += on[i] ? `<mark>${esc(text.slice(i, j))}</mark>` : esc(text.slice(i, j));
    i = j;
  }
  return out;
}

/* One edit (insert, delete, substitute or swap two neighbours) apart: catches most typos. */
function oneEdit(a, b) {
  if (Math.abs(a.length - b.length) > 1 || a === b) return a === b;
  let i = 0;
  while (i < a.length && i < b.length && a[i] === b[i]) i++;
  if (a.length === b.length) return a.slice(i + 1) === b.slice(i + 1) || (a[i] === b[i + 1] && a[i + 1] === b[i] && a.slice(i + 2) === b.slice(i + 2));
  return a.length > b.length ? a.slice(i + 1) === b.slice(i) : a.slice(i) === b.slice(i + 1);
}

/* How well one word matches one field's tokens: exact, prefix, inside, or one typo away. */
function wordScore(w, toks, text) {
  let best = 0;
  for (const t of toks) {
    if (t === w) return 1;
    if (t.startsWith(w)) best = Math.max(best, 0.8);
    else if (w.length >= 4 && oneEdit(w, t)) best = Math.max(best, 0.45);
  }
  if (!best && w.length >= 2 && text.includes(w)) best = 0.5;
  return best;
}

// A word found on the card itself counts fully; one found only on its chapter (title, keywords...)
// counts for less, so the card that is actually about the word comes first.
const CARD_FIELDS = [["syntax", 6], ["explain", 3], ["example", 1.5]];
const CHAPTER_FIELDS = [["title", 4], ["keywords", 4], ["concepts", 3], ["summary", 1]];
const CHAPTER_SHARE = 0.6;

/* Every card of every unlocked chapter, with its searchable fields prepared once per payload. */
function index(lib) {
  if (lib._index) return lib._index;
  const docs = [];
  for (const e of lib.entries) {
    e.cards.forEach((c, i) => {
      const f = { syntax: c.syntax, title: e.title, keywords: e.keywords.join(" "), concepts: e.concepts.join(" "),
                  explain: c.explain, example: c.example, summary: e.summary };
      docs.push({ e, c, i, f: Object.fromEntries(Object.entries(f).map(([k, v]) => [k, { text: v.toLowerCase(), toks: tokens(v) }])) });
    });
  }
  lib._index = docs;
  return docs;
}

const recentKey = (id, i) => `${id}#${i}`;

/* Everyday names for syntax the cards show but don't spell out: searching "slice" should find
   items[start:stop] even though that card never says the word. */
const ALIASES = {
  slice: ["start:stop", "[:", ":]"], slicing: ["start:stop", "[:", ":]"],
  fstring: ['f"', "f'"], "f-string": ['f"', "f'"],
  comprehension: [" for ", "comprehension"], ternary: [" if ", " else "], walrus: [":="],
  unpack: ["*args", "**", ", *"], unpacking: ["*args", "**", ", *"], kwargs: ["**kwargs", "**"],
  truthy: ["if not", "bool("], falsy: ["if not", "bool("], decorator: ["@"], docstring: ['"""'],
};
const aliasHit = (w, d) => (ALIASES[w] || []).some((a) => d.f.syntax.text.includes(a) || d.f.example.text.includes(a));

/* Ranked cards for a query: every word has to match somewhere on the card or its chapter, the
   closer the match the better, and what you've been working with lately counts on top. */
export function libSearch(lib, q) {
  const words = libWords(q), boost = lib.boost || {}, recent = new Set((lib.recent || []).map((r) => recentKey(r.id, r.card)));
  if (!words.length) return { words, hits: [] };
  const hits = [];
  for (const d of index(lib)) {
    let score = 0;
    for (const w of words) {
      const best = (fields) => Math.max(...fields.map(([name, weight]) => weight * wordScore(w, d.f[name].toks, d.f[name].text)));
      const s = Math.max(best(CARD_FIELDS), aliasHit(w, d) ? 5 : 0) + CHAPTER_SHARE * best(CHAPTER_FIELDS);
      if (!s) { score = 0; break; }
      score += s;
    }
    if (!score) continue;
    score *= 1 + 0.6 * (boost[d.e.id] || 0);
    if (d.e.id === libHere) score += 2;
    if (recent.has(recentKey(d.e.id, d.i))) score += 1;
    hits.push({ ...d, score });
  }
  hits.sort((a, b) => b.score - a.score || a.e.number - b.e.number || a.i - b.i);
  return { words, hits };
}

/* "Did you mean": the closest words from your Library's chapters when nothing matched. */
function suggestions(lib, q) {
  const vocab = new Set();
  for (const e of lib.entries) for (const t of tokens([e.title, ...e.keywords, ...e.concepts].join(" "))) if (t.length > 2) vocab.add(t);
  const out = [];
  for (const w of libWords(q)) for (const t of vocab) if (t !== w && (oneEdit(w, t) || (w.length >= 3 && t.startsWith(w.slice(0, 3))))) out.push(t);
  return [...new Set(out)].slice(0, 6);
}

/* For an empty search box: cards from the chapters you're most likely to need right now. */
function forYou(lib) {
  const boost = lib.boost || {}, byId = new Map(lib.entries.map((e) => [e.id, e]));
  const ranked = lib.entries.map((e) => [e, (boost[e.id] || 0) + (e.id === libHere ? 2 : 0)]).filter(([, s]) => s > 0)
    .sort((a, b) => b[1] - a[1]).map(([e]) => e);
  const picks = [], seen = new Set();
  for (const r of lib.recent || []) {
    const e = byId.get(r.id);
    if (e && r.card != null && e.cards[r.card] && !seen.has(recentKey(r.id, r.card))) { seen.add(recentKey(r.id, r.card)); picks.push({ e, c: e.cards[r.card], i: r.card, why: "opened recently" }); }
    if (picks.length >= 3) break;
  }
  for (const e of ranked) {
    const why = e.id === libHere ? "this chapter" : (lib.working_on || []).includes(e.id) ? "you're practising this" : "related to your recent work";
    let n = 0;
    e.cards.forEach((c, i) => { if (n < 2 && !seen.has(recentKey(e.id, i))) { seen.add(recentKey(e.id, i)); picks.push({ e, c, i, why }); n++; } });
    if (picks.length >= 8) break;
  }
  return picks.slice(0, 8);
}

function cardHTML({ e, c, i, why }, words, panel) {
  const key = recentKey(e.id, i), open = libState.shown.has(key);
  return `<article class="lib-hit ${open ? "open" : ""}" style="${modColor(e.module)}" data-id="${esc(e.id)}" data-card="${i}">
    <button type="button" class="lib-hit-head" aria-expanded="${open}">
      <span class="lib-crumb">${libMark(e.title, words)}${why ? ` · <em>${esc(why)}</em>` : ""}</span>
      <code class="lib-syn">${libMark(c.syntax, words)}</code>
      <span class="lib-explain">${libMark(c.explain, words)}</span></button>
    ${open ? `<div class="lib-hit-in"><pre><code class="language-python">${esc(c.example)}</code></pre>
      ${panel ? "" : `<a class="lib-more" href="#/chapter/${esc(e.id)}?notes">Chapter notes</a>`}</div>` : ""}
  </article>`;
}

export function libEntryHTML(e, words, open, panel) {
  return `<article class="lib-entry ${open ? "open" : ""}" style="${modColor(e.module)}" data-id="${esc(e.id)}">
    <button type="button" class="lib-head" aria-expanded="${open}"><span class="lib-num">${String(e.number).padStart(2, "0")}</span>
      <span class="lib-title"><b>${libMark(e.title, words)}</b><span class="lib-sum">${libMark(e.summary, words)}</span></span>
      ${e.id === libHere ? `<span class="pill warn">this chapter</span>` : ""}<span class="lib-caret" aria-hidden="true"></span></button>
    ${open ? `<div class="lib-in">
      <div class="lib-tags">${e.concepts.map((c) => `<span>${libMark(c, words)}</span>`).join("")}</div>
      <div class="lib-cards">${e.cards.map((c) => `<div class="lib-card"><code class="lib-syn">${libMark(c.syntax, words)}</code>
        <p>${libMark(c.explain, words)}</p><pre><code class="language-python">${esc(c.example)}</code></pre></div>`).join("")}</div>
      ${panel ? "" : `<div class="lib-foot"><a class="btn small ghost" href="#/chapter/${esc(e.id)}?notes">Open the chapter notes</a></div>`}</div>` : ""}
  </article>`;
}

const remember = (id, card = null) => api(`library/${id}/open`, { card }).catch(() => {});

/* Draw the results (or, with an empty box, suggestions and the chapters to browse) into `body`. */
export function libDraw(body, lib, { panel = false } = {}) {
  const st = libState, q = st.q.trim();
  let h = "";
  if (!lib.unlocked) {
    h = `<div class="note">Your Library is empty so far. Finish the lesson steps of a chapter and its reference cards are added here${panel ? "." : `. <a href="#/course">Go to the course</a>.`}</div>`;
  } else if (q) {
    const { words, hits } = libSearch(lib, q);
    if (hits.length) {
      h += `<p class="lib-status" role="status">${hits.length} card${hits.length === 1 ? "" : "s"} for "${esc(q)}"${hits.length > 30 ? ", best 30 shown" : ""}</p>`;
      h += hits.slice(0, 30).map((d) => cardHTML(d, words, panel)).join("");
    } else {
      const alt = suggestions(lib, q);
      h += `<p class="lib-status" role="status">Nothing in your Library matches "${esc(q)}".</p>
        ${alt.length ? `<p class="lib-alt">Try: ${alt.map((w) => `<button type="button" class="lib-try" data-q="${esc(w)}">${esc(w)}</button>`).join(" ")}</p>` : ""}
        <p class="faint small">The Library holds the chapters you've finished (${lib.unlocked} of ${lib.total}). Finish more chapters to search them too.</p>`;
    }
  } else {
    const picks = forYou(lib);
    if (picks.length) h += `<section class="lib-mod lib-foryou"><h2><span>For you</span><small>from what you've opened and practised</small></h2>${picks.map((d) => cardHTML(d, [], panel)).join("")}</section>`;
    for (const m of lib.modules) {
      const rows = lib.entries.filter((e) => e.module === m.id);
      if (!rows.length) continue;
      h += `<section class="lib-mod" style="${modColor(m.id)}"><h2><span>${esc(m.title)}</span><small>${rows.length} chapter${rows.length === 1 ? "" : "s"}</small></h2>
        ${rows.map((e) => libEntryHTML(e, [], st.open.has(e.id), panel)).join("")}</section>`;
    }
  }
  body.innerHTML = h;
  highlight(body);
  $$(".lib-hit", body).forEach((el) => {
    const id = el.dataset.id, card = +el.dataset.card, key = recentKey(id, card);
    $(".lib-hit-head", el).onclick = () => {
      const was = st.shown.has(key);
      if (was) st.shown.delete(key); else { st.shown.add(key); remember(id, card); }
      libDraw(body, lib, { panel });
      const now = $(`.lib-hit[data-id="${id}"][data-card="${card}"]`, body);
      $(".lib-hit-head", now)?.focus();
      if (!was) anim($(".lib-hit-in", now), [{ opacity: 0, transform: "translateY(-6px)" }, { opacity: 1, transform: "none" }], { duration: 200 });
    };
  });
  $$(".lib-entry", body).forEach((el) => {
    const id = el.dataset.id;
    $(".lib-head", el).onclick = () => {
      const was = st.open.has(id);
      if (was) st.open.delete(id); else { st.open.add(id); remember(id); }
      libDraw(body, lib, { panel });
      const now = $(`.lib-entry[data-id="${id}"]`, body);
      $(".lib-head", now)?.focus();
      if (!was) anim($(".lib-in", now), [{ opacity: 0, transform: "translateY(-8px)" }, { opacity: 1, transform: "none" }], { duration: 240 });
    };
  });
  $$(".lib-try", body).forEach((b) => b.onclick = () => {
    st.q = b.dataset.q;
    const input = body.parentElement.querySelector("input[role=searchbox]") || $("#lib-q");
    if (input) input.value = st.q;
    libDraw(body, lib, { panel });
  });
}

export const libCountHTML = (lib) => `<div class="lib-count"><b>${lib.unlocked}</b> of ${lib.total} chapters</div>
  <div class="lib-bar" role="img" aria-label="${lib.unlocked} of ${lib.total} chapters in your Library"><i style="width:${Math.round((lib.unlocked / lib.total) * 100)}%"></i></div>`;

export function libSearchBox(input, body, lib, opts) {
  input.value = libState.q;
  input.oninput = () => { libState.q = input.value; libState.shown.clear(); libDraw(body, lib, opts); };
  input.onkeydown = (e) => {
    if (e.key === "Enter") { e.preventDefault(); $(".lib-hit-head", body)?.click(); }
    else if (e.key === "Escape" && input.value) { e.preventDefault(); e.stopPropagation(); input.value = ""; input.oninput(); }
  };
}

export async function viewLibrary() {
  await refreshState();
  const lib = LIB = await api("library");
  main.innerHTML = `<div class="page lib-page">
    <div class="lib-top"><div><h1>Library</h1>
      <p class="dim" style="margin:10px 0 0;max-width:62ch">Search the reference cards of every chapter you've finished: the key syntax, what it does, and a tiny example. Results you've opened and topics you're practising come first, and you can still find anything else in your Library by searching for it. Inside an exercise, press <kbd>Ctrl+K</kbd>.</p></div>
      <div class="lib-meter">${libCountHTML(lib)}</div></div>
    <div class="lib-search"><input type="text" id="lib-q" role="searchbox" aria-label="Search the Library" autocomplete="off" spellcheck="false" placeholder="Search anything you've learned: slice, KeyError, sorted key, f-string"></div>
    <div id="lib-body" class="lib-body"></div></div>`;
  const body = $("#lib-body"), input = $("#lib-q");
  libSearchBox(input, body, lib, {});
  libDraw(body, lib, {});
  if (!matchMedia("(pointer: coarse)").matches) input.focus();
}

/* ---- the Library inside a workspace
   One <aside> per workspace. It lives in the bottom dock as a tab, or is moved (the same element,
   so search text and open entries survive) into the workspace grid as a column on the left or
   right. The choice and the width are remembered. On a phone it is always a dock tab. */
export const LIB_ICON = {
  left: `<svg viewBox="0 0 18 14" width="18" height="14" aria-hidden="true"><rect x=".75" y=".75" width="16.5" height="12.5" rx="2.5" fill="none" stroke="currentColor" stroke-width="1.5"/><rect x="2.5" y="2.5" width="4.5" height="9" rx="1" fill="currentColor"/></svg>`,
  bottom: `<svg viewBox="0 0 18 14" width="18" height="14" aria-hidden="true"><rect x=".75" y=".75" width="16.5" height="12.5" rx="2.5" fill="none" stroke="currentColor" stroke-width="1.5"/><rect x="2.5" y="7.5" width="13" height="4" rx="1" fill="currentColor"/></svg>`,
  right: `<svg viewBox="0 0 18 14" width="18" height="14" aria-hidden="true"><rect x=".75" y=".75" width="16.5" height="12.5" rx="2.5" fill="none" stroke="currentColor" stroke-width="1.5"/><rect x="11" y="2.5" width="4.5" height="9" rx="1" fill="currentColor"/></svg>`,
  close: `<svg viewBox="0 0 14 14" width="12" height="12" aria-hidden="true"><path d="M2 2l10 10M12 2L2 12" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>`,
};
export const libPrefs = (() => {
  const d = { pos: "bottom", open: true, w: 380 };
  try { return { ...d, ...JSON.parse(localStorage.getItem("pt-lib") || "{}") }; } catch { return d; }
})();
export const saveLibPrefs = () => { try { localStorage.setItem("pt-lib", JSON.stringify(libPrefs)); } catch {} };
export let wsLib = null;               // the Library of the workspace on screen, if any (Ctrl+K talks to it)

/* ws: the .ws grid. dock: its bottom dock. topic: chapter id of the step, if it has one (adds the
   chapter-notes view). onPlace(pos): the view redraws its dock tabs. selectTab(): the view shows the
   Library tab. editor: where the cursor goes back to. */
export function mountLibrary(ws, dock, { topic = null, onPlace, selectTab, editor } = {}) {
  const panel = document.createElement("aside");
  panel.className = "ws-lib";
  panel.setAttribute("aria-label", "Library");
  panel.innerHTML = `<div class="ws-lib-grip" title="Drag to resize"></div><div class="ws-lib-in">
    <div class="ws-lib-top"><h2>Library</h2><span class="lib-dcount"></span>
      ${topic ? `<div class="lib-modes" role="tablist"><button type="button" data-m="cards" class="on" role="tab">Cards</button><button type="button" data-m="notes" role="tab">Chapter notes</button></div>` : ""}
      <span class="grow"></span>
      <div class="lib-pos" role="group" aria-label="Where the Library sits">
        <button type="button" data-pos="left" title="Dock the Library on the left" aria-label="Dock on the left">${LIB_ICON.left}</button>
        <button type="button" data-pos="bottom" title="Keep the Library as a tab under the editor" aria-label="Tab under the editor">${LIB_ICON.bottom}</button>
        <button type="button" data-pos="right" title="Dock the Library on the right" aria-label="Dock on the right">${LIB_ICON.right}</button></div>
      <button type="button" class="lib-x" title="Close the panel (Esc)" aria-label="Close the Library panel">${LIB_ICON.close}</button><i class="lib-break"></i></div>
    <div class="lib-search"><input type="text" role="searchbox" aria-label="Search the Library" autocomplete="off" spellcheck="false" placeholder="Search: slice, KeyError, sorted"></div>
    <div class="lib-body"><p class="dim"><span class="spin"></span> Loading</p></div></div>`;
  const input = $(".lib-search input", panel), body = $(".lib-body", panel);
  const dockLib = dgEl("div", { class: "dock-lib" });
  dock.append(dockLib);
  let mode = "cards", notes = null, loaded = false, chose = false;
  const pos = () => (isNarrow() ? "bottom" : libPrefs.pos);

  function draw(lib) {
    $(".lib-dcount", panel).textContent = `${lib.unlocked} of ${lib.total} chapters`;
    if (mode !== "cards") return;
    libSearchBox(input, body, lib, { panel: true });
    libDraw(body, lib, { panel: true });
  }
  async function load() {
    if (LIB) draw(LIB);
    try {
      LIB = await api("library"); loaded = true;
      if (!panel.isConnected) return;
      if (topic && !chose && mode === "cards" && !LIB.entries.some((e) => e.id === topic)) return setMode("notes");
      draw(LIB);
    }
    catch (err) { if (!LIB && panel.isConnected) body.innerHTML = `<div class="errbox">${esc(err.message)}</div>`; }
  }
  async function setMode(m) {
    mode = m;
    $$(".lib-modes button", panel).forEach((b) => { b.classList.toggle("on", b.dataset.m === m); b.setAttribute("aria-selected", b.dataset.m === m); });
    panel.classList.toggle("notes", m === "notes");
    if (m === "cards") { if (LIB) draw(LIB); else load(); }
    else {
      body.innerHTML = `<p class="dim"><span class="spin"></span> Loading</p>`;
      try { notes ??= (await api("topic/" + topic)).topic.lesson; } catch (err) { body.innerHTML = `<div class="errbox">${esc(err.message)}</div>`; return; }
      if (mode !== "notes") return;
      body.innerHTML = notes ? md(notes, "lesson lib-notes") : `<p class="dim">This chapter has no notes.</p>`;
      renderRich(body);
    }
    anim(body, [{ opacity: 0 }, { opacity: 1 }], { duration: 180 });
  }
  function place() {
    const p = pos();
    $$(".lib-pos button", panel).forEach((b) => { b.classList.toggle("on", b.dataset.pos === p); b.setAttribute("aria-pressed", b.dataset.pos === p); });
    if (p === "bottom") { dockLib.append(panel); delete ws.dataset.lib; ws.classList.remove("lib-open"); panel.inert = false; }
    else {
      ws.append(panel);
      ws.dataset.lib = p;
      ws.style.setProperty("--libw", libPrefs.w + "px");
      // let the browser see the closed column first, so opening is a transition and not a jump
      requestAnimationFrame(() => { ws.classList.toggle("lib-open", libPrefs.open); panel.inert = !libPrefs.open; });
    }
    onPlace?.(p);
  }
  const focusSearch = () => { if (mode === "cards") { input.focus(); input.select(); } else body.focus?.(); };
  const api_ = {
    panel,
    get pos() { return pos(); },
    get tabOn() { return dock.classList.contains("lib-on"); },
    /* called by the view when its Library tab is switched on or off */
    tab(on) { dock.classList.toggle("lib-on", on); if (on && !loaded) load(); },
    show() {
      if (pos() === "bottom") selectTab?.();
      else { libPrefs.open = true; saveLibPrefs(); ws.classList.add("lib-open"); panel.inert = false; }
      if (!loaded) load();
      setTimeout(focusSearch, 0);
    },
    hide() {
      if (pos() !== "bottom") { libPrefs.open = false; saveLibPrefs(); ws.classList.remove("lib-open"); panel.inert = true; }
      editor?.focus();
    },
    get visible() { return pos() === "bottom" ? dock.classList.contains("lib-on") : libPrefs.open; },
    toggle() { if (api_.visible && panel.contains(document.activeElement)) api_.hide(); else if (api_.visible && pos() !== "bottom") api_.hide(); else api_.show(); },
  };
  $$(".lib-pos button", panel).forEach((b) => b.onclick = () => {
    libPrefs.pos = b.dataset.pos; libPrefs.open = true; saveLibPrefs();
    place();
    if (libPrefs.pos === "bottom") selectTab?.();
    if (!loaded) load();
  });
  $(".lib-x", panel).onclick = () => api_.hide();
  $$(".lib-modes button", panel).forEach((b) => b.onclick = () => { chose = true; setMode(b.dataset.m); });
  const grip = $(".ws-lib-grip", panel);
  grip.onpointerdown = (e) => {
    e.preventDefault();
    grip.setPointerCapture(e.pointerId);
    ws.classList.add("resizing");
    const x0 = e.clientX, w0 = libPrefs.w, dir = pos() === "left" ? 1 : -1;
    grip.onpointermove = (ev) => { libPrefs.w = Math.round(Math.min(620, Math.max(280, w0 + dir * (ev.clientX - x0)))); ws.style.setProperty("--libw", libPrefs.w + "px"); };
    grip.onpointerup = grip.onpointercancel = () => { grip.onpointermove = null; ws.classList.remove("resizing"); saveLibPrefs(); };
  };
  const mq = matchMedia("(max-width: 960px)");
  mq.addEventListener("change", place);
  cleanup.push(() => { mq.removeEventListener("change", place); if (wsLib === api_) wsLib = null; libHere = null; });
  libHere = topic;
  wsLib = api_;
  place();
  if (pos() !== "bottom" && libPrefs.open) load();
  return api_;
}

document.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && !e.altKey && !e.shiftKey && e.key.toLowerCase() === "k") {
    if (!S?.settings.onboarded) return;
    e.preventDefault();
    if (/^#\/library/.test(location.hash)) { $("#lib-q")?.focus(); $("#lib-q")?.select(); }
    else if (wsLib) { if (wsLib.visible && wsLib.panel.contains(document.activeElement)) wsLib.hide(); else wsLib.show(); }
    else location.hash = "#/library";
  } else if (e.key === "Escape" && wsLib?.panel.contains(document.activeElement)) { e.preventDefault(); wsLib.hide(); }
});

/* Placement questions and projects have a dock with one fixed pane (Output). Give it a Library tab. */
export function dockLibrary(ws, dock, opts = {}) {
  const tabs = $(".dock-tabs", dock), mainBtn = $("button", tabs);
  const libBtn = dgEl("button", { type: "button", text: "Library" });
  mainBtn.after(libBtn);
  let lib = null;
  const set = (t) => {
    mainBtn.classList.toggle("on", t !== "library"); libBtn.classList.toggle("on", t === "library");
    lib?.tab(t === "library");
    tabIndicator(tabs);
    if (t === "library") anim(lib.panel, [{ opacity: 0, transform: "translateY(5px)" }, { opacity: 1, transform: "none" }], { duration: 200 });
  };
  lib = mountLibrary(ws, dock, { ...opts,
    onPlace: (pos) => { libBtn.classList.toggle("hidden", pos !== "bottom"); if (pos !== "bottom") set("main"); else tabIndicator(tabs); },
    selectTab: () => { set("library"); opts.selectTab?.(); } });
  mainBtn.onclick = () => set("main");
  libBtn.onclick = () => set("library");
  libBtn.classList.toggle("hidden", lib.pos !== "bottom");
  tabIndicator(tabs);
  return lib;
}

/* The underline of a tab strip slides to the tab that is on. */
export function tabIndicator(tabs) {
  const on = $("button.on", tabs);
  tabs.classList.add("has-ind");
  tabs.style.setProperty("--ind-x", (on ? on.offsetLeft : 0) + "px");
  tabs.style.setProperty("--ind-w", (on ? on.offsetWidth : 0) + "px");
}
