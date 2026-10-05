/* The REPL panel: a live Python session (pytrainer/repl.py) in a dock tab. Variables persist between
   commands; "Load my code" starts a fresh session with your file run first, like `python -i`. */
import { api, cleanup, esc } from "./core.js";

export function createRepl({ files, main }) {
  let sid = null, starting = null, buffer = "", log = [], history = [], hpos = 0, host = null, busy = false;

  const push = (cls, text) => { if (text) log.push(`<span class="${cls}">${esc(text)}</span>`); if (log.length > 400) log = log.slice(-400); };
  async function ensure(run) {
    if (sid && !run) return sid;
    if (starting && !run) return starting;
    if (sid) api(`repl/${sid}/stop`, {}).catch(() => {});
    sid = null;
    // Your files are always in the session's folder (so `import` works); "Load my code" also runs one.
    starting = api("repl/start", run ? { files: files(), run: main() } : { files: files() }).then((r) => {
      sid = r.id; starting = null;
      if (run) { push("rp-info", `# ran ${main()}\n`); push("rp-out", r.out); push("rp-err", r.err); }
      return sid;
    }).catch((err) => { starting = null; push("rp-err", err.message + "\n"); draw(); throw err; });
    return starting;
  }

  async function submit(line) {
    if (busy) return;
    const code = buffer ? `${buffer}\n${line}` : line;
    push("rp-in", `${buffer ? "... " : ">>> "}${line}\n`);
    if (line.trim()) { history.push(line); if (history.length > 200) history.shift(); }
    hpos = history.length;
    busy = true; draw();
    try {
      await ensure();
      let r;
      try { r = await api(`repl/${sid}/run`, { code }); }
      catch (err) {
        if (!/ended/.test(err.message)) throw err;
        sid = null; await ensure(); r = await api(`repl/${sid}/run`, { code });  // the server forgot it: start over
      }
      buffer = r.more ? code : "";
      push("rp-out", r.out); push("rp-err", r.err);
    } catch (err) { push("rp-err", err.message + "\n"); buffer = ""; }
    busy = false; draw();
  }

  function draw() {
    if (!host || !host.isConnected) return;
    const out = host.querySelector(".rp-log");
    out.innerHTML = log.join("") || `<span class="rp-info"># Python REPL in the sandbox, next to a copy of your files (import them by name). Try 2 ** 10, or "Load my code" to run the file you're viewing first.\n</span>`;
    out.scrollTop = out.scrollHeight;
    host.querySelector(".rp-prompt").textContent = buffer ? "..." : ">>>";
    const input = host.querySelector(".rp-input");
    input.disabled = busy;
    if (!busy) input.focus({ preventScroll: true });
  }

  function render(el) {
    host = el;
    el.innerHTML = `<div class="repl">
      <div class="rp-bar"><button class="btn small" data-rp="load" title="Start fresh with your file run first, like python -i">Load my code</button>
        <button class="btn small ghost" data-rp="restart">Restart</button><button class="btn small ghost" data-rp="clear" title="Ctrl+L">Clear</button>
        <span class="grow"></span><span class="faint small">Enter runs · Shift+Enter new line · ↑↓ history</span></div>
      <pre class="rp-log" aria-live="polite"></pre>
      <div class="rp-line"><span class="rp-prompt">&gt;&gt;&gt;</span><textarea class="rp-input" rows="1" spellcheck="false" aria-label="Python command"></textarea></div></div>`;
    const input = el.querySelector(".rp-input");
    const grow = () => { input.style.height = "auto"; input.style.height = `${Math.min(160, input.scrollHeight)}px`; };
    input.addEventListener("input", grow);
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        const v = input.value;
        input.value = ""; grow();
        // A pasted multi-line block runs as one command.
        submit(v);
      } else if (e.key === "ArrowUp" && !input.value.includes("\n") && history.length) {
        e.preventDefault(); hpos = Math.max(0, hpos - 1); input.value = history[hpos] || ""; grow();
      } else if (e.key === "ArrowDown" && !input.value.includes("\n") && history.length) {
        e.preventDefault(); hpos = Math.min(history.length, hpos + 1); input.value = history[hpos] || ""; grow();
      } else if (e.key === "l" && e.ctrlKey) {
        e.preventDefault(); log = []; draw();
      } else if (e.key === "c" && e.ctrlKey && !input.selectionEnd && buffer) {
        e.preventDefault(); buffer = ""; push("rp-info", "KeyboardInterrupt\n"); draw();
      }
    });
    el.querySelector("[data-rp=load]").onclick = async () => { busy = true; draw(); buffer = ""; try { await ensure(true); } catch {} busy = false; draw(); };
    el.querySelector("[data-rp=restart]").onclick = async () => {
      if (sid) api(`repl/${sid}/stop`, {}).catch(() => {});
      sid = null; buffer = ""; push("rp-info", "# restarted: a fresh session\n"); draw();
    };
    el.querySelector("[data-rp=clear]").onclick = () => { log = []; draw(); };
    el.querySelector(".rp-log").addEventListener("mouseup", () => { if (!getSelection().toString()) input.focus(); });
    draw();
  }

  cleanup.push(() => { if (sid) api(`repl/${sid}/stop`, {}).catch(() => {}); sid = null; });
  return { render };
}
