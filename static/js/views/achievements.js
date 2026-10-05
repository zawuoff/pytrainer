import { api, esc, main } from "../core.js";

/* ---------------------------------------------------------------- achievements: milestones you've earned */

const GLYPHS = { Practice: "✓", Course: "▲", Memory: "↻", Habit: "●", "Extra practice": "◆", Building: "■" };

export async function viewAchievements() {
  const d = await api("achievements");
  main.innerHTML = `<div class="page narrow">
    <div class="crumbs"><a href="#/progress">Progress</a></div>
    <h1>Achievements</h1>
    <p class="dim" style="max-width:64ch;margin-top:10px">Milestones for the things that make you better: solving on your own, coming back to review, finishing chapters and shipping projects. Once earned, they stay.</p>
    <div class="stat-row" style="margin-top:20px">
      <div class="stat"><b>${d.unlocked}<small class="faint"> / ${d.total}</small></b><span>unlocked</span></div>
      ${d.recent.length ? `<div class="stat"><b class="ach-recent">${esc(d.recent[0].title)}</b><span>latest, ${esc(d.recent[0].unlocked_at.slice(0, 10))}</span></div>` : ""}
    </div>
    ${d.groups.map((g) => {
      const items = d.items.filter((i) => i.group === g);
      return `<section class="section"><h2>${esc(g)} <span class="faint small">${items.filter((i) => i.unlocked_at).length} of ${items.length}</span></h2>
        <div class="ach-grid">${items.map((i) => achHTML(i, GLYPHS[g])).join("")}</div></section>`;
    }).join("")}
  </div>`;
}

function achHTML(i, glyph) {
  const done = !!i.unlocked_at;
  const pct = i.value !== undefined ? Math.round((i.value / i.target) * 100) : 0;
  return `<div class="ach ${done ? "done" : ""}">
    <span class="ach-badge" aria-hidden="true">${done ? glyph : i.secret ? "?" : glyph}</span>
    <div><b>${esc(i.title)}</b><p>${esc(i.text)}</p>
      ${done ? `<span class="faint small">Unlocked ${esc(i.unlocked_at.slice(0, 10))}</span>`
        : i.value !== undefined && i.target > 1 ? `<span class="ach-bar" role="progressbar" aria-valuenow="${i.value}" aria-valuemax="${i.target}" aria-label="${esc(i.title)} progress"><i style="width:${pct}%"></i></span><span class="faint small">${i.value} of ${i.target}</span>` : ""}</div></div>`;
}
