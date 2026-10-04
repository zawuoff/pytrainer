import { $, S, aiName, aiOn, api, busy, esc, fmtDate, main, md, modColor, refreshState, toast } from "../core.js";
import { renderRich } from "../blocks.js";
import { checksHTML, isNarrow, makeDock, makeEditor, paneSwitch, startTimer } from "../workspace.js";
import { dockLibrary } from "../library.js";

/* ---------------------------------------------------------------- placement */

export const OUTCOME_LABEL = { placed: ["pass", "tested out"], partial: ["warn", "mostly"], basics: ["warn", "basics only"], unknown: ["fail", "not yet"] };

export async function viewPlacement() {
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

export function placementReport(d) {
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

export async function viewPlacementQuestion(exId) {
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
        <button class="btn ghost" id="skip-btn">I don't know this yet</button>
        <button class="btn ghost" id="lib-btn" title="Look up syntax from the chapters you have finished (Ctrl+K)">Library <kbd>Ctrl+K</kbd></button>
        <span class="grow"></span><span class="timer" id="timer">0:00</span></div>
      <div class="filetabs"></div><div class="editor" id="editor"></div>
      <div class="dock" id="pl-dock"><div class="dock-grip"></div><div class="dock-tabs"><button class="on">Output</button><span class="grow"></span></div><div class="dock-body"><pre class="out faint" id="out">Run shows what your code prints. Submit grades it once, then the next question loads.</pre></div></div>
    </section></div></div>`;
  renderRich($(".ws-read"));
  const timer = startTimer($("#timer"));
  const ed = makeEditor($("#editor"), { "solution.py": ex.starter });
  const setPane = paneSwitch($(".ws"), ed.cm, ["Question", "Code"]);
  makeDock($("#pl-dock"));
  const lib = dockLibrary($(".ws"), $("#pl-dock"), { editor: ed.cm, selectTab: () => { if (isNarrow()) setPane("code"); } });
  $("#lib-btn").onclick = () => lib.toggle();
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
