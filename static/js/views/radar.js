import { aiOn, api, busy, esc, main, md, noAI, toast } from "../core.js";
import { startSession } from "../session.js";

/* ---------------------------------------------------------------- weakness radar: patterns in failed checks */

export async function viewRadar() {
  const d = await api("radar");
  const top = d.patterns[0]?.score || 1;
  main.innerHTML = `<div class="page narrow">
    <div class="crumbs"><a href="#/progress">Progress</a></div>
    <h1>Weakness radar</h1>
    <p class="dim" style="max-width:64ch;margin-top:10px">Every failed check says what went wrong. This sorts your recent ones into patterns, so you can see whether it's always the same kind of slip, then practise exactly that. Recent failures count more than old ones.</p>
    ${!d.patterns.length ? `<div class="note">No patterns yet. They show up once you have a few failed checks, which is a normal part of learning here.</div>` : `
    <section class="section"><h2>What keeps going wrong</h2>
      <div class="radar-chart" role="list" aria-label="Patterns in recent failed checks, strongest first">
        ${d.patterns.map((p, i) => `<button type="button" class="radar-row ${i === 0 ? "on" : ""}" role="listitem" data-p="${p.id}" aria-label="${esc(p.label)}: ${p.count} failed checks">
          <span class="radar-label">${esc(p.label)}</span>
          <span class="radar-track"><i style="width:${Math.max(4, Math.round((p.score / top) * 100))}%"></i></span>
          <span class="radar-val">${p.count}</span>
          <span class="radar-tip" role="tooltip"><b>${esc(p.label)}</b><br>${esc(p.description)}<br><span class="faint">${p.count} failed check${p.count === 1 ? "" : "s"}, weighted by recency</span></span>
        </button>`).join("")}
      </div>
      <p class="faint small" style="margin-top:6px">Bar length: recent failed checks in that pattern (older ones count less). Number: all of them, from your last ${d.attempts_considered} failed checks.</p>
      <div class="panel" id="radar-detail" style="margin-top:14px"></div>
    </section>`}
    ${d.chapters.length ? `<section class="section"><h2>Chapters where it shows</h2><table class="ptable">${d.chapters.map((c) => `<tr><td><a href="#/chapter/${c.id}">${esc(c.title)}</a></td>
      <td class="faint small">${c.failed} failed check${c.failed === 1 ? "" : "s"}${c.lapses ? ` · ${c.lapses} failed review${c.lapses === 1 ? "" : "s"}` : ""}</td></tr>`).join("")}</table></section>` : ""}
    <section class="section"><h2>A drill from your mistakes</h2><div class="panel stack" id="md-box"></div></section>
    <section class="section"><h2>Targeted practice</h2>
      ${d.session.length ? `<p class="dim small">${d.session.length} steps picked for your top patterns. The step page walks you through them.</p>
        <ol class="steps">${d.session.map((s) => `<li><a href="${esc(s.href)}"><span>${esc(s.title)}<span class="sub">${esc(s.reason)}</span></span><span class="kind"></span><span class="dot"></span></a></li>`).join("")}</ol>
        <div class="row" style="margin-top:14px"><button class="btn primary" id="radar-go">Start the session</button></div>`
      : `<p class="dim">Nothing to aim at yet.</p>`}
    </section>
  </div>`;
  const detail = (id) => {
    const p = d.patterns.find((x) => x.id === id);
    const box = document.getElementById("radar-detail");
    if (!p || !box) return;
    document.querySelectorAll(".radar-row").forEach((r) => r.classList.toggle("on", r.dataset.p === id));
    box.innerHTML = `<h3>${esc(p.label)}</h3><p class="dim small">${esc(p.description)}</p>
      <ul class="map-list">${p.examples.map((e) => `<li><a href="#/step/${e.id}">${esc(e.title)}</a> <span class="faint small">failed: ${esc(e.check)}</span></li>`).join("")}</ul>`;
  };
  document.querySelectorAll(".radar-row").forEach((r) => r.onclick = () => detail(r.dataset.p));
  if (d.patterns.length) detail(d.patterns[0].id);
  drawMistakes(d.mistake_drill, d.mistakes);
  const go = document.getElementById("radar-go");
  if (go) go.onclick = () => startSession("Targeted practice", d.session);
}

function drawMistakes(drill, count) {
  const box = document.getElementById("md-box");
  if (!aiOn()) { box.innerHTML = noAI("A drill from your mistakes"); return; }
  const done = drill ? drill.steps.filter((s) => s.status === "solved").length : 0;
  box.innerHTML = `<p class="dim small">Your AI reads your last ${Math.min(10, count) || "few"} failed attempts (the task, your code and what failed), says what they have in common, and writes new exercises aimed at exactly that. Each one is checked before you see it.</p>
    ${drill ? `<div><h3>Your latest drill <span class="faint small">${done} of ${drill.steps.length} solved</span></h3>${md(drill.summary)}
      <ol class="steps">${drill.steps.map((s) => `<li><a href="${esc(s.href)}"><span>${esc(s.title)}<span class="sub">${esc(s.reason)}</span></span><span class="kind"></span><span class="dot ${s.status}"></span></a></li>`).join("")}</ol></div>` : ""}
    <div class="row">${drill ? `<button class="btn primary" id="md-start">Start this drill</button>` : ""}
      <button class="btn ${drill ? "ghost" : "primary"}" id="md-make" ${count ? "" : "disabled"}>${drill ? "Make a new one" : "Make my drill"}</button>
      ${count ? "" : `<span class="faint small">Needs at least one failed check first.</span>`}</div>`;
  document.getElementById("md-start")?.addEventListener("click", () => startSession("Drill from your mistakes", drill.steps));
  document.getElementById("md-make")?.addEventListener("click", async (e) => {
    busy(e.target, true, "Reading your mistakes (a minute or two)");
    try { drawMistakes((await api("ai/mistakes", {})), count); toast("Your drill is ready"); }
    catch (err) { toast(err.message, true); busy(e.target, false); }
  });
}
