PROJECT = {
    "id": "rag-evals",
    "title": "RAG with Evals, Traces & a Release Gate",
    "module": "evals",
    "order": 14,
    "level": "Advanced",
    "estimated_hours": 5,
    "requires": ["vectors", "json", "files", "classes", "regex", "sorting"],
    "tags": ["rag", "evals", "llm-as-judge", "tracing", "latency", "cost", "capstone"],
    "main": "evals.py",
    "files": ["rag.py", "evals.py", "eval_set.jsonl", "docs.jsonl"],
    "brief": r'''
# RAG with evals, traces and a release gate (capstone)

Anyone can demo a RAG app. What gets people hired is proving it **works, keeps working,
and what it costs**. In this capstone you ship a RAG pipeline together with the tools a
team uses to trust it:

- an **eval set** (`eval_set.jsonl`, 24 cases to start with) with the documents each
  question needs and phrases a correct answer must contain;
- **graders**: retrieval hit@k, "does the answer cite real sources", "does it contain the
  key facts", and an **LLM-as-judge** score;
- a **trace record** for every request: latency (retrieval, generation, total), tokens
  and cost;
- a **release gate** that compares a new eval run to a saved baseline and blocks the
  release if quality drops or latency/cost go up too much.

The embedding model, the LLM, the judge model and the clock are all **injected**, so the
tests use fakes and you can plug in any real provider.

## Files

- `docs.jsonl`: the knowledge base, one `{"id": "refunds", "text": "..."}` per line.
- `eval_set.jsonl`: one case per line:
  `{"id": "q01", "question": "...", "expected_doc_ids": ["refunds"], "must_include": ["30 days"]}`.
  Keep at least 20 valid cases. You may add more (try some tricky ones).
- `rag.py`: the pipeline. `evals.py`: graders, runner and gate.

## `rag.py`

```python
PRICES = {"fake-small": {"input": 0.15, "output": 0.60}, "fake-large": {...}}  # USD per 1M tokens

def load_docs(path): ...                      # JSONL -> list of dicts (skip blank lines)

class RAGPipeline:
    def __init__(self, embed, llm, docs, *, clock=time.perf_counter,
                 model="fake-small", k=3, prices=PRICES): ...
    def retrieve(self, question, k=None): ...  # -> [{"id", "text", "score"}, ...]
    def build_prompt(self, question, sources): ...
    def answer(self, question): ...            # -> {"answer", "doc_ids", "trace"}
    def save_traces(self, path): ...
    # attribute: self.traces -> list of trace dicts, oldest first
```

- `embed(texts) -> list[list[float]]`, `llm(prompt) -> {"text": str, "usage":
  {"input_tokens": int, "output_tokens": int}}`, `clock() -> float` (seconds).
- `__init__`: raise `ValueError` if `model` is not in `prices` or two documents share an
  id. Embed **all** documents with **one** `embed` call (no call if there are none).
- `retrieve`: embed the question with one call, score every document by **cosine
  similarity** (`0.0` if a vector has zero length), return the best `k` (default
  `self.k`), best first. Ties keep document order.
- `build_prompt(question, sources)` fills `PROMPT_TEMPLATE` (given in the starter).
  `{sources}` is one line per source, `[<id>] <text>`, joined with `"\n"`.
- `answer(question)`: call `clock()` exactly **three** times: before retrieval, after
  retrieval, after the LLM call. Then build and append this trace:

  ```python
  {
      "request_id": 1,                 # 1, 2, 3... per pipeline
      "question": "...", "model": "fake-small",
      "retrieved": ["refunds", "sla", "pricing"],
      "retrieval_ms": 12.5,            # (t1 - t0) * 1000, rounded to 1 decimal
      "generation_ms": 500.0,          # (t2 - t1) * 1000, rounded to 1 decimal
      "latency_ms": 512.5,             # (t2 - t0) * 1000, rounded to 1 decimal
      "input_tokens": 2000, "output_tokens": 500,   # from the llm usage
      "cost_usd": 0.0135,              # tokens x price / 1_000_000, rounded to 8 decimals
  }
  ```
  Return `{"answer": <llm text>, "doc_ids": <retrieved ids>, "trace": <that dict>}`.
- `save_traces(path)`: write `self.traces` as JSONL (one JSON object per line).

## `evals.py`

| function | returns |
| --- | --- |
| `load_cases(path)` | list of case dicts. Skip blank lines. Invalid JSON or a missing key (`id`, `question`, `expected_doc_ids`, `must_include`) raises `ValueError` whose message contains `line <n>` (1-based file line). |
| `hit_at_k(retrieved_ids, expected_ids, k)` | `1.0` if any expected id is in the first `k` retrieved ids, else `0.0`. |
| `cites_sources(answer, retrieved_ids)` | `True` if the answer has at least one citation `[something]` and **every** cited id is among `retrieved_ids` (an invented citation fails). |
| `contains_all(answer, phrases)` | `True` if every phrase appears in the answer, case-insensitive (`[]` -> `True`). |
| `judge(judge_llm, question, answer)` | calls `judge_llm(JUDGE_TEMPLATE.format(question=..., answer=...))` once. Find `SCORE: <n>` in the reply (case-insensitive, first match). Map 1..5 to `(n - 1) / 4` (0.0 to 1.0). No score or out of range -> `0.0`. |
| `percentile(values, p)` | nearest-rank percentile: sort, take item number `ceil(p / 100 * len)` (at least 1). Empty list -> `ValueError`. |

### `run_eval(pipeline, cases, judge_llm, k=3) -> dict`

Call `pipeline.answer(case["question"])` once per case, in order, grade it, and return:

```python
{
    "n": 24,
    "metrics": {                 # means over all cases, rounded to 4 decimals
        "hit_at_k": 0.9583,      # hit_at_k(doc_ids, expected_doc_ids, k)
        "citation_rate": 1.0,    # cites_sources(answer, doc_ids) (True = 1.0)
        "contains_rate": 0.75,   # contains_all(answer, must_include)
        "judge_score": 0.8125,   # judge(...)
    },
    "latency_ms": {"p50": 210.0, "p95": 480.0},   # percentiles of trace["latency_ms"]
    "cost_usd": 0.0042,                           # sum of trace["cost_usd"], rounded to 8 decimals
    "results": [                                  # one per case, in order
        {"id": "q01", "hit": 1.0, "cited": True, "contains": True, "judge": 0.75,
         "latency_ms": 212.5, "cost_usd": 0.0002},
        ...
    ],
}
```
An empty `cases` list raises `ValueError`.

### `release_gate(current, baseline, max_drop=0.02, max_latency_increase=0.2, max_cost_increase=0.2)`

`current` and `baseline` are `run_eval` reports (only `metrics`, `latency_ms["p95"]` and
`cost_usd` are used). Returns `{"passed": bool, "failures": [str, ...]}`. Check, in this
order, and add one failure string per problem, each starting with its name and `:`:

1. every metric in `baseline["metrics"]` (in its order): missing in `current` ->
   `"<name>: ..."`; lower than `baseline - max_drop` -> `"<name>: dropped from 0.9 to 0.8"`;
2. `current` p95 latency above `baseline p95 * (1 + max_latency_increase)` -> `"latency_p95: ..."`;
3. `current` cost above `baseline cost * (1 + max_cost_increase)` -> `"cost_usd: ..."`.

Being *exactly* at a limit passes. `passed` is `True` only with no failures.

## Try it

```python
rag = RAGPipeline(my_embed, my_llm, load_docs("docs.jsonl"))
report = run_eval(rag, load_cases("eval_set.jsonl"), my_judge)
rag.save_traces("traces.jsonl")
json.dump(report, open("baseline.json", "w"), indent=2)   # next run: release_gate(new, baseline)
```

Standard library only (`json`, `math`, `re`, `time`).
''',
    "explore": r'''
# Explore

- **Eval-driven development**: read Anthropic's "Demystifying evals for AI agents" and
  Hamel Husain's "Your AI product needs evals". Why start with 20-50 hand-written cases
  from real failures instead of a huge synthetic set? What is *error analysis*?
- **LLM-as-judge pitfalls**: look up position bias, verbosity bias and self-preference.
  How do teams check that a judge agrees with human labels (a small labelled set, and
  agreement rate or Cohen's kappa)?
- **Tracing standards**: look up OpenTelemetry *spans* and the GenAI semantic conventions
  (`gen_ai.usage.input_tokens`...). Your trace dict is one span with two child spans
  (retrieval and generation). Tools like Langfuse, Arize Phoenix and LangSmith store
  exactly this.

## Make it real (optional, ungraded)

```bash
uv pip install openai     # or: pip install openai
export OPENAI_API_KEY=sk-...
```

```python
from openai import OpenAI
client = OpenAI()

def embed(texts):
    resp = client.embeddings.create(model="text-embedding-3-small", input=texts)
    return [d.embedding for d in resp.data]

def llm(prompt):
    resp = client.chat.completions.create(model="gpt-4o-mini",
                                          messages=[{"role": "user", "content": prompt}])
    return {"text": resp.choices[0].message.content,
            "usage": {"input_tokens": resp.usage.prompt_tokens,
                      "output_tokens": resp.usage.completion_tokens}}

judge_llm = lambda prompt: llm(prompt)["text"]
prices = {"gpt-4o-mini": {"input": 0.15, "output": 0.60}}   # check today's prices
rag = RAGPipeline(embed, llm, load_docs("docs.jsonl"), model="gpt-4o-mini", prices=prices)
```

Save the first report as `baseline.json`, then change one thing (`k`, the prompt, the
model) and let `release_gate` decide. Run it in CI (a GitHub Actions job) and you have
a portfolio piece: "measured eval set, traces, latency/cost tracking, release gate".
''',
    "rubric": [
        "The pipeline, the graders, the eval runner and the gate are separate, small, testable pieces; graders are pure functions.",
        "Every request produces a complete trace (per-stage latency from the injected clock, tokens, cost) and traces are exported as JSONL.",
        "The eval set is meaningful: at least 20 cases tied to real documents, with ids, expected sources and key facts; bad lines fail loudly with a line number.",
        "The release gate compares against a baseline with explicit tolerances and explains every failure in a readable message.",
        "No hidden globals or real time/network: embed, llm, judge and clock are injected, and numbers are rounded exactly as specified.",
    ],
    "starter_files": {
        "rag.py": r'''
import json
import time

PRICES = {  # USD per 1M tokens
    "fake-small": {"input": 0.15, "output": 0.60},
    "fake-large": {"input": 3.00, "output": 15.00},
}

PROMPT_TEMPLATE = """Answer the question using only the sources below. Cite the sources you use like [doc-id].
If the sources do not contain the answer, say you don't know.

Sources:
{sources}

Question: {question}"""


def load_docs(path):
    ...


class RAGPipeline:
    def __init__(self, embed, llm, docs, *, clock=time.perf_counter, model="fake-small",
                 k=3, prices=PRICES):
        ...

    def retrieve(self, question, k=None):
        ...

    def build_prompt(self, question, sources):
        ...

    def answer(self, question):
        ...

    def save_traces(self, path):
        ...
''',
        "evals.py": r'''
JUDGE_TEMPLATE = """You are grading an answer to a question.
Question: {question}
Answer: {answer}
Reply with SCORE: <1-5> where 5 means correct, grounded and complete."""


def load_cases(path):
    ...


def hit_at_k(retrieved_ids, expected_ids, k):
    ...


def cites_sources(answer, retrieved_ids):
    ...


def contains_all(answer, phrases):
    ...


def judge(judge_llm, question, answer):
    ...


def percentile(values, p):
    ...


def run_eval(pipeline, cases, judge_llm, k=3):
    ...


def release_gate(current, baseline, max_drop=0.02, max_latency_increase=0.2,
                 max_cost_increase=0.2):
    ...
''',
        "docs.jsonl": r'''
{"id": "refunds", "text": "Refund policy: customers can request a full refund within 30 days of purchase. Refunds are paid back to the original payment method within 5 business days."}
{"id": "shipping", "text": "Shipping: standard shipping takes 3 to 5 business days. Express shipping arrives the next business day and costs 15 dollars."}
{"id": "password", "text": "Password reset: open Settings, choose Security and click Reset password. The reset link in the email expires after 2 hours."}
{"id": "rate-limits", "text": "API rate limits: the free plan allows 60 requests per minute. The pro plan allows 600 requests per minute. Exceeding the limit returns HTTP status 429."}
{"id": "retention", "text": "Data retention: chat logs are kept for 90 days and then deleted. Enterprise customers can set a custom retention period."}
{"id": "sla", "text": "Uptime SLA: the enterprise plan guarantees 99.9 percent monthly uptime. If uptime falls below the SLA, customers receive service credits."}
{"id": "support-hours", "text": "Support hours: the support team answers tickets Monday to Friday, 9am to 6pm Central European Time. Enterprise customers get 24/7 phone support."}
{"id": "pricing", "text": "Pricing: the pro plan costs 20 dollars per user per month. The enterprise plan has custom pricing negotiated with sales."}
{"id": "gpu-quota", "text": "GPU quota: each project gets 4 GPUs by default. To raise the GPU quota, open a quota request form in the console."}
{"id": "regions", "text": "Regions: workloads can run in Frankfurt, Virginia and Singapore. Customer data stays inside the region chosen at signup."}
{"id": "sso", "text": "Single sign-on: SSO with SAML and OIDC is available on the enterprise plan only. Admins configure SSO under Organization settings."}
{"id": "invoices", "text": "Invoices and billing: invoices are issued on the first day of each month in euros. Invoices can be downloaded as PDF from the Billing page."}
{"id": "api-keys", "text": "API keys: create API keys in the console under Developer settings. Keys can be rotated at any time and old keys stop working after 24 hours."}
{"id": "deletion", "text": "Account deletion: to delete an account, the owner submits a deletion request. All data is permanently erased within 14 days."}
''',
        "eval_set.jsonl": r'''
{"id": "q01", "question": "How many days do I have to request a refund?", "expected_doc_ids": ["refunds"], "must_include": ["30 days"]}
{"id": "q02", "question": "When is a refund paid back to my payment method?", "expected_doc_ids": ["refunds"], "must_include": ["5 business days"]}
{"id": "q03", "question": "How long does standard shipping take?", "expected_doc_ids": ["shipping"], "must_include": ["3 to 5"]}
{"id": "q04", "question": "How much does express shipping cost?", "expected_doc_ids": ["shipping"], "must_include": ["15 dollars"]}
{"id": "q05", "question": "How do I reset my password?", "expected_doc_ids": ["password"], "must_include": ["Settings"]}
{"id": "q06", "question": "When does the password reset link expire?", "expected_doc_ids": ["password"], "must_include": ["2 hours"]}
{"id": "q07", "question": "How many requests per minute does the free plan allow?", "expected_doc_ids": ["rate-limits"], "must_include": ["60"]}
{"id": "q08", "question": "Which HTTP status is returned when I exceed the rate limit?", "expected_doc_ids": ["rate-limits"], "must_include": ["429"]}
{"id": "q09", "question": "How long are chat logs kept?", "expected_doc_ids": ["retention"], "must_include": ["90 days"]}
{"id": "q10", "question": "What monthly uptime does the enterprise SLA guarantee?", "expected_doc_ids": ["sla"], "must_include": ["99.9"]}
{"id": "q11", "question": "What happens if uptime falls below the SLA?", "expected_doc_ids": ["sla"], "must_include": ["service credits"]}
{"id": "q12", "question": "What are the support team hours?", "expected_doc_ids": ["support-hours"], "must_include": ["9am to 6pm"]}
{"id": "q13", "question": "Do enterprise customers get phone support?", "expected_doc_ids": ["support-hours"], "must_include": ["24/7"]}
{"id": "q14", "question": "How much does the pro plan cost per user?", "expected_doc_ids": ["pricing"], "must_include": ["20 dollars"]}
{"id": "q15", "question": "How many GPUs does a project get by default?", "expected_doc_ids": ["gpu-quota"], "must_include": ["4 GPUs"]}
{"id": "q16", "question": "How can I raise my GPU quota?", "expected_doc_ids": ["gpu-quota"], "must_include": ["quota request"]}
{"id": "q17", "question": "Which regions can workloads run in?", "expected_doc_ids": ["regions"], "must_include": ["Frankfurt"]}
{"id": "q18", "question": "Is SSO available on the pro plan?", "expected_doc_ids": ["sso"], "must_include": ["enterprise"]}
{"id": "q19", "question": "In which currency are invoices issued?", "expected_doc_ids": ["invoices"], "must_include": ["euros"]}
{"id": "q20", "question": "Where can I download invoices as PDF?", "expected_doc_ids": ["invoices"], "must_include": ["Billing page"]}
{"id": "q21", "question": "Where do I create API keys?", "expected_doc_ids": ["api-keys"], "must_include": ["Developer settings"]}
{"id": "q22", "question": "When do old API keys stop working after rotation?", "expected_doc_ids": ["api-keys"], "must_include": ["24 hours"]}
{"id": "q23", "question": "How long until data is erased after an account deletion request?", "expected_doc_ids": ["deletion"], "must_include": ["14 days"]}
{"id": "q24", "question": "Does the pro plan include SSO and what does it cost?", "expected_doc_ids": ["sso", "pricing"], "must_include": ["20 dollars"]}
''',
    },
    "solution_files": {
        "rag.py": r'''
"""A small RAG pipeline that records a trace for every request."""

import json
import math
import time

PRICES = {  # USD per 1M tokens
    "fake-small": {"input": 0.15, "output": 0.60},
    "fake-large": {"input": 3.00, "output": 15.00},
}

PROMPT_TEMPLATE = """Answer the question using only the sources below. Cite the sources you use like [doc-id].
If the sources do not contain the answer, say you don't know.

Sources:
{sources}

Question: {question}"""


def load_docs(path):
    """Read a JSONL file of {"id", "text"} documents."""
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def cosine(a, b):
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if not norm_a or not norm_b:
        return 0.0
    return sum(x * y for x, y in zip(a, b)) / (norm_a * norm_b)


def _ms(seconds):
    return round(seconds * 1000, 1)


class RAGPipeline:
    def __init__(self, embed, llm, docs, *, clock=time.perf_counter, model="fake-small",
                 k=3, prices=PRICES):
        if model not in prices:
            raise ValueError(f"no price for model {model!r}")
        ids = [d["id"] for d in docs]
        if len(set(ids)) != len(ids):
            raise ValueError("document ids must be unique")
        self.embed, self.llm, self.clock = embed, llm, clock
        self.model, self.k, self.price = model, k, prices[model]
        self.docs = list(docs)
        self.vectors = embed([d["text"] for d in self.docs]) if self.docs else []
        self.traces = []

    def retrieve(self, question, k=None):
        if not self.docs:
            return []
        query = self.embed([question])[0]
        scored = [{"id": d["id"], "text": d["text"], "score": cosine(query, v)}
                  for d, v in zip(self.docs, self.vectors)]
        scored.sort(key=lambda s: -s["score"])  # stable: ties keep document order
        return scored[: self.k if k is None else k]

    def build_prompt(self, question, sources):
        lines = "\n".join(f"[{s['id']}] {s['text']}" for s in sources)
        return PROMPT_TEMPLATE.format(sources=lines, question=question)

    def _cost(self, input_tokens, output_tokens):
        usd = input_tokens * self.price["input"] + output_tokens * self.price["output"]
        return round(usd / 1_000_000, 8)

    def answer(self, question):
        t0 = self.clock()
        sources = self.retrieve(question)
        t1 = self.clock()
        reply = self.llm(self.build_prompt(question, sources))
        t2 = self.clock()
        usage = reply.get("usage", {})
        tokens_in, tokens_out = usage.get("input_tokens", 0), usage.get("output_tokens", 0)
        doc_ids = [s["id"] for s in sources]
        trace = {
            "request_id": len(self.traces) + 1,
            "question": question,
            "model": self.model,
            "retrieved": doc_ids,
            "retrieval_ms": _ms(t1 - t0),
            "generation_ms": _ms(t2 - t1),
            "latency_ms": _ms(t2 - t0),
            "input_tokens": tokens_in,
            "output_tokens": tokens_out,
            "cost_usd": self._cost(tokens_in, tokens_out),
        }
        self.traces.append(trace)
        return {"answer": reply["text"], "doc_ids": doc_ids, "trace": trace}

    def save_traces(self, path):
        with open(path, "w", encoding="utf-8") as f:
            for trace in self.traces:
                f.write(json.dumps(trace) + "\n")
''',
        "evals.py": r'''
"""Eval set loading, graders, an eval runner and a release gate."""

import json
import math
import re

CASE_KEYS = ("id", "question", "expected_doc_ids", "must_include")

JUDGE_TEMPLATE = """You are grading an answer to a question.
Question: {question}
Answer: {answer}
Reply with SCORE: <1-5> where 5 means correct, grounded and complete."""

CITATION = re.compile(r"\[([^\[\]]+)\]")
SCORE = re.compile(r"SCORE:\s*(\d+)", re.IGNORECASE)


def load_cases(path):
    cases = []
    with open(path, encoding="utf-8") as f:
        for number, line in enumerate(f, start=1):
            if not line.strip():
                continue
            try:
                case = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"line {number}: invalid JSON ({exc.msg})") from exc
            missing = [k for k in CASE_KEYS if not isinstance(case, dict) or k not in case]
            if missing:
                raise ValueError(f"line {number}: missing key(s) {', '.join(missing)}")
            cases.append(case)
    return cases


def hit_at_k(retrieved_ids, expected_ids, k):
    return 1.0 if set(retrieved_ids[:k]) & set(expected_ids) else 0.0


def cites_sources(answer, retrieved_ids):
    cited = CITATION.findall(answer)
    return bool(cited) and all(c in retrieved_ids for c in cited)


def contains_all(answer, phrases):
    low = answer.lower()
    return all(p.lower() in low for p in phrases)


def judge(judge_llm, question, answer):
    reply = judge_llm(JUDGE_TEMPLATE.format(question=question, answer=answer))
    match = SCORE.search(reply)
    if not match or not 1 <= int(match.group(1)) <= 5:
        return 0.0
    return (int(match.group(1)) - 1) / 4


def percentile(values, p):
    if not values:
        raise ValueError("percentile of an empty list")
    ordered = sorted(values)
    rank = max(1, math.ceil(p / 100 * len(ordered)))
    return ordered[rank - 1]


def _mean(values):
    return round(sum(values) / len(values), 4)


def run_eval(pipeline, cases, judge_llm, k=3):
    if not cases:
        raise ValueError("no eval cases")
    results = []
    for case in cases:
        out = pipeline.answer(case["question"])
        trace = out["trace"]
        results.append({
            "id": case["id"],
            "hit": hit_at_k(out["doc_ids"], case["expected_doc_ids"], k),
            "cited": cites_sources(out["answer"], out["doc_ids"]),
            "contains": contains_all(out["answer"], case["must_include"]),
            "judge": judge(judge_llm, case["question"], out["answer"]),
            "latency_ms": trace["latency_ms"],
            "cost_usd": trace["cost_usd"],
        })
    latencies = [r["latency_ms"] for r in results]
    return {
        "n": len(results),
        "metrics": {
            "hit_at_k": _mean([r["hit"] for r in results]),
            "citation_rate": _mean([float(r["cited"]) for r in results]),
            "contains_rate": _mean([float(r["contains"]) for r in results]),
            "judge_score": _mean([r["judge"] for r in results]),
        },
        "latency_ms": {"p50": percentile(latencies, 50), "p95": percentile(latencies, 95)},
        "cost_usd": round(sum(r["cost_usd"] for r in results), 8),
        "results": results,
    }


def release_gate(current, baseline, max_drop=0.02, max_latency_increase=0.2,
                 max_cost_increase=0.2):
    failures = []
    for name, base in baseline["metrics"].items():
        now = current["metrics"].get(name)
        if now is None:
            failures.append(f"{name}: missing from the current report")
        elif now < base - max_drop - 1e-9:
            failures.append(f"{name}: dropped from {base} to {now}")
    base_p95, now_p95 = baseline["latency_ms"]["p95"], current["latency_ms"]["p95"]
    if now_p95 > base_p95 * (1 + max_latency_increase):
        failures.append(f"latency_p95: rose from {base_p95} ms to {now_p95} ms")
    if current["cost_usd"] > baseline["cost_usd"] * (1 + max_cost_increase):
        failures.append(f"cost_usd: rose from {baseline['cost_usd']} to {current['cost_usd']}")
    return {"passed": not failures, "failures": failures}
''',
        "docs.jsonl": r'''
{"id": "refunds", "text": "Refund policy: customers can request a full refund within 30 days of purchase. Refunds are paid back to the original payment method within 5 business days."}
{"id": "shipping", "text": "Shipping: standard shipping takes 3 to 5 business days. Express shipping arrives the next business day and costs 15 dollars."}
{"id": "password", "text": "Password reset: open Settings, choose Security and click Reset password. The reset link in the email expires after 2 hours."}
{"id": "rate-limits", "text": "API rate limits: the free plan allows 60 requests per minute. The pro plan allows 600 requests per minute. Exceeding the limit returns HTTP status 429."}
{"id": "retention", "text": "Data retention: chat logs are kept for 90 days and then deleted. Enterprise customers can set a custom retention period."}
{"id": "sla", "text": "Uptime SLA: the enterprise plan guarantees 99.9 percent monthly uptime. If uptime falls below the SLA, customers receive service credits."}
{"id": "support-hours", "text": "Support hours: the support team answers tickets Monday to Friday, 9am to 6pm Central European Time. Enterprise customers get 24/7 phone support."}
{"id": "pricing", "text": "Pricing: the pro plan costs 20 dollars per user per month. The enterprise plan has custom pricing negotiated with sales."}
{"id": "gpu-quota", "text": "GPU quota: each project gets 4 GPUs by default. To raise the GPU quota, open a quota request form in the console."}
{"id": "regions", "text": "Regions: workloads can run in Frankfurt, Virginia and Singapore. Customer data stays inside the region chosen at signup."}
{"id": "sso", "text": "Single sign-on: SSO with SAML and OIDC is available on the enterprise plan only. Admins configure SSO under Organization settings."}
{"id": "invoices", "text": "Invoices and billing: invoices are issued on the first day of each month in euros. Invoices can be downloaded as PDF from the Billing page."}
{"id": "api-keys", "text": "API keys: create API keys in the console under Developer settings. Keys can be rotated at any time and old keys stop working after 24 hours."}
{"id": "deletion", "text": "Account deletion: to delete an account, the owner submits a deletion request. All data is permanently erased within 14 days."}
''',
        "eval_set.jsonl": r'''
{"id": "q01", "question": "How many days do I have to request a refund?", "expected_doc_ids": ["refunds"], "must_include": ["30 days"]}
{"id": "q02", "question": "When is a refund paid back to my payment method?", "expected_doc_ids": ["refunds"], "must_include": ["5 business days"]}
{"id": "q03", "question": "How long does standard shipping take?", "expected_doc_ids": ["shipping"], "must_include": ["3 to 5"]}
{"id": "q04", "question": "How much does express shipping cost?", "expected_doc_ids": ["shipping"], "must_include": ["15 dollars"]}
{"id": "q05", "question": "How do I reset my password?", "expected_doc_ids": ["password"], "must_include": ["Settings"]}
{"id": "q06", "question": "When does the password reset link expire?", "expected_doc_ids": ["password"], "must_include": ["2 hours"]}
{"id": "q07", "question": "How many requests per minute does the free plan allow?", "expected_doc_ids": ["rate-limits"], "must_include": ["60"]}
{"id": "q08", "question": "Which HTTP status is returned when I exceed the rate limit?", "expected_doc_ids": ["rate-limits"], "must_include": ["429"]}
{"id": "q09", "question": "How long are chat logs kept?", "expected_doc_ids": ["retention"], "must_include": ["90 days"]}
{"id": "q10", "question": "What monthly uptime does the enterprise SLA guarantee?", "expected_doc_ids": ["sla"], "must_include": ["99.9"]}
{"id": "q11", "question": "What happens if uptime falls below the SLA?", "expected_doc_ids": ["sla"], "must_include": ["service credits"]}
{"id": "q12", "question": "What are the support team hours?", "expected_doc_ids": ["support-hours"], "must_include": ["9am to 6pm"]}
{"id": "q13", "question": "Do enterprise customers get phone support?", "expected_doc_ids": ["support-hours"], "must_include": ["24/7"]}
{"id": "q14", "question": "How much does the pro plan cost per user?", "expected_doc_ids": ["pricing"], "must_include": ["20 dollars"]}
{"id": "q15", "question": "How many GPUs does a project get by default?", "expected_doc_ids": ["gpu-quota"], "must_include": ["4 GPUs"]}
{"id": "q16", "question": "How can I raise my GPU quota?", "expected_doc_ids": ["gpu-quota"], "must_include": ["quota request"]}
{"id": "q17", "question": "Which regions can workloads run in?", "expected_doc_ids": ["regions"], "must_include": ["Frankfurt"]}
{"id": "q18", "question": "Is SSO available on the pro plan?", "expected_doc_ids": ["sso"], "must_include": ["enterprise"]}
{"id": "q19", "question": "In which currency are invoices issued?", "expected_doc_ids": ["invoices"], "must_include": ["euros"]}
{"id": "q20", "question": "Where can I download invoices as PDF?", "expected_doc_ids": ["invoices"], "must_include": ["Billing page"]}
{"id": "q21", "question": "Where do I create API keys?", "expected_doc_ids": ["api-keys"], "must_include": ["Developer settings"]}
{"id": "q22", "question": "When do old API keys stop working after rotation?", "expected_doc_ids": ["api-keys"], "must_include": ["24 hours"]}
{"id": "q23", "question": "How long until data is erased after an account deletion request?", "expected_doc_ids": ["deletion"], "must_include": ["14 days"]}
{"id": "q24", "question": "Does the pro plan include SSO and what does it cost?", "expected_doc_ids": ["sso", "pricing"], "must_include": ["20 dollars"]}
''',
    },
    "tests": r'''
import json
import re
import zlib
from rag import PRICES, RAGPipeline, load_docs
from evals import (cites_sources, contains_all, hit_at_k, judge, load_cases, percentile,
                   release_gate, run_eval)

STOP = {"the", "a", "an", "is", "are", "do", "does", "i", "my", "how", "what", "when", "which",
        "to", "of", "in", "and", "can", "be", "for", "after", "on", "per", "it", "get", "where",
        "until", "much", "many", "long"}


def bow_embed(texts):
    """Fake embedding: hashed bag of words (64 dims)."""
    out = []
    for text in texts:
        vec = [0.0] * 64
        for word in re.findall(r"[a-z0-9]+", text.lower()):
            if word not in STOP:
                vec[zlib.crc32(word.encode()) % 64] += 1
        out.append(vec)
    return out


class TableEmbed:
    """Fake embedding from a lookup table; records every call."""

    def __init__(self, table):
        self.table = table
        self.calls = []

    def __call__(self, texts):
        self.calls.append(list(texts))
        return [self.table.get(t, [0.0, 0.0]) for t in texts]


class FakeLLM:
    def __init__(self, text="ok [a]", usage=(100, 20)):
        self.text, self.usage = text, usage
        self.prompts = []

    def __call__(self, prompt):
        self.prompts.append(prompt)
        return {"text": self.text, "usage": {"input_tokens": self.usage[0], "output_tokens": self.usage[1]}}


def ticking(step=0.01):
    t = [0.0]

    def clock():
        t[0] += step
        return t[0]
    return clock


DOCS = [{"id": "a", "text": "alpha"}, {"id": "b", "text": "beta"}, {"id": "c", "text": "gamma"}]
TABLE = {"alpha": [1.0, 0.0], "beta": [0.0, 1.0], "gamma": [1.0, 1.0],
         "q-alpha": [1.0, 0.1], "q-beta": [0.0, 2.0]}


def test_eval_set_has_at_least_20_valid_cases():
    docs = load_docs("docs.jsonl")
    doc_ids = {d["id"] for d in docs}
    cases = load_cases("eval_set.jsonl")
    assert len(cases) >= 20, f"eval_set.jsonl has {len(cases)} cases, need at least 20"
    ids = [c["id"] for c in cases]
    assert len(set(ids)) == len(ids), "case ids must be unique"
    for c in cases:
        assert c["question"].strip(), f"{c['id']}: empty question"
        assert c["expected_doc_ids"] and set(c["expected_doc_ids"]) <= doc_ids, \
            f"{c['id']}: expected_doc_ids must name documents in docs.jsonl"
        assert isinstance(c["must_include"], list) and c["must_include"], f"{c['id']}: must_include"


def test_load_cases_skips_blank_lines_and_reports_bad_lines():
    good = '{"id": "x", "question": "q?", "expected_doc_ids": ["a"], "must_include": ["y"]}'
    with open("ok.jsonl", "w") as f:
        f.write(good + "\n\n" + good.replace('"x"', '"z"') + "\n")
    assert [c["id"] for c in load_cases("ok.jsonl")] == ["x", "z"]
    for name, bad in [("broken.jsonl", "{not json"), ("missing.jsonl", '{"id": "m", "question": "q?"}')]:
        with open(name, "w") as f:
            f.write(good + "\n\n" + bad + "\n")
        try:
            load_cases(name)
        except ValueError as exc:
            assert "line 3" in str(exc), f"error should name the line number: {exc}"
        else:
            raise AssertionError(f"{name}: expected ValueError")


def test_pipeline_embeds_docs_once_and_validates_config():
    embed = TableEmbed(TABLE)
    RAGPipeline(embed, FakeLLM(), DOCS)
    assert embed.calls == [["alpha", "beta", "gamma"]], f"embed calls: {embed.calls!r}"
    for kwargs, docs in [({"model": "gpt-unknown"}, DOCS),
                         ({}, DOCS + [{"id": "a", "text": "again"}])]:
        try:
            RAGPipeline(TableEmbed(TABLE), FakeLLM(), docs, **kwargs)
        except ValueError:
            continue
        raise AssertionError(f"expected ValueError for {kwargs or 'duplicate ids'}")
    assert PRICES["fake-small"] == {"input": 0.15, "output": 0.60}


def test_retrieve_ranks_by_cosine_similarity():
    embed = TableEmbed(TABLE)
    rag = RAGPipeline(embed, FakeLLM(), DOCS, k=2)
    got = rag.retrieve("q-alpha")
    assert [r["id"] for r in got] == ["a", "c"], f"got {got!r}"
    assert set(got[0]) == {"id", "text", "score"} and got[0]["text"] == "alpha"
    assert abs(got[0]["score"] - 0.995037) < 1e-5, f"score {got[0]['score']!r}"
    assert [r["id"] for r in rag.retrieve("q-beta", k=3)] == ["b", "c", "a"]
    assert [r["id"] for r in rag.retrieve("unknown", k=3)] == ["a", "b", "c"], "zero vector: ties keep order"
    assert embed.calls[-1] == ["unknown"], "embed the question with one call"


def test_answer_sends_the_grounded_prompt():
    llm = FakeLLM(text="Alpha it is [a].")
    rag = RAGPipeline(TableEmbed(TABLE), llm, DOCS, k=2, clock=ticking())
    out = rag.answer("q-alpha")
    expected = (
        "Answer the question using only the sources below. Cite the sources you use like [doc-id].\n"
        "If the sources do not contain the answer, say you don't know.\n\n"
        "Sources:\n[a] alpha\n[c] gamma\n\n"
        "Question: q-alpha")
    assert llm.prompts == [expected], f"prompt was:\n{llm.prompts[-1]}"
    assert out["answer"] == "Alpha it is [a]." and out["doc_ids"] == ["a", "c"], f"got {out!r}"


def test_trace_records_latency_tokens_and_cost():
    ticks = iter([10.0, 10.0125, 10.5125, 20.0, 20.001, 20.101])
    rag = RAGPipeline(TableEmbed(TABLE), FakeLLM(usage=(2000, 500)), DOCS,
                      clock=lambda: next(ticks), model="fake-large")
    first = rag.answer("q-alpha")["trace"]
    expected = {"request_id": 1, "question": "q-alpha", "model": "fake-large",
                "retrieved": ["a", "c", "b"], "retrieval_ms": 12.5, "generation_ms": 500.0,
                "latency_ms": 512.5, "input_tokens": 2000, "output_tokens": 500, "cost_usd": 0.0135}
    assert first == expected, f"got {first!r}"
    second = rag.answer("q-beta")["trace"]
    assert second["request_id"] == 2 and second["latency_ms"] == 101.0, f"got {second!r}"
    assert rag.traces == [first, second]


def test_traces_are_saved_as_jsonl():
    rag = RAGPipeline(TableEmbed(TABLE), FakeLLM(), DOCS, clock=ticking())
    rag.answer("q-alpha")
    rag.answer("q-beta")
    rag.save_traces("traces.jsonl")
    with open("traces.jsonl") as f:
        lines = [json.loads(line) for line in f if line.strip()]
    assert lines == rag.traces, f"got {lines!r}"


def test_hit_at_k():
    assert hit_at_k(["a", "b", "c"], ["c"], 3) == 1.0
    assert hit_at_k(["a", "b", "c"], ["c"], 2) == 0.0
    assert hit_at_k(["a", "b"], ["x", "b"], 5) == 1.0
    assert hit_at_k([], ["a"], 3) == 0.0


def test_citation_and_contains_graders():
    assert cites_sources("Refunds take 30 days [refunds].", ["refunds", "sla"]) is True
    assert cites_sources("See [refunds] and [sla].", ["refunds", "sla"]) is True
    assert cites_sources("Refunds take 30 days.", ["refunds"]) is False, "no citation"
    assert cites_sources("Per [policy-7] it is 30 days.", ["refunds"]) is False, "invented citation"
    assert cites_sources("[refunds] and [made-up]", ["refunds"]) is False
    assert contains_all("Refunds within 30 DAYS.", ["30 days", "refunds"]) is True
    assert contains_all("Refunds within 30 days.", ["30 days", "euros"]) is False
    assert contains_all("anything", []) is True


def test_llm_judge_parses_and_normalises_the_score():
    prompts = []

    def fake_judge(reply):
        def call(prompt):
            prompts.append(prompt)
            return reply
        return call

    assert judge(fake_judge("SCORE: 5"), "Q?", "A.") == 1.0
    assert judge(fake_judge("Reasoning... score: 3"), "Q?", "A.") == 0.5
    assert judge(fake_judge("SCORE: 1"), "Q?", "A.") == 0.0
    assert judge(fake_judge("SCORE: 9"), "Q?", "A.") == 0.0, "out of range scores count as 0.0"
    assert judge(fake_judge("looks fine to me"), "Q?", "A.") == 0.0
    judge(fake_judge("SCORE: 4"), "How long?", "30 days.")
    assert "Question: How long?" in prompts[-1] and "Answer: 30 days." in prompts[-1], prompts[-1]
    assert "SCORE: <1-5>" in prompts[-1]


def test_percentile_nearest_rank():
    assert percentile([40, 10, 30, 20], 50) == 20
    assert percentile([40, 10, 30, 20], 95) == 40
    assert percentile([7.5], 95) == 7.5
    assert percentile(list(range(1, 101)), 95) == 95
    try:
        percentile([], 50)
    except ValueError:
        pass
    else:
        raise AssertionError("empty list should raise ValueError")


class StubPipeline:
    def __init__(self, outputs):
        self.outputs = outputs
        self.questions = []

    def answer(self, question):
        self.questions.append(question)
        return self.outputs[question]


def out(answer, doc_ids, latency, cost):
    return {"answer": answer, "doc_ids": doc_ids,
            "trace": {"latency_ms": latency, "cost_usd": cost}}


def test_run_eval_aggregates_grader_results():
    cases = [
        {"id": "1", "question": "q1", "expected_doc_ids": ["a"], "must_include": ["30 days"]},
        {"id": "2", "question": "q2", "expected_doc_ids": ["z"], "must_include": ["euros"]},
        {"id": "3", "question": "q3", "expected_doc_ids": ["c"], "must_include": ["429"]},
        {"id": "4", "question": "q4", "expected_doc_ids": ["b"], "must_include": ["SSO"]},
    ]
    pipe = StubPipeline({
        "q1": out("It is 30 days [a].", ["a", "b", "c"], 100.0, 0.001),
        "q2": out("Paid in euros [x].", ["a", "b", "c"], 300.0, 0.002),
        "q3": out("Returns 429.", ["b", "c", "a"], 200.0, 0.001),
        "q4": out("I don't know [b].", ["a", "c", "d", "b"], 400.0, 0.0005),
    })
    scores = {"q1": "SCORE: 5", "q2": "SCORE: 3", "q3": "SCORE: 4", "q4": "SCORE: 1"}

    def judge_llm(prompt):
        return next(v for q, v in scores.items() if f"Question: {q}\n" in prompt)

    rep = run_eval(pipe, cases, judge_llm, k=3)
    assert pipe.questions == ["q1", "q2", "q3", "q4"]
    assert rep["n"] == 4
    assert rep["metrics"] == {"hit_at_k": 0.5, "citation_rate": 0.5, "contains_rate": 0.75,
                              "judge_score": 0.5625}, f"metrics: {rep['metrics']!r}"
    assert rep["latency_ms"] == {"p50": 200.0, "p95": 400.0}, f"latency: {rep['latency_ms']!r}"
    assert abs(rep["cost_usd"] - 0.0045) < 1e-12, f"cost: {rep['cost_usd']!r}"
    first = rep["results"][0]
    assert first == {"id": "1", "hit": 1.0, "cited": True, "contains": True, "judge": 1.0,
                     "latency_ms": 100.0, "cost_usd": 0.001}, f"results[0]: {first!r}"
    try:
        run_eval(pipe, [], judge_llm)
    except ValueError:
        pass
    else:
        raise AssertionError("an empty eval set should raise ValueError")


def report(hit=0.9, cite=0.95, judge_score=0.8, p95=500.0, cost=0.01):
    return {"metrics": {"hit_at_k": hit, "citation_rate": cite, "judge_score": judge_score},
            "latency_ms": {"p50": p95 / 2, "p95": p95}, "cost_usd": cost}


def test_release_gate_passes_within_tolerance():
    base = report()
    assert release_gate(report(), base) == {"passed": True, "failures": []}
    small_changes = report(hit=0.88, cite=0.99, p95=600.0, cost=0.012)
    got = release_gate(small_changes, base)
    assert got == {"passed": True, "failures": []}, f"small changes within tolerance: {got!r}"


def test_release_gate_reports_every_regression():
    base = report()
    got = release_gate(report(hit=0.8, judge_score=0.7, p95=700.0, cost=0.02), base)
    assert got["passed"] is False
    names = [f.split(":")[0] for f in got["failures"]]
    assert names == ["hit_at_k", "judge_score", "latency_p95", "cost_usd"], f"failures: {got['failures']!r}"
    missing = {"metrics": {"hit_at_k": 0.9}, "latency_ms": {"p95": 100.0}, "cost_usd": 0.001}
    got = release_gate(missing, base)
    assert [f.split(":")[0] for f in got["failures"]] == ["citation_rate", "judge_score"], got
    strict = release_gate(report(hit=0.88), base, max_drop=0.0)
    assert strict["passed"] is False, "max_drop=0.0 should fail on any drop"


def test_end_to_end_on_the_shipped_eval_set():
    docs = load_docs("docs.jsonl")
    cases = load_cases("eval_set.jsonl")

    def llm(prompt):
        first = re.search(r"^\[([^\]]+)\] (.*)$", prompt, re.MULTILINE)
        return {"text": f"{first.group(2)} [{first.group(1)}]",
                "usage": {"input_tokens": len(prompt.split()), "output_tokens": 30}}

    rag = RAGPipeline(bow_embed, llm, docs, clock=ticking(0.05))
    rep = run_eval(rag, cases, lambda prompt: "SCORE: 4")
    assert rep["n"] == len(cases) and len(rag.traces) == len(cases)
    assert rep["metrics"]["hit_at_k"] >= 0.8, f"hit@3 = {rep['metrics']['hit_at_k']}"
    assert rep["metrics"]["citation_rate"] == 1.0 and rep["metrics"]["judge_score"] == 0.75
    assert rep["latency_ms"]["p95"] == 100.0, f"latency: {rep['latency_ms']!r}"
    assert rep["cost_usd"] > 0
    assert release_gate(rep, rep)["passed"] is True
''',
}
