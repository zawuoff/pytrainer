import { $, aiName, aiOn, api, busy, cleanup, esc, main, md, toast } from "../core.js";
import { renderRich } from "../blocks.js";
import { makeEditor } from "../workspace.js";

/* ---------------------------------------------------------------- interview mode: solve, follow-ups, debrief */

const clock = (ms) => { const s = Math.max(0, Math.ceil(ms / 1000)); return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`; };
const SCORE_NAMES = { correctness: "Correctness", problem_solving: "Problem solving", communication: "Communication", code_quality: "Code quality" };

export async function viewInterview() {
  const d = await api("interviews");
  main.innerHTML = `<div class="page narrow">
    <h1>Interview mode</h1>
    <p class="dim" style="max-width:64ch;margin-top:10px">A practice coding interview. You get one problem and a clock: solve it, run it as often as you like, then submit once. ${aiOn() ? `Then ${esc(aiName())} plays the interviewer: three follow-up questions about your code (complexity, edge cases, what changes at scale), and a scored debrief.` : "Connect an AI in Settings and it will play the interviewer, with follow-up questions and a scored debrief. Without one you get standard questions to answer on your own."}</p>
    <section class="section"><h2>Start an interview</h2><div class="drill-lengths">${d.lengths.map((m) => `<button class="drill-len" data-m="${m}"><b>${m} min</b>
      <span class="faint small">${m >= 45 ? "a hard problem" : "a medium problem"}</span></button>`).join("")}</div>
      <p class="faint small" style="margin-top:10px">Interviews don't count as practice attempts and don't change your reviews.</p></section>
    ${d.history.length ? `<section class="section"><h2>Past interviews</h2><table class="ptable">${d.history.map((h) => `<tr><td>${esc(h.title)}</td><td class="faint small">${h.tests} checks · ${Math.round((h.seconds || 0) / 60)}/${h.minutes} min</td>
      <td>${h.verdict ? `<span class="pill ${/yes/.test(h.verdict) ? "pass" : "warn"}">${esc(h.verdict)}</span>` : ""}</td><td class="faint small">${esc(h.created_at.slice(0, 10))}</td></tr>`).join("")}</table></section>` : ""}
  </div>`;
  document.querySelectorAll(".drill-len").forEach((b) => b.onclick = async () => {
    try { solve(await api("interview/start", { minutes: +b.dataset.m })); }
    catch (err) { toast(err.message, true); }
  });
}

function solve(iv) {
  const ex = iv.exercise, deadline = Date.now() + iv.minutes * 60000, started = Date.now();
  let submitted = false;
  main.innerHTML = `<div class="page wide iv">
    <div class="drill-bar"><span class="drill-clock" id="iv-clock">${clock(iv.minutes * 60000)}</span><span class="dim">Interview · ${iv.minutes} min</span>
      <span class="grow"></span><button class="btn small" id="iv-run" title="Alt+Enter">Run</button><button class="btn small primary" id="iv-submit">Submit solution</button></div>
    <div class="iv-grid">
      <div class="iv-task"><h2>${esc(ex.title)}</h2><div id="iv-prompt">${md(ex.prompt)}</div></div>
      <div class="iv-work"><div class="drill-editor" id="iv-editor" style="height:340px"></div><pre class="out iv-out" id="iv-out"><span class="faint">Run shows what your file prints. Submit runs the hidden checks, once.</span></pre></div>
    </div></div>`;
  renderRich($("#iv-prompt"));
  const ed = makeEditor($("#iv-editor"), { "solution.py": ex.starter });
  const tick = setInterval(() => {
    const left = deadline - Date.now(), el = $("#iv-clock");
    if (el) { el.textContent = clock(left); el.classList.toggle("low", left < 120000); }
    if (left <= 0 && !submitted) { toast("Time's up: submitting what you have."); submit(); }
  }, 500);
  cleanup.push(() => clearInterval(tick));
  async function run() {
    busy($("#iv-run"), true);
    try {
      const r = await api(`exercise/${ex.id}/run`, { files: ed.files() });
      $("#iv-out").innerHTML = (esc(r.stdout) + (r.stderr ? `<span class="err">${esc(r.stderr)}</span>` : "")) || `<span class="faint">(nothing was printed)</span>`;
    } catch (err) { toast(err.message, true); }
    busy($("#iv-run"), false);
  }
  async function submit() {
    if (submitted) return;
    submitted = true; clearInterval(tick);
    busy($("#iv-submit"), true, "Checking");
    try {
      const r = (await api(`interview/${iv.id}/submit`, { files: ed.files(), seconds: Math.round((Date.now() - started) / 1000) })).result;
      followups(iv, r, ed.files());
    } catch (err) { toast(err.message, true); submitted = false; busy($("#iv-submit"), false); }
  }
  $("#iv-run").onclick = run;
  $("#iv-submit").onclick = submit;
  const keys = (e) => { if (e.key === "Enter" && e.altKey) { e.preventDefault(); run(); } };
  document.addEventListener("keydown", keys);
  cleanup.push(() => document.removeEventListener("keydown", keys));
}

function followups(iv, result, files) {
  const ok = result.status === "passed";
  main.innerHTML = `<div class="page narrow">
    <h1>${ok ? "All checks passed" : `${result.passed} of ${result.total} checks passed`}</h1>
    <details style="margin-top:8px"><summary class="small">Your solution and the checks</summary>
      ${md("```python\n" + (files["solution.py"] || "") + "\n```")}
      <ul class="small">${result.tests.map((t) => `<li>${t.passed ? "✓" : "✕"} ${esc(t.name)}${t.message ? ` <span class="faint">${esc(t.message)}</span>` : ""}</li>`).join("")}</ul>
      ${result.error ? `<div class="errbox">${esc(result.error)}</div>` : ""}</details>
    <section class="section"><h2>Follow-up questions</h2><div id="iv-chat"></div></section>
    <section class="section" id="iv-debrief"></section></div>`;
  renderRich(main);
  if (!aiOn()) return selfReview(iv);
  let transcript = [];
  const draw = (done) => {
    $("#iv-chat").innerHTML = `<div class="chat">${transcript.map((m) => `<div class="msg ${m.role === "interviewer" ? "tutor" : "learner"}"><div class="who">${m.role === "interviewer" ? "Interviewer" : "You"}</div>${esc(m.content).replace(/\n/g, "<br>")}</div>`).join("")}</div>
      ${done ? `<div class="row" style="margin-top:12px"><button class="btn primary" id="iv-db">Get my debrief</button></div>`
        : `<div class="chat-input"><textarea id="iv-ans" rows="3" placeholder="Answer as you would out loud. Enter sends, Shift+Enter for a new line"></textarea><button class="btn primary" id="iv-send">Answer</button></div>`}`;
    const ans = $("#iv-ans");
    if (ans) {
      const send = async () => {
        if (!ans.value.trim()) return;
        busy($("#iv-send"), true, "Listening"); ans.disabled = true;
        try { const r = await api(`interview/${iv.id}/followup`, { answer: ans.value }); transcript = r.transcript; draw(r.done); }
        catch (err) { toast(err.message, true); busy($("#iv-send"), false); ans.disabled = false; }
      };
      $("#iv-send").onclick = send;
      ans.onkeydown = (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } };
      ans.focus();
    }
    $("#iv-db")?.addEventListener("click", async (e) => {
      busy(e.target, true, "Writing your debrief");
      try { drawDebrief((await api(`interview/${iv.id}/debrief`, {})).debrief); e.target.remove(); }
      catch (err) { toast(err.message, true); busy(e.target, false); }
    });
  };
  $("#iv-chat").innerHTML = `<p class="dim">The interviewer is reading your code…</p>`;
  api(`interview/${iv.id}/followup`, {}).then((r) => { transcript = r.transcript; draw(r.done); })
    .catch((err) => { $("#iv-chat").innerHTML = `<div class="errbox">${esc(err.message)}</div>`; selfReview(iv); });
}

function selfReview(iv) {
  $("#iv-debrief").innerHTML = `<h2>Answer these on your own</h2>
    <p class="dim small">Say or write each answer as if an interviewer asked it. Being able to explain your code is half of the interview.</p>
    <ol>${iv.questions.map((q, i) => `<li style="margin:10px 0">${esc(q)}<textarea rows="2" aria-label="Your answer to question ${i + 1}" style="margin-top:6px"></textarea></li>`).join("")}</ol>
    <h3>Check yourself</h3><ul class="small"><li>Could you state the time complexity without hesitating?</li><li>Did you name at least one edge case before running anything?</li><li>Would someone else understand your variable names?</li></ul>
    <a class="btn" href="#/interview">Another interview</a>`;
}

function drawDebrief(r) {
  $("#iv-debrief").innerHTML = `<h2>Debrief <span class="pill ${/yes/.test(r.verdict || "") ? "pass" : "warn"}">${esc(r.verdict || "")}</span></h2>
    <p>${esc(r.summary || "")}</p>
    <div class="panel" style="margin:12px 0">${Object.entries(r.scores || {}).map(([k, v]) => `<div class="qrow"><span>${esc(SCORE_NAMES[k] || k)}</span>
      <div class="bar" style="--mc:${v >= 4 ? "var(--pass)" : v >= 3 ? "var(--amber)" : "var(--fail)"}"><i style="width:${(Number(v) || 0) * 20}%"></i></div><span class="faint">${esc(v)}/5</span></div>`).join("")}</div>
    <div class="grid2"><div><h3>Strengths</h3><ul>${(r.strengths || []).map((s) => `<li>${esc(s)}</li>`).join("")}</ul></div>
      <div><h3>To work on</h3><ul>${(r.to_work_on || []).map((s) => `<li>${esc(s)}</li>`).join("")}</ul></div></div>
    ${r.practice ? `<div class="note"><b>Next:</b> ${esc(r.practice)}</div>` : ""}
    <a class="btn" href="#/interview">Another interview</a>`;
}
