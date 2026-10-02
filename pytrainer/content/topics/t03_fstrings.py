TOPIC = {
    "id": "fstrings",
    "title": "F-Strings & Formatting",
    "track": "foundations",
    "order": 4,
    "requires": ["data-types"],
    "summary": """
        Building text with f-strings: format specs for width, alignment, padding,
        decimals, thousands separators and percentages, the `=` debug specifier,
        multi-line strings and aligned text reports.
    """,
    "concepts": ["f-strings", "format spec", "width", "alignment", "zero padding",
                 "decimals", "thousands separator", "percent", "= specifier",
                 "nested format specs", "multi-line strings", "text tables"],
}

# The Library card for this chapter (shown once the chapter's steps are done).
# Every line that starts with `#` in an example is the real output of that example.
REFERENCE = {
    "keywords": ["f-string", "fstring", "format", "formatting", "placeholder", "curly braces",
                 "format spec", "decimals", "round", "width", "align", "padding", "percent",
                 "thousands separator", "newline", "debug"],
    "cards": [
        {
            "syntax": 'f"text {expression}"',
            "explain": "Python evaluates the code in the braces and inserts the result as text. Without the f, the braces stay.",
            "example": r'''
                model = "gpt-4o"
                tokens = 512
                print(f"{model} used {tokens * 2} tokens")
                # gpt-4o used 1024 tokens
                print("{model}")
                # {model}
            ''',
        },
        {
            "syntax": 'f"{value:.2f}"',
            "explain": "Shows a number with exactly 2 digits after the decimal point, rounded. The variable keeps its value.",
            "example": r'''
                cost = 0.126
                print(f"${cost:.2f}")
                # $0.13
                print(f"{3:.2f}")
                # 3.00
            ''',
        },
        {
            "syntax": 'f"{value:,}"  /  f"{value:.1%}"',
            "explain": "The comma spec adds a comma between groups of three digits. The % spec multiplies by 100 and adds a % sign.",
            "example": r'''
                tokens = 128000
                rate = 0.873
                print(f"{tokens:,}")
                # 128,000
                print(f"{rate:.1%}")
                # 87.3%
            ''',
        },
        {
            "syntax": 'f"{value:<10}"  /  f"{value:>10}"',
            "explain": "Pads with spaces to at least 10 characters. < puts the value on the left, > puts it on the right.",
            "example": r'''
                name = "gpt-4o"
                print(f"[{name:<10}]")
                # [gpt-4o    ]
                print(f"[{name:>10}]")
                # [    gpt-4o]
                print(f"{42:05}")
                # 00042
            ''',
        },
        {
            "syntax": 'f"{name=}"',
            "explain": "Inserts the text of the expression, an equals sign and the value. Strings are shown with quotes.",
            "example": r'''
                model = "gpt-4o"
                latency = 0.3456
                print(f"{model=} {latency=:.2f}")
                # model='gpt-4o' latency=0.35
            ''',
        },
        {
            "syntax": 'f"line one\\nline two"',
            "explain": "A backslash and n inside a string are the newline character. The output continues on a new line.",
            "example": r'''
                model = "gpt-4o"
                card = f"Model: {model}\nTokens: {128000:,}"
                print(card)
                # Model: gpt-4o
                # Tokens: 128,000
            ''',
        },
    ],
}

LESSON = r'''
## Chapter notes: F-Strings & Formatting

### F-strings

An **f-string** is a string written with the letter `f` directly before the opening quote.
Each `{...}` inside it is a **placeholder**. Python evaluates the code inside the braces,
converts the result to text and inserts that text where the braces are.

```python
model = "gpt-4o"
tokens = 512
print(f"{model} used {tokens} tokens")
# gpt-4o used 512 tokens
print(f"{tokens * 2}")
# 1024
print("{model}")
# {model}
```

The braces can hold any **expression**: code that produces a value. The last string has no
`f`, so Python prints the braces as ordinary characters.

### Format specs

A **format spec** is the text after a colon inside the braces. It tells Python how to convert
the value to text. The value comes first, then the colon, then the spec.

```python
cost = 0.126
print(f"cost: ${cost:.2f}")
# cost: $0.13
print(cost)
# 0.126
```

Click each stage to see what Python does with `f"cost: ${cost:.2f}"`.

```diagram
{"type":"flow","title":"How Python evaluates f\"cost: ${cost:.2f}\"","steps":[
  {"label":"Split the f-string","detail":"Python separates the literal text from the placeholder. Text outside the braces is kept unchanged.","code":"literal text: cost: $\nplaceholder:  {cost:.2f}"},
  {"label":"Evaluate the expression","detail":"The part before the colon is the expression. Python evaluates cost and gets the float 0.126.","code":"cost  ->  0.126"},
  {"label":"Apply the format spec","detail":"The part after the colon is the format spec. The spec .2f converts the float to text with 2 digits after the decimal point, rounded.","code":"0.126 with .2f  ->  '0.13'"},
  {"label":"Insert the text","detail":"Python joins the literal text and the formatted text into one new string. The variable cost still holds 0.126.","code":"'cost: $0.13'"}
]}
```

### Number specs

`.2f` shows a number with 2 digits after the decimal point. `,` adds a comma between groups
of three digits. `.1%` multiplies by 100, shows 1 decimal and adds a `%` sign.

```python
price = 1.5
count = 128000
share = 0.4567
print(f"{price:.2f}")
# 1.50
print(f"{count:,}")
# 128,000
print(f"{share:.1%}")
# 45.7%
```

### Width and alignment

A whole number in the spec that does not follow a `.` is the **width**: the minimum number
of characters in the result.
Python adds spaces to reach the width. `<` puts the value on the left, `>` puts it on the
right. A `0` directly before the width pads a number with zeros. On a string, `.N` cuts the
text to `N` characters.

```python
name = "gpt-4o"
print(f"[{name:<10}]")
# [gpt-4o    ]
print(f"[{name:>10}]")
# [    gpt-4o]
print(f"{7:03}")
# 007
print(f"{name:.3}")
# gpt
```

### Spec order

The parts of a spec must appear in this order: `[fill][align][0][width][,][.precision][type]`.
Every part is optional. The **fill** is the character used for padding instead of a space.
The **precision** is the number after the `.`. The **type** is the last character, such as
`f` or `%`.

```python
tokens = 128000
cost = 0.126
print(f"{tokens:>10,}|")
#    128,000|
print(f"{cost:>8.2f}|")
#     0.13|
print(f"{tokens:*>10}|")
# ****128000|
```

A spec can contain its own placeholder. Python replaces the inner braces first, so the width
can come from a variable. With `width = 5`, the spec `0{width}` becomes `05`.

```python
width = 5
print(f"{42:0{width}}")
# 00042
```

### The = specifier

`{name=}` inserts the text of the expression, an equals sign and the value. Strings are shown
with quotes. A format spec can follow the `=`.

```python
model = "gpt-4o"
latency = 0.3456
print(f"{model=}")
# model='gpt-4o'
print(f"{latency=:.2f}")
# latency=0.35
```

### Newlines

`\n` inside a string is an **escape sequence**: a backslash followed by other characters
that together stand for one character. `\n` is the newline character. It ends the current
line of output. (`\\` is also an escape sequence. It stands for one backslash.)

```python
model = "gpt-4o"
tokens = 128000
card = f"Model: {model}\nTokens: {tokens:,}"
print(card)
# Model: gpt-4o
# Tokens: 128,000
print(len("a\nb"))
# 3
```

### Common mistakes

- Without the `f`, Python prints the braces as text: `"{model}"` prints `{model}`.
- `f"Model: model"` contains no placeholder. The name needs braces: `f"Model: {model}"`.
- `{.2f:price}` is a `SyntaxError`. The value comes first: `{price:.2f}`.
- A spec changes only the text that is produced. The variable keeps its value.
- The result is a string. `"1,000"` is text, so you cannot do arithmetic with it.
- Width is a minimum. A longer value is shown in full. Only `.N` on a string cuts text.
- `"a \n b"` keeps the spaces around the newline, so the lines are `"a "` and `" b"`.

Docs: [f-strings tutorial](https://docs.python.org/3/tutorial/inputoutput.html#formatted-string-literals),
[Format Specification Mini-Language](https://docs.python.org/3/library/string.html#format-specification-mini-language).
'''

EXERCISES = [
    {
        "id": "fstrings-s1",
        "lesson": r'''
            ## F-strings

            A **string literal** is text written between quotes in your code, such as `"hello"`. An
            **f-string** is a string literal with the letter `f` directly before the opening quote.
            Its full name is *formatted string literal*.

            Inside an f-string, a pair of curly braces `{}` is a **placeholder**. Python evaluates
            the code inside the braces, converts the result to text and inserts that text where the
            braces are.

            ```python
            model = "gpt-4o"
            tokens = 512
            print(f"{model} used {tokens} tokens")
            # gpt-4o used 512 tokens
            print(f"next call: {tokens * 2} tokens")
            # next call: 1024 tokens
            print("{model}")
            # {model}
            ```

            The braces can hold any **expression**: code that produces a value. Python calculates
            `tokens * 2` first, then inserts `1024`.

            The third string has no `f`. Python treats its braces as ordinary characters and prints
            them unchanged.

            Step through the code to see the output of each line.

            ```diagram
            {"type": "trace", "title": "Three print calls, one without the f", "code": ["model = \"gpt-4o\"", "tokens = 512", "print(f\"{model} used {tokens} tokens\")", "print(f\"next call: {tokens * 2} tokens\")", "print(\"{model}\")"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 2, "vars": {"model": "'gpt-4o'"}, "out": ""},
              {"line": 3, "vars": {"model": "'gpt-4o'", "tokens": "512"}, "out": ""},
              {"line": 4, "vars": {"model": "'gpt-4o'", "tokens": "512"}, "out": "gpt-4o used 512 tokens\n"},
              {"line": 5, "vars": {"model": "'gpt-4o'", "tokens": "512"}, "out": "gpt-4o used 512 tokens\nnext call: 1024 tokens\n"},
              {"line": null, "vars": {"model": "'gpt-4o'", "tokens": "512"}, "out": "gpt-4o used 512 tokens\nnext call: 1024 tokens\n{model}\n"}
            ]}
            ```

            Inserting values into a string this way is called **string interpolation**.
        ''',
        "title": "What gets printed?",
        "difficulty": 0,
        "mode": "predict",
        "prompt": r'''
            Read the code and type exactly what it prints.
        ''',
        "code": r'''
            model = "gpt-4o"
            tokens = 512
            print(f"{model} used {tokens} tokens")
            print("{model}")
            print(f"{tokens + 8}")
        ''',
        "solution": r'''
            gpt-4o used 512 tokens
            {model}
            520
        ''',
        "explanation": r'''
            Line 1 is an f-string, so `{model}` and `{tokens}` are replaced by their values.
            Line 2 has **no `f`**, so the braces are printed as plain text. Line 3 shows that
            any expression works inside the braces: `tokens + 8` is computed first (520).
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Check each string: does it start with the letter f before the quote?",
            "In an f-string, each {...} is replaced by the value of what is inside. Without the f, braces stay as text.",
            "Line 1: substitute gpt-4o and 512. Line 2: no f, so print it literally. Line 3: compute 512 + 8.",
        ],
    },
    {
        "id": "fstrings-s2",
        "lesson": r'''
            ## Prompt templates

            A **template** is a string with fixed text and one or more placeholders. A prompt
            is the text you send to an AI model. Most prompts are templates: the same sentence,
            with one part that changes.

            A **parameter** is a name in the parentheses of a function definition. It holds the
            value that is passed in when the function is called. An f-string inside a function can
            use a parameter in a placeholder. Python builds a new string on every call.

            ```python
            def greet(name):
                return f"Hello {name}, how can I help?"

            print(greet("Ada"))
            # Hello Ada, how can I help?
            print(greet("Linus"))
            # Hello Linus, how can I help?
            ```

            Python copies everything outside the braces exactly: every space, comma and full stop.
            Only the text inserted for `{name}` changes between calls.

            The string that the function returns is its **return value**. Building text from a
            template is called **string formatting**.

            The braces hold the variable name without quotes. With quotes, the expression is a
            string, so Python inserts the word itself.

            ```python
            name = "Ada"
            print(f"Hello {name}")
            # Hello Ada
            print(f"Hello {'name'}")
            # Hello name
            ```
        ''',
        "title": "Fill in the prompt",
        "difficulty": 0,
        "prompt": r'''
            A small helper that builds a prompt for a language model.

            **Write:** replace the `___` in `ask(topic)`

            - `topic`: a string, e.g. `"RAG"`
            - **Returns:** a string like `"Explain RAG in one sentence."`

            **Rules**
            - The value of `topic` must be inserted where the `___` is (inside an f-string, a
              variable goes inside curly braces).
            - Keep the rest of the text exactly as it is, including the final period.

            **Examples**
            ```python
            ask("RAG")         # returns "Explain RAG in one sentence."
            ask("embeddings")  # returns "Explain embeddings in one sentence."
            ```
        ''',
        "starter": r'''
            def ask(topic):
                return f"Explain ___ in one sentence."
        ''',
        "tests": r'''
            from solution import ask

            def test_inserts_rag_into_the_prompt():
                got = ask("RAG")
                assert got == "Explain RAG in one sentence.", f"got {got!r}"

            def test_inserts_embeddings_into_the_prompt():
                got = ask("embeddings")
                assert got == "Explain embeddings in one sentence.", f"got {got!r}"
        ''',
        "solution": r'''
            def ask(topic):
                return f"Explain {topic} in one sentence."
        ''',
        "hints": [
            "Inside an f-string, a variable is inserted with curly braces.",
            "Replace the three underscores with the parameter name wrapped in braces.",
            "The parameter is called topic, so the blank becomes {topic}. Keep the f and the rest of the text exactly as it is.",
        ],
    },
    {
        "id": "fstrings-s3",
        "lesson": r'''
            ## The f prefix

            A **prefix** is a letter written directly before the opening quote of a string literal.
            The `f` prefix is what makes Python evaluate the placeholders. Without it, the braces
            are ordinary characters.

            ```python
            model = "claude"
            print("{model} is ready")
            # {model} is ready
            print(f"{model} is ready")
            # claude is ready
            print(f'{model} is ready')
            # claude is ready
            ```

            The first string has no prefix, so Python prints the braces and the name as text. Python
            does not report an error for this. The string is valid, and the output is wrong.

            The `f` goes directly before the opening quote, with no space. `f "..."` is a
            `SyntaxError`. The prefix works the same way with single quotes: `f'...'`.

            When your output shows `{something}` with the braces, check first whether the `f`
            prefix is missing.
        ''',
        "title": "Fix the status line",
        "difficulty": 0,
        "prompt": r'''
            A status message for a model. It currently returns the braces as plain text.
            Find and fix the bug.

            **Write:** fix `status(model)`

            - `model`: a string, the model name, e.g. `"gpt-4o"`
            - **Returns:** a string: the model name, then ` is ready`

            **Rules**
            - The braces must be replaced by the value of `model` (not shown as `{model}`).
            - One space between the name and `is ready`, no period at the end.

            **Examples**
            ```python
            status("gpt-4o")   # returns "gpt-4o is ready"
            status("claude")   # returns "claude is ready"
            ```
        ''',
        "starter": r'''
            def status(model):
                return "{model} is ready"
        ''',
        "tests": r'''
            from solution import status

            def test_gpt_4o_is_ready():
                got = status("gpt-4o")
                assert got == "gpt-4o is ready", f"got {got!r}"

            def test_works_for_another_model_name():
                got = status("claude")
                assert got == "claude is ready", f"got {got!r}"
        ''',
        "solution": r'''
            def status(model):
                return f"{model} is ready"
        ''',
        "hints": [
            "Look at the start of the string. What makes Python treat braces as placeholders?",
            "Braces are only replaced in an f-string. This string is missing something before the quote.",
            "Add the letter f directly in front of the opening quote, with no space.",
        ],
    },
    {
        "id": "fstrings-s4",
        "lesson": r'''
            ## Two decimals

            Inside the braces, you can add a colon after the value and then a **format spec**
            (format specification). The format spec tells Python how to convert the value to text.

            The spec `.2f` shows a number with exactly 2 digits after the decimal point.

            ```python
            price = 1.5
            cost = 0.126
            text = f"{price:.2f}"
            print(text)
            # 1.50
            print(f"${cost:.2f}")
            # $0.13
            print(f"{3:.2f}")
            # 3.00
            print(price)
            # 1.5
            ```

            `.2f` has two parts. `.2` is the **precision**: the number of digits after the decimal
            point. `f` is the **type**: it shows the value as a decimal number with exactly that many
            digits after the point.

            Python rounds when the value has more digits, so `0.126` becomes `0.13`. Python adds
            zeros when the value has fewer digits, so `3` becomes `3.00`.

            Step through the code and compare `price` with `text`.

            ```diagram
            {"type": "trace", "title": "Formatting with .2f", "code": ["price = 1.5", "cost = 0.126", "text = f\"{price:.2f}\"", "print(text)", "print(f\"${cost:.2f}\")", "print(f\"{3:.2f}\")", "print(price)"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 2, "vars": {"price": "1.5"}, "out": ""},
              {"line": 3, "vars": {"price": "1.5", "cost": "0.126"}, "out": ""},
              {"line": 4, "vars": {"price": "1.5", "cost": "0.126", "text": "'1.50'"}, "out": "", "note": "text is a new string. price still holds the float 1.5."},
              {"line": 5, "vars": {"price": "1.5", "cost": "0.126", "text": "'1.50'"}, "out": "1.50\n"},
              {"line": 6, "vars": {"price": "1.5", "cost": "0.126", "text": "'1.50'"}, "out": "1.50\n$0.13\n"},
              {"line": 7, "vars": {"price": "1.5", "cost": "0.126", "text": "'1.50'"}, "out": "1.50\n$0.13\n3.00\n"},
              {"line": null, "vars": {"price": "1.5", "cost": "0.126", "text": "'1.50'"}, "out": "1.50\n$0.13\n3.00\n1.5\n"}
            ]}
            ```

            The value comes first, then the colon, then the spec: `{price:.2f}`. The spec changes
            only the text that is produced. The variable `price` still holds `1.5`.
        ''',
        "title": "Price with two decimals",
        "difficulty": 0,
        "prompt": r'''
            A price label for a billing page.

            **Write:** `price_label(price)`

            - `price`: a number (float or int), e.g. `1.5`
            - **Returns:** a string: `$` followed by the price with **exactly 2 decimals**

            **Rules**
            - Always 2 decimals, even for whole numbers (`3` becomes `"$3.00"`).
            - Round to 2 decimals (`0.126` becomes `"$0.13"`).
            - No space between `$` and the number.
            - Reminder of the syntax: inside an f-string, `{value:.2f}` shows `value` with 2 decimals.

            **Examples**
            ```python
            price_label(1.5)     # returns "$1.50"
            price_label(0.126)   # returns "$0.13"
            price_label(3)       # returns "$3.00"
            ```
        ''',
        "starter": r'''
            def price_label(price):
                ...
        ''',
        "tests": r'''
            from solution import price_label

            def test_one_decimal_gets_a_second_zero():
                got = price_label(1.5)
                assert got == "$1.50", f"got {got!r}"

            def test_rounds_to_two_decimals():
                got = price_label(0.126)
                assert got == "$0.13", f"got {got!r}"

            def test_whole_number_shows_two_zeros():
                got = price_label(3)
                assert got == "$3.00", f"got {got!r}"
        ''',
        "solution": r'''
            def price_label(price):
                return f"${price:.2f}"
        ''',
        "hints": [
            "Use an f-string with a format spec after a colon inside the braces.",
            "The $ is ordinary text before the braces; the braces hold the price plus a spec for 2 decimals.",
            "Write return, then an f-string that starts with $, then {price:.2f} as the placeholder.",
        ],
    },
    {
        "id": "fstrings-s5",
        "lesson": r'''
            ## Thousands separators

            A long number such as `1000000` is hard to read because you have to count the digits.
            A **thousands separator** is a character placed between groups of three digits, as in
            `1,000,000`.

            The format spec `,` tells Python to add a comma between each group of three digits.

            ```python
            context = 128000
            total = 1234567
            print(f"{context:,} tokens")
            # 128,000 tokens
            print(f"{total:,}")
            # 1,234,567
            print(f"{512:,}")
            # 512
            ```

            Python counts the groups from the right. A number below 1000 has only one group, so it
            gets no comma.

            The Python docs call this the **grouping** option of the format spec.

            The result is a string. `"128,000"` is text for people to read, and you cannot do
            arithmetic with it. Keep the original number in its variable for calculations.
        ''',
        "title": "Big numbers with commas",
        "difficulty": 0,
        "prompt": r'''
            A label showing a model's context window size.

            **Write:** `context_label(tokens)`

            - `tokens`: an integer, e.g. `128000`
            - **Returns:** a string: the number with commas between thousands, then a space and
              the word `tokens`

            **Rules**
            - Use a comma every 3 digits (`1000000` becomes `1,000,000`).
            - Numbers below 1,000 get no comma (`512`).
            - Reminder of the syntax: inside an f-string, `{value:,}` adds the commas.

            **Examples**
            ```python
            context_label(128000)    # returns "128,000 tokens"
            context_label(1000000)   # returns "1,000,000 tokens"
            context_label(512)       # returns "512 tokens"
            ```
        ''',
        "starter": r'''
            def context_label(tokens):
                ...
        ''',
        "tests": r'''
            from solution import context_label

            def test_thousands_get_a_comma():
                got = context_label(128000)
                assert got == "128,000 tokens", f"got {got!r}"

            def test_millions_get_two_commas():
                got = context_label(1000000)
                assert got == "1,000,000 tokens", f"got {got!r}"

            def test_small_number_has_no_comma():
                got = context_label(512)
                assert got == "512 tokens", f"got {got!r}"
        ''',
        "solution": r'''
            def context_label(tokens):
                return f"{tokens:,} tokens"
        ''',
        "hints": [
            "A format spec after a colon inside the braces can add thousands separators.",
            "Put tokens in braces with the comma spec, then the word tokens after it as plain text.",
            "Return an f-string: {tokens:,} followed by a space and the word tokens.",
        ],
    },
    {
        "id": "fstrings-s6",
        "lesson": r'''
            ## Percentages

            A **fraction** here means a number between 0 and 1, such as `0.873`. Code usually stores
            a rate as a fraction, and a report shows it as a percentage: `87.3%`.

            The `%` format spec does three things. It multiplies the value by 100, shows it with a
            fixed number of decimals and adds a `%` sign.

            ```python
            rate = 0.873
            print(f"{rate:.1%}")
            # 87.3%
            print(f"{0.5:.1%}")
            # 50.0%
            print(f"{1:.0%}")
            # 100%
            ```

            `.1%` means a percentage with 1 decimal. The number after the point is the precision,
            the same as in `.2f`. `.0%` shows no decimals.

            `%` is a **presentation type** in the format spec. `f` is another presentation type.

            Use the fraction as the value, not the percentage. Python always multiplies by 100, so
            `87.3` is shown as `8730.0%`.

            ```python
            print(f"{87.3:.1%}")
            # 8730.0%
            ```
        ''',
        "title": "Success rate",
        "difficulty": 0,
        "prompt": r'''
            A monitoring dashboard shows what share of API calls succeeded.

            **Write:** `success_label(rate)`

            - `rate`: a fraction between 0 and 1 (float or int), e.g. `0.873`
            - **Returns:** a string: the rate as a **percentage with 1 decimal**, a `%` sign,
              then a space and the word `success`

            **Rules**
            - The number is multiplied by 100 and rounded to 1 decimal (`0.873` shows as `87.3%`).
            - Always 1 decimal, even for whole percentages (`1` shows as `100.0%`).
            - Reminder of the syntax: inside an f-string, `{value:.1%}` does the conversion.

            **Examples**
            ```python
            success_label(0.873)   # returns "87.3% success"
            success_label(0.5)     # returns "50.0% success"
            success_label(1)       # returns "100.0% success"
            ```
        ''',
        "starter": r'''
            def success_label(rate):
                ...
        ''',
        "tests": r'''
            from solution import success_label

            def test_fraction_becomes_percentage_with_one_decimal():
                got = success_label(0.873)
                assert got == "87.3% success", f"got {got!r}"

            def test_half_shows_fifty_point_zero():
                got = success_label(0.5)
                assert got == "50.0% success", f"got {got!r}"

            def test_one_shows_one_hundred_percent():
                got = success_label(1)
                assert got == "100.0% success", f"got {got!r}"

            def test_zero_shows_zero_percent():
                got = success_label(0)
                assert got == "0.0% success", f"got {got!r}"
        ''',
        "solution": r'''
            def success_label(rate):
                return f"{rate:.1%} success"
        ''',
        "hints": [
            "A format spec ending in % turns a fraction into a percentage.",
            "Put rate in braces with a spec for a percentage with 1 decimal, then add the word success after it.",
            "Return an f-string: {rate:.1%} followed by a space and the word success. Don't multiply by 100 yourself.",
        ],
    },
    {
        "id": "fstrings-1",
        "lesson": r'''
            ## Newlines in a string

            One string can hold several lines. An **escape sequence** is a backslash followed by a
            character, and Python reads the pair as one special character. The escape sequence `\n`
            is the **newline character**. When Python prints it, the output continues on a new line.

            ```python
            model = "gpt-4o"
            temperature = 0.7
            card = f"Model: {model}\nTemperature: {temperature:.2f}"
            print(card)
            # Model: gpt-4o
            # Temperature: 0.70
            print(len("a\nb"))
            # 3
            ```

            `card` is one string, and `print` shows it as two lines. `len("a\nb")` is 3 because
            `\n` is written with two characters in the code and stored as one character in the
            string.

            Two other escape sequences are `\t`, the tab character, and `\\`, a single backslash.

            Python keeps the spaces around `\n`. `"a \n b"` gives the lines `"a "` and `" b"`.

            A `\n` at the very end of a string is one more character, and `print` shows an empty
            line after the text. Add it only when the task asks for it.
        ''',
        "title": "Model card",
        "difficulty": 1,
        "hints": [
            "You need an f-string, a newline character, and a format spec for decimals.",
            "Build one string with two parts: the model line, then \\n, then the temperature line with 2 decimals.",
            "Start with f\"Model: {model}, then add \\n, then Temperature: followed by {temperature:.2f}. Do not end with \\n.",
        ],
        "prompt": r'''
            A short "model card" shown in a chat app's settings panel.

            **Write:** `model_card(model, temperature)`

            - `model`: a string, the model name, e.g. `"gpt-4o"`
            - `temperature`: a number (float or int), e.g. `0.7`
            - **Returns:** one string made of **two lines** separated by a newline character `\n`

            **Rules**
            - Line 1 is `Model: ` followed by the model name.
            - Line 2 is `Temperature: ` followed by the temperature with **exactly 2 decimals**
              (rounded: `0.456` shows as `0.46`, `1` shows as `1.00`).
            - Exactly one `\n` (between the lines). No `\n` at the end.

            **Examples**
            ```python
            model_card("gpt-4o", 0.7)   # returns "Model: gpt-4o\nTemperature: 0.70"
            model_card("m", 1)          # returns "Model: m\nTemperature: 1.00"
            model_card("m", 0.456)      # returns "Model: m\nTemperature: 0.46"
            ```
            Printed, the first one looks like:
            ```
            Model: gpt-4o
            Temperature: 0.70
            ```
        ''',
        "starter": r'''
            def model_card(model, temperature):
                ...
        ''',
        "tests": r'''
            from solution import model_card

            def test_gpt_4o_card_matches_exactly():
                got = model_card("gpt-4o", 0.7)
                assert got == "Model: gpt-4o\nTemperature: 0.70", f"got {got!r}"

            def test_integer_temperature_gets_decimals():
                got = model_card("m", 1)
                assert got.splitlines()[-1] == "Temperature: 1.00", f"got {got!r}"

            def test_rounds_temperature():
                got = model_card("m", 0.456)
                assert got.splitlines()[-1] == "Temperature: 0.46", f"got {got!r}"

            def test_first_line_uses_the_model_name():
                got = model_card("claude", 0.5)
                assert got.splitlines()[0] == "Model: claude", f"got {got!r}"

            def test_exactly_two_lines_no_trailing_newline():
                got = model_card("m", 0.5)
                assert got.count("\n") == 1, f"expected exactly one newline, got {got!r}"
                assert not got.endswith("\n"), "the string should not end with a newline"
        ''',
        "solution": r'''
            def model_card(model, temperature):
                return f"Model: {model}\nTemperature: {temperature:.2f}"
        ''',
    },
    {
        "id": "fstrings-2",
        "lesson": r'''
            ## The = specifier

            To find a bug, you often print variables to see their values. A line of values such as
            `gpt-4o 512 0.35` does not show which value belongs to which variable. You could write
            `f"model={model}"` for each one. The **`=` specifier** is shorter: write `=` after the
            expression inside the braces.

            ```python
            model = "gpt-4o"
            tokens = 512
            latency = 0.3456
            print(f"{model=} {tokens=}")
            # model='gpt-4o' tokens=512
            print(f"{latency=:.2f}")
            # latency=0.35
            ```

            For `{model=}`, Python inserts the text of the expression, an equals sign and then the
            value.

            A string value is shown with quotes around it. The quotes make an empty string or a
            space at the end of a string visible.

            You can add a format spec. The `=` goes before the colon: `{latency=:.2f}`.

            The Python docs call a placeholder with `=` a **self-documenting expression**.
        ''',
        "title": "Debug line",
        "hints": [
            "The f-string = specifier, like {model=}, prints the name, an equals sign and the value.",
            "Use three placeholders separated by spaces, one per parameter, each with =. Latency also needs a 2-decimal spec after the =.",
            "Write {model=}, a space, {tokens=}, a space, then {latency=:.2f}. Note the = comes before the colon.",
        ],
        "difficulty": 1,
        "prompt": r'''
            A one-line debug log for an API call.

            **Write:** `debug_line(model, tokens, latency)`

            - `model`: a string, e.g. `"gpt-4o"`
            - `tokens`: an integer, e.g. `512`
            - `latency`: a number of seconds (float or int), e.g. `0.3456`
            - **Returns:** a string like `"model='gpt-4o' tokens=512 latency=0.35"`

            **Rules**
            - Three parts, in this order, separated by single spaces: `model=...`, `tokens=...`,
              `latency=...`.
            - The model name appears **with quotes** around it (`model='gpt-4o'`).
            - `latency` is shown with exactly 2 decimals (`2` shows as `2.00`).
            - You must use the f-string **`=` specifier** (a *self-documenting expression*: inside
              the braces, a name followed by `=`). A check looks for it in your code.

            **Examples**
            ```python
            debug_line("gpt-4o", 512, 0.3456)   # returns "model='gpt-4o' tokens=512 latency=0.35"
            debug_line("claude", 0, 2)          # returns "model='claude' tokens=0 latency=2.00"
            ```
        ''',
        "starter": r'''
            def debug_line(model, tokens, latency):
                ...
        ''',
        "tests": r'''
            from solution import debug_line

            def test_gpt_4o_line_matches_exactly():
                got = debug_line("gpt-4o", 512, 0.3456)
                assert got == "model='gpt-4o' tokens=512 latency=0.35", f"got {got!r}"

            def test_zero_tokens_and_whole_latency():
                got = debug_line("claude", 0, 2)
                assert got == "model='claude' tokens=0 latency=2.00", f"got {got!r}"

            def test_uses_the_equals_specifier():
                import re
                assert re.search(r"\{\s*\w+\s*=\s*[:}]", source()), "use the f-string = specifier, e.g. {name=}"
        ''',
        "solution": r'''
            def debug_line(model, tokens, latency):
                return f"{model=} {tokens=} {latency=:.2f}"
        ''',
    },
    {
        "id": "fstrings-7",
        "lesson": r'''
            ## Width and alignment

            A table is readable when every column has a fixed width. A whole number in a format
            spec that does not follow a `.` is the **width**: the minimum number of characters
            the result must have. Python
            adds spaces to reach the width. Those extra spaces are called **padding**.

            The **alignment** option decides where the padding goes. `<` left-aligns the value, so
            the spaces go after it. `>` right-aligns the value, so the spaces go before it.

            ```python
            name = "gpt-4o"
            tokens = 512
            print(f"[{name:<10}]")
            # [gpt-4o    ]
            print(f"[{name:>10}]")
            # [    gpt-4o]
            print(f"[{tokens:>6}]")
            # [   512]
            print(f"[{'a-very-long-name':<5}]")
            # [a-very-long-name]
            ```

            The square brackets are ordinary text that shows where the spaces are. `gpt-4o` has 6
            characters, so Python adds 4 spaces to reach 10.

            Step through the code and count the spaces in each output line.

            ```diagram
            {"type": "trace", "title": "Padding to a width", "code": ["name = \"gpt-4o\"", "tokens = 512", "print(f\"[{name:<10}]\")", "print(f\"[{name:>10}]\")", "print(f\"[{tokens:>6}]\")", "print(f\"[{'a-very-long-name':<5}]\")"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 2, "vars": {"name": "'gpt-4o'"}, "out": ""},
              {"line": 3, "vars": {"name": "'gpt-4o'", "tokens": "512"}, "out": ""},
              {"line": 4, "vars": {"name": "'gpt-4o'", "tokens": "512"}, "out": "[gpt-4o    ]\n"},
              {"line": 5, "vars": {"name": "'gpt-4o'", "tokens": "512"}, "out": "[gpt-4o    ]\n[    gpt-4o]\n"},
              {"line": 6, "vars": {"name": "'gpt-4o'", "tokens": "512"}, "out": "[gpt-4o    ]\n[    gpt-4o]\n[   512]\n"},
              {"line": null, "vars": {"name": "'gpt-4o'", "tokens": "512"}, "out": "[gpt-4o    ]\n[    gpt-4o]\n[   512]\n[a-very-long-name]\n"}
            ]}
            ```

            Width is a minimum. The last line has a 16-character value and a width of 5, and Python
            shows the value in full.

            Without an alignment option, Python left-aligns strings and right-aligns numbers.

            Width counts characters. `{name:<10}{tokens:>6}` produces 16 characters when both
            values fit.
        ''',
        "title": "Aligned usage cell",
        "difficulty": 1,
        "prompt": r'''
            A usage table in a terminal: model names on the left, token counts on the right,
            so that every row lines up.

            **Write:** `usage_cell(name, tokens)`

            - `name`: a string, the model name, e.g. `"gpt-4o"`
            - `tokens`: an integer, e.g. `512`
            - **Returns:** one string: `name` **left-aligned** in 10 characters, immediately
              followed by `tokens` **right-aligned** in 6 characters (16 characters in total
              when both fit)

            **Rules**
            - Padding is done with spaces.
            - Nothing between the two columns: the padding *is* the gap.
            - A name longer than 10 characters is shown **in full** (not cut); the number
              column still follows it directly.
            - No thousands separators.

            **Examples**
            ```python
            usage_cell("gpt-4o", 512)          # returns "gpt-4o       512"
            usage_cell("claude", 12000)        # returns "claude     12000"
            usage_cell("claude-3-opus", 42)    # returns "claude-3-opus    42"
            ```
        ''',
        "starter": r'''
            def usage_cell(name, tokens):
                ...
        ''',
        "tests": r'''
            from solution import usage_cell

            def test_short_name_and_number_line_up():
                got = usage_cell("gpt-4o", 512)
                assert got == "gpt-4o       512", f"got {got!r}"

            def test_five_digit_number():
                got = usage_cell("claude", 12000)
                assert got == "claude     12000", f"got {got!r}"

            def test_rows_are_16_characters_wide():
                a = usage_cell("a", 1)
                b = usage_cell("mistral", 99999)
                assert len(a) == len(b) == 16, f"rows have lengths {len(a)} and {len(b)}"

            def test_long_name_is_not_cut():
                got = usage_cell("claude-3-opus", 42)
                assert got == "claude-3-opus    42", f"got {got!r}"
        ''',
        "solution": r'''
            def usage_cell(name, tokens):
                return f"{name:<10}{tokens:>6}"
        ''',
        "hints": [
            "A format spec can set a width and an alignment: < for left, > for right.",
            "Use two placeholders right next to each other: the name with left alignment and width 10, then tokens with right alignment and width 6.",
            "Return an f-string with {name:<10} immediately followed by {tokens:>6}, with no space between the two placeholders.",
        ],
    },
    {
        "id": "fstrings-8",
        "lesson": r'''
            ## Reading the format spec reference

            You have used several format spec options: `.2f`, `,`, `%`, `<`, `>` and widths. There
            are more. The official Python reference lists all of them, so you can look an option up
            when you need it.

            The docs describe the parts of a spec with a short list of rules. Written on one
            line, the rules say:

            `[[fill]align][sign]["z"]["#"]["0"][width][grouping]["." precision][type]`

            Read it from left to right. You can ignore `sign`, `"z"` and `"#"` for now. Each `[...]` is an optional part. Text in double quotes,
            such as `"0"`, is a character you type exactly as shown. The parts you use must
            appear in this order. In `>10,` the `>` is the align part, `10` is the width and `,` is
            the grouping part.

            ```python
            tokens = 12345
            print(f"[{tokens:>10,}]")
            # [    12,345]
            print(f"[{tokens:*>10}]")
            # [*****12345]
            ```

            The second spec starts with a **fill** character: the character Python uses for padding
            instead of a space. The fill goes directly before the alignment option.

            For this step, open the reference and find the part that pads a number with zeros
            instead of spaces. Read its description and the examples, then come back. The terms to
            search for are *zero padding* and *width*.
        ''',
        "title": "Zero-padded request ids",
        "difficulty": 1,
        "research": {
            "note": "The format spec can pad a number with zeros instead of spaces. Read the Format Specification Mini-Language section (look for the `0` option and *width*) and the examples below it, then come back.",
            "links": [
                {"title": "Format Specification Mini-Language - Python docs",
                 "url": "https://docs.python.org/3/library/string.html#format-specification-mini-language"},
                {"title": "Format examples - Python docs",
                 "url": "https://docs.python.org/3/library/string.html#format-examples"},
            ],
        },
        "prompt": r'''
            Every API request gets an id like `REQ-00042`. Padding the number with zeros keeps
            the ids the same length, so they line up in logs and sort correctly as text.

            **Write:** `request_id(n)`

            - `n`: a non-negative integer, e.g. `42`
            - **Returns:** a string: `REQ-` followed by `n` padded with **leading zeros** to
              **5 digits**

            **Rules**
            - Numbers with fewer than 5 digits get zeros in front (`42` becomes `00042`).
            - Numbers with 5 or more digits are shown in full, without cutting
              (`123456` becomes `123456`).
            - Use a format spec for the padding (the docs linked above explain how).

            **Examples**
            ```python
            request_id(42)       # returns "REQ-00042"
            request_id(7)        # returns "REQ-00007"
            request_id(99999)    # returns "REQ-99999"
            request_id(123456)   # returns "REQ-123456"
            ```
        ''',
        "starter": r'''
            def request_id(n):
                ...
        ''',
        "tests": r'''
            from solution import request_id

            def test_two_digits_get_three_zeros():
                got = request_id(42)
                assert got == "REQ-00042", f"got {got!r}"

            def test_single_digit_and_zero():
                assert request_id(7) == "REQ-00007", f"got {request_id(7)!r}"
                assert request_id(0) == "REQ-00000", f"got {request_id(0)!r}"

            def test_five_digits_need_no_padding():
                got = request_id(99999)
                assert got == "REQ-99999", f"got {got!r}"

            def test_six_digits_are_not_cut():
                got = request_id(123456)
                assert got == "REQ-123456", f"got {got!r}"
        ''',
        "solution": r'''
            def request_id(n):
                return f"REQ-{n:05}"
        ''',
        "hints": [
            "Look in the format spec grammar for the option that goes right before the width.",
            "A 0 placed directly in front of the width pads a number with zeros instead of spaces. You need a width of 5.",
            "Return an f-string that starts with REQ- followed by a placeholder for n whose spec is a zero and then the width 5.",
        ],
    },
    {
        "id": "fstrings-3",
        "hints": [
            'Everything can be done with format specs: width, alignment, precision, separators and percent.',
            'Build one f-string with three placeholders separated by |. For strings, a precision like .12 cuts the text; for numbers use , and %.',
            'Column 1: name with < alignment, width 12 and precision .12. Column 2: tokens with >, width 8 and ,. Column 3: share with >, width 7 and .1%.',
        ],
        "title": "Fixed-width row",
        "difficulty": 2,
        "placement": True,
        "research": {
            "note": "Column 1 needs a name cut to at most 12 characters. In the Format Specification Mini-Language, read what *precision* (the `.N` part) does when the value is a string rather than a number, then come back.",
            "links": [
                {"title": "Format Specification Mini-Language - Python docs",
                 "url": "https://docs.python.org/3/library/string.html#format-specification-mini-language"},
            ],
        },
        "prompt": r'''
            One row of a usage table, printed in fixed-width columns so rows line up.

            **Write:** `format_row(name, tokens, share)`

            - `name`: a string, the model name, e.g. `"gpt-4o"`
            - `tokens`: an integer, e.g. `12345`
            - `share`: a fraction between 0 and 1, e.g. `0.4567` (meaning 45.67%)
            - **Returns:** one string with three columns separated by `|` (no spaces around the `|`
              other than the padding), 29 characters long when every value fits its column

            **Rules**
            - Column 1: `name` **left-aligned** in 12 characters (padded with spaces on the right).
              A name longer than 12 characters is **cut** to its first 12 characters.
            - Column 2: `tokens` **right-aligned** in 8 characters, with comma thousands separators.
              (If the number with commas is wider than 8, it is simply shown in full.)
            - Column 3: `share` as a **percentage** with 1 decimal and a `%` sign, **right-aligned**
              in 7 characters (`1` shows as `100.0%`, `0.00049` shows as `0.0%`).
            - The first `|` is always at position 12 (right after the name column).

            **Examples**
            ```python
            format_row("gpt-4o", 12345, 0.4567)
            # returns "gpt-4o      |  12,345|  45.7%"
            format_row("claude-3-5-sonnet", 800, 1)
            # returns "claude-3-5-s|     800| 100.0%"
            format_row("m", 5, 0.00049)
            # returns "m           |       5|   0.0%"
            ```
        ''',
        "starter": r'''
            def format_row(name, tokens, share):
                ...
        ''',
        "tests": r'''
            from solution import format_row

            def test_gpt_4o_row_matches_exactly():
                got = format_row("gpt-4o", 12345, 0.4567)
                assert got == "gpt-4o      |  12,345|  45.7%", f"got {got!r}"

            def test_long_name_is_cut_to_12_characters():
                got = format_row("claude-3-5-sonnet", 800, 1)
                assert got == "claude-3-5-s|     800| 100.0%", f"got {got!r}"

            def test_twelve_char_name_and_million_tokens():
                got = format_row("abcdefghijkl", 1000000, 0.0)
                assert got == "abcdefghijkl|1,000,000|   0.0%", f"got {got!r}"

            def test_tiny_share_shows_as_zero_percent():
                got = format_row("m", 5, 0.00049)
                assert got == "m           |       5|   0.0%", f"got {got!r}"

            def test_rows_are_29_chars_and_columns_line_up():
                a = format_row("a", 1, 0.1)
                b = format_row("longer-name", 99999, 0.955)
                assert len(a) == len(b) == 29, f"rows have lengths {len(a)} and {len(b)}"
                assert a.index("|") == b.index("|") == 12
        ''',
        "solution": r'''
            def format_row(name, tokens, share):
                return f"{name:<12.12}|{tokens:>8,}|{share:>7.1%}"
        ''',
    },
    {
        "id": "fstrings-4",
        "hints": [
            "Zero padding is a format spec (like {7:03}), and the width inside a spec can itself come from a variable.",
            "First handle an index outside 1..total with an if. Then work out how many digits total has and pad index to that many digits.",
            "If not 1 <= index <= total, return the invalid label. Otherwise compute width = len(str(total)) and use a nested spec like {index:0{width}} in the label.",
        ],
        "title": "Chunk labels",
        "difficulty": 2,
        "prompt": r'''
            When a document is split into chunks, each chunk gets a label such as
            `"report.pdf [003/120]"`. Padding with zeros makes the labels sort correctly as text.

            **Write:** `chunk_label(source, index, total)`

            - `source`: a string, the file name, e.g. `"report.pdf"`
            - `index`: an integer, the chunk number, **starting at 1**
            - `total`: an integer, how many chunks there are, e.g. `120`
            - **Returns:** a string: `source`, a space, then `[index/total]`

            **Rules**
            - `index` is padded with leading zeros to have **as many digits as `total`**
              (`total` 120 has 3 digits, so index 3 shows as `003`). `total` itself is shown as is.
            - If `total` has 1 digit, there is no padding (`[3/9]`).
            - If `index` is not between 1 and `total` (inclusive) - e.g. `0`, a negative number, or
              bigger than `total` - return `source` followed by ` [invalid]` instead.

            **Examples**
            ```python
            chunk_label("report.pdf", 3, 120)   # returns "report.pdf [003/120]"
            chunk_label("notes.md", 3, 9)       # returns "notes.md [3/9]"
            chunk_label("wiki.html", 42, 1000)  # returns "wiki.html [0042/1000]"
            chunk_label("a", 10, 10)            # returns "a [10/10]"
            chunk_label("notes.md", 0, 9)       # returns "notes.md [invalid]"
            ```
        ''',
        "starter": r'''
            def chunk_label(source, index, total):
                ...
        ''',
        "tests": r'''
            from solution import chunk_label

            def test_pads_index_to_three_digits():
                got = chunk_label("report.pdf", 3, 120)
                assert got == "report.pdf [003/120]", f"got {got!r}"

            def test_single_digit_total_has_no_padding():
                got = chunk_label("notes.md", 3, 9)
                assert got == "notes.md [3/9]", f"got {got!r}"

            def test_pads_index_to_four_digits():
                got = chunk_label("wiki.html", 42, 1000)
                assert got == "wiki.html [0042/1000]", f"got {got!r}"

            def test_first_and_last_chunk_are_valid():
                assert chunk_label("a", 1, 10) == "a [01/10]", f"got {chunk_label('a', 1, 10)!r}"
                assert chunk_label("a", 10, 10) == "a [10/10]", f"got {chunk_label('a', 10, 10)!r}"

            def test_labels_sort_correctly_as_text():
                labels = [chunk_label("d", i, 250) for i in range(1, 251)]
                assert sorted(labels) == labels, "labels should sort in numeric order as plain text"

            def test_index_out_of_range_is_invalid():
                for idx, total in ((0, 5), (6, 5), (-1, 5)):
                    got = chunk_label("d", idx, total)
                    assert got == "d [invalid]", f"chunk_label('d', {idx}, {total}) returned {got!r}"
        ''',
        "solution": r'''
            def chunk_label(source, index, total):
                if not 1 <= index <= total:
                    return f"{source} [invalid]"
                width = len(str(total))
                return f"{source} [{index:0{width}}/{total}]"
        ''',
    },
    {
        "id": "fstrings-5",
        "hints": [
            "Build each of the three lines as its own f-string with width and alignment specs, then join them with \\n.",
            "Compute the cost first (prices are per 1,000,000 tokens). The trick: make the money text \"$\" plus 4 decimals as its own string, then right-align that whole string in 10 characters.",
            "cost = (input_tokens * price_in + output_tokens * price_out) / 1_000_000. money = f\"${cost:.4f}\". Header: 'MODEL' left in 14, then 'INPUT', 'OUTPUT', 'COST' right in 10 each. Row: model <14, tokens >10 with commas, money >10. Third line: 44 dashes. Return the lines joined with \\n (none at the end).",
        ],
        "title": "Cost report",
        "difficulty": 3,
        "prompt": r'''
            A small cost report for one model's API usage, aligned like a table.

            **Write:** `cost_report(model, input_tokens, output_tokens, price_in, price_out)`

            - `model`: a string, e.g. `"gpt-4o-mini"`
            - `input_tokens`, `output_tokens`: integers, e.g. `12000`
            - `price_in`, `price_out`: floats, dollars **per 1,000,000 tokens**, e.g. `0.15`
            - **Returns:** one string of **three lines** joined with `\n`, no `\n` at the end

            **Rules**
            - Cost = `input_tokens` times `price_in` plus `output_tokens` times `price_out`, all
              divided by 1,000,000.
            - Line 1 (header) is exactly `MODEL              INPUT    OUTPUT      COST`
              (`MODEL` left-aligned in 14 characters, then `INPUT`, `OUTPUT`, `COST` each
              right-aligned in 10 characters).
            - Line 2 uses the same columns: model name left-aligned in 14; input tokens and output
              tokens right-aligned in 10 each **with comma thousands separators**; the cost as `$`
              followed by the amount with **4 decimals**, and the **whole** `$...` text right-aligned
              in 10 characters (so the `$` sits right next to the number).
            - Line 3 is 44 `-` characters.

            **Examples**
            ```python
            cost_report("gpt-4o-mini", 12000, 3400, 0.15, 0.60)
            cost_report("gpt-4o", 1200000, 2000000, 2.50, 10.00)
            cost_report("m", 0, 0, 1.0, 1.0)
            ```
            Printed, the first one is:
            ```
            MODEL              INPUT    OUTPUT      COST
            gpt-4o-mini       12,000     3,400   $0.0038
            --------------------------------------------
            ```
            The second line of the other two:
            ```
            gpt-4o         1,200,000 2,000,000  $23.0000
            m                      0         0   $0.0000
            ```
        ''',
        "starter": r'''
            def cost_report(model, input_tokens, output_tokens, price_in, price_out):
                ...
        ''',
        "tests": r'''
            from solution import cost_report

            HEADER = "MODEL              INPUT    OUTPUT      COST"

            def lines(*args):
                got = cost_report(*args)
                assert isinstance(got, str), f"returned {got!r}, not a string"
                assert not got.endswith("\n"), "the report should not end with a newline"
                return got.split("\n")

            def test_three_lines_with_exact_header_and_dashes():
                out = lines("gpt-4o-mini", 12000, 3400, 0.15, 0.60)
                assert len(out) == 3, f"expected 3 lines, got {out!r}"
                assert out[0] == HEADER, f"header was {out[0]!r}"
                assert out[2] == "-" * 44, f"separator was {out[2]!r}"

            def test_row_matches_exactly():
                out = lines("gpt-4o-mini", 12000, 3400, 0.15, 0.60)
                assert out[1] == "gpt-4o-mini       12,000     3,400   $0.0038", f"row was {out[1]!r}"

            def test_row_with_other_prices():
                out = lines("gpt-4o", 250000, 12000, 2.50, 10.00)
                assert out[1] == "gpt-4o           250,000    12,000   $0.7450", f"row was {out[1]!r}"

            def test_row_with_millions_of_tokens():
                out = lines("gpt-4o", 1200000, 2000000, 2.50, 10.00)
                assert out[1] == "gpt-4o         1,200,000 2,000,000  $23.0000", f"row was {out[1]!r}"

            def test_zero_usage_costs_zero():
                out = lines("m", 0, 0, 1.0, 1.0)
                assert out[1] == "m                      0         0   $0.0000", f"row was {out[1]!r}"
        ''',
        "solution": r'''
            def cost_report(model, input_tokens, output_tokens, price_in, price_out):
                cost = (input_tokens * price_in + output_tokens * price_out) / 1_000_000
                money = f"${cost:.4f}"
                header = f"{'MODEL':<14}{'INPUT':>10}{'OUTPUT':>10}{'COST':>10}"
                row = f"{model:<14}{input_tokens:>10,}{output_tokens:>10,}{money:>10}"
                return header + "\n" + row + "\n" + "-" * 44
        ''',
    },
    {
        "id": "fstrings-6",
        "hints": [
            "Try the units in order (k, then M, then B) with if statements, and look at the formatted text, not just the raw number.",
            "Format n divided by the unit size with one decimal. If that displayed number is below 1000, use this unit; otherwise try the next one. B is used when nothing smaller works.",
            "Return str(n) when n < 1000. Make shown = f\"{n / 1000:.1f}\"; if float(shown) < 1000 return shown + \"k\". Do the same with 1_000_000 and \"M\". Otherwise return the value divided by 1_000_000_000 with one decimal plus \"B\".",
        ],
        "title": "Human-readable token counts",
        "difficulty": 3,
        "prompt": r'''
            Dashboards show token counts in short form, like `"128.0k"` or `"1.5M"`.

            **Write:** `humanize(n)`

            - `n`: a non-negative integer token count, e.g. `128000`
            - **Returns:** a string

            **Rules**
            - Below 1,000: the plain integer as text (`0` returns `"0"`, `999` returns `"999"`).
            - Otherwise divide by 1,000 (suffix `k`), 1,000,000 (suffix `M`) or 1,000,000,000
              (suffix `B`), show **one decimal** (rounded), then the suffix with no space.
            - Use the smallest unit whose **displayed** (rounded) number is below 1000. A value must
              never be shown as `"1000.0k"` or `"1000.0M"`: `999_990` is `"1.0M"`, and
              `999_960_000` is `"1.0B"`.
            - `B` is the largest unit, so it may show 1000 or more (`"1234.6B"`).

            **Examples**
            ```python
            humanize(950)                # returns "950"
            humanize(1234)               # returns "1.2k"
            humanize(999_900)            # returns "999.9k"
            humanize(999_990)            # returns "1.0M"     (not "1000.0k")
            humanize(12_345_678)         # returns "12.3M"
            humanize(1_234_567_890_123)  # returns "1234.6B"
            ```
        ''',
        "starter": r'''
            def humanize(n):
                ...
        ''',
        "tests": r'''
            from solution import humanize

            def check(n, expected):
                got = humanize(n)
                assert got == expected, f"humanize({n}) returned {got!r}"

            def test_below_1000_is_the_plain_number():
                check(0, "0")
                check(950, "950")
                check(999, "999")

            def test_thousands_use_k_with_one_decimal():
                check(1000, "1.0k")
                check(1234, "1.2k")
                check(128000, "128.0k")
                check(999_900, "999.9k")

            def test_rounding_to_1000_moves_to_next_unit():
                check(999_990, "1.0M")
                check(999_960_000, "1.0B")

            def test_millions_use_m():
                check(1_500_000, "1.5M")
                check(12_345_678, "12.3M")

            def test_b_is_the_largest_unit():
                check(2_000_000_000, "2.0B")
                check(1_234_567_890_123, "1234.6B")
        ''',
        "solution": r'''
            def humanize(n):
                if n < 1000:
                    return str(n)
                shown = f"{n / 1_000:.1f}"
                if float(shown) < 1000:
                    return shown + "k"
                shown = f"{n / 1_000_000:.1f}"
                if float(shown) < 1000:
                    return shown + "M"
                return f"{n / 1_000_000_000:.1f}B"
        ''',
    },
]
