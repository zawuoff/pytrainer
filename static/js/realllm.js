/* "Real model calls" for Run: when ticked, code can `from pytrainer_llm import llm` and reach the
   connected AI (at most 6 calls per run). The choice is remembered in this browser. */
import { aiName, aiOn, esc } from "./core.js";

const KEY = "pt-real-llm";

export const realLLM = () => { try { return aiOn() && localStorage.getItem(KEY) === "1"; } catch { return false; } };

export function realLLMToggleHTML() {
  if (!aiOn()) return `<p class="faint small" style="margin:10px 0 0">Connect an AI in Settings to let <code>llm()</code> make real model calls from Run.</p>`;
  return `<label class="real-llm"><input type="checkbox" data-real-llm ${realLLM() ? "checked" : ""}>
    Real model calls: <code>from pytrainer_llm import llm, embed</code> reaches ${esc(aiName())} (up to 6 per run)</label>`;
}

document.addEventListener("change", (e) => {
  if (!e.target.matches?.("[data-real-llm]")) return;
  try { localStorage.setItem(KEY, e.target.checked ? "1" : "0"); } catch {}
});

export function llmCallsHTML(calls) {
  if (!calls?.length) return "";
  const ok = calls.filter((c) => !c.error).length;
  return `<details class="llm-calls"><summary>${ok} real model call${ok === 1 ? "" : "s"}${calls.length > ok ? `, ${calls.length - ok} refused` : ""}</summary>
    ${calls.map((c, i) => `<div class="llm-call"><b>${i + 1}.</b> <span class="faint">${c.ms} ms</span><div><span class="faint">prompt:</span> ${esc(c.prompt)}</div>
      <div>${c.error ? `<span class="err">${esc(c.error)}</span>` : `<span class="faint">reply:</span> ${esc(c.reply)}`}</div></div>`).join("")}</details>`;
}
