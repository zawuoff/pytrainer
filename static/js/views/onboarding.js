import { $, $$, S, api, busy, esc, main, refreshState } from "../core.js";

/* ---------------------------------------------------------------- onboarding */

export async function viewWelcome(placeFlag) {
  let step = placeFlag ? 3 : S.settings.name ? 2 : 1;
  const render = async () => {
    if (step === 1) {
      main.innerHTML = `<div class="center">
        <h1>Learn Python the way AI engineers use it.</h1>
        <p class="dim">A course in small steps: read a short lesson, write a bit of code, and get it checked straight away. It starts from your very first line of Python and builds up to LLM apps, RAG, evals and agents, in the order job postings ask for them.</p>
        <div class="panel" style="margin-top:26px">
          <label class="field"><span>What should I call you?</span><input type="text" id="name" value="${esc(S.settings.name)}" placeholder="Your first name"></label>
          <label class="field"><span>Daily practice goal (minutes)</span><input type="number" id="goal" min="15" max="480" value="${S.settings.daily_goal}"></label>
          <button class="btn primary" id="next1">Continue</button>
        </div></div>`;
      $("#next1").onclick = async () => { await api("settings", { name: $("#name").value.trim(), daily_goal: +$("#goal").value || 90 }); await refreshState(); step = 2; render(); };
    } else if (step === 2) {
      main.innerHTML = `<div class="center"><h1>Connect an AI</h1>
        <p class="dim">Optional. It powers the tutor, code reviews, the placement report, fresh challenges and project grading. It uses a CLI you're already logged into, so it runs on your existing subscription with no API keys.</p>
        <div id="ai-box" style="margin-top:22px"></div>
        <div class="row" style="margin-top:18px"><button class="btn primary" id="next2">Continue</button><button class="btn ghost" id="back2">Back</button></div></div>`;
      aiPicker($("#ai-box"));
      $("#next2").onclick = () => { step = 3; render(); };
      $("#back2").onclick = () => { step = 1; render(); };
    } else {
      main.innerHTML = `<div class="center"><h1>Where should you start?</h1>
        <p class="dim">If you already know some Python, the placement test finds out what, one topic at a time, starting with variables. Each topic climbs from a warm-up to an easy exercise to a core question, and every chapter you pass can be skipped.</p>
        <p class="dim">New to all this? Start from the first lesson. Nothing is assumed.</p>
        <div class="row" style="margin-top:22px"><a class="btn primary" href="#/placement">Take the placement test</a>
          <button class="btn" id="start-zero">Start from lesson one</button></div></div>`;
      $("#start-zero").onclick = async () => { await api("settings", { onboarded: true }); await refreshState(); location.hash = "#/home"; };
    }
  };
  render();
}

export async function aiPicker(box) {
  box.innerHTML = `<p class="dim"><span class="spin"></span> Looking for installed AI CLIs…</p>`;
  let d;
  try { d = await api("ai/providers"); }
  catch (err) { if (box.isConnected) box.innerHTML = `<div class="errbox">${esc(err.message)}</div>`; return; }
  if (!box.isConnected) return;
  let sel = d.current.provider || "none", model = d.current.model || "";
  const draw = () => {
    const p = d.providers.find((x) => x.id === sel);
    box.innerHTML = d.providers.map((pr) => `<div class="provider ${sel === pr.id ? "sel" : ""} ${pr.installed ? "" : "off"}" data-id="${pr.id}">
        <input type="radio" name="prov" ${sel === pr.id ? "checked" : ""} ${pr.installed ? "" : "disabled"}>
        <div><b>${esc(pr.label)}</b><div class="dim small">${esc(pr.detail)}</div></div>
        <span class="pill ${pr.installed ? "pass" : ""}">${pr.installed ? "installed" : "not found"}</span></div>`).join("") +
      `<div class="provider ${sel === "none" ? "sel" : ""}" data-id="none"><input type="radio" name="prov" ${sel === "none" ? "checked" : ""}>
        <div><b>No AI</b><div class="dim small">All the lessons, exercises and checks still work offline.</div></div><span></span></div>` +
      (p ? `<label class="field" style="margin-top:14px"><span>Model (optional)</span>
        ${p.models.length ? `<select id="model"><option value="">Default</option>${p.models.map((m) => `<option ${m === model ? "selected" : ""}>${esc(m)}</option>`).join("")}</select>`
          : `<input type="text" id="model" value="${esc(model)}" placeholder="Leave empty for the CLI's default">`}</label>` : "") +
      `<div class="row"><button class="btn" id="ai-save">${sel === "none" ? "Save" : "Test & save"}</button><span id="ai-msg" class="dim small"></span></div>`;
    $$(".provider", box).forEach((el) => el.onclick = () => {
      if (el.classList.contains("off")) return;
      sel = el.dataset.id; model = sel === d.current.provider ? d.current.model : (d.providers.find((x) => x.id === sel)?.default_model || ""); draw();
    });
    $("#model", box)?.addEventListener("change", (e) => { model = e.target.value; });
    $("#ai-save", box).onclick = async (e) => {
      model = $("#model", box)?.value ?? "";
      const msg = $("#ai-msg", box);
      if (sel !== "none") {
        busy(e.target, true, "Testing");
        msg.textContent = "Sending a test message. The first one can take 10–30 seconds.";
        try { const t = await api("ai/test", { provider: sel, model }); if (!t.ok) throw new Error("Unexpected reply: " + t.reply); }
        catch (err) { busy(e.target, false); msg.innerHTML = `<span style="color:var(--fail)">${esc(err.message)}</span>`; return; }
        busy(e.target, false);
      }
      await api("settings", { ai: { provider: sel, model } });
      d.current = { provider: sel, model };
      await refreshState();
      msg.innerHTML = `<span style="color:var(--pass)">${sel === "none" ? "Saved. AI features are off." : "Connected and saved."}</span>`;
    };
  };
  draw();
}
