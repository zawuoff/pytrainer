/* "Open in VS Code": put this step's or project's files in a folder, open your editor there, and
   reload the browser editor whenever you save. While it watches, the page editor is read-only so
   the two never disagree; Stop watching hands editing back to the page. */
import { api, cleanup, esc, toast } from "./core.js";

const POLL_MS = 1200;

export function folderSync({ kind, id, ed, banner, onReload }) {
  let timer = null, stamp = {}, folder = "", busy = false;

  function stop() {
    clearInterval(timer); timer = null;
    ed.cm.setOption("readOnly", false);
    banner.hidden = true; banner.innerHTML = "";
    ed.cm.refresh();
  }

  async function poll() {
    if (busy) return;
    busy = true;
    try {
      const r = await api("sync/poll", { kind, id, names: ed.names(), stamp });
      stamp = r.stamp;
      if (Object.keys(r.changed).length) {
        ed.set(r.changed);
        onReload?.(Object.keys(r.changed));
        flash(`Reloaded ${Object.keys(r.changed).join(", ")} from your editor`);
      }
      if (r.missing.length) flash(`${r.missing.join(", ")} is missing from the folder`, true);
    } catch { /* the server restarting shouldn't end the watch */ }
    busy = false;
  }

  function flash(text, bad = false) {
    const el = banner.querySelector(".sync-flash");
    if (!el) return;
    el.textContent = text; el.classList.toggle("bad", bad);
    el.classList.remove("on"); void el.offsetWidth; el.classList.add("on");
  }

  async function open() {
    let r;
    try { r = await api("sync/open", { kind, id, files: ed.files(), file: ed.active }); }
    catch (err) { toast(err.message, true); return; }
    folder = r.folder; stamp = r.stamp;
    ed.set(r.files);
    if (r.url) location.href = r.url;  // no editor command on PATH: let VS Code's link handler open it
    toast(r.opened ? `Opened in ${r.opened}` : "Opening VS Code… (if nothing happens, open the folder yourself)");
    if (r.kept.length) toast(`Kept your work from the folder: ${r.kept.join(", ")}`);
    ed.cm.setOption("readOnly", true);
    banner.hidden = false;
    banner.innerHTML = `<span class="sync-msg"><span class="sync-dot" aria-hidden="true"></span>Editing in ${esc(r.opened || "your editor")}: <code title="${esc(folder)}">${esc(r.display)}</code>. Saves show up here, and Run and Check use them.</span>
      <span class="sync-flash" aria-live="polite"></span><span class="grow"></span><button class="btn small ghost" data-sync="stop">Stop watching</button>`;
    ed.cm.refresh();
    banner.querySelector("[data-sync=stop]").onclick = () => { stop(); toast("Editing here again."); };
    clearInterval(timer);
    timer = setInterval(poll, POLL_MS);
  }

  cleanup.push(() => clearInterval(timer));
  return { open, stop, get watching() { return !!timer; } };
}
