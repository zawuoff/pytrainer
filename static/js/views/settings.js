import { $, S, api, busy, esc, main, refreshState, resetState, toast } from "../core.js";
import { aiPicker } from "./onboarding.js";

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

export async function viewSettings() {
  await refreshState();
  const theme = (() => { try { return localStorage.getItem("pt-theme") || "auto"; } catch { return "auto"; } })();
  main.innerHTML = `<div class="page narrow">
    <h1>Settings</h1>
    <section class="section"><h2>AI connection</h2><p class="dim">The tutor, code reviews, the placement report, generated challenges and project reviews all run through this.</p><div id="ai-box"></div></section>
    <section class="section"><h2>Jev quality scoring</h2>
      <p class="dim">Jev (TypeSafe) scores your code in about a second on readability, naming, idioms, simplicity and edge cases, and it checks that the tutor never gives answers away. <a href="https://console.typesafe.ai" target="_blank" rel="noopener">Get a key</a></p>
      <div class="panel" id="jev-box"></div></section>
    <section class="section"><h2>You</h2><div class="panel">
      <label class="field"><span>Name</span><input type="text" id="name" value="${esc(S.settings.name)}"></label>
      <label class="field"><span>Daily goal (minutes)</span><input type="number" id="goal" min="15" max="480" value="${S.settings.daily_goal}"></label>
      <label class="field"><span>Theme</span><select id="theme"><option value="auto">Follow system</option><option value="dark">Dark</option><option value="light">Light</option></select></label>
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
  $("#theme").value = theme;
  drawJev();
  aiPicker($("#ai-box"));
  $("#save-me").onclick = async () => {
    await api("settings", { name: $("#name").value.trim(), daily_goal: +$("#goal").value || 90 });
    const t = $("#theme").value;
    try { t === "auto" ? localStorage.removeItem("pt-theme") : localStorage.setItem("pt-theme", t); } catch {}
    if (t === "auto") delete document.documentElement.dataset.theme; else document.documentElement.dataset.theme = t;
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
