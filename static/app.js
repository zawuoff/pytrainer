"use strict";
/* PyTrainer front-end: a hash-routed single page app, no build step. */

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
const main = $("#main");
let S = null;            // cached /api/state
let cleanup = [];        // run when leaving a view
let lastInteraction = Date.now();

const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

async function api(path, body) {
  const opts = body === undefined ? {} : {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
  };
  const res = await fetch("/api/" + path, opts);
  let data;
  try { data = await res.json(); } catch { data = { error: `Server returned ${res.status}` }; }
  if (!res.ok) throw new Error(data.error || `Request failed (${res.status})`);
  return data;
}

function toast(msg, bad = false) {
  const t = document.createElement("div");
  t.className = "toast" + (bad ? " bad" : "");
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), bad ? 6000 : 3000);
}

marked.setOptions({ gfm: true, breaks: false });
const md = (text, cls = "prose") => `<div class="${cls}">${DOMPurify.sanitize(marked.parse(text || ""))}</div>`;

function highlight(root) {
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

const modColor = (id) => `--mc: var(--m-${id || "foundations"})`;
const diffBars = (d) => `<span class="diff" title="Difficulty ${d} of 3">${[1, 2, 3].map((i) => `<i class="${i <= d ? "on" : ""}"></i>`).join("")}</span>`;
const ticks = (cells) => `<span class="ticks">${cells.map(([, st]) => `<i class="${st}"></i>`).join("")}</span>`;
const fmtMin = (m) => m >= 60 ? `${Math.floor(m / 60)}h ${m % 60}m` : `${m}m`;
const fmtDate = (s) => s ? new Date(s).toLocaleString([], { dateStyle: "medium", timeStyle: "short" }) : "";
const aiOn = () => S && S.settings.ai.provider !== "none";
const aiName = () => ({ claude: "Claude Code", codex: "Codex", opencode: "OpenCode" }[S?.settings.ai.provider] || "AI");
const moduleOf = (id) => S.modules.find((m) => m.id === id);
const topicOf = (id) => S.topics.find((t) => t.id === id);

function busy(btn, on, label) {
  if (!btn) return;
  if (on) { btn.dataset.label = btn.innerHTML; btn.innerHTML = `<span class="spin"></span> ${label || ""}`; btn.disabled = true; }
  else { btn.innerHTML = btn.dataset.label || btn.innerHTML; btn.disabled = false; }
}
const noAI = (what) => `<div class="note">${what} needs an AI connection. <a href="#/settings">Connect Claude Code, Codex or OpenCode in Settings</a>.</div>`;

function stepKind(e) {
  if (e.mode === "predict") return "Read & predict";
  if (e.mode === "tests") return "Write the tests";
  if (e.difficulty <= 1) return "Lesson + exercise";
  return e.difficulty === 3 ? "Checkpoint" : "Practice";
}

async function refreshState() {
  S = await api("state");
  const due = S.summary.reviews_due;
  const b = $("#review-badge");
  b.textContent = due; b.classList.toggle("hidden", !due);
  $("#ai-status").innerHTML = aiOn() ? `AI: ${esc(aiName())}${S.settings.ai.model ? " · " + esc(S.settings.ai.model) : ""}` : `AI: not connected`;
  $("#rail-course").innerHTML = `<div class="lbl">Your course</div>` + S.modules.map((m) => {
    const pct = m.steps_total ? Math.round((m.steps_done / m.steps_total) * 100) : 0;
    return `<a class="rail-mod" style="${modColor(m.id)}" href="#/course/${m.id}" title="${esc(m.title)}: ${pct}%">
      <span class="n">${m.number}</span><span>${esc(m.title)}<div class="rb"><i style="width:${m.complete ? 100 : pct}%"></i></div></span></a>`;
  }).join("");
  return S;
}

/* ---------------------------------------------------------------- router */

const routes = [
  [/^#\/home$/, viewHome],
  [/^#\/welcome(\?place)?$/, viewWelcome],
  [/^#\/me(\?onboarding|\?restart)?$/, viewMe],
  [/^#\/course(?:\/([\w-]+))?$/, viewCourse],
  [/^#\/chapter\/([\w-]+)(\?notes)?$/, viewChapter],
  [/^#\/topic\/([\w-]+)(\?learn)?$/, (id) => { location.replace("#/chapter/" + id); }],
  [/^#\/step\/([\w-]+)(\?review)?$/, viewStep],
  [/^#\/ex\/([\w-]+)(\?review)?$/, (id, r) => { location.replace("#/step/" + id + (r || "")); }],
  [/^#\/exam\/([\w-]+)$/, viewExam],
  [/^#\/extras$/, viewExtras],
  [/^#\/reviews$/, viewReviews],
  [/^#\/placement$/, viewPlacement],
  [/^#\/placement\/([\w-]+)$/, viewPlacementQuestion],
  [/^#\/projects$/, viewProjects],
  [/^#\/project\/([\w-]+)$/, viewProject],
  [/^#\/labs$/, viewLabs],
  [/^#\/progress$/, viewProgress],
  [/^#\/settings$/, viewSettings],
];

async function route() {
  cleanup.forEach((fn) => { try { fn(); } catch {} });
  cleanup = [];
  const hash = location.hash || "#/home";
  if (!S) {
    try { await refreshState(); }
    catch (e) { main.innerHTML = `<div class="page"><div class="errbox">Cannot reach the PyTrainer server: ${esc(e.message)}</div></div>`; return; }
  }
  if (!S.settings.onboarded && !/^#\/(welcome|placement|settings|me)/.test(hash)) { location.hash = "#/welcome"; return; }
  const nav = hash.split("/")[1]?.split("?")[0];
  document.body.classList.toggle("focus", /^#\/(step|project|placement)\//.test(hash));
  const navMap = { me: "home", step: "course", chapter: "course", exam: "course", extras: "course", project: "projects", placement: "home", welcome: "home", today: "home" };
  $$(".nav a[data-nav]").forEach((a) => a.classList.toggle("on", a.dataset.nav === (navMap[nav] || nav)));
  for (const [rx, fn] of routes) {
    const m = hash.match(rx);
    if (m) {
      main.scrollTop = 0;
      try { await fn(...m.slice(1)); }
      catch (e) { console.error(e); main.innerHTML = `<div class="page"><div class="errbox">${esc(e.message)}</div></div>`; }
      return;
    }
  }
  location.hash = "#/home";
}
window.addEventListener("hashchange", route);

["keydown", "mousedown", "mousemove", "wheel", "touchstart"].forEach((ev) =>
  window.addEventListener(ev, () => { lastInteraction = Date.now(); }, { passive: true }));
setInterval(() => {
  if (document.visibilityState === "visible" && Date.now() - lastInteraction < 120000) api("heartbeat", { seconds: 30 }).catch(() => {});
}, 30000);

/* ---------------------------------------------------------------- shared pieces */

function heatmap(days) {
  const pad = new Date(days[0].day).getDay();
  const cells = Array(pad).fill(`<i style="visibility:hidden"></i>`);
  days.forEach((d) => {
    const m = d.minutes, lvl = m === 0 && !d.solved ? 0 : m < 20 ? 1 : m < 45 ? 2 : m < 90 ? 3 : 4;
    cells.push(`<i class="l${lvl}" title="${d.day}: ${m} min, ${d.solved} solved"></i>`);
  });
  return `<div class="heat">${cells.join("")}</div>`;
}

const EDITOR_OPTS = {
  mode: "python", theme: "pt", lineNumbers: true, indentUnit: 4, tabSize: 4, indentWithTabs: false,
  matchBrackets: true, autoCloseBrackets: true, styleActiveLine: true, lineWrapping: false,
  inputStyle: matchMedia("(pointer: coarse)").matches ? "contenteditable" : "textarea",
  extraKeys: {
    Tab: (cm) => cm.somethingSelected() ? cm.indentSelection("add") : cm.replaceSelection("    ", "end"),
    "Shift-Tab": (cm) => cm.indentSelection("subtract"),
    "Ctrl-/": "toggleComment",
    Backspace: (cm) => {
      const c = cm.getCursor(), before = cm.getLine(c.line).slice(0, c.ch);
      if (!cm.somethingSelected() && before.length && /^ +$/.test(before)) {
        cm.replaceRange("", { line: c.line, ch: c.ch - (before.length % 4 || 4) }, c);
      } else return CodeMirror.Pass;
    },
  },
};

/* Every python example in a lesson gets Run / Edit & run. */
function enhanceCode(root) {
  $$("pre", root).forEach((pre) => {
    const codeEl = $("code", pre);
    if (!codeEl || pre.dataset.run) return;
    const lang = (codeEl.className.match(/language-(\w+)/) || [])[1] || "";
    if (!["python", "py"].includes(lang)) return;
    pre.dataset.run = "1";
    const code = codeEl.textContent;
    const bar = document.createElement("div");
    bar.className = "runbar";
    bar.innerHTML = `<button class="btn small">Run</button><button class="btn small ghost">Edit & run</button>`;
    const out = document.createElement("pre");
    out.className = "outbox hidden";
    out.style.marginTop = "-6px";
    pre.after(bar, out);
    const [runBtn, editBtn] = bar.querySelectorAll("button");
    let cm = null;
    runBtn.onclick = async () => {
      busy(runBtn, true);
      try {
        const r = await api("run", { code: cm ? cm.getValue() : code });
        out.classList.remove("hidden");
        out.innerHTML = esc(r.stdout || "") + (r.stderr ? `<span style="color:var(--fail)">${esc(r.stderr)}</span>` : "") + (!r.stdout && !r.stderr ? `<span class="faint">(no output)</span>` : "");
      } catch (err) { toast(err.message, true); }
      busy(runBtn, false);
    };
    editBtn.onclick = () => {
      pre.classList.add("hidden");
      const host = document.createElement("div");
      host.style.cssText = "border:1px solid var(--rule);border-radius:8px;overflow:hidden;margin:0 0 14px";
      bar.before(host);
      cm = CodeMirror(host, { ...EDITOR_OPTS, value: code, viewportMargin: Infinity });
      cm.setSize(null, "auto");
      editBtn.classList.add("hidden");
      setTimeout(() => cm.refresh(), 10);
    };
  });
}
function renderRich(root) { highlight(root); enhanceCode(root); }

function makeEditor(host, files, onChange, { focus = true } = {}) {
  const docs = {};
  Object.entries(files).forEach(([name, code]) => { docs[name] = CodeMirror.Doc(code, "python"); });
  let active = Object.keys(files)[0];
  const cm = CodeMirror(host, { ...EDITOR_OPTS });
  cm.swapDoc(docs[active]);
  cm.on("change", () => onChange && onChange());
  setTimeout(() => { cm.refresh(); if (focus) cm.focus(); }, 30);
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

function startTimer(el) {
  let secs = 0;
  const id = setInterval(() => {
    if (document.visibilityState === "visible" && Date.now() - lastInteraction < 120000) secs++;
    if (el) el.textContent = `${Math.floor(secs / 60)}:${String(secs % 60).padStart(2, "0")}`;
  }, 1000);
  cleanup.push(() => clearInterval(id));
  return { get secs() { return secs; } };
}

/* The output dock under the editor can be dragged taller or shorter. */
function makeDock(dock) {
  const grip = $(".dock-grip", dock), col = dock.parentElement;
  if (!grip) return;
  grip.onmousedown = (e) => {
    e.preventDefault();
    const rect = col.getBoundingClientRect();
    const move = (ev) => col.style.setProperty("--dock", Math.min(80, Math.max(15, ((rect.bottom - ev.clientY) / rect.height) * 100)) + "%");
    const up = () => { window.removeEventListener("mousemove", move); window.removeEventListener("mouseup", up); };
    window.addEventListener("mousemove", move); window.addEventListener("mouseup", up);
  };
}

/* Phones: show the lesson or the code, switched from the top bar. */
const isNarrow = () => matchMedia("(max-width: 960px)").matches;
function paneSwitch(ws, cm, labels = ["Lesson", "Code"]) {
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
    if (p === "code" && cm) setTimeout(() => cm.refresh(), 20);
  };
  $$("button", sw).forEach((b) => b.onclick = () => set(b.dataset.p));
  return set;
}

const interestName = () => (S?.settings.profile?.primary_interest || "").split("(")[0].trim();
const burst = () => `<span class="burst">${Array.from({ length: 12 }, (_, i) =>
  `<i style="--r:${i * 30}deg;background:${["var(--amber)", "var(--pass)", "var(--text)"][i % 3]};animation-delay:${(i % 3) * 40}ms"></i>`).join("")}</span>`;
const WRITING_STEPS = (topic) => ["Reading the lesson…", `Finding a ${topic || "personal"} angle…`, "Writing examples…", "Running every example…", "Polishing the wording…"];
function writingHTML(topic) {
  return `<div class="writing reveal"><div class="status"><div class="orbit"><i></i><i></i><i></i></div><span id="wstatus">${esc(WRITING_STEPS(topic)[0])}</span></div>
    <div class="lines"><i style="width:92%"></i><i style="width:78%"></i><i style="width:86%"></i><i style="width:60%"></i><i style="width:72%"></i></div>
    <p class="faint small" style="margin:12px 0 0">Re-telling this lesson around ${esc(topic || "what you love")}. The first time takes a few seconds; after that it's instant.</p></div>`;
}

function resultsHTML(r, extra = "") {
  if (!r) return `<p class="dim">Press <b>Check</b> (Ctrl+Enter) when you're ready. Each check shows exactly what passed and what didn't.</p>`;
  const ok = r.status === "passed";
  const unit = r.tests[0]?.name?.startsWith("line ") ? "lines right" : "checks";
  let html = `<div class="results"><div class="sum ${ok ? "pass" : "fail"}"><b>${ok ? "Correct" : r.status === "timeout" ? "Timed out" : r.status === "error" ? "Your code didn't run" : "Not yet"}</b>
    <span class="dim">${r.passed}/${r.total} ${unit}</span></div>`;
  if (r.error) html += `<div class="errbox">${esc(r.error)}</div>`;
  html += r.tests.map((t) => `<div class="test ${t.passed ? "ok" : "no"}"><span class="ic">${t.passed ? "✓" : "✕"}</span>
      <div>${esc(t.name)}${t.message ? `<pre>${esc(t.message)}</pre>` : ""}</div></div>`).join("");
  if (r.stdout && r.stdout.trim()) html += `<h3 style="margin:16px 0 6px">Printed while checking</h3><pre class="outbox">${esc(r.stdout)}</pre>`;
  return html + extra + "</div>";
}

const chatHTML = (chat, empty) => !chat.length ? `<p class="dim">${empty}</p>` :
  `<div class="chat">${chat.map((m) => `<div class="msg ${m.role}"><div class="who">${m.role === "tutor" ? "Tutor" : "You"}</div>${m.role === "tutor" ? md(m.content) : esc(m.content).replace(/\n/g, "<br>")}</div>`).join("")}</div>`;

const QUALITY_NAMES = { readability: "Readability", naming: "Naming", idiomatic: "Pythonic", simplicity: "Simplicity", robustness: "Edge cases" };
function qualityHTML(q) {
  if (!q) return "";
  return `<div class="review"><div class="row" style="gap:14px;align-items:baseline"><div class="score">${q.overall}<small>/10</small></div><span class="dim small">code quality, scored by Jev</span></div>
    <div style="margin-top:10px">${Object.entries(q.dims).map(([k, v]) => `<div class="qrow"><span>${esc(QUALITY_NAMES[k] || k)}</span>
      <div class="bar" style="--mc:${v.score >= 7 ? "var(--pass)" : v.score >= 4 ? "var(--amber)" : "var(--fail)"}"><i style="width:${v.score * 10}%"></i></div><span class="faint">${v.score}</span></div>`).join("")}</div></div>`;
}

function reviewHTML(rv) {
  if (!rv) return "";
  return `<div class="review stack">
    <div class="row" style="gap:16px;align-items:baseline"><div class="score">${esc(rv.score)}<small>/10</small></div><div>${esc(rv.summary || "")}</div></div>
    ${rv.strengths?.length ? `<div><h3>Strengths</h3><ul>${rv.strengths.map((s) => `<li>${esc(s)}</li>`).join("")}</ul></div>` : ""}
    ${rv.issues?.length ? `<div><h3>Issues</h3><ul>${rv.issues.map((i) => `<li><span class="sev-${esc(i.severity)}">${esc(i.severity)}</span>${i.line ? ` · line ${esc(i.line)}` : ""}: ${esc(i.comment)}</li>`).join("")}</ul></div>` : ""}
    ${rv.idioms?.length ? `<div><h3>Worth learning</h3><ul>${rv.idioms.map((s) => `<li>${md(s)}</li>`).join("")}</ul></div>` : ""}
    ${rv.interview_note ? `<div class="note">${esc(rv.interview_note)}</div>` : ""}</div>`;
}

const checksHTML = (checks) => !checks?.length ? "" :
  `<div style="margin-top:16px"><h3 class="small dim" style="margin-bottom:2px">What gets checked</h3>
   <ul class="check-list">${checks.map((c) => `<li><span class="pending">○</span><div>${esc(c)}</div></li>`).join("")}</ul></div>`;

function researchHTML(r) {
  if (!r) return "";
  return `<div class="research"><b>${r.links?.length ? "Read first" : "Look it up"}</b><div>${md(r.note)}</div>
    ${r.links?.length ? `<ul>${r.links.map((l) => `<li><a href="${esc(l.url)}" target="_blank" rel="noopener">${esc(l.title)}</a></li>`).join("")}</ul>` : ""}</div>`;
}

/* ---------------------------------------------------------------- home */

function greeting() {
  const h = new Date().getHours();
  const part = h < 5 ? "Late night" : h < 12 ? "Morning" : h < 18 ? "Afternoon" : "Evening";
  return S.settings.name ? `${part}, ${esc(S.settings.name)}` : `${part} session`;
}

function planItem(p) {
  const href = { project: `#/project/${p.id}`, review: `#/step/${p.id}?review`, exam: `#/exam/${p.id}` }[p.kind] || `#/step/${p.id}`;
  const kind = { review: "Review", exercise: p.difficulty >= 2 ? "Practice" : "Step", project: "Project", exam: "Module test" }[p.kind];
  return `<li><a href="${href}"><span><div class="t">${esc(p.title)}</div><div class="w">${esc(p.why)}</div></span><span class="k">${kind}</span></a></li>`;
}

async function viewHome() {
  await refreshState();
  const sm = S.summary, goal = S.settings.daily_goal, c = S.continue;
  const pct = Math.min(100, Math.round((sm.today_minutes / goal) * 100));
  const cm = c ? moduleOf(c.module) : null;
  const chap = c ? cm.chapters.find((x) => x.id === c.topic) : null;
  main.innerHTML = `<div class="page">
    <div class="hello">
      <div><h1>${greeting()}</h1><p>${esc(S.level)} · ${sm.topics_cleared} of ${sm.topics_total} chapters cleared</p></div>
      <div class="today-meter">
        <div class="stat"><b>${fmtMin(sm.today_minutes)}</b><span>of ${fmtMin(goal)} today</span><div class="bar"><i style="width:${pct}%"></i></div></div>
        <div class="stat"><b>${sm.streak.current}</b><span>day streak</span></div>
        <div class="stat"><b>${sm.reviews_due}</b><span>reviews due</span></div>
      </div>
    </div>
    ${(() => {
      const tips = [];
      if (aiOn() && !S.settings.profile) tips.push(`<a class="suggest" href="#/me"><b>Make the course yours</b><span>A two-minute chat about what you love, so lessons are explained through it.</span><em>Start the chat</em></a>`);
      if (S.placement.status !== "done") tips.push(`<a class="suggest" href="#/placement"><b>${S.placement.status === "in_progress" ? "Placement test in progress" : "Already know some Python?"}</b><span>${S.placement.status === "in_progress" ? "Pick up where you left off and skip what you know." : "Take the placement test and skip what you know."}</span><em>${S.placement.status === "in_progress" ? "Continue placement" : "Take the test"}</em></a>`);
      return tips.length ? `<div class="suggests">${tips.join("")}</div>` : "";
    })()}
    ${c ? `<a class="continue" style="${modColor(c.module)}" href="${c.type === "project" ? `#/project/${c.id}` : `#/step/${c.id}`}">
        <div class="where"><b>Module ${cm.number} · ${esc(cm.title)}</b> · ${esc(c.topic_title)}</div>
        <div class="title">${esc(c.title)}</div>
        <div class="dim">${c.type === "project" ? "Chapter project · build it on your own to finish the chapter" : `Step ${c.step} of ${c.steps} · ${c.kind === "learn" ? "a short lesson, then an exercise" : "practice"}`}</div>
        <div class="foot">${ticks(chap.strip)}<span class="btn primary big">Continue</span></div></a>`
      : `<div class="continue" style="--mc:var(--pass)"><div class="title">You've cleared every chapter.</div><p class="dim">Take the module tests, build the projects, or generate fresh challenges from any chapter.</p></div>`}
    <div class="grid2 section" style="margin-top:28px;align-items:start">
      <section><div class="row between" style="margin-bottom:6px"><h2>Tonight</h2><span class="faint small">${sm.today_solved} solved today</span></div>
        ${S.plan.length ? `<ol class="plan">${S.plan.map(planItem).join("")}</ol>` : `<p class="dim">Nothing queued.</p>`}</section>
      <section>
        <div class="panel"><h3 style="margin-bottom:12px">Your practice, last 20 weeks</h3><div id="heat"></div>
          <div class="stat-row" style="margin-top:16px;gap:28px">
            <div class="stat"><b>${sm.solved}</b><span>steps solved</span></div>
            <div class="stat"><b>${sm.first_try_rate == null ? "–" : Math.round(sm.first_try_rate * 100) + "%"}</b><span>first try</span></div>
            <div class="stat"><b>${sm.avg_quality == null ? "–" : sm.avg_quality}</b><span>code quality</span></div>
          </div></div>
        <div class="panel"><div class="row between"><h3>Coach</h3><button class="btn small" id="coach-btn">Get tonight's advice</button></div>
          <div id="coach-out" class="dim small" style="margin-top:8px">A plan built from your real progress${aiOn() ? "" : " (needs an AI connection)"}.</div></div>
      </section>
    </div>
    <section class="section"><div class="row between"><h2>The course</h2><a class="btn small ghost" href="#/course">Open the full course</a></div>
      <div style="margin-top:10px">${S.modules.map((m) => `<a class="chapter-row" style="${modColor(m.id)}" href="#/course/${m.id}">
        <span class="ct"><span style="color:var(--mc);font-family:var(--read)">${m.number}</span>&nbsp; ${esc(m.title)}</span>
        <div class="bar"><i style="width:${m.complete ? 100 : Math.round((m.steps_done / Math.max(1, m.steps_total)) * 100)}%"></i></div>
        <span class="state ${m.complete ? "cleared" : ""}">${m.complete ? "complete" : `${m.cleared}/${m.chapters.length} chapters`}</span></a>`).join("")}</div></section>
  </div>`;
  api("stats").then((st) => { const el = $("#heat"); if (el) el.innerHTML = heatmap(st.heatmap); });
  $("#coach-btn").onclick = async (e) => {
    if (!aiOn()) { $("#coach-out").innerHTML = noAI("The coach"); return; }
    busy(e.target, true, "Thinking");
    try { const r = await api("ai/coach", {}); $("#coach-out").innerHTML = md(r.advice); $("#coach-out").classList.remove("dim", "small"); }
    catch (err) { $("#coach-out").innerHTML = `<div class="errbox">${esc(err.message)}</div>`; }
    busy(e.target, false);
  };
}

/* ---------------------------------------------------------------- course */

async function viewCourse(focus) {
  await refreshState();
  const projects = (await api("projects")).projects;
  main.innerHTML = `<div class="page">
    <h1>The course</h1>
    <p class="dim" style="max-width:66ch;margin-top:10px">Eight modules, ordered by what AI-engineering job postings ask for: solid Python first, then APIs and data, then building with LLMs, RAG, evals and agents. Every chapter is a path of short lessons, each followed by an exercise. Each module ends with a test, and passing it lets you skip the module.</p>
    <div class="section" style="margin-top:20px">${S.modules.map((m, i) => `
      <section class="module ${i === 0 ? "first" : ""}" id="mod-${m.id}" style="${modColor(m.id)}">
        <div class="num">${m.number}</div>
        <div>
          <h2>${esc(m.title)}</h2>
          <p class="why">${esc(m.why)}</p>
          <div class="meta"><span>${m.chapters.length} chapters</span><span>${m.steps_done}/${m.steps_total} steps done</span>${m.complete ? `<span style="color:var(--mc)">complete</span>` : ""}</div>
          <div class="chapters">${m.chapters.map((c) => `<a class="chapter-row" href="#/chapter/${c.id}">
              <span><span class="ct">${esc(c.title)}</span><div class="cs">${esc(c.summary)}</div></span>
              ${ticks(c.strip)}
              <span class="state ${c.cleared ? "cleared" : ""}">${c.earned ? "cleared" : c.placed ? "tested out" : c.done ? `${c.done}/${c.steps}` : !c.unlocked ? "later" : ""}</span></a>`).join("")}
            ${m.exam ? `<a class="exam-row" href="#/exam/${m.id}"><span><span class="ct">Module test</span><div class="cs">${m.exam.total} questions · pass ${Math.round(m.exam.pass_ratio * 100)}% to complete the module and skip ahead</div></span>
              <span class="pill ${m.exam.passed ? "pass" : m.exam.attempted ? "warn" : ""}">${m.exam.passed ? "passed" : `${m.exam.solved}/${m.exam.total}`}</span></a>` : ""}
          </div>
          ${m.projects.length ? `<div class="resources"><b style="color:var(--text)">Build it:</b> ${m.projects.map((pid) => { const p = projects.find((x) => x.id === pid); return p ? `<a href="#/project/${pid}">${esc(p.title)}</a>${p.passed ? " ✓" : ""}` : ""; }).join(" · ")}</div>` : ""}
          <div class="resources"><b style="color:var(--text)">Further reading:</b> ${m.resources.map((r) => `<a href="${esc(r.url)}" target="_blank" rel="noopener">${esc(r.title)}</a>`).join(" · ")}</div>
          <div class="resources"><b style="color:var(--text)">Show it:</b> ${esc(m.show_it)}</div>
        </div>
      </section>`).join("")}
    </div>
    <section class="section"><h2>Extra practice</h2><p class="dim">Combination challenges that mix chapters. You can also generate AI exercises from any chapter page.</p><a class="btn" href="#/extras">Open extra practice</a></section>
  </div>`;
  if (focus) setTimeout(() => $("#mod-" + focus)?.scrollIntoView({ behavior: "smooth", block: "start" }), 60);
}

async function viewExtras() {
  await refreshState();
  main.innerHTML = `<div class="page narrow"><div class="crumbs"><a href="#/course">Course</a></div><h1>Combination challenges</h1>
    <p class="dim" style="margin-top:10px">Mini real-world tasks that mix several chapters. Each unlocks when its chapters are cleared, but you can open any of them.</p>
    <ol class="steps">${S.combos.map((c) => `<li><a href="#/step/${c.id}"><span>${esc(c.title)}<span class="sub">${c.topics.map((t) => esc(topicOf(t)?.title || t)).join(" + ")}</span></span>
      <span class="kind">${c.unlocked ? "" : "later"} ${diffBars(c.difficulty)}</span><span class="dot ${c.status}"></span></a></li>`).join("")}</ol></div>`;
}

async function viewChapter(id, notesFlag) {
  await refreshState();
  const d = await api("topic/" + id);
  const t = d.topic, p = d.progress, m = moduleOf(t.track);
  const done = d.exercises.filter((e) => e.status === "solved" && !e.revealed).length;
  const proj = p.project;
  const cta = d.next?.type === "step" ? `<a class="btn primary big" href="#/step/${d.next.id}">${done ? "Continue" : "Start the chapter"}</a>`
    : d.next?.type === "project" ? `<a class="btn primary big" href="#/project/${d.next.id}">Start the chapter project</a>`
    : d.next_chapter ? `<a class="btn primary big" href="#/chapter/${d.next_chapter.id}">Next chapter: ${esc(d.next_chapter.title)}</a>`
    : `<a class="btn primary big" href="#/course">Back to the course</a>`;
  main.innerHTML = `<div class="page narrow" style="${modColor(t.track)}">
    <div class="crumbs"><a href="#/course/${m.id}">Module ${m.number} · ${esc(m.title)}</a></div>
    <h1>${esc(t.title)}</h1>
    <p class="dim" style="margin:10px 0 0;max-width:62ch">${esc(t.summary)}</p>
    <div class="row between" style="margin-top:20px">
      <div style="flex:1;max-width:380px">${ticks(topicOf(id).strip)}<div class="faint small" style="margin-top:6px">${done}/${d.exercises.length} steps · ${Math.round(p.mastery * 100)}% mastery${p.earned ? " · cleared" : p.placed ? " · tested out" : ""}</div></div>
      ${cta}
    </div>
    ${d.requires.some((r) => !r.cleared) ? `<div class="note">This chapter builds on ${d.requires.filter((r) => !r.cleared).map((r) => `<a href="#/chapter/${r.id}">${esc(r.title)}</a>`).join(", ")}, which you haven't cleared yet. You can still start it.</div>` : ""}
    <ol class="steps">${d.exercises.map((e) => `<li><a href="#/step/${e.id}">
      <span>${esc(e.title)}<span class="sub">${stepKind(e)}${e.research ? " · research" : ""}${e.attempts ? ` · ${e.attempts} attempt${e.attempts > 1 ? "s" : ""}` : ""}</span></span>
      <span class="kind">${e.revealed ? `<span class="pill warn">redo to earn</span>` : e.difficulty ? diffBars(e.difficulty) : ""}</span>
      <span class="dot ${e.revealed ? "revealed" : e.status}"></span></a></li>`).join("")}</ol>
    ${proj ? `<section class="section"><div class="row between"><h2>Chapter project</h2>${proj.passed ? `<span class="pill pass">passed</span>` : ""}</div>
      <a class="list-row" href="#/project/${proj.id}" style="border-top:1px solid var(--rule)">
        <div><h3>${esc(proj.title)}</h3><div class="meta"><span>Build it on your own, with a bit of googling. Hidden checks grade it when you submit.</span></div></div>
        <span class="btn ${proj.passed ? "" : p.steps_done ? "primary" : ""}">${proj.passed ? "Open" : "Start"}</span></a>
      <p class="dim small" style="margin-top:8px">The chapter is complete once you've worked through the steps and this project passes.</p></section>` : ""}
    ${t.lesson ? `<section class="section" id="notes"><div class="row between"><h2>Chapter notes</h2><button class="btn small ghost" id="notes-btn">${notesFlag ? "Hide" : "Show"}</button></div>
      <p class="dim small">The whole chapter on one page, for revision.</p>
      <div id="notes-body" class="${notesFlag ? "" : "hidden"}"><div class="panel" style="background:var(--paper)">${md(t.lesson, "lesson")}</div></div></section>` : ""}
    <section class="section"><h2>More practice</h2>
      <p class="dim" style="max-width:62ch">Have ${aiOn() ? esc(aiName()) : "the AI"} write a fresh exercise for this chapter, aimed at your recent mistakes. It's only added if its reference solution passes its own checks.</p>
      <div class="row"><select id="gen-diff" style="width:auto"><option value="1" selected>Easy</option><option value="2">Medium</option><option value="3">Hard</option></select>
        <button class="btn" id="gen-btn">Generate a challenge</button><span class="faint small" id="gen-msg"></span></div>
      ${d.generated.length ? `<ol class="steps">${d.generated.map((e) => `<li><a href="#/step/${e.id}"><span>${esc(e.title)}<span class="sub">AI-generated</span></span><span class="kind">${diffBars(e.difficulty)}</span><span class="dot ${e.status}"></span></a></li>`).join("")}</ol>` : ""}
    </section></div>`;
  const nb = $("#notes-body");
  if (nb) { renderRich(nb); $("#notes-btn").onclick = (e) => { nb.classList.toggle("hidden"); e.target.textContent = nb.classList.contains("hidden") ? "Show" : "Hide"; }; }
  if (notesFlag) setTimeout(() => $("#notes")?.scrollIntoView({ behavior: "smooth" }), 60);
  $("#gen-btn").onclick = async (e) => {
    if (!aiOn()) { $("#gen-msg").innerHTML = `Connect an AI in <a href="#/settings">Settings</a> first.`; return; }
    busy(e.target, true, "Writing and verifying (up to a minute)");
    try { const r = await api("ai/generate", { topic: id, difficulty: +$("#gen-diff").value }); location.hash = "#/step/" + r.id; }
    catch (err) { toast(err.message, true); busy(e.target, false); }
  };
}

async function viewExam(moduleId) {
  await refreshState();
  const d = await api("exam/" + moduleId);
  const m = moduleOf(moduleId), st = d.status;
  const next = d.exercises.find((e) => e.status !== "solved") || d.exercises[0];
  main.innerHTML = `<div class="page narrow" style="${modColor(moduleId)}">
    <div class="crumbs"><a href="#/course/${moduleId}">Module ${m.number} · ${esc(m.title)}</a></div>
    <h1>${esc(d.exam.title)}</h1>
    <div style="margin-top:14px">${md(d.exam.intro)}</div>
    <div class="panel row between" style="margin-top:18px">
      <div class="stat"><b>${st.solved}/${st.total}</b><span>solved · ${Math.ceil(st.total * st.pass_ratio)} needed to pass</span></div>
      ${st.passed ? `<span class="pill pass">passed: module complete</span>` : `<a class="btn primary big" href="#/step/${next.id}">${st.attempted ? "Continue the test" : "Start the test"}</a>`}
    </div>
    <p class="dim small" style="margin-top:12px">During the test there are no hints, tutor or solutions, and some questions ask you to look things up, just like at work. Once you pass, all of that unlocks for review.</p>
    <ol class="steps">${d.exercises.map((e) => `<li><a href="#/step/${e.id}"><span>${esc(e.title)}<span class="sub">${e.research ? "research needed" : "&nbsp;"}</span></span><span class="kind">${diffBars(e.difficulty)}</span><span class="dot ${e.status}"></span></a></li>`).join("")}</ol>
  </div>`;
}

/* ---------------------------------------------------------------- step workspace: lesson left, code right, output below */

async function viewStep(id, reviewFlag) {
  const review = !!reviewFlag;
  const d = await api("exercise/" + id);
  const ex = d.exercise, path = d.path, exam = d.exam, noHelp = d.exam_locked_help;
  const predict = ex.mode === "predict", testsMode = ex.mode === "tests";
  let lastResult = null, chat = d.chat, reviewData = d.review, hints = d.hints, canReveal = d.can_reveal;
  let revealed = d.revealed, explanation = d.explanation, walkthrough = null, improve = null, answer = "";
  let feedback = d.reference ? { reference: d.reference, quality: null, tips: [], style: [] } : null;
  let personal = d.personal, lessonMode = "orig", personalLoading = false, statusTimer = null;
  cleanup.push(() => clearInterval(statusTimer));
  let dockTab = predict ? "answer" : "results";
  let outputHTML = `<span class="faint">${testsMode ? "Run executes your test file (the code under test is importable as <code>target</code>). Check grades your tests." : "Run executes your file and shows what it prints. Check runs the checks."}</span>`;
  let stdin = "", args = "";
  const initial = predict ? ex.code : review ? ex.starter : (d.draft?.["solution.py"] ?? ex.starter);
  const back = path?.kind === "exam" ? `#/exam/${d.module}` : path?.kind === "chapter" ? `#/chapter/${ex.topic}` : path?.kind === "combo" ? "#/extras" : "#/course";
  const idx = path ? path.index : 0, total = path ? path.total : 1;
  const prevId = path && idx > 0 ? path.steps[idx - 1].id : null;
  const nextId = path && idx + 1 < total ? path.steps[idx + 1].id : null;
  const kindText = exam ? "Module test" : review ? "Review: rebuild it from memory" : stepKind(ex);

  main.innerHTML = `<div class="page wide"><div class="ws" style="${modColor(d.module)}">
    <div class="ws-top">
      <a class="btn small ghost" href="${back}" title="Back to the chapter">←</a>
      <span class="ttl"><a href="${back}">${esc(path?.title || d.topic_title || "")}</a> · <b>${idx + 1}/${total}</b></span>
      <div class="stepdots">${(path?.steps || []).map((s, i) => `<a href="#/step/${s.id}" class="${s.status} ${i === idx ? "here" : ""}" title="${i + 1}. ${esc(s.title)}"></a>`).join("")}</div>
      ${prevId ? `<a class="btn small ghost hide-m" href="#/step/${prevId}">Back</a>` : ""}
      ${nextId ? `<a class="btn small" href="#/step/${nextId}">Next</a>` : path?.project && !path.project.passed ? `<a class="btn small" href="#/project/${path.project.id}">Chapter project</a>` : `<a class="btn small" href="${back}">Finish</a>`}
    </div>
    <section class="ws-read"><div class="ws-read-in" id="read"></div></section>
    <section class="ws-code">
      <div class="toolbar">
        <button class="btn" id="run-btn" ${predict ? "disabled" : ""} title="Alt+Enter">Run <kbd>Alt+⏎</kbd></button>
        <button class="btn primary" id="check-btn" title="Ctrl+Enter">Check <kbd>Ctrl+⏎</kbd></button>
        ${ex.hint_count && !noHelp ? `<button class="btn ghost" id="hint-btn">Hint <span class="faint" id="hint-count">${hints.length}/${ex.hint_count}</span></button>` : ""}
        <span class="grow"></span><span class="timer" id="timer">0:00</span>
        ${predict ? "" : `<button class="btn ghost small" id="reset-btn">Reset</button>`}
      </div>
      <div class="filetabs">${testsMode ? `<button class="on">your tests</button>` : predict ? `<button class="on">the program (read it)</button>` : ""}</div>
      <div class="editor" id="editor"></div>
      <div class="dock" id="dock"><div class="dock-grip"></div><div class="dock-tabs" id="dock-tabs"></div><div class="dock-body" id="dock-body"></div></div>
    </section></div></div>`;

  const timer = startTimer($("#timer"));
  let saveT = null;
  const ed = makeEditor($("#editor"), { "solution.py": initial }, () => {
    if (review || predict) return;
    clearTimeout(saveT);
    saveT = setTimeout(() => api("draft", { item_id: id, files: ed.files() }).catch(() => {}), 700);
  }, { focus: !predict });
  if (predict) {
    // The program is for reading only: no cursor, and any click or typing goes to the answer box.
    ed.cm.setOption("readOnly", "nocursor");
    const toAnswer = () => { if (dockTab !== "answer") { dockTab = "answer"; drawDock(); } $("#predict")?.focus(); };
    $("#editor").addEventListener("mousedown", () => setTimeout(toAnswer, 0));
    const typeToAnswer = (e) => {
      const el = document.activeElement;
      if (e.ctrlKey || e.metaKey || e.altKey || e.key.length !== 1) return;
      if (el && (el.tagName === "TEXTAREA" || el.tagName === "INPUT")) return;
      toAnswer();
    };
    document.addEventListener("keydown", typeToAnswer);
    cleanup.push(() => document.removeEventListener("keydown", typeToAnswer));
  }
  cleanup.push(() => { clearTimeout(saveT); if (!review && !predict) api("draft", { item_id: id, files: ed.files() }).catch(() => {}); });
  makeDock($("#dock"));
  const setPane = paneSwitch($(".ws"), ed.cm, ["Lesson", predict ? "Answer" : "Code"]);

  /* left: lesson, then the task */
  const read = $("#read");
  function drawRead() {
    const status = d.state.status === "solved" ? `<span class="pill pass">solved</span>` : d.state.status === "attempted" ? `<span class="pill warn">attempted</span>` : "";
    let h = `<div class="kindline"><span>${esc(kindText)}</span>${ex.difficulty ? diffBars(ex.difficulty) : ""}${status}</div><h1>${esc(ex.title)}</h1>`;
    if (ex.lesson && !review) {
      if (d.personal_available) h += `<div class="persona-bar"><div class="seg"><button data-m="orig" class="${lessonMode === "orig" ? "on" : ""}">Original</button><button data-m="you" class="${lessonMode === "you" ? "on" : ""}">Made for you</button></div>
        <span class="for-you">${lessonMode === "you" ? `explained through ${esc(interestName() || "your interests")}` : `switch${matchMedia("(pointer: coarse)").matches ? " or swipe" : ""} to see it explained through ${esc(interestName() || "your interests")}`}</span></div>`;
      if (lessonMode === "you" && d.personal_available) h += personal ? `<div class="reveal" style="margin-top:14px">${md(personal, "lesson")}</div>` : writingHTML(interestName());
      else h += `<div style="margin-top:18px">${md(ex.lesson, "lesson")}</div>`;
    }
    h += `<div class="task"><div class="label">${predict ? "Your turn: predict the output" : testsMode ? "Your turn: write the tests" : "Your turn"}</div>
      ${researchHTML(ex.research)}${md(ex.prompt)}${checksHTML(d.checks)}
      ${ex.setup_files?.length ? `<p class="faint small" style="margin-top:10px">Files next to your code: ${ex.setup_files.map(esc).join(", ")}</p>` : ""}</div>`;
    if (explanation) h += `<div class="good" style="margin-top:18px"><b>Why:</b> ${md(explanation)}</div>`;
    if (!noHelp) {
      if (hints.length) h += `<div class="section" style="margin-top:26px"><h3>Hints</h3><ol style="padding-left:1.2em">${hints.map((x) => `<li style="margin:6px 0">${md(x)}</li>`).join("")}</ol></div>`;
      if (revealed) {
        h += `<div class="panel" style="margin-top:22px;border-color:var(--amber)"><h3>${predict ? "The actual output" : "A reference solution"}</h3>
          <p class="dim small">${predict ? "Compare it with your prediction, line by line." : "Study it until every line makes sense. Then write it yourself in the editor, without copying, and press Check. It comes back tomorrow for you to rebuild from memory, and only counts once you pass that."}</p>
          ${predict ? `<pre class="outbox">${esc(revealed.output)}</pre>${md(revealed.explanation || "")}` : md("```python\n" + revealed.solution + "\n```")}
          ${!predict && aiOn() ? `<button class="btn small" id="explain-btn">Walk me through it line by line</button>` : ""}
          <div id="walk">${walkthrough ? md(walkthrough) : ""}</div></div>`;
      } else if (d.state.status !== "solved") {
        h += `<div class="section" style="margin-top:28px"><h3>Stuck?</h3>
          <p class="dim small">Take a hint, or ask the Tutor tab below. ${canReveal ? "You've given it a real go, so you can view the solution: study it, then write it yourself." : `The solution unlocks after ${predict ? "2" : "3"} checks or 10 minutes of trying.`}</p>
          <div class="row">${ex.hint_count && hints.length < ex.hint_count ? `<button class="btn small" id="hint-inline">Get hint ${hints.length + 1} of ${ex.hint_count}</button>` : ""}
          <button class="btn small ${canReveal ? "" : "ghost"}" id="reveal-btn" ${canReveal ? "" : "disabled"}>Show solution</button></div></div>`;
      }
    } else {
      h += `<p class="faint small" style="margin-top:22px">Module test: no hints, tutor or solutions until you pass. Some questions need you to look things up, and that's part of the test.</p>`;
    }
    read.innerHTML = h;
    renderRich(read);
    $$(".seg button", read).forEach((b) => b.onclick = () => { lessonMode = b.dataset.m; drawRead(); });
    if (lessonMode === "you" && d.personal_available && !personal) loadPersonal();
    $("#hint-inline", read)?.addEventListener("click", getHint);
    $("#reveal-btn", read)?.addEventListener("click", async (e) => {
      busy(e.target, true);
      try { revealed = (await api(`exercise/${id}/reveal`, { duration_s: timer.secs })).revealed; drawRead(); if (predict) $("#run-btn").disabled = false; }
      catch (err) { toast(err.message, true); busy(e.target, false); }
    });
    $("#explain-btn", read)?.addEventListener("click", async (e) => {
      busy(e.target, true, "Explaining");
      try { walkthrough = (await api("ai/explain", { item_id: id, files: ed.files() })).explanation; drawRead(); }
      catch (err) { toast(err.message, true); busy(e.target, false); }
    });
  }
  async function loadPersonal() {
    const steps = WRITING_STEPS(interestName());
    let i = 0;
    clearInterval(statusTimer);
    statusTimer = setInterval(() => { const el = $("#wstatus"); if (el) el.textContent = steps[Math.min(++i, steps.length - 1)]; }, 2200);
    if (personalLoading) return;
    personalLoading = true;
    try { personal = (await api(`personal/${id}`, {})).content; }
    catch (err) { toast("Couldn't personalise this one: " + err.message, true); lessonMode = "orig"; }
    personalLoading = false;
    clearInterval(statusTimer);
    if (read.isConnected) drawRead();
  }
  async function getHint() {
    try {
      const r = await api(`exercise/${id}/hint`, {});
      hints = r.hints; drawRead();
      if (isNarrow()) setPane("read");
      const hc = $("#hint-count"); if (hc) hc.textContent = `${hints.length}/${r.total}`;
      $(".ws-read").scrollTop = $(".ws-read").scrollHeight;
    } catch (err) { toast(err.message, true); }
  }
  drawRead();
  if (d.personal_available) {
    let x0 = null, y0 = null;
    const pane = $(".ws-read");
    pane.addEventListener("touchstart", (e) => { x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; }, { passive: true });
    pane.addEventListener("touchend", (e) => {
      if (x0 === null) return;
      const dx = e.changedTouches[0].clientX - x0, dy = e.changedTouches[0].clientY - y0;
      x0 = null;
      if (Math.abs(dx) < 70 || Math.abs(dx) < Math.abs(dy) * 1.5) return;
      const want = dx < 0 ? "you" : "orig";
      if (want !== lessonMode) { lessonMode = want; drawRead(); pane.scrollTop = 0; }
    }, { passive: true });
  }

  /* right bottom: results / output / tutor / feedback */
  const dockBody = $("#dock-body");
  function tabsList() {
    const t = [];
    if (predict) t.push(["answer", "Your answer"]);
    t.push(["results", "Results"]);
    t.push(["output", "Output"]);
    if (!noHelp) t.push(["tutor", `Tutor${chat.length ? `<span class="n">${chat.length / 2}</span>` : ""}`]);
    if (!predict) t.push(["feedback", "Feedback"]);
    return t;
  }
  function drawDock() {
    $("#dock-tabs").innerHTML = tabsList().map(([k, label]) => `<button data-t="${k}" class="${dockTab === k ? "on" : ""}">${label}</button>`).join("") + `<span class="grow"></span>`;
    $$("#dock-tabs button").forEach((b) => b.onclick = () => { dockTab = b.dataset.t; drawDock(); });
    if (dockTab === "answer") {
      dockBody.innerHTML = `<p class="dim small" style="margin-top:0">Type exactly what the program prints, one line per line. Then press Check.</p>
        <textarea id="predict" class="predict-box" spellcheck="false" rows="5" placeholder="Type the output here…">${esc(answer)}</textarea>`;
      $("#predict").oninput = (e) => { answer = e.target.value; };
      $("#predict").focus();
    } else if (dockTab === "results") {
      dockBody.innerHTML = resultsHTML(lastResult, lastResult?._extra || "");
      $("#res-hint", dockBody)?.addEventListener("click", (e) => { e.preventDefault(); getHint(); });
      $("#res-feedback", dockBody)?.addEventListener("click", (e) => { e.preventDefault(); dockTab = "feedback"; drawDock(); });
    } else if (dockTab === "output") {
      dockBody.innerHTML = `<pre class="out">${outputHTML}</pre>` + (predict ? "" :
        `<div class="stdin-row"><input type="text" id="stdin" placeholder="input for Run (\\n = new line)" value="${esc(stdin)}"><input type="text" id="args" placeholder="command-line args" style="max-width:200px" value="${esc(args)}"></div>`);
      $("#stdin")?.addEventListener("input", (e) => { stdin = e.target.value; });
      $("#args")?.addEventListener("input", (e) => { args = e.target.value; });
    } else if (dockTab === "tutor") {
      dockBody.innerHTML = aiOn() ? `${chatHTML(chat, "Stuck or confused? Ask about the lesson, an error message, or your approach. The tutor explains and teaches, but won't write the answer for you.")}
        <div class="chat-input"><textarea id="ask" rows="2" placeholder="Enter sends, Shift+Enter for a new line"></textarea><button class="btn primary" id="ask-btn">Ask</button></div>
        ${chat.length ? `<button class="btn ghost small" id="clear-chat" style="margin-top:8px">Clear conversation</button>` : ""}` : noAI("The tutor");
      renderRich(dockBody);
      const ask = $("#ask", dockBody);
      if (ask) {
        const send = async () => {
          const msg = ask.value.trim(); if (!msg) return;
          busy($("#ask-btn"), true); ask.disabled = true;
          try { chat = (await api("ai/tutor", { item_id: id, message: msg, files: ed.files(), result: lastResult })).chat; drawDock(); dockBody.scrollTop = dockBody.scrollHeight; }
          catch (err) { toast(err.message, true); busy($("#ask-btn"), false); ask.disabled = false; }
        };
        $("#ask-btn").onclick = send;
        ask.onkeydown = (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } };
        ask.focus();
        $("#clear-chat", dockBody)?.addEventListener("click", async () => { await api("ai/tutor/clear", { item_id: id }); chat = []; drawDock(); });
      }
    } else if (dockTab === "feedback") {
      drawFeedback();
    }
  }
  function drawFeedback() {
    if (!feedback) {
      dockBody.innerHTML = `<p class="dim">Once your code passes, this is where you'll get a code-quality score from Jev, suggestions, a reference solution to compare with, and a senior engineer's take on making it cleaner.</p>`;
      return;
    }
    const f = feedback;
    let h = "";
    if (f.quality) h += qualityHTML(f.quality);
    else if (!S.settings.jev.enabled) h += `<p class="faint small">Add a Jev key in Settings for an instant code-quality score.</p>`;
    if (f.tips?.length) h += `<h3 style="margin-top:16px">Could be even better</h3><ul>${f.tips.map((t) => `<li style="margin:4px 0">${md(t)}</li>`).join("")}</ul>`;
    if (f.style?.length) h += `<h3 style="margin-top:16px">Style notes</h3><ul>${f.style.map((s) => `<li>${s.line ? `<span class="faint">line ${s.line}</span> ` : ""}${esc(s.message)}</li>`).join("")}</ul>`;
    h += `<p class="dim small" style="margin-top:14px">Your answer is correct, so you can move on. These are just ideas for next time.</p>`;
    if (f.reference) h += `<details style="margin-top:10px"><summary>Compare with a reference solution</summary>${md("```python\n" + f.reference + "\n```")}</details>`;
    if (aiOn()) h += `<div class="row" style="margin-top:14px"><button class="btn small" id="improve-btn">Show me a cleaner way</button><button class="btn small ghost" id="review-btn">Full code review</button></div>`;
    if (improve) h += `<div class="panel" style="margin-top:14px">${md(improve)}</div>`;
    if (reviewData) h += `<div class="panel" style="margin-top:14px">${reviewHTML(reviewData)}</div>`;
    dockBody.innerHTML = h;
    renderRich(dockBody);
    $("#improve-btn", dockBody)?.addEventListener("click", async (e) => {
      busy(e.target, true, "Thinking");
      try { improve = (await api("ai/improve", { item_id: id, files: ed.files() })).advice; drawFeedback(); }
      catch (err) { toast(err.message, true); busy(e.target, false); }
    });
    $("#review-btn", dockBody)?.addEventListener("click", async (e) => {
      busy(e.target, true, "Reviewing");
      try { reviewData = (await api("ai/review", { item_id: id, files: ed.files(), result: lastResult })).review; drawFeedback(); }
      catch (err) { toast(err.message, true); busy(e.target, false); }
    });
  }
  drawDock();

  async function run() {
    const btn = $("#run-btn"); busy(btn, true);
    try {
      const r = predict ? await api(`exercise/${id}/run`, {}) :
        await api(`exercise/${id}/run`, { files: ed.files(), stdin: stdin.replace(/\\n/g, "\n"), args: args.trim() ? args.trim().split(/\s+/) : [] });
      outputHTML = (esc(r.stdout) + (r.stderr ? `<span class="err">${esc(r.stderr)}</span>` : "")) || `<span class="faint">(nothing was printed)</span>`;
      outputHTML += r.timed_out ? `<span class="err">\n[stopped: time limit]</span>` : `<span class="faint">\n[finished, exit code ${r.returncode}]</span>`;
      dockTab = "output"; drawDock();
    } catch (err) { toast(err.message, true); }
    busy(btn, false);
  }
  async function check() {
    const btn = $("#check-btn"); busy(btn, true, "Checking");
    try {
      const payload = predict ? { answer } : { files: ed.files() };
      const r = await api(`exercise/${id}/check`, { ...payload, kind: review ? "review" : "practice", duration_s: timer.secs });
      lastResult = r.result; canReveal = r.can_reveal;
      let extra = "";
      if (r.result.status === "passed") {
        d.state = r.state;
        const q = r.result.quality;
        extra += `<div class="good">${r.state.newly_solved ? burst() : ""}<span class="celebrate">${r.state.newly_solved ? (r.state.first_try ? "Solved on the first try." : "Solved.") : review ? "Review passed. It'll come back later, at a longer gap." : "Still correct."}</span>
          ${q ? ` Code quality ${q.overall}/10.` : ""} ${!predict ? `<a href="#" id="res-feedback">See feedback</a>` : ""}</div>`;
        if (r.exam) extra += `<div class="note">Module test: ${r.exam.solved}/${r.exam.total} solved. ${r.exam.passed ? (r.exam.placed_now ? "<b>Passed. The whole module is marked complete.</b>" : "Passed.") : `You pass at ${Math.ceil(r.exam.total * r.exam.pass_ratio)}.`}</div>`;
        extra += `<div class="row" style="margin-top:12px">${nextId ? `<a class="btn primary" href="#/step/${nextId}">Next step</a>`
          : path?.project && !path.project.passed ? `<a class="btn primary" href="#/project/${path.project.id}">On to the chapter project</a>`
          : `<a class="btn primary" href="${back}">Finish</a>`}</div>`;
        if (predict) { explanation = r.result.explanation; $("#run-btn").disabled = false; }
        else feedback = { reference: r.reference, quality: q, tips: r.tips, style: r.style };
        const dot = $(`.stepdots a[href="#/step/${id}"]`); if (dot) dot.className = "solved here";
        drawRead();
      } else {
        extra += `<div class="note">Not there yet, and that's normal. Read the failing check above.${!noHelp && ex.hint_count && hints.length < ex.hint_count ? ` <a href="#" id="res-hint">Take a hint</a>` : ""}${!noHelp && aiOn() ? ", or ask the Tutor tab" : ""}.${!noHelp && canReveal && !revealed ? " The Show solution option is now open on the left." : ""}</div>`;
        if (!noHelp) drawRead();
      }
      lastResult._extra = extra;
      dockTab = "results"; drawDock();
      if (isNarrow()) setPane("code");
      refreshState().catch(() => {});
    } catch (err) { toast(err.message, true); }
    busy(btn, false);
  }
  $("#run-btn").onclick = run;
  $("#check-btn").onclick = check;
  $("#hint-btn")?.addEventListener("click", getHint);
  $("#reset-btn")?.addEventListener("click", (e) => {
    const b = e.currentTarget;
    if (b.dataset.armed) { ed.set({ "solution.py": ex.starter }); b.textContent = "Reset"; delete b.dataset.armed; }
    else { b.dataset.armed = 1; b.textContent = "Click again to reset"; setTimeout(() => { if (b.isConnected) { b.textContent = "Reset"; delete b.dataset.armed; } }, 3000); }
  });
  const keys = (e) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) { e.preventDefault(); check(); }
    else if (e.key === "Enter" && e.altKey && !predict) { e.preventDefault(); run(); }
  };
  document.addEventListener("keydown", keys);
  cleanup.push(() => document.removeEventListener("keydown", keys));
}

/* ---------------------------------------------------------------- reviews */

async function viewReviews() {
  const d = await api("reviews");
  main.innerHTML = `<div class="page narrow">
    <h1>Reviews</h1>
    <p class="dim" style="margin-top:10px;max-width:64ch">Steps you've solved come back after 1, 3, 7, 16 and 35 days, and each time you rebuild them from a blank file. Passing pushes the next review further out, and failing brings it back tomorrow. That's how "I solved it once" becomes "I know it".</p>
    <section class="section"><h2>Due now</h2>
      ${d.due.length ? `<ol class="steps">${d.due.map((r) => `<li><a href="#/step/${r.id}?review"><span>${esc(r.title)}<span class="sub">${esc(topicOf(r.topic)?.title || r.topic)}</span></span>
        <span class="kind">${r.lapses ? `<span class="pill fail">${r.lapses} lapse${r.lapses > 1 ? "s" : ""}</span>` : ""}</span><span class="dot attempted"></span></a></li>`).join("")}</ol>`
        : `<p class="dim">Nothing due. Solve new steps and they'll show up here later.</p>`}
    </section>
    ${d.upcoming.length ? `<section class="section"><h2>Coming up</h2><table class="ptable">${d.upcoming.map((u) => `<tr><td>${esc(u.title)}</td><td class="faint">${esc(u.next_review)}</td></tr>`).join("")}</table></section>` : ""}
  </div>`;
}

/* ---------------------------------------------------------------- onboarding */

async function viewWelcome(placeFlag) {
  let step = placeFlag ? 3 : S.settings.name ? 2 : 1;
  const render = async () => {
    if (step === 1) {
      main.innerHTML = `<div class="center">
        <h1>Learn Python the way AI engineers use it.</h1>
        <p class="dim">A course in small steps: read a short lesson, write a bit of code, and get it checked straight away. It starts from your very first line of Python and builds up to LLM apps, RAG, evals and agents, in the order job postings ask for them.</p>
        <div class="panel" style="margin-top:26px">
          <label class="field"><span>What should I call you?</span><input type="text" id="name" value="${esc(S.settings.name)}" placeholder="Your first name"></label>
          <label class="field"><span>Daily practice goal (minutes)</span><input type="number" id="goal" min="15" max="480" value="${S.settings.daily_goal}"></label>
          <button class="btn primary" id="next1">Continue</button>
        </div></div>`;
      $("#next1").onclick = async () => { await api("settings", { name: $("#name").value.trim(), daily_goal: +$("#goal").value || 90 }); await refreshState(); step = 2; render(); };
    } else if (step === 2) {
      main.innerHTML = `<div class="center"><h1>Connect an AI</h1>
        <p class="dim">Optional. It powers the tutor, code reviews, the placement report, fresh challenges and project grading. It uses a CLI you're already logged into, so it runs on your existing subscription with no API keys.</p>
        <div id="ai-box" style="margin-top:22px"></div>
        <div class="row" style="margin-top:18px"><button class="btn primary" id="next2">Continue</button><button class="btn ghost" id="back2">Back</button></div></div>`;
      await aiPicker($("#ai-box"));
      $("#next2").onclick = () => { if (aiOn() && !S.settings.profile) location.hash = "#/me?onboarding"; else { step = 3; render(); } };
      $("#back2").onclick = () => { step = 1; render(); };
    } else {
      main.innerHTML = `<div class="center"><h1>Where should you start?</h1>
        <p class="dim">If you already know some Python, the placement test finds out what, one topic at a time, starting with variables. Each topic climbs from a warm-up to an easy exercise to a core question, and every chapter you pass can be skipped.</p>
        <p class="dim">New to all this? Start from the first lesson. Nothing is assumed.</p>
        <div class="row" style="margin-top:22px"><a class="btn primary" href="#/placement">Take the placement test</a>
          <button class="btn" id="start-zero">Start from lesson one</button></div></div>`;
      $("#start-zero").onclick = async () => { await api("settings", { onboarded: true }); await refreshState(); location.hash = "#/home"; };
    }
  };
  render();
}

async function aiPicker(box) {
  box.innerHTML = `<p class="dim"><span class="spin"></span> Looking for installed AI CLIs…</p>`;
  const d = await api("ai/providers");
  let sel = d.current.provider || "none", model = d.current.model || "";
  const draw = () => {
    const p = d.providers.find((x) => x.id === sel);
    box.innerHTML = d.providers.map((pr) => `<div class="provider ${sel === pr.id ? "sel" : ""} ${pr.installed ? "" : "off"}" data-id="${pr.id}">
        <input type="radio" name="prov" ${sel === pr.id ? "checked" : ""} ${pr.installed ? "" : "disabled"}>
        <div><b>${esc(pr.label)}</b><div class="dim small">${esc(pr.detail)}</div></div>
        <span class="pill ${pr.installed ? "pass" : ""}">${pr.installed ? "installed" : "not found"}</span></div>`).join("") +
      `<div class="provider ${sel === "none" ? "sel" : ""}" data-id="none"><input type="radio" name="prov" ${sel === "none" ? "checked" : ""}>
        <div><b>No AI</b><div class="dim small">All the lessons, exercises and checks still work offline.</div></div><span></span></div>` +
      (p ? `<label class="field" style="margin-top:14px"><span>Model (optional)</span>
        ${p.models.length ? `<select id="model"><option value="">Default</option>${p.models.map((m) => `<option ${m === model ? "selected" : ""}>${esc(m)}</option>`).join("")}</select>`
          : `<input type="text" id="model" value="${esc(model)}" placeholder="Leave empty for the CLI's default">`}</label>` : "") +
      `<div class="row"><button class="btn" id="ai-save">${sel === "none" ? "Save" : "Test & save"}</button><span id="ai-msg" class="dim small"></span></div>`;
    $$(".provider", box).forEach((el) => el.onclick = () => {
      if (el.classList.contains("off")) return;
      sel = el.dataset.id; model = sel === d.current.provider ? d.current.model : (d.providers.find((x) => x.id === sel)?.default_model || ""); draw();
    });
    $("#model", box)?.addEventListener("change", (e) => { model = e.target.value; });
    $("#ai-save", box).onclick = async (e) => {
      model = $("#model", box)?.value ?? "";
      const msg = $("#ai-msg", box);
      if (sel !== "none") {
        busy(e.target, true, "Testing");
        msg.textContent = "Sending a test message. The first one can take 10–30 seconds.";
        try { const t = await api("ai/test", { provider: sel, model }); if (!t.ok) throw new Error("Unexpected reply: " + t.reply); }
        catch (err) { busy(e.target, false); msg.innerHTML = `<span style="color:var(--fail)">${esc(err.message)}</span>`; return; }
        busy(e.target, false);
      }
      await api("settings", { ai: { provider: sel, model } });
      d.current = { provider: sel, model };
      await refreshState();
      msg.innerHTML = `<span style="color:var(--pass)">${sel === "none" ? "Saved. AI features are off." : "Connected and saved."}</span>`;
    };
  };
  draw();
}

/* ---------------------------------------------------------------- placement */

const OUTCOME_LABEL = { placed: ["pass", "tested out"], partial: ["warn", "mostly"], basics: ["warn", "basics only"], unknown: ["fail", "not yet"] };

async function viewPlacement() {
  let d = await api("placement");
  if (d.status === "none") d = await api("placement/start", {});
  if (d.status === "done") { await refreshState(); return placementReport(d); }
  const topicN = Math.min(d.topic_index + 1, d.topics_total);
  const pct = Math.round((d.topic_index / d.topics_total) * 100);
  main.innerHTML = `<div class="page narrow">
    <h1>Placement test</h1>
    <p class="dim" style="margin-top:10px">It goes through the course in order, one topic at a time, starting with Python basics. Each topic climbs three steps: a <b>warm-up</b>, an <b>easy</b> exercise, then a <b>core question</b>, and you only go up when you pass. Pass the core question and you can skip that chapter. Every question says exactly what to write, shows example results and lists what gets checked.</p>
    <p class="dim">"I don't know this yet" is a perfectly good answer. It can be long if you know a lot, so stop whenever you like.</p>
    <div class="panel" style="margin:22px 0">
      ${d.ready_to_finish
        ? `<h2>${d.stopped_early ? "Looks like your current edge" : "All topics done"}</h2>
           <p class="dim" style="margin-top:6px">${d.stopped_early ? "Several topics in a row were out of reach, so the test paused. If you think you know later topics (they don't all depend on these), keep going. Otherwise, finish and start learning from here." : "You went through every topic."}</p>
           <div class="row">${d.stopped_early ? `<button class="btn" id="keep-going">Keep going with the next topics</button>` : ""}<button class="btn primary" id="finish">Finish and get my report</button></div>`
        : `<div class="row between"><div><div class="faint small">Topic ${topicN} of ${d.topics_total} · step ${d.next_step} of ${d.next_steps} (${esc(d.next_stage)})</div>
             <h2 style="margin-top:4px">${esc(d.next_topic)}</h2></div>
             <a class="btn primary" href="#/placement/${d.next}">${d.items.length ? "Continue" : "Start"}</a></div>
           <div class="bar" style="margin-top:14px"><i style="width:${pct}%"></i></div>
           ${d.items.length ? `<button class="btn ghost small" id="finish" style="margin-top:14px">Stop here and get my report</button>` : ""}`}
    </div>
    ${d.items.length ? `<h3 style="margin-bottom:8px">Answered so far</h3><table class="ptable">${d.items.map((i) => `<tr>
      <td>${esc(i.topic_title)} <span class="faint small">· ${esc(i.title)}</span></td>
      <td>${i.quality ? `<span class="faint small">quality ${i.quality.overall}/10</span>` : ""}</td>
      <td>${i.skipped ? `<span class="pill">not yet</span>` : `<span class="pill ${i.passed ? "pass" : "fail"}">${esc(i.score)}</span>`}</td></tr>`).join("")}</table>` : ""}
  </div>`;
  $("#keep-going")?.addEventListener("click", async (e) => {
    busy(e.target, true);
    try { const r = await api("placement/continue", {}); location.hash = r.next ? "#/placement/" + r.next : "#/placement"; }
    catch (err) { toast(err.message, true); busy(e.target, false); }
  });
  const fin = $("#finish");
  if (fin) fin.onclick = async (e) => {
    busy(e.target, true, aiOn() ? `${aiName()} is assessing your code (up to 2 minutes)` : "Scoring");
    try { await api("placement/finish", {}); await refreshState(); viewPlacement(); }
    catch (err) { toast(err.message, true); busy(e.target, false); }
  };
}

function placementReport(d) {
  const r = d.report || {};
  const list = (arr) => arr?.length ? `<ul>${arr.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>` : `<p class="dim">–</p>`;
  const outcomes = r.outcomes || {};
  main.innerHTML = `<div class="page narrow">
    <div class="crumbs"><a href="#/progress">Progress</a></div>
    <div class="row between" style="align-items:flex-end"><div><h1>${esc(r.level || "Placement report")}</h1><p class="dim" style="margin:6px 0 0">Finished ${fmtDate(d.finished_at)}${r.ai ? " · assessed by " + esc(aiName()) : ""}</p></div>
      <div class="today-meter"><div class="stat"><b>${esc(r.score ?? "–")}</b><span>score / 100</span></div><div class="stat"><b>${Object.values(outcomes).filter((o) => o === "placed").length}</b><span>chapters tested out</span></div></div></div>
    ${r.ai_error ? `<div class="note">The AI assessment failed (${esc(r.ai_error)}), so this is the offline report.</div>` : ""}
    <div class="panel" style="margin-top:22px">${md(r.summary || "")}${r.code_quality ? `<h3 style="margin-top:14px">How you write code</h3>${md(r.code_quality)}` : ""}</div>
    <div class="grid2" style="margin-top:14px"><div class="panel"><h3>Strengths</h3>${list(r.strengths)}</div><div class="panel"><h3>Gaps</h3>${list(r.gaps)}</div></div>
    ${r.first_week?.length ? `<div class="panel" style="margin-top:14px"><h3>Your first week</h3><ol>${r.first_week.map((x) => `<li>${esc(x)}</li>`).join("")}</ol></div>` : ""}
    <div class="panel" style="margin-top:14px"><h3>Per topic</h3><table class="ptable">${S.topics.map((t) => {
      const o = outcomes[t.id], lab = o ? OUTCOME_LABEL[o] : ["", "not reached"], note = r.topics?.[t.id]?.note;
      return `<tr><td><a href="#/chapter/${t.id}">${esc(t.title)}</a>${note ? `<div class="dim small">${esc(note)}</div>` : ""}</td><td><span class="pill ${lab[0]}">${lab[1]}</span></td></tr>`;
    }).join("")}</table></div>
    <div class="row" style="margin-top:22px"><a class="btn primary" href="#/home">Start learning</a><button class="btn ghost" id="retake">Retake placement</button></div></div>`;
  $("#retake").onclick = async () => { await api("placement/start", {}); viewPlacement(); };
}

async function viewPlacementQuestion(exId) {
  const pl = await api("placement");
  if (pl.status !== "in_progress") { location.hash = "#/placement"; return; }
  if (pl.next !== exId) { location.hash = pl.next ? "#/placement/" + pl.next : "#/placement"; return; }
  const d = await api("exercise/" + exId);
  const ex = d.exercise;
  const topicN = Math.min(pl.topic_index + 1, pl.topics_total);
  main.innerHTML = `<div class="page wide"><div class="ws" style="${modColor(d.module)}">
    <div class="ws-top"><a class="btn small ghost" href="#/placement">←</a>
      <span class="ttl">Placement · topic ${topicN} of ${pl.topics_total} · <b>${esc(pl.next_topic)}</b></span><span style="flex:1"></span>
      <span class="pill ${pl.next_stage === "core" ? "warn" : ""}">Step ${pl.next_step} of ${pl.next_steps}: ${esc(pl.next_stage)}</span></div>
    <section class="ws-read"><div class="ws-read-in"><h1>${esc(ex.title)}</h1>
      <div class="task">${md(ex.prompt)}${checksHTML(d.checks)}</div><div id="pl-res" style="margin-top:18px"></div></div></section>
    <section class="ws-code">
      <div class="toolbar"><button class="btn" id="run-btn">Run</button><button class="btn primary" id="submit-btn">Submit answer</button>
        <button class="btn ghost" id="skip-btn">I don't know this yet</button><span class="grow"></span><span class="timer" id="timer">0:00</span></div>
      <div class="filetabs"></div><div class="editor" id="editor"></div>
      <div class="dock"><div class="dock-tabs"><button class="on">Output</button></div><div class="dock-body"><pre class="out faint" id="out">Run shows what your code prints. Submit grades it once, then the next question loads.</pre></div></div>
    </section></div></div>`;
  renderRich($(".ws-read"));
  const timer = startTimer($("#timer"));
  const ed = makeEditor($("#editor"), { "solution.py": ex.starter });
  const setPane = paneSwitch($(".ws"), ed.cm, ["Question", "Code"]);
  let done = false;
  $("#run-btn").onclick = async () => {
    try {
      const r = await api(`exercise/${exId}/run`, { files: ed.files() });
      $("#out").classList.remove("faint");
      $("#out").innerHTML = esc(r.stdout) + (r.stderr ? `<span class="err">${esc(r.stderr)}</span>` : "") + `<span class="faint">\n[exit ${r.returncode}]</span>`;
    } catch (err) { toast(err.message, true); }
  };
  const after = (resp) => {
    done = true; $("#submit-btn").disabled = true; $("#skip-btn").disabled = true;
    if (isNarrow()) setPane("read");
    const r = resp.result, q = resp.quality, next = resp.placement.next;
    $("#pl-res").innerHTML = (r ? `<div class="${r.status === "passed" ? "good" : "note"}">${r.status === "passed" ? "Passed" : "Not passed"}: ${r.passed}/${r.total} checks${q ? ` · code quality ${q.overall}/10` : ""}.</div>` : `<div class="note">Noted: not yet.</div>`) +
      `<p class="dim">${next ? "Loading the next question…" : "That's the end of the test. Opening the overview…"}</p>`;
    setTimeout(() => { location.hash = next ? "#/placement/" + next : "#/placement"; }, r ? 1600 : 700);
  };
  const submit = async (skipped) => {
    if (done) return;
    const btn = skipped ? $("#skip-btn") : $("#submit-btn");
    busy(btn, true, skipped ? "" : "Grading");
    try { after(await api("placement/answer", skipped ? { exercise_id: exId, skipped: true } : { exercise_id: exId, files: ed.files(), duration_s: timer.secs })); }
    catch (err) { toast(err.message, true); busy(btn, false); }
  };
  $("#submit-btn").onclick = () => submit(false);
  $("#skip-btn").onclick = () => submit(true);
}

/* ---------------------------------------------------------------- projects */

async function viewProjects() {
  await refreshState();
  const d = await api("projects");
  main.innerHTML = `<div class="page">
    <h1>Portfolio projects</h1>
    <p class="dim" style="max-width:66ch;margin-top:10px">Real AI-engineering builds, the kind the job report says get people hired. Each specifies an interface; you design and write the code in your own editor, then submit. Hidden tests grade the behaviour, and ${aiOn() ? esc(aiName()) : "an AI (if connected)"} grades the quality against a rubric.</p>
    ${S.modules.filter((m) => d.projects.some((p) => p.module === m.id)).map((m) => `<section class="section" style="${modColor(m.id)}">
      <h3 style="color:var(--mc)">Module ${m.number} · ${esc(m.title)}</h3>
      <div style="border-top:1px solid var(--rule);margin-top:10px">${d.projects.filter((p) => p.module === m.id).map((p) => `<a class="list-row" href="#/project/${p.id}">
        <div><h3>${esc(p.title)}</h3><div class="meta"><span>${esc(p.level)}</span><span>~${p.estimated_hours}h</span><span>${p.tags.map(esc).join(", ")}</span></div>
          <div style="margin-top:5px">${p.requires.map((r) => `<span class="req ${r.cleared ? "ok" : "no"}">${r.cleared ? "✓" : "○"} ${esc(r.title)}</span>`).join("&nbsp;&nbsp; ")}</div></div>
        <div style="text-align:right">${p.passed ? `<span class="pill pass">passed</span>` : p.submissions ? `<span class="pill warn">${p.submissions} submission${p.submissions > 1 ? "s" : ""}</span>` : p.ready ? `<span class="pill">ready</span>` : ""}
          ${p.score != null ? `<div class="faint small" style="margin-top:4px">review ${esc(p.score)}/100</div>` : ""}</div></a>`).join("")}</div></section>`).join("")}
    <section class="section"><h2>Chapter projects</h2>
      <p class="dim" style="max-width:66ch">Small builds at the end of every chapter. Do them on your own, with a bit of googling, to finish the chapter.</p>
      ${S.modules.map((m) => { const list = d.chapter_projects.filter((c) => c.module === m.id); return list.length ? `<div style="${modColor(m.id)};margin-top:18px">
        <h3 style="color:var(--mc)">Module ${m.number} · ${esc(m.title)}</h3><table class="ptable">${list.map((c) => `<tr><td><a href="#/project/${c.id}">${esc(c.title)}</a> <span class="faint small">· ${esc(c.chapter_title)}</span></td>
        <td>${c.passed ? `<span class="pill pass">passed</span>` : c.submissions ? `<span class="pill warn">tried</span>` : ""}</td></tr>`).join("")}</table></div>` : ""; }).join("")}
    </section>
  </div>`;
}

async function viewProject(pid) {
  const d = await api("project/" + pid);
  const p = d.project;
  const isMini = p.kind === "mini";
  let tab = "brief", chat = d.chat, subs = d.submissions, current = subs[0] || null, nextChapter = d.next_chapter;
  main.innerHTML = `<div class="page wide"><div class="ws" style="${modColor(p.module)}">
    <div class="ws-top"><a class="btn small ghost" href="${isMini ? `#/chapter/${p.chapter}` : "#/projects"}">←</a><span class="ttl">${isMini ? `${esc(d.chapter_title)} · chapter project` : "Projects"} · <b>${esc(p.title)}</b>${p.level ? ` · ${esc(p.level)}` : ""} · ~${p.estimated_hours}h</span><span style="flex:1"></span></div>
    <section class="ws-read"><div class="ws-read-in"><div class="dock-tabs" id="ptabs" style="padding:0;margin-bottom:16px"></div><div id="pbody"></div></div></section>
    <section class="ws-code">
      <div class="toolbar"><button class="btn" id="prun-btn" title="Alt+Enter">Run <kbd>Alt+⏎</kbd></button>
        <button class="btn primary" id="submit-btn">Submit for grading</button>
        <button class="btn ghost" id="upload-btn">Upload files</button><input type="file" id="file-in" multiple accept=".py,.txt,.md,.json,.jsonl" class="hidden">
        <span class="grow"></span><button class="btn ghost small" id="scaffold-btn" title="${esc(d.folder)}">${d.folder_exists ? "Folder ready" : "Create project folder"}</button>
        <button class="btn ghost small" id="load-btn">Load from folder</button></div>
      <div class="filetabs" id="filetabs"></div><div class="editor" id="editor"></div>
      <div class="dock" id="pdock"><div class="dock-grip"></div>
        <div class="dock-tabs"><button class="on">Output</button><span class="grow"></span><span class="faint small" style="padding-right:6px">runs the file you're viewing</span></div>
        <div class="dock-body"><pre class="out" id="pout"><span class="faint">Press Run (Alt+Enter) to run the file you're viewing and see what it prints. Add a few print(...) calls at the bottom to try your functions, like in "Try it yourself". Submit runs the hidden checks.</span></pre>
          <div class="stdin-row"><input type="text" id="pstdin" placeholder="input for Run (\\n = new line)"><input type="text" id="pargs" placeholder="command-line args" style="max-width:200px"></div>
          <p class="faint small" style="margin:10px 0 0">Work here or in your own editor under <code>${esc(d.folder)}</code>. Drop files on this side to upload them.</p></div></div>
    </section></div></div>`;
  let saveT;
  const ed = makeEditor($("#editor"), d.draft || p.starter_files, () => {
    clearTimeout(saveT); saveT = setTimeout(() => api("draft", { item_id: "project:" + pid, files: ed.files() }).catch(() => {}), 800);
  });
  cleanup.push(() => clearTimeout(saveT));
  const setPane = paneSwitch($(".ws"), ed.cm, ["Brief", "Code"]);
  const drawTabs = () => {
    $("#filetabs").innerHTML = ed.names().map((n) => `<button class="${n === ed.active ? "on" : ""}" data-f="${esc(n)}">${esc(n)}</button>`).join("");
    $$("#filetabs button").forEach((b) => b.onclick = () => { ed.show(b.dataset.f); drawTabs(); });
  };
  drawTabs();
  const loadFiles = (files) => { ed.set(files); drawTabs(); api("draft", { item_id: "project:" + pid, files: ed.files() }).catch(() => {}); toast(`Loaded ${Object.keys(files).join(", ")}`); };
  const body = $("#pbody");
  function render() {
    $("#ptabs").innerHTML = [["brief", "Brief"], ["explore", "Explore"], ["results", `Results${subs.length ? `<span class="n">${subs.length}</span>` : ""}`], ["tutor", "Tutor"]]
      .map(([k, l]) => `<button data-t="${k}" class="${tab === k ? "on" : ""}">${l}</button>`).join("");
    $$("#ptabs button").forEach((b) => b.onclick = () => { tab = b.dataset.t; render(); });
    if (tab === "brief") {
      body.innerHTML = md(p.brief) + `<h3 style="margin-top:24px">Files to submit</h3><p>${p.files.map((f) => `<code>${esc(f)}</code>`).join(" ")}</p>
        <h3 style="margin-top:16px">How it's graded</h3><ul>${p.rubric.map((r) => `<li>${esc(r)}</li>`).join("")}</ul>`;
    } else if (tab === "explore") {
      body.innerHTML = md(p.explore);
    } else if (tab === "results") {
      if (!current) { body.innerHTML = `<p class="dim">No submissions yet.</p>`; return; }
      const r = current.result, style = Object.entries(r.style || {}).filter(([, v]) => v.length);
      const doneNote = isMini && r.status === "passed" ? `<div class="good"><span class="celebrate">Chapter project passed.</span> ${esc(d.chapter_title)} is complete.
        ${nextChapter ? ` <a class="btn primary small" href="#/chapter/${nextChapter.id}">Next chapter: ${esc(nextChapter.title)}</a>` : ""}</div>` : "";
      body.innerHTML = doneNote + `${subs.length > 1 ? `<select id="sub-sel" style="width:auto;margin-bottom:14px">${subs.map((s) => `<option value="${s.id}" ${s.id === current.id ? "selected" : ""}>Submission ${fmtDate(s.created_at)} · ${s.result.passed}/${s.result.total}</option>`).join("")}</select>` : ""}
        ${resultsHTML(r)}
        ${style.length ? `<h3 style="margin-top:18px">Style notes</h3>${style.map(([f, notes]) => `<p><code>${esc(f)}</code></p><ul>${notes.map((s) => `<li>${s.line ? `<span class="faint">line ${s.line}</span> ` : ""}${esc(s.message)}</li>`).join("")}</ul>`).join("")}` : ""}
        <h2 style="margin-top:26px">Rubric review</h2>
        ${current.review ? projectReviewHTML(current.review) : aiOn() ? `<p class="dim">A senior engineer's review of this submission against the rubric.</p><button class="btn primary" id="rv-btn">Review this submission</button>` : noAI("Rubric review")}`;
      $("#sub-sel", body)?.addEventListener("change", (e) => { current = subs.find((s) => s.id === +e.target.value); render(); });
      $("#rv-btn", body)?.addEventListener("click", async (e) => {
        busy(e.target, true, "Reviewing (up to 2 minutes)");
        try { current.review = (await api(`project/${pid}/review`, { submission_id: current.id })).review; render(); }
        catch (err) { toast(err.message, true); busy(e.target, false); }
      });
    } else if (tab === "tutor") {
      body.innerHTML = aiOn() ? `${chatHTML(chat, "Ask about the design, a concept or an error.")}<div class="chat-input"><textarea id="ask" rows="2"></textarea><button class="btn primary" id="ask-btn">Ask</button></div>` : noAI("The tutor");
      const ask = $("#ask", body);
      if (ask) {
        const send = async () => {
          const msg = ask.value.trim(); if (!msg) return;
          busy($("#ask-btn"), true);
          try { chat = (await api("ai/tutor", { item_id: "project:" + pid, message: msg, files: ed.files(), result: current?.result })).chat; render(); }
          catch (err) { toast(err.message, true); busy($("#ask-btn"), false); }
        };
        $("#ask-btn").onclick = send;
        ask.onkeydown = (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } };
      }
    }
    renderRich(body);
  }
  render();
  makeDock($("#pdock"));
  const runProject = async () => {
    const btn = $("#prun-btn"); busy(btn, true);
    try {
      const args = $("#pargs").value.trim();
      const r = await api(`project/${pid}/run`, { files: ed.files(), file: ed.active, stdin: $("#pstdin").value.replace(/\\n/g, "\n"), args: args ? args.split(/\s+/) : [] });
      $("#pout").innerHTML = (esc(r.stdout) + (r.stderr ? `<span class="err">${esc(r.stderr)}</span>` : "")) ||
        `<span class="faint">(${esc(ed.active)} ran but printed nothing. Add print(...) calls to see your results.)</span>`;
      $("#pout").innerHTML += r.timed_out ? `<span class="err">\n[stopped: time limit]</span>` : `<span class="faint">\n[${esc(ed.active)} finished, exit code ${r.returncode}]</span>`;
    } catch (err) { toast(err.message, true); }
    busy(btn, false);
  };
  $("#prun-btn").onclick = runProject;
  const pkeys = (e) => { if (e.key === "Enter" && e.altKey) { e.preventDefault(); runProject(); } };
  document.addEventListener("keydown", pkeys);
  cleanup.push(() => document.removeEventListener("keydown", pkeys));
  $("#submit-btn").onclick = async (e) => {
    busy(e.target, true, "Running hidden tests");
    try {
      const r = await api(`project/${pid}/submit`, { files: ed.files() });
      const sub = { id: r.submission_id, created_at: new Date().toISOString(), result: r.result, review: null };
      nextChapter = r.next_chapter;
      subs.unshift(sub); current = sub; tab = "results"; render();
      if (isNarrow()) setPane("read");
    } catch (err) { toast(err.message, true); }
    busy(e.target, false);
  };
  $("#scaffold-btn").onclick = async (e) => { const r = await api(`project/${pid}/scaffold`, {}); e.target.textContent = "Folder ready"; toast(r.written.length ? `Created ${r.folder} with starter files and BRIEF.md` : `${r.folder} is ready (existing files kept)`); };
  $("#load-btn").onclick = async () => { try { loadFiles((await api(`project/${pid}/load-folder`, {})).files); } catch (err) { toast(err.message, true); } };
  const readFiles = async (list) => { const files = {}; for (const f of list) files[f.name] = await f.text(); if (Object.keys(files).length) loadFiles(files); };
  $("#upload-btn").onclick = () => $("#file-in").click();
  $("#file-in").onchange = (e) => readFiles(e.target.files);
  const right = $(".ws-code");
  right.addEventListener("dragover", (e) => { e.preventDefault(); right.style.outline = "2px dashed var(--amber)"; });
  right.addEventListener("dragleave", () => { right.style.outline = ""; });
  right.addEventListener("drop", (e) => { e.preventDefault(); right.style.outline = ""; readFiles(e.dataTransfer.files); });
}

function projectReviewHTML(rv) {
  return `<div class="review stack">
    <div class="row" style="gap:16px;align-items:baseline"><div class="score">${esc(rv.score)}<small>/100</small></div><div>${esc(rv.summary || "")}</div></div>
    ${rv.rubric?.length ? `<table class="ptable">${rv.rubric.map((r) => `<tr><td><b>${esc(r.criterion)}</b><div class="dim small">${esc(r.comment)}</div></td><td>${esc(r.score)}/5</td></tr>`).join("")}</table>` : ""}
    ${rv.strengths?.length ? `<div><h3>Strengths</h3><ul>${rv.strengths.map((s) => `<li>${esc(s)}</li>`).join("")}</ul></div>` : ""}
    ${rv.improvements?.length ? `<div><h3>Improve</h3><ul>${rv.improvements.map((s) => `<li>${esc(s)}</li>`).join("")}</ul></div>` : ""}
    ${rv.next_step ? `<div class="note"><b>Next step:</b> ${esc(rv.next_step)}</div>` : ""}
    <p class="dim">${rv.portfolio_ready ? "Portfolio-ready. Put it on GitHub with a README." : "Not portfolio-ready yet."}</p></div>`;
}

/* ---------------------------------------------------------------- labs */

async function viewLabs() {
  const d = await api("labs");
  main.innerHTML = `<div class="page narrow">
    <h1>Ship it labs</h1>
    <p class="dim" style="margin-top:10px">Things you can only learn in a real terminal: running scripts, virtual environments, uv, secrets and your first real LLM call. Then shipping: an API, a container and CI. Do each mission in your own shell under <code>${esc(d.root)}</code>, then press Check. PyTrainer inspects the result and runs your commands.</p>
    <div class="section">${d.labs.map((lab, i) => `<div class="panel" style="margin-bottom:14px">
      <div class="row between"><h2 style="font-size:21px">${i + 1}. ${esc(lab.title)}</h2>${lab.done ? `<span class="pill pass">done</span>` : ""}</div>
      <div style="margin-top:10px">${md(lab.brief)}</div>
      <ul class="check-list">${lab.checks.map((c, j) => {
        const r = lab.last_result?.checks?.[j];
        return `<li><span class="${r ? (r.passed ? "ok" : "no") : "pending"}">${r ? (r.passed ? "✓" : "✕") : "○"}</span><div>${esc(c)}${r && !r.passed ? `<small>${esc(r.detail)}</small>` : ""}</div></li>`;
      }).join("")}</ul>
      <button class="btn primary" data-lab="${lab.id}" style="margin-top:12px">Check</button></div>`).join("")}</div></div>`;
  $$("[data-lab]").forEach((b) => b.onclick = async () => {
    busy(b, true, "Checking");
    try { await api(`lab/${b.dataset.lab}/check`, {}); const y = main.scrollTop; await viewLabs(); main.scrollTop = y; }
    catch (err) { toast(err.message, true); busy(b, false); }
  });
  highlight(main);
}

/* ---------------------------------------------------------------- progress */

async function viewProgress() {
  await refreshState();
  const st = await api("stats");
  const sm = st.summary;
  const maxN = Math.max(1, ...st.per_day.map((x) => x.n));
  main.innerHTML = `<div class="page">
    <h1>Progress</h1>
    <div class="stat-row" style="margin-top:24px">
      <div class="stat"><b>${sm.solved}</b><span>steps solved of ${sm.total_exercises}</span></div>
      <div class="stat"><b>${sm.topics_cleared}/${sm.topics_total}</b><span>chapters cleared</span></div>
      <div class="stat"><b>${sm.first_try_rate == null ? "–" : Math.round(sm.first_try_rate * 100) + "%"}</b><span>first-try solves</span></div>
      <div class="stat"><b>${sm.avg_quality == null ? "–" : sm.avg_quality + "/10"}</b><span>code quality (last 20)</span></div>
      <div class="stat"><b>${fmtMin(sm.week_minutes)}</b><span>this week</span></div>
      <div class="stat"><b>${sm.streak.current} / ${sm.streak.best}</b><span>streak / best</span></div>
    </div>
    <section class="section"><h2>Activity</h2><div class="panel">${heatmap(st.heatmap)}
      <p class="faint small" style="margin:10px 0 0">A day counts toward your streak with 10+ minutes of practice or at least one solve.</p></div></section>
    ${st.per_day.length ? `<section class="section"><h2>Checks per day</h2><div class="panel"><div style="display:flex;gap:4px;align-items:flex-end;height:110px">${st.per_day.map((x) =>
      `<div title="${x.d}: ${x.p}/${x.n} passing" style="flex:1;max-width:26px;display:flex;flex-direction:column-reverse;height:100%"><div style="height:${(x.p / maxN) * 100}%;background:var(--pass);border-radius:2px 2px 0 0"></div><div style="height:${((x.n - x.p) / maxN) * 100}%;background:color-mix(in srgb,var(--fail) 55%,var(--rule));border-radius:2px 2px 0 0"></div></div>`).join("")}</div>
      <p class="faint small" style="margin:8px 0 0">Green: passing checks. Red: failing ones. Failing is how the checks teach you.</p></div></section>` : ""}
    <section class="section"><h2>By module</h2>${S.modules.map((m) => `<div style="${modColor(m.id)};margin:18px 0">
      <h3 style="color:var(--mc);margin-bottom:6px">${m.number}. ${esc(m.title)}</h3>
      <table class="ptable">${m.chapters.map((c) => `<tr><td><a href="#/chapter/${c.id}">${esc(c.title)}</a></td>
        <td style="width:200px"><div class="bar"><i style="width:${Math.round(c.mastery * 100)}%"></i></div></td>
        <td class="faint small" style="width:90px">${c.done}/${c.steps} steps</td>
        <td style="width:100px">${c.earned ? `<span class="pill pass">cleared</span>` : c.placed ? `<span class="pill">tested out</span>` : ""}</td></tr>`).join("")}</table></div>`).join("")}</section>
    <section class="section grid2" style="align-items:start">
      <div><h2 style="margin-bottom:12px">Recent struggles</h2>${st.weak_spots.length ? `<ul>${st.weak_spots.map((w) => `<li class="dim">${esc(w)}</li>`).join("")}</ul>` : `<p class="dim">No failed checks yet.</p>`}</div>
      <div><h2 style="margin-bottom:12px">Placement</h2>${st.placement ? `<p><b>${esc(st.placement.report?.level || "")}</b> · ${fmtDate(st.placement.finished_at)}</p><a class="btn small" href="#/placement">View report</a>` : `<a class="btn small" href="#/placement">Take the placement test</a>`}</div>
    </section>
    <section class="section"><h2>Recent attempts</h2>${st.recent.length ? `<table class="ptable">${st.recent.map((a) => `<tr><td><a href="#/${a.item_id.startsWith("project:") ? "project/" + a.item_id.slice(8) : "step/" + a.item_id}">${esc(a.title)}</a> <span class="faint small">${esc(a.kind)}</span></td>
      <td class="faint">${fmtDate(a.created_at)}</td><td><span class="pill ${a.status === "passed" ? "pass" : "fail"}">${a.passed}/${a.total}</span></td></tr>`).join("")}</table>` : `<p class="dim">No attempts yet.</p>`}</section>
  </div>`;
}

/* ---------------------------------------------------------------- get to know you (personalisation chat) */

async function viewMe(flag) {
  await refreshState();
  const onboarding = flag === "?onboarding";
  let d = await api("profile");
  let history = d.history, pending = null, busyChat = false, editing = !!d.profile && flag !== "?restart";
  if (flag === "?restart" || (!history.length && d.ai && !editing)) history = (await api("profile/start", { restart: flag === "?restart" })).history;
  const saved = d.profile;

  const done = () => { if (onboarding) location.hash = "#/welcome?place"; else location.hash = "#/home"; };

  function profileForm(p, title, sub) {
    const interests = (p.interests || []).join(", ");
    return `<div class="profile-card">
      <h2>${esc(title)}</h2><p class="dim" style="margin-top:4px">${esc(sub)}</p>
      ${p.summary ? `<p style="margin:12px 0 16px">${esc(p.summary)}</p>` : ""}
      <div class="tagrow" style="margin-bottom:16px">${p.primary_interest ? `<span class="chip main">${esc(p.primary_interest)}</span>` : ""}${(p.interests || []).filter((i) => i.toLowerCase() !== (p.primary_interest || "").toLowerCase()).map((i) => `<span class="chip">${esc(i)}</span>`).join("")}</div>
      <label class="field"><span>Explain things through</span><input type="text" id="pf-primary" value="${esc(p.primary_interest || "")}" placeholder="e.g. cricket (Test matches)"></label>
      <label class="field"><span>Other interests</span><input type="text" id="pf-interests" value="${esc(interests)}" placeholder="comma separated"></label>
      <label class="field"><span>Work or study</span><input type="text" id="pf-profession" value="${esc(p.profession || "")}"></label>
      <label class="field"><span>What you want to build</span><input type="text" id="pf-goal" value="${esc(p.goal || "")}"></label>
      <label class="field"><span>How you like things explained</span><input type="text" id="pf-style" value="${esc(p.analogy_style || "")}" placeholder="e.g. everyday analogies, short and direct"></label>
      <div class="row"><button class="btn primary big" id="pf-save">${onboarding ? "Looks right, let's go" : "Save my profile"}</button>
        ${d.ai ? `<button class="btn ghost" id="pf-chat">${pending ? "Keep chatting" : "Chat again"}</button>` : ""}</div></div>`;
  }

  function render() {
    const last = history[history.length - 1];
    main.innerHTML = `<div class="me">
      <div class="me-head"><img src="icon.svg" alt=""><div><h1>Make it yours</h1><p>${onboarding ? "One quick chat, then we start." : "Your course, explained through what you love."}</p></div></div>
      ${!d.ai ? `<div class="note">Connect an AI in Settings for the chat and personalised lessons. You can still fill in your profile below.</div>${profileForm(saved || {}, "Your profile", "Used to personalise lessons once an AI is connected.")}`
      : editing && saved ? profileForm(saved, "Your profile", "Edit anything, or chat again to rebuild it.")
      : `<div class="convo" id="convo">${history.map((m) => `<div class="bubble ${m.role}">${m.role === "guide" ? md(m.content) : esc(m.content)}</div>`).join("")}
          ${busyChat ? `<div class="bubble guide typing"><i></i><i></i><i></i></div>` : ""}
          ${!busyChat && !pending && last?.role === "guide" && last.options?.length ? `<div class="chips">${last.options.map((o, i) => `<button class="chip" style="animation-delay:${i * 60}ms" data-o="${esc(o)}">${esc(o)}</button>`).join("")}</div>` : ""}
          ${pending ? profileForm(pending, "Here's what I learned about you", "Tweak anything that's off. This shapes how every lesson is explained.") : ""}
        </div>
        ${pending ? "" : `<div class="composer"><div class="box"><textarea id="say" rows="1" placeholder="Type your answer…" ${busyChat ? "disabled" : ""}></textarea>
          <button class="btn primary" id="say-btn" ${busyChat ? "disabled" : ""}>Send</button></div>
          <div class="foot"><span>Enter to send</span>${history.length > 2 ? `<button id="finish">That's enough, build my profile</button>` : `<button id="skip">Skip for now</button>`}</div></div>`}`}
    </div>`;
    renderRich(main);
    const ta = $("#say");
    if (ta) {
      ta.focus();
      ta.oninput = () => { ta.style.height = "auto"; ta.style.height = Math.min(140, ta.scrollHeight) + "px"; };
      ta.onkeydown = (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(ta.value); } };
      $("#say-btn").onclick = () => send(ta.value);
    }
    $$(".chips .chip").forEach((c) => c.onclick = () => send(c.dataset.o));
    $("#finish")?.addEventListener("click", () => send("", true));
    $("#skip")?.addEventListener("click", async () => { if (onboarding) done(); else location.hash = "#/home"; });
    $("#pf-chat")?.addEventListener("click", async () => {
      if (pending) { pending = null; render(); return; }
      history = (await api("profile/start", { restart: true })).history; editing = false; render();
    });
    $("#pf-save")?.addEventListener("click", async (e) => {
      const base = pending || saved || {};
      const profile = { ...base,
        primary_interest: $("#pf-primary").value.trim(), profession: $("#pf-profession").value.trim() || null,
        goal: $("#pf-goal").value.trim() || null, analogy_style: $("#pf-style").value.trim() || null,
        interests: $("#pf-interests").value.split(",").map((x) => x.trim()).filter(Boolean) };
      busy(e.target, true, "Saving");
      try { await api("profile/save", { profile }); await refreshState(); toast("Profile saved. Lessons will now be explained your way"); done(); }
      catch (err) { toast(err.message, true); busy(e.target, false); }
    });
    const convo = $("#convo");
    if (convo) convo.scrollTop = convo.scrollHeight;
  }

  async function send(text, finish = false) {
    text = (text || "").trim();
    if ((!text && !finish) || busyChat) return;
    if (text) history.push({ role: "learner", content: text });
    busyChat = true; render();
    try {
      const r = await api("profile/chat", { message: text, finish });
      history = r.history;
      if (r.done && r.profile) pending = r.profile;
    } catch (err) { toast(err.message, true); }
    busyChat = false; render();
  }
  render();
}

/* ---------------------------------------------------------------- settings */

function drawJev() {
  const box = $("#jev-box"), j = S.settings.jev;
  box.innerHTML = j.configured
    ? `<div class="row between"><div><b>Connected</b> <span class="faint" style="font-family:var(--mono);font-size:13px">${esc(j.masked)}</span></div>
        <div class="row"><label class="row" style="gap:6px;font-size:14px"><input type="checkbox" id="jev-on" ${j.enabled ? "checked" : ""}> Use Jev</label>
        <button class="btn small ghost" id="jev-remove">Remove key</button></div></div>`
    : `<label class="field"><span>TypeSafe API key</span><input type="password" id="jev-key" autocomplete="off" placeholder="Paste your key"></label>
       <div class="row"><button class="btn primary" id="jev-save">Test & save</button><span id="jev-msg" class="dim small"></span></div>`;
  $("#jev-save")?.addEventListener("click", async (e) => {
    busy(e.target, true, "Testing");
    try { await api("jev/key", { key: $("#jev-key").value }); await refreshState(); drawJev(); toast("Jev connected"); }
    catch (err) { busy(e.target, false); $("#jev-msg").innerHTML = `<span style="color:var(--fail)">${esc(err.message)}</span>`; }
  });
  $("#jev-remove")?.addEventListener("click", async () => { await api("jev/key", { remove: true }); await refreshState(); drawJev(); });
  $("#jev-on")?.addEventListener("change", async (e) => { await api("settings", { jev_enabled: e.target.checked }); await refreshState(); });
}

async function viewSettings() {
  await refreshState();
  const theme = (() => { try { return localStorage.getItem("pt-theme") || "auto"; } catch { return "auto"; } })();
  main.innerHTML = `<div class="page narrow">
    <h1>Settings</h1>
    <section class="section"><h2>AI connection</h2><p class="dim">The tutor, code reviews, the placement report, generated challenges and project reviews all run through this.</p><div id="ai-box"></div></section>
    <section class="section"><h2>Personalisation</h2>
      <p class="dim">Lessons are re-told through what you love, and the tutor and feedback know who you are.</p>
      <div class="panel">${S.settings.profile ? `<div class="row between"><div><b>Explained through:</b> ${esc(S.settings.profile.primary_interest || "–")}
          <div class="dim small" style="margin-top:4px">${esc(S.settings.profile.summary || "")}</div></div></div>
        <div class="row" style="margin-top:14px"><label class="row" style="gap:6px;font-size:14px"><input type="checkbox" id="pers-on" ${S.settings.personalise ? "checked" : ""}> Personalise lessons</label>
          <a class="btn small" href="#/me">Edit profile</a><a class="btn small ghost" href="#/me?restart">Chat again</a></div>`
        : `<div class="row between"><span class="dim">No profile yet.</span><a class="btn primary small" href="#/me">Start the chat</a></div>`}</div></section>
    <section class="section"><h2>Jev quality scoring</h2>
      <p class="dim">Jev (TypeSafe) scores your code in about a second on readability, naming, idioms, simplicity and edge cases, and it checks that the tutor never gives answers away. <a href="https://console.typesafe.ai" target="_blank" rel="noopener">Get a key</a></p>
      <div class="panel" id="jev-box"></div></section>
    <section class="section"><h2>You</h2><div class="panel">
      <label class="field"><span>Name</span><input type="text" id="name" value="${esc(S.settings.name)}"></label>
      <label class="field"><span>Daily goal (minutes)</span><input type="number" id="goal" min="15" max="480" value="${S.settings.daily_goal}"></label>
      <label class="field"><span>Theme</span><select id="theme"><option value="auto">Follow system</option><option value="dark">Dark</option><option value="light">Light</option></select></label>
      <button class="btn primary" id="save-me">Save</button></div></section>
    <section class="section"><h2>Your data</h2><div class="panel stack">
      <p class="dim">Stored locally in <code>~/.local/share/pytrainer/pytrainer.db</code>, with daily backups in <code>backups/</code> (the last 14 are kept).</p>
      <div class="row"><button class="btn" id="export">Export as JSON</button><button class="btn" id="retake">Retake placement test</button></div>
      <div class="row"><input type="text" id="reset-confirm" placeholder="Type RESET to erase all progress" style="max-width:280px"><button class="btn" id="reset">Erase everything</button></div>
    </div></section></div>`;
  $("#theme").value = theme;
  $("#pers-on")?.addEventListener("change", async (e) => { await api("settings", { personalise: e.target.checked }); await refreshState(); toast(e.target.checked ? "Personalised lessons on" : "Personalised lessons off"); });
  drawJev();
  await aiPicker($("#ai-box"));
  $("#save-me").onclick = async () => {
    await api("settings", { name: $("#name").value.trim(), daily_goal: +$("#goal").value || 90 });
    const t = $("#theme").value;
    try { t === "auto" ? localStorage.removeItem("pt-theme") : localStorage.setItem("pt-theme", t); } catch {}
    if (t === "auto") delete document.documentElement.dataset.theme; else document.documentElement.dataset.theme = t;
    await refreshState(); toast("Saved");
  };
  $("#export").onclick = async () => {
    const data = await api("export");
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([JSON.stringify(data, null, 1)], { type: "application/json" }));
    a.download = `pytrainer-export-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
  };
  $("#retake").onclick = async () => { await api("placement/start", {}); location.hash = "#/placement"; };
  $("#reset").onclick = async () => {
    try { await api("reset", { confirm: $("#reset-confirm").value }); S = null; location.hash = "#/welcome"; toast("All progress erased (a backup was kept)"); }
    catch (err) { toast(err.message, true); }
  };
}

route();
