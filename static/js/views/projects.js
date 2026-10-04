import { $, $$, S, aiName, aiOn, anim, api, busy, cleanup, esc, fmtDate, main, md, modColor, noAI, refreshState, toast } from "../core.js";
import { renderRich } from "../blocks.js";
import { chatHTML, isNarrow, makeDock, makeEditor, paneSwitch, resultsHTML } from "../workspace.js";
import { dockLibrary, tabIndicator } from "../library.js";

/* ---------------------------------------------------------------- projects */

export async function viewProjects() {
  await refreshState();
  const d = await api("projects");
  main.innerHTML = `<div class="page">
    <h1>Portfolio projects</h1>
    <p class="dim" style="max-width:66ch;margin-top:10px">Real AI-engineering builds, the kind the job report says get people hired. Each specifies an interface; you design and write the code in your own editor, then submit. Hidden tests grade the behaviour, and ${aiOn() ? esc(aiName()) : "an AI (if connected)"} grades the quality against a rubric.</p>
    <a class="suggest" href="#/capstone" style="margin-top:18px"><b>Capstone: Docs Assistant</b><span>Five of these projects are the parts of one app. Wire them together and export a repository for your GitHub.</span><em>Open the capstone</em></a>
    ${S.modules.filter((m) => d.projects.some((p) => p.module === m.id)).map((m) => `<section class="section" style="${modColor(m.id)}">
      <h3 style="color:var(--mc)">Module ${m.number} · ${esc(m.title)}</h3>
      <div style="border-top:1px solid var(--rule);margin-top:10px">${d.projects.filter((p) => p.module === m.id).map((p) => `<a class="list-row" href="#/project/${p.id}">
        <div><h3>${esc(p.title)}</h3><div class="meta"><span>${esc(p.level)}</span><span>~${p.estimated_hours}h</span><span>${p.tags.map(esc).join(", ")}</span></div>
          <div style="margin-top:5px">${p.requires.map((r) => `<span class="req ${r.cleared ? "ok" : "no"}">${r.cleared ? "✓" : "○"} ${esc(r.title)}</span>`).join("&nbsp;&nbsp; ")}</div></div>
        <div style="text-align:right">${p.passed ? `<span class="pill pass">passed</span>` : p.submissions ? `<span class="pill warn">${p.submissions} submission${p.submissions > 1 ? "s" : ""}</span>` : p.ready ? `<span class="pill">ready</span>` : ""}
          ${p.score != null ? `<div class="faint small" style="margin-top:4px">review ${esc(p.score)}/100</div>` : ""}</div></a>`).join("")}</div></section>`).join("")}
    <section class="section"><h2>Chapter projects</h2>
      <p class="dim" style="max-width:66ch">Small builds at the end of every chapter. Do them on your own, with a bit of googling, to finish the chapter.</p>
      ${S.modules.map((m) => { const list = d.chapter_projects.filter((c) => c.module === m.id); return list.length ? `<div style="${modColor(m.id)};margin-top:18px">
        <h3 style="color:var(--mc)">Module ${m.number} · ${esc(m.title)}</h3><table class="ptable">${list.map((c) => `<tr><td><a href="#/project/${c.id}">${esc(c.title)}</a> <span class="faint small">· ${esc(c.chapter_title)}</span></td>
        <td>${c.passed ? `<span class="pill pass">passed</span>` : c.submissions ? `<span class="pill warn">tried</span>` : ""}</td></tr>`).join("")}</table></div>` : ""; }).join("")}
    </section>
  </div>`;
}

export async function viewProject(pid) {
  const d = await api("project/" + pid);
  const p = d.project;
  const isMini = p.kind === "mini";
  let tab = "brief", chat = d.chat, subs = d.submissions, current = subs[0] || null, nextChapter = d.next_chapter;
  main.innerHTML = `<div class="page wide"><div class="ws" style="${modColor(p.module)}">
    <div class="ws-top"><a class="btn small ghost" href="${isMini ? `#/chapter/${p.chapter}` : "#/projects"}">←</a><span class="ttl">${isMini ? `${esc(d.chapter_title)} · chapter project` : "Projects"} · <b>${esc(p.title)}</b>${p.level ? ` · ${esc(p.level)}` : ""} · ~${p.estimated_hours}h</span><span style="flex:1"></span></div>
    <section class="ws-read"><div class="ws-read-in"><div class="dock-tabs" id="ptabs" style="padding:0;margin-bottom:16px"></div><div id="pbody"></div></div></section>
    <section class="ws-code">
      <div class="toolbar"><button class="btn" id="prun-btn" title="Alt+Enter">Run <kbd>Alt+⏎</kbd></button>
        <button class="btn primary" id="submit-btn">Submit for grading</button>
        <button class="btn ghost" id="upload-btn">Upload files</button><input type="file" id="file-in" multiple accept=".py,.txt,.md,.json,.jsonl" class="hidden">
        <button class="btn ghost" id="lib-btn" title="Look up syntax from the chapters you have finished (Ctrl+K)">Library <kbd>Ctrl+K</kbd></button>
        <span class="grow"></span><button class="btn ghost small" id="scaffold-btn" title="${esc(d.folder)}">${d.folder_exists ? "Folder ready" : "Create project folder"}</button>
        <button class="btn ghost small" id="load-btn">Load from folder</button></div>
      <div class="filetabs" id="filetabs"></div><div class="editor" id="editor"></div>
      <div class="dock" id="pdock"><div class="dock-grip"></div>
        <div class="dock-tabs"><button class="on">Output</button><span class="grow"></span><span class="faint small" style="padding-right:6px">runs the file you're viewing</span></div>
        <div class="dock-body"><pre class="out" id="pout"><span class="faint">Press Run (Alt+Enter) to run the file you're viewing and see what it prints. Add a few print(...) calls at the bottom to try your functions, like in "Try it yourself". Submit runs the hidden checks.</span></pre>
          <div class="stdin-row"><input type="text" id="pstdin" placeholder="input for Run (\\n = new line)"><input type="text" id="pargs" placeholder="command-line args" style="max-width:200px"></div>
          <p class="faint small" style="margin:10px 0 0">Work here or in your own editor under <code>${esc(d.folder)}</code>. Drop files on this side to upload them.</p></div></div>
    </section></div></div>`;
  let saveT;
  const ed = makeEditor($("#editor"), d.draft || p.starter_files, () => {
    clearTimeout(saveT); saveT = setTimeout(() => api("draft", { item_id: "project:" + pid, files: ed.files() }).catch(() => {}), 800);
  });
  cleanup.push(() => clearTimeout(saveT));
  const setPane = paneSwitch($(".ws"), ed.cm, ["Brief", "Code"]);
  const drawTabs = () => {
    $("#filetabs").innerHTML = ed.names().map((n) => `<button class="${n === ed.active ? "on" : ""}" data-f="${esc(n)}">${esc(n)}</button>`).join("");
    $$("#filetabs button").forEach((b) => b.onclick = () => { ed.show(b.dataset.f); drawTabs(); });
  };
  drawTabs();
  const loadFiles = (files) => { ed.set(files); drawTabs(); api("draft", { item_id: "project:" + pid, files: ed.files() }).catch(() => {}); toast(`Loaded ${Object.keys(files).join(", ")}`); };
  const body = $("#pbody");
  function render() {
    $("#ptabs").innerHTML = [["brief", "Brief"], ["explore", "Explore"], ["results", `Results${subs.length ? `<span class="n">${subs.length}</span>` : ""}`], ["tutor", "Tutor"]]
      .map(([k, l]) => `<button data-t="${k}" class="${tab === k ? "on" : ""}">${l}</button>`).join("");
    $$("#ptabs button").forEach((b) => b.onclick = () => { tab = b.dataset.t; render(); anim(body, [{ opacity: 0, transform: "translateY(5px)" }, { opacity: 1, transform: "none" }], { duration: 200 }); });
    tabIndicator($("#ptabs"));
    if (tab === "brief") {
      const builds = d.builds_on ? `<div class="note small"><b>Runs on your own code.</b> Your latest passing version of each of these is placed next to your file: ${d.builds_on.map((b) => `<a href="#/project/${b.id}">${esc(b.title)}</a> <code>${b.files.map(esc).join(", ")}</code> ${b.passed ? "✓" : "<b>(not passed yet)</b>"}`).join(" · ")}. <a href="#/capstone">Capstone overview</a></div>` : "";
      body.innerHTML = builds + md(p.brief) + `<h3 style="margin-top:24px">Files to submit</h3><p>${p.files.map((f) => `<code>${esc(f)}</code>`).join(" ")}</p>
        <h3 style="margin-top:16px">How it's graded</h3><ul>${p.rubric.map((r) => `<li>${esc(r)}</li>`).join("")}</ul>`;
    } else if (tab === "explore") {
      body.innerHTML = md(p.explore);
    } else if (tab === "results") {
      if (!current) { body.innerHTML = `<p class="dim">No submissions yet.</p>`; return; }
      const r = current.result, style = Object.entries(r.style || {}).filter(([, v]) => v.length);
      const doneNote = isMini && r.status === "passed" ? `<div class="good"><span class="celebrate">Chapter project passed.</span> ${esc(d.chapter_title)} is complete.
        ${nextChapter ? ` <a class="btn primary small" href="#/chapter/${nextChapter.id}">Next chapter: ${esc(nextChapter.title)}</a>` : ""}</div>` : "";
      body.innerHTML = doneNote + `${subs.length > 1 ? `<select id="sub-sel" style="width:auto;margin-bottom:14px">${subs.map((s) => `<option value="${s.id}" ${s.id === current.id ? "selected" : ""}>Submission ${fmtDate(s.created_at)} · ${s.result.passed}/${s.result.total}</option>`).join("")}</select>` : ""}
        ${resultsHTML(r)}
        ${style.length ? `<h3 style="margin-top:18px">Style notes</h3>${style.map(([f, notes]) => `<p><code>${esc(f)}</code></p><ul>${notes.map((s) => `<li>${s.line ? `<span class="faint">line ${s.line}</span> ` : ""}${esc(s.message)}</li>`).join("")}</ul>`).join("")}` : ""}
        <h2 style="margin-top:26px">Rubric review</h2>
        ${current.review ? projectReviewHTML(current.review) : aiOn() ? `<p class="dim">A senior engineer's review of this submission against the rubric.</p><button class="btn primary" id="rv-btn">Review this submission</button>` : noAI("Rubric review")}`;
      $("#sub-sel", body)?.addEventListener("change", (e) => { current = subs.find((s) => s.id === +e.target.value); render(); });
      $("#rv-btn", body)?.addEventListener("click", async (e) => {
        busy(e.target, true, "Reviewing (up to 2 minutes)");
        try { current.review = (await api(`project/${pid}/review`, { submission_id: current.id })).review; render(); }
        catch (err) { toast(err.message, true); busy(e.target, false); }
      });
    } else if (tab === "tutor") {
      body.innerHTML = aiOn() ? `${chatHTML(chat, "Ask about the design, a concept or an error.")}<div class="chat-input"><textarea id="ask" rows="2"></textarea><button class="btn primary" id="ask-btn">Ask</button></div>` : noAI("The tutor");
      const ask = $("#ask", body);
      if (ask) {
        const send = async () => {
          const msg = ask.value.trim(); if (!msg) return;
          busy($("#ask-btn"), true);
          try { chat = (await api("ai/tutor", { item_id: "project:" + pid, message: msg, files: ed.files(), result: current?.result })).chat; render(); }
          catch (err) { toast(err.message, true); busy($("#ask-btn"), false); }
        };
        $("#ask-btn").onclick = send;
        ask.onkeydown = (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } };
      }
    }
    renderRich(body);
  }
  render();
  makeDock($("#pdock"));
  const lib = dockLibrary($(".ws"), $("#pdock"), { topic: isMini ? p.chapter : null, editor: ed.cm, selectTab: () => { if (isNarrow()) setPane("code"); } });
  $("#lib-btn").onclick = () => lib.toggle();
  const runProject = async () => {
    const btn = $("#prun-btn"); busy(btn, true);
    try {
      const args = $("#pargs").value.trim();
      const r = await api(`project/${pid}/run`, { files: ed.files(), file: ed.active, stdin: $("#pstdin").value.replace(/\\n/g, "\n"), args: args ? args.split(/\s+/) : [] });
      $("#pout").innerHTML = (esc(r.stdout) + (r.stderr ? `<span class="err">${esc(r.stderr)}</span>` : "")) ||
        `<span class="faint">(${esc(ed.active)} ran but printed nothing. Add print(...) calls to see your results.)</span>`;
      $("#pout").innerHTML += r.timed_out ? `<span class="err">\n[stopped: time limit]</span>` : `<span class="faint">\n[${esc(ed.active)} finished, exit code ${r.returncode}]</span>`;
    } catch (err) { toast(err.message, true); }
    busy(btn, false);
  };
  $("#prun-btn").onclick = runProject;
  const pkeys = (e) => { if (e.key === "Enter" && e.altKey) { e.preventDefault(); runProject(); } };
  document.addEventListener("keydown", pkeys);
  cleanup.push(() => document.removeEventListener("keydown", pkeys));
  $("#submit-btn").onclick = async (e) => {
    busy(e.target, true, "Running hidden tests");
    try {
      const r = await api(`project/${pid}/submit`, { files: ed.files() });
      const sub = { id: r.submission_id, created_at: new Date().toISOString(), result: r.result, review: null };
      nextChapter = r.next_chapter;
      subs.unshift(sub); current = sub; tab = "results"; render();
      if (isNarrow()) setPane("read");
    } catch (err) { toast(err.message, true); }
    busy(e.target, false);
  };
  $("#scaffold-btn").onclick = async (e) => { const r = await api(`project/${pid}/scaffold`, {}); e.target.textContent = "Folder ready"; toast(r.written.length ? `Created ${r.folder} with starter files and BRIEF.md` : `${r.folder} is ready (existing files kept)`); };
  $("#load-btn").onclick = async () => { try { loadFiles((await api(`project/${pid}/load-folder`, {})).files); } catch (err) { toast(err.message, true); } };
  const readFiles = async (list) => { const files = {}; for (const f of list) files[f.name] = await f.text(); if (Object.keys(files).length) loadFiles(files); };
  $("#upload-btn").onclick = () => $("#file-in").click();
  $("#file-in").onchange = (e) => readFiles(e.target.files);
  const right = $(".ws-code");
  right.addEventListener("dragover", (e) => { e.preventDefault(); right.style.outline = "2px dashed var(--amber)"; });
  right.addEventListener("dragleave", () => { right.style.outline = ""; });
  right.addEventListener("drop", (e) => { e.preventDefault(); right.style.outline = ""; readFiles(e.dataTransfer.files); });
}

export function projectReviewHTML(rv) {
  return `<div class="review stack">
    <div class="row" style="gap:16px;align-items:baseline"><div class="score">${esc(rv.score)}<small>/100</small></div><div>${esc(rv.summary || "")}</div></div>
    ${rv.rubric?.length ? `<table class="ptable">${rv.rubric.map((r) => `<tr><td><b>${esc(r.criterion)}</b><div class="dim small">${esc(r.comment)}</div></td><td>${esc(r.score)}/5</td></tr>`).join("")}</table>` : ""}
    ${rv.strengths?.length ? `<div><h3>Strengths</h3><ul>${rv.strengths.map((s) => `<li>${esc(s)}</li>`).join("")}</ul></div>` : ""}
    ${rv.improvements?.length ? `<div><h3>Improve</h3><ul>${rv.improvements.map((s) => `<li>${esc(s)}</li>`).join("")}</ul></div>` : ""}
    ${rv.next_step ? `<div class="note"><b>Next step:</b> ${esc(rv.next_step)}</div>` : ""}
    <p class="dim">${rv.portfolio_ready ? "Portfolio-ready. Put it on GitHub with a README." : "Not portfolio-ready yet."}</p></div>`;
}
