"""Real model calls from sandboxed code, without giving the sandbox any network.

When Run is asked for real model calls, the run folder gets ``pytrainer_llm.py``. Its ``llm()``
writes each request as a JSON file into ``_llm/`` and waits for the answer file. The runner, which
is outside the sandbox, picks the request up, sends it through the learner's connected AI CLI and
writes the reply back. So learner code only ever touches files in its own folder, every call is
capped (``BUDGET`` per run) and logged, and grading never uses this: checks stay deterministic.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

BUDGET = 6
MAX_PROMPT = 20_000
DEFAULT_SYSTEM = "You are a helpful assistant. Answer concisely."

HELPER = r'''"""Real model calls from PyTrainer's Run button (when "Real model calls" is ticked).

    from pytrainer_llm import llm, embed

    llm("Name one RAG failure mode.")                     # -> the model's reply, a string
    llm([{"role": "user", "content": "hi"}], system="Be brief.")
    embed(["first text", "second text"])                  # -> one vector per text

llm() goes to the AI you connected in Settings, at most 6 calls per run. embed() is a small local
stand-in (a hashed bag of words), not a real embedding model, so RAG code has something to run on.
"""

import json
import os
import re
import time
import zlib

_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_llm")
_count = 0


def llm(prompt, system=None, timeout=120):
    """Send one prompt (a string, or a list of chat messages) to your model and return its reply."""
    global _count
    if isinstance(prompt, (list, tuple)):
        prompt = "\n\n".join(f"{m.get('role', 'user')}: {m.get('content', '')}" for m in prompt)
    _count += 1
    request = os.path.join(_DIR, f"req-{_count}.json")
    answer = os.path.join(_DIR, f"res-{_count}.json")
    with open(request + ".part", "w", encoding="utf-8") as fh:
        json.dump({"prompt": str(prompt), "system": system}, fh)
    os.replace(request + ".part", request)
    deadline = time.time() + timeout
    while not os.path.exists(answer):
        if time.time() > deadline:
            raise TimeoutError("the model did not answer in time")
        time.sleep(0.05)
    with open(answer, encoding="utf-8") as fh:
        data = json.load(fh)
    if "error" in data:
        raise RuntimeError(data["error"])
    return data["text"]


def embed(texts, dims=256):
    """A local stand-in for an embeddings API: words (3+ letters) hashed into `dims` buckets."""
    vectors = []
    for text in texts:
        vector = [0.0] * dims
        for word in re.findall(r"[a-z0-9]{3,}", str(text).lower()):
            vector[zlib.crc32(word.encode()) % dims] += 1.0
        vectors.append(vector)
    return vectors
'''


def install(folder: Path) -> None:
    (folder / "pytrainer_llm.py").write_text(HELPER, encoding="utf-8")
    (folder / "_llm").mkdir(exist_ok=True)


def serve(folder: Path, llm, calls: list[dict]) -> float:
    """Answer every waiting request. Returns the seconds spent waiting on the model."""
    spent = 0.0
    box = folder / "_llm"
    for request in sorted(box.glob("req-*.json"), key=lambda p: int(p.stem.split("-")[1])):
        answer = box / ("res-" + request.stem.split("-")[1] + ".json")
        if answer.exists():
            continue
        try:
            data = json.loads(request.read_text(encoding="utf-8"))
            prompt, system = str(data.get("prompt", ""))[:MAX_PROMPT], data.get("system")
        except (OSError, ValueError):
            prompt, system = "", None
        started = time.time()
        entry = {"prompt": prompt[:200], "reply": "", "ms": 0, "error": None}
        if len(calls) >= BUDGET:
            reply = {"error": f"call limit reached ({BUDGET} real model calls per run)"}
        elif not prompt.strip():
            reply = {"error": "empty prompt"}
        else:
            try:
                text = llm(prompt, str(system) if system else DEFAULT_SYSTEM)
                reply = {"text": text}
                entry["reply"] = text[:300]
            except Exception as exc:  # the AI CLI failed: tell the learner's code, keep running
                reply = {"error": f"{type(exc).__name__}: {exc}"}
        entry["error"] = reply.get("error")
        entry["ms"] = int((time.time() - started) * 1000)
        spent += time.time() - started
        calls.append(entry)
        part = answer.with_suffix(".part")
        part.write_text(json.dumps(reply), encoding="utf-8")
        part.replace(answer)
    return spent
