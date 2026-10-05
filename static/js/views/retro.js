import { $, aiOn, api, busy, esc, fmtDate, highlight, main, md, modColor, noAI, toast } from "../core.js";
import { diffHTML, makeEditor, resultsHTML } from "../workspace.js";

/* ---------------------------------------------------------------- look back: your old code, read with new eyes */

const THEN_NOW = { heads: ["Then", "Now"], none: ["(not there before)", "(taken out)"], cls: "dv-thennow" };
const code = (files) => files["solution.py"] ?? Object.values(files).join("\n\n");
const styleList = (notes) => notes.map((s) => `<li>${s.line ? `<span class="faint">line ${s.line}</span> ` : ""}${esc(s.message)}</li>`).join("");

export async function viewRetro() {
  const d = await api("retro");
  const skipped = [];
  main.innerHTML = `<div class="page narrow">
    <div class="crumbs"><a href="#/reviews">Reviews</a></div>
    <h1>Look back</h1>
    <p class="dim" style="max-width:64ch;margin-top:10px">Code you wrote at least ${d.min_days} days ago, exactly as you wrote it. Read it with what you know now: what would you change? Write it down, rewrite it if you like (the step's checks run, but nothing is recorded), then compare then and now.</p>
    <div id="rt-body"></div>
    ${d.history.length ? `<section class="section"><h2>Earlier look-backs</h2><div class="rt-hist">${d.history.map((h) => `<details>
      <summary><span>${esc(h.title)}</span><span class="faint small">${esc(fmtDate(h.created_at))}</span>
        ${h.rewritten ? `<span class="pill ${h.passed ? "pass" : h.passed === 0 ? "fail" : ""}">${h.passed ? "rewritten, passing" : h.passed === 0 ? "rewrite failing" : "rewritten"}</span>` : `<span class="pill">notes</span>`}</summary>
      ${h.notes ? `<p><b>You noted:</b> ${esc(h.notes)}</p>` : ""}${h.review ? md(h.review) : ""}
      <a class="small" href="#/step/${esc(h.item_id)}">Open the step</a></details>`).join("")}</div></section>` : ""}
  </div>`;
  highlight($(".rt-hist") || main);
  show(d.pick, d.available);

  function show(p, available) {
    const body = $("#rt-body");
    if (!p) {
      const day = (iso) => esc(new Date(iso + "T12:00").toLocaleDateString([], { dateStyle: "medium" }));
      body.innerHTML = `<div class="note">${available ? "That's all of them for now: you've skipped the rest."
        : d.next_at ? `Nothing to look back on right now. Solutions come back here ${d.min_days} days after you write them; the next one on <b>${day(d.next_at)}</b>.`
        : d.history.length ? `All caught up. Each step rests ${d.cooldown_days} days after you look back on it, and new ones arrive ${d.min_days} days after you solve them.`
        : `Solutions come back here ${d.min_days} days after you write them. Solve a few steps first.`}</div>`;
      return;
    }
    const old = code(p.files);
    let ed = null, lastCheck = null;
    body.innerHTML = `<section class="section rt">
      <div class="go-kicker" style="${modColor(p.module)}"><span>${esc(p.chapter)}</span> · written ${esc(new Date(p.written_at).toLocaleDateString([], { dateStyle: "medium" }))}, ${p.days_ago} days ago</div>
      <h2 class="go-title">${esc(p.title)}</h2>
      <details class="rt-task"><summary>The task</summary>${md(p.prompt)}</details>
      <pre class="go-code"><code class="language-python">${esc(old)}</code></pre>
      ${p.style.length ? `<div class="note small"><b>A linter would also mention:</b><ul class="go-bad">${styleList(p.style)}</ul></div>` : ""}
      <label class="rt-label" for="rt-notes">What would you change now?</label>
      <textarea id="rt-notes" rows="3" placeholder="Names, structure, an idiom you know now, an edge case it misses…"></textarea>
      <div class="row rt-actions"><button class="btn" id="rt-rewrite">Rewrite it</button><button class="btn primary" id="rt-save">Save and compare</button>
        <span class="grow"></span><button class="btn ghost" id="rt-skip">Show me another</button></div>
      <div id="rt-edit" hidden><div class="drill-editor" id="rt-editor"></div>
        <div class="row" style="margin-top:8px"><button class="btn" id="rt-check">Check <kbd>Ctrl+⏎</kbd></button>
          <button class="btn ghost small" id="rt-reset">Start again from the old code</button></div><div id="rt-res"></div></div>
      <div id="rt-compare"></div></section>`;
    highlight(body);
    $("#rt-skip").onclick = async (e) => {
      skipped.push(p.id);
      busy(e.target, true);
      try { const r = await api("retro/pick", { skip: skipped }); show(r.pick, r.available); }
      catch (err) { toast(err.message, true); busy(e.target, false); }
    };
    $("#rt-rewrite").onclick = () => {
      $("#rt-edit").hidden = false; $("#rt-rewrite").remove();
      ed = makeEditor($("#rt-editor"), { "solution.py": old });
      ed.cm.on("keydown", (cm, e) => { if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) { e.preventDefault(); check(); } });
    };
    $("#rt-reset").onclick = () => ed?.set({ "solution.py": old });
    $("#rt-check").onclick = () => check();

    async function check() {
      const files = ed.files();
      busy($("#rt-check"), true, "Checking");
      try {
        const r = await api(`retro/${p.id}/check`, { files });
        lastCheck = { code: code(files), passed: r.result.status === "passed" };
        $("#rt-res").innerHTML = resultsHTML(r.result);
      } catch (err) { toast(err.message, true); }
      busy($("#rt-check"), false);
      return lastCheck;
    }
    $("#rt-save").onclick = async (e) => {
      const files = ed ? ed.files() : null;
      const rewritten = files && code(files).trim() !== old.trim();
      const notes = $("#rt-notes").value.trim();
      if (!rewritten && !notes) { toast("Write what you'd change, or rewrite it, first."); $("#rt-notes").focus(); return; }
      // A rewrite gets checked before it's saved, so the record says whether it works.
      if (rewritten && lastCheck?.code !== code(files)) await check();
      busy(e.target, true, "Saving");
      try {
        const r = await api(`retro/${p.id}/save`, { attempt: p.attempt, notes, ...(rewritten ? { files, passed: lastCheck?.passed ?? null } : {}) });
        $(".rt-actions").hidden = true; $("#rt-notes").readOnly = true;
        if (ed) ed.cm.setOption("readOnly", true);
        compare(r, rewritten);
      } catch (err) { toast(err.message, true); busy(e.target, false); }
    };

    function compare(r, rewritten) {
      const then = r.style_then.length, now = r.style_now?.length;
      const box = $("#rt-compare");
      box.innerHTML = `<h2 style="margin-top:26px">Then and now</h2>
        ${rewritten ? (r.diff ? diffHTML(r.diff, THEN_NOW) : "") : `<p class="dim">No rewrite this time, just your notes. That counts: noticing is most of it.</p>`}
        ${rewritten && lastCheck ? `<p class="small">${lastCheck.passed ? "✓ The rewrite still passes every check." : "✕ The rewrite doesn't pass every check yet."}</p>` : ""}
        ${rewritten && (then || now) ? `<p class="small dim">Linter notes: ${then} then, ${now} now.</p>` : ""}
        <div class="panel" style="margin-top:14px"><div class="row between"><h3>A second opinion</h3>
          ${aiOn() ? `<button class="btn small" id="rt-ai">Compare them with your AI</button>` : ""}</div>
          <div id="rt-ai-out">${aiOn() ? `<p class="dim small" style="margin:6px 0 0">What got better, what's still worth changing, and what your notes caught or missed.</p>` : noAI("The comparison")}</div></div>
        <div class="row" style="margin-top:16px"><button class="btn primary" id="rt-next">Another one</button><a class="btn ghost" href="#/step/${esc(p.id)}">Open the step</a></div>`;
      $("#rt-ai")?.addEventListener("click", async (e) => {
        busy(e.target, true, "Comparing");
        try { const a = await api("ai/retro", { retro: r.retro }); $("#rt-ai-out").innerHTML = md(a.review); highlight($("#rt-ai-out")); e.target.remove(); }
        catch (err) { toast(err.message, true); busy(e.target, false); }
      });
      $("#rt-next").onclick = async () => { const n = await api("retro/pick", { skip: skipped }); show(n.pick, n.available); window.scrollTo(0, 0); main.scrollTop = 0; };
      box.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }
}
