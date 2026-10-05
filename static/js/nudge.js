import { $, S, aiOn, cleanup, esc, lastInteraction } from "./core.js";

/* ---------------------------------------------------------------- live tutor nudges

   When the same check keeps failing for a few minutes, offer a way forward (a hint, the tutor,
   stepping through the code) instead of waiting for the learner to ask. It's an offer in the
   corner, never a popup that takes focus, and "Not now" quiets it for a while. */

export const NUDGE_AFTER = 3 * 60 * 1000;        // the same check failing this long, over 2+ checks
export const NUDGE_ALONE = 6 * 60 * 1000;        // or this long after a single failing check
const SNOOZE = 5 * 60 * 1000;
const ACTIVE = 2 * 60 * 1000;                    // only while they're at it, not away from the keyboard

/* What "the same failure" means: the first failing check by name, or the kind of error. */
export function failureKey(r) {
  if (!r || r.status === "passed") return null;
  if (r.error) {
    const last = r.error.trim().split("\n").pop() || "";
    return "error:" + (last.match(/^(\w+(?:Error|Exception|Interrupt))\b/)?.[1] || (r.status === "timeout" ? "timeout" : "error"));
  }
  const t = r.tests?.find((x) => !x.passed);
  return t ? "check:" + t.name : null;
}

function label(key) {
  const v = key.slice(key.indexOf(":") + 1);
  if (key.startsWith("check:")) return `“${v}”`;
  if (v === "timeout") return "the time limit";
  if (v === "error") return "this error";
  return `${/^[AEIOU]/.test(v) ? "an" : "a"} ${v}`;
}

/* host: the element the card goes in (positioned). actions: hint() gives {next, total} while hints
   are left, else null; onHint(); onTutor(message); onDebug() or null where stepping through can't help. */
export function createNudger(host, actions) {
  let stuck = null;   // {key, since, checks, snoozed}
  const on = () => S.settings.nudges !== false;

  function hide() { $(".nudge", host)?.remove(); }
  function show() {
    if ($(".nudge", host)) return;
    const mins = Math.max(1, Math.round((Date.now() - stuck.since) / 60000));
    const h = actions.hint();
    const el = document.createElement("div");
    el.className = "nudge";
    el.setAttribute("role", "status");
    el.innerHTML = `<button class="nudge-x" aria-label="Not now" title="Not now">×</button>
      <b>Stuck on ${esc(label(stuck.key))}?</b>
      <p>It's been failing for ${mins} minute${mins === 1 ? "" : "s"}. That's part of learning; here's a way forward:</p>
      <div class="row">${h ? `<button class="btn small primary" data-a="hint">Hint ${h.next} of ${h.total}</button>` : ""}
        ${aiOn() ? `<button class="btn small ${h ? "" : "primary"}" data-a="tutor">Ask the tutor where to look</button>` : ""}
        ${actions.onDebug ? `<button class="btn small ghost" data-a="debug">Step through it</button>` : ""}
        <button class="btn small ghost" data-a="later">Not now</button></div>`;
    host.appendChild(el);
    el.querySelectorAll("[data-a]").forEach((b) => b.onclick = () => act(b.dataset.a));
    el.querySelector(".nudge-x").onclick = () => act("later");
  }
  function act(a) {
    hide();
    if (a === "later") { stuck.snoozed = Date.now() + SNOOZE; return; }
    // Help was taken: give it time to work before offering more.
    stuck.since = Date.now(); stuck.checks = 0;
    if (a === "hint") actions.onHint();
    else if (a === "tutor") actions.onTutor(`I've been stuck on ${label(stuck.key)} for a few minutes. Where should I look, without giving me the answer?`);
    else if (a === "debug") actions.onDebug();
  }
  function tick() {
    if (!stuck || !on() || $(".nudge", host)) return;
    const now = Date.now(), long = now - stuck.since;
    if (now < (stuck.snoozed || 0) || now - lastInteraction > ACTIVE) return;
    if ((stuck.checks >= 2 && long >= NUDGE_AFTER) || long >= NUDGE_ALONE) show();
  }
  const timer = setInterval(tick, 10000);
  cleanup.push(() => clearInterval(timer));

  return {
    /* Feed every check result in. */
    result(r) {
      const key = failureKey(r);
      if (!key) { stuck = null; hide(); return; }
      if (stuck?.key === key) stuck.checks += 1;
      else { stuck = { key, since: Date.now(), checks: 1, snoozed: 0 }; hide(); }
      tick();
    },
  };
}
