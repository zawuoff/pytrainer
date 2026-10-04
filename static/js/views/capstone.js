import { api, busy, esc, main, toast } from "../core.js";

/* ---------------------------------------------------------------- capstone: five projects, one app, one repo */

export async function viewCapstone() {
  const d = await api("capstone");
  const done = d.stages.filter((s) => s.passed).length;
  const stage = (s, n) => `<li class="cap-stage ${s.passed ? "ok" : ""}">
      <span class="cap-n">${n}</span>
      <div class="cap-body"><a href="#/project/${s.id}"><b>${esc(s.title)}</b></a> <code>${esc(s.file)}</code>
        <p class="dim small">${esc(s.what)}</p></div>
      <div class="cap-st">${s.passed ? `<span class="pill pass">passed ${esc(s.tests)}</span>${s.score != null ? `<div class="faint small">review ${esc(s.score)}/100</div>` : ""}`
        : `<a class="btn small" href="#/project/${s.id}">Open</a>`}</div></li>`;
  main.innerHTML = `<div class="page narrow">
    <div class="crumbs"><a href="#/projects">Projects</a></div>
    <h1>Capstone: Docs Assistant</h1>
    <p class="dim" style="max-width:64ch;margin-top:10px">Five of your projects are the parts of one application. Pass them, wire them together in one last project, and export the result as a repository with a README, your scores and tests, ready to push to GitHub.</p>
    <section class="section"><h2>The parts <span class="faint small">${done} of ${d.stages.length} passed</span></h2>
      <ol class="cap-list">${d.stages.map((s, i) => stage(s, i + 1)).join("")}
        <li class="cap-stage app ${d.app.passed ? "ok" : ""}"><span class="cap-n">6</span>
          <div class="cap-body"><a href="#/project/${d.app.id}"><b>${esc(d.app.title)}</b></a> <code>app.py</code>
            <p class="dim small">The glue: a DocsAssistant that runs on your five modules, exposes them as agent tools, scores itself with your eval harness, and a command line.</p></div>
          <div class="cap-st">${d.app.passed ? `<span class="pill pass">passed ${esc(d.app.tests)}</span>${d.app.score != null ? `<div class="faint small">review ${esc(d.app.score)}/100</div>` : ""}`
            : d.ready ? `<a class="btn small primary" href="#/project/${d.app.id}">Start</a>` : `<span class="faint small">after the five parts</span>`}</div></li>
      </ol></section>
    <section class="section"><h2>Your portfolio repository</h2><div class="panel stack" id="cap-export">
      ${d.ready ? `<p>Writes your passing code to <code>${esc(d.repo)}</code> with a README (architecture diagram, what each part does, your test results and review scores), sample docs, every part's tests with a standard-library runner (<code>python run_tests.py</code>), and ${d.git ? "a git commit" : "everything git needs (git was not found on this machine)"}.${d.app.passed ? "" : " Pass the Docs Assistant project first to include <code>app.py</code> and its command line."}</p>
        <div class="row"><button class="btn primary" id="cap-go">${d.repo_exists ? "Update the repository" : "Create the repository"}</button></div>
        <div id="cap-out"></div>`
      : `<p class="dim">Available once the five parts above have passed. Your code is never changed: the repository gets a copy of your latest passing version of each.</p>`}
    </div></section></div>`;
  const go = document.getElementById("cap-go");
  if (!go) return;
  go.onclick = async () => {
    busy(go, true, "Writing");
    try {
      const r = await api("capstone/export", {});
      document.getElementById("cap-out").innerHTML = `<div class="good small">Wrote ${r.files.length} files to <code>${esc(r.path)}</code>. ${esc(r.git.message)}</div>
        <h3 style="margin-top:14px">Put it on GitHub</h3>
        <p class="dim small">With the GitHub CLI:</p><pre class="outbox">cd "${esc(r.path)}"\ngh repo create docs-assistant --public --source=. --push</pre>
        <p class="dim small">Or create an empty repository on github.com, then:</p><pre class="outbox">cd "${esc(r.path)}"\ngit remote add origin https://github.com/YOUR-NAME/docs-assistant.git\ngit push -u origin main</pre>
        <details style="margin-top:8px"><summary class="small">Files written</summary><p class="faint small">${r.files.map((f) => `<code>${esc(f)}</code>`).join(" ")}</p></details>`;
      go.textContent = "Update the repository";
    } catch (err) { toast(err.message, true); }
    busy(go, false);
  };
}
