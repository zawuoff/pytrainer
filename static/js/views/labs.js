import { $$, api, busy, esc, highlight, main, md, toast } from "../core.js";

/* ---------------------------------------------------------------- labs */

export async function viewLabs() {
  const d = await api("labs");
  main.innerHTML = `<div class="page narrow">
    <h1>Ship it labs</h1>
    <p class="dim" style="margin-top:10px">Things you can only learn in a real terminal: running scripts, virtual environments, uv, secrets and your first real LLM call. Then shipping: an API, a container and CI. Do each mission in your own shell under <code>${esc(d.root)}</code>, then press Check. PyTrainer inspects the result and runs your commands.</p>
    <div class="section">${d.labs.map((lab, i) => `<div class="panel" style="margin-bottom:14px">
      <div class="row between"><h2 style="font-size:21px">${i + 1}. ${esc(lab.title)}</h2>${lab.done ? `<span class="pill pass">done</span>` : ""}</div>
      <div style="margin-top:10px">${md(lab.brief)}</div>
      <ul class="check-list">${lab.checks.map((c, j) => {
        const r = lab.last_result?.checks?.[j];
        return `<li><span class="${r ? (r.passed ? "ok" : "no") : "pending"}">${r ? (r.passed ? "✓" : "✕") : "○"}</span><div>${esc(c)}${r && !r.passed ? `<small>${esc(r.detail)}</small>` : ""}</div></li>`;
      }).join("")}</ul>
      <button class="btn primary" data-lab="${lab.id}" style="margin-top:12px">Check</button></div>`).join("")}</div></div>`;
  $$("[data-lab]").forEach((b) => b.onclick = async () => {
    busy(b, true, "Checking");
    try { await api(`lab/${b.dataset.lab}/check`, {}); const y = main.scrollTop; await viewLabs(); main.scrollTop = y; }
    catch (err) { toast(err.message, true); busy(b, false); }
  });
  highlight(main);
}
