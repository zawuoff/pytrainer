import { $, S, aiOn, api, busy, esc, fmtMin, main, md, modColor, moduleOf, noAI, refreshState, ticks } from "../core.js";
import { heatmap } from "../shared.js";

/* ---------------------------------------------------------------- home */

export function greeting() {
  const h = new Date().getHours();
  const part = h < 5 ? "Late night" : h < 12 ? "Morning" : h < 18 ? "Afternoon" : "Evening";
  return S.settings.name ? `${part}, ${esc(S.settings.name)}` : `${part} session`;
}

export function planItem(p) {
  const href = { project: `#/project/${p.id}`, review: `#/step/${p.id}?review`, exam: `#/exam/${p.id}` }[p.kind] || `#/step/${p.id}`;
  const kind = { review: "Review", exercise: p.difficulty >= 2 ? "Practice" : "Step", project: "Project", exam: "Module test" }[p.kind];
  return `<li><a href="${href}"><span><div class="t">${esc(p.title)}</div><div class="w">${esc(p.why)}</div></span><span class="k">${kind}</span></a></li>`;
}

export async function viewHome() {
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
