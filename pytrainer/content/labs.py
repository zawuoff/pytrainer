"""Terminal labs. Done in your real terminal; the app verifies the result on disk.

Check types (see pytrainer/labs.py): command, path, glob, absent, contains, run.
"""

LAB = "~/pytrainer-lab"

LABS = [
    {
        "id": "lab-run-scripts",
        "title": "Run a script like a pro",
        "order": 1,
        "topics": ["scripts"],
        "brief": r'''
            Everything in AI engineering starts with running Python files from a terminal.

            **Mission**

            1. Create the folder `~/pytrainer-lab/01-hello/`.
            2. Inside, create `greet.py`. It takes a name as a **command-line argument** and prints
               `Hello, <name>!`. With no argument it prints `Hello, world!`.
            3. Make it also work as an executable: add a shebang line and `chmod +x greet.py`,
               so `./greet.py Ada` works without typing `python3`.
            4. Importing `greet` from another file must **not** print anything.

            Run it yourself first, then press **Check**.
        ''',
        "checks": [
            {"type": "path", "label": "greet.py exists", "path": f"{LAB}/01-hello/greet.py"},
            {"type": "run", "label": "python3 greet.py Ada prints Hello, Ada!",
             "cmd": ["python3", "greet.py", "Ada"], "cwd": f"{LAB}/01-hello", "stdout": r"^Hello, Ada!\s*$"},
            {"type": "run", "label": "no argument prints Hello, world!",
             "cmd": ["python3", "greet.py"], "cwd": f"{LAB}/01-hello", "stdout": r"^Hello, world!\s*$"},
            {"type": "run", "label": "./greet.py runs directly (shebang + chmod +x)",
             "cmd": [f"{LAB}/01-hello/greet.py", "Linus"], "cwd": f"{LAB}/01-hello",
             "stdout": r"^Hello, Linus!\s*$"},
            {"type": "run", "label": "importing greet prints nothing (__main__ guard)",
             "cmd": ["python3", "-c", "import greet"], "cwd": f"{LAB}/01-hello", "stdout": r"\A\Z"},
        ],
    },
    {
        "id": "lab-venv-pip",
        "title": "Virtual environments + pip",
        "order": 2,
        "topics": ["scripts"],
        "brief": r'''
            On Arch/Omarchy the system Python has **no pip** and is "externally managed" - you are
            not supposed to install packages into it. That is exactly why virtual environments exist.

            **Mission** (folder `~/pytrainer-lab/02-venv/`)

            1. Create a virtual environment named `.venv` in that folder using the built-in `venv` module.
            2. Using **the venv's pip**, install the packages `rich` and `python-dotenv`.
            3. Freeze the exact installed versions into `requirements.txt`.
            4. Write `show.py` that uses `rich` to print (any styling) the text `venv works`.
            5. Delete the venv folder, recreate it, and reinstall **from requirements.txt**
               (this is how teammates reproduce your environment). Then run `show.py` with the venv's Python.

            Also answer for yourself: what does `source .venv/bin/activate` actually change?
            (Hint for exploration: look at `$PATH` and `which python` before and after.)
        ''',
        "checks": [
            {"type": "path", "label": ".venv exists", "path": f"{LAB}/02-venv/.venv/bin/python"},
            {"type": "contains", "label": "requirements.txt pins rich with ==",
             "path": f"{LAB}/02-venv/requirements.txt", "pattern": r"(?im)^rich==\d",
             "hint": "requirements.txt should come from `pip freeze` (pinned with ==)"},
            {"type": "contains", "label": "requirements.txt pins python-dotenv",
             "path": f"{LAB}/02-venv/requirements.txt", "pattern": r"(?im)^python-dotenv==\d"},
            {"type": "run", "label": "rich importable inside the venv",
             "cmd": [f"{LAB}/02-venv/.venv/bin/python", "-c", "import rich, dotenv"], "cwd": f"{LAB}/02-venv"},
            {"type": "run", "label": "rich is NOT installed in system Python (you kept it clean)",
             "cmd": ["/usr/bin/python3", "-c", "import rich"], "cwd": f"{LAB}/02-venv", "returncode": 1},
            {"type": "run", "label": "show.py prints 'venv works' using rich",
             "cmd": [f"{LAB}/02-venv/.venv/bin/python", "show.py"], "cwd": f"{LAB}/02-venv",
             "stdout": r"venv works"},
            {"type": "contains", "label": "show.py actually uses rich",
             "path": f"{LAB}/02-venv/show.py", "pattern": r"(?m)^\s*(from rich|import rich)"},
        ],
    },
    {
        "id": "lab-install-uv",
        "title": "Install uv",
        "order": 3,
        "topics": [],
        "brief": r'''
            `uv` is the modern, very fast Python package & project manager (it replaces pip,
            venv, pip-tools, pipx and pyenv for most workflows). Most new AI projects and
            tutorials use it.

            **Mission**

            1. Install `uv` using its official installer or your package manager
               (on Omarchy/Arch: `sudo pacman -S uv` works, or the official install script from
               docs.astral.sh/uv).
            2. Make sure `uv --version` works in a **new** terminal.
            3. Use uv to install a Python version of your choice (`uv python install ...`) and
               list what uv can see with `uv python list`.
        ''',
        "checks": [
            {"type": "command", "label": "uv is on PATH", "cmd": "uv"},
            {"type": "run", "label": "uv --version works", "cmd": ["uv", "--version"], "stdout": r"uv \d"},
            {"type": "run", "label": "uv python list works", "cmd": ["uv", "python", "list"], "stdout": r"cpython"},
        ],
    },
    {
        "id": "lab-uv-project",
        "title": "A real uv project",
        "order": 4,
        "topics": ["scripts", "json"],
        "brief": r'''
            **Mission**: create a uv-managed project at `~/pytrainer-lab/04-uv-project/`.

            1. Initialise it with uv (it should get a `pyproject.toml`).
            2. Add `httpx` as a dependency **with uv** (not pip). Notice the `uv.lock` file appear.
            3. Add `pytest` as a **development** dependency (dependency group `dev`).
            4. Write `main.py` that uses `httpx` to GET `https://httpbin.org/json` (or any JSON API),
               parses it and prints the number of top-level keys like `keys: 1`.
               Handle network errors gracefully (print `offline` and exit with code 0).
            5. Run it with `uv run main.py`.
            6. Write `test_main.py` with at least one pytest test, and run `uv run pytest`.

            Explore: what is the difference between `pyproject.toml` and `uv.lock`? Which one do you commit?
        ''',
        "checks": [
            {"type": "path", "label": "pyproject.toml exists", "path": f"{LAB}/04-uv-project/pyproject.toml"},
            {"type": "contains", "label": "httpx is a dependency", "path": f"{LAB}/04-uv-project/pyproject.toml",
             "pattern": r"(?s)dependencies\s*=\s*\[[^\]]*httpx"},
            {"type": "contains", "label": "pytest is in a dev dependency group",
             "path": f"{LAB}/04-uv-project/pyproject.toml", "pattern": r"(?s)\[dependency-groups\].*dev\s*=\s*\[[^\]]*pytest"},
            {"type": "path", "label": "uv.lock exists", "path": f"{LAB}/04-uv-project/uv.lock"},
            {"type": "run", "label": "uv run main.py prints keys: N (or offline)",
             "cmd": ["uv", "run", "main.py"], "cwd": f"{LAB}/04-uv-project", "stdout": r"(keys: \d+|offline)"},
            {"type": "run", "label": "uv run pytest passes", "cmd": ["uv", "run", "pytest", "-q"],
             "cwd": f"{LAB}/04-uv-project", "stdout": r"passed"},
        ],
    },
    {
        "id": "lab-env-dotenv",
        "title": "Secrets, env vars and .env",
        "order": 5,
        "topics": ["env"],
        "brief": r'''
            Every AI app needs API keys. They must **never** be hard-coded or committed.

            **Mission** in `~/pytrainer-lab/05-env/` (make it a uv project):

            1. Add `python-dotenv` with uv.
            2. Create `.env` containing `APP_NAME=pytrainer-lab` and `OPENAI_API_KEY=sk-test-1234567890abcd`.
            3. Create `.gitignore` that ignores `.env` (and `.venv`).
            4. Create `.env.example` listing the same variable **names** with empty values - this one is safe to commit.
            5. Write `config.py` that loads `.env` (real environment variables must **win** over `.env` values)
               and prints two lines:
               ```
               app=<APP_NAME>
               key=sk-...abcd
               ```
               The key is masked: first 3 chars, `...`, last 4 chars.
               If `OPENAI_API_KEY` is missing entirely, print `error: OPENAI_API_KEY is not set` to **stderr** and exit with code 1.
        ''',
        "checks": [
            {"type": "contains", "label": ".gitignore ignores .env", "path": f"{LAB}/05-env/.gitignore",
             "pattern": r"(?m)^/?\.env\s*$"},
            {"type": "contains", "label": ".env.example has names but no secret",
             "path": f"{LAB}/05-env/.env.example", "pattern": r"(?m)^OPENAI_API_KEY=\s*$"},
            {"type": "contains", "label": "python-dotenv added with uv", "path": f"{LAB}/05-env/pyproject.toml",
             "pattern": r"python-dotenv"},
            {"type": "run", "label": "reads values from .env", "cmd": ["uv", "run", "config.py"],
             "cwd": f"{LAB}/05-env", "stdout": r"(?s)app=pytrainer-lab\s+key=sk-\.\.\.abcd"},
            {"type": "run", "label": "real env vars override .env", "cmd": ["uv", "run", "config.py"],
             "cwd": f"{LAB}/05-env", "env": {"APP_NAME": "from-shell"}, "stdout": r"app=from-shell"},
            {"type": "contains", "label": "no API key hard-coded in config.py", "path": f"{LAB}/05-env/config.py",
             "pattern": r"sk-test", "negate": True, "hint": "the key must come from the environment, not the code"},
        ],
    },
    {
        "id": "lab-inline-script",
        "title": "Single-file scripts with inline dependencies",
        "order": 6,
        "topics": ["scripts"],
        "brief": r'''
            Not everything needs a whole project. PEP 723 lets a single script declare its own
            dependencies, and `uv run` builds a throwaway environment for it automatically.
            Perfect for quick AI experiments.

            **Mission** in `~/pytrainer-lab/06-inline/`:

            1. Create `tokens.py` with an inline script metadata block declaring the dependency
               `tiktoken` (look up the exact `# /// script` format - `uv add --script` can write it for you).
            2. The script reads text from **stdin** and prints `tokens: N` - the number of tokens using
               tiktoken's `o200k_base` encoding.
            3. `echo "hello world" | uv run tokens.py` should work with no venv or project.

            Explore: why do LLM APIs bill by tokens, and roughly how many characters is a token in English?
        ''',
        "checks": [
            {"type": "contains", "label": "has a PEP 723 script block", "path": f"{LAB}/06-inline/tokens.py",
             "pattern": r"(?s)# /// script.*dependencies.*tiktoken.*# ///"},
            {"type": "absent", "label": "no pyproject.toml needed", "path": f"{LAB}/06-inline/pyproject.toml"},
            {"type": "run", "label": "uv run tokens.py counts tokens from stdin",
             "cmd": ["bash", "-c", "echo 'hello world' | uv run tokens.py"], "cwd": f"{LAB}/06-inline",
             "stdout": r"tokens: 2\b", "timeout": 240},
        ],
    },
    {
        "id": "lab-first-llm-call",
        "title": "Your first real LLM call",
        "order": 7,
        "topics": ["env", "api-data"],
        "brief": r'''
            Time to talk to a real model from your own code.

            **Mission** in `~/pytrainer-lab/07-llm/` (uv project):

            1. Add the official SDK for a provider you have an **API key** for: `openai` or `anthropic`.
               (API keys are separate from ChatGPT/Claude subscriptions - you get them from the
               provider's developer console. A few dollars of credit lasts a long time for learning.)
            2. Put the key in `.env` (git-ignored!) and load it.
            3. Write `ask.py` that takes a question as a CLI argument, calls the model, prints the answer,
               then prints a final line `usage: <input_tokens> in / <output_tokens> out` from the response's
               usage data.
            4. Support `--model` to choose the model and `--system` for a system prompt (argparse).
            5. Handle the failure cases: missing **or empty** key (clear error on stderr, exit 1), and API errors (print the
               error type, exit 2) - never a raw traceback.

            No API key? Do steps 1-4 anyway, and the checks below will still verify structure; the last
            check needs a key.
        ''',
        "checks": [
            {"type": "contains", "label": "openai or anthropic SDK added with uv", "path": f"{LAB}/07-llm/pyproject.toml",
             "pattern": r"\"(openai|anthropic)"},
            {"type": "contains", "label": ".env is git-ignored", "path": f"{LAB}/07-llm/.gitignore", "pattern": r"(?m)^/?\.env\s*$"},
            {"type": "contains", "label": "ask.py uses argparse with --model", "path": f"{LAB}/07-llm/ask.py",
             "pattern": r"(?s)argparse.*--model"},
            {"type": "run", "label": "empty/missing key -> exit code 1, no traceback",
             "cmd": ["uv", "run", "ask.py", "hi"], "cwd": f"{LAB}/07-llm", "returncode": 1,
             "env": {"OPENAI_API_KEY": "", "ANTHROPIC_API_KEY": ""}},
            {"type": "run", "label": "real call prints an answer and usage (needs a key in .env)",
             "cmd": ["uv", "run", "ask.py", "Reply with the single word: pong"], "cwd": f"{LAB}/07-llm",
             "stdout": r"(?is)pong.*usage: \d+ in / \d+ out", "timeout": 120},
        ],
    },
    {
        "id": "lab-fastapi-service",
        "title": "Ship an API with FastAPI",
        "order": 8,
        "topics": ["http", "testing"],
        "brief": r"""
            The report's first "show it" for Python roles: *a small API with tests, logging, a
            clear README and a reproducible local setup.* FastAPI is the standard way to put an
            AI feature behind an HTTP endpoint in Python.

            **Mission** in `~/pytrainer-lab/08-api/` (a uv project):

            1. Add `fastapi` and `uvicorn` as dependencies, and `pytest` + `httpx` to the `dev` group.
            2. In `main.py`, create `app = FastAPI()` with:
               - `GET /health` → `{"status": "ok"}`
               - `POST /summarize` taking JSON `{"text": "..."}` → `{"summary": ..., "words": N}` where
                 the summary is the first 10 words (a stand-in for an LLM call you'll swap in later).
                 Empty text must return **422** (use a Pydantic model with validation).
            3. Log each request with the `logging` module.
            4. Write `test_main.py` using FastAPI's `TestClient`, covering both endpoints and the 422 case.
            5. Write a `README.md` with how to run it (`uv run uvicorn main:app --reload`) and test it.

            Then run it and open `http://127.0.0.1:8000/docs`: FastAPI generated interactive docs for you.
        """,
        "checks": [
            {"type": "contains", "label": "fastapi + uvicorn are dependencies", "path": f"{LAB}/08-api/pyproject.toml",
             "pattern": r"(?s)dependencies\s*=\s*\[[^\]]*fastapi[^\]]*\]"},
            {"type": "contains", "label": "uvicorn is a dependency", "path": f"{LAB}/08-api/pyproject.toml",
             "pattern": r"uvicorn"},
            {"type": "contains", "label": "pytest in the dev group", "path": f"{LAB}/08-api/pyproject.toml",
             "pattern": r"(?s)\[dependency-groups\].*pytest"},
            {"type": "run", "label": "GET /health returns ok",
             "cmd": ["uv", "run", "python", "-c",
                     "from fastapi.testclient import TestClient; from main import app; "
                     "r = TestClient(app).get('/health'); assert r.json() == {'status': 'ok'}, r.text; print('ok')"],
             "cwd": f"{LAB}/08-api", "stdout": r"ok"},
            {"type": "run", "label": "POST /summarize works and rejects empty text with 422",
             "cmd": ["uv", "run", "python", "-c",
                     "from fastapi.testclient import TestClient; from main import app; c = TestClient(app); "
                     "r = c.post('/summarize', json={'text': 'one two three'}); d = r.json(); "
                     "assert r.status_code == 200 and d['words'] == 3, r.text; "
                     "assert c.post('/summarize', json={'text': ''}).status_code == 422; print('ok')"],
             "cwd": f"{LAB}/08-api", "stdout": r"ok"},
            {"type": "contains", "label": "uses the logging module", "path": f"{LAB}/08-api/main.py",
             "pattern": r"import logging|from logging"},
            {"type": "run", "label": "uv run pytest passes", "cmd": ["uv", "run", "pytest", "-q"],
             "cwd": f"{LAB}/08-api", "stdout": r"passed"},
            {"type": "path", "label": "README.md exists", "path": f"{LAB}/08-api/README.md"},
        ],
    },
    {
        "id": "lab-docker",
        "title": "Put it in a container",
        "order": 9,
        "topics": [],
        "brief": r"""
            "Ship a service" in the report means a container. Docker packages your app and its
            exact environment so it runs the same on your laptop, a server or the cloud.

            **Mission**: containerize the FastAPI app from the previous lab (`~/pytrainer-lab/08-api/`).

            1. Start Docker (`sudo systemctl start docker`). You may need to add yourself to the
               `docker` group and log in again.
            2. Write a `Dockerfile` using a slim Python base image, install dependencies with uv, copy
               the app, and run uvicorn on `0.0.0.0:8000`.
            3. Add a `.dockerignore` so `.venv`, `__pycache__` and `.env` stay out of the image.
            4. Add a `HEALTHCHECK` that hits `/health`.
            5. Build it as `pytrainer-api` and run it: `docker run -p 8000:8000 pytrainer-api`.

            Explore: what is an image vs a container? Why does the order of `COPY` lines affect build speed?
        """,
        "checks": [
            {"type": "contains", "label": "Dockerfile starts from a Python base image",
             "path": f"{LAB}/08-api/Dockerfile", "pattern": r"(?im)^FROM\s+\S*python"},
            {"type": "contains", "label": "Dockerfile has a HEALTHCHECK", "path": f"{LAB}/08-api/Dockerfile",
             "pattern": r"(?im)^HEALTHCHECK"},
            {"type": "contains", "label": ".dockerignore excludes .venv and .env", "path": f"{LAB}/08-api/.dockerignore",
             "pattern": r"(?s)(?=.*\.venv)(?=.*\.env)"},
            {"type": "run", "label": "the image pytrainer-api exists (docker build done)",
             "cmd": ["docker", "image", "inspect", "pytrainer-api", "--format", "ok"], "stdout": r"ok"},
        ],
    },
    {
        "id": "lab-ci",
        "title": "Automate tests with GitHub Actions",
        "order": 10,
        "topics": ["testing"],
        "brief": r"""
            CI/CD shows up in 39% of AI engineering postings. CI means every push runs your tests
            automatically, so broken code never sneaks in.

            **Mission** in `~/pytrainer-lab/08-api/`:

            1. Make it a git repository and commit your work.
            2. Create `.github/workflows/ci.yml` that runs on `push` and `pull_request`:
               check out the code, install uv (the official `astral-sh/setup-uv` action), then run
               `uv run pytest`.
            3. Push it to a new GitHub repository (`gh repo create` makes this quick) and watch the
               run go green in the Actions tab.

            Explore: what's the difference between CI and CD? What would a "release gate" check
            before deploying an AI feature?
        """,
        "checks": [
            {"type": "path", "label": "it's a git repository", "path": f"{LAB}/08-api/.git", "dir": True},
            {"type": "contains", "label": "workflow runs on push", "path": f"{LAB}/08-api/.github/workflows/ci.yml",
             "pattern": r"(?m)^\s*(on:|push)"},
            {"type": "contains", "label": "workflow uses setup-uv", "path": f"{LAB}/08-api/.github/workflows/ci.yml",
             "pattern": r"astral-sh/setup-uv"},
            {"type": "contains", "label": "workflow runs pytest", "path": f"{LAB}/08-api/.github/workflows/ci.yml",
             "pattern": r"pytest"},
            {"type": "run", "label": "a GitHub remote is configured", "cmd": ["git", "remote", "-v"],
             "cwd": f"{LAB}/08-api", "stdout": r"github\.com"},
        ],
    },
    {
        "id": "lab-ship-package",
        "title": "Ship it: package and install a CLI",
        "order": 11,
        "topics": ["scripts", "testing"],
        "brief": r"""
            Code on your laptop helps one person. A package with a command people can install helps
            everyone, and it's how internal AI tools get shared in a team. Here you package a tiny
            token counter the way real Python tools are shipped.

            **Mission** in `~/pytrainer-lab/09-ship/`:

            1. Create a packaged project there called `tokcount` with uv (look for the option that
               makes a *package* with a `src/` layout, not just a script).
            2. Make the package expose a command named `tokcount` (the `[project.scripts]` table in
               `pyproject.toml`). `tokcount FILE` reads a text file and prints
               `words: <n>  tokens: <t>`, where `t` is the number of characters divided by 4,
               rounded up. With `--json` it prints `{"words": <n>, "tokens": <t>}` instead.
            3. Create `sample.txt` containing exactly `the cat sat on the mat` and check that
               `uv run tokcount sample.txt` prints `words: 6  tokens: 6`.
            4. Add pytest as a dev dependency and at least one test in `tests/`; `uv run pytest` passes.
            5. Build the package: `uv build`. A wheel (`.whl`) and a source archive appear in `dist/`.
            6. Install your wheel as a tool with uv, so `tokcount` works from any folder in a new terminal.

            Explore: what is inside a wheel (it's a zip file: open one)? What would you change to
            publish this on PyPI, and why would you try TestPyPI first?
        """,
        "checks": [
            {"type": "path", "label": "pyproject.toml exists", "path": f"{LAB}/09-ship/pyproject.toml"},
            {"type": "contains", "label": "it defines a tokcount command", "path": f"{LAB}/09-ship/pyproject.toml",
             "pattern": r"(?s)\[project\.scripts\][^\[]*tokcount\s*="},
            {"type": "path", "label": "it uses a src/ layout", "path": f"{LAB}/09-ship/src", "dir": True},
            {"type": "run", "label": "uv run tokcount sample.txt counts words and tokens",
             "cmd": ["uv", "run", "tokcount", "sample.txt"], "cwd": f"{LAB}/09-ship", "stdout": r"words: 6\s+tokens: 6"},
            {"type": "run", "label": "--json prints JSON", "cmd": ["uv", "run", "tokcount", "--json", "sample.txt"],
             "cwd": f"{LAB}/09-ship", "stdout": r'"words":\s*6'},
            {"type": "run", "label": "uv run pytest passes", "cmd": ["uv", "run", "pytest", "-q"],
             "cwd": f"{LAB}/09-ship", "stdout": r"passed"},
            {"type": "glob", "label": "uv build made a wheel", "pattern": f"{LAB}/09-ship/dist/tokcount-*.whl"},
            {"type": "command", "label": "tokcount is installed as a command", "cmd": "tokcount"},
        ],
    },
]
