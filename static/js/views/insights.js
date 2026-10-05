import { $, api, esc, main, modColor } from "../core.js";

/* ---------------------------------------------------------------- where it got hard: steps and chapters by trouble */

const SHOW = 15;
const pct = (x) => x == null ? "–" : `${Math.round(x * 100)}%`;
const num = (x) => x == null ? "–" : String(x);
const plural = (n, one, many = one + "s") => `${n} ${n === 1 ? one : many}`;

function stepRow(r, max) {
  const chips = [
    r.fails ? `<span class="pill fail">${plural(r.fails, "failing check")}${r.solved ? " before solving" : ""}</span>` : `<span class="pill pass">first try</span>`,
    r.hints ? `<span class="pill">${r.hints}/${r.hint_count} hints</span>` : "",
    r.revealed ? `<span class="pill warn">solution shown</span>` : "",
    r.tutor ? `<span class="pill">${plural(r.tutor, "tutor question")}</span>` : "",
    r.solved ? "" : `<span class="pill warn">not solved yet</span>`,
  ].join("");
  return `<li class="ins-row" style="${modColor(r.module)}">
    <div class="ins-bar" title="Trouble ${r.trouble}"><i style="width:${Math.max(3, Math.round((r.trouble / max) * 100))}%"></i><b>${r.trouble}</b></div>
    <div class="ins-main"><a href="#/step/${esc(r.id)}"><b>${esc(r.title)}</b></a> <span class="faint small">${esc(r.chapter)}</span>
      <div class="ins-chips">${chips}</div>
      ${r.top_failure ? `<div class="small dim">Failed most on <b>${esc(r.top_failure)}</b>${r.top_failure_n > 1 ? `, ${r.top_failure_n} times` : ""}</div>` : ""}</div></li>`;
}

function csv(rows) {
  const cols = ["id", "title", "chapter", "difficulty", "checks", "fails", "solved", "hints", "hint_count", "revealed", "tutor", "top_failure", "top_failure_n", "trouble"];
  const cell = (v) => { const s = String(v ?? ""); return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s; };
  return [cols.join(","), ...rows.map((r) => cols.map((c) => cell(r[c])).join(","))].join("\n") + "\n";
}

export async function viewInsights() {
  const d = await api("insights");
  const t = d.totals, w = d.weights;
  const hard = d.steps.filter((r) => r.trouble > 0);
  const max = Math.max(1, ...hard.map((r) => r.trouble));
  let all = false;
  main.innerHTML = `<div class="page">
    <div class="crumbs"><a href="#/progress">Progress</a></div>
    <h1>Where it got hard</h1>
    <p class="dim" style="max-width:68ch;margin-top:10px">The steps that took the most failing checks, hints and solution peeks. They're worth another go. And if you write PyTrainer's content, they're the first place to look for an unclear prompt, a hint that doesn't help, or a check that's stricter than the task says.</p>
    ${t.tried ? `<div class="stat-row" style="margin-top:22px">
      <div class="stat"><b>${t.tried}</b><span>steps tried</span></div>
      <div class="stat"><b>${pct(t.first_try)}</b><span>solved first try</span></div>
      <div class="stat"><b>${num(t.fails_per_solve)}</b><span>failing checks per solve</span></div>
      <div class="stat"><b>${num(t.hints_per_solve)}</b><span>hints per solve</span></div>
      <div class="stat"><b>${t.revealed}</b><span>solutions shown</span></div></div>
    <section class="section"><div class="row between"><h2>Steps</h2><button class="btn small ghost" id="ins-csv">Download CSV</button></div>
      ${hard.length ? `<ol class="ins-list" id="ins-steps"></ol><div id="ins-more"></div>` : `<p class="dim">Every step you've tried went through on the first check, without hints. Nothing to see here yet.</p>`}
      ${d.steps.length > hard.length ? `<p class="faint small">${plural(d.steps.length - hard.length, "more step")} solved on the first try, without help.</p>` : ""}</section>
    <section class="section"><h2>Chapters</h2><div class="ins-table"><table class="ptable">
      <tr class="faint small"><td>Chapter</td><td>Solved</td><td>First try</td><td>Fails per solve</td><td>Hints per solve</td><td>Trouble per step</td></tr>
      ${d.chapters.map((c) => `<tr style="${modColor(c.module)}"><td><a href="#/chapter/${esc(c.id)}">${esc(c.title)}</a></td><td>${c.solved}/${c.tried}</td><td>${pct(c.first_try)}</td>
        <td>${num(c.fails_per_solve)}</td><td>${num(c.hints_per_solve)}</td><td><b>${c.trouble}</b></td></tr>`).join("")}</table></div></section>
    <p class="faint small" style="margin-top:22px;max-width:68ch">Trouble adds up ${w.fail} per failing check before the first solve, ${w.hint} per hint, ${w.revealed} for a shown solution, ${w.tutor} per tutor question, and ${w.unsolved} while a step is unsolved. Only practice counts: reviews, drills and rewrites don't. From a terminal: <code>python3 scripts/content_report.py</code>.</p>`
    : `<div class="note" style="margin-top:20px">No checks yet. Solve a few steps and this fills in.</div>`}
  </div>`;
  const draw = () => {
    const list = $("#ins-steps");
    if (!list) return;
    list.innerHTML = (all ? hard : hard.slice(0, SHOW)).map((r) => stepRow(r, max)).join("");
    $("#ins-more").innerHTML = !all && hard.length > SHOW ? `<button class="btn small" id="ins-all">Show all ${hard.length}</button>` : "";
    $("#ins-all")?.addEventListener("click", () => { all = true; draw(); });
  };
  draw();
  $("#ins-csv")?.addEventListener("click", () => {
    const url = URL.createObjectURL(new Blob([csv(d.steps)], { type: "text/csv" }));
    const a = Object.assign(document.createElement("a"), { href: url, download: "pytrainer-steps.csv" });
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
}
