import { S, api, esc, fmtDate, fmtMin, main, modColor, refreshState } from "../core.js";
import { heatmap } from "../shared.js";

/* ---------------------------------------------------------------- progress */

export async function viewProgress() {
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
