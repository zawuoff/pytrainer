import { $, $$, api, busy, cleanup, esc, highlight, main, md, modColor, refreshState, toast } from "../core.js";

/* ---------------------------------------------------------------- on the go: practice for a phone, no code to type

   One item at a time, big tap targets: predict what a program prints, find the line to change from
   a traceback, flip flashcards from your Library. Steps go through the normal check, so they count
   like anywhere else. */

const KINDS = {
  predict: { name: "Predict the output", what: "Read a short program, type what it prints." },
  traceback: { name: "Read the traceback", what: "A program crashed. Tap the line you'd change." },
  cards: { name: "Flashcards", what: "Syntax from your Library. Say what it does, then flip." },
};

/* The step prompts were written for the desktop workspace. */
const phoneText = (s) => s.replace(/ in the editor/g, "").replace(/\bclick the line\b/g, "tap the line");

export async function viewGo() {
  const d = await api("go");
  const n = { predict: d.predict.length, traceback: d.traceback.length, cards: d.cards.length };
  const any = n.predict + n.traceback + n.cards;
  main.innerHTML = `<div class="page narrow go">
    <h1>On the go</h1>
    <p class="dim" style="max-width:60ch;margin-top:8px">Practice that works with a thumb: nothing to type but a short answer. Everything comes from chapters you've reached, and steps count like they do at the desk.</p>
    ${any ? `<button class="btn primary big go-start" id="go-mix">Start a mixed round <span class="faint">${Math.min(12, any)} items</span></button>` : ""}
    <div class="go-tiles">
      ${Object.entries(KINDS).map(([k, v]) => `<button class="go-tile" data-kind="${k}" ${n[k] ? "" : "disabled"}>
        <b>${v.name}</b><span>${v.what}</span><em>${n[k] ? `${n[k]} ready` : k === "cards" ? "Finish a chapter's lessons to unlock its cards" : "None in the chapters you've reached yet"}</em></button>`).join("")}
      ${d.reading ? `<a class="go-tile" href="#/chapter/${esc(d.reading.id)}?notes"><b>Read: ${esc(d.reading.title)}</b>
        <span>The notes of the chapter you're on${d.reading.read ? ", to go over again" : ", before you practise it"}.</span><em>Open the notes</em></a>` : ""}
      ${d.reviews_due ? `<a class="go-tile" href="#/reviews"><b>${d.reviews_due} review${d.reviews_due === 1 ? "" : "s"} due</b>
        <span>Reviews mean rebuilding code, so they're easier with a keyboard.</span><em>See reviews</em></a>` : ""}
    </div>
  </div>`;
  const mix = () => {
    // Interleave the kinds so a round doesn't turn into ten flashcards in a row.
    const out = [], lists = [d.predict.map((x) => ["predict", x]), d.cards.map((x) => ["card", x]), d.traceback.map((x) => ["traceback", x])];
    while (out.length < 12 && lists.some((l) => l.length)) for (const l of lists) if (l.length && out.length < 12) out.push(l.shift());
    return out;
  };
  $("#go-mix")?.addEventListener("click", () => runRound(mix()));
  $$(".go-tile[data-kind]").forEach((b) => b.onclick = () => {
    const k = b.dataset.kind;
    runRound(d[k].map((x) => [k === "cards" ? "card" : k, x]));
  });
}

function runRound(queue) {
  let i = 0, shownAt = Date.now(), over = false;
  const tally = { right: 0, knew: 0, cards: 0, tried: new Set(), retried: new Set() };
  main.innerHTML = `<div class="page narrow go go-run">
    <div class="go-bar"><div class="go-prog" aria-hidden="true"><i id="go-fill"></i></div><span class="small dim" id="go-count"></span>
      <button class="btn small ghost" id="go-end">End</button></div>
    <div id="go-item"></div></div>`;
  $("#go-end").onclick = finish;
  const body = $("#go-item");
  const secs = () => Math.round((Date.now() - shownAt) / 1000);

  function show() {
    if (i >= queue.length) { finish(); return; }
    shownAt = Date.now();
    $("#go-count").textContent = `${i + 1} of ${queue.length}`;
    $("#go-fill").style.width = `${Math.round((i / queue.length) * 100)}%`;
    const [kind, item] = queue[i];
    ({ predict: showPredict, traceback: showTraceback, card: showCard })[kind](item);
    main.scrollTop = 0; window.scrollTo(0, 0);
  }
  const next = () => { i += 1; show(); };
  const head = (item, label) => `<div class="go-kicker" style="${modColor(item.module)}"><span>${label}</span> · ${esc(item.chapter)}</div>`;
  const doneRow = (passed) => `<div class="go-actions">${passed ? "" : `<button class="btn big ghost" id="go-skip">Skip</button>`}
    <button class="btn big ${passed ? "primary" : ""}" id="go-next" ${passed ? "" : "hidden"}>Next</button></div>`;

  async function grade(item, answer, btn) {
    busy(btn, true, "Checking");
    try {
      const r = await api(`exercise/${item.id}/check`, { answer, duration_s: secs() });
      busy(btn, false);
      return r.result;
    } catch (err) { toast(err.message, true); busy(btn, false); return null; }
  }
  function verdict(item, r) {
    const ok = r.status === "passed";
    tally.tried.add(item.id);
    if (ok && !tally.retried.has(item.id)) tally.right += 1;
    if (!ok) tally.retried.add(item.id);
    const bad = r.tests.filter((t) => !t.passed);
    return ok ? `<div class="good"><b>Right.</b>${r.explanation ? md(r.explanation) : ""}</div>`
      : `<div class="note"><b>Not yet.</b> ${bad.length > 1 ? `${r.passed} of ${r.total} lines right.` : ""}
          <ul class="go-bad">${bad.slice(0, 4).map((t) => `<li>${t.name.startsWith("line ") ? `<b>${esc(t.name)}:</b> ` : ""}${esc(t.message)}</li>`).join("")}</ul>
          <span class="small dim">Try again, or skip it. <a href="#/step/${esc(item.id)}">Open the full step</a> for hints.</span></div>`;
  }

  function showPredict(item) {
    body.innerHTML = `${head(item, "Predict the output")}
      <h2 class="go-title">${esc(item.title)}</h2>
      ${md(phoneText(item.prompt), "prose go-prompt")}
      <pre class="go-code"><code class="language-python">${esc(item.code)}</code></pre>
      <label class="small dim" for="go-answer">What it prints</label>
      <textarea id="go-answer" class="predict-box go-answer" rows="4" spellcheck="false" autocapitalize="off" autocomplete="off" autocorrect="off"
        placeholder="One line of output per line"></textarea>
      <div class="go-actions"><button class="btn big primary" id="go-check">Check</button></div>
      <div id="go-res" aria-live="polite"></div>${doneRow(false)}`;
    highlight(body);
    const check = async () => {
      const r = await grade(item, $("#go-answer").value, $("#go-check"));
      if (!r) return;
      $("#go-res").innerHTML = verdict(item, r);
      highlight($("#go-res"));
      if (r.status === "passed") passed();
    };
    $("#go-check").onclick = check;
    $("#go-answer").addEventListener("keydown", (e) => { if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) { e.preventDefault(); check(); } });
    wireNext();
  }

  function showTraceback(item) {
    let picked = null;
    const lines = item.code.replace(/\n+$/, "").split("\n");
    body.innerHTML = `${head(item, "Read the traceback")}
      <h2 class="go-title">${esc(item.title)}</h2>
      ${md(phoneText(item.prompt), "prose go-prompt")}
      <pre class="tb-out go-tb">${esc(item.traceback || "")}</pre>
      <p class="small dim" style="margin:14px 0 6px">Tap the line you'd change:</p>
      <div class="go-lines" role="listbox" aria-label="The program's lines">${lines.map((l, n) => `<button class="go-line" role="option" aria-selected="false" data-n="${n + 1}">
        <span class="go-ln">${n + 1}</span><code class="cm-s-pt" style="--ind:${l.match(/^\s*/)[0].length + 4}ch" data-src="${esc(l)}"></code></button>`).join("")}</div>
      <div class="go-actions"><button class="btn big primary" id="go-check" disabled>Check</button></div>
      <div id="go-res" aria-live="polite"></div>${doneRow(false)}`;
    $$(".go-line code", body).forEach((c) => CodeMirror.runMode(c.dataset.src || " ", "python", c));
    $$(".go-line", body).forEach((b) => b.onclick = () => {
      $$(".go-line", body).forEach((x) => { x.classList.toggle("on", x === b); x.setAttribute("aria-selected", x === b); });
      picked = +b.dataset.n;
      $("#go-check").disabled = false;
      $("#go-check").textContent = `Check line ${picked}`;
    });
    $("#go-check").onclick = async () => {
      if (!picked) return;
      const r = await grade(item, picked, $("#go-check"));
      if (!r) return;
      if (r.status !== "passed") $("#go-check").textContent = `Check line ${picked}`;
      $("#go-res").innerHTML = verdict(item, r);
      highlight($("#go-res"));
      if (r.status === "passed") passed();
    };
    wireNext();
  }

  function showCard(item) {
    body.innerHTML = `${head(item, "Flashcard")}
      <div class="go-flash">
        <p class="small dim">What does this do, and when would you use it?</p>
        <code class="go-syn">${esc(item.syntax)}</code>
        <div id="go-back" hidden><p>${esc(item.explain)}</p><pre class="go-code"><code class="language-python">${esc(item.example)}</code></pre></div>
      </div>
      <div class="go-actions" id="go-flip-row"><button class="btn big primary" id="go-flip">Show the answer</button></div>
      <div class="go-actions" id="go-rate" hidden><button class="btn big" id="go-again">Not yet</button><button class="btn big primary" id="go-knew">I knew it</button></div>`;
    $("#go-flip").onclick = () => {
      $("#go-back").hidden = false; $("#go-flip-row").hidden = true; $("#go-rate").hidden = false;
      highlight(body);
      api(`library/${item.id}/open`, { card: item.card }).catch(() => {});
      $("#go-knew").focus();
    };
    $("#go-knew").onclick = () => { tally.cards += 1; tally.knew += 1; next(); };
    $("#go-again").onclick = () => {
      // Missed cards come back once, at the end of the round.
      tally.cards += 1;
      if (!item._again) queue.push(["card", { ...item, _again: true }]);
      next();
    };
  }

  function passed() {
    $("#go-check").hidden = true;
    $("#go-skip")?.remove();
    $("#go-next").hidden = false;
    $("#go-next").classList.add("primary");
    $("#go-next").focus();
    const a = $("#go-answer"); if (a) a.readOnly = true;
    $$(".go-line", body).forEach((b) => { b.disabled = true; });
  }
  function wireNext() {
    $("#go-next").onclick = next;
    $("#go-skip").onclick = next;
  }

  function finish() {
    if (over) return;
    over = true;
    const steps = tally.tried.size, cards = tally.cards;
    main.innerHTML = `<div class="page narrow go">
      <h1>Round done</h1>
      <table class="ptable" style="margin-top:14px">
        ${steps ? `<tr><td>Steps right on the first try</td><td>${tally.right} of ${steps}</td></tr>` : ""}
        ${cards ? `<tr><td>Cards you knew</td><td>${tally.knew} of ${cards}</td></tr>` : ""}
        ${!steps && !cards ? `<tr><td>Nothing answered this round</td><td></td></tr>` : ""}
      </table>
      <p class="dim small" style="margin-top:10px">Solved steps count toward their chapters and come back as reviews later.</p>
      <div class="go-actions"><a class="btn big ghost" href="#/home">Home</a><button class="btn big primary" id="go-again-round">Another round</button></div></div>`;
    $("#go-again-round").onclick = () => viewGo();
    refreshState().catch(() => {});
  }

  const keys = (e) => {
    if (e.key === "Escape" && !over && e.target.tagName !== "TEXTAREA") { e.preventDefault(); finish(); }
  };
  document.addEventListener("keydown", keys);
  cleanup.push(() => document.removeEventListener("keydown", keys));
  show();
}
