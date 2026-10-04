/* A practice session: an ordered list of steps (from the weakness radar or a mistakes drill) that the
   step page walks through with "n of N · Next". Kept per browser; ending it or finishing clears it. */
import { esc } from "./core.js";

const KEY = "pt-session";

function load() {
  try { return JSON.parse(localStorage.getItem(KEY) || "null"); } catch { return null; }
}

export function startSession(title, steps) {
  if (!steps.length) return;
  try { localStorage.setItem(KEY, JSON.stringify({ title, steps })); } catch {}
  location.hash = steps[0].href;
}

export function endSession() {
  try { localStorage.removeItem(KEY); } catch {}
}

/* The banner for the step page, or "" when this step isn't part of the current session. */
export function sessionBanner(stepId) {
  const s = load();
  const i = s ? s.steps.findIndex((x) => x.id === stepId) : -1;
  if (i < 0) return "";
  const next = s.steps[i + 1];
  return `<div class="sess-bar"><span><b>${esc(s.title)}</b> · ${i + 1} of ${s.steps.length}${s.steps[i].reason ? ` · <span class="faint">${esc(s.steps[i].reason)}</span>` : ""}</span>
    <span class="row" style="gap:6px">${next ? `<a class="btn small" href="${esc(next.href)}">Next in session</a>` : `<a class="btn small" href="#/radar" data-end-session>Finish session</a>`}
    <button class="btn small ghost" type="button" data-end-session>End</button></span></div>`;
}

document.addEventListener("click", (e) => {
  const el = e.target.closest("[data-end-session]");
  if (!el) return;
  endSession();
  el.closest(".sess-bar")?.remove();
});
