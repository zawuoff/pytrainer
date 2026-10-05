import { $, api, busy, cleanup, esc, main, md, toast } from "../core.js";
import { renderRich } from "../blocks.js";
import { makeEditor } from "../workspace.js";

/* ---------------------------------------------------------------- speed drill: timed rounds of solved easy steps */

const minutes = (s) => `${Math.round(s / 60)} min`;
const clock = (ms) => { const s = Math.max(0, Math.ceil(ms / 1000)); return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`; };

export async function viewDrill() {
  const d = await api("drill");
  main.innerHTML = `<div class="page narrow">
    <div class="crumbs"><a href="#/reviews">Reviews</a></div>
    <h1>Speed drill</h1>
    <p class="dim" style="max-width:64ch;margin-top:10px">Rebuild easy steps you've already solved, one after another, against the clock. It's for fluency: the syntax you know should come out without thinking. Drill checks don't count as attempts and don't change your reviews.</p>
    ${d.enough ? `<section class="section"><h2>Pick a round</h2><div class="drill-lengths">${d.lengths.map((s) => `<button class="drill-len" data-s="${s}">
        <b>${minutes(s)}</b><span class="faint small">${d.best[s] ? `best: ${d.best[s]} solved` : "no rounds yet"}</span></button>`).join("")}</div>
      <p class="faint small" style="margin-top:10px">${d.pool.length} steps in the pool. Ctrl+Enter checks, Alt+S skips.</p></section>`
    : `<div class="note">Solve at least ${d.min} easy steps first (you have ${d.pool.length}). The drill only uses steps you've already solved.</div>`}
    ${d.recent.length ? `<section class="section"><h2>Recent rounds</h2><table class="ptable">${d.recent.map((r) => `<tr><td>${minutes(r.seconds)}</td><td>${r.solved} solved</td><td class="faint">${r.skipped} skipped · best streak ${r.best_streak}</td><td class="faint">${esc(r.created_at.slice(0, 16).replace("T", " "))}</td></tr>`).join("")}</table></section>` : ""}
  </div>`;
  document.querySelectorAll(".drill-len").forEach((b) => b.onclick = () => runRound(+b.dataset.s, d.pool));
}

function runRound(seconds, pool) {
  let i = 0, solved = 0, skipped = 0, streak = 0, bestStreak = 0, checking = false, over = false, abandoned = false;
  const deadline = Date.now() + seconds * 1000;
  const order = [...pool];
  main.innerHTML = `<div class="page narrow drill">
    <div class="drill-bar">
      <span class="drill-clock" id="dr-clock">${clock(seconds * 1000)}</span>
      <span>Solved <b id="dr-solved">0</b></span><span>Streak <b id="dr-streak">0</b></span>
      <span class="grow"></span>
      <button class="btn small ghost" id="dr-skip" title="Alt+S">Skip</button>
      <button class="btn small ghost" id="dr-end">End round</button>
    </div>
    <div class="drill-task"><h2 id="dr-title"></h2><div id="dr-prompt"></div></div>
    <div class="drill-editor" id="dr-editor"></div>
    <div class="row" style="margin-top:10px"><button class="btn primary" id="dr-check">Check <kbd>Ctrl+⏎</kbd></button><span class="small" id="dr-msg"></span></div>
  </div>`;
  const current = () => order[i % order.length];
  const ed = makeEditor($("#dr-editor"), { "solution.py": current().starter });

  function show() {
    const ex = current();
    $("#dr-title").textContent = ex.title;
    $("#dr-prompt").innerHTML = md(ex.prompt);
    renderRich($("#dr-prompt"));
    ed.set({ "solution.py": ex.starter });
    ed.cm.focus();
    $("#dr-msg").textContent = "";
  }
  function counters() {
    $("#dr-solved").textContent = solved;
    $("#dr-streak").textContent = streak;
  }
  function next() { i += 1; show(); counters(); }

  async function check() {
    if (checking || over) return;
    checking = true; busy($("#dr-check"), true, "Checking");
    try {
      const r = (await api("drill/check", { id: current().id, files: ed.files() })).result;
      if (r.status === "passed") {
        solved += 1; streak += 1; bestStreak = Math.max(bestStreak, streak);
        if (!over) next();
      } else {
        const t = r.tests.find((x) => !x.passed);
        $("#dr-msg").innerHTML = `<span style="color:var(--fail)">${esc(r.error ? r.error.split("\n")[0] : `${t?.name}: ${t?.message || "failed"}`)}</span>`;
      }
    } catch (err) { toast(err.message, true); }
    checking = false;
    if ($("#dr-check")) busy($("#dr-check"), false);
    if (over) finish();
  }
  function skip() { if (over) return; skipped += 1; streak = 0; next(); }

  async function finish() {
    if (abandoned) return;
    if (checking) { over = true; return; }
    if (main.dataset.drillDone) return;
    over = true; main.dataset.drillDone = "1";
    clearInterval(tick);
    const r = await api("drill/finish", { seconds, solved, skipped, best_streak: bestStreak }).catch((e) => { toast(e.message, true); return null; });
    delete main.dataset.drillDone;
    main.innerHTML = `<div class="page narrow">
      <h1>${solved} solved in ${minutes(seconds)}</h1>
      ${r?.new_best ? `<div class="good"><span class="celebrate">New personal best.</span> Your previous best was ${r.previous_best}.</div>` : r ? `<p class="dim">Your best for ${minutes(seconds)} is ${r.best[seconds]}.</p>` : ""}
      <table class="ptable" style="margin-top:14px"><tr><td>Solved</td><td>${solved}</td></tr><tr><td>Skipped</td><td>${skipped}</td></tr>
        <tr><td>Best streak</td><td>${bestStreak}</td></tr>${solved ? `<tr><td>Average per step</td><td>${Math.round(seconds / Math.max(1, solved))} s</td></tr>` : ""}</table>
      <div class="row" style="margin-top:18px"><button class="btn primary" id="dr-again">Another round</button><a class="btn ghost" href="#/reviews">Back to reviews</a></div></div>`;
    $("#dr-again").onclick = () => viewDrill();
  }

  const tick = setInterval(() => {
    const left = deadline - Date.now();
    const el = $("#dr-clock");
    if (el) { el.textContent = clock(left); el.classList.toggle("low", left < 30000); }
    if (left <= 0) finish();
  }, 250);
  const keys = (e) => {
    if (over) return;
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) { e.preventDefault(); check(); }
    else if (e.altKey && (e.key === "s" || e.key === "S" || e.code === "KeyS")) { e.preventDefault(); skip(); }
  };
  document.addEventListener("keydown", keys);
  cleanup.push(() => { clearInterval(tick); document.removeEventListener("keydown", keys); over = true; abandoned = true; });
  $("#dr-check").onclick = check;
  $("#dr-skip").onclick = skip;
  $("#dr-end").onclick = finish;
  show();
}
