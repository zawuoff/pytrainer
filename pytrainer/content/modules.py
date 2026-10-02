"""The course: 8 modules, ordered by what AI-engineering job postings ask for.

Source for the "why" lines: the learner's report "AI engineering skills in current job
postings" (23 Sep 2026) - ~707 US AI engineer descriptions (Sep 2026) plus a 1,222-posting
cross-check (Aug 2026).
"""

MODULES = [
    {
        "id": "foundations",
        "title": "Python Foundations",
        "summary": "The core language: values, decisions, collections, loops, functions and errors.",
        "why": "Python appears in 68% of AI engineer postings. Everything else is built on this module.",
        "resources": [
            {"title": "The official Python tutorial", "url": "https://docs.python.org/3/tutorial/"},
        ],
        "show_it": "Solve every chapter checkpoint without hints.",
    },
    {
        "id": "working-python",
        "title": "Everyday Python",
        "summary": "Text, comprehensions, JSON, files, environment variables, scripts and sorting.",
        "why": "The daily tools of AI apps: nearly every LLM request or response passes through JSON, "
               "files and environment config.",
        "resources": [
            {"title": "Python standard library: json", "url": "https://docs.python.org/3/library/json.html"},
            {"title": "Python standard library: pathlib", "url": "https://docs.python.org/3/library/pathlib.html"},
        ],
        "show_it": "A command-line tool that reads a folder of documents and writes a JSON report.",
    },
    {
        "id": "production-python",
        "title": "Production Python",
        "summary": "Classes, typed data, testing, generators and async: code a team can trust.",
        "why": "Postings ask for typed, tested code that handles errors and async work. This separates "
               "'can code' from 'can ship'.",
        "resources": [
            {"title": "Python typing docs", "url": "https://docs.python.org/3/library/typing.html"},
            {"title": "pytest: get started", "url": "https://docs.pytest.org/en/stable/getting-started.html"},
            {"title": "asyncio docs", "url": "https://docs.python.org/3/library/asyncio.html"},
        ],
        "show_it": "A small library with type hints, tests and a clear README.",
    },
    {
        "id": "apis-data",
        "title": "APIs, Data & Integrations",
        "summary": "HTTP, working with API responses, regular expressions and SQL.",
        "why": "Every role in the report lists APIs, HTTP, auth and SQL basics. Forward-deployed "
               "engineers live in integrations.",
        "resources": [
            {"title": "MDN: An overview of HTTP", "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview"},
            {"title": "Python sqlite3 docs", "url": "https://docs.python.org/3/library/sqlite3.html"},
            {"title": "PostgreSQL tutorial", "url": "https://www.postgresql.org/docs/current/tutorial.html"},
        ],
        "show_it": "Connect an API to a database, and handle pagination, retries and failures.",
    },
    {
        "id": "llm-apps",
        "title": "Building with LLM APIs",
        "summary": "Chat messages, prompts in code, structured output and tool calling.",
        "why": "LLMs appear in 53-59% of AI engineer postings, the second most requested skill after Python.",
        "resources": [
            {"title": "Anthropic: effective context engineering",
             "url": "https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents"},
            {"title": "Anthropic docs: tool use", "url": "https://docs.anthropic.com/en/docs/build-with-claude/tool-use"},
            {"title": "OpenAI docs: structured outputs", "url": "https://platform.openai.com/docs/guides/structured-outputs"},
        ],
        "show_it": "A task-specific feature with versioned prompts, input validation and fallback behaviour.",
    },
    {
        "id": "rag",
        "title": "RAG, Embeddings & Search",
        "summary": "Vectors, chunking, retrieval and grounded answers with citations.",
        "why": "RAG appears in 35-43% of AI engineer postings. It's the most common production LLM pattern.",
        "resources": [
            {"title": "OpenAI: retrieval guide", "url": "https://platform.openai.com/docs/guides/retrieval"},
            {"title": "Anthropic: contextual retrieval", "url": "https://www.anthropic.com/news/contextual-retrieval"},
        ],
        "show_it": "A document Q&A app with source citations and a retrieval test set.",
    },
    {
        "id": "evals",
        "title": "Evaluation & Observability",
        "summary": "Measuring quality with eval sets and graders; logs, traces, latency and cost.",
        "why": "LLM evaluation is named in 21% of postings and CI/CD in 39%. 'Measurable quality' is "
               "what the report says to prioritise.",
        "resources": [
            {"title": "Anthropic: demystifying evals for AI agents",
             "url": "https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents"},
            {"title": "OpenTelemetry Python: getting started",
             "url": "https://opentelemetry.io/docs/languages/python/getting-started/"},
        ],
        "show_it": "A 30-case eval set with baseline scores, trace samples and a release gate.",
    },
    {
        "id": "agents",
        "title": "Agents, Tools & Safety",
        "summary": "Agent loops, bounded tool use, and defending against prompt injection.",
        "why": "Agentic workflows appear in 42% of postings, and every role lists security.",
        "resources": [
            {"title": "Anthropic: building effective agents", "url": "https://www.anthropic.com/engineering/building-effective-agents"},
            {"title": "OWASP Top 10 for LLM applications", "url": "https://genai.owasp.org/llm-top-10/"},
            {"title": "Hugging Face agents course", "url": "https://huggingface.co/learn/agents-course"},
        ],
        "show_it": "A workflow that uses two tools, recovers from errors and records each action.",
    },
]

# Where each project sits in the course (projects are listed under their module).
PROJECT_MODULES = {
    "prompt-kit": "llm-apps", "chat-memory": "llm-apps", "structured-output": "llm-apps",
    "resilient-client": "llm-apps", "cli-chat": "working-python", "async-batch": "production-python",
    "chunker": "rag", "search-index": "rag", "mini-rag": "rag", "doc-qa": "rag",
    "eval-harness": "evals", "tool-agent": "agents",
}
