/* PyTrainer front-end: a hash-routed single page app, no build step. This is the entry module:
   it owns the router and imports every view. Shared helpers live in core.js, the lesson widgets in
   diagrams.js and blocks.js, the editor/results pieces in workspace.js, one file per page in views/. */
import { $$, S, api, esc, lastInteraction, main, refreshState, runCleanup } from "./core.js";
import { viewLibrary } from "./library.js";
import { viewHome } from "./views/home.js";
import { viewChapter, viewCourse, viewExam, viewExtras } from "./views/course.js";
import { viewStep } from "./views/step.js";
import { viewReviews } from "./views/reviews.js";
import { viewWelcome } from "./views/onboarding.js";
import { viewPlacement, viewPlacementQuestion } from "./views/placement.js";
import { viewProject, viewProjects } from "./views/projects.js";
import { viewCapstone } from "./views/capstone.js";
import { viewDrill } from "./views/drill.js";
import { viewMap } from "./views/map.js";
import { viewRadar } from "./views/radar.js";
import { viewInterview } from "./views/interview.js";
import { viewLeaderboard } from "./views/leaderboard.js";
import { viewTraces } from "./views/traces.js";
import { viewAchievements } from "./views/achievements.js";
import { viewLabs } from "./views/labs.js";
import { viewProgress } from "./views/progress.js";
import { viewSettings } from "./views/settings.js";

/* ---------------------------------------------------------------- router */

const routes = [
  [/^#\/home$/, viewHome],
  [/^#\/welcome(\?place)?$/, viewWelcome],
  [/^#\/course(?:\/([\w-]+))?$/, viewCourse],
  [/^#\/chapter\/([\w-]+)(\?notes)?$/, viewChapter],
  [/^#\/topic\/([\w-]+)(\?learn)?$/, (id) => { location.replace("#/chapter/" + id); }],
  [/^#\/step\/([\w-]+)(\?review(?:-original)?)?$/, viewStep],
  [/^#\/ex\/([\w-]+)(\?review)?$/, (id, r) => { location.replace("#/step/" + id + (r || "")); }],
  [/^#\/exam\/([\w-]+)$/, viewExam],
  [/^#\/extras$/, viewExtras],
  [/^#\/reviews$/, viewReviews],
  [/^#\/library$/, viewLibrary],
  [/^#\/placement$/, viewPlacement],
  [/^#\/placement\/([\w-]+)$/, viewPlacementQuestion],
  [/^#\/projects$/, viewProjects],
  [/^#\/project\/([\w-]+)$/, viewProject],
  [/^#\/capstone$/, viewCapstone],
  [/^#\/drill$/, viewDrill],
  [/^#\/map$/, viewMap],
  [/^#\/radar$/, viewRadar],
  [/^#\/interview$/, viewInterview],
  [/^#\/leaderboard$/, viewLeaderboard],
  [/^#\/traces$/, viewTraces],
  [/^#\/achievements$/, viewAchievements],
  [/^#\/labs$/, viewLabs],
  [/^#\/progress$/, viewProgress],
  [/^#\/settings$/, viewSettings],
];

let routeTurn = 0, routeWant = 0, routeChain = Promise.resolve();
function route() {
  const want = ++routeWant;
  routeChain = routeChain.then(() => (want === routeWant ? showRoute() : null)).catch((e) => console.error(e));
  return routeChain;
}
async function showRoute() {
  runCleanup();
  const hash = location.hash || "#/home";
  if (!S) {
    try { await refreshState(); }
    catch (e) { main.innerHTML = `<div class="page"><div class="errbox">Cannot reach the PyTrainer server: ${esc(e.message)}</div></div>`; return; }
  }
  if (!S.settings.onboarded && !/^#\/(welcome|placement|settings)/.test(hash)) { location.hash = "#/welcome"; return; }
  const nav = hash.split("/")[1]?.split("?")[0];
  document.body.classList.toggle("focus", /^#\/(step|project|placement)\//.test(hash));
  const navMap = { achievements: "progress", traces: "projects", leaderboard: "projects", interview: "projects", radar: "progress", map: "course", drill: "reviews", capstone: "projects", step: "course", chapter: "course", exam: "course", extras: "course", project: "projects", placement: "home", welcome: "home", today: "home" };
  $$(".nav a[data-nav]").forEach((a) => a.classList.toggle("on", a.dataset.nav === (navMap[nav] || nav)));
  for (const [rx, fn] of routes) {
    const m = hash.match(rx);
    if (m) {
      main.scrollTop = 0;
      const turn = ++routeTurn;
      main.dataset.enter = "1";
      try { await fn(...m.slice(1)); }
      catch (e) { console.error(e); main.innerHTML = `<div class="page"><div class="errbox">${esc(e.message)}</div></div>`; }
      setTimeout(() => { if (turn === routeTurn) delete main.dataset.enter; }, 900);
      return;
    }
  }
  location.hash = "#/home";
}
window.addEventListener("hashchange", route);

setInterval(() => {
  if (document.visibilityState === "visible" && Date.now() - lastInteraction < 120000) api("heartbeat", { seconds: 30 }).catch(() => {});
}, 30000);

route();
