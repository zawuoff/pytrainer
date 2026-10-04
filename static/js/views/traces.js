import { $, api, esc, main, toast } from "../core.js";
import { spansHTML } from "../spans.js";

/* ---------------------------------------------------------------- trace viewer: open a traces.jsonl as a waterfall */

export function viewTraces() {
  main.innerHTML = `<div class="page narrow">
    <div class="crumbs"><a href="#/project/agent-tracing">Trace Your Agent</a></div>
    <h1>Trace viewer</h1>
    <p class="dim" style="max-width:64ch;margin-top:10px">Open a <code>traces.jsonl</code> file (one span per line, as the <a href="#/project/agent-tracing">Trace Your Agent</a> project writes) and see it as a waterfall. Each line needs a <code>name</code> and a <code>start</code> and <code>end</code> in seconds; <code>span_id</code>, <code>parent_id</code>, <code>trace_id</code>, <code>status</code> and <code>attributes</code> are used when they're there. Running a file that writes <code>traces.jsonl</code> shows the same view under its output.</p>
    <section class="section"><div class="panel stack">
      <div class="row"><label class="btn" for="tr-file">Open a file</label><input type="file" id="tr-file" accept=".jsonl,.json,.txt,application/json" hidden>
        <button class="btn" id="tr-sample">Try a sample</button><span class="grow"></span><span class="faint small">Nothing leaves your computer.</span></div>
      <textarea id="tr-text" rows="5" spellcheck="false" aria-label="Spans, one JSON object per line" placeholder='Or paste spans here, one per line: {"name": "llm.call", "start": 0.0, "end": 0.25, ...}'></textarea>
      <div class="row"><button class="btn primary" id="tr-show">Show the waterfall</button></div></div></section>
    <div id="tr-out"></div></div>`;
  const show = async (text) => {
    try {
      const r = await api("traces/parse", { text });
      $("#tr-out").innerHTML = summaryHTML(r.spans) + spansHTML(r.spans);
    } catch (err) { toast(err.message, true); }
  };
  $("#tr-show").onclick = () => { if ($("#tr-text").value.trim()) show($("#tr-text").value); else toast("Paste some spans or open a file first."); };
  $("#tr-file").onchange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (file.size > 2_000_000) return toast("That file is too big for the viewer (2 MB at most).", true);
    $("#tr-text").value = "";
    show(await file.text());
  };
  $("#tr-sample").onclick = async () => {
    const r = await api("traces/sample");
    $("#tr-out").innerHTML = summaryHTML(r.spans) + spansHTML(r.spans);
  };
}

/* The questions a trace answers first: where the time went, and what failed. */
function summaryHTML(spans) {
  const byName = new Map();
  for (const s of spans) {
    const e = byName.get(s.name) || { name: s.name, n: 0, ms: 0, errors: 0, max: 0 };
    const ms = (s.end - s.start) * 1000;
    e.n += 1; e.ms += ms; e.max = Math.max(e.max, ms); e.errors += s.status === "error" ? 1 : 0;
    byName.set(s.name, e);
  }
  const rows = [...byName.values()].sort((a, b) => b.ms - a.ms);
  const tokens = spans.reduce((t, s) => s.parent_id ? t : t + (Number(s.attributes?.input_tokens) || 0) + (Number(s.attributes?.output_tokens) || 0), 0);
  return `<section class="section"><h2>By span name</h2><table class="ptable"><tr><th>span</th><th>count</th><th>total</th><th>slowest</th><th>errors</th></tr>
    ${rows.map((r) => `<tr><td><code>${esc(r.name)}</code></td><td>${r.n}</td><td>${Math.round(r.ms)} ms</td><td>${Math.round(r.max)} ms</td><td>${r.errors ? `<span class="err">✕ ${r.errors}</span>` : "0"}</td></tr>`).join("")}</table>
    ${tokens ? `<p class="faint small">Root spans report ${tokens} tokens in total.</p>` : ""}</section>`;
}
