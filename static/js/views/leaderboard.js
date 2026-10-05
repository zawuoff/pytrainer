import { api, busy, esc, main, toast } from "../core.js";

/* ---------------------------------------------------------------- eval leaderboard: your Docs Assistant vs fixed questions */

const fmtSettings = (s) => `chunk ${s.max_chars} · overlap ${s.overlap} · threshold ${s.threshold} · k ${s.k}`;

export async function viewLeaderboard() {
  const d = await api("leaderboard");
  main.innerHTML = `<div class="page narrow">
    <div class="crumbs"><a href="#/capstone">Capstone</a></div>
    <h1>Eval leaderboard</h1>
    <p class="dim" style="max-width:64ch;margin-top:10px">Your Docs Assistant answers questions about the docs of a made-up app, Orbit. A question counts as right when <code>ask()</code> cites the document that answers it, or refuses when the docs don't say. The embedder and the model are fixed stand-ins, so only your code and settings change the score.</p>
    <div class="stat-row" style="margin-top:20px">
      <div class="stat"><b>${d.best}</b><span>your best held-out score</span></div>
      <div class="stat"><b>${d.runs.length ? d.runs[0].test : "–"}</b><span>last held-out score</span></div>
      <div class="stat"><b>${d.runs.length ? d.runs[0].dev : "–"}</b><span>last dev score</span></div>
    </div>
    <section class="section"><h2>Tune it</h2><div class="panel stack">
      <p class="small">Add this to your <code>app.py</code> in the capstone project, change the numbers, submit it, and run the eval again. Improving your chunker, search or RAG code counts too.</p>
      <pre class="outbox">EVAL_SETTINGS = {"max_chars": ${d.defaults.max_chars}, "overlap": ${d.defaults.overlap}, "threshold": ${d.defaults.threshold}, "k": ${d.defaults.k}}</pre>
      <p class="dim small"><b>Dev</b> is ${d.dev_questions.length} questions you can see below: tune against them. <b>Held out</b> is ${d.test_count} questions you never see, and it's what the leaderboard ranks. If your dev score climbs but held-out doesn't, your settings fit the dev questions rather than the problem: that's overfitting, the most common way evals mislead.</p>
      <div class="row">${d.ready ? `<button class="btn primary" id="lb-run">Run the eval</button>` : `<span class="dim">Pass <a href="#/project/capstone">the capstone project</a> first.</span>`}</div>
      <div id="lb-out"></div></div></section>
    ${d.runs.length ? `<section class="section"><h2>Your runs</h2><table class="ptable"><tr><th>held out</th><th>dev</th><th>settings</th><th></th></tr>${d.runs.map((r) => `<tr>
      <td><b>${r.test}</b>${r.test === d.best ? ` <span class="pill pass">best</span>` : ""}</td><td>${r.dev}</td><td class="faint small">${esc(fmtSettings(r.settings))}</td><td class="faint small">${esc(r.created_at.slice(0, 16).replace("T", " "))}</td></tr>`).join("")}</table></section>` : ""}
    <section class="section"><h2>The dev questions</h2>
      ${d.last ? `<table class="ptable">${d.last.dev.map((r) => `<tr><td>${r.ok ? "✓" : "✕"} ${esc(r.q)}</td><td class="faint small">${esc(r.outcome)}${r.ok ? "" : r.expected ? ` (answer is in ${esc(r.expected)})` : " (not in the docs)"}</td></tr>`).join("")}</table>`
      : `<ul>${d.dev_questions.map((q) => `<li>${esc(q.q)} <span class="faint small">${q.source ? esc(q.source) : "not in the docs"}</span></li>`).join("")}</ul>`}
      <p class="faint small">The docs: ${d.docs.map((x) => `<code>${esc(x)}</code>`).join(" ")}</p></section>
  </div>`;
  const go = document.getElementById("lb-run");
  if (go) go.onclick = async () => {
    busy(go, true, "Running the eval");
    try {
      const r = await api("leaderboard/run", {});
      document.getElementById("lb-out").innerHTML = `<div class="${r.new_best ? "good" : "note"}">${r.new_best ? `<span class="celebrate">New best!</span> ` : ""}Held out <b>${r.test}</b> · dev <b>${r.dev}</b> · ${r.chunks} chunks · ${esc(fmtSettings(r.settings))}
        <div class="small faint" style="margin-top:6px">Held-out results: ${Object.entries(r.test_outcomes).map(([k, v]) => `${v} ${esc(k)}`).join(", ")}</div></div>`;
      setTimeout(viewLeaderboard, 1600);
    } catch (err) { toast(err.message, true); }
    busy(go, false);
  };
}
