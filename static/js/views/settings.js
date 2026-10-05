import { $, S, aiOn, api, busy, esc, main, refreshState, resetState, toast } from "../core.js";
import { aiPicker } from "./onboarding.js";
import { drawInstall } from "../install.js";

/* ---------------------------------------------------------------- settings */

export function drawJev() {
  const box = $("#jev-box"), j = S.settings.jev;
  box.innerHTML = j.configured
    ? `<div class="row between"><div><b>Connected</b> <span class="faint" style="font-family:var(--mono);font-size:13px">${esc(j.masked)}</span></div>
        <div class="row"><label class="row" style="gap:6px;font-size:14px"><input type="checkbox" id="jev-on" ${j.enabled ? "checked" : ""}> Use Jev</label>
        <button class="btn small ghost" id="jev-remove">Remove key</button></div></div>`
    : `<label class="field"><span>TypeSafe API key</span><input type="password" id="jev-key" autocomplete="off" placeholder="Paste your key"></label>
       <div class="row"><button class="btn primary" id="jev-save">Test & save</button><span id="jev-msg" class="dim small"></span></div>`;
  $("#jev-save")?.addEventListener("click", async (e) => {
    busy(e.target, true, "Testing");
    try { await api("jev/key", { key: $("#jev-key").value }); await refreshState(); drawJev(); toast("Jev connected"); }
    catch (err) { busy(e.target, false); $("#jev-msg").innerHTML = `<span style="color:var(--fail)">${esc(err.message)}</span>`; }
  });
  $("#jev-remove")?.addEventListener("click", async () => { await api("jev/key", { remove: true }); await refreshState(); drawJev(); });
  $("#jev-on")?.addEventListener("change", async (e) => { await api("settings", { jev_enabled: e.target.checked }); await refreshState(); });
}

/* [key, label, preview colours: page, panel, text, dim text, accent] */
const THEMES = [
  ["auto", "Follow system", ["linear-gradient(90deg,#131218 50%,#f7f5f1 50%)", "#1a1920", "#eeebe4", "#a19eaa", "#f5845a"]],
  ["dark", "Dark", ["#131218", "#1a1920", "#eeebe4", "#a19eaa", "#f5845a"]],
  ["light", "Light", ["#f7f5f1", "#ffffff", "#1e1c24", "#5f5b68", "#dd6435"]],
  ["nord", "Nord", ["#2a303c", "#313846", "#eceff4", "#bcc4d3", "#88c0d0"]],
  ["solarized", "Solarized Light", ["#fdf6e3", "#fffbef", "#1f3a40", "#4f646b", "#bd4313"]],
  ["sepia", "Sepia", ["#f4ecd8", "#fbf5e6", "#3b2f22", "#634f37", "#a84c24"]],
  ["contrast", "High contrast", ["#000000", "#0b0b0b", "#ffffff", "#e3e3e3", "#ffb000"]],
];

export async function viewSettings() {
  await refreshState();
  const theme = (() => { try { return localStorage.getItem("pt-theme") || "auto"; } catch { return "auto"; } })();
  const codeSize = (() => { try { return +localStorage.getItem("pt-code-size") || 14; } catch { return 14; } })();
  main.innerHTML = `<div class="page narrow">
    <h1>Settings</h1>
    <section class="section"><h2>AI connection</h2><p class="dim">The tutor, code reviews, the placement report, generated challenges and project reviews all run through this.</p><div id="ai-box"></div></section>
    <section class="section"><h2>Reviews</h2><div class="panel">
      <label class="row" style="gap:8px;font-size:14px"><input type="checkbox" id="variants-on" ${S.settings.review_variants ? "checked" : ""}> Give me reviews in a changed form</label>
      <p class="dim small" style="margin:8px 0 0">Your AI connection rewrites due reviews with new names and data, so you rebuild the idea instead of remembering the text. Each one is checked before you see it. ${aiOn() ? "" : "Needs an AI connection."}</p></div></section>
    <section class="section"><h2>Editor</h2><div class="panel">
      <label class="row" style="gap:8px;font-size:14px"><input type="checkbox" id="assist-on" ${S.settings.editor_assist ? "checked" : ""}> Autocomplete and inline errors</label>
      <p class="dim small" style="margin:8px 0 0">Syntax errors and names that are never defined get underlined as you type; Ctrl+Space (or typing a dot) suggests names, methods and modules. ${S.assist.jedi ? "Jedi is installed, so suggestions understand types." : "For suggestions that understand types, install Jedi into the Python that runs PyTrainer: <code>pip install jedi</code>."}</p></div></section>
    <section class="section"><h2>Help when you're stuck</h2><div class="panel">
      <label class="row" style="gap:8px;font-size:14px"><input type="checkbox" id="nudges-on" ${S.settings.nudges ? "checked" : ""}> Offer help when the same check keeps failing</label>
      <p class="dim small" style="margin:8px 0 0">After a few minutes on the same failing check, a small card in the corner of the editor offers a hint, a pointer from the tutor${aiOn() ? "" : " (with an AI connection)"}, or stepping through your code. It never takes focus, and "Not now" quiets it for a while. Never in module tests.</p></div></section>
    <section class="section"><h2>Streak</h2><div class="panel">
      <label class="row" style="gap:8px;font-size:14px"><input type="checkbox" id="freezes-on" ${S.settings.streak_freezes ? "checked" : ""}> Earn streak freezes</label>
      <p class="dim small" style="margin:8px 0 0">Every 7 days in a row earns a freeze (you can hold 2). If you miss a day while holding one, it's used automatically and your streak carries on. Turn this off for a strict streak.</p></div></section>
    <section class="section"><h2>Jev quality scoring</h2>
      <p class="dim">Jev (TypeSafe) scores your code in about a second on readability, naming, idioms, simplicity and edge cases, and it checks that the tutor never gives answers away. <a href="https://console.typesafe.ai" target="_blank" rel="noopener">Get a key</a></p>
      <div class="panel" id="jev-box"></div></section>
    <section class="section"><h2>Appearance</h2><div class="panel stack">
      <div class="theme-grid" role="radiogroup" aria-label="Theme">${THEMES.map(([key, label, c]) => `<button class="theme-card ${theme === key ? "on" : ""}" role="radio" aria-checked="${theme === key}" data-theme-pick="${key}">
        <span class="theme-prev" style="background:${c[0]}"><i style="background:${c[1]}"><b style="background:${c[2]}"></b><b style="background:${c[3]};width:60%"></b><b style="background:${c[4]};width:34%"></b></i></span><span>${label}</span></button>`).join("")}</div>
      <label class="field"><span>Code size <b id="code-size-val">${codeSize}px</b></span><input type="range" id="code-size" min="12" max="20" step="1" value="${codeSize}"></label>
      <p class="dim small" style="margin:0">Zen mode hides everything but the editor while you work on a step or project: press <kbd>Alt</kbd>+<kbd>Z</kbd> (or the Zen button), and <kbd>Alt</kbd>+<kbd>Z</kbd> or <kbd>Esc</kbd> to come back.</p></div></section>
    <section class="section"><h2>App</h2><div class="panel" id="install-box"></div></section>
    <section class="section"><h2>You</h2><div class="panel">
      <label class="field"><span>Name</span><input type="text" id="name" value="${esc(S.settings.name)}"></label>
      <label class="field"><span>Daily goal (minutes)</span><input type="number" id="goal" min="15" max="480" value="${S.settings.daily_goal}"></label>
      <button class="btn primary" id="save-me">Save</button></div></section>
    <section class="section"><h2>Code sandbox</h2><div class="panel stack">
      <p><span class="pill ${S.sandbox.level === "basic" ? "warn" : "pass"}">${esc(S.sandbox.level)}</span> ${esc(S.sandbox.detail)}</p>
      <p class="dim small">Your code, and the tests that grade it (including AI-written ones), run in this sandbox.</p>
    </div></section>
    <section class="section"><h2>Your data</h2><div class="panel stack">
      <p class="dim">Stored locally in <code>${esc(S.data_dir)}</code> (<code>pytrainer.db</code>), with daily backups in <code>backups/</code> (the last 14 are kept).</p>
      <div class="row"><button class="btn" id="export">Export as JSON</button><button class="btn" id="retake">Retake placement test</button></div>
      <div class="row"><input type="text" id="reset-confirm" placeholder="Type RESET to erase all progress" style="max-width:280px"><button class="btn" id="reset">Erase everything</button></div>
    </div></section></div>`;
  document.querySelectorAll("[data-theme-pick]").forEach((b) => b.onclick = () => {
    const t = b.dataset.themePick;
    try { t === "auto" ? localStorage.removeItem("pt-theme") : localStorage.setItem("pt-theme", t); } catch {}
    if (t === "auto") delete document.documentElement.dataset.theme; else document.documentElement.dataset.theme = t;
    document.querySelectorAll("[data-theme-pick]").forEach((x) => { x.classList.toggle("on", x === b); x.setAttribute("aria-checked", String(x === b)); });
  });
  $("#code-size").oninput = (e) => {
    const v = e.target.value;
    document.documentElement.style.setProperty("--code-size", v + "px");
    $("#code-size-val").textContent = v + "px";
    try { localStorage.setItem("pt-code-size", v); } catch {}
  };
  drawJev();
  drawInstall();
  aiPicker($("#ai-box"));
  $("#nudges-on").onchange = async (e) => { await api("settings", { nudges: e.target.checked }); await refreshState(); toast("Saved."); };
  $("#assist-on").onchange = async (e) => { await api("settings", { editor_assist: e.target.checked }); await refreshState(); toast("Saved. It applies to editors you open from now on."); };
  $("#freezes-on").onchange = async (e) => { await api("settings", { streak_freezes: e.target.checked }); await refreshState(); toast("Saved"); };
  $("#variants-on").onchange = async (e) => { await api("settings", { review_variants: e.target.checked }); await refreshState(); toast("Saved"); };
  $("#save-me").onclick = async () => {
    await api("settings", { name: $("#name").value.trim(), daily_goal: +$("#goal").value || 90 });
    await refreshState(); toast("Saved");
  };
  $("#export").onclick = async () => {
    const data = await api("export");
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([JSON.stringify(data, null, 1)], { type: "application/json" }));
    a.download = `pytrainer-export-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
  };
  $("#retake").onclick = async () => { await api("placement/start", {}); location.hash = "#/placement"; };
  $("#reset").onclick = async () => {
    try { await api("reset", { confirm: $("#reset-confirm").value }); resetState(); location.hash = "#/welcome"; toast("All progress erased (a backup was kept)"); }
    catch (err) { toast(err.message, true); }
  };
}
