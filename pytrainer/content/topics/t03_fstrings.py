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
            ## Put values straight into your text

            So far you have built messages by gluing pieces together with `+` and `str()`. With one value
            that is fine. With three it turns into a tangle of quotes and plus signs:

            ```python
            model = "gpt-4o"
            tokens = 512
            print(model + " used " + str(tokens) + " tokens")
            # gpt-4o used 512 tokens
            print(f"{model} used {tokens} tokens")
            # gpt-4o used 512 tokens
            ```

            The last `print` gives the same output, and its code reads like the sentence it produces. It
            needs two things: the letter `f` directly before the opening quote, and curly braces around
            each value. Python works out what is inside the braces, turns the result into text, and puts
            that text in place of the braces. No `str()` is needed.

            A string with an `f` in front is called an **f-string**, short for formatted string. Each pair
            of braces is a **placeholder**.

            The braces can hold anything that produces a value, a calculation for example:

            ```python
            tokens = 512
            print(f"next call: {tokens * 2} tokens")
            # next call: 1024 tokens
            ```

            ```try
            name = "Ada"
            city = "Paris"
            print("Hello")
            ---
            Change the last line into an f-string that uses both variables, so that the program prints `Hello Ada from Paris`.
            ---
            name = "Ada"
            city = "Paris"
            print(f"Hello {name} from {city}")
            ---
            Each placeholder was replaced by the value of its variable. Everything outside the braces was copied as it stands.
            ```

            ### Without the f, braces are only characters

            ```quiz
            `city` is `"Paris"`. What does `print("{city}")` show?
            - [x] `{city}` :: Right. The string has no `f` in front, so the braces and the name are ordinary characters. Python prints them as they are and reports no error.
            - [ ] `Paris` :: That needs the `f`: `print(f"{city}")`. Without it, nothing is replaced.
            - [ ] An error message :: A string that contains braces is a perfectly valid string. That is what makes this mistake easy to miss.
            ```

            Putting values into a string in this way is called **string interpolation**. You will meet
            that term in documentation.

            **Watch out:** the placeholder holds the name without quotes. `f"{'city'}"` inserts the word
            `city`, not the value of the variable.

            **In short:** in an f-string, each `{...}` is replaced by the value of what is inside it. A
            string without the `f` keeps its braces as plain text.
        ''',
        "title": "What gets printed?",
        "difficulty": 0,
        "mode": "predict",
        "prompt": r'''
            Read the program in the editor. Type exactly what it prints, one line of output per line.
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
            The first `print` has an f-string, so `{model}` and `{tokens}` are replaced by their values:
            `gpt-4o used 512 tokens`. The second string has no `f`, so its braces are plain characters and
            the output is `{model}`. The third is an f-string again, and Python works out `tokens + 8`
            before it inserts the result, `520`.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Look at each string in turn. Does it have the letter `f` directly before its opening quote?",
            "In an f-string, each pair of braces is replaced by the value of what is inside. Without the `f`, the braces stay as they are.",
            "For the first line of output, put the two values into the sentence. For the second, the string has no `f`, so copy it character by character. For the third, work out the sum inside the braces.",
        ],
    },
    {
        "id": "fstrings-s2",
        "lesson": r'''
            ## A sentence with a gap in it

            Most of the prompts an app sends to a model are the same sentence with one part that
            changes: "Translate this into French", "Summarise that in three lines". You want to reuse the fixed wording while changing only the requested word or language.

            An f-string inside a function is exactly that. The parameter fills the gap, and every call
            builds a new string:

            ```python
            def greet(name):
                return f"Hello {name}, how can I help?"

            print(greet("Ada"))
            # Hello Ada, how can I help?
            print(greet("Linus"))
            # Hello Linus, how can I help?
            ```

            Fixed wording with gaps for changing values is called a **template**.

            Everything outside the braces is copied exactly, every space, comma and full stop. Only the
            text that replaces `{name}` changes from call to call.

            ```predict
            def tag(word):
                return f"#{word}!"

            print(tag("python"))
            print(tag("ai") + tag("rag"))
            ---
            The template puts `#` in front of the word and `!` behind it, with no spaces. The second line joins the results of two calls: `#ai!` and `#rag!`.
            ```

            The braces hold the name of the variable, without quotes. With quotes, the placeholder holds
            a string, and Python inserts that string itself:

            ```python
            name = "Ada"
            print(f"Hello {name}")
            # Hello Ada
            print(f"Hello {'name'}")
            # Hello name
            ```

            ```quiz
            `word` is `"cat"`. Which line hands back `Translate cat into French.`?
            - [x] `return f"Translate {word} into French."` :: Right. The `f` switches the braces on, and the braces hold the variable.
            - [ ] `return f"Translate word into French."` :: Without braces, `word` is four ordinary letters. The result is `Translate word into French.`
            - [ ] `return "Translate {word} into French."` :: The `f` is missing, so the braces stay in the text as they are.
            ```

            Building text from a template is called **string formatting**.

            **Watch out:** spaces inside a template count. A space before or after the braces appears in
            every result.

            **In short:** an f-string in a function is a template, and each call fills its placeholders
            with the arguments of that call.
        ''',
        "title": "Fill in the prompt",
        "difficulty": 0,
        "prompt": r'''
            Apps that talk to a language model rarely send a fixed text. They send a template with the
            user's topic filled in.

            **Your job:** finish `ask(topic)`. It is written except for one gap, marked `___`. Replace the
            gap so that the topic appears in the sentence.

            **What goes in**
            - `topic`: a string, for example `"RAG"`

            **What comes out**
            - a string such as `"Explain RAG in one sentence."`

            **Rules**
            - The value of `topic` appears in the place of the gap.
            - The rest of the text stays exactly as it is, including the full stop at the end.

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
            "Inside an f-string, how do you mark the place where a value goes?",
            "The gap has to become a placeholder that holds the parameter of the function.",
            "Replace the three underscores with the parameter name inside curly braces. Keep the `f` and the rest of the text as they are.",
        ],
    },
    {
        "id": "fstrings-s3",
        "lesson": r'''
            ## The letter that switches the braces on

            Your status line prints `{model} is ready`, braces and all. There is no error message. What
            went wrong?

            ```python
            model = "claude"
            print("{model} is ready")
            # {model} is ready
            print(f"{model} is ready")
            # claude is ready
            ```

            The only difference between the two lines is the `f`. A letter that stands directly before
            the opening quote of a string is called a **prefix**. Without the `f` prefix, braces are
            ordinary characters. And Python does not complain, because a string with braces in it is a
            valid string. Only the output is wrong, so this is a bug you find by looking at the output.

            Two details about the prefix. It stands directly before the quote, with no space:
            `f "..."` is a `SyntaxError`. And it works with single quotes too: `f'...'`.

            ```match
            `f"{n} left"` :: the value of `n`, followed by ` left`
            `"{n} left"` :: the characters `{n} left`, braces included
            `f"n left"` :: the characters `n left`, because nothing is in braces
            ```

            The third line of that table is the opposite mistake: the `f` is there, and the braces are
            missing. Fix one:

            ```try
            count = 3
            print(f"count items in the cart")
            ---
            The `f` is there, but the output still shows the word `count`. Fix the string so that the program prints `3 items in the cart`.
            ---
            count = 3
            print(f"{count} items in the cart")
            ---
            A value is inserted only when both parts are present: the `f` before the quote, and braces around the name.
            ```

            **Watch out:** when your output shows something like `{name}` with its braces, look for a
            missing `f` first.

            **In short:** the `f` prefix makes Python fill in the placeholders, and without it a string
            keeps its braces as plain text.
        ''',
        "title": "Fix the status line",
        "difficulty": 0,
        "prompt": r'''
            An app shows a status line for each model, such as `gpt-4o is ready`. The function for it
            gives back the text with the braces still in it, instead of the model name.

            **Your job:** find the bug in `status(model)` and fix it. The code is already in the editor.

            **What goes in**
            - `model`: the name of the model, a string, for example `"gpt-4o"`

            **What comes out**
            - a string: the model name, followed by ` is ready`

            **Rules**
            - The braces are replaced by the value of `model`. They do not appear in the result.
            - There is one space between the name and `is ready`, and no full stop at the end.

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
            "Look at the very start of the string. What makes Python treat braces as placeholders?",
            "Braces are only replaced in an f-string. This string is missing something in front of its opening quote.",
            "Add the prefix from the lesson directly in front of the opening quote, with no space between them.",
        ],
    },
    {
        "id": "fstrings-s4",
        "lesson": r'''
            ## Always two digits after the point

            A price of 1.5 should appear on a bill as `1.50`. Printing the number gives `1.5`, and
            `round(1.5, 2)` is still `1.5`, because rounding never adds zeros. Text that people read needs
            a fixed look, and an f-string can give it one.

            Inside the braces, after the value, write a colon and then an instruction for how the value
            is shown:

            ```python
            price = 1.5
            print(f"{price:.2f}")
            # 1.50
            print(f"{0.126:.2f}")
            # 0.13
            print(f"{3:.2f}")
            # 3.00
            ```

            The part after the colon is called the **format spec**. In `.2f`, the `.2` asks for two
            digits after the decimal point, which is called the **precision**. The `f` means "show this
            as a number with a decimal point". It is not the `f` prefix of the string, only the same
            letter.

            Python rounds when the value has more digits, so `0.126` becomes `0.13`. It adds zeros when
            the value has fewer, so `3` becomes `3.00`.

            ```predict
            rate = 2.5
            print(f"{rate:.1f}")
            print(f"{rate:.3f}")
            print(f"{7.268:.2f} seconds")
            ---
            With a precision of 1 the value shows as `2.5`. With a precision of 3, zeros are added: `2.500`. `7.268` is rounded to two digits, `7.27`, and the text after the braces is copied as it is.
            ```

            Text outside the braces can stand right next to a placeholder, with no space, so a unit or a
            sign can sit against the number: `f"{2.5:.1f}s"` gives `2.5s`.

            ### The spec changes the text, not the value

            ```quiz
            After `price = 1.5` and `text = f"{price:.2f}"`, what is `price`?
            - [x] The number `1.5` :: Right. The f-string built a new string, `"1.50"`, and stored it under `text`. The variable `price` was only read.
            - [ ] The string `"1.50"` :: That is `text`. A format spec never changes the variable it reads.
            - [ ] The number `1.50` :: A number does not remember zeros at its end. `1.50` and `1.5` are the same number. Only text can keep the extra zero.
            ```

            **Watch out:** the order inside the braces is value, colon, spec: `{price:.2f}`. The spec
            alone, or the spec in front of the value, is an error.

            **In short:** `{value:.2f}` shows a number with exactly two digits after the point, rounding
            it or adding zeros as needed.
        ''',
        "title": "Price with two decimals",
        "difficulty": 0,
        "prompt": r'''
            A billing page shows prices. Every price needs the same look: a dollar sign, and exactly two
            digits after the decimal point.

            **Your job:** write `price_label(price)` so that it gives back the text for a price.

            **What goes in**
            - `price`: a number, a float or an int, for example `1.5`

            **What comes out**
            - a string: `$` followed by the price with exactly 2 decimals: `"$1.50"` for the example value

            **Rules**
            - There are always 2 decimals, even for a whole number: `3` gives `"$3.00"`.
            - The price is rounded to 2 decimals: `0.126` gives `"$0.13"`.
            - There is no space between `$` and the number.

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
            "An f-string with a format spec after a colon controls how many decimals are shown.",
            "The dollar sign is ordinary text in front of the braces. The braces hold the price, and a spec for 2 decimals.",
            "Hand back an f-string that starts with `$` and continues with one placeholder: the parameter, a colon, and the spec from the lesson for two digits after the point.",
        ],
    },
    {
        "id": "fstrings-s5",
        "lesson": r'''
            ## Big numbers that people can read

            Is `128000000` a hundred and twenty-eight million, or twelve million? You have to count the
            digits to know. People avoid that by writing `128,000,000`, and an f-string can do it for
            them:

            ```python
            context = 128000
            total = 1234567
            print(f"{context:,}")
            # 128,000
            print(f"{total:,}")
            # 1,234,567
            print(f"{512:,}")
            # 512
            ```

            A comma as the format spec asks for a **thousands separator**: a comma between each group of
            three digits, counted from the right. A number below 1000 has only one group, so it gets no
            comma. The Python docs call this the grouping option.

            ```predict
            print(f"{9999:,}")
            print(f"{1000000:,} tokens")
            print(f"{250:,} and {2500:,}")
            ---
            `9999` has two groups: `9,999`. A million has three: `1,000,000`. In the last line the first number is below 1000 and stays as it is, and the second becomes `2,500`.
            ```

            ### The result is text

            `f"{context:,}"` builds a string. `"128,000"` is made for people to read, and a program
            cannot calculate with it.

            ```quiz
            What does `int("128,000")` do?
            - [x] It stops with a `ValueError` :: Right. `int()` accepts digits, and spaces around them. A comma in the middle is not part of a number for Python.
            - [ ] It gives `128000` :: `int()` does not remove commas. The text has to be only digits.
            - [ ] It gives `128` :: `int()` never reads part of a string. It converts the whole text or it stops.
            ```

            So keep the number itself in its variable, and format it only at the moment you show it.

            **Watch out:** the colon is still needed. In `{context:,}` the comma is the spec, and it
            stands after the colon like every spec.

            **In short:** `{value:,}` shows a number with a comma between each group of three digits.
        ''',
        "title": "Big numbers with commas",
        "difficulty": 0,
        "prompt": r'''
            A model's context window is the number of tokens it can handle at once, and for current
            models it is a large number. A label on a settings page should show it in a form that is easy
            to read.

            **Your job:** write `context_label(tokens)` so that it gives back that label.

            **What goes in**
            - `tokens`: a whole number, for example `128000`

            **What comes out**
            - a string: the number with commas between the thousands, then a space and the word `tokens`:
              `"128,000 tokens"` for the example value

            **Rules**
            - There is a comma after every 3 digits, counted from the right: `1000000` gives `1,000,000`.
            - A number below 1,000 gets no comma: `512` stays `512`.

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
            "The braces hold the number and the spec for the separators. The word `tokens` comes after the braces, as plain text.",
            "Hand back an f-string with one placeholder, the parameter with the spec for thousands separators, followed by a space and the word `tokens`.",
        ],
    },
    {
        "id": "fstrings-s6",
        "lesson": r'''
            ## From a fraction to a percentage

            Code usually stores a rate as a number between 0 and 1: a success rate of `0.873`. A report
            shows the same thing as `87.3%`. Turning one into the other takes three steps: multiply by
            100, round, and add the percent sign. One format spec does all three:

            ```python
            rate = 0.873
            print(f"{rate:.1%}")
            # 87.3%
            print(f"{0.5:.1%}")
            # 50.0%
            print(f"{1:.0%}")
            # 100%
            ```

            `.1%` means "as a percentage, with 1 digit after the point". The number in front of the `%`
            is the precision, the same as in `.2f`, and `.0%` shows no decimals at all.

            ```quiz
            What does `f"{0.25:.0%}"` produce?
            - [x] `25%` :: Right. 0.25 times 100 is 25, and a precision of 0 shows no decimals.
            - [ ] `0.25%` :: The `%` spec multiplies by 100 before it adds the sign. It does not only attach the sign.
            - [ ] `25.0%` :: That would be `.1%`. With `.0%` there is no digit after the point.
            ```

            ### Give it the fraction, not the percentage

            The spec always multiplies by 100. Hand it a number that is already a percentage, and the
            result is a hundred times too big:

            ```python
            print(f"{87.3:.1%}")
            # 8730.0%
            ```

            The program below makes a mistake of the same kind:

            ```try
            done = 45
            total = 60
            print(f"{done:.0%} finished")
            ---
            The output is a silly number, because `done` is a count and not a fraction. Change the placeholder so that the program prints `75% finished`.
            ---
            done = 45
            total = 60
            print(f"{done / total:.0%} finished")
            ---
            45 out of 60 is the fraction 0.75, and the `%` spec turns a fraction into a percentage.
            ```

            **Watch out:** do not multiply by 100 yourself. The `%` spec does it, and doing it twice gives
            a number like `8730.0%`.

            **In short:** `{fraction:.1%}` multiplies by 100, shows 1 decimal and adds the `%` sign.
        ''',
        "title": "Success rate",
        "difficulty": 0,
        "prompt": r'''
            A monitoring dashboard shows what share of the calls to an API succeeded. The app stores that
            share as a fraction between 0 and 1, and the dashboard shows it as a percentage.

            **Your job:** write `success_label(rate)` so that it gives back the text for the dashboard.

            **What goes in**
            - `rate`: a fraction between 0 and 1, a float or an int, for example `0.873`

            **What comes out**
            - a string: the rate as a percentage with 1 decimal and a `%` sign, then a space and the word
              `success`: `"87.3% success"` for the example value

            **Rules**
            - The fraction is multiplied by 100 and rounded to 1 decimal: `0.873` shows as `87.3%`.
            - There is always 1 decimal, even for a whole percentage: `1` shows as `100.0%`.

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
            "One format spec turns a fraction into a percentage.",
            "The braces hold the rate and a spec for a percentage with 1 decimal. The word `success` comes after the braces.",
            "Hand back an f-string: one placeholder with the parameter and the percentage spec with 1 decimal, then a space and the word `success`. Do not multiply by 100 yourself.",
        ],
    },
    {
        "id": "fstrings-1",
        "lesson": r'''
            ## One string, two lines

            A settings panel shows a small card with two lines of text. The function that builds the card
            returns one string. So how does one string hold two lines?

            With the newline character. You met `\n` in the Data Types chapter as something to strip
            away. Now you put it in on purpose:

            ```python
            card = "Model: gpt-4o\nTemperature: 0.70"
            print(card)
            # Model: gpt-4o
            # Temperature: 0.70
            print(len("a\nb"))
            # 3
            ```

            `card` is one string, and `print` shows it as two lines, because at the `\n` the output
            moves on to a new line. `len("a\nb")` is 3: the `\n` is typed as two signs and stored as one
            character.

            A backslash followed by a character, which Python reads as one special character, is called
            an **escape sequence**. `\n` is the newline. Two others are `\t`, a tab, and `\\`, a real
            backslash.

            A `\n` works inside an f-string too, right next to placeholders:

            ```predict
            user = "Ada"
            print(f"Hi {user},\nwelcome back.")
            print(len("x\ny\n"))
            ---
            The first string holds one newline, so `print` shows it as two lines: `Hi Ada,` and `welcome back.`. The second string has four characters: `x`, a newline, `y` and another newline.
            ```

            Python keeps every space around a `\n`.

            ```quiz
            What is on the second line of the output of `print("a \n b")`?
            - [x] A space, then `b` :: Right. The space after `\n` belongs to the string, so the second line starts with it. In the same way the first line ends with a space.
            - [ ] Only `b` :: Python does not tidy spaces away. Every character between the quotes is kept.
            - [ ] `\n b` :: The `\n` itself is never shown. It is the character that ends the first line.
            ```

            **Watch out:** a `\n` at the very end of a string is one more character, and `print` then
            shows an empty line under the text. Put one there only when a task asks for it.

            **In short:** `\n` inside a string starts a new line, so one string can hold several lines.
        ''',
        "title": "Model card",
        "difficulty": 1,
        "hints": [
            "Three things from this chapter meet here: an f-string, the newline character, and a format spec for decimals.",
            "Build one string with two parts: the line for the model, then the newline, then the line for the temperature with 2 decimals.",
            "One f-string does it: the text `Model: `, a placeholder for the model, the newline escape, the text `Temperature: `, and a placeholder for the temperature with the 2-decimal spec. Nothing comes after it.",
        ],
        "prompt": r'''
            The settings panel of a chat app shows a small "model card": the name of the model on one
            line, and its temperature on the next.

            **Your job:** write `model_card(model, temperature)` so that it gives back the card as one
            string that holds two lines.

            **What goes in**
            - `model`: the name of the model, a string, for example `"gpt-4o"`
            - `temperature`: a number, a float or an int, for example `0.7`

            **What comes out**
            - one string with two lines, separated by a newline character `\n`

            **Rules**
            - Line 1 is `Model: ` followed by the model name.
            - Line 2 is `Temperature: ` followed by the temperature with exactly 2 decimals. It is rounded:
              `0.456` shows as `0.46`, and `1` shows as `1.00`.
            - There is exactly one `\n`, between the two lines. There is none at the end.

            **Examples**
            ```python
            model_card("gpt-4o", 0.7)   # returns "Model: gpt-4o\nTemperature: 0.70"
            model_card("m", 1)          # returns "Model: m\nTemperature: 1.00"
            model_card("m", 0.456)      # returns "Model: m\nTemperature: 0.46"
            ```

            Printed, the first one looks like this:
            ```text
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
            ## Print the name along with the value

            When you hunt a bug, you print variables to see what they hold. A line such as
            `gpt-4o 512 0.35` then leaves you guessing which number is which. You could write
            `f"model={model} tokens={tokens}"`, typing every name twice. There is a shorter way:

            ```python
            model = "gpt-4o"
            tokens = 512
            print(f"{model=} {tokens=}")
            # model='gpt-4o' tokens=512
            ```

            Put an `=` right after the name inside the braces. Python then inserts three things: the
            text of what you wrote, an equals sign, and the value. This is called the **`=` specifier**.
            The Python docs also call it a self-documenting expression.

            Notice the quotes around `gpt-4o`. A string value is shown with quotes here, and that is
            useful, because it makes an empty string or a space at the end visible.

            ```predict
            city = "Rome "
            count = 0
            print(f"{city=}")
            print(f"{count=} {count + 1=}")
            ---
            The quotes show that `city` ends with a space: `city='Rome '`. The specifier works with any expression: it shows the text `count + 1`, an equals sign, and the result, 1.
            ```

            ### Together with a format spec

            You can still add a format spec. The `=` goes first, then the colon, then the spec:

            ```python
            ratio = 0.3456
            print(f"{ratio=:.1f}")
            # ratio=0.3
            ```

            ```quiz
            `share` is `0.25`. Which placeholder shows `share=25%`?
            - [x] `{share=:.0%}` :: Right. The name, then `=`, then the colon and the spec.
            - [ ] `{share:.0%=}` :: The `=` has to stand before the colon. After the spec, Python does not accept it.
            - [ ] `{share:=.0%}` :: After the colon, everything is read as the format spec, and there `=` means something else. The name is not printed.
            ```

            **Watch out:** the `=` specifier is a tool for debugging. Text that users will read is better
            written out, because they should not see the names of your variables.

            **In short:** `{name=}` inserts the name, an equals sign and the value, and a format spec can
            follow after `=:`.
        ''',
        "title": "Debug line",
        "hints": [
            "The `=` specifier of an f-string prints a name, an equals sign and the value.",
            "Use three placeholders with a space between them, one for each parameter, each with `=` after the name. The latency also needs a spec for 2 decimals, placed after the `=`.",
            "Hand back one f-string with three placeholders in the order of the task. Each holds a parameter name followed by `=`. In the last one, a colon and the 2-decimal spec come after the `=`.",
        ],
        "difficulty": 1,
        "prompt": r'''
            When a call to a model API goes wrong, a one-line debug log shows you at a glance what was
            sent and how long it took: the model, the number of tokens and the latency, which is the time
            the call took in seconds.

            **Your job:** write `debug_line(model, tokens, latency)` so that it gives back that line.

            **What goes in**
            - `model`: a string, for example `"gpt-4o"`
            - `tokens`: a whole number, for example `512`
            - `latency`: a number of seconds, a float or an int, for example `0.3456`

            **What comes out**
            - a string such as `"model='gpt-4o' tokens=512 latency=0.35"`

            **Rules**
            - There are three parts in this order, with single spaces between them: `model=...`,
              `tokens=...` and `latency=...`.
            - The model name appears with quotes around it: `model='gpt-4o'`.
            - `latency` is shown with exactly 2 decimals: `2` shows as `2.00`.
            - Use the `=` specifier of f-strings, a name followed by `=` inside the braces. A check looks
              for it in your code.

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
            ## Columns that line up

            A usage table in a terminal has model names of different lengths and numbers of different
            sizes. Printed one after the other, they make a ragged mess. For the rows to line up, each
            column needs a fixed width.

            ```python
            name = "gpt-4o"
            print(f"[{name:<10}]")
            # [gpt-4o    ]
            print(f"[{name:>10}]")
            # [    gpt-4o]
            print(f"[{512:>6}]")
            # [   512]
            ```

            The square brackets are ordinary text. They are only there to show where the spaces are.

            A whole number in the format spec is the **width**: the smallest number of characters the
            result may have. Python fills the rest with spaces, and those spaces are called **padding**.
            The sign in front of the width decides where the padding goes. `<` puts the value on the
            left and the spaces after it. `>` puts the value on the right and the spaces before it. This
            is called the **alignment**.

            Press Next and count the spaces in each line of output:

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

            The last line of that program shows that the width is a minimum. A value that is longer than
            the width is shown in full, and nothing is cut off.

            ```predict
            print(f"[{'ab':<4}]")
            print(f"[{'ab':>4}]")
            print(f"[{7:>3}][{'toolong':<3}]")
            ---
            `ab` has 2 characters, so a width of 4 adds 2 spaces: after the value for `<`, and before it for `>`. In the last line, `7` gets 2 spaces in front, and `toolong` is longer than its width of 3, so it is shown in full.
            ```

            ```quiz
            What does `f"[{42:5}]"` produce? The spec has a width and no alignment sign.
            - [x] `[   42]` :: Right. Without a sign, Python right-aligns numbers and left-aligns strings.
            - [ ] `[42   ]` :: That is how a string would be padded. Numbers go to the right by default, so that their digits line up.
            - [ ] `[42]` :: The width of 5 still applies. Only the alignment was left to the default.
            ```

            Two placeholders side by side make a row with two columns, and their widths add up.

            **Watch out:** the width counts every character of the result. A placeholder with a width of
            10 and one with a width of 6 give 16 characters, as long as both values fit.

            **In short:** `{value:<10}` pads on the right, `{value:>10}` pads on the left, and a value
            that is longer than the width is shown in full.
        ''',
        "title": "Aligned usage cell",
        "difficulty": 1,
        "prompt": r'''
            A usage table in a terminal has the model names on the left and the token counts on the
            right. For the rows to line up, every row is built from two columns of fixed width.

            **Your job:** write `usage_cell(name, tokens)` so that it gives back one row.

            **What goes in**
            - `name`: the name of the model, a string, for example `"gpt-4o"`
            - `tokens`: a whole number, for example `512`

            **What comes out**
            - one string: `name` left-aligned in 10 characters, directly followed by `tokens`
              right-aligned in 6 characters. When both values fit, that is 16 characters in total.

            **Rules**
            - The padding is made of spaces.
            - Nothing stands between the two columns. The padding is the gap.
            - A name that is longer than 10 characters is shown in full, not cut. The number column
              follows it directly.
            - The number has no thousands separators.

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
            "A format spec can set a width and an alignment: one sign for left, another for right.",
            "Use two placeholders directly next to each other: the name, left-aligned in a width of 10, and then the tokens, right-aligned in a width of 6.",
            "Hand back an f-string with two placeholders and nothing between them. The first holds the name, the sign for left alignment and the width 10. The second holds the tokens, the sign for right alignment and the width 6.",
        ],
    },
    {
        "id": "fstrings-8",
        "lesson": r'''
            ## Looking up a format option

            You now know several format options: `.2f`, the comma, `%`, `<`, `>` and the width. There are
            more, and nobody keeps them all in their head. The official reference lists every one of
            them, and it sums up the whole format spec in a single dense line:

            ```text
            [[fill]align][sign]["z"]["#"]["0"][width][grouping]["." precision][type]
            ```

            It looks forbidding, and it follows three simple rules.

            - Each `[...]` is a part that you may leave out.
            - Text in double quotes, such as `"0"`, is a character that you type exactly as shown.
            - The parts that you do use appear in this order, from left to right.

            You can ignore `sign`, `"z"` and `"#"` for now. Take the spec `>10,` and read it against the
            line: `>` is the align part, `10` is the width, and `,` is the grouping.

            ```python
            tokens = 12345
            print(f"[{tokens:>10,}]")
            # [    12,345]
            print(f"[{tokens:*>10}]")
            # [*****12345]
            ```

            The second spec starts with a **fill** character. It is the character Python pads with, in
            place of a space, and it stands directly before the alignment sign.

            ```match
            `>` in `{x:>8.2f}` :: the align part: the padding goes in front
            `8` in `{x:>8.2f}` :: the width: at least 8 characters
            `.2` in `{x:>8.2f}` :: the precision: 2 digits after the point
            `f` in `{x:>8.2f}` :: the type: show a number with a decimal point
            ```

            ```quiz
            You want a number right-aligned in 12 characters, with thousands separators. Which spec has its parts in the right order?
            - [x] `>12,` :: Right. Align, then width, then grouping, as in the line from the reference.
            - [ ] `,12>` :: The parts are in the reverse order. Python stops with a `ValueError` about the format spec.
            - [ ] `12>,` :: The align sign has to come before the width. After a width, Python expects the grouping or the precision, so it stops with a `ValueError` about the format spec.
            ```

            For this step, open the reference that is linked in the task. Find the option that pads a
            number with zeros in place of spaces, and read its description. The words to look for are
            "zero padding" and "width".

            **Watch out:** the order of the parts is fixed. A spec whose parts are in another order is
            either an error or means something different.

            **In short:** the reference line lists the parts of a format spec in the order in which they
            must be written, and every part is optional.
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
            Every request to your API gets an id such as `REQ-00042`. The number is padded with zeros so
            that all ids have the same length. They then line up in a log, and they sort correctly when
            they are sorted as text.

            **Your job:** write `request_id(n)` so that it gives back the id for request number `n`.

            **What goes in**
            - `n`: a whole number that is 0 or more, for example `42`

            **What comes out**
            - a string: `REQ-` followed by `n`, padded with zeros in front to 5 digits: `"REQ-00042"` for
              the example value

            **Rules**
            - A number with fewer than 5 digits gets zeros in front: `42` becomes `00042`.
            - A number with 5 digits or more is shown in full, with nothing cut off: `123456` stays
              `123456`.
            - The padding is done by a format spec. The reference linked above explains which option
              does it.

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
            "In the line from the reference, find the option that stands directly before the width.",
            "That option pads a number with zeros in place of spaces. You also need a width.",
            "Hand back an f-string that starts with `REQ-` and continues with a placeholder for `n`. Its spec is the zero option, followed by the width that the task asks for.",
        ],
    },
    {
        "id": "fstrings-3",
        "hints": [
            "Everything here is done with format specs: width, alignment, precision, separators and percent.",
            "Build one f-string with three placeholders and a `|` between them. For a string, a precision cuts the text to that many characters. The numbers use the comma and the percent spec.",
            "Column 1 is the name with left alignment, width 12 and precision 12. Column 2 is the tokens with right alignment, width 8 and the thousands separator. Column 3 is the share with right alignment, width 7 and the percent spec with 1 decimal.",
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
            A usage table has three columns: the model name, the number of tokens, and the share of all
            tokens that this model used. Each row is printed in columns of fixed width, so that the rows
            line up.

            **Your job:** write `format_row(name, tokens, share)` so that it gives back one row of that
            table.

            **What goes in**
            - `name`: the name of the model, a string, for example `"gpt-4o"`
            - `tokens`: a whole number, for example `12345`
            - `share`: a fraction between 0 and 1, for example `0.4567`, which means 45.67%

            **What comes out**
            - one string with three columns and a `|` between them. When every value fits its column, the
              string is 29 characters long.

            **Rules**
            - Column 1 is `name`, left-aligned in 12 characters, with spaces as padding on the right. A
              name that is longer than 12 characters is cut to its first 12 characters.
            - Column 2 is `tokens`, right-aligned in 8 characters, with commas as thousands separators.
              A number that is wider than 8 characters with its commas is shown in full.
            - Column 3 is `share` as a percentage with 1 decimal and a `%` sign, right-aligned in 7
              characters. `1` shows as `100.0%`, and `0.00049` shows as `0.0%`.
            - There are no spaces around the `|` signs apart from the padding, so the first `|` always
              comes directly after the 12 characters of the name column.

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
            "Zero padding is a format spec, and the width inside a spec can itself come from a variable: a placeholder inside the spec.",
            "Handle an index outside the range first, with an `if`. Then work out how many digits the total has, and pad the index to that many digits.",
            "When the index is not between 1 and the total, hand back the invalid label. Otherwise count the digits of the total, by taking `len` of its text form. Use that count as the width of a zero-padded placeholder for the index, written as a second pair of braces inside the spec.",
        ],
        "title": "Chunk labels",
        "difficulty": 2,
        "prompt": r'''
            When a long document is split into pieces, called chunks, each chunk gets a label such as
            `report.pdf [003/120]`: the file, the number of the chunk, and the number of chunks. The chunk
            number is padded with zeros, so that the labels sort correctly when they are sorted as text.

            **Your job:** write `chunk_label(source, index, total)` so that it gives back the label.

            **What goes in**
            - `source`: the name of the file, a string, for example `"report.pdf"`
            - `index`: the number of the chunk, a whole number. The first chunk is number 1.
            - `total`: the number of chunks, a whole number, for example `120`

            **What comes out**
            - a string: `source`, a space, and then `[index/total]`: `"report.pdf [003/120]"` for chunk 3
              of 120

            **Rules**
            - `index` is padded with zeros in front until it has as many digits as `total`. A `total` of
              120 has 3 digits, so index 3 shows as `003`. `total` itself is shown as it is.
            - When `total` has 1 digit, nothing is padded: `[3/9]`.
            - When `index` is not between 1 and `total`, both included, the result is `source` followed
              by ` [invalid]`. That covers `0`, a negative number, and a number greater than `total`.

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
            "Build each of the three lines as a string of its own, with specs for width and alignment. Then join the lines with `\\n`.",
            "Work out the cost first. The prices are for 1,000,000 tokens. The trick for the last column: make the money text, `$` and 4 decimals, as a string of its own, and then right-align that whole string in 10 characters.",
            "Five steps: the cost, from the two token counts and the two prices, divided by a million. The money text. The header, with `MODEL` left in 14 and the other three titles right in 10 each. The row, with the same widths, commas for the token counts, and the money text. Last, hand back the header, the row and 44 dashes, joined with newlines and with no newline at the end.",
        ],
        "title": "Cost report",
        "difficulty": 3,
        "prompt": r'''
            A cost report shows what one model's API usage cost: the tokens that went in, the tokens that
            came out, and the price. It is laid out like a small table, with a header, one row and a
            line of dashes.

            **Your job:** write
            `cost_report(model, input_tokens, output_tokens, price_in, price_out)` so that it gives back
            the report as one string.

            **What goes in**
            - `model`: a string, for example `"gpt-4o-mini"`
            - `input_tokens`, `output_tokens`: whole numbers, for example `12000`
            - `price_in`, `price_out`: floats, the price in dollars for 1,000,000 tokens, for example `0.15`

            **What comes out**
            - one string of three lines, joined with `\n`, with no `\n` at the end

            **Rules**
            - The cost is `input_tokens` times `price_in`, plus `output_tokens` times `price_out`, and
              that sum divided by 1,000,000.
            - Line 1, the header, is exactly `MODEL              INPUT    OUTPUT      COST`. That is
              `MODEL` left-aligned in 14 characters, and then `INPUT`, `OUTPUT` and `COST`, each
              right-aligned in 10 characters.
            - Line 2 has the same columns. The model name is left-aligned in 14. The input tokens and the
              output tokens are right-aligned in 10 each, with commas as thousands separators. The cost
              is `$` followed by the amount with 4 decimals, and that whole text, `$` included, is
              right-aligned in 10 characters, so the `$` stands directly against the number.
            - Line 3 is 44 `-` characters. A string times a number repeats the string: `"-" * 3` is
              `"---"`.

            **Examples**
            ```python
            cost_report("gpt-4o-mini", 12000, 3400, 0.15, 0.60)
            cost_report("gpt-4o", 1200000, 2000000, 2.50, 10.00)
            cost_report("m", 0, 0, 1.0, 1.0)
            ```

            Printed, the first one is:
            ```text
            MODEL              INPUT    OUTPUT      COST
            gpt-4o-mini       12,000     3,400   $0.0038
            --------------------------------------------
            ```

            The second line of the other two:
            ```text
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
            "Try the units in order, `k`, then `M`, then `B`, with `if` statements. Look at the formatted text, not only at the raw number.",
            "Format `n` divided by the size of the unit with one decimal. When the number that is shown is below 1000, use that unit. Otherwise try the next one. `B` takes whatever is left.",
            "Below 1000, hand back the number as text. Otherwise format `n` divided by a thousand with one decimal, and store the text. When that text, turned back into a float, is below 1000, hand it back with `k` joined on. Do the same with a million and `M`. Otherwise hand back `n` divided by a billion with one decimal, and `B`.",
        ],
        "title": "Human-readable token counts",
        "difficulty": 3,
        "prompt": r'''
            Dashboards show token counts in a short form that is quick to read, such as `128.0k` for
            128,000 or `1.5M` for 1,500,000.

            **Your job:** write `humanize(n)` so that it gives back the short form of a count.

            **What goes in**
            - `n`: a number of tokens, a whole number that is 0 or more, for example `128000`

            **What comes out**
            - a string

            **Rules**
            - Below 1,000 the result is the plain number as text: `0` gives `"0"`, and `999` gives `"999"`.
            - From 1,000 on, the number is divided by 1,000 (letter `k`), by 1,000,000 (letter `M`) or by
              1,000,000,000 (letter `B`), shown with one decimal, rounded, and followed by the letter
              with no space.
            - Use the smallest unit for which the number that is shown, after rounding, is below 1000. A
              value must never appear as `"1000.0k"` or `"1000.0M"`: `999_990` is `"1.0M"`, and
              `999_960_000` is `"1.0B"`. (Python lets you write `999_990` for 999990. The underscores only
              help the eye.)
            - `B` is the largest unit, so with `B` the number may be 1000 or more: `"1234.6B"`.

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
