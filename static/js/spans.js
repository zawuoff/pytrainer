/* The built-in trace viewer: spans (from a run's traces.jsonl, or a file you open on #/traces) drawn
   as a waterfall, one group per trace. Rows nest under their parent span; click one for its attributes. */
import { esc } from "./core.js";

const KINDS = [["llm", "model call"], ["tool", "tool call"], ["other", "other work"]];
const kind = (name) => (/^(llm|model|gen_ai)\b/i.test(name) ? "llm" : /^tool\b/i.test(name) ? "tool" : "other");
const fmt = (ms) => (ms === 0 ? "0" : ms >= 1000 ? `${(ms / 1000).toFixed(2)} s` : ms >= 10 ? `${Math.round(ms)} ms` : `${ms.toFixed(1)} ms`);

/* Depth-first rows (children sorted by start), so each span sits right under its parent. */
function treeRows(spans) {
  const byId = new Map(spans.filter((s) => s.span_id).map((s) => [s.span_id, s]));
  const kids = new Map();
  const roots = [];
  for (const s of spans) {
    if (s.parent_id && byId.has(s.parent_id) && s.parent_id !== s.span_id) {
      if (!kids.has(s.parent_id)) kids.set(s.parent_id, []);
      kids.get(s.parent_id).push(s);
    } else roots.push(s);
  }
  const rows = [], seen = new Set();
  const walk = (s, depth) => {
    if (seen.has(s)) return;
    seen.add(s);
    rows.push({ s, depth });
    (kids.get(s.span_id) || []).sort((a, b) => a.start - b.start).forEach((c) => walk(c, depth + 1));
  };
  roots.sort((a, b) => a.start - b.start).forEach((r) => walk(r, 0));
  return rows;
}

/* Group spans into traces: by trace_id when spans have one, otherwise by their root. */
function traces(spans) {
  const groups = new Map();
  for (const s of spans) {
    const key = s.trace_id || "_";
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(s);
  }
  return [...groups.values()].sort((a, b) => Math.min(...a.map((s) => s.start)) - Math.min(...b.map((s) => s.start)));
}

const attrValue = (v) => (v === null ? "null" : typeof v === "string" ? v : JSON.stringify(v));

function traceHTML(spans, n) {
  const t0 = Math.min(...spans.map((s) => s.start));
  const total = Math.max(...spans.map((s) => s.end)) - t0 || 1e-9;
  const errors = spans.filter((s) => s.status === "error").length;
  const root = treeRows(spans)[0]?.s;
  const ticks = [0, 0.25, 0.5, 0.75, 1];
  return `<div class="wf" role="table" aria-label="Trace ${n}: ${spans.length} spans">
    <div class="wf-head"><b>${esc(root?.name || "trace")}</b><span class="faint">${spans.length} span${spans.length === 1 ? "" : "s"} · ${fmt(total * 1000)}</span>
      ${errors ? `<span class="wf-errs">✕ ${errors} error${errors === 1 ? "" : "s"}</span>` : ""}</div>
    <div class="wf-axis" aria-hidden="true"><span></span><span class="wf-ticks">${ticks.map((t) => `<i style="left:${t * 100}%">${fmt(t * total * 1000)}</i>`).join("")}</span><span></span></div>
    ${treeRows(spans).map(({ s, depth }) => {
      const ms = (s.end - s.start) * 1000;
      const left = ((s.start - t0) / total) * 100;
      const width = Math.max(0.6, (ms / 1000 / total) * 100);
      const attrs = Object.entries(s.attributes || {});
      return `<button class="wf-row k-${kind(s.name)} ${s.status === "error" ? "err" : ""}" role="row" aria-expanded="false" data-span>
        <span class="wf-name" style="padding-left:${Math.min(depth, 8) * 14}px" title="${esc(s.name)}">${s.status === "error" ? `<b class="wf-x" aria-label="error">✕</b>` : ""}${esc(s.name)}</span>
        <span class="wf-track"><i style="left:${Math.min(left, 99.4)}%;width:${Math.min(width, 100 - Math.min(left, 99.4))}%"></i></span>
        <span class="wf-ms">${fmt(ms)}</span></button>
      <div class="wf-detail" hidden><dl>
        <dt>starts at</dt><dd>${fmt((s.start - t0) * 1000)}</dd><dt>duration</dt><dd>${fmt(ms)}</dd><dt>status</dt><dd>${esc(s.status)}</dd>
        ${attrs.map(([k, v]) => `<dt>${esc(k)}</dt><dd>${esc(attrValue(v))}</dd>`).join("")}
        ${s.span_id ? `<dt>span id</dt><dd class="faint">${esc(s.span_id)}${s.parent_id ? ` · parent ${esc(s.parent_id)}` : ""}</dd>` : ""}</dl></div>`;
    }).join("")}</div>`;
}

export function spansHTML(spans, { open = true } = {}) {
  if (!spans?.length) return "";
  const groups = traces(spans);
  const legend = `<span class="wf-legend">${KINDS.map(([k, label]) => `<span class="k-${k}"><i></i>${label}</span>`).join("")}<span class="err"><i></i>error</span></span>`;
  return `<details class="spans" ${open ? "open" : ""}><summary>Trace waterfall: ${spans.length} span${spans.length === 1 ? "" : "s"}${groups.length > 1 ? ` in ${groups.length} traces` : ""}</summary>
    ${legend}${groups.slice(0, 20).map((g, i) => traceHTML(g, i + 1)).join("")}
    ${groups.length > 20 ? `<p class="faint small">Showing the first 20 of ${groups.length} traces.</p>` : ""}</details>`;
}

document.addEventListener("click", (e) => {
  const row = e.target.closest?.("[data-span]");
  if (!row) return;
  const detail = row.nextElementSibling;
  const open = detail.hidden;
  detail.hidden = !open;
  row.setAttribute("aria-expanded", String(open));
});
