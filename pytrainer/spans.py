"""Read trace spans (JSON Lines, one span per line) for the built-in waterfall viewer.

A run that leaves a ``traces.jsonl`` in its folder gets its spans back in ``result["spans"]``. The
format is the one the Trace Your Agent project writes, and close enough to OpenTelemetry's that
other exporters work too: each line needs a ``name`` and numeric ``start``/``end`` (seconds), and
may have ``span_id``, ``parent_id``, ``trace_id``, ``status`` and ``attributes``. Lines that don't
fit are skipped, never fatal: the viewer is a debugging aid.
"""

from __future__ import annotations

import json
from pathlib import Path

FILE = "traces.jsonl"
MAX_SPANS = 2000
MAX_BYTES = 2_000_000
MAX_ATTR = 2000

# What the Trace Your Agent demo writes (ids shortened, times from 0): shown by "Try a sample".
SAMPLE = '''\
{"name": "llm.call", "trace_id": "s1", "span_id": "s3", "parent_id": "s2", "start": 0.0, "end": 0.06, "status": "ok", "attributes": {"step": 1, "messages": 1, "reply": "tool_calls", "input_tokens": 120, "output_tokens": 30}}
{"name": "tool.get_order", "trace_id": "s1", "span_id": "s4", "parent_id": "s2", "start": 0.06, "end": 0.08, "status": "error", "attributes": {"call_id": "c1", "arguments": "{\\"order_id\\": \\"B7\\"}", "error": "Error: KeyError: 'B7'", "result": "Error: KeyError: 'B7'"}}
{"name": "tool.search_docs", "trace_id": "s1", "span_id": "s5", "parent_id": "s2", "start": 0.081, "end": 0.111, "status": "ok", "attributes": {"call_id": "c2", "arguments": "{\\"query\\": \\"refund time\\"}", "result": "Refunds are paid within 5 business days."}}
{"name": "agent.step", "trace_id": "s1", "span_id": "s2", "parent_id": "s1", "start": 0.0, "end": 0.111, "status": "ok", "attributes": {"step": 1}}
{"name": "llm.call", "trace_id": "s1", "span_id": "s7", "parent_id": "s6", "start": 0.111, "end": 0.171, "status": "ok", "attributes": {"step": 2, "messages": 4, "reply": "tool_calls", "input_tokens": 210, "output_tokens": 18}}
{"name": "tool.get_order", "trace_id": "s1", "span_id": "s8", "parent_id": "s6", "start": 0.171, "end": 0.191, "status": "ok", "attributes": {"call_id": "c3", "arguments": "{\\"order_id\\": \\"A1\\"}", "result": "{\\"id\\": \\"A1\\", \\"status\\": \\"shipped\\"}"}}
{"name": "agent.step", "trace_id": "s1", "span_id": "s6", "parent_id": "s1", "start": 0.111, "end": 0.191, "status": "ok", "attributes": {"step": 2}}
{"name": "llm.call", "trace_id": "s1", "span_id": "s10", "parent_id": "s9", "start": 0.191, "end": 0.251, "status": "ok", "attributes": {"step": 3, "messages": 6, "reply": "final", "input_tokens": 260, "output_tokens": 40}}
{"name": "agent.step", "trace_id": "s1", "span_id": "s9", "parent_id": "s1", "start": 0.191, "end": 0.251, "status": "ok", "attributes": {"step": 3}}
{"name": "agent.run", "trace_id": "s1", "span_id": "s1", "parent_id": null, "start": 0.0, "end": 0.251, "status": "ok", "attributes": {"question": "Where is my order, and how long do refunds take?", "steps": 3, "answer": "Order A1 has shipped. Refunds are paid within 5 business days.", "input_tokens": 590, "output_tokens": 88}}
'''


def _attrs(raw) -> dict:
    if not isinstance(raw, dict):
        return {}
    out = {}
    for key, value in list(raw.items())[:50]:
        if not isinstance(value, (str, int, float, bool, type(None))):
            value = json.dumps(value, default=str)
        if isinstance(value, str):
            value = value[:MAX_ATTR]
        out[str(key)[:100]] = value
    return out


def normalise(row) -> dict | None:
    """One span in the viewer's shape, or None when the row isn't a usable span."""
    if not isinstance(row, dict) or not isinstance(row.get("name"), str):
        return None
    start, end = row.get("start"), row.get("end")
    if not all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in (start, end)) or end < start:
        return None
    ident = lambda v: None if v is None else str(v)[:64]  # noqa: E731
    return {"name": row["name"][:200], "span_id": ident(row.get("span_id")), "parent_id": ident(row.get("parent_id")),
            "trace_id": ident(row.get("trace_id")), "start": float(start), "end": float(end),
            "status": "error" if row.get("status") == "error" else "ok", "attributes": _attrs(row.get("attributes"))}


def parse(text: str) -> list[dict]:
    spans = []
    for line in text[:MAX_BYTES].splitlines():
        if len(spans) >= MAX_SPANS:
            break
        line = line.strip()
        if not line:
            continue
        try:
            span = normalise(json.loads(line))
        except ValueError:
            continue
        if span:
            spans.append(span)
    return spans


def collect(folder: Path) -> list[dict]:
    """The spans a run left in its folder (empty when it wrote none)."""
    path = folder / FILE
    try:
        if not path.is_file():
            return []
        with open(path, encoding="utf-8", errors="replace") as fh:
            return parse(fh.read(MAX_BYTES))
    except OSError:
        return []
