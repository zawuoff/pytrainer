/* Zen mode for steps and projects: only the editor and Run/Check stay on screen. The task slides in
   on demand (T or the Task button), XP pings are muted, and the choice follows you to the next step
   until you leave it (Alt+Z, Esc, or Exit). */
import { $ } from "./core.js";

const KEY = "pt-zen";
const inWorkspace = () => document.body.classList.contains("focus");

function bar() {
  let el = $("#zen-bar");
  if (!el) {
    el = document.createElement("div");
    el.id = "zen-bar";
    el.innerHTML = `<span class="zen-label">Zen</span><button type="button" data-zen="task" aria-pressed="false" title="Show the task (T)">Task</button><button type="button" data-zen="exit" title="Alt+Z or Esc">Exit</button>`;
    el.addEventListener("click", (e) => {
      const b = e.target.closest("[data-zen]");
      if (!b) return;
      if (b.dataset.zen === "exit") setZen(false); else toggleTask();
    });
    document.body.appendChild(el);
  }
  return el;
}

function refreshEditors() {
  setTimeout(() => document.querySelectorAll(".CodeMirror").forEach((el) => el.CodeMirror?.refresh()), 30);
}

function toggleTask(force) {
  const on = force ?? !document.body.classList.contains("zen-task");
  document.body.classList.toggle("zen-task", on);
  $("#zen-bar [data-zen=task]")?.setAttribute("aria-pressed", String(on));
}

export function setZen(on, remember = true) {
  on = on && inWorkspace();
  document.body.classList.toggle("zen", on);
  if (!on) toggleTask(false);
  bar().hidden = !on;
  if (remember) { try { on ? sessionStorage.setItem(KEY, "1") : sessionStorage.removeItem(KEY); } catch {} }
  refreshEditors();
}

/* Called after every route change: keep zen across steps, drop it everywhere else. */
export function zenAfterRoute() {
  let want = false;
  try { want = sessionStorage.getItem(KEY) === "1"; } catch {}
  setZen(want && inWorkspace(), false);
}

document.addEventListener("keydown", (e) => {
  if (e.altKey && !e.ctrlKey && !e.metaKey && e.code === "KeyZ") {
    if (!inWorkspace()) return;
    e.preventDefault();
    setZen(!document.body.classList.contains("zen"));
  } else if (e.key === "Escape" && document.body.classList.contains("zen") && !e.defaultPrevented && !document.querySelector(".cm-hints")) {
    if (document.body.classList.contains("zen-task")) toggleTask(false); else setZen(false);
  } else if (e.key.toLowerCase() === "t" && document.body.classList.contains("zen") && !e.altKey && !e.ctrlKey && !e.metaKey
             && !/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement?.tagName) && !document.activeElement?.isContentEditable) {
    e.preventDefault();
    toggleTask();
  }
});
