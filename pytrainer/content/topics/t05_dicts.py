TOPIC = {
    "id": "dicts",
    "title": "Dictionaries",
    "track": "foundations",
    "order": 7,
    "requires": ["lists", "loops"],
    "summary": """
        Key-value mappings: safe access with defaults, merging, iterating over items,
        counting and grouping, nested API-response-like structures, and deleting keys.
    """,
    "concepts": ["key access", "get with default", "update", "merge operator |", "items()",
                 "counting", "grouping", "setdefault", "dict of lists", "nested dicts",
                 "del / pop", "copying nested data"],
}

# The Library card for this chapter (shown once the chapter's steps are done).
# Every line that starts with `#` in an example is the real output of that example.
REFERENCE = {
    "keywords": ["dict", "dictionary", "key", "value", "pair", "lookup", "keyerror", "curly braces",
                 "count", "group", "nested"],
    "cards": [
        {
            "syntax": 'd = {"key": value}',
            "explain": "Creates a dict. d[key] reads a value, d[key] = value adds or replaces a pair.",
            "example": r'''
                msg = {"role": "user"}
                msg["content"] = "hi"
                print(msg["role"], len(msg))
                # user 2
            ''',
        },
        {
            "syntax": "d.get(key, default)",
            "explain": "Reads a value without a KeyError. Returns default (or None) when the key is missing.",
            "example": r'''
                usage = {"input": 12}
                print(usage.get("input", 0))
                # 12
                print(usage.get("output", 0))
                # 0
            ''',
        },
        {
            "syntax": "key in d",
            "explain": "True when key is one of the dict's keys. It does not look at the values.",
            "example": r'''
                msg = {"role": "user"}
                print("role" in msg)
                # True
                print("user" in msg)
                # False
            ''',
        },
        {
            "syntax": "for key, value in d.items():",
            "explain": "Loops over the pairs in the order they were added. d.keys() and d.values() give one side.",
            "example": r'''
                prices = {"tea": 3, "cake": 4}
                for name, price in prices.items():
                    print(name, price)
                # tea 3
                # cake 4
            ''',
        },
        {
            "syntax": "counts[x] = counts.get(x, 0) + 1",
            "explain": "Counts how many times each value appears: start from 0 for a new key, then add 1.",
            "example": r'''
                counts = {}
                for word in ["a", "b", "a"]:
                    counts[word] = counts.get(word, 0) + 1
                print(counts)
                # {'a': 2, 'b': 1}
            ''',
        },
        {
            "syntax": "del d[key]  /  d.pop(key)",
            "explain": "del removes a pair. pop removes it and returns its value. Both raise KeyError if the key is missing.",
            "example": r'''
                msg = {"role": "user", "name": "bot"}
                print(msg.pop("name"))
                # bot
                del msg["role"]
                print(msg)
                # {}
            ''',
        },
    ],
}

LESSON = r'''
## Chapter notes: Dictionaries

A **dict** (dictionary) is a value that stores **key-value pairs**. Each **key** is paired
with one **value**, and you read a value by giving its key. You write a dict with curly
braces, a colon between each key and its value, and commas between the pairs. `{}` is the
empty dict.

```python
msg = {"role": "user", "content": "hi"}
print(msg)
# {'role': 'user', 'content': 'hi'}
print(len(msg))
# 2
```

Keys are usually strings. A value can be of any type, including a list or another dict.
A dict keeps its pairs in the order you added them. `len(msg)` returns the number of pairs.

### Reading and writing

`msg["role"]` returns the value stored under the key `"role"`. `msg["role"] = "assistant"`
replaces that value. Assigning to a key that does not exist adds a new pair.
`"role" in msg` is `True` when `"role"` is a key. It checks the keys, not the values.

```python
msg = {"role": "user", "content": "hi"}
print(msg["role"])
# user
msg["role"] = "assistant"
msg["name"] = "bot"
print(msg)
# {'role': 'assistant', 'content': 'hi', 'name': 'bot'}
print("role" in msg)
# True
print("hi" in msg)
# False
```

Click a key to read its value. Then type a key that does not exist and run `d[key]`.

```diagram
{"type":"dict","title":"Read, add and delete keys in msg","name":"msg","entries":[["role","user"],["content","hi"]]}
```

### Missing keys

`msg["name"]` raises `KeyError` when `"name"` is not a key, and the program stops.
`msg.get("name")` returns `None` in that case. `msg.get("name", "anon")` returns the
second value you pass, here `"anon"`.

```python
msg = {"role": "user", "content": "hi"}
print(msg.get("name"))
# None
print(msg.get("name", "anon"))
# anon
print(msg.get("role", "anon"))
# user
```

### Looping

`for key in d:` gives each key. `d.values()` gives each value. `d.items()` gives each key
together with its value, so the loop needs two names.

```python
usage = {"prompt_tokens": 12, "completion_tokens": 3}
for key in usage:
    print(key)
# prompt_tokens
# completion_tokens
for value in usage.values():
    print(value)
# 12
# 3
for key, value in usage.items():
    print(key, value)
# prompt_tokens 12
# completion_tokens 3
```

### Counting and grouping

To count, read the current count with a default of `0`, add 1, and store the result.
To group, store a list under each key and append to it. `groups.setdefault(source, [])`
returns the list stored under `source`. If `source` is not a key yet, it first stores `[]`
under that key.

```python
roles = ["user", "assistant", "user"]
counts = {}
for role in roles:
    counts[role] = counts.get(role, 0) + 1
print(counts)
# {'user': 2, 'assistant': 1}

chunks = [("a.pdf", "intro"), ("b.md", "setup"), ("a.pdf", "details")]
groups = {}
for source, text in chunks:
    groups.setdefault(source, []).append(text)
print(groups)
# {'a.pdf': ['intro', 'details'], 'b.md': ['setup']}
```

### Nested data

An **API** is a service that your program sends a request to and that sends data back.
API responses are dicts that contain lists and other dicts. Write one pair of square
brackets per level, starting with the outermost dict.

```python
response = {"choices": [{"message": {"role": "assistant", "content": "Paris."}}]}
print(response["choices"][0]["message"]["content"])
# Paris.
```

### Merging, copying and deleting

`a | b` builds a new dict with the pairs of both. When a key is in both, the value from
`b` is used. `a.update(b)` does the same merge but changes `a` itself. `a.copy()` returns a
new dict with the same pairs. The copy is **shallow**: a list or dict stored as a value is
not copied, so both dicts refer to the same inner object.

`del d[key]` removes a pair and raises `KeyError` when the key is missing. `d.pop(key)`
removes the pair and returns its value. `d.pop(key, None)` returns `None` when the key is
missing and raises no error.

```python
a = {"model": "gpt-4o-mini", "temperature": 0.7}
b = {"temperature": 0}
print(a | b)
# {'model': 'gpt-4o-mini', 'temperature': 0}
c = a.copy()
c.update(b)
del c["model"]
print(c)
# {'temperature': 0}
print(c.pop("temperature"))
# 0
print(c.pop("temperature", None))
# None
print(a)
# {'model': 'gpt-4o-mini', 'temperature': 0.7}
```

### Common mistakes

- `config[model]` uses the value of the variable `model` as the key. To look up the key
  `"model"`, write `config["model"]`.
- `d.get(key) or default` returns `default` when the stored value is `0`, `""` or `False`.
  `d.get(key, default)` returns `default` only when the key is missing.
- `b = a` does not copy. Both names refer to the same dict object. Use `a.copy()`.
- Do not add or remove keys inside a `for` loop over the same dict. When the number of
  pairs changes during the loop, Python stops with
  `RuntimeError: dictionary changed size during iteration`.

Docs: [Dictionaries tutorial](https://docs.python.org/3/tutorial/datastructures.html#dictionaries),
[dict methods](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict).
'''

EXERCISES = [
    {
        "id": "dicts-s1",
        "lesson": r'''
            ## Giving every value a label

            Your app keeps a few facts about each document that a model may search: its title, and how many
            pages it has. A list can hold them, as `["Refund policy", 4]`. But a list only knows positions.
            You have to remember that index 0 is the title and index 1 is the page count, and so does
            everyone who reads your code. It is easier to stick a label on each value, and to ask for the
            value by its label.

            ```python
            doc = {"title": "Refund policy", "pages": 4}
            print(doc["title"])
            # Refund policy
            print(len(doc))
            # 2
            ```

            The curly braces hold two pairs, with a comma between them. In each pair, the label stands
            before the colon and the value after it. `doc["title"]` reads the value that carries the label
            `"title"`. The square brackets are the ones you know from lists, with a label in the place of
            the index.

            This is called a **dictionary**, or **dict** for short. A label is called a **key**. A key
            together with its value is a **key-value pair**, and `len` counts the pairs.

            ```quiz
            What does `doc["pages"]` give?
            - [x] `4` :: Right. Python finds the pair whose key is `"pages"` and hands back the value of that pair.
            - [ ] `"pages"` :: That is the key, the label you asked with. The lookup hands back the value that is stored under it.
            - [ ] `1` :: A dict does not answer with a position. It answers with the value that is stored under the key, and that is 4.
            ```

            ### Adding a pair

            An assignment to a key that is not in the dict yet adds a new pair:

            ```python
            doc = {"title": "Refund policy", "pages": 4}
            doc["language"] = "en"
            print(doc)
            # {'title': 'Refund policy', 'pages': 4, 'language': 'en'}
            ```

            Python prints the strings of a dict in single quotes. They are still the same strings.

            Click a row to read the value under that key. Then type a new key and a value, and press the
            `doc[key] = value` button to add a pair:

            ```diagram
            {"type":"dict","title":"Keys and values of doc","name":"doc","entries":[["title","Refund policy"],["pages",4]]}
            ```

            ### A key that may not be there

            There is a second way to read a value: `doc.get("author")`. When the key is in the dict, `.get`
            hands back its value. When the key is missing, it hands back `None`. With a second argument, it
            hands back that argument in place of `None`:

            ```python
            doc = {"title": "Refund policy", "pages": 4}
            print(doc.get("pages"))
            # 4
            print(doc.get("author"))
            # None
            print(doc.get("author", "unknown"))
            # unknown
            ```

            ```predict
            tool = {"name": "search"}
            tool["calls"] = 2
            tool["limit"] = 10
            print(len(tool))
            print(tool.get("owner", "nobody"))
            ---
            Two assignments to new keys added two pairs, so the dict now has 3 of them. It has no key
            `"owner"`, so `.get` hands back its second argument, `nobody`.
            ```

            Later steps in this chapter come back to each of these, so a first look is enough here.

            **Watch out:** a dict has no positions. `doc[0]` does not read the first pair. Python looks for
            a key that is equal to `0`, finds none, and stops with `KeyError: 0`.

            **In short:** a dict holds key-value pairs, and you read a value by its key, not by a position.
        ''',
        "title": "What gets printed?",
        "difficulty": 0,
        "mode": "predict",
        "prompt": r'''
            Read the program in the editor. Type exactly what it prints, one line for each `print`.
        ''',
        "code": r'''
            config = {"model": "gpt-4o", "temperature": 0.7}
            print(config["model"])
            config["max_tokens"] = 256
            print(len(config))
            print(config.get("stream"))
            print(config.get("stream", False))
        ''',
        "solution": r'''
            gpt-4o
            3
            None
            False
        ''',
        "explanation": r'''
            `config["model"]` reads the value that is stored under the key `"model"`, and `print` shows that
            string without its quotes: `gpt-4o`. The key `"max_tokens"` was not in the dict, so the
            assignment adds a third pair, and `len` counts 3. The dict has no key `"stream"`. For a missing
            key, `.get` with one argument hands back `None`. With a second argument it hands back that
            argument, which is `False` here.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Go through the program one line at a time, and keep track of the pairs that are in the dict after each line.",
            "An assignment to a key that the dict does not have yet adds a pair, and that happens before `len` counts. `.get` never stops the program when a key is missing.",
            "Your first line is the value stored under the key that the first `print` asks for, without quotes. Your second line is the number of pairs after one pair was added. Your third and fourth lines are what `.get` hands back for a key that is not in the dict: first with no second argument, then with one.",
        ],
    },
    {
        "id": "dicts-s2",
        "lesson": r'''
            ## Asking a dict for one value

            After every call, a model service reports how many tokens the call used: how many went in with
            your prompt, and how many came out in the answer. Your app needs one of those two numbers for
            the bill. Which number it gets depends on the key that it asks with.

            ```python
            usage = {"input_tokens": 12, "output_tokens": 3}
            print(usage["output_tokens"])
            # 3
            ```

            Write the name of the dict, and then the key in square brackets. Python goes to the pair that
            has this key and hands back its value. Where the pair stands in the dict makes no difference.
            `"output_tokens"` is the second pair here, and Python would find it just the same if it were the
            first pair or the tenth.

            Reading a value by its key is called a **lookup**.

            ### The quotes belong to the key

            The keys of this dict are strings, so the key in the brackets is a string too, with its quotes.
            It has to be exactly equal to a key of the dict, down to the capital letters. Pick the key that
            makes this program print `3`:

            ```fill
            usage = {"input_tokens": 12, "output_tokens": 3}
            print(usage[___])
            ---
            - [x] "output_tokens" :: Right. This string is exactly equal to the key of the second pair, so Python hands back the value of that pair.
            - [ ] output_tokens :: Without quotes this is the name of a variable, and no variable of that name exists. Python stops with `NameError: name 'output_tokens' is not defined`.
            - [ ] "Output_tokens" :: The capital `O` makes this a different string. No key is equal to it, so Python stops with `KeyError: 'Output_tokens'`.
            - [ ] 1 :: A dict has no positions. Python looks for a key that is equal to `1`, finds none, and stops with `KeyError: 1`.
            ```

            ### A key that comes from a variable

            Without quotes, Python reads a word as the name of a variable. That is an error when no such
            variable exists. It is useful when one does, because the lookup then uses the value of the
            variable as the key:

            ```python
            usage = {"input_tokens": 12, "output_tokens": 3}
            wanted = "input_tokens"
            print(usage[wanted])
            # 12
            ```

            ```try
            prices = {"mini": 0.15, "standard": 2.5, "large": 10.0}
            model = "mini"
            print(prices[model])
            ---
            This prints the price of the model `mini`. Change one value so that the program prints `10.0`.
            ---
            prices = {"mini": 0.15, "standard": 2.5, "large": 10.0}
            model = "large"
            print(prices[model])
            ---
            The line with the lookup stayed as it was. It uses the value of `model` as the key, so another value in that variable reads another pair.
            ```

            **Watch out:** when a lookup stops with `NameError: name 'output_tokens' is not defined`, the
            quotes around the key are missing. Python took the key for a variable.

            **In short:** `d["key"]` hands back the value that is stored under that key, and a string key
            needs its quotes.
        ''',
        "title": "Read the model name",
        "difficulty": 0,
        "prompt": r'''
            The settings for a call to a model are kept in a dict: which model to use, and a few options.
            Your app wants to show the name of the chosen model on the screen.

            **Your job:** finish `get_model(config)` so that it gives back the name of the model. The
            function is already written except for one gap, marked `___`. Replace the gap.

            **What goes in**
            - `config`: a dict of settings that always has the key `"model"`, for example
              `{"model": "gpt-4o", "temperature": 0.7}`

            **What comes out**
            - the value that is stored under the key `"model"`, a string: `"gpt-4o"` for the example value

            **Rules**
            - The pair with the key `"model"` may stand anywhere in the dict. It is not always the first
              pair.

            **Examples**
            ```python
            get_model({"model": "gpt-4o", "temperature": 0.7})   # returns "gpt-4o"
            get_model({"temperature": 0, "model": "claude"})     # returns "claude"
            ```
        ''',
        "starter": r'''
            def get_model(config):
                return config[___]
        ''',
        "tests": r'''
            from solution import get_model

            def test_returns_model_value_gpt_4o():
                got = get_model({"model": "gpt-4o", "temperature": 0.7})
                assert got == "gpt-4o", f"got {got!r}"

            def test_returns_model_value_when_not_first_key():
                got = get_model({"temperature": 0, "model": "claude"})
                assert got == "claude", f"got {got!r}"
        ''',
        "solution": r'''
            def get_model(config):
                return config["model"]
        ''',
        "hints": [
            "The lesson reads a value out of a dict with square brackets. What stands between the brackets?",
            "The gap needs the key of the pair that you want. The task names that key, and the key is a string.",
            "Write the key into the gap as a string, spelled the way the task spells it and with its quotes. Without the quotes, Python would look for a variable of that name.",
        ],
    },
    {
        "id": "dicts-s4",
        "lesson": r'''
            ## Building a dict from values you have

            A search tool in your app finds a passage in a file and works out a score for it. Now it has two
            values in two variables. It wants to hand them on as one result, in a form that says which value
            is which. So it packs them into a dict.

            ```python
            source = "faq.md"
            score = 0.82
            hit = {"source": source, "score": score}
            print(hit)
            # {'source': 'faq.md', 'score': 0.82}
            ```

            Look at the two sides of each colon. On the left stands the key, a string that you choose and
            write in quotes. On the right stands the value, and here it is a variable, written without
            quotes. Python reads what the variable holds at that moment and stores it in the dict.

            The next program should print `en`. Put its lines in an order that works:

            ```order
            language = "en"
            length = 120
            note = {"language": language, "length": length}
            print(note["language"])
            ---
            The two variables have to exist before the line that builds the dict, because Python reads their values on that line. The `print` comes last, because it needs the dict.
            ```

            ### Quotes decide: text or variable

            The same word can stand on both sides of a colon, as in `"score": score`. With quotes it is a
            piece of text. Without quotes it is the variable. See what happens when the value gets quotes by
            mistake:

            ```predict
            name = "claude"
            right = {"model": name}
            wrong = {"model": "name"}
            print(right["model"])
            print(wrong["model"])
            ---
            `name` without quotes is the variable, so the first dict stores its value, `claude`. `"name"`
            with quotes is a string of four letters, so the second dict stores the text `name`.
            ```

            A dict that you write in braces is a value like any other. You can store it under a name, as in
            the examples above, or hand it back from a function with `return`.

            Two dicts are equal when they hold the same pairs. That is how a check compares the dict that
            your function hands back with the one it expects:

            ```python
            hit = {"source": "faq.md", "score": 0.82}
            print(hit == {"source": "faq.md", "score": 0.82})
            # True
            print(hit == {"Source": "faq.md", "score": 0.82})
            # False
            ```

            **Watch out:** a key without quotes is not always an error. When a variable `source` exists,
            `{source: source}` uses the value of the variable as the key and gives `{'faq.md': 'faq.md'}`.
            No message warns you, and a later lookup with `"source"` fails.

            **In short:** `{"key": value}` builds a dict, with the key in quotes on the left of each colon
            and the value on the right.
        ''',
        "title": "Make a chat message",
        "difficulty": 0,
        "prompt": r'''
            A conversation with a model is sent as a list of messages, and every message is a small dict
            with two pairs. One pair says who is speaking, which is called the role. The other pair holds
            what was said, which is called the content. The role `"user"` stands for the person who types.
            The role `"system"` stands for the instructions that an app gives the model before the
            conversation starts.

            **Your job:** write `make_message(role, content)` so that it gives back one such message dict.

            **What goes in**
            - `role`: a string that says who is speaking, for example `"user"`
            - `content`: a string, the text of the message, for example `"hi"`

            **What comes out**
            - a dict with two pairs: the key `"role"` with the value of `role`, and the key `"content"` with
              the value of `content`. For the example values that is `{"role": "user", "content": "hi"}`.

            **Rules**
            - The keys are exactly the strings `"role"` and `"content"`, in small letters.
            - The dict has no other keys.
            - The two values are stored as they come in. Nothing is added to them or changed.

            **Examples**
            ```python
            make_message("user", "hi")            # returns {"role": "user", "content": "hi"}
            make_message("system", "Be brief.")   # returns {"role": "system", "content": "Be brief."}
            ```
        ''',
        "starter": r'''
            def make_message(role, content):
                ...
        ''',
        "tests": r'''
            from solution import make_message

            def test_user_message_dict():
                got = make_message("user", "hi")
                assert got == {"role": "user", "content": "hi"}, f"got {got!r}"

            def test_system_message_dict():
                got = make_message("system", "Be brief.")
                assert got == {"role": "system", "content": "Be brief."}, f"got {got!r}"
        ''',
        "solution": r'''
            def make_message(role, content):
                return {"role": role, "content": content}
        ''',
        "hints": [
            "The lesson builds a dict from two variables. In your function, the two parameters play the part of those variables.",
            "Write a dict in curly braces with two pairs. The keys are fixed text, and the task tells you how they are spelled. The values are whatever was passed in.",
            "The body is one `return` line with a dict in curly braces. In each pair, the key stands on the left of the colon as a string in quotes, and the parameter stands on the right of the colon without quotes.",
        ],
    },
    {
        "id": "dicts-s6",
        "lesson": r'''
            ## Storing a value under a key

            A user opens the settings of your chat app and switches the reply language to French. The dict
            of settings already exists, and one value in it has to change. A minute later the user picks a
            voice for the first time, and the dict has to take a pair that it never had.

            Both jobs are done by the same kind of line:

            ```python
            prefs = {"language": "en"}
            prefs["language"] = "fr"
            prefs["voice"] = "calm"
            print(prefs)
            # {'language': 'fr', 'voice': 'calm'}
            ```

            Read `prefs["voice"] = "calm"` as "prefs, store `calm` under the key `voice`". Python looks for
            the key. When the key is already there, its value is replaced. When it is not, a new pair is
            added at the end. You do not have to know which of the two cases you are in.

            A dict never holds the same key twice. That is why the first assignment could only replace:
            there is one place for `"language"`, and it now holds `"fr"`.

            ```predict
            profile = {"name": "Ada"}
            profile["plan"] = "free"
            profile["plan"] = "pro"
            print(len(profile))
            print(profile["plan"])
            ---
            The first assignment adds the key `"plan"`, so the dict has 2 pairs. The second one finds that
            key and replaces its value. The length stays 2, and the value is now `pro`.
            ```

            ### A typo makes a new pair

            The key has to be spelled exactly as it is in the dict. Fix this program:

            ```try
            prefs = {"language": "en", "voice": "calm"}
            prefs["Voice"] = "loud"
            print(prefs)
            ---
            This should change the voice to `loud`. Because of a capital letter in the key, it adds a third pair instead. Fix the key so that the program prints `{'language': 'en', 'voice': 'loud'}`.
            ---
            prefs = {"language": "en", "voice": "calm"}
            prefs["voice"] = "loud"
            print(prefs)
            ---
            With the key spelled exactly as in the dict, the assignment found the pair and replaced its value.
            ```

            ### The dict itself changes

            Like `append` on a list, this assignment changes the dict that is already there, in place. No
            second dict is made. In the Lists chapter you saw that a parameter is a second name for the
            caller's list, not a copy. The same is true of a dict:

            ```quiz
            What does this program print?

            ~~~python
            def turn_on(options):
                options["stream"] = True

            mine = {"stream": False}
            turn_on(mine)
            print(mine)
            ~~~
            - [x] `{'stream': True}` :: Right. Inside the function, `options` is a second name for the dict that `mine` names. The assignment changed that one dict.
            - [ ] `{'stream': False}` :: That would be the output if the function had received a copy. It receives the dict itself.
            - [ ] `None` :: `turn_on` hands back `None`, but the program prints `mine`, not the result of the call.
            ```

            A function that changes a dict in this way can also hand that same dict back with `return`, so
            that the caller can go on working with it.

            **Watch out:** a wrong key in an assignment is never an error. Python adds a pair under the
            wrong key, and the value that you meant to change stays as it was.

            **In short:** `d[key] = value` replaces the value when the key exists, and adds a new pair when
            it does not.
        ''',
        "title": "Set the token limit",
        "difficulty": 0,
        "prompt": r'''
            A model writes its answer piece by piece, in tokens, and a request can set the most tokens that
            the answer may have. That setting is stored in the request's dict of settings, under the key
            `"max_tokens"`.

            **Your job:** write `set_max_tokens(config, limit)`. It stores the limit in the dict that it is
            given, and it gives that same dict back.

            **What goes in**
            - `config`: a dict of settings, for example `{"model": "gpt-4o"}`. The key `"max_tokens"` may
              be in it already, or not.
            - `limit`: a whole number, for example `256`

            **What comes out**
            - the dict that was passed in, which now has `limit` stored under the key `"max_tokens"`. For
              the example values that is `{"model": "gpt-4o", "max_tokens": 256}`.

            **Rules**
            - When the dict has no key `"max_tokens"`, the pair is added.
            - When the key is already there, its old value is replaced.
            - All the other pairs stay as they are.
            - What comes back is the very dict that was passed in, with the change made to it. It is not a
              copy. A check tests this.

            **Examples**
            ```python
            set_max_tokens({"model": "gpt-4o"}, 256)
            # returns {"model": "gpt-4o", "max_tokens": 256}
            set_max_tokens({"model": "m", "max_tokens": 100}, 1024)
            # returns {"model": "m", "max_tokens": 1024}
            ```
        ''',
        "starter": r'''
            def set_max_tokens(config, limit):
                ...
        ''',
        "tests": r'''
            from solution import set_max_tokens

            def test_adds_missing_key():
                got = set_max_tokens({"model": "gpt-4o"}, 256)
                assert got == {"model": "gpt-4o", "max_tokens": 256}, f"got {got!r}"

            def test_replaces_existing_value():
                got = set_max_tokens({"model": "m", "max_tokens": 100}, 1024)
                assert got == {"model": "m", "max_tokens": 1024}, f"got {got!r}"

            def test_changes_and_returns_the_same_dict():
                config = {"model": "m"}
                got = set_max_tokens(config, 5)
                assert config.get("max_tokens") == 5, f"the dict you were given is {config!r}"
                assert got is config, "return the same dict you were given"
        ''',
        "solution": r'''
            def set_max_tokens(config, limit):
                config["max_tokens"] = limit
                return config
        ''',
        "hints": [
            "The lesson stores a value under a key with one assignment. Does that line need to know whether the key is already in the dict?",
            "One assignment covers both cases: it adds the pair, or it replaces the value. Make it on the dict that was passed in, not on a copy, and then hand that dict back.",
            "The body has two lines. The first is an assignment. On its left stands the dict, with the key from the task in square brackets, and on its right stands the limit. The second line hands the dict back with `return`.",
        ],
    },
    {
        "id": "dicts-s3",
        "lesson": r'''
            ## When a key might be missing

            Most users of your chat app never open the settings. For them, the dict of settings has no pair
            for the reply language at all. Your code asks for it anyway, and this happens:

            ```python
            settings = {"theme": "dark"}
            print(settings["language"])
            # KeyError: 'language'
            ```

            Square brackets insist that the key exists. When it does not, Python stops the program, and the
            message `KeyError: 'language'` names the key that it could not find. (This example stops with
            the error on purpose.)

            ### Ask first

            You know `in` from lists. On a dict, it asks whether a key exists:

            ```python
            settings = {"theme": "dark"}
            print("theme" in settings)
            # True
            print("language" in settings)
            # False
            print("dark" in settings)
            # False
            ```

            The last line is `False` because, on a dict, `in` looks at the keys and never at the values.

            With `in` and an `if` you could choose a fallback for a missing key. That takes four lines for
            one value, so dicts offer a shorter way.

            ### Read with a fallback

            You met `.get` in the first step of this chapter. Its second argument is the value to hand back
            when the key is missing:

            ```python
            settings = {"theme": "dark", "volume": 0}
            print(settings.get("language", "en"))
            # en
            print(settings.get("volume", 5))
            # 0
            ```

            `"language"` is missing, so `.get` hands back `"en"`. `"volume"` is there, so `.get` hands back
            the stored value and ignores the 5. That the stored value is 0 makes no difference, because
            `.get` only asks whether the key exists. The second argument is called the **default value**,
            or the **default** for short.

            Pick the line that makes this program print `free`:

            ```fill
            user = {"name": "Ada"}
            print(___)
            ---
            - [x] user.get("plan", "free") :: Right. The dict has no key `"plan"`, so `.get` hands back the default.
            - [ ] user["plan"] :: Square brackets need the key to exist. Python stops with `KeyError: 'plan'`.
            - [ ] user.get("plan") :: With no second argument, `.get` hands back `None` for a missing key, so the program prints `None`.
            ```

            ### Not the same as `or`

            In the Conditionals chapter you wrote a fallback as `value or fallback`. Here it does not do the
            same job:

            ```predict
            limits = {"retries": 0}
            print(limits.get("retries", 3))
            print(limits.get("retries") or 3)
            print(limits.get("timeout", 30))
            ---
            The key `"retries"` exists, so the first line prints the stored 0. In the second line `.get`
            finds that 0 as well, but 0 is falsy, so `or` drops it and hands back 3. The key `"timeout"` is
            missing, so the third line prints the default, 30.
            ```

            **Watch out:** `d.get(key) or default` replaces every falsy value, such as `0`, `""` and
            `False`, even when it was stored on purpose. `d.get(key, default)` uses the default only when
            the key is missing.

            **In short:** `d[key]` stops with a `KeyError` when the key is missing, and
            `d.get(key, default)` hands back the default.
        ''',
        "title": "Fix the missing key crash",
        "difficulty": 0,
        "prompt": r'''
            A setting called the temperature steers how much a model varies its answers. A request may set
            it. When a request does not, the model works with a temperature of `1.0`. The function below
            should read the temperature from a dict of settings. It works when the key is there. When the
            key is missing, it stops with a `KeyError`.

            **Your job:** fix `get_temperature(config)` so that a dict without a temperature gives `1.0`.
            The code is already in the editor.

            **What goes in**
            - `config`: a dict of settings, for example `{"temperature": 0.2}` or `{"model": "gpt-4o"}`.
              The key `"temperature"` may be in it, or not.

            **What comes out**
            - the value that is stored under `"temperature"`, or `1.0` when the dict has no such key

            **Rules**
            - When the key is there, its value comes back as it is. That holds for `0` as well. A
              temperature of 0 is a real setting, and it must not turn into `1.0`.
            - When the key is missing, the result is `1.0`, and there is no error.

            **Examples**
            ```python
            get_temperature({"temperature": 0.2})   # returns 0.2
            get_temperature({"temperature": 0})     # returns 0
            get_temperature({"model": "gpt-4o"})    # returns 1.0
            ```
        ''',
        "starter": r'''
            def get_temperature(config):
                return config["temperature"]
        ''',
        "tests": r'''
            from solution import get_temperature

            def test_present_key_returns_its_value():
                got = get_temperature({"temperature": 0.2})
                assert got == 0.2, f"got {got!r}"

            def test_zero_temperature_is_kept():
                got = get_temperature({"temperature": 0})
                assert got == 0, f"got {got!r}"

            def test_missing_key_returns_1_0():
                got = get_temperature({"model": "gpt-4o"})
                assert got == 1.0, f"got {got!r}"
        ''',
        "solution": r'''
            def get_temperature(config):
                return config.get("temperature", 1.0)
        ''',
        "hints": [
            "Square brackets stop the program when the key is missing. Which way of reading in the lesson does not?",
            "Read the key with the method that takes a second argument: the value to hand back when the key is not in the dict. Do not build the fallback with `or`, because that would replace a stored 0 as well.",
            "Keep the `return`. After it, replace the lookup in square brackets with a call of that method on the dict. The first argument is the key, and the second argument is the fallback that the task names.",
        ],
    },
    {
        "id": "dicts-s5",
        "lesson": r'''
            ## Going through every pair

            At the end of the month your app prints a bill: one line for each model, with the number of
            tokens that it used. The numbers are in a dict, with the names of the models as keys. A `for`
            loop visits every item of a list, and it can go through a dict as well.

            ```python
            tokens = {"mini": 1200, "large": 300}
            for name in tokens:
                print(name)
            # mini
            # large
            ```

            A loop over a dict gives you the keys, one per iteration, in the order in which the pairs were
            added. With the key you could look up the value in the body, as `tokens[name]`.

            ### The key and the value together

            Most of the time you want both. `tokens.items()` hands the loop one pair per iteration: a key
            and its value. Two loop variables unpack that pair, the way they did with `enumerate` in the
            Loops chapter. The first one gets the key and the second one gets the value.

            ```python
            tokens = {"mini": 1200, "large": 300}
            total = 0
            for name, count in tokens.items():
                print(f"{name}: {count}")
                total += count
            print(total)
            # mini: 1200
            # large: 300
            # 1500
            ```

            Press Next and watch `name` and `count` change on each iteration:

            ```diagram
            {"type": "trace", "title": "Looping over tokens.items()", "code": ["tokens = {\"mini\": 1200, \"large\": 300}", "total = 0", "for name, count in tokens.items():", "    print(f\"{name}: {count}\")", "    total += count", "print(total)"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 2, "vars": {"tokens": "{'mini': 1200, 'large': 300}"}, "out": ""},
              {"line": 3, "vars": {"tokens": "{'mini': 1200, 'large': 300}", "total": "0"}, "out": ""},
              {"line": 4, "vars": {"tokens": "{'mini': 1200, 'large': 300}", "total": "0", "name": "'mini'", "count": "1200"}, "out": ""},
              {"line": 5, "vars": {"tokens": "{'mini': 1200, 'large': 300}", "total": "0", "name": "'mini'", "count": "1200"}, "out": "mini: 1200\n"},
              {"line": 3, "vars": {"tokens": "{'mini': 1200, 'large': 300}", "total": "1200", "name": "'mini'", "count": "1200"}, "out": "mini: 1200\n"},
              {"line": 4, "vars": {"tokens": "{'mini': 1200, 'large': 300}", "total": "1200", "name": "'large'", "count": "300"}, "out": "mini: 1200\n"},
              {"line": 5, "vars": {"tokens": "{'mini': 1200, 'large': 300}", "total": "1200", "name": "'large'", "count": "300"}, "out": "mini: 1200\nlarge: 300\n"},
              {"line": 3, "vars": {"tokens": "{'mini': 1200, 'large': 300}", "total": "1500", "name": "'large'", "count": "300"}, "out": "mini: 1200\nlarge: 300\n"},
              {"line": 6, "vars": {"tokens": "{'mini': 1200, 'large': 300}", "total": "1500", "name": "'large'", "count": "300"}, "out": "mini: 1200\nlarge: 300\n"},
              {"line": null, "vars": {"tokens": "{'mini': 1200, 'large': 300}", "total": "1500", "name": "'large'", "count": "300"}, "out": "mini: 1200\nlarge: 300\n1500\n"}
            ]}
            ```

            The body is an ordinary loop body, so the accumulators from the Loops chapter work in it. The
            next program should print `['pads']`, the list of the things that have run out. Put its lines in
            order:

            ```order
            stock = {"pens": 4, "pads": 0}
            empty = []
            for item, count in stock.items():
                if count == 0:
                    empty.append(item)
            print(empty)
            ---
            The dict and the empty list have to exist before the loop. The `if` stands in the body, so it is checked for every pair, and the `append` under it runs only for a count of 0. The `print` comes after the loop.
            ```

            There is a third way to loop. `tokens.values()` gives the values alone, without the keys.

            ```predict
            ages = {"Ada": 36, "Bo": 41}
            for x in ages:
                print(x)
            for x in ages.values():
                print(x)
            ---
            A loop over the dict itself gives the keys, so the first loop prints `Ada` and `Bo`. `.values()`
            gives only the values, so the second loop prints 36 and 41.
            ```

            **Watch out:** without `.items()`, the loop gets only a key. `for name, count in tokens:` stops
            with `ValueError: too many values to unpack (expected 2)`, because Python tries to split the
            characters of the key `"mini"` between the two variables.

            **In short:** `for key, value in d.items():` runs its body once for each pair, with the key and
            the value in two loop variables.
        ''',
        "title": "Config as lines",
        "difficulty": 0,
        "prompt": r'''
            When a call to a model goes wrong, it helps to see the settings that were sent with it. Programs
            write such notes into a log, a plain text file in which they record what they did. For the log,
            each setting becomes one short piece of text of the form `key=value`.

            **Your job:** write `config_lines(config)` so that it gives back those pieces of text as a list.

            **What goes in**
            - `config`: a dict of settings, for example `{"model": "gpt-4o", "temperature": 0.7}`. It may
              be empty.

            **What comes out**
            - a list of strings, one for each pair of the dict: `["model=gpt-4o", "temperature=0.7"]` for
              the example value

            **Rules**
            - Each string is the key, then the sign `=`, then the value. There are no spaces around the `=`.
            - The strings stand in the same order as the pairs in the dict.
            - An empty dict gives the empty list `[]`.

            **Examples**
            ```python
            config_lines({"model": "gpt-4o", "temperature": 0.7})
            # returns ["model=gpt-4o", "temperature=0.7"]
            config_lines({"b": 1, "a": 2})   # returns ["b=1", "a=2"]
            config_lines({})                 # returns []
            ```
        ''',
        "starter": r'''
            def config_lines(config):
                ...
        ''',
        "tests": r'''
            from solution import config_lines

            def test_two_keys_give_two_key_equals_value_lines():
                got = config_lines({"model": "gpt-4o", "temperature": 0.7})
                assert got == ["model=gpt-4o", "temperature=0.7"], f"got {got!r}"

            def test_empty_dict_returns_empty_list():
                assert config_lines({}) == []

            def test_lines_follow_dict_key_order():
                got = config_lines({"b": 1, "a": 2})
                assert got == ["b=1", "a=2"], f"got {got!r}"
        ''',
        "solution": r'''
            def config_lines(config):
                lines = []
                for key, value in config.items():
                    lines.append(f"{key}={value}")
                return lines
        ''',
        "hints": [
            "The lesson shows a loop that gives you the key and the value of each pair together. How does a list grow inside a loop?",
            "Start with an empty list. For every pair of the dict, build one string from the key, the `=` sign and the value, and add that string to the list.",
            "Create the empty list before the loop. Loop over the pairs of the dict with two loop variables. In the body, append an f-string that holds the key, then `=`, then the value, with each of the two in curly braces. After the loop, hand the list back.",
        ],
    },
    {
        "id": "dicts-7",
        "lesson": r'''
            ## Follow a path to the value you need

            A tool returns more than one piece of information: its name, a result, and perhaps a list of sources. You want one source title, but the outer dictionary does not have a title key. You need to open the containers in order.

            ```python
            result = {"sources": [{"title": "Guide"}, {"title": "FAQ"}]}
            sources = result["sources"]
            first = sources[0]
            print(first["title"])
            # Guide
            ```

            The first lookup gives you a list. Position zero gives you a dictionary inside that list. Only then can you read its title. Dictionaries and lists inside other containers are called **nested data**. At each step, ask what kind of value you have now: a list needs a number; a dictionary needs a key.

            ```fill
            result = {"sources": [{"title": "Guide"}, {"title": "FAQ"}]}
            print(result["sources"][___]["title"])
            ---
            - [x] 1 :: Position one selects the second source, whose title is FAQ.
            - [ ] 0 :: Position zero selects Guide instead.
            - [ ] "title" :: This part is still a list, so a text key cannot select an item.
            ```

            You can put the brackets next to each other, because each lookup uses the value returned by the preceding one. This saves names but does not change the order of the work. When a longer path is confusing, split it into separate assignments again and print the intermediate values.

            ```predict
            record = {"stats": {"pages": 6}}
            print(record["stats"]["pages"])
            ---
            The outer lookup selects a dictionary. The inner lookup selects its page count.
            ```

            **Watch out:** `TypeError: list indices must be integers or slices, not str` means you tried a dictionary-style key while still looking at a list.

            The useful habit is to follow the data one container at a time.
        ''',
        "title": "Reply text from a response",
        "difficulty": 1,
        "prompt": r'''
            A chat-completion API returns nested data. You need the text of the reply.

            ```python
            response = {
                "id": "resp_1",
                "choices": [
                    {"message": {"role": "assistant", "content": "Paris."}, "finish_reason": "stop"},
                ],
            }
            ```

            **Your job:** write `reply_text(response)`

            **What goes in**
            - `response`: a dict shaped like the one above. It always has a `"choices"` list
              with at least one item, and each item has a `"message"` dict with a `"content"`.

            **What comes out**
            - the `"content"` string of the message in the **first** choice

            **Rules**
            - If there are several choices, use only the first one.
            - Don't change the response.

            **Examples**
            ```python
            reply_text(response)   # returns "Paris."
            reply_text({"choices": [{"message": {"content": "A"}}, {"message": {"content": "B"}}]})
            # returns "A"
            ```

            An empty content string is returned as an empty string; do not replace it with a default.
        ''',
        "starter": r'''
            def reply_text(response):
                ...
        ''',
        "tests": r'''
            from solution import reply_text

            def resp(*texts):
                return {"id": "r", "choices": [{"message": {"role": "assistant", "content": t},
                                                "finish_reason": "stop"} for t in texts]}

            def test_returns_content_of_the_reply():
                got = reply_text(resp("Paris."))
                assert got == "Paris.", f"got {got!r}"

            def test_uses_only_the_first_choice():
                got = reply_text(resp("A", "B"))
                assert got == "A", f"got {got!r}"

            def test_empty_content_is_returned_as_is():
                got = reply_text(resp(""))
                assert got == "", f"got {got!r}"

            def test_response_not_modified():
                r = resp("x")
                reply_text(r)
                assert r == resp("x"), "the response was modified"
        ''',
        "solution": r'''
            def reply_text(response):
                return response["choices"][0]["message"]["content"]
        ''',
        "hints": [
            "Look at the type of container at each level of the response.",
            "Find the list of choices, then the message belonging to its first item.",
            "Read the content from that message and give it back unchanged, including an empty string.",
        ],
    },
    {
        "id": "dicts-1",
        "lesson": r'''
            ## Combine defaults with one request's choices

            Most requests use the same settings, but one caller wants a different limit. You need a combined dictionary for that request while keeping the defaults ready for the next caller. Changing the defaults themselves would let one request affect another.

            ```python
            usual = {"limit": 20, "language": "en"}
            chosen = {"limit": 5, "trace": True}
            request = usual | chosen
            print(request)
            # {'limit': 5, 'language': 'en', 'trace': True}
            print(usual)
            # {'limit': 20, 'language': 'en'}
            ```

            The vertical bar combines pairs into a new dictionary. This is the dictionary **merge operator**. Both dictionaries contribute their keys. When they share a key, the value on the right wins. A zero or `False` is still a real replacement value; merging does not skip it.

            ```predict
            left = {"enabled": True, "limit": 8}
            right = {"enabled": False}
            print((left | right)["enabled"])
            print(left["enabled"])
            ---
            The combined dictionary takes False from the right. The original left dictionary still contains True.
            ```

            Earlier you changed individual values using assignment. The method `update` changes an existing dictionary with several pairs at once. That is a change **in place**, meaning the original object changes. Use it only when later code should see the edited dictionary.

            ```quiz
            Which operation protects the original defaults?
            - [x] Build a new dictionary with the request's choices on the right. :: The new dictionary receives the replacements while the defaults stay available.
            - [ ] Update the defaults themselves for each request. :: The changed settings would remain for later callers.
            ```

            **Watch out:** reversing the dictionaries makes the defaults win. The program may run without an error but quietly ignore the caller's choices.

            Keep the shared defaults unchanged and give each request its own combined settings.
        ''',
        "hints": [
            "Remember which side wins when dictionaries are merged.",
            "Combine the shared settings and request choices into a separate dictionary.",
            "Keep every default unless the caller supplies the same key; add new keys and return the combined result without editing either input.",
        ],
        "title": "Request defaults",
        "difficulty": 1,
        "prompt": r'''
            An API request starts from default settings, and the caller can override some
            of them. The starter already defines:

            ```python
            DEFAULTS = {"model": "gpt-4o-mini", "temperature": 0.7, "max_tokens": 256}
            ```

            **Your job:** write `build_request(overrides)`

            **What goes in**
            - `overrides`: a dict of settings to change or add, e.g. `{"temperature": 0}`

            **What comes out**
            - a **new** dict: all of `DEFAULTS`, with the `overrides` applied

            **Rules**
            - A key in `overrides` replaces the default value, even when the new value is
              `0`, `False` or another "empty" value.
            - Keys in `overrides` that are not in `DEFAULTS` are added to the result.
            - `overrides={}` returns a dict equal to `DEFAULTS`.
            - Don't modify `DEFAULTS`: a later call must still see the original defaults.
            - Don't modify the `overrides` dict you were given.

            **Examples**
            ```python
            build_request({"temperature": 0})
            # returns {"model": "gpt-4o-mini", "temperature": 0, "max_tokens": 256}
            build_request({"stream": True})
            # returns {"model": "gpt-4o-mini", "temperature": 0.7, "max_tokens": 256, "stream": True}
            build_request({})
            # returns {"model": "gpt-4o-mini", "temperature": 0.7, "max_tokens": 256}
            ```
        ''',
        "starter": r'''
            DEFAULTS = {"model": "gpt-4o-mini", "temperature": 0.7, "max_tokens": 256}


            def build_request(overrides):
                ...
        ''',
        "tests": r'''
            from solution import build_request

            def test_empty_overrides_return_the_defaults():
                got = build_request({})
                assert got == {"model": "gpt-4o-mini", "temperature": 0.7, "max_tokens": 256}, f"got {got!r}"

            def test_override_wins_even_when_falsy():
                got = build_request({"temperature": 0})
                assert got["temperature"] == 0, f"got {got!r}"
                assert got["model"] == "gpt-4o-mini" and got["max_tokens"] == 256, f"got {got!r}"

            def test_extra_override_keys_are_added():
                got = build_request({"stream": True})
                assert got.get("stream") is True and len(got) == 4, f"got {got!r}"

            def test_defaults_not_modified_between_calls():
                build_request({"model": "gpt-4o", "stream": True})
                got = build_request({})
                assert got == {"model": "gpt-4o-mini", "temperature": 0.7, "max_tokens": 256}, (
                    f"an earlier call leaked into the defaults: {got!r}")

            def test_overrides_dict_not_modified():
                overrides = {"model": "gpt-4o"}
                build_request(overrides)
                assert overrides == {"model": "gpt-4o"}, f"overrides changed to {overrides!r}"
        ''',
        "solution": r'''
            DEFAULTS = {"model": "gpt-4o-mini", "temperature": 0.7, "max_tokens": 256}


            def build_request(overrides):
                return DEFAULTS | overrides
        ''',
    },
    {
        "id": "dicts-8",
        "lesson": r'''
            ## Remove a value without damaging the original

            You want to display a request's settings in a log, but one field contains a secret. The request still needs that field. You therefore need two dictionaries: the original for the request and a cleaned version for the log.

            ```python
            account = {"name": "Mina", "password": "private"}
            public = account.copy()
            del public["password"]
            print(public)
            # {'name': 'Mina'}
            print("password" in account)
            # True
            ```

            Remember that assigning another name to a dictionary does not copy it. The `copy` method creates a new outer dictionary. Deleting a pair from that copy leaves the original pair alone. This is a **shallow copy**: values inside the dictionary are still shared objects, so this technique alone does not isolate changes inside nested lists or dictionaries.

            ```quiz
            Why would assigning `public = account` be a problem here?
            - [x] Both names would refer to the same dictionary. :: Deleting through either name would remove the original pair too.
            - [ ] Assignment would turn the dictionary into text. :: Assignment gives an object another name; it does not convert it.
            ```

            There is another detail to plan for: some requests may not contain the secret field at all. A plain deletion expects the key to exist. The dictionary documentation lists a removal method with an optional default for a missing key. Read that entry and check what the method returns as well as what it changes.

            ```match
            `copy()` :: makes a separate outer dictionary
            `del d[key]` :: removes an existing pair
            `key in d` :: checks whether a key exists
            ```

            **Watch out:** deleting an absent key raises `KeyError`. Decide how missing keys should behave before you choose the removal operation.

            Make a copy first when the original must keep its values.
        ''',
        "title": "Strip a secret before logging",
        "difficulty": 1,
        "research": {
            "note": "Dicts have a method that removes a key and can return a default instead of raising `KeyError` when the key is missing. Find it in the dict methods list, read what its second argument does, then come back.",
            "links": [
                {"title": "Mapping types - dict (Python docs)",
                 "url": "https://docs.python.org/3/library/stdtypes.html#mapping-types-dict"},
            ],
        },
        "prompt": r'''
            Request configs are logged for debugging, but secrets such as API keys must never
            end up in the logs.

            **Your job:** write `without_key(config, key)`

            **What goes in**
            - `config`: a flat dict, e.g. `{"model": "gpt-4o", "api_key": "sk-123"}`
            - `key`: the key to leave out, a string, e.g. `"api_key"`

            **What comes out**
            - a **new** dict with every pair of `config` except `key`

            **Rules**
            - If `key` is not in `config`, return a copy equal to `config` (no error).
            - Don't change the dict you were given - the real request still needs its key.
            - Always return a new dict object, even when nothing was removed.

            **Examples**
            ```python
            without_key({"model": "gpt-4o", "api_key": "sk-123"}, "api_key")
            # returns {"model": "gpt-4o"}
            without_key({"model": "gpt-4o"}, "api_key")
            # returns {"model": "gpt-4o"}
            without_key({}, "api_key")   # returns {}
            ```
        ''',
        "starter": r'''
            def without_key(config, key):
                ...
        ''',
        "tests": r'''
            from solution import without_key

            def test_removes_the_key():
                got = without_key({"model": "gpt-4o", "api_key": "sk-123"}, "api_key")
                assert got == {"model": "gpt-4o"}, f"got {got!r}"

            def test_missing_key_is_not_an_error():
                got = without_key({"model": "gpt-4o"}, "api_key")
                assert got == {"model": "gpt-4o"}, f"got {got!r}"
                assert without_key({}, "api_key") == {}

            def test_original_dict_keeps_its_key():
                config = {"model": "m", "api_key": "sk-1"}
                without_key(config, "api_key")
                assert config == {"model": "m", "api_key": "sk-1"}, f"the input changed to {config!r}"

            def test_returns_a_new_dict():
                config = {"model": "m"}
                got = without_key(config, "api_key")
                assert got is not config, "return a new dict, not the one you were given"
        ''',
        "solution": r'''
            def without_key(config, key):
                clean = config.copy()
                clean.pop(key, None)
                return clean
        ''',
        "hints": [
            "The real request must keep its secret; think about dictionary copies.",
            "Remove the requested key from a separate dictionary, allowing the key to be absent.",
            "Copy the input, use a removal operation with a missing-key fallback, and return the copy.",
        ],
    },
    {
        "id": "dicts-2",
        "lesson": r'''
            ## Keep a separate count for each name

            A log lists which tools were used, including repeated names. A single total tells you how many calls happened, but you also want a count for each tool. You do not know every possible tool name in advance.

            ```python
            names = ["lookup", "save", "lookup"]
            seen = {}
            for name in names:
                previous = seen.get(name, 0)
                seen[name] = previous + 1
            print(seen)
            # {'lookup': 2, 'save': 1}
            ```

            The dictionary stores one running total per name. Each pass reads that name's previous total, adds one, and saves it under the same key. The default zero handles the first appearance, when there is no pair yet. This is a **counting pattern**, combining the accumulator from the loops chapter with dictionary lookups.

            ```fill
            seen = {"lookup": 2}
            print(seen.get("save", ___) + 1)
            ---
            - [x] 0 :: A name never seen before starts at zero, so its first appearance makes one.
            - [ ] 1 :: Starting at one would count an appearance that never happened.
            - [ ] None :: None cannot be added to a number.
            ```

            Notice that the dictionary starts empty. Only names actually encountered become keys. With an empty input, the loop does no work and the dictionary stays empty. You do not need to invent zero entries for names that were never used.

            ```predict
            seen = {"lookup": 2}
            seen["lookup"] = seen.get("lookup", 0) + 1
            print(len(seen))
            print(seen["lookup"])
            ---
            Updating an existing key keeps one pair. Its stored count becomes three.
            ```

            **Watch out:** increasing a missing key directly raises `KeyError`, because Python must read the old count before it can add to it.

            Each appearance increases exactly one name's stored count.
        ''',
        "hints": [
            "You need one running count for each role name.",
            "For each message, increase the count stored under its role, starting unseen roles at zero.",
            "Begin with an empty dictionary, visit every message, update the appropriate count, and return the dictionary after all messages.",
        ],
        "title": "Count roles",
        "difficulty": 1,
        "prompt": r'''
            Count who said what in a chat history.

            **Your job:** write `count_roles(messages)`

            **What goes in**
            - `messages`: a list of message dicts like `{"role": "user", "content": "hi"}`

            **What comes out**
            - a dict mapping each role (string) to how many messages have that
              role (int), e.g. `{"system": 1, "user": 2}`

            **Rules**
            - Only roles that actually appear are keys - any role string counts (not only
              `"system"`, `"user"`, `"assistant"`).
            - An empty list returns `{}`.

            **Examples**
            ```python
            count_roles([
                {"role": "system", "content": "..."},
                {"role": "user", "content": "hi"},
                {"role": "assistant", "content": "hello"},
                {"role": "user", "content": "thanks"},
            ])
            # returns {"system": 1, "user": 2, "assistant": 1}
            count_roles([{"role": "tool", "content": "42"}])   # returns {"tool": 1}
            count_roles([])                                    # returns {}
            ```
        ''',
        "starter": r'''
            def count_roles(messages):
                ...
        ''',
        "tests": r'''
            from solution import count_roles

            def m(role):
                return {"role": role, "content": "x"}

            def test_counts_each_role_in_mixed_chat():
                got = count_roles([m("system"), m("user"), m("assistant"), m("user")])
                assert got == {"system": 1, "user": 2, "assistant": 1}, f"got {got!r}"

            def test_empty_list_returns_empty_dict():
                got = count_roles([])
                assert got == {}, f"got {got!r}"

            def test_five_user_messages_count_five():
                got = count_roles([m("user")] * 5)
                assert got == {"user": 5}, f"got {got!r}"

            def test_any_role_name_is_counted():
                got = count_roles([m("tool")])
                assert got == {"tool": 1}, f"got {got!r}"
        ''',
        "solution": r'''
            def count_roles(messages):
                counts = {}
                for message in messages:
                    role = message["role"]
                    counts[role] = counts.get(role, 0) + 1
                return counts
        ''',
    },
    {
        "id": "dicts-3",
        "hints": [
            "Separate the reply fields from the usage fields; they have different missing-data rules.",
            "Only read the first choice when one exists, and treat each absent usage count as zero.",
            "Prepare the two empty reply values, replace them when a first choice is available, total the usage counts, and return the three named fields.",
        ],
        "title": "Read an API response",
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            A chat-completion API returns nested data like this:

            ```python
            response = {
                "id": "resp_123",
                "choices": [
                    {"message": {"role": "assistant", "content": "Paris."},
                     "finish_reason": "stop"},
                ],
                "usage": {"prompt_tokens": 12, "completion_tokens": 3},
            }
            ```

            **Your job:** write `summarize(response)`

            **What goes in**
            - `response`: a dict shaped like the one above (parts may be missing, see Rules)

            **What comes out**
            - a new dict with exactly three keys:
              `{"text": ..., "finish_reason": ..., "total_tokens": ...}`

            **Rules**
            - `"text"` is the `"content"` of the `"message"` of the **first** choice, and
              `"finish_reason"` is that first choice's `"finish_reason"`. Ignore any other
              choices.
            - If the `"choices"` key is missing, or the list is empty, both `"text"` and
              `"finish_reason"` are `None`.
            - `"total_tokens"` is `"prompt_tokens"` + `"completion_tokens"` from `"usage"`.
            - If the `"usage"` key is missing, `"total_tokens"` is `0`. If only one of the two
              counts is missing, count the missing one as `0`.
            - Don't modify the `response` dict you were given.

            **Examples**
            ```python
            summarize(response)
            # returns {"text": "Paris.", "finish_reason": "stop", "total_tokens": 15}
            summarize({"id": "x", "choices": []})
            # returns {"text": None, "finish_reason": None, "total_tokens": 0}
            summarize({"id": "x", "usage": {"prompt_tokens": 4, "completion_tokens": 0}})
            # returns {"text": None, "finish_reason": None, "total_tokens": 4}
            ```
        ''',
        "starter": r'''
            def summarize(response):
                ...
        ''',
        "tests": r'''
            from solution import summarize

            def full():
                return {
                    "id": "resp_123",
                    "choices": [
                        {"message": {"role": "assistant", "content": "Paris."}, "finish_reason": "stop"},
                        {"message": {"role": "assistant", "content": "Lyon."}, "finish_reason": "length"},
                    ],
                    "usage": {"prompt_tokens": 12, "completion_tokens": 3},
                }

            def test_full_response_uses_first_choice_and_sums_tokens():
                got = summarize(full())
                assert got == {"text": "Paris.", "finish_reason": "stop", "total_tokens": 15}, f"got {got!r}"

            def test_empty_choices_and_no_usage_give_none_and_zero():
                got = summarize({"id": "x", "choices": []})
                assert got == {"text": None, "finish_reason": None, "total_tokens": 0}, f"got {got!r}"

            def test_missing_choices_key_gives_none():
                got = summarize({"id": "x", "usage": {"prompt_tokens": 4, "completion_tokens": 0}})
                assert got == {"text": None, "finish_reason": None, "total_tokens": 4}, f"got {got!r}"

            def test_missing_completion_tokens_counts_as_zero():
                r = full()
                del r["usage"]["completion_tokens"]
                got = summarize(r)
                assert got["total_tokens"] == 12, f"got {got!r}"

            def test_response_dict_not_modified():
                r = full()
                summarize(r)
                assert r == full(), "the response dict was modified"
        ''',
        "solution": r'''
            def summarize(response):
                choices = response.get("choices") or []
                text = finish_reason = None
                if choices:
                    first = choices[0]
                    text = first["message"]["content"]
                    finish_reason = first["finish_reason"]
                usage = response.get("usage", {})
                total = usage.get("prompt_tokens", 0) + usage.get("completion_tokens", 0)
                return {"text": text, "finish_reason": finish_reason, "total_tokens": total}
        ''',
    },
    {
        "id": "dicts-4",
        "hints": [
            "Each source needs its own growing list of text.",
            "Create a new list when a source first appears, then keep adding its text in input order.",
            "Start with an empty dictionary, visit the chunks in order, create only missing groups, append every text including duplicates, and return the groups.",
        ],
        "title": "Group chunks by source",
        "difficulty": 2,
        "prompt": r'''
            In a RAG app, retrieved chunks arrive as one flat list. Group them by the
            document they came from.

            **Your job:** write `group_by_source(chunks)`

            **What goes in**
            - `chunks`: a list of dicts like `{"source": "a.pdf", "text": "intro"}`

            **What comes out**
            - a dict mapping each source (string) to a **list of its texts**

            **Rules**
            - Inside each list, texts keep the order they had in `chunks`.
            - The keys are in order of first appearance in `chunks`.
            - Duplicate texts are kept (not removed).
            - Each source gets its own separate list: appending to one source's list must
              not change another's.
            - An empty list returns `{}`.

            **Examples**
            ```python
            group_by_source([
                {"source": "a.pdf", "text": "intro"},
                {"source": "b.md", "text": "setup"},
                {"source": "a.pdf", "text": "details"},
            ])
            # returns {"a.pdf": ["intro", "details"], "b.md": ["setup"]}
            group_by_source([
                {"source": "a", "text": "same"},
                {"source": "a", "text": "same"},
            ])
            # returns {"a": ["same", "same"]}
            group_by_source([])   # returns {}
            ```
        ''',
        "starter": r'''
            def group_by_source(chunks):
                ...
        ''',
        "tests": r'''
            from solution import group_by_source

            def c(source, text):
                return {"source": source, "text": text}

            def test_texts_grouped_by_source_in_order():
                got = group_by_source([c("a.pdf", "intro"), c("b.md", "setup"), c("a.pdf", "details")])
                assert got == {"a.pdf": ["intro", "details"], "b.md": ["setup"]}, f"got {got!r}"

            def test_key_order_is_first_appearance():
                got = group_by_source([c("z", "1"), c("a", "2"), c("z", "3")])
                assert list(got) == ["z", "a"], f"keys in order {list(got)!r}"

            def test_empty_list_returns_empty_dict():
                assert group_by_source([]) == {}

            def test_each_source_has_its_own_list():
                got = group_by_source([c("a", "1"), c("b", "2")])
                got["a"].append("x")
                assert got["b"] == ["2"], "the lists for different sources are the same object"

            def test_duplicate_texts_kept():
                got = group_by_source([c("a", "same"), c("a", "same")])
                assert got == {"a": ["same", "same"]}, f"got {got!r}"
        ''',
        "solution": r'''
            def group_by_source(chunks):
                groups = {}
                for chunk in chunks:
                    groups.setdefault(chunk["source"], []).append(chunk["text"])
                return groups
        ''',
    },
    {
        "id": "dicts-5",
        "hints": [
            "Distinguish a replacement, a section merge, and a deletion request.",
            "Copy the base sections before processing overrides so later changes cannot reach either input.",
            "For each override, remove the key for None, combine section pairs when appropriate, or replace the value; handle None inside sections as deletion too.",
        ],
        "title": "Merge configs",
        "difficulty": 3,
        "prompt": r'''
            Combine a base model config with a user's overrides. Configs have **at most two
            levels**: each top-level value is either a plain value or a dict of plain values
            (called a "section", e.g. `"params"`).

            **Your job:** write `merge_config(base, override)`

            **What goes in**
            - `base`: a config dict, e.g. `{"model": "gpt-4o", "params": {"temperature": 0.7}}`
            - `override`: a config dict with changes, e.g. `{"params": {"temperature": 0.2}}`

            **What comes out**
            - a **new** merged config dict

            **Rules**
            - Keys that are only in `base` or only in `override` are kept.
            - If a key's value is a dict in **both**, merge the two sections key by key
              (the `override` section's values win; other section keys are kept).
            - Otherwise the `override` value replaces the `base` value - this includes a
              plain value replacing a section, and a section replacing a plain value.
            - An `override` value of `None` **removes** that key from the result, at the top
              level or inside a section. A `None` key that isn't in `base` is simply left out.
              `None` override values act as deletion markers and are not stored in the result.
            - A section that exists only in `override` is copied without its `None` values.
            - Don't modify `base` or `override`.
            - The result must not share section dicts with the inputs: changing a section in
              the result must not change `base` or `override`.

            **Examples**
            ```python
            base = {"model": "gpt-4o", "params": {"temperature": 0.7, "top_p": 1.0},
                    "tools": ["search"]}
            override = {"params": {"temperature": 0.2, "top_p": None}, "stream": True}
            merge_config(base, override)
            # returns {"model": "gpt-4o", "params": {"temperature": 0.2},
            #          "tools": ["search"], "stream": True}
            merge_config({"a": 1, "b": 2}, {"a": None, "zzz": None})   # returns {"b": 2}
            merge_config({"a": {"x": 1}}, {"a": 5})                    # returns {"a": 5}
            merge_config({}, {"p": {"a": 1, "b": None}})               # returns {"p": {"a": 1}}
            ```
        ''',
        "starter": r'''
            def merge_config(base, override):
                ...
        ''',
        "tests": r'''
            import copy
            from solution import merge_config

            def sample():
                base = {"model": "gpt-4o", "params": {"temperature": 0.7, "top_p": 1.0},
                        "tools": ["search"]}
                override = {"params": {"temperature": 0.2, "top_p": None}, "stream": True}
                return base, override

            def test_example_config_is_merged():
                got = merge_config(*sample())
                expected = {"model": "gpt-4o", "params": {"temperature": 0.2},
                            "tools": ["search"], "stream": True}
                assert got == expected, f"got {got!r}"

            def test_sections_merge_key_by_key():
                got = merge_config({"p": {"a": 1, "b": 2}, "x": 0}, {"p": {"b": 20, "c": 3}})
                assert got == {"p": {"a": 1, "b": 20, "c": 3}, "x": 0}, f"got {got!r}"

            def test_none_removes_top_level_key():
                got = merge_config({"a": 1, "b": 2}, {"a": None, "zzz": None})
                assert got == {"b": 2}, f"got {got!r}"

            def test_new_section_drops_none_values():
                got = merge_config({}, {"p": {"a": 1, "b": None}})
                assert got == {"p": {"a": 1}}, f"got {got!r}"

            def test_plain_value_and_section_replace_each_other():
                got = merge_config({"a": {"x": 1}}, {"a": 5})
                assert got == {"a": 5}, f"got {got!r}"
                got = merge_config({"a": 5}, {"a": {"x": 1}})
                assert got == {"a": {"x": 1}}, f"got {got!r}"

            def test_base_and_override_not_modified():
                base, override = sample()
                b0, o0 = copy.deepcopy(base), copy.deepcopy(override)
                merge_config(base, override)
                assert base == b0, f"base was modified: {base!r}"
                assert override == o0, f"override was modified: {override!r}"

            def test_changing_result_sections_leaves_inputs_alone():
                base = {"params": {"temperature": 0.7}, "meta": {"user": "a"}}
                override = {"extra": {"k": 1}}
                got = merge_config(base, override)
                got["params"]["temperature"] = 99
                got["meta"]["user"] = "changed"
                got["extra"]["k"] = 99
                assert base == {"params": {"temperature": 0.7}, "meta": {"user": "a"}}, (
                    f"mutating the result changed base: {base!r}")
                assert override == {"extra": {"k": 1}}, f"mutating the result changed override: {override!r}"
        ''',
        "solution": r'''
            def merge_config(base, override):
                result = {}
                for key, value in base.items():
                    if isinstance(value, dict):
                        result[key] = value.copy()
                    else:
                        result[key] = value
                for key, value in override.items():
                    if value is None:
                        result.pop(key, None)
                    elif isinstance(value, dict):
                        if isinstance(result.get(key), dict):
                            section = result[key]
                        else:
                            section = {}
                        for inner_key, inner_value in value.items():
                            if inner_value is None:
                                section.pop(inner_key, None)
                            else:
                                section[inner_key] = inner_value
                        result[key] = section
                    else:
                        result[key] = value
                return result
        ''',
    },
    {
        "id": "dicts-6",
        "hints": [
            "Keep each user's totals and model counts separate.",
            "Collect usage first, then choose a winning model from each user's completed counts.",
            "Create a fresh entry per user, add every record with missing tokens treated as zero, then compare models by token count and use alphabetical order for ties.",
        ],
        "title": "Per-user usage report",
        "difficulty": 3,
        "prompt": r'''
            Build a per-user token usage report from API usage records.

            **Your job:** write `usage_report(records)`

            **What goes in**
            - `records`: a list of dicts like `{"user": "ana", "model": "gpt-4o", "tokens": 120}`

            **What comes out**
            - a dict keyed by user name; each value is a dict with exactly three
              keys:

            ```python
            {
                "ana": {
                    "total": 450,
                    "by_model": {"gpt-4o": 120, "gpt-4o-mini": 330},
                    "top_model": "gpt-4o-mini",
                },
                ...
            }
            ```

            **Rules**
            - A record without a `"tokens"` key counts as `0` tokens (its model still appears
              in `by_model`, with `0`).
            - `"total"`: the sum of all that user's tokens.
            - `"by_model"`: for that user, model name -> sum of tokens (several records for
              the same model are added together).
            - Each user has their own `by_model` dict.
            - `"top_model"`: the model with the most tokens for that user. On a tie, pick
              the model name that comes first alphabetically (`"alpha"` before `"zeta"`).
            - An empty list returns `{}`.

            **Examples**
            ```python
            usage_report([
                {"user": "ana", "model": "gpt-4o", "tokens": 120},
                {"user": "ana", "model": "gpt-4o-mini", "tokens": 330},
                {"user": "bo", "model": "gpt-4o"},
            ])
            # returns {"ana": {"total": 450, "by_model": {"gpt-4o": 120, "gpt-4o-mini": 330},
            #                  "top_model": "gpt-4o-mini"},
            #          "bo": {"total": 0, "by_model": {"gpt-4o": 0}, "top_model": "gpt-4o"}}
            usage_report([
                {"user": "a", "model": "zeta", "tokens": 50},
                {"user": "a", "model": "alpha", "tokens": 50},
            ])
            # returns {"a": {"total": 100, "by_model": {"zeta": 50, "alpha": 50},
            #                "top_model": "alpha"}}
            usage_report([])   # returns {}
            ```
        ''',
        "starter": r'''
            def usage_report(records):
                ...
        ''',
        "tests": r'''
            from solution import usage_report

            def r(user, model, tokens=None):
                d = {"user": user, "model": model}
                if tokens is not None:
                    d["tokens"] = tokens
                return d

            def test_example_report_with_missing_tokens():
                got = usage_report([r("ana", "gpt-4o", 120), r("ana", "gpt-4o-mini", 330), r("bo", "gpt-4o")])
                expected = {
                    "ana": {"total": 450, "by_model": {"gpt-4o": 120, "gpt-4o-mini": 330},
                            "top_model": "gpt-4o-mini"},
                    "bo": {"total": 0, "by_model": {"gpt-4o": 0}, "top_model": "gpt-4o"},
                }
                assert got == expected, f"got {got!r}"

            def test_same_model_tokens_are_added_up():
                got = usage_report([r("ana", "m1", 10), r("ana", "m1", 15), r("ana", "m2", 20)])
                assert got["ana"]["by_model"] == {"m1": 25, "m2": 20}, f"got {got!r}"
                assert got["ana"]["top_model"] == "m1", f"got {got!r}"
                assert got["ana"]["total"] == 45

            def test_each_user_has_separate_by_model():
                got = usage_report([r("a", "m1", 5), r("b", "m1", 7)])
                assert got["a"]["by_model"] == {"m1": 5}, f"got {got!r}"
                assert got["b"]["by_model"] == {"m1": 7}, f"got {got!r}"
                assert got["a"]["by_model"] is not got["b"]["by_model"]

            def test_top_model_tie_picks_alphabetically_first():
                got = usage_report([r("a", "zeta", 50), r("a", "alpha", 50), r("a", "mid", 10)])
                assert got["a"]["top_model"] == "alpha", f"got {got['a']['top_model']!r}"
                got = usage_report([r("a", "beta", 0), r("a", "alpha", 0)])
                assert got["a"]["top_model"] == "alpha", f"got {got['a']['top_model']!r}"

            def test_empty_list_returns_empty_dict():
                assert usage_report([]) == {}
        ''',
        "solution": r'''
            def usage_report(records):
                report = {}
                for record in records:
                    tokens = record.get("tokens", 0)
                    entry = report.setdefault(record["user"], {"total": 0, "by_model": {}})
                    entry["total"] += tokens
                    by_model = entry["by_model"]
                    by_model[record["model"]] = by_model.get(record["model"], 0) + tokens
                for entry in report.values():
                    best = None
                    for model, tokens in entry["by_model"].items():
                        if best is None or tokens > entry["by_model"][best] or (
                                tokens == entry["by_model"][best] and model < best):
                            best = model
                    entry["top_model"] = best
                return report
        ''',
    },
]
