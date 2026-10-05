import { $, S, aiName, aiOn, api, busy, diffBars, esc, main, md, modColor, moduleOf, refreshState, stepKind, ticks, toast, topicOf } from "../core.js";
import { renderRich } from "../blocks.js";

/* ---------------------------------------------------------------- course */

export async function viewCourse(focus) {
  await refreshState();
  const projects = (await api("projects")).projects;
  main.innerHTML = `<div class="page">
    <div class="row between"><h1>The course</h1><a class="btn small ghost" href="#/map">Concept map</a></div>
    <p class="dim" style="max-width:66ch;margin-top:10px">Eight modules, ordered by what AI-engineering job postings ask for: solid Python first, then APIs and data, then building with LLMs, RAG, evals and agents. Every chapter is a path of short lessons, each followed by an exercise. Each module ends with a test, and passing it lets you skip the module.</p>
    <div class="section" style="margin-top:20px">${S.modules.map((m, i) => `
      <section class="module ${i === 0 ? "first" : ""}" id="mod-${m.id}" style="${modColor(m.id)}">
        <div class="num">${m.number}</div>
        <div>
          <h2>${esc(m.title)}</h2>
          <p class="why">${esc(m.why)}</p>
          <div class="meta"><span>${m.chapters.length} chapters</span><span>${m.steps_done}/${m.steps_total} steps done</span>${m.complete ? `<span style="color:var(--mc)">complete</span>` : ""}</div>
          <div class="chapters">${m.chapters.map((c) => `<a class="chapter-row" href="#/chapter/${c.id}">
              <span><span class="ct">${esc(c.title)}</span><div class="cs">${esc(c.summary)}</div></span>
              ${ticks(c.strip)}
              <span class="state ${c.cleared ? "cleared" : ""}">${c.earned ? "cleared" : c.placed ? "tested out" : c.done ? `${c.done}/${c.steps}` : !c.unlocked ? "later" : ""}</span></a>`).join("")}
            ${m.exam ? `<a class="exam-row" href="#/exam/${m.id}"><span><span class="ct">Module test</span><div class="cs">${m.exam.total} questions · pass ${Math.round(m.exam.pass_ratio * 100)}% to complete the module and skip ahead</div></span>
              <span class="pill ${m.exam.passed ? "pass" : m.exam.attempted ? "warn" : ""}">${m.exam.passed ? "passed" : `${m.exam.solved}/${m.exam.total}`}</span></a>` : ""}
          </div>
          ${m.projects.length ? `<div class="resources"><b style="color:var(--text)">Build it:</b> ${m.projects.map((pid) => { const p = projects.find((x) => x.id === pid); return p ? `<a href="#/project/${pid}">${esc(p.title)}</a>${p.passed ? " ✓" : ""}` : ""; }).join(" · ")}</div>` : ""}
          <div class="resources"><b style="color:var(--text)">Further reading:</b> ${m.resources.map((r) => `<a href="${esc(r.url)}" target="_blank" rel="noopener">${esc(r.title)}</a>`).join(" · ")}</div>
          <div class="resources"><b style="color:var(--text)">Show it:</b> ${esc(m.show_it)}</div>
        </div>
      </section>`).join("")}
    </div>
    <section class="section"><h2>Extra practice</h2><p class="dim">Combination challenges that mix chapters. You can also generate AI exercises from any chapter page.</p><a class="btn" href="#/extras">Open extra practice</a></section>
  </div>`;
  if (focus) setTimeout(() => $("#mod-" + focus)?.scrollIntoView({ behavior: "smooth", block: "start" }), 60);
}

export async function viewExtras() {
  await refreshState();
  main.innerHTML = `<div class="page narrow"><div class="crumbs"><a href="#/course">Course</a></div><h1>Combination challenges</h1>
    <p class="dim" style="margin-top:10px">Mini real-world tasks that mix several chapters. Each unlocks when its chapters are cleared, but you can open any of them.</p>
    <ol class="steps">${S.combos.map((c) => `<li><a href="#/step/${c.id}"><span>${esc(c.title)}<span class="sub">${c.topics.map((t) => esc(topicOf(t)?.title || t)).join(" + ")}</span></span>
      <span class="kind">${c.unlocked ? "" : "later"} ${diffBars(c.difficulty)}</span><span class="dot ${c.status}"></span></a></li>`).join("")}</ol></div>`;
}

export async function viewChapter(id, notesFlag) {
  await refreshState();
  const d = await api("topic/" + id);
  const t = d.topic, p = d.progress, m = moduleOf(t.track);
  const done = d.exercises.filter((e) => e.status === "solved" && !e.revealed).length;
  const proj = p.project;
  const cta = d.next?.type === "step" ? `<a class="btn primary big" href="#/step/${d.next.id}">${done ? "Continue" : "Start the chapter"}</a>`
    : d.next?.type === "project" ? `<a class="btn primary big" href="#/project/${d.next.id}">Start the chapter project</a>`
    : d.next_chapter ? `<a class="btn primary big" href="#/chapter/${d.next_chapter.id}">Next chapter: ${esc(d.next_chapter.title)}</a>`
    : `<a class="btn primary big" href="#/course">Back to the course</a>`;
  main.innerHTML = `<div class="page narrow" style="${modColor(t.track)}">
    <div class="crumbs"><a href="#/course/${m.id}">Module ${m.number} · ${esc(m.title)}</a></div>
    <h1>${esc(t.title)}</h1>
    <p class="dim" style="margin:10px 0 0;max-width:62ch">${esc(t.summary)}</p>
    <div class="row between" style="margin-top:20px">
      <div style="flex:1;max-width:380px">${ticks(topicOf(id).strip)}<div class="faint small" style="margin-top:6px">${done}/${d.exercises.length} steps · ${Math.round(p.mastery * 100)}% mastery${p.earned ? " · cleared" : p.placed ? " · tested out" : ""}</div></div>
      ${cta}
    </div>
    ${d.requires.some((r) => !r.cleared) ? `<div class="note">This chapter builds on ${d.requires.filter((r) => !r.cleared).map((r) => `<a href="#/chapter/${r.id}">${esc(r.title)}</a>`).join(", ")}, which you haven't cleared yet. You can still start it.</div>` : ""}
    <ol class="steps">${d.exercises.map((e, i) => `${e.extra && !d.exercises[i - 1]?.extra ? `<li class="steps-sep">Extra practice: doesn't count toward clearing the chapter</li>` : ""}<li><a href="#/step/${e.id}">
      <span>${esc(e.title)}<span class="sub">${stepKind(e)}${e.research ? " · research" : ""}${e.attempts ? ` · ${e.attempts} attempt${e.attempts > 1 ? "s" : ""}` : ""}</span></span>
      <span class="kind">${e.revealed ? `<span class="pill warn">redo to earn</span>` : e.difficulty ? diffBars(e.difficulty) : ""}</span>
      <span class="dot ${e.revealed ? "revealed" : e.status}"></span></a></li>`).join("")}</ol>
    ${proj ? `<section class="section"><div class="row between"><h2>Chapter project</h2>${proj.passed ? `<span class="pill pass">passed</span>` : ""}</div>
      <a class="list-row" href="#/project/${proj.id}" style="border-top:1px solid var(--rule)">
        <div><h3>${esc(proj.title)}</h3><div class="meta"><span>Build it on your own, with a bit of googling. Hidden checks grade it when you submit.</span></div></div>
        <span class="btn ${proj.passed ? "" : p.steps_done ? "primary" : ""}">${proj.passed ? "Open" : "Start"}</span></a>
      <p class="dim small" style="margin-top:8px">The chapter is complete once you've worked through the steps and this project passes.</p></section>` : ""}
    ${t.lesson ? `<section class="section" id="notes"><div class="row between"><h2>Chapter notes</h2><button class="btn small ghost" id="notes-btn">${notesFlag ? "Hide" : "Show"}</button></div>
      <p class="dim small">The whole chapter on one page, for revision.</p>
      <div id="notes-body" class="${notesFlag ? "" : "hidden"}"><div class="panel" style="background:var(--paper)">${md(t.lesson, "lesson")}</div></div></section>` : ""}
    <section class="section"><h2>More practice</h2>
      <p class="dim" style="max-width:62ch">Have ${aiOn() ? esc(aiName()) : "the AI"} write a fresh exercise for this chapter, aimed at your recent mistakes. It's only added if its reference solution passes its own checks.</p>
      <div class="row"><select id="gen-diff" style="width:auto"><option value="1" selected>Easy</option><option value="2">Medium</option><option value="3">Hard</option></select>
        <button class="btn" id="gen-btn">Generate a challenge</button><span class="faint small" id="gen-msg"></span></div>
      ${d.generated.length ? `<ol class="steps">${d.generated.map((e) => `<li><a href="#/step/${e.id}"><span>${esc(e.title)}<span class="sub">AI-generated</span></span><span class="kind">${diffBars(e.difficulty)}</span><span class="dot ${e.status}"></span></a></li>`).join("")}</ol>` : ""}
    </section></div>`;
  const nb = $("#notes-body");
  if (nb) { renderRich(nb); $("#notes-btn").onclick = (e) => { nb.classList.toggle("hidden"); e.target.textContent = nb.classList.contains("hidden") ? "Show" : "Hide"; }; }
  if (notesFlag) setTimeout(() => $("#notes")?.scrollIntoView({ behavior: "smooth" }), 60);
  $("#gen-btn").onclick = async (e) => {
    if (!aiOn()) { $("#gen-msg").innerHTML = `Connect an AI in <a href="#/settings">Settings</a> first.`; return; }
    busy(e.target, true, "Writing and verifying (up to a minute)");
    try { const r = await api("ai/generate", { topic: id, difficulty: +$("#gen-diff").value }); location.hash = "#/step/" + r.id; }
    catch (err) { toast(err.message, true); busy(e.target, false); }
  };
}

export async function viewExam(moduleId) {
  await refreshState();
  const d = await api("exam/" + moduleId);
  const m = moduleOf(moduleId), st = d.status;
  const next = d.exercises.find((e) => e.status !== "solved") || d.exercises[0];
  main.innerHTML = `<div class="page narrow" style="${modColor(moduleId)}">
    <div class="crumbs"><a href="#/course/${moduleId}">Module ${m.number} · ${esc(m.title)}</a></div>
    <h1>${esc(d.exam.title)}</h1>
    <div style="margin-top:14px">${md(d.exam.intro)}</div>
    <div class="panel row between" style="margin-top:18px">
      <div class="stat"><b>${st.solved}/${st.total}</b><span>solved · ${Math.ceil(st.total * st.pass_ratio)} needed to pass</span></div>
      ${st.passed ? `<span class="pill pass">passed: module complete</span>` : `<a class="btn primary big" href="#/step/${next.id}">${st.attempted ? "Continue the test" : "Start the test"}</a>`}
    </div>
    <p class="dim small" style="margin-top:12px">During the test there are no hints, tutor or solutions, and some questions ask you to look things up, just like at work. Once you pass, all of that unlocks for review.</p>
    <ol class="steps">${d.exercises.map((e) => `<li><a href="#/step/${e.id}"><span>${esc(e.title)}<span class="sub">${e.research ? "research needed" : "&nbsp;"}</span></span><span class="kind">${diffBars(e.difficulty)}</span><span class="dot ${e.status}"></span></a></li>`).join("")}</ol>
  </div>`;
}
