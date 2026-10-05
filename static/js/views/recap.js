import { $, api, esc, main, toast } from "../core.js";

/* ---------------------------------------------------------------- weekly recap: your week as a card */

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const nice = (iso) => { const [, m, d] = iso.split("-").map(Number); return `${MONTHS[m - 1]} ${d}`; };
const shift = (iso, days) => { const d = new Date(iso + "T12:00:00"); d.setDate(d.getDate() + days); return d.toISOString().slice(0, 10); };
const plural = (n, w) => `${n} ${w}${n === 1 ? "" : "s"}`;
const range = (r) => `${nice(r.start)} – ${nice(r.end)}`;

function delta(now, before) {
  const d = now - before;
  if (!before && !now) return "";
  if (d === 0) return `<small class="rc-delta">same as last week</small>`;
  return `<small class="rc-delta ${d > 0 ? "up" : "down"}">${d > 0 ? "▲" : "▼"} ${Math.abs(d)} vs last week</small>`;
}

export async function viewRecap(day) {
  let r;
  try { r = await api(day ? `recap/${day}` : "recap"); }
  catch (err) { main.innerHTML = `<div class="page narrow"><h1>Weekly recap</h1><div class="errbox">${esc(err.message)}</div><a class="btn" href="#/recap">Last week</a></div>`; return; }
  try { localStorage.setItem("pt-recap-seen", r.start); } catch {}
  const maxMin = Math.max(30, ...r.days.map((d) => d.minutes));
  const highlights = [
    r.top_chapter && `<li><span class="faint">Most practised</span> <a href="#/chapter/${r.top_chapter.id}">${esc(r.top_chapter.title)}</a> · ${plural(r.top_chapter.solved, "step")}</li>`,
    r.toughest && `<li><span class="faint">Toughest win</span> <a href="#/step/${r.toughest.id}">${esc(r.toughest.title)}</a> · solved after ${plural(r.toughest.fails, "failed check")}</li>`,
    r.best_day && `<li><span class="faint">Best day</span> ${r.best_day.name}: ${r.best_day.minutes} min, ${plural(r.best_day.solved, "step")}</li>`,
    ...r.projects.map((p) => `<li><span class="faint">Shipped</span> <a href="#/project/${p.id}">${esc(p.title)}</a></li>`),
    ...r.labs.map((l) => `<li><span class="faint">Lab done</span> ${esc(l.title)}</li>`),
    r.clean && `<li><span class="faint">Clean first tries</span> ${r.clean} of ${r.solved}</li>`,
  ].filter(Boolean);
  main.innerHTML = `<div class="page narrow">
    <div class="crumbs"><a href="#/progress">Progress</a></div>
    <div class="row between" style="align-items:baseline;flex-wrap:wrap;gap:8px"><h1>${r.is_current ? "This week so far" : "Your week"}</h1>
      <div class="row" style="gap:6px">${r.has_previous || !r.empty ? `<a class="btn small" href="#/recap/${shift(r.start, -7)}" aria-label="Previous week">← Earlier</a>` : ""}
        ${r.is_current ? "" : `<a class="btn small" href="#/recap/${shift(r.start, 7)}" aria-label="Next week">Later →</a>`}</div></div>
    <div class="recap-card" id="recap-card">
      <div class="rc-head"><b>PyTrainer</b><span>${range(r)}</span></div>
      ${r.empty ? `<p class="rc-empty">Nothing recorded this week. ${r.is_current ? "There's still time." : "Every streak starts with one day."}</p>` : `
      <div class="rc-big">
        <div><b>${r.minutes}</b><span>minutes</span>${delta(r.minutes, r.previous.minutes)}</div>
        <div><b>${r.solved}</b><span>steps solved</span>${delta(r.solved, r.previous.solved)}</div>
        <div><b>${r.reviews}</b><span>reviews passed</span>${delta(r.reviews, r.previous.reviews)}</div>
        <div><b>+${r.xp}</b><span>XP</span>${delta(r.xp, r.previous.xp)}</div>
      </div>
      <div class="rc-days" role="img" aria-label="Minutes per day: ${r.days.map((d) => `${d.name} ${d.minutes}`).join(", ")}">${r.days.map((d) => `<div class="rc-day ${d.active ? "on" : ""}">
        <span class="rc-bar"><i style="height:${Math.max(d.minutes ? 6 : 0, (d.minutes / maxMin) * 100)}%"></i></span><span>${d.name}</span></div>`).join("")}</div>
      <p class="faint small rc-active">${plural(r.active_days, "day")} counted toward your streak</p>
      ${highlights.length ? `<ul class="rc-high">${highlights.join("")}</ul>` : ""}
      ${r.achievements.length ? `<div class="rc-ach">${r.achievements.map((a) => `<span class="pill">★ ${esc(a.title)}</span>`).join("")}</div>` : ""}`}
      <div class="rc-foot"><span>Level ${r.level.level} · ${esc(r.level.title)}</span><span>${r.streak.current}-day streak</span></div>
    </div>
    ${r.empty ? "" : `<div class="row" style="margin-top:14px;gap:8px"><button class="btn" id="rc-png">Save as image</button><button class="btn" id="rc-copy">Copy as text</button></div>`}
    ${r.next ? `<section class="section"><h2>${r.is_current ? "For the rest of the week" : "This week"}</h2><ul>
      ${r.next.reviews_due ? `<li><a href="#/reviews">${plural(r.next.reviews_due, "review")} due</a>: reviews keep what you learned last week.</li>` : ""}
      ${r.next.continue ? `<li>Next in the course: <a href="${r.next.continue.type === "project" ? `#/project/${r.next.continue.id}` : `#/step/${r.next.continue.id}`}">${esc(r.next.continue.title)}</a> (${esc(r.next.continue.topic_title)})</li>` : ""}
      ${r.active_days < 4 ? `<li>Aim for four active days: a short session most days beats one long one.</li>` : `<li>${r.active_days} active days: keep that rhythm.</li>`}</ul></section>` : ""}
  </div>`;
  $("#rc-copy")?.addEventListener("click", async () => {
    try { await navigator.clipboard.writeText(r.text); toast("Recap copied."); } catch { toast("Couldn't reach the clipboard.", true); }
  });
  $("#rc-png")?.addEventListener("click", () => saveImage(r));
}

/* The card drawn on a canvas (1080×1350, the size social apps expect), in the current theme. */
function saveImage(r) {
  const css = getComputedStyle(document.documentElement);
  const v = (name) => css.getPropertyValue(name).trim();
  const W = 1080, H = 1350, P = 80;
  const c = document.createElement("canvas");
  c.width = W; c.height = H;
  const g = c.getContext("2d");
  const font = (size, weight = 500, fam = "--ui") => `${weight} ${size}px ${v(fam)}`;
  g.fillStyle = v("--panel"); g.fillRect(0, 0, W, H);
  const grad = g.createLinearGradient(0, 0, W, 0);
  grad.addColorStop(0, "#f5845a"); grad.addColorStop(0.5, "#e97aa6"); grad.addColorStop(1, "#a996ff");
  g.fillStyle = grad; g.fillRect(0, 0, W, 14);
  g.fillStyle = v("--text"); g.font = font(44, 700, "--display"); g.fillText("PyTrainer", P, 120);
  g.fillStyle = v("--dim"); g.font = font(34); g.textAlign = "right"; g.fillText(range(r), W - P, 120); g.textAlign = "left";
  g.fillStyle = v("--text"); g.font = font(64, 700, "--display"); g.fillText(r.is_current ? "This week so far" : "My week in Python", P, 230);
  const big = [[r.minutes, "minutes"], [r.solved, "steps solved"], [r.reviews, "reviews passed"], [`+${r.xp}`, "XP"]];
  big.forEach(([n, label], i) => {
    const x = P + (i % 2) * 460, y = 360 + Math.floor(i / 2) * 170;
    g.fillStyle = v("--text"); g.font = font(96, 700, "--display"); g.fillText(String(n), x, y);
    g.fillStyle = v("--dim"); g.font = font(32); g.fillText(label, x, y + 48);
  });
  const maxMin = Math.max(30, ...r.days.map((d) => d.minutes));
  const top = 760, h = 220, bw = 92, gap = (W - 2 * P - 7 * bw) / 6;
  r.days.forEach((d, i) => {
    const x = P + i * (bw + gap), bh = d.minutes ? Math.max(10, (d.minutes / maxMin) * h) : 0;
    g.fillStyle = v("--rule"); g.fillRect(x, top, bw, h);
    g.fillStyle = d.active ? v("--amber") : v("--faint");
    if (bh) { g.beginPath(); g.roundRect(x, top + h - bh, bw, bh, [10, 10, 0, 0]); g.fill(); }
    g.fillStyle = v("--dim"); g.font = font(28); g.textAlign = "center"; g.fillText(d.name, x + bw / 2, top + h + 44); g.textAlign = "left";
  });
  const lines = [`${plural(r.active_days, "active day")}${r.best_day ? ` · best day ${r.best_day.name}, ${r.best_day.minutes} min` : ""}`,
    r.top_chapter && `Most practised: ${r.top_chapter.title}`, r.toughest && `Toughest win: ${r.toughest.title}`,
    ...r.projects.map((p) => `Shipped: ${p.title}`), r.achievements.length && `Achievements: ${r.achievements.map((a) => a.title).join(", ")}`].filter(Boolean).slice(0, 4);
  g.font = font(32);
  lines.forEach((t, i) => { g.fillStyle = i ? v("--text") : v("--dim"); g.fillText(clip(g, t, W - 2 * P), P, 1090 + i * 50); });
  g.fillStyle = v("--dim"); g.font = font(30);
  g.fillText(`Level ${r.level.level} · ${r.level.title}`, P, H - 70);
  g.textAlign = "right"; g.fillText(`${r.streak.current}-day streak`, W - P, H - 70);
  c.toBlob((blob) => {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `pytrainer-week-${r.start}.png`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 5000);
  }, "image/png");
}

function clip(g, text, width) {
  if (g.measureText(text).width <= width) return text;
  while (text.length > 1 && g.measureText(text + "…").width > width) text = text.slice(0, -1);
  return text + "…";
}
