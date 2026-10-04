import { S, esc, main, refreshState } from "../core.js";

/* ---------------------------------------------------------------- concept map: chapters, prerequisites, mastery */

const NODE_W = 156, NODE_H = 38, COL_GAP = 58, ROW_GAP = 16, PAD = 24, HEAD = 34;

function stateOf(t) {
  if (t.cleared) return "cleared";
  if (t.attempted || t.mastery > 0) return "started";
  return t.unlocked ? "ready" : "locked";
}

const STATE_LABEL = { cleared: "cleared", started: "in progress", ready: "ready to start", locked: "not unlocked yet" };

function closure(start, next) {
  const seen = new Set(), stack = [...next(start)];
  while (stack.length) {
    const id = stack.pop();
    if (seen.has(id)) continue;
    seen.add(id);
    stack.push(...next(id));
  }
  return seen;
}

export async function viewMap() {
  await refreshState();
  const topics = S.topics, byId = Object.fromEntries(topics.map((t) => [t.id, t]));
  const dependents = {};
  topics.forEach((t) => t.requires.forEach((r) => (dependents[r] ||= []).push(t.id)));
  const modules = S.modules.filter((m) => topics.some((t) => t.track === m.id));

  // Layout: one column per module, chapters stacked in course order.
  const pos = {};
  let height = 0;
  modules.forEach((m, col) => {
    topics.filter((t) => t.track === m.id).forEach((t, row) => {
      pos[t.id] = { x: PAD + col * (NODE_W + COL_GAP), y: PAD + HEAD + row * (NODE_H + ROW_GAP) };
      height = Math.max(height, pos[t.id].y + NODE_H + PAD);
    });
  });
  const width = PAD * 2 + modules.length * NODE_W + (modules.length - 1) * COL_GAP;

  const edge = (from, to) => {
    const a = pos[from], b = pos[to];
    if (!a || !b) return "";
    if (a.x === b.x) {   // same module: loop out to the left of the column
      const x = a.x - 14, y1 = a.y + NODE_H / 2, y2 = b.y + NODE_H / 2;
      return `M${a.x} ${y1} C${x} ${y1} ${x} ${y2} ${b.x} ${y2}`;
    }
    const x1 = a.x + NODE_W, y1 = a.y + NODE_H / 2, x2 = b.x, y2 = b.y + NODE_H / 2, mid = (x1 + x2) / 2;
    return `M${x1} ${y1} C${mid} ${y1} ${mid} ${y2} ${x2} ${y2}`;
  };

  const ready = topics.filter((t) => stateOf(t) === "ready");
  const shaky = topics.filter((t) => stateOf(t) === "started" && t.requires.some((r) => !byId[r]?.cleared));
  const counts = topics.reduce((c, t) => ((c[stateOf(t)] = (c[stateOf(t)] || 0) + 1), c), {});

  main.innerHTML = `<div class="page">
    <div class="crumbs"><a href="#/course">Course</a></div>
    <h1>Concept map</h1>
    <p class="dim" style="max-width:66ch;margin-top:10px">Every chapter and what it builds on. Select a chapter to light up everything it needs and everything it unlocks.</p>
    <div class="map-legend">${["cleared", "started", "ready", "locked"].map((s) => `<span><i class="map-key ${s}"></i>${STATE_LABEL[s]} <b>${counts[s] || 0}</b></span>`).join("")}</div>
    <div class="map-wrap"><svg class="map" id="map" viewBox="0 0 ${width} ${height}" width="${width}" height="${height}" role="group" aria-label="Chapters and their prerequisites">
      ${modules.map((m, col) => `<text class="map-mod" x="${PAD + col * (NODE_W + COL_GAP)}" y="${PAD + 12}">${m.number ? `${m.number}. ` : ""}${esc(m.title)}</text>`).join("")}
      <g class="map-edges">${topics.flatMap((t) => t.requires.map((r) => `<path data-from="${r}" data-to="${t.id}" d="${edge(r, t.id)}"/>`)).join("")}</g>
      <g class="map-nodes">${topics.map((t) => { const p = pos[t.id], st = stateOf(t); return `<g class="map-node ${st}" data-id="${t.id}" tabindex="0" role="button" aria-label="${esc(t.title)}: ${STATE_LABEL[st]}, ${Math.round(t.mastery * 100)}% mastery" transform="translate(${p.x} ${p.y})">
          <rect width="${NODE_W}" height="${NODE_H}" rx="8"/>
          <rect class="map-bar" x="1" y="${NODE_H - 5}" width="${Math.max(0, (NODE_W - 2) * (t.cleared ? 1 : t.mastery))}" height="4" rx="2"/>
          <text x="10" y="${NODE_H / 2 + 4}">${esc(t.title.length > 21 ? t.title.slice(0, 20) + "…" : t.title)}</text>
          <title>${esc(t.title)}</title></g>`; }).join("")}</g>
    </svg></div>
    <div class="map-side">
      <div class="panel" id="map-info"><p class="dim">Select a chapter on the map.</p></div>
      <div class="panel"><h3>Ready to start</h3>${ready.length ? `<ul class="map-list">${ready.slice(0, 6).map((t) => `<li><a href="#/chapter/${t.id}">${esc(t.title)}</a></li>`).join("")}</ul>` : `<p class="dim small">Nothing new is unlocked right now: keep going with the chapters in progress.</p>`}</div>
      ${shaky.length ? `<div class="panel"><h3>Weak foundations</h3><p class="dim small">You've started these, but not every chapter they build on is cleared yet.</p><ul class="map-list">${shaky.map((t) => `<li><a href="#/chapter/${t.id}">${esc(t.title)}</a> <span class="faint small">needs ${t.requires.filter((r) => !byId[r]?.cleared).map((r) => esc(byId[r]?.title || r)).join(", ")}</span></li>`).join("")}</ul></div>` : ""}
    </div>
  </div>`;

  const svg = document.getElementById("map");
  function select(id) {
    const t = byId[id];
    const needs = closure(id, (x) => byId[x]?.requires || []);
    const unlocks = closure(id, (x) => dependents[x] || []);
    svg.classList.add("focus");
    svg.querySelectorAll(".map-node").forEach((n) => {
      const nid = n.dataset.id;
      n.classList.toggle("sel", nid === id);
      n.classList.toggle("needs", needs.has(nid));
      n.classList.toggle("unlocks", unlocks.has(nid));
    });
    svg.querySelectorAll(".map-edges path").forEach((p) => {
      const { from, to } = p.dataset;
      p.classList.toggle("needs", (to === id || needs.has(to)) && (needs.has(from)));
      p.classList.toggle("unlocks", (from === id || unlocks.has(from)) && unlocks.has(to));
    });
    const req = t.requires.map((r) => byId[r]).filter(Boolean);
    const next = (dependents[id] || []).map((d) => byId[d]);
    document.getElementById("map-info").innerHTML = `<h3>${esc(t.title)}</h3>
      <p class="small"><span class="pill ${t.cleared ? "pass" : stateOf(t) === "started" ? "warn" : ""}">${STATE_LABEL[stateOf(t)]}</span> ${Math.round(t.mastery * 100)}% mastery · ${t.solved}/${t.total} steps</p>
      <p class="dim small">${esc(t.summary)}</p>
      ${req.length ? `<p class="small"><b>Builds on</b> ${req.map((r) => `<a href="#/chapter/${r.id}">${esc(r.title)}</a>${r.cleared ? " ✓" : ""}`).join(", ")}</p>` : `<p class="small faint">A starting point: needs nothing else.</p>`}
      ${next.length ? `<p class="small"><b>Unlocks</b> ${next.map((n) => `<a href="#/chapter/${n.id}">${esc(n.title)}</a>`).join(", ")}</p>` : ""}
      <a class="btn small primary" href="#/chapter/${t.id}">Open the chapter</a>`;
  }
  svg.addEventListener("click", (e) => { const n = e.target.closest(".map-node"); if (n) select(n.dataset.id); });
  svg.addEventListener("keydown", (e) => {
    const n = e.target.closest(".map-node");
    if (n && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); select(n.dataset.id); }
  });
  const first = shaky[0] || topics.find((t) => stateOf(t) === "started") || ready[0];
  if (first) select(first.id);
}
