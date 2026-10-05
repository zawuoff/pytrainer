import { $, esc } from "./core.js";

/* ---------------------------------------------------------------- the installable app (PWA)

   The service worker (static/sw.js) keeps an offline copy of the app's files, so the installed app
   opens without the network; progress still comes from the server. Browsers only run service
   workers, and only offer to install, on https:// or localhost. */

let promptEvent = null;   // the browser's "install this app" offer, when it has made one

export function setupInstall() {
  if ("serviceWorker" in navigator && window.isSecureContext) {
    navigator.serviceWorker.register("sw.js").catch((e) => console.warn("service worker:", e));
  }
  // Not prevented, so phones still show their own install banner; Settings keeps a button too.
  window.addEventListener("beforeinstallprompt", (e) => { promptEvent = e; drawInstall(); });
  window.addEventListener("appinstalled", () => { promptEvent = null; drawInstall(); });
}

const installed = () => matchMedia("(display-mode: standalone)").matches || navigator.standalone === true;
const isIOS = () => /iPhone|iPad|iPod/.test(navigator.userAgent) || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);

/* The "App" panel in Settings. */
export function drawInstall() {
  const box = $("#install-box");
  if (!box) return;
  const host = location.hostname;
  let h;
  if (installed()) h = `<p style="margin:0"><b>You're using the installed app.</b> It opens straight to PyTrainer, and still opens when the server can't be reached (your progress shows again once it can).</p>`;
  else if (promptEvent) h = `<div class="row between"><p style="margin:0">Install PyTrainer as an app: its own window and icon, a home-screen icon on a phone, and it opens without the network.</p>
      <button class="btn primary" id="install-btn">Install</button></div>`;
  else if (!window.isSecureContext) h = `<p style="margin:0">Installing needs a secure address (<code>https://</code>, or <code>localhost</code> on this computer), and <code>${esc(host)}</code> is plain http.</p>
      <p class="dim small" style="margin:8px 0 0">To use it on your phone over Tailscale: on the computer running PyTrainer, run <code>tailscale serve --bg ${esc(location.port || "80")}</code>, then open the <code>https://….ts.net</code> address it prints on your phone and install from there.</p>`;
  else if (isIOS()) h = `<p style="margin:0">In Safari, tap <b>Share</b>, then <b>Add to Home Screen</b>. PyTrainer then opens like an app, without the browser around it.</p>`;
  else h = `<p style="margin:0">Use your browser's menu: <b>Install app</b> (or <b>Add to Home screen</b> on a phone). It gets its own window and icon, and opens without the network.</p>`;
  box.innerHTML = h;
  $("#install-btn")?.addEventListener("click", async () => {
    const ev = promptEvent;
    promptEvent = null;
    await ev.prompt();
    drawInstall();
  });
}
