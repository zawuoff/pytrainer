import { $, $$, anim, api, busy, esc, toast } from "./core.js";

/* ---------------------------------------------------------------- shared pieces */

/* The streak number with its freezes: "12" plus a snowflake chip per freeze held. */
export function streakHTML(st) {
  const chips = st.freezes_on && st.freezes ? `<span class="freeze" title="${st.freezes} streak freeze${st.freezes === 1 ? "" : "s"} held: a missed day uses one and keeps your streak">❄ ${st.freezes}</span>` : "";
  return `${st.current}${chips}`;
}

export function streakNote(st) {
  if (st.saved_yesterday) return `<p class="freeze-note">❄ A streak freeze covered yesterday, so your ${st.current}-day streak is safe.${st.today_active ? " You've practised today too." : " Practise today to keep it going."}</p>`;
  if (!st.freezes_on) return "";
  return st.freezes >= st.max_freezes ? `<span class="faint small">Holding the most freezes (${st.max_freezes}).</span>`
    : `<span class="faint small">${st.next_freeze_in} more day${st.next_freeze_in === 1 ? "" : "s"} in a row earns a streak freeze.</span>`;
}

export function heatmap(days) {
  const pad = new Date(days[0].day).getDay();
  const cells = Array(pad).fill(`<i style="visibility:hidden"></i>`);
  days.forEach((d) => {
    const m = d.minutes, lvl = m === 0 && !d.solved ? 0 : m < 20 ? 1 : m < 45 ? 2 : m < 90 ? 3 : 4;
    cells.push(d.frozen ? `<i class="frozen" title="${d.day}: streak freeze used"></i>`
      : `<i class="l${lvl}" title="${d.day}: ${m} min, ${d.solved} solved"></i>`);
  });
  return `<div class="heat">${cells.join("")}</div>`;
}

export const EDITOR_OPTS = {
  mode: "python", theme: "pt", lineNumbers: true, indentUnit: 4, tabSize: 4, indentWithTabs: false,
  matchBrackets: true, autoCloseBrackets: true, styleActiveLine: true, lineWrapping: false,
  inputStyle: matchMedia("(pointer: coarse)").matches ? "contenteditable" : "textarea",
  extraKeys: {
    Tab: (cm) => cm.somethingSelected() ? cm.indentSelection("add") : cm.replaceSelection("    ", "end"),
    "Shift-Tab": (cm) => cm.indentSelection("subtract"),
    "Ctrl-/": "toggleComment",
    Backspace: (cm) => {
      const c = cm.getCursor(), before = cm.getLine(c.line).slice(0, c.ch);
      if (!cm.somethingSelected() && before.length && /^ +$/.test(before)) {
        cm.replaceRange("", { line: c.line, ch: c.ch - (before.length % 4 || 4) }, c);
      } else return CodeMirror.Pass;
    },
  },
};

/* Every python example in a lesson gets Run / Edit & run. */
export function enhanceCode(root) {
  $$("pre", root).forEach((pre) => {
    const codeEl = $("code", pre);
    if (!codeEl || pre.dataset.run || pre.closest(".lx, .task")) return;
    const lang = (codeEl.className.match(/language-(\w+)/) || [])[1] || "";
    if (!["python", "py"].includes(lang)) return;
    pre.dataset.run = "1";
    const code = codeEl.textContent;
    const bar = document.createElement("div");
    bar.className = "runbar";
    bar.innerHTML = `<button class="btn small">Run</button><button class="btn small ghost">Edit & run</button>`;
    const out = document.createElement("pre");
    out.className = "outbox hidden";
    out.style.marginTop = "-6px";
    pre.after(bar, out);
    const [runBtn, editBtn] = bar.querySelectorAll("button");
    let cm = null;
    runBtn.onclick = async () => {
      busy(runBtn, true);
      try {
        const r = await api("run", { code: cm ? cm.getValue() : code });
        out.classList.remove("hidden");
        anim(out, [{ opacity: 0, transform: "translateY(-4px)" }, { opacity: 1, transform: "none" }], { duration: 200 });
        out.innerHTML = esc(r.stdout || "") + (r.stderr ? `<span style="color:var(--fail)">${esc(r.stderr)}</span>` : "") + (!r.stdout && !r.stderr ? `<span class="faint">(no output)</span>` : "");
      } catch (err) { toast(err.message, true); }
      busy(runBtn, false);
    };
    editBtn.onclick = () => {
      pre.classList.add("hidden");
      const host = document.createElement("div");
      host.style.cssText = "border:1px solid var(--rule);border-radius:8px;overflow:hidden;margin:0 0 14px";
      bar.before(host);
      cm = CodeMirror(host, { ...EDITOR_OPTS, value: code, viewportMargin: Infinity });
      cm.setSize(null, "auto");
      editBtn.classList.add("hidden");
      setTimeout(() => cm.refresh(), 10);
    };
  });
}
