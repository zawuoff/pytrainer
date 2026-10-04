import { $, $$, S, anim, api, cleanup, esc, highlight, main, md, modColor, refreshState } from "./core.js";
import { dgEl } from "./diagrams.js";
import { renderRich } from "./blocks.js";
import { isNarrow } from "./workspace.js";

/* ---------------------------------------------------------------- library
   Reference cards for the chapters whose lesson is finished. The same list is drawn as a page
   (#/library) and inside every workspace (step, module test, placement question, project), where
   it is part of the screen instead of something laid over it: a tab of the bottom dock, or a
   panel docked on the left or the right. Locked chapters arrive from the server as a title only:
   there is nothing locked in the page to reveal. */

export let LIB = null;                 // last /api/library payload
export let libHere = null;             // topic id of the exercise on screen, if any
export const libState = { q: "", open: new Set(), shut: new Set() };
export const LOCK_SVG = `<svg class="lib-lock" viewBox="0 0 16 16" width="13" height="13" aria-hidden="true"><path d="M4.5 7V5a3.5 3.5 0 0 1 7 0v2" fill="none" stroke="currentColor" stroke-width="1.6"/><rect x="3" y="7" width="10" height="7" rx="1.6" fill="currentColor"/></svg>`;

export const libWords = (q) => q.toLowerCase().split(/\s+/).filter(Boolean);
export const libHas = (text, words) => { const t = text.toLowerCase(); return words.every((w) => t.includes(w)); };

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

/* Unlocked entries that contain every search word, best match first. An entry found only
   through its cards shows just the matching cards. Locked chapters can match by title only. */
export function libSearch(lib, q) {
  const words = libWords(q), hits = [];
  for (const e of lib.entries.filter((x) => x.unlocked)) {
    const names = [...e.keywords, ...e.concepts].join(" ");
    const cardText = (c) => [c.syntax, c.explain, c.example].join(" ");
    const rank = libHas(e.title, words) ? 0 : libHas(e.title + " " + names, words) ? 1 : libHas(e.title + " " + names + " " + e.summary, words) ? 2 : 3;
    const cards = e.cards.filter((c) => libHas(cardText(c), words));
    if (rank === 3 && !cards.length && !libHas([e.title, names, e.summary, ...e.cards.map(cardText)].join(" "), words)) continue;
    hits.push({ e, rank, cards: rank === 3 && cards.length ? cards : e.cards });
  }
  hits.sort((a, b) => a.rank - b.rank || a.e.number - b.e.number);
  return { words, hits, locked: lib.entries.filter((x) => !x.unlocked && libHas(x.title, words)) };
}

export function libEntryHTML(e, cards, words, open, panel) {
  const hidden = e.cards.length - cards.length;
  return `<article class="lib-entry ${open ? "open" : ""}" style="${modColor(e.module)}" data-id="${esc(e.id)}">
    <button type="button" class="lib-head" aria-expanded="${open}"><span class="lib-num">${String(e.number).padStart(2, "0")}</span>
      <span class="lib-title"><b>${libMark(e.title, words)}</b><span class="lib-sum">${libMark(e.summary, words)}</span></span>
      ${e.id === libHere ? `<span class="pill warn">this chapter</span>` : ""}<span class="lib-caret" aria-hidden="true"></span></button>
    ${open ? `<div class="lib-in">
      <div class="lib-tags">${e.concepts.map((c) => `<span>${libMark(c, words)}</span>`).join("")}</div>
      <div class="lib-cards">${cards.map((c) => `<div class="lib-card"><code class="lib-syn">${libMark(c.syntax, words)}</code>
        <p>${libMark(c.explain, words)}</p><pre><code class="language-python">${esc(c.example)}</code></pre></div>`).join("")}</div>
      <div class="lib-foot">${hidden > 0 ? `<button type="button" class="btn small ghost lib-all">Show all ${e.cards.length} cards</button>` : ""}
        ${panel ? "" : `<a class="btn small ghost" href="#/chapter/${esc(e.id)}?notes">Open the chapter notes</a>`}</div></div>` : ""}
  </article>`;
}

export const libLockedHTML = (e, panel) => `<div class="lib-entry locked" style="${modColor(e.module)}"><div class="lib-head">
  <span class="lib-num">${String(e.number).padStart(2, "0")}</span><span class="lib-title"><b>${esc(e.title)}</b></span>
  <span class="lib-why">${LOCK_SVG} ${panel ? "locked" : `<a href="#/chapter/${esc(e.id)}">Finish the chapter</a> to unlock`}</span></div></div>`;

/* Draw the list (or the search results) into `body`. Only this part is redrawn while typing. */
export function libDraw(body, lib, { panel = false } = {}) {
  const st = libState, q = st.q.trim();
  const { words, hits, locked } = libSearch(lib, q);
  const isOpen = (id) => q ? !st.shut.has(id) : st.open.has(id);
  const full = new Set(st.full || []);
  let h = "";
  if (!lib.unlocked) {
    h += `<div class="note">Your Library is empty so far. Work through a chapter's steps and its reference card is added here${panel ? "." : `. <a href="#/course">Go to the course</a>.`}</div>`;
  }
  if (q) {
    h += `<p class="lib-status" role="status">${hits.length ? `${hits.length} unlocked ${hits.length === 1 ? "entry matches" : "entries match"}` : "No unlocked entry matches"} "${esc(q)}".</p>`;
    h += hits.map(({ e, cards }) => libEntryHTML(e, full.has(e.id) ? e.cards : cards, words, isOpen(e.id), panel)).join("");
    if (locked.length) h += `<p class="lib-status">${LOCK_SVG} ${locked.length === 1 ? "One locked chapter has" : `${locked.length} locked chapters have`} a matching title:</p>` + locked.map((e) => libLockedHTML(e, panel)).join("");
  } else {
    for (const m of lib.modules) {
      const rows = lib.entries.filter((e) => e.module === m.id);
      if (!rows.length) continue;
      const got = rows.filter((e) => e.unlocked).length;
      h += `<section class="lib-mod" style="${modColor(m.id)}"><h2><span>${esc(m.title)}</span><small>${got} of ${rows.length}</small></h2>
        ${rows.map((e) => e.unlocked ? libEntryHTML(e, e.cards, words, isOpen(e.id), panel) : libLockedHTML(e, panel)).join("")}</section>`;
    }
  }
  body.innerHTML = h;
  highlight(body);
  $$(".lib-entry:not(.locked)", body).forEach((el) => {
    const id = el.dataset.id;
    $(".lib-head", el).onclick = () => {
      const set = q ? st.shut : st.open, was = isOpen(id);
      if (q ? was : !was) set.add(id); else set.delete(id);
      libDraw(body, lib, { panel });
      const now = $(`.lib-entry[data-id="${id}"]`, body);
      $(".lib-head", now)?.focus();
      if (!was) anim($(".lib-in", now), [{ opacity: 0, transform: "translateY(-8px)" }, { opacity: 1, transform: "none" }], { duration: 240 });
    };
    $(".lib-all", el)?.addEventListener("click", () => { st.full = [...full, id]; libDraw(body, lib, { panel }); });
  });
}

export const libCountHTML = (lib) => `<div class="lib-count"><b>${lib.unlocked}</b> of ${lib.total} unlocked</div>
  <div class="lib-ticks" role="img" aria-label="${lib.unlocked} of ${lib.total} chapters unlocked">${lib.entries.map((e) =>
    `<i class="${e.unlocked ? "on" : ""}" style="${modColor(e.module)}" title="${esc(e.title)}: ${e.unlocked ? "unlocked" : "locked"}"></i>`).join("")}</div>`;

export function libSearchBox(input, body, lib, opts) {
  input.value = libState.q;
  input.oninput = () => { libState.q = input.value; libState.shut.clear(); libState.full = []; libDraw(body, lib, opts); };
}

/* With nothing chosen yet, open the entry most likely to be wanted: this chapter, else the newest. */
export function libDefaultOpen(lib) {
  if (libState.open.size) return;
  const got = lib.entries.filter((e) => e.unlocked);
  const pick = got.find((e) => e.id === libHere) || got[got.length - 1];
  if (pick) libState.open.add(pick.id);
}

export async function viewLibrary() {
  await refreshState();
  const lib = LIB = await api("library");
  libDefaultOpen(lib);
  main.innerHTML = `<div class="page lib-page">
    <div class="lib-top"><div><h1>Library</h1>
      <p class="dim" style="margin:10px 0 0;max-width:60ch">Reference cards for the chapters you have finished: the key syntax, what it does, and a tiny example. Each chapter you finish adds its card. Inside an exercise the Library sits next to your code: press <kbd>Ctrl+K</kbd>.</p></div>
      <div class="lib-meter">${libCountHTML(lib)}</div></div>
    <div class="lib-search"><input type="text" id="lib-q" role="searchbox" aria-label="Search the Library" autocomplete="off" spellcheck="false" placeholder="Search by chapter or keyword, for example: slice, KeyError, sorted"></div>
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
    $(".lib-dcount", panel).textContent = `${lib.unlocked} of ${lib.total} unlocked`;
    if (mode !== "cards") return;
    libDefaultOpen(lib);
    libSearchBox(input, body, lib, { panel: true });
    libDraw(body, lib, { panel: true });
  }
  async function load() {
    if (LIB) draw(LIB);
    try {
      LIB = await api("library"); loaded = true;
      if (!panel.isConnected) return;
      if (topic && !chose && mode === "cards" && !LIB.entries.find((e) => e.id === topic)?.unlocked) return setMode("notes");
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
