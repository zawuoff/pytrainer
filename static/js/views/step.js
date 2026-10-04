import { $, $$, S, aiOn, anim, api, busy, cleanup, diffBars, esc, main, md, modColor, motionOK, noAI, refreshState, stepKind, toast } from "../core.js";
import { lessonTracker, lxPop, renderRich } from "../blocks.js";
import { burst, chatHTML, checksHTML, isNarrow, makeDock, makeEditor, paneSwitch, qualityHTML, researchHTML, resultsHTML, reviewHTML, startTimer } from "../workspace.js";
import { mountLibrary, tabIndicator } from "../library.js";
import { createDebugger } from "../debugger.js";

/* ---------------------------------------------------------------- step workspace: lesson left, code right, output below */

export async function viewStep(id, reviewFlag) {
  const review = !!reviewFlag;
  const d = await api("exercise/" + id);
  const ex = d.exercise, path = d.path, exam = d.exam;
  // Reviews come in a changed form when one is ready: same skill, new names and data.
  let variant = null;
  if (review && reviewFlag !== "?review-original" && ["function", "script", undefined].includes(ex.mode)) {
    const v = await api(`exercise/${id}/variant`).catch(() => null);
    if (v?.variant) {
      variant = { original: ex.title };
      Object.assign(ex, v.variant, { lesson: null });
      d.checks = v.checks; d.debug_call = v.debug_call; d.reference = null;
    }
  }
  const noHelp = d.exam_locked_help || !!variant;
  const predict = ex.mode === "predict", testsMode = ex.mode === "tests";
  let lastResult = null, chat = d.chat, reviewData = d.review, hints = d.hints, canReveal = d.can_reveal;
  let revealed = d.revealed, explanation = d.explanation, walkthrough = null, improve = null, answer = "";
  let feedback = d.reference ? { reference: d.reference, quality: null, tips: [], style: [] } : null;
  let dockTab = predict ? "answer" : "results";
  let outputHTML = `<span class="faint">${testsMode ? "Run executes your test file (the code under test is importable as <code>target</code>). Check grades your tests." : "Run executes your file and shows what it prints. Check runs the checks."}</span>`;
  let stdin = "", args = "";
  const initial = predict ? ex.code : review ? ex.starter : (d.draft?.["solution.py"] ?? ex.starter);
  const back = path?.kind === "exam" ? `#/exam/${d.module}` : path?.kind === "chapter" ? `#/chapter/${ex.topic}` : path?.kind === "combo" ? "#/extras" : "#/course";
  const idx = path ? path.index : 0, total = path ? path.total : 1;
  const prevId = path && idx > 0 ? path.steps[idx - 1].id : null;
  const nextId = path && idx + 1 < total ? path.steps[idx + 1].id : null;
  const kindText = exam ? "Module test" : variant ? "Review: same idea, new form" : review ? "Review: rebuild it from memory" : stepKind(ex);

  main.innerHTML = `<div class="page wide"><div class="ws" style="${modColor(d.module)}">
    <div class="ws-top">
      <a class="btn small ghost" href="${back}" title="Back to the chapter">←</a>
      <span class="ttl"><a href="${back}">${esc(path?.title || d.topic_title || "")}</a> · <b>${idx + 1}/${total}</b></span>
      <div class="stepdots">${(path?.steps || []).map((s, i) => `<a href="#/step/${s.id}" class="${s.status} ${i === idx ? "here" : ""}" title="${i + 1}. ${esc(s.title)}"></a>`).join("")}</div>
      ${prevId ? `<a class="btn small ghost hide-m" href="#/step/${prevId}">Back</a>` : ""}
      ${nextId ? `<a class="btn small" href="#/step/${nextId}">Next</a>` : path?.project && !path.project.passed ? `<a class="btn small" href="#/project/${path.project.id}">Chapter project</a>` : `<a class="btn small" href="${back}">Finish</a>`}
    </div>
    <section class="ws-read"><div class="ws-read-in" id="read"></div></section>
    <section class="ws-code">
      <div class="toolbar">
        <button class="btn" id="run-btn" ${predict ? "disabled" : ""} title="Alt+Enter">Run <kbd>Alt+⏎</kbd></button>
        <button class="btn ghost" id="dbg-btn" ${predict && !d.revealed && d.state.status !== "solved" ? "disabled" : ""} title="Step through your code one line at a time (Alt+D)">Debug</button>
        <button class="btn primary" id="check-btn" title="Ctrl+Enter">Check <kbd>Ctrl+⏎</kbd></button>
        ${ex.hint_count && !noHelp ? `<button class="btn ghost" id="hint-btn">Hint <span class="faint" id="hint-count">${hints.length}/${ex.hint_count}</span></button>` : ""}
        <button class="btn ghost" id="lib-btn" title="Look up syntax from the chapters you have finished (Ctrl+K). Your code stays as it is.">Library <kbd>Ctrl+K</kbd></button>
        <span class="grow"></span><span class="timer" id="timer">0:00</span>
        ${predict ? "" : `<button class="btn ghost small" id="reset-btn">Reset</button>`}
      </div>
      <div class="filetabs">${testsMode ? `<button class="on">your tests</button>` : predict ? `<button class="on">the program (read it)</button>` : ""}</div>
      <div class="editor" id="editor"></div>
      <div class="dock" id="dock"><div class="dock-grip"></div><div class="dock-tabs" id="dock-tabs"></div><div class="dock-body" id="dock-body"></div></div>
    </section></div></div>`;

  const timer = startTimer($("#timer"));
  let saveT = null;
  const ed = makeEditor($("#editor"), { "solution.py": initial }, () => {
    if (review || predict) return;
    clearTimeout(saveT);
    saveT = setTimeout(() => api("draft", { item_id: id, files: ed.files() }).catch(() => {}), 700);
  }, { focus: !predict });
  if (predict) {
    // The program is for reading only: no cursor, and any click or typing goes to the answer box.
    ed.cm.setOption("readOnly", "nocursor");
    const toAnswer = () => { if (dockTab !== "answer") { dockTab = "answer"; drawDock(); } $("#predict")?.focus(); };
    $("#editor").addEventListener("mousedown", () => setTimeout(toAnswer, 0));
    const typeToAnswer = (e) => {
      const el = document.activeElement;
      if (e.ctrlKey || e.metaKey || e.altKey || e.key.length !== 1) return;
      if (el && (el.tagName === "TEXTAREA" || el.tagName === "INPUT" || el.isContentEditable || el.closest(".lx, .dg, .ws-lib"))) return;
      toAnswer();
    };
    document.addEventListener("keydown", typeToAnswer);
    cleanup.push(() => document.removeEventListener("keydown", typeToAnswer));
  }
  cleanup.push(() => { clearTimeout(saveT); if (!review && !predict) api("draft", { item_id: id, files: ed.files() }).catch(() => {}); });
  makeDock($("#dock"));
  const dbg = createDebugger({
    cm: ed.cm, exerciseId: id, suggestion: d.debug_call, predict,
    getFiles: () => ed.files(), getStdin: () => stdin.replace(/\\n/g, "\n"),
  });
  const setPane = paneSwitch($(".ws"), ed.cm, ["Lesson", predict ? "Answer" : "Code"]);

  /* left: lesson, then the task. The lesson and the task are drawn once, so the activities in the
     lesson keep their state. drawRead() only redraws the status line and the help under the task. */
  const read = $("#read");
  read.innerHTML = `<div id="read-head"></div>
    ${ex.lesson && !review ? `<div class="lesson-wrap" id="read-lesson">${md(ex.lesson, "lesson")}</div>` : ""}
    <div class="task" id="read-task"><div class="label">${predict ? "Your turn: predict the output" : testsMode ? "Your turn: write the tests" : ex.kind === "bughunt" ? "Your turn: find and fix the bug" : "Your turn"}</div>
      ${researchHTML(ex.research)}${md(ex.prompt)}${checksHTML(d.checks)}
      ${ex.setup_files?.length ? `<p class="faint small" style="margin-top:10px">Files next to your code: ${ex.setup_files.map(esc).join(", ")}</p>` : ""}</div>
    <div id="read-extra"></div>`;
  renderRich(read);
  if ($("#read-lesson")) lessonTracker($(".ws-read"), $("#read-lesson"));
  function drawRead() {
    const status = d.state.status === "solved" ? `<span class="pill pass">solved</span>` : d.state.status === "attempted" ? `<span class="pill warn">attempted</span>` : "";
    $("#read-head").innerHTML = `<div class="kindline"><span>${esc(kindText)}</span>${ex.difficulty ? diffBars(ex.difficulty) : ""}${status}</div><h1>${esc(ex.title)}</h1>
      ${variant ? `<div class="note small">This review tests the same skill as <b>${esc(variant.original)}</b>, with new names and data, so you rebuild the idea rather than remember the text. Passing it counts as reviewing that step. <a href="#/step/${id}?review-original">Review the original instead</a></div>` : ""}`;
    const extra = $("#read-extra");
    let h = "";
    if (explanation) h += `<div class="good" style="margin-top:18px"><b>Why:</b> ${md(explanation)}</div>`;
    if (!noHelp) {
      if (hints.length) h += `<div class="section hints" style="margin-top:26px"><h3>Hints</h3><ol style="padding-left:1.2em">${hints.map((x) => `<li style="margin:6px 0">${md(x)}</li>`).join("")}</ol></div>`;
      if (revealed) {
        h += `<div class="panel" style="margin-top:22px;border-color:var(--amber)"><h3>${predict ? "The actual output" : "A reference solution"}</h3>
          <p class="dim small">${predict ? "Compare it with your prediction, line by line." : "Study it until every line makes sense. Then write it yourself in the editor, without copying, and press Check. It comes back tomorrow for you to rebuild from memory, and only counts once you pass that."}</p>
          ${predict ? `<pre class="outbox">${esc(revealed.output)}</pre>${md(revealed.explanation || "")}` : md("```python\n" + revealed.solution + "\n```")}
          ${!predict && aiOn() ? `<button class="btn small" id="explain-btn">Walk me through it line by line</button>` : ""}
          <div id="walk">${walkthrough ? md(walkthrough) : ""}</div></div>`;
      } else if (d.state.status !== "solved") {
        h += `<div class="section" style="margin-top:28px"><h3>Stuck?</h3>
          <p class="dim small">Take a hint${aiOn() ? ", or ask the Tutor tab below" : ""}. ${canReveal ? "You've given it a real go, so you can view the solution: study it, then write it yourself." : `The solution unlocks after ${predict ? "2" : "3"} checks or 10 minutes of trying.`}</p>
          <div class="row">${ex.hint_count && hints.length < ex.hint_count ? `<button class="btn small" id="hint-inline">Get hint ${hints.length + 1} of ${ex.hint_count}</button>` : ""}
          <button class="btn small ${canReveal ? "" : "ghost"}" id="reveal-btn" ${canReveal ? "" : "disabled"}>Show solution</button></div></div>`;
      }
    } else if (variant) {
      h += `<p class="faint small" style="margin-top:22px">No hints, tutor or solution in a changed-form review: they belong to the original. If you're stuck, <a href="#/step/${id}?review-original">review the original</a> instead.</p>`;
    } else {
      h += `<p class="faint small" style="margin-top:22px">Module test: no hints, tutor or solutions until you pass. Some questions need you to look things up, and that's part of the test.</p>`;
    }
    extra.innerHTML = h;
    renderRich(extra);
    $("#hint-inline", extra)?.addEventListener("click", getHint);
    $("#reveal-btn", extra)?.addEventListener("click", async (e) => {
      busy(e.target, true);
      try { revealed = (await api(`exercise/${id}/reveal`, { duration_s: timer.secs })).revealed; drawRead(); if (predict) { $("#run-btn").disabled = false; $("#dbg-btn").disabled = false; drawDock(); } }
      catch (err) { toast(err.message, true); busy(e.target, false); }
    });
    $("#explain-btn", extra)?.addEventListener("click", async (e) => {
      busy(e.target, true, "Explaining");
      try { walkthrough = (await api("ai/explain", { item_id: id, files: ed.files() })).explanation; drawRead(); }
      catch (err) { toast(err.message, true); busy(e.target, false); }
    });
  }
  async function getHint() {
    try {
      const r = await api(`exercise/${id}/hint`, {});
      hints = r.hints; drawRead();
      if (isNarrow()) setPane("read");
      const hc = $("#hint-count"); if (hc) hc.textContent = `${hints.length}/${r.total}`;
      const fresh = $(".hints li:last-child", read);
      if (fresh) { fresh.scrollIntoView({ behavior: motionOK() ? "smooth" : "auto", block: "center" }); anim(fresh, [{ opacity: 0, transform: "translateY(10px)" }, { opacity: 1, transform: "none" }], { duration: 320 }); }
    } catch (err) { toast(err.message, true); }
  }
  drawRead();
  /* right bottom: results / output / tutor / feedback / library */
  const dockBody = $("#dock-body");
  let shownTab = null;
  const lib = mountLibrary($(".ws"), $("#dock"), {
    topic: path?.kind === "chapter" ? ex.topic : null, editor: ed.cm,
    onPlace: () => { if (shownTab !== null) drawDock(); },
    selectTab: () => { dockTab = "library"; drawDock(); if (isNarrow()) setPane("code"); },
  });
  function tabsList() {
    const t = [];
    if (predict) t.push(["answer", "Your answer"]);
    t.push(["results", "Results"]);
    t.push(["output", "Output"]);
    if (!predict || revealed || d.state.status === "solved") t.push(["debug", "Step through"]);
    if (!noHelp) t.push(["tutor", `Tutor${chat.length ? `<span class="n">${Math.ceil(chat.length / 2)}</span>` : ""}`]);
    if (!predict) t.push(["feedback", "Feedback"]);
    if (lib.pos === "bottom") t.push(["library", "Library"]);
    return t;
  }
  function drawDock() {
    if (dockTab === "library" && lib.pos !== "bottom") dockTab = predict ? "answer" : "results";
    const tabs = $("#dock-tabs");
    tabs.innerHTML = tabsList().map(([k, label]) => `<button data-t="${k}" class="${dockTab === k ? "on" : ""}">${label}</button>`).join("") + `<span class="grow"></span>`;
    $$("button", tabs).forEach((b) => b.onclick = () => { dockTab = b.dataset.t; drawDock(); });
    tabIndicator(tabs);
    lib.tab(dockTab === "library");
    if (shownTab !== dockTab) anim(dockTab === "library" ? lib.panel : dockBody, [{ opacity: 0, transform: "translateY(5px)" }, { opacity: 1, transform: "none" }], { duration: 200 });
    shownTab = dockTab;
    if (dockTab !== "debug") dbg.hide();
    if (dockTab === "library") return;
    if (dockTab === "answer") {
      dockBody.innerHTML = `<p class="dim small" style="margin-top:0">Type exactly what the program prints, one line per line. Then press Check.</p>
        <textarea id="predict" class="predict-box" spellcheck="false" rows="5" placeholder="Type the output here…">${esc(answer)}</textarea>`;
      $("#predict").oninput = (e) => { answer = e.target.value; };
      $("#predict").focus();
    } else if (dockTab === "results") {
      dockBody.innerHTML = resultsHTML(lastResult, lastResult?._extra || "");
      $("#res-hint", dockBody)?.addEventListener("click", (e) => { e.preventDefault(); getHint(); });
      $("#res-feedback", dockBody)?.addEventListener("click", (e) => { e.preventDefault(); dockTab = "feedback"; drawDock(); });
    } else if (dockTab === "output") {
      dockBody.innerHTML = `<pre class="out">${outputHTML}</pre>` + (predict ? "" :
        `<div class="stdin-row"><input type="text" id="stdin" placeholder="input for Run (\\n = new line)" value="${esc(stdin)}"><input type="text" id="args" placeholder="command-line args" style="max-width:200px" value="${esc(args)}"></div>`);
      $("#stdin")?.addEventListener("input", (e) => { stdin = e.target.value; });
      $("#args")?.addEventListener("input", (e) => { args = e.target.value; });
    } else if (dockTab === "tutor") {
      dockBody.innerHTML = aiOn() ? `${chatHTML(chat, "Stuck or confused? Ask about the lesson, an error message, or your approach. The tutor explains and teaches, but won't write the answer for you.")}
        <div class="chat-input"><textarea id="ask" rows="2" placeholder="Enter sends, Shift+Enter for a new line"></textarea><button class="btn primary" id="ask-btn">Ask</button></div>
        ${chat.length ? `<button class="btn ghost small" id="clear-chat" style="margin-top:8px">Clear conversation</button>` : ""}` : noAI("The tutor");
      renderRich(dockBody);
      const ask = $("#ask", dockBody);
      if (ask) {
        const send = async () => {
          const msg = ask.value.trim(); if (!msg) return;
          busy($("#ask-btn"), true); ask.disabled = true;
          try { chat = (await api("ai/tutor", { item_id: id, message: msg, files: ed.files(), result: lastResult })).chat; drawDock(); dockBody.scrollTop = dockBody.scrollHeight; }
          catch (err) { toast(err.message, true); busy($("#ask-btn"), false); ask.disabled = false; }
        };
        $("#ask-btn").onclick = send;
        ask.onkeydown = (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } };
        ask.focus();
        $("#clear-chat", dockBody)?.addEventListener("click", async () => { await api("ai/tutor/clear", { item_id: id }); chat = []; drawDock(); });
      }
    } else if (dockTab === "feedback") {
      drawFeedback();
    } else if (dockTab === "debug") {
      dbg.render(dockBody);
    }
  }
  function drawFeedback() {
    if (!feedback) {
      dockBody.innerHTML = `<p class="dim">Once your code passes, this is where you'll get a code-quality score from Jev, suggestions, a reference solution to compare with, and a senior engineer's take on making it cleaner.</p>`;
      return;
    }
    const f = feedback;
    let h = "";
    if (f.quality) h += qualityHTML(f.quality);
    else if (!S.settings.jev.enabled) h += `<p class="faint small">Add a Jev key in Settings for an instant code-quality score.</p>`;
    if (f.tips?.length) h += `<h3 style="margin-top:16px">Could be even better</h3><ul>${f.tips.map((t) => `<li style="margin:4px 0">${md(t)}</li>`).join("")}</ul>`;
    if (f.style?.length) h += `<h3 style="margin-top:16px">Style notes</h3><ul>${f.style.map((s) => `<li>${s.line ? `<span class="faint">line ${s.line}</span> ` : ""}${esc(s.message)}</li>`).join("")}</ul>`;
    h += `<p class="dim small" style="margin-top:14px">Your answer is correct, so you can move on. These are just ideas for next time.</p>`;
    if (f.reference) h += `<details style="margin-top:10px"><summary>Compare with a reference solution</summary>${md("```python\n" + f.reference + "\n```")}</details>`;
    if (aiOn()) h += `<div class="row" style="margin-top:14px"><button class="btn small" id="improve-btn">Show me a cleaner way</button><button class="btn small ghost" id="review-btn">Full code review</button></div>`;
    if (improve) h += `<div class="panel" style="margin-top:14px">${md(improve)}</div>`;
    if (reviewData) h += `<div class="panel" style="margin-top:14px">${reviewHTML(reviewData)}</div>`;
    dockBody.innerHTML = h;
    renderRich(dockBody);
    $("#improve-btn", dockBody)?.addEventListener("click", async (e) => {
      busy(e.target, true, "Thinking");
      try { improve = (await api("ai/improve", { item_id: id, files: ed.files() })).advice; drawFeedback(); }
      catch (err) { toast(err.message, true); busy(e.target, false); }
    });
    $("#review-btn", dockBody)?.addEventListener("click", async (e) => {
      busy(e.target, true, "Reviewing");
      try { reviewData = (await api("ai/review", { item_id: id, files: ed.files(), result: lastResult })).review; drawFeedback(); }
      catch (err) { toast(err.message, true); busy(e.target, false); }
    });
  }
  drawDock();

  async function run() {
    const btn = $("#run-btn"); busy(btn, true);
    try {
      const r = predict ? await api(`exercise/${id}/run`, {}) :
        await api(`exercise/${id}/run`, { files: ed.files(), stdin: stdin.replace(/\\n/g, "\n"), args: args.trim() ? args.trim().split(/\s+/) : [] });
      outputHTML = (esc(r.stdout) + (r.stderr ? `<span class="err">${esc(r.stderr)}</span>` : "")) || `<span class="faint">(nothing was printed)</span>`;
      outputHTML += r.timed_out ? `<span class="err">\n[stopped: time limit]</span>` : `<span class="faint">\n[finished, exit code ${r.returncode}]</span>`;
      dockTab = "output"; drawDock();
    } catch (err) { toast(err.message, true); }
    busy(btn, false);
  }
  async function check() {
    const btn = $("#check-btn"); busy(btn, true, "Checking");
    try {
      const payload = predict ? { answer } : { files: ed.files(), variant: !!variant };
      const r = await api(`exercise/${id}/check`, { ...payload, kind: review ? "review" : "practice", duration_s: timer.secs });
      lastResult = r.result; lastResult._fresh = true; canReveal = r.can_reveal;
      $$("#read-task .check-list li").forEach((li, i) => {
        const t = r.result.tests.find((x) => x.name === li.lastElementChild.textContent) || (r.result.tests.length === d.checks.length ? r.result.tests[i] : null);
        const mark = li.firstElementChild;
        mark.className = t ? (t.passed ? "ok" : "no") : "pending";
        mark.textContent = t ? (t.passed ? "✓" : "✕") : "○";
        if (t) anim(mark, [{ transform: "scale(.3)", opacity: 0 }, { transform: "scale(1)", opacity: 1 }], { duration: 300, delay: i * 50, fill: "backwards" });
      });
      let extra = "";
      if (r.result.status === "passed") {
        d.state = r.state;
        const q = r.result.quality;
        extra += `<div class="good">${r.state.newly_solved ? burst() : ""}<span class="celebrate">${r.state.newly_solved ? (r.state.first_try ? "Solved on the first try." : "Solved.") : review ? "Review passed. It'll come back later, at a longer gap." : "Still correct."}</span>
          ${q ? ` Code quality ${q.overall}/10.` : ""} ${!predict ? `<a href="#" id="res-feedback">See feedback</a>` : ""}</div>`;
        if (r.exam) extra += `<div class="note">Module test: ${r.exam.solved}/${r.exam.total} solved. ${r.exam.passed ? (r.exam.placed_now ? "<b>Passed. The whole module is marked complete.</b>" : "Passed.") : `You pass at ${Math.ceil(r.exam.total * r.exam.pass_ratio)}.`}</div>`;
        extra += `<div class="row" style="margin-top:12px">${nextId ? `<a class="btn primary" href="#/step/${nextId}">Next step</a>`
          : path?.project && !path.project.passed ? `<a class="btn primary" href="#/project/${path.project.id}">On to the chapter project</a>`
          : `<a class="btn primary" href="${back}">Finish</a>`}</div>`;
        if (predict) { explanation = r.result.explanation; $("#run-btn").disabled = false; $("#dbg-btn").disabled = false; }
        else feedback = { reference: r.reference, quality: q, tips: r.tips, style: r.style };
        const dot = $(`.stepdots a[href="#/step/${id}"]`); if (dot) { if (r.state.newly_solved) lxPop(dot); dot.className = "solved here"; }
        drawRead();
      } else {
        extra += `<div class="note">Not there yet, and that's normal. Read the failing check above.${!noHelp && ex.hint_count && hints.length < ex.hint_count ? ` <a href="#" id="res-hint">Take a hint</a>` : ""}${!noHelp && aiOn() ? ", or ask the Tutor tab" : ""}.${!noHelp && canReveal && !revealed ? " The Show solution option is now open on the left." : ""}</div>`;
        if (!noHelp) drawRead();
      }
      lastResult._extra = extra;
      dockTab = "results"; drawDock();
      if (isNarrow()) setPane("code");
      refreshState().catch(() => {});
    } catch (err) { toast(err.message, true); }
    busy(btn, false);
  }
  function debug() {
    if ($("#dbg-btn").disabled) return;
    dockTab = "debug"; drawDock();
    if (isNarrow()) setPane("code");
    dbg.start();
  }
  $("#dbg-btn").onclick = debug;
  $("#run-btn").onclick = run;
  $("#check-btn").onclick = check;
  $("#hint-btn")?.addEventListener("click", getHint);
  $("#lib-btn").onclick = () => lib.toggle();
  $("#reset-btn")?.addEventListener("click", (e) => {
    const b = e.currentTarget;
    if (b.dataset.armed) { ed.set({ "solution.py": ex.starter }); b.textContent = "Reset"; delete b.dataset.armed; }
    else { b.dataset.armed = 1; b.textContent = "Click again to reset"; setTimeout(() => { if (b.isConnected) { b.textContent = "Reset"; delete b.dataset.armed; } }, 3000); }
  });
  const keys = (e) => {
    if (e.target.closest?.(".lx")) return;              // an activity in the lesson has its own Ctrl+Enter
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) { e.preventDefault(); check(); }
    else if (e.key === "Enter" && e.altKey && !predict) { e.preventDefault(); run(); }
    else if (e.altKey && !e.ctrlKey && (e.key === "d" || e.key === "D" || e.code === "KeyD")) { e.preventDefault(); debug(); }
  };
  document.addEventListener("keydown", keys);
  cleanup.push(() => document.removeEventListener("keydown", keys));
}
