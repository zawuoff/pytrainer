"""Read-the-traceback drills: a program crashes; click the line you would change to fix it.

``code`` really runs (in the sandbox) to produce the traceback the learner reads. ``answer_line``
is the line to change, which is often not the line the error points at: the skill is reading the
stack from the bottom up and asking where the bad value came from. ``solution`` is the fixed
program (shown once solved) and must run cleanly; ``error`` is the exception the code raises.
"""

PROMPT = ("This program crashed. Read the traceback, then **click the line you would change to fix it**, "
          "and press Check. The line the error points at isn't always the one that's wrong.")

EXTRAS = [
    {
        "id": "errors-tb1", "topic": "errors", "kind": "traceback", "mode": "traceback", "difficulty": 2,
        "title": "Read the traceback: a missing key", "error": "KeyError", "answer_line": 2,
        "prompt": PROMPT,
        "code": r'''
            def get_tokens(usage):
                return usage["total_tokens"]

            def report(response):
                usage = response["usage"]
                return f"Used {get_tokens(usage)} tokens"

            response = {"usage": {"prompt_tokens": 12, "completion_tokens": 30}}
            print(report(response))
        ''',
        "solution": r'''
            def get_tokens(usage):
                return usage["prompt_tokens"] + usage["completion_tokens"]

            def report(response):
                usage = response["usage"]
                return f"Used {get_tokens(usage)} tokens"

            response = {"usage": {"prompt_tokens": 12, "completion_tokens": 30}}
            print(report(response))
        ''',
        "explanation": r'''
            The last line of the traceback says `KeyError: 'total_tokens'`, and the frame above it points at line 2.
            The usage dict only has `prompt_tokens` and `completion_tokens`, so line 2 asks for a key that isn't
            there. Here the line that crashed is also the line to fix: add the two counts instead.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Start at the bottom of the traceback: what kind of error is it, and what key does it name?",
            "Look at the data the program builds on line 8. Which keys does the usage dict really have?",
            "The line that asks for the missing key is the one to change.",
        ],
    },
    {
        "id": "functions-tb1", "topic": "functions", "kind": "traceback", "mode": "traceback", "difficulty": 2,
        "title": "Read the traceback: a missing argument", "error": "TypeError", "answer_line": 6,
        "prompt": PROMPT,
        "code": r'''
            def build_prompt(system, question, context):
                return f"{system}\n\nContext: {context}\n\nQ: {question}"

            def ask(question):
                system = "Answer briefly."
                return build_prompt(system, question)

            print(ask("What is RAG?"))
        ''',
        "solution": r'''
            def build_prompt(system, question, context):
                return f"{system}\n\nContext: {context}\n\nQ: {question}"

            def ask(question):
                system = "Answer briefly."
                return build_prompt(system, question, "RAG retrieves passages before answering.")

            print(ask("What is RAG?"))
        ''',
        "explanation": r'''
            `TypeError: build_prompt() missing 1 required positional argument: 'context'`. The error is raised at the
            call, on line 6, before `build_prompt` even starts. `build_prompt` is fine; the call gives it two
            arguments when it needs three.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Read the error message word for word: which function, and which argument?",
            "A missing argument is a problem with the call, not with the function's body.",
            "Find the line that calls the function with too few arguments.",
        ],
    },
    {
        "id": "lists-tb1", "topic": "lists", "kind": "traceback", "mode": "traceback", "difficulty": 2,
        "title": "Read the traceback: one step too far", "error": "IndexError", "answer_line": 3,
        "prompt": PROMPT,
        "code": r'''
            def show(messages):
                lines = []
                for i in range(len(messages) + 1):
                    lines.append(f"{i + 1}. {messages[i]}")
                return "\n".join(lines)

            print(show(["hi", "hello", "bye"]))
        ''',
        "solution": r'''
            def show(messages):
                lines = []
                for i in range(len(messages)):
                    lines.append(f"{i + 1}. {messages[i]}")
                return "\n".join(lines)

            print(show(["hi", "hello", "bye"]))
        ''',
        "explanation": r'''
            `IndexError: list index out of range` is raised on line 4, where `messages[i]` is read. But line 4 is only
            the victim: `i` reaches 3 because the loop on line 3 runs `len(messages) + 1` times, and a 3-item list
            has no index 3. Fix the range, not the lookup.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "The error happens when reading `messages[i]`. Which value of i is too big?",
            "Where does i come from? Count how many times the loop runs for a list of 3.",
            "Change the line that decides how far i goes.",
        ],
    },
    {
        "id": "dicts-tb1", "topic": "dicts", "kind": "traceback", "mode": "traceback", "difficulty": 2,
        "title": "Read the traceback: a misspelled key", "error": "KeyError", "answer_line": 2,
        "prompt": PROMPT,
        "code": r'''
            def make_config(model, temperature):
                return {"model": model, "temprature": temperature}

            def describe(config):
                return f"{config['model']} at temperature {config['temperature']}"

            config = make_config("small", 0.2)
            print(describe(config))
        ''',
        "solution": r'''
            def make_config(model, temperature):
                return {"model": model, "temperature": temperature}

            def describe(config):
                return f"{config['model']} at temperature {config['temperature']}"

            config = make_config("small", 0.2)
            print(describe(config))
        ''',
        "explanation": r'''
            The crash is in `describe` on line 5: `KeyError: 'temperature'`. `describe` asks for the right key. The
            dict was built on line 2 with the key spelled `temprature`, so the fix is where the dict is made.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Which key is missing? Is it spelled correctly where it's read?",
            "Where was this dict created? Compare its keys with the one being read.",
            "Fix the line that builds the dict.",
        ],
    },
    {
        "id": "strings-tb1", "topic": "strings", "kind": "traceback", "mode": "traceback", "difficulty": 2,
        "title": "Read the traceback: the wrong variable", "error": "AttributeError", "answer_line": 5,
        "prompt": PROMPT,
        "code": r'''
            def normalize(text):
                return " ".join(text.lower().split())

            def normalize_all(texts):
                return [normalize(texts) for text in texts]

            print(normalize_all(["Hello  World", "RAG Systems"]))
        ''',
        "solution": r'''
            def normalize(text):
                return " ".join(text.lower().split())

            def normalize_all(texts):
                return [normalize(text) for text in texts]

            print(normalize_all(["Hello  World", "RAG Systems"]))
        ''',
        "explanation": r'''
            `AttributeError: 'list' object has no attribute 'lower'`, raised on line 2. `normalize` expects one string,
            but it got a list. The traceback shows who called it: line 5, which passes `texts` (the whole list)
            instead of `text` (one item).
        ''',
        "starter": "", "tests": "",
        "hints": [
            "The error says a list has no `lower`. `normalize` expects a string, so who handed it a list?",
            "Go one frame up in the traceback, to the line that called `normalize`.",
            "Look closely at which variable that line passes: the loop variable or the whole list?",
        ],
    },
    {
        "id": "classes-tb1", "topic": "classes", "kind": "traceback", "mode": "traceback", "difficulty": 2,
        "title": "Read the traceback: an attribute that never existed", "error": "AttributeError", "answer_line": 3,
        "prompt": PROMPT,
        "code": r'''
            class Chat:
                def __init__(self, system):
                    self.message = [{"role": "system", "content": system}]

                def add(self, role, content):
                    self.messages.append({"role": role, "content": content})

            chat = Chat("Be brief.")
            chat.add("user", "hi")
            print(len(chat.messages))
        ''',
        "solution": r'''
            class Chat:
                def __init__(self, system):
                    self.messages = [{"role": "system", "content": system}]

                def add(self, role, content):
                    self.messages.append({"role": role, "content": content})

            chat = Chat("Be brief.")
            chat.add("user", "hi")
            print(len(chat.messages))
        ''',
        "explanation": r'''
            `'Chat' object has no attribute 'messages'` is raised in `add`, line 6. Every other line uses `messages`;
            only `__init__`, on line 3, creates `self.message` without the s. So the attribute was never created under
            the name the rest of the class expects.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Which attribute is missing? Where should it have been created?",
            "Attributes are usually created in `__init__`. Compare the names.",
            "Fix the line that creates the attribute.",
        ],
    },
    {
        "id": "json-tb1", "topic": "json", "kind": "traceback", "mode": "traceback", "difficulty": 2,
        "title": "Read the traceback: past the library frames", "error": "JSONDecodeError", "answer_line": 4,
        "setup_files": {"settings.json": "{\"model\": \"small\", \"temperature\": 0.2}\n"},
        "prompt": PROMPT,
        "code": r'''
            import json

            def load_settings(path):
                return json.loads(path)

            settings = load_settings("settings.json")
            print(settings["model"])
        ''',
        "solution": r'''
            import json

            def load_settings(path):
                with open(path, encoding="utf-8") as f:
                    return json.load(f)

            settings = load_settings("settings.json")
            print(settings["model"])
        ''',
        "explanation": r'''
            The bottom frames are inside the `json` library: that's where the error was raised, but library code is
            almost never what's wrong. Go up to the last frame in your own file: line 4 hands `json.loads` the
            *file name* `"settings.json"` and asks it to parse that as JSON. It should read the file first.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Several frames are inside Python's json library. Skip them: which line of this program is the last one listed?",
            "What does `json.loads` expect: a file name, or JSON text?",
            "Change the line that passes the path to the JSON parser.",
        ],
    },
    {
        "id": "comprehensions-tb1", "topic": "comprehensions", "kind": "traceback", "mode": "traceback",
        "difficulty": 2, "title": "Read the traceback: an empty list from a filter", "error": "ZeroDivisionError",
        "answer_line": 2,
        "prompt": PROMPT,
        "code": r'''
            def average_latency(latencies):
                valid = [ms for ms in latencies if ms < 0]
                return sum(valid) / len(valid)

            print(average_latency([120, 80, 100]))
        ''',
        "solution": r'''
            def average_latency(latencies):
                valid = [ms for ms in latencies if ms >= 0]
                return sum(valid) / len(valid)

            print(average_latency([120, 80, 100]))
        ''',
        "explanation": r'''
            `ZeroDivisionError` on line 3 means `len(valid)` was 0. Why is `valid` empty when there are three
            latencies? Line 2 keeps only negative values, which is backwards: valid latencies are the ones that
            are 0 or more.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Dividing by zero here means one of the values on line 3 was 0. Which one?",
            "Why would that list be empty? Look at how it was built.",
            "Check the condition in the comprehension against the data.",
        ],
    },
    {
        "id": "api-data-tb1", "topic": "api-data", "kind": "traceback", "mode": "traceback", "difficulty": 2,
        "title": "Read the traceback: the API's real key", "error": "KeyError", "answer_line": 2,
        "prompt": PROMPT,
        "code": r'''
            def total_tokens(responses):
                return sum(r["usage"]["total"] for r in responses)

            responses = [
                {"id": "a", "usage": {"total_tokens": 40}},
                {"id": "b", "usage": {"total_tokens": 12}},
            ]
            print(total_tokens(responses))
        ''',
        "solution": r'''
            def total_tokens(responses):
                return sum(r["usage"]["total_tokens"] for r in responses)

            responses = [
                {"id": "a", "usage": {"total_tokens": 40}},
                {"id": "b", "usage": {"total_tokens": 12}},
            ]
            print(total_tokens(responses))
        ''',
        "explanation": r'''
            `KeyError: 'total'`, raised on line 2. The responses use `total_tokens` as the key, so the generator
            expression on line 2 looks up a key the data never had. The data is right; the lookup is wrong.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Which key is missing, and which keys does each usage dict actually have?",
            "The data comes from an API you don't control. Which side should change: the data or the code?",
            "Change the line that looks the key up.",
        ],
    },
    {
        "id": "files-tb1", "topic": "files", "kind": "traceback", "mode": "traceback", "difficulty": 2,
        "title": "Read the traceback: a path built twice", "error": "FileNotFoundError", "answer_line": 10,
        "setup_files": {"docs/intro.md": "# Intro\nWelcome.\n", "docs/setup.md": "# Setup\nInstall it.\n"},
        "prompt": PROMPT,
        "code": r'''
            from pathlib import Path

            DOCS = Path("docs")

            def load(name):
                return (DOCS / name).read_text(encoding="utf-8")

            names = ["intro.md", "setup.md"]
            for name in names:
                print(load(name + ".md")[:7])
        ''',
        "solution": r'''
            from pathlib import Path

            DOCS = Path("docs")

            def load(name):
                return (DOCS / name).read_text(encoding="utf-8")

            names = ["intro.md", "setup.md"]
            for name in names:
                print(load(name)[:7])
        ''',
        "explanation": r'''
            The bottom frames are inside `pathlib`; the error names the file it tried to open:
            `docs/intro.md.md`. `load` on line 6 does what it's told. The extra `.md` is added by the caller on
            line 10, even though the names already end in `.md`.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Read the file name in the error message carefully. Does that file exist?",
            "`load` joins whatever name it gets onto the folder. Who decides the name it gets?",
            "Change the line that builds the name passed to `load`.",
        ],
    },
    {
        "id": "regex-tb1", "topic": "regex", "kind": "traceback", "mode": "traceback", "difficulty": 2,
        "title": "Read the traceback: a broken pattern", "error": "error", "answer_line": 3,
        "prompt": PROMPT,
        "code": r'''
            import re

            CITATION = re.compile(r"\[(\d+\]")

            def citations(answer):
                return [int(n) for n in CITATION.findall(answer)]

            print(citations("Paris [1] and Lyon [2]"))
        ''',
        "solution": r'''
            import re

            CITATION = re.compile(r"\[(\d+)\]")

            def citations(answer):
                return [int(n) for n in CITATION.findall(answer)]

            print(citations("Paris [1] and Lyon [2]"))
        ''',
        "explanation": r'''
            The error is raised deep inside the `re` module while compiling the pattern: `missing ), unterminated
            subpattern`. The last frame in this file is line 3, the `re.compile` call. The group `(` opened before
            `\d+` is never closed: the pattern needs `)` before `\]`.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "The error happens while the program starts, before `citations` is ever called. Which line runs then?",
            "The message mentions a missing `)`. Count the opening and closing parentheses in the pattern.",
            "Fix the line that compiles the pattern.",
        ],
    },
    {
        "id": "sorting-tb1", "topic": "sorting", "kind": "traceback", "mode": "traceback", "difficulty": 2,
        "title": "Read the traceback: bad data, not bad sorting", "error": "TypeError", "answer_line": 1,
        "prompt": PROMPT,
        "code": r'''
            results = [("a", 0.9), ("b", "0.4"), ("c", 0.7)]

            def rank(items):
                return sorted(items, key=lambda item: item[1], reverse=True)

            for doc_id, score in rank(results):
                print(doc_id, score)
        ''',
        "solution": r'''
            results = [("a", 0.9), ("b", 0.4), ("c", 0.7)]

            def rank(items):
                return sorted(items, key=lambda item: item[1], reverse=True)

            for doc_id, score in rank(results):
                print(doc_id, score)
        ''',
        "explanation": r'''
            `'<' not supported between instances of 'str' and 'float'`, raised by `sorted` on line 4. The sorting
            code is fine: it can't compare a string with a number. One score on line 1, `"0.4"`, is a string. Fix
            the data where it's created.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "The message names two types that can't be compared. Which values are they?",
            "Look at the scores in the data. Are they all the same type?",
            "Change the line where the bad value comes from.",
        ],
    },
]
