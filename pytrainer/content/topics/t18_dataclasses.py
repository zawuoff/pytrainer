TOPIC = {
    "id": "dataclasses",
    "title": "Dataclasses & Type Hints",
    "track": "production-python",
    "order": 2,
    "requires": ["classes"],
    "summary": """
        Modelling structured data with @dataclass: defaults, default factories,
        frozen and ordered dataclasses, validation in __post_init__, Enums and
        type hints, and converting API dicts to typed objects and back.
    """,
    "concepts": ["@dataclass", "field(default_factory=...)", "frozen", "order", "__post_init__",
                 "asdict", "replace", "Enum", "type hints", "Literal", "X | None"],
}

# The Library card for this chapter (shown once the chapter's steps are done).
# Every line that starts with `#` in an example is the real output of that example.
REFERENCE = {
    "keywords": ["dataclass", "decorator", "field", "type hint", "annotation", "default_factory",
                 "post_init", "frozen", "frozeninstanceerror", "asdict", "replace", "enum",
                 "optional", "literal", "validation"],
    "cards": [
        {
            "syntax": "@dataclass",
            "explain": "Written above a class. Generates __init__, __repr__ and __eq__ from the name: type field lines.",
            "example": r'''
                from dataclasses import dataclass
                @dataclass
                class Message:
                    role: str
                    name: str | None = None
                print(Message("user") == Message("user"), Message("tool", "calc"))
                # True Message(role='tool', name='calc')
            ''',
        },
        {
            "syntax": "turns: list[str] = field(default_factory=list)",
            "explain": "A list or dict default. Python calls list() for each new object, so every object gets its own list.",
            "example": r'''
                from dataclasses import dataclass, field
                @dataclass
                class Chat:
                    turns: list[str] = field(default_factory=list)
                a, b = Chat(), Chat()
                a.turns.append("Hi")
                print(a.turns, b.turns)
                # ['Hi'] []
            ''',
        },
        {
            "syntax": "def __post_init__(self):",
            "explain": "The generated __init__ calls this method after it stores the fields. Use it to check or convert them.",
            "example": r'''
                from dataclasses import dataclass
                @dataclass
                class Chunk:
                    text: str
                    def __post_init__(self):
                        self.text = self.text.strip()
                print(Chunk("  hi "))
                # Chunk(text='hi')
            ''',
        },
        {
            "syntax": "@dataclass(frozen=True, order=True)",
            "explain": "frozen makes instances read-only and usable in sets. order adds < and >, comparing fields in order.",
            "example": r'''
                from dataclasses import dataclass
                @dataclass(frozen=True, order=True)
                class Version:
                    major: int
                    minor: int
                print(Version(1, 2) < Version(1, 10), len({Version(1, 2)}))
                # True 1
            ''',
        },
        {
            "syntax": "asdict(obj)  /  replace(obj, field=value)",
            "explain": "asdict converts an instance to a dict. replace returns a copy with the given fields changed.",
            "example": r'''
                from dataclasses import dataclass, asdict, replace
                @dataclass
                class Usage:
                    tokens: int
                u = Usage(5)
                print(asdict(u), replace(u, tokens=9), u)
                # {'tokens': 5} Usage(tokens=9) Usage(tokens=5)
            ''',
        },
        {
            "syntax": "class Role(Enum):",
            "explain": "A fixed set of named members. Role(value) finds a member by its value, or raises ValueError.",
            "example": r'''
                from enum import Enum
                class Role(Enum):
                    USER = "user"
                    TOOL = "tool"
                print(Role("tool"), Role.USER.value)
                # Role.TOOL user
            ''',
        },
    ],
}

LESSON = r'''
## Dataclasses and type hints: chapter notes

### `@dataclass`

A **field** is a line of the form `name: type` in a class body. A **decorator** is a
function that you apply to a class or a function by writing `@name` on the line above it.
The `dataclass` decorator reads the fields of a class and adds three generated methods to
it: `__init__`, `__repr__` and `__eq__`. A class decorated this way is a **dataclass**.

```python
from dataclasses import dataclass

@dataclass
class Message:
    role: str
    content: str

m = Message("user", "Hi")
print(m)
# Message(role='user', content='Hi')
print(m == Message("user", "Hi"))
# True
```

Step through the stages to see what `@dataclass` generates from the two fields.

```diagram
{"type":"flow","title":"What @dataclass generates for Message","steps":[
{"label":"Class body runs","detail":"Python runs the class body and creates the class Message. The two field lines are recorded in Message.__annotations__ in the order you wrote them.","code":"class Message:\n    role: str\n    content: str\n\nMessage.__annotations__\n# {'role': <class 'str'>, 'content': <class 'str'>}"},
{"label":"dataclass(Message) is called","detail":"The line @dataclass makes Python call dataclass(Message). The function reads the fields in order: role, then content.","code":"Message = dataclass(Message)"},
{"label":"__init__ is generated","detail":"The generated __init__ has one parameter per field, in field order. It stores each argument as an attribute on self.","code":"def __init__(self, role: str, content: str):\n    self.role = role\n    self.content = content"},
{"label":"__repr__ is generated","detail":"The generated __repr__ returns the class name followed by every field as name=value. Each value is formatted with repr(), so strings appear in single quotes.","code":"def __repr__(self):\n    return f\"Message(role={self.role!r}, content={self.content!r})\"\n\nprint(Message(\"user\", \"Hi\"))\n# Message(role='user', content='Hi')"},
{"label":"__eq__ is generated","detail":"The generated __eq__ returns True when the other object has the same class and every field is equal. It behaves the same as this code.","code":"def __eq__(self, other):\n    if other.__class__ is self.__class__:\n        return (self.role, self.content) == (other.role, other.content)\n    return NotImplemented\n\nMessage(\"user\", \"Hi\") == Message(\"user\", \"Hi\")\n# True"},
{"label":"The class is returned","detail":"dataclass returns the same class with the three methods added. The name Message now refers to it.","code":"m = Message(\"user\", \"Hi\")\nm.content\n# 'Hi'"}
]}
```

### Type hints

A **type hint**, also called an **annotation**, is a type written in your code to state
what kind of value is expected. Fields, parameters and return values can all have one.

| hint | meaning |
| --- | --- |
| `str`, `int`, `float`, `bool` | one value of that type |
| `list[str]` | a list of strings |
| `dict[str, float]` | a dict with `str` keys and `float` values |
| `str \| None` | a string or `None` |
| `def f(text: str) -> int:` | a parameter annotation and a return annotation |

Python does not check hints when the program runs. A **type checker** is a tool that reads
your code without running it and reports type mistakes. `mypy` and `pyright` are type
checkers. Editors read hints too and show warnings as you type.

In the example below, `double("ab")` breaks the hint `n: int`. Python still runs the body:
`"ab" * 2` repeats the string.

```python
def double(n: int) -> int:
    return n * 2

print(double("ab"))
# abab
print(double.__annotations__)
# {'n': <class 'int'>, 'return': <class 'int'>}
```

`Literal["stop", "length"]` from `typing` is a hint that allows only those exact values.
Python does not check it while the program runs either.

### Defaults

A field can have a default value: `name: type = value`. Fields without a default must
come before fields with one. A default that is a list or a dict needs
`field(default_factory=list)`. Python calls the function you pass, here `list`, once per
new object. `list()` returns a new empty list, so each object gets its own list.

```python
from dataclasses import dataclass, field

@dataclass
class Chat:
    model: str
    temperature: float = 0.7
    turns: list[str] = field(default_factory=list)

a = Chat("gpt-4o")
b = Chat("gpt-4o")
a.turns.append("Hi")
print(a)
# Chat(model='gpt-4o', temperature=0.7, turns=['Hi'])
print(b.turns)
# []
```

### Methods and `__post_init__`

A dataclass is a normal class, so you can add your own methods and `@property` methods.
A **class method** is a method decorated with `@classmethod`. Python passes it the class
as the first argument, named `cls`, instead of an instance. Use one to build an object
from other data, for example `from_dict(cls, data)`.

If the class defines `__post_init__(self)`, the generated `__init__` calls it after it has
stored every field. Use it to validate or convert the fields.

```python
from dataclasses import dataclass

@dataclass
class Chunk:
    text: str
    page: int = 1

    def __post_init__(self):
        if self.page < 1:
            raise ValueError(f"page must be >= 1, got {self.page}")

    @classmethod
    def from_dict(cls, data):
        return cls(data["text"], data.get("page", 1))

print(Chunk.from_dict({"text": "Hello", "page": 3}))
# Chunk(text='Hello', page=3)
try:
    Chunk("Hello", 0)
except ValueError as e:
    print("error:", e)
# error: page must be >= 1, got 0
```

### Options and helpers

`@dataclass(frozen=True)` makes instances read-only: assigning to a field raises an error.
It also makes them **hashable**, which means you can put them in a set or use them as dict
keys. `@dataclass(order=True)` adds `<`, `<=`, `>` and `>=`, which
compare the fields one by one in the order you declared them.

`asdict(obj)` converts a dataclass instance to a dict, including nested dataclasses.
`replace(obj, x=1)` returns a copy with the field `x` changed. `fields(cls)` returns the
fields of a dataclass. `is_dataclass(x)` returns `True` for a dataclass or an instance of one.

```python
from dataclasses import dataclass, asdict, replace, fields

@dataclass(frozen=True, order=True)
class Version:
    major: int
    minor: int

v = Version(1, 2)
print(sorted([Version(2, 0), v]))
# [Version(major=1, minor=2), Version(major=2, minor=0)]
print(asdict(v))
# {'major': 1, 'minor': 2}
print(replace(v, minor=3))
# Version(major=1, minor=3)
print([f.name for f in fields(Version)])
# ['major', 'minor']
```

An **Enum** is a class with a fixed set of named members, each with a value. Calling the
class with a value, as in `Role("user")`, returns the member that has that value.

```python
from enum import Enum

class Role(Enum):
    USER = "user"
    TOOL = "tool"

print(Role("user"))
# Role.USER
print(Role.USER.value)
# user
```

## Common mistakes

- Without the `@dataclass` line, the class has no generated `__init__`. `Message("user", "Hi")`
  raises `TypeError: Message() takes no arguments`.
- A field with a default placed before a field without one raises `TypeError` when the
  class is created. The message starts with `non-default argument`.
- `tags: list[str] = []` raises `ValueError` when the class is created. The message says
  `mutable default <class 'list'> for field tags is not allowed: use default_factory`.
- Assigning to a field of a frozen dataclass raises `dataclasses.FrozenInstanceError`.
- An unknown value such as `Role("robot")` raises `ValueError`.
'''


EXERCISES = [
    {
        "id": "dataclasses-s1",
        "title": "What gets printed?",
        "lesson": r'''
            ## Let Python write the repetitive part of a class

            In the Classes chapter you wrote classes that hold a few values, such as a chat message with a
            role and a text. To make such a class store its values, print in a readable way and compare
            with `==`, you wrote three methods by hand:

            ```python
            class Model:
                def __init__(self, name, context):
                    self.name = name
                    self.context = context
                def __repr__(self):
                    return f"Model(name={self.name!r}, context={self.context!r})"
                def __eq__(self, other):
                    return (self.name, self.context) == (other.name, other.context)
            print(Model("gpt-4o", 128000))
            # Model(name='gpt-4o', context=128000)
            ```

            Count how often the word `name` appears: seven times. The class holds two values, and it took
            three methods to say so. A third value would mean a change in every one of them.

            Python can write those three methods for you. You only list what the class holds:

            ```python
            from dataclasses import dataclass
            @dataclass
            class Model:
                name: str
                context: int
            m = Model("gpt-4o", 128000)
            print(m)
            # Model(name='gpt-4o', context=128000)
            print(m.name)
            # gpt-4o
            print(m == Model("gpt-4o", 128000))
            # True
            ```

            This short class behaves like the long one. Two kinds of line are new in it.

            `name: str` and `context: int` each name one value that every object stores. The word after
            the colon says what kind of value it should be: `str` for text, `int` for a whole number. A
            line like this is called a **field**.

            `@dataclass`, above the `class` line, tells Python to read the fields and to write `__init__`,
            `__repr__` and `__eq__` from them. A class made this way is called a **dataclass**. The next
            step looks at that line more closely.

            Here is what the three methods that Python wrote do:

            - `Model("gpt-4o", 128000)` stores the values in the fields, in the order the fields are
              written: the first value in `name`, the second in `context`.
            - `print(m)` shows the class name and then every field as `name=value`.
            - `==` gives `True` when every field of one object is equal to the same field of the other.

            ```predict
            from dataclasses import dataclass

            @dataclass
            class Tool:
                name: str
                calls: int

            t = Tool("search", 3)
            print(t)
            print(t.name)
            print(t.calls + 1)
            ---
            `print(t)` shows the class name and both fields: `Tool(name='search', calls=3)`. The text has quotes and the number has none. `print(t.name)` prints one field on its own, so there are no quotes: `search`. `t.calls` is the number 3, and 3 + 1 is `4`.
            ```

            ```quiz
            `Tool` is the dataclass from the box above. What does `Tool("search", 3) == Tool("search", 4)` give?
            - [x] `False` :: Right. The `__eq__` that `@dataclass` wrote compares every field. The names are equal, but `3` is not equal to `4`.
            - [ ] `True` :: Both objects are a `Tool` and both are named `"search"`, but that is not enough. Every field has to be equal, and `calls` differs.
            - [ ] An error :: Comparing two objects of the same dataclass never stops the program. The answer is `True` or `False`.
            ```

            **Watch out:** `print(m)` shows text in quotes, as in `name='gpt-4o'`, and `print(m.name)` does
            not. The whole object is printed the way you would type it in code. One field on its own is
            printed as the plain value.

            **In short:** put `@dataclass` above a class that lists its fields as `name: type`, and Python
            writes `__init__`, `__repr__` and `__eq__` for you.
        ''',
        "difficulty": 0,
        "mode": "predict",
        "prompt": r'''
            Read the program in the editor. Type exactly what it prints, one line for each `print`.
        ''',
        "code": r'''
            from dataclasses import dataclass

            @dataclass
            class Message:
                role: str
                content: str

            m = Message("user", "Hi")
            print(m)
            print(m.content)
            print(m == Message("user", "Hi"))
        ''',
        "solution": r'''
            Message(role='user', content='Hi')
            Hi
            True
        ''',
        "explanation": r'''
            `Message("user", "Hi")` stores `"user"` in `role` and `"Hi"` in `content`, because the values
            go to the fields in the order the fields are written. `print(m)` uses the `__repr__` that
            `@dataclass` wrote: the class name, then each field as `name=value`, with the text in single
            quotes. `print(m.content)` prints one field on its own, so there are no quotes: `Hi`. The last
            line makes a second message with the same two values. The `__eq__` that `@dataclass` wrote
            compares the fields one by one. They are all equal, so `==` gives `True`.
        ''',
        "starter": "",
        "tests": "",
        "hints": [
            "Look at the three `print` lines of the second example in the lesson. This program prints the same three kinds of thing, for a different class.",
            "Printing a whole dataclass object shows the class name and every field with its value. Printing one field shows only that value. `==` compares the fields of the two objects.",
            "Your first line is the class name followed by round brackets, with both fields inside as name=value and the text in single quotes. Your second line is the content on its own, without quotes. Your third line is `True` or `False`: are both fields of the two messages equal?",
        ],
    },
    {
        "id": "dataclasses-s2",
        "title": "Add the decorator",
        "lesson": r'''
            ## What the line with the @ does

            In the last step, `@dataclass` sat above the class and three methods appeared. What does that
            line do? One way to find out is to leave it out:

            ```python
            class Tag:
                label: str

            try:
                Tag("urgent")
            except TypeError as e:
                print("error:", e)
            # error: Tag() takes no arguments
            ```

            On its own, the field `label: str` is a note and nothing more. Nobody wrote an `__init__`, so
            the class has no idea what to do with `"urgent"`.

            The methods come from `dataclass`, which is a function. You give it a class. It reads the
            fields, adds `__init__`, `__repr__` and `__eq__` to the class, and hands the class back. You
            can call it yourself:

            ```python
            from dataclasses import dataclass

            class Tag:
                label: str

            Tag = dataclass(Tag)
            print(Tag("urgent"))
            # Tag(label='urgent')
            ```

            `Tag = dataclass(Tag)` passes the class to the function and stores what comes back under the
            same name. It works, but the line sits below the class, where it is easy to miss and easy to
            forget. So Python has a shorter spelling for it: `@` and the name of the function, on the
            line above `class`.

            ```python
            from dataclasses import dataclass

            @dataclass
            class Tag:
                label: str

            print(Tag("urgent"))
            # Tag(label='urgent')
            ```

            Both programs do the same thing. A line that starts with `@` above a class or a function is
            called a **decorator**. Read it as "when this class is finished, pass it through that
            function". You have used one before: `@property` in the Classes chapter is a decorator above
            a method.

            Put these lines in order so that the program prints `Point(x=1, y=2)`:

            ```order
            from dataclasses import dataclass
            @dataclass
            class Point:
                x: int
                y: int
            print(Point(1, 2))
            ---
            The import comes first, because the `@` line needs the name `dataclass`. The decorator sits above `class`, and the fields are indented under it, `x` before `y`, because the first value goes to the first field. The `print` comes last, when the class is complete.
            ```

            That import matters. `dataclass` is not built in the way `print` is. It lives in `dataclasses`,
            a module that comes with Python, and the `import` line at the top fetches it.

            ```quiz
            This program has the `@dataclass` line, but no `import` line. What happens when you run it?
            ~~~python
            @dataclass
            class Tag:
                label: str

            print(Tag("urgent"))
            ~~~
            - [x] Python stops with `NameError: name 'dataclass' is not defined` :: Right. The `@` line passes the class to a function called `dataclass`, and without the import Python does not know that name.
            - [ ] It prints `Tag(label='urgent')` :: The `@` line can only use a function that Python knows. `dataclass` has to be imported from the module `dataclasses` first.
            - [ ] Python stops with `TypeError: Tag() takes no arguments` :: That is the error when the `@dataclass` line is missing. Here the line is there, and Python fails earlier, on the name `dataclass`.
            ```

            **Watch out:** when a class with fields stops with `TypeError: Tag() takes no arguments`, the
            `@dataclass` line is missing. Fields alone do not make an `__init__`.

            **In short:** `@dataclass` above a class passes the class through the function `dataclass`,
            and that function adds the methods.
        ''',
        "difficulty": 0,
        "prompt": r'''
            A search tool keeps every document it can search as a small record: a title and the text.
            Someone wrote the class `Document` with both fields, but the class is not a dataclass yet, so
            it cannot take the two values.

            **Your job:** make `Document` a dataclass. The code is already in the editor. One line is
            missing, and its place is marked `___`. Replace the gap.

            **What goes in**
            - `title`: the title of the document, a string, for example `"Intro"`
            - `text`: the text of the document, a string, for example `"Hello"`

            **What comes out**
            - `Document("Intro", "Hello")` gives an object that stores both values, as `.title` and `.text`

            **Rules**
            - Change only the line with the gap. The import and the two fields stay as they are.
            - Two documents with the same title and the same text are equal with `==`.
            - A check asks Python whether `Document` is a dataclass.

            **Examples**
            ```python
            d = Document("Intro", "Hello")
            d.title                                    # "Intro"
            d.text                                     # "Hello"
            Document("a", "b") == Document("a", "b")   # True
            ```
        ''',
        "starter": r'''
            from dataclasses import dataclass

            ___
            class Document:
                title: str
                text: str
        ''',
        "tests": r'''
            import dataclasses
            from solution import Document

            def test_document_is_a_dataclass():
                assert dataclasses.is_dataclass(Document), "Document is not a dataclass yet"

            def test_constructor_sets_title_and_text():
                d = Document("Intro", "Hello")
                assert (d.title, d.text) == ("Intro", "Hello")

            def test_documents_with_same_fields_are_equal():
                assert Document("a", "b") == Document("a", "b")
        ''',
        "solution": r'''
            from dataclasses import dataclass

            @dataclass
            class Document:
                title: str
                text: str
        ''',
        "hints": [
            "Which line turned a class with fields into a dataclass in the lesson? It starts with a special character.",
            "The function you need is already imported on the first line of the file. The missing line passes the class below it through that function.",
            "The gap is on the line above `class`, and that is where a decorator goes. Write the character that starts a decorator, followed straight away by the name that the first line of the file imports.",
        ],
    },
    {
        "id": "dataclasses-s6",
        "title": "Label a function",
        "lesson": r'''
            ## Say what goes in and what comes out

            Here is a function from someone else's code. What do you have to pass to it, and what do you
            get back?

            ```python
            def cost(tokens, price):
                return tokens / 1000 * price

            print(cost(2000, 0.5))
            # 1.0
            ```

            You had to read the body to find out, and even then you cannot be sure. Is `tokens` a number,
            or a list of tokens?

            In the fields of a dataclass you wrote the kind of value after the name: `name: str`. The
            first line of a function can carry the same labels:

            ```python
            def cost(tokens: int, price: float) -> float:
                return tokens / 1000 * price

            print(cost(2000, 0.5))
            # 1.0
            ```

            The result is the same. What changed is that the first line now answers the question:

            - `tokens: int` says that `tokens` should be a whole number.
            - `price: float` says that `price` should be a number with a decimal point.
            - `-> float` says what comes back. It is an arrow made of a minus sign and a greater-than
              sign, and it goes after the closing bracket and before the colon.

            A label like this is called a **type hint**. The formal word, which the Python docs use, is
            **annotation**. You wrote a few in the Functions chapter. This step and the next one look at
            them properly.

            ```match
            `text: str` :: the parameter `text` should be a string
            `n: int` :: the parameter `n` should be a whole number
            `-> bool` :: the function gives back `True` or `False`
            `-> float` :: the function gives back a number with a decimal point
            ---
            A hint with a colon belongs to a parameter. The hint after the arrow belongs to the value that the function gives back.
            ```

            Python keeps the hints of a function, and you can look at them:

            ```python
            def shout(text: str) -> str:
                return text.upper() + "!"

            print(shout.__annotations__)
            # {'text': <class 'str'>, 'return': <class 'str'>}
            ```

            `__annotations__` is a dict. It holds each parameter name with its hint, and the hint for the
            result under the key `"return"`. `<class 'str'>` is how Python prints the type `str` itself,
            as you saw with `type()` in the Data Types chapter. The checks of this step read this dict.

            ```fill
            def is_long(prompt: str) -> ___:
                return len(prompt) > 100

            print(is_long("hi"))
            print(is_long.__annotations__["return"])
            ---
            - [x] bool :: Right. `len(prompt) > 100` is a comparison, and a comparison gives `True` or `False`.
            - [ ] str :: `prompt` is a string, but the function does not give `prompt` back. It gives back the result of a comparison.
            - [ ] int :: `len(prompt)` is a whole number, but the function gives back whether that number is greater than 100.
            - [ ] "bool" :: With quotes this is a piece of text, not a type. Python stores the text `bool` as the hint, and the last line prints `bool` where it should print `<class 'bool'>`.
            ```

            **Watch out:** the names are the short ones that Python uses: `str`, `int`, `float`, `bool`.
            With `text: string`, Python says nothing when the function is defined or called. It complains
            when something reads the hints, as a check does: `NameError: name 'string' is not defined`.

            **In short:** `def f(x: int) -> str:` says that `x` should be an `int` and that a `str` comes
            back.
        ''',
        "difficulty": 0,
        "prompt": r'''
            Counting the words of a text is a quick way to estimate how many tokens it will cost. The
            function `count_words` in the editor already counts correctly. What it lacks is its type
            hints. Both places are marked `___`.

            **Your job:** replace the two gaps so that the first line of `count_words(text)` says what
            kind of value goes in and what kind of value comes back.

            **What goes in**
            - `text`: a piece of text, for example `"tokens are not words"`

            **What comes out**
            - the number of words in the text, as a whole number: `4` for the example value

            **Rules**
            - The first gap is the hint for `text`: the type of a piece of text.
            - The second gap is the hint for the result: the type of a whole number.
            - Write each hint as the type itself, without quotes. A check reads the hints that Python
              stored for the function and compares them with the two types.
            - Leave the body as it is. A text with no words still gives `0`.

            **Examples**
            ```python
            count_words("tokens are not words")   # returns 4
            count_words("")                       # returns 0
            ```
        ''',
        "starter": r'''
            def count_words(text: ___) -> ___:
                return len(text.split())
        ''',
        "tests": r'''
            from solution import count_words

            def test_counts_words():
                got = count_words("tokens are not words")
                assert got == 4, f"got {got!r}"

            def test_empty_text_has_zero_words():
                assert count_words("") == 0

            def test_parameter_is_annotated_str():
                hints = count_words.__annotations__
                assert hints.get("text") is str, f"text is annotated as {hints.get('text')!r}"

            def test_return_is_annotated_int():
                hints = count_words.__annotations__
                assert hints.get("return") is int, f"return is annotated as {hints.get('return')!r}"
        ''',
        "solution": r'''
            def count_words(text: str) -> int:
                return len(text.split())
        ''',
        "hints": [
            "The first gap is the hint for the parameter. The second gap, after the arrow, is the hint for what the function gives back.",
            "Ask two questions. What kind of value is a text such as `\"tokens are not words\"`? What kind of value does `len(...)` give?",
            "Each gap takes one short type name of the kind you wrote in dataclass fields, without quotes. The first is the type of text. The second is the type of whole numbers.",
        ],
    },
    {
        "id": "dataclasses-s7",
        "title": "Signs, not fences",
        "lesson": r'''
            ## What happens when a call ignores the hint

            The first line of this function says that it wants two whole numbers:

            ```python
            def add_tokens(a: int, b: int) -> int:
                return a + b

            print(add_tokens(2, 3))
            # 5
            ```

            Somewhere else in the program, the two counts arrive as text, perhaps read from a file, and
            nobody converts them. What does Python do with a call that goes against the hints? Decide
            what you expect, then find out:

            ```predict
            def add_tokens(a: int, b: int) -> int:
                return a + b

            print(add_tokens("2", "3"))
            ---
            There is no error. Python runs the body with the values it was given, and `+` between two pieces of text joins them: `23`. Nothing compared the values with the hints.
            ```

            Python stores type hints, and that is all it does with them. While the program runs, nothing
            checks a value against a hint. The time while a program runs is called **runtime**, so
            programmers say that type hints are not checked at runtime.

            A hint works like a sign that says "whole numbers only". A sign informs. It does not stop
            anyone, the way a fence would. What happens after a call that ignores the sign depends only on
            what the body does with the value.

            ```quiz
            `def half(n: int) -> float:` has the body `return n / 2`. Someone calls `half("10")`. What does Python do because of the hint `n: int`?
            - [x] Nothing. It runs the body with the text `"10"` :: Right. Hints are not checked at runtime. Here the body then divides text by a number, and that stops with a `TypeError` that comes from the division, not from the hint.
            - [ ] It turns `"10"` into the number `10` :: A hint never changes a value. If you want a number, you have to convert the text yourself with `int()`.
            - [ ] It stops with an error before the body runs :: Python does not compare a value with a hint. The body always starts, with whatever it was given.
            ```

            So why write hints at all? Because other readers do use them:

            - A person sees what the function expects without reading the body.
            - Your editor uses them to suggest methods that fit the type, and to underline a call such as
              `add_tokens("2", "3")` while you type.
            - A **type checker** is a program that reads your code without running it and reports every
              call that breaks a hint. `mypy` and `pyright` are two of them. Many teams run one on every
              change.

            For those readers, the hints stay stored with the function, whatever the calls do:

            ```python
            def add_tokens(a: int, b: int) -> int:
                return a + b

            print(add_tokens.__annotations__["a"])
            # <class 'int'>
            ```

            `__annotations__` is the dict from the last step. The key `"a"` gives the hint of the
            parameter `a`, which is the type `int` itself.

            **Watch out:** a call with the wrong type often gives a wrong result and no error, such as `23`
            where you expected `5`. That is harder to find than a crash. When a value must have the right
            type, your own code has to check it. A later step in this chapter shows where such a check
            goes in a dataclass.

            **In short:** type hints tell people and tools what you intended, and Python does not check
            them when the program runs.
        ''',
        "difficulty": 0,
        "mode": "predict",
        "prompt": r'''
            Read the program in the editor. Type exactly what it prints, one line for each `print`.
        ''',
        "code": r'''
            def double(n: int) -> int:
                return n * 2

            print(double(4))
            print(double("ab"))
            print(double.__annotations__["n"])
        ''',
        "solution": r'''
            8
            abab
            <class 'int'>
        ''',
        "explanation": r'''
            `double(4)` gives `4 * 2`, which is `8`. `double("ab")` goes against the hint `n: int`, but
            Python does not check hints while the program runs. It runs the body with the text, and `*`
            between a piece of text and a whole number repeats the text: `abab`. The last line reads the
            hint that Python stored for the parameter `n`. The hint is the type `int` itself, and Python
            prints a type as `<class 'int'>`.
        ''',
        "starter": "",
        "tests": "",
        "hints": [
            "Does Python compare the value in a call with the hint of the parameter? The first box in the lesson answers that.",
            "The body runs with whatever it is given. Think about what `*` does with a number, and what it does with a piece of text. The last line prints a stored hint, and a hint is a type.",
            "Your first line is 4 doubled. Your second line is the text `ab` written two times in a row, with nothing in between. Your third line is the type of whole numbers, written the way Python prints a type: the word class and the name of the type in single quotes, all inside angle brackets.",
        ],
    },
    {
        "id": "dataclasses-s3",
        "title": "Fix the bug: field order",
        "lesson": r'''
            ## A field with a value to fall back on

            Most requests to a model use the same limit, for example 256 tokens. Nobody wants to type
            `256` each time a request is created. In a class written by hand, the fall-back value went
            into `__init__`, as the default of a parameter:

            ```python
            class Request:
                def __init__(self, prompt, max_tokens=256):
                    self.prompt = prompt
                    self.max_tokens = max_tokens

            print(Request("Hi").max_tokens)
            # 256
            ```

            A dataclass has no `__init__` for you to write in. The default goes on the field, after the
            type:

            ```python
            from dataclasses import dataclass

            @dataclass
            class Request:
                prompt: str
                max_tokens: int = 256

            print(Request("Hi"))
            # Request(prompt='Hi', max_tokens=256)
            print(Request("Hi", 50))
            # Request(prompt='Hi', max_tokens=50)
            ```

            `Request("Hi")` gives no second value, so `max_tokens` falls back to `256`. `Request("Hi", 50)`
            gives one, and the default is not used.

            ```try
            from dataclasses import dataclass

            @dataclass
            class Job:
                name: str
                retries: int

            print(Job("sync"))
            ---
            The program stops with a `TypeError`, because `Job("sync")` gives no value for `retries`. Give `retries` a default so that the program prints `Job(name='sync', retries=3)`.
            ---
            from dataclasses import dataclass

            @dataclass
            class Job:
                name: str
                retries: int = 3

            print(Job("sync"))
            ---
            With `= 3` after the type, `retries` no longer has to be given. `Job("sync", 5)` still works, and uses 5.
            ```

            ### The order of the fields

            From the fields, `@dataclass` writes `def __init__(self, prompt, max_tokens=256)`: one
            parameter for each field, in the order of the fields. Parameters have a rule: after a
            parameter with a default, every later parameter needs a default too. Without that rule, Python
            could not tell which value a short call such as `Request("Hi")` leaves out.

            Fields follow the same rule. The fields without a default come first, and the fields with a
            default come after them. When a class breaks the rule, Python stops while it builds the
            class, before any object is made:

            ```python
            from dataclasses import dataclass

            try:
                @dataclass
                class Broken:
                    max_tokens: int = 256
                    prompt: str
            except TypeError as e:
                print("error:", e)
            # error: non-default argument 'prompt' follows default argument 'max_tokens'
            ```

            In the message, "non-default argument" means a field without a default.

            ```quiz
            A dataclass has these three fields, in this order: `model: str`, then `stream: bool = False`, then `user: str`. What happens?
            - [x] Python stops with a `TypeError` while it builds the class :: Right. `user` has no default and comes after `stream`, which has one. The message is `non-default argument 'user' follows default argument 'stream'`.
            - [ ] The class is built, and `user` is `None` when it is left out :: A field never gets a default on its own. Without `= value` it must be given in every call.
            - [ ] The class is built, and the error comes when an object is created without `user` :: The error comes earlier. Python refuses to build the class, so no object can be created at all.
            ```

            **Watch out:** this error comes from the class itself. It appears as soon as the file runs,
            even when no line creates an object. Look at the fields, not at the calls.

            **In short:** `name: type = value` gives a field a default, and the fields with a default come
            after the fields without one.
        ''',
        "difficulty": 0,
        "prompt": r'''
            Every request to a model has to say which model it is for, and most requests use the same
            temperature. (The temperature is the setting for how much a model varies its answers.) The
            class `ModelConfig` in the editor should hold both values, with `0.7` as the temperature when
            none is given. Instead, the program stops with a `TypeError` as soon as it runs, before any
            object is made.

            **Your job:** find out why Python refuses to build the class `ModelConfig`, and fix it. The
            code is already in the editor. Run it first and read the error message.

            **What goes in**
            - `model`: the name of the model, a string, for example `"gpt-4o"`. It must always be given.
            - `temperature`: a number with a decimal point, for example `0.0`. It may be left out.

            **What comes out**
            - `ModelConfig("gpt-4o")` gives an object with the model `"gpt-4o"` and the temperature `0.7`

            **Rules**
            - When no temperature is given, it is `0.7`.
            - The first value of a call is the model and the second is the temperature. A check looks at
              the order of the fields: `model`, then `temperature`.
            - Both fields keep their names and their type hints.

            **Examples**
            ```python
            ModelConfig("gpt-4o")        # ModelConfig(model='gpt-4o', temperature=0.7)
            ModelConfig("claude", 0.0)   # ModelConfig(model='claude', temperature=0.0)
            ```
        ''',
        "starter": r'''
            from dataclasses import dataclass

            @dataclass
            class ModelConfig:
                temperature: float = 0.7
                model: str
        ''',
        "tests": r'''
            import dataclasses
            from solution import ModelConfig

            def test_temperature_defaults_to_0_7():
                c = ModelConfig("gpt-4o")
                assert (c.model, c.temperature) == ("gpt-4o", 0.7), f"got {c!r}"

            def test_explicit_temperature_is_used():
                c = ModelConfig("claude", 0.0)
                assert (c.model, c.temperature) == ("claude", 0.0), f"got {c!r}"

            def test_fields_are_model_then_temperature():
                names = [f.name for f in dataclasses.fields(ModelConfig)]
                assert names == ["model", "temperature"], f"fields are {names}"
        ''',
        "solution": r'''
            from dataclasses import dataclass

            @dataclass
            class ModelConfig:
                model: str
                temperature: float = 0.7
        ''',
        "hints": [
            "Run the program and read the last line of the error. It names two fields, and it says which of them follows the other.",
            "The lesson has a rule about where a field with a default may stand among the other fields. Which of the two fields here has a default?",
            "Nothing has to be added and nothing has to be removed. The two field lines stay as they are written. Only their position in the class changes, so that the field that must always be given comes first.",
        ],
    },
    {
        "id": "dataclasses-s4",
        "title": "A chunk record",
        "lesson": r'''
            ## From a description to a dataclass

            So far the class was already there, and you filled in or repaired one line. In real work you
            start from a sentence, such as this one from a teammate:

            "A search result has the id of the document, a score between 0 and 1, and a flag that says
            whether the user has seen it. A new result has not been seen."

            To turn the sentence into a dataclass, ask three questions about each value. What is it
            called? What kind of value is it? Must it always be given, or is there a value to fall back
            on?

            | in the sentence | name | type | default |
            | --- | --- | --- | --- |
            | the id of the document | `doc_id` | `str` | none |
            | a score between 0 and 1 | `score` | `float` | none |
            | whether the user has seen it | `seen` | `bool` | `False` |

            Each row becomes one field line:

            ```python
            from dataclasses import dataclass

            @dataclass
            class Result:
                doc_id: str
                score: float
                seen: bool = False

            print(Result("doc-7", 0.92))
            # Result(doc_id='doc-7', score=0.92, seen=False)
            print(Result.__annotations__)
            # {'doc_id': <class 'str'>, 'score': <class 'float'>, 'seen': <class 'bool'>}
            ```

            A whole dataclass has four parts, from top to bottom: the import, the decorator, the `class`
            line, and one indented line for each field. The fields with a default go last, as you saw in
            the last step.

            A class keeps the hints of its fields in `__annotations__`, the same way a function does. The
            last line of the example prints them. The checks of this step read that dict.

            Match each description with the field line that fits it:

            ```match
            the name of the model, always given :: `model: str`
            the price for 1000 tokens, always given :: `price: float`
            the number of retries, 3 unless stated otherwise :: `retries: int = 3`
            whether the reply is streamed, off unless stated otherwise :: `stream: bool = False`
            ---
            Text is `str`, a number with a decimal point is `float`, a whole number is `int`, and on or off is `bool`. "Unless stated otherwise" is a default.
            ```

            Now the other way round. Which line completes this class?

            ```fill
            from dataclasses import dataclass

            @dataclass
            class Limit:
                model: str
                ___

            print(Limit("gpt-4o"))
            ---
            - [x] max_tokens: int = 256 :: Right. A name, a colon, the type, and then the default after an equals sign. The program prints `Limit(model='gpt-4o', max_tokens=256)`.
            - [ ] max_tokens = 256 :: Without a type this line is not a field. `@dataclass` skips it, and the program prints `Limit(model='gpt-4o')`.
            - [ ] max_tokens: int :: This is a field, but it has no default, so `Limit("gpt-4o")` stops with a `TypeError` about a missing argument.
            - [ ] int max_tokens = 256 :: Some languages put the type first. Python does not, and stops with a `SyntaxError`.
            ```

            **Watch out:** a line without a type, such as `seen = False`, is not a field. Python accepts it
            without an error and `@dataclass` skips it, so the value is missing from `print` and cannot be
            passed in a call.

            **In short:** write the import, `@dataclass` and the `class` line, then one `name: type` line
            for each value, with the ones that have a default last.
        ''',
        "difficulty": 0,
        "prompt": r'''
            Before a long document can be searched, it is cut into smaller pieces called chunks. For every
            chunk you want to remember its text, the file it came from, and the page it was on.

            **Your job:** write a dataclass named `Chunk` that holds those three values. The import is
            already in the editor.

            **What goes in**
            - `text`: the text of the chunk, a string, for example `"Hello"`. Always given.
            - `source`: the name of the file it came from, a string, for example `"guide.pdf"`. Always
              given.
            - `page`: the page number, a whole number, for example `7`. When it is left out, it is `1`.

            **What comes out**
            - `Chunk("Hello", "guide.pdf")` gives an object that stores the three values as `.text`,
              `.source` and `.page`

            **Rules**
            - `Chunk` is a dataclass. A check asks Python whether it is one.
            - The fields are in the order `text`, `source`, `page`, so that the values of a call go to
              the right fields.
            - Every field has the type hint that fits its description: the type of text for `text` and
              for `source`, the type of whole numbers for `page`. A check compares the hints with the
              real types, so write them without quotes.
            - `page` falls back to `1`.

            **Examples**
            ```python
            Chunk("Hello", "guide.pdf")         # Chunk(text='Hello', source='guide.pdf', page=1)
            Chunk("Bye", "guide.pdf", 7).page   # 7
            ```
        ''',
        "starter": r'''
            from dataclasses import dataclass

            # define the Chunk dataclass here
        ''',
        "tests": r'''
            import dataclasses
            from solution import Chunk

            def test_chunk_is_a_dataclass():
                assert dataclasses.is_dataclass(Chunk), "Chunk must use @dataclass"

            def test_fields_are_text_source_page_in_order():
                names = [f.name for f in dataclasses.fields(Chunk)]
                assert names == ["text", "source", "page"], f"fields are {names}"

            def test_page_defaults_to_one():
                c = Chunk("Hello", "guide.pdf")
                assert c.page == 1, f"page is {c.page!r}"
                assert Chunk("Bye", "guide.pdf", 7).page == 7

            def test_type_hints_are_str_str_int():
                hints = Chunk.__annotations__
                assert hints == {"text": str, "source": str, "page": int}, f"annotations: {hints}"
        ''',
        "solution": r'''
            from dataclasses import dataclass

            @dataclass
            class Chunk:
                text: str
                source: str
                page: int = 1
        ''',
        "hints": [
            "The lesson built a dataclass from a sentence. Ask its three questions about each value here: what is it called, what kind of value is it, and is there a value to fall back on?",
            "A dataclass has four parts, from top to bottom: the import, the decorator, the `class` line, and one indented line for each field. The import is already there.",
            "Under the import, write the decorator and then the `class` line with the name `Chunk`. Under that, indented, write three field lines in the order of the task. Each one has the name, a colon and the type. The two text fields come first. The page comes last, and its line ends with an equals sign and the value to fall back on.",
        ],
    },
    {
        "id": "dataclasses-s5",
        "title": "Total tokens",
        "lesson": r'''
            ## Give a dataclass a method

            A record often has to answer a question about itself: how many tokens did this request use in
            all, how long is this chunk? In the Classes chapter, code like that went into a method. Does a
            dataclass still allow it?

            It does. Write the method below the fields, indented, the way you did in any class:

            ```python
            from dataclasses import dataclass
            @dataclass
            class Rate:
                input_per_1k: float
                output_per_1k: float
                def average(self) -> float:
                    return (self.input_per_1k + self.output_per_1k) / 2
            print(Rate(1.0, 3.0).average())
            # 2.0
            print(Rate(0.5, 0.5).average())
            # 0.5
            ```

            `@dataclass` writes `__init__`, `__repr__` and `__eq__` and leaves every other method alone. A
            dataclass is a normal class, so a method of it works as it did before.

            In `Rate(1.0, 3.0).average()`, the parameter `self` is that very `Rate` object.
            `self.input_per_1k` is the field stored in it, which is `1.0`, and `self.output_per_1k` is
            `3.0`. The second object stores other numbers, so it gives another answer.

            ```predict
            from dataclasses import dataclass

            @dataclass
            class Box:
                width: int
                height: int

                def area(self):
                    return self.width * self.height

            small = Box(2, 3)
            print(small.area())
            print(Box(10, 10).area())
            print(small)
            ---
            `small.area()` runs with `self` set to `small`, so it multiplies 2 by 3 and gives `6`. The second call makes a new `Box` of 10 by 10 and gives `100`. `print(small)` shows only the fields, `Box(width=2, height=3)`. A method is not a field, so it does not appear there.
            ```

            A method reads a field through `self`. Without `self.`, Python looks for an ordinary variable
            with that name, and there is none. This program stops with an error. Fix the method:

            ```try
            from dataclasses import dataclass

            @dataclass
            class Rate:
                input_per_1k: float
                output_per_1k: float

                def spread(self) -> float:
                    return output_per_1k - input_per_1k

            print(Rate(1.0, 3.0).spread())
            ---
            Run it and read the error. Then change the method so that the program prints `2.0`.
            ---
            from dataclasses import dataclass

            @dataclass
            class Rate:
                input_per_1k: float
                output_per_1k: float

                def spread(self) -> float:
                    return self.output_per_1k - self.input_per_1k

            print(Rate(1.0, 3.0).spread())
            ---
            The fields belong to the object, not to the method. The method has to ask the object for them, and `self` is the object.
            ```

            **Watch out:** a field written without `self.` inside a method stops the program with a
            `NameError`. For the program above, the message is `name 'output_per_1k' is not defined`. It does
            not say "you forgot self". It says that Python found no variable with that name.

            **In short:** a dataclass method goes below the fields, and it reads the fields of its object as
            `self.name`.
        ''',
        "difficulty": 0,
        "prompt": r'''
            An LLM API reports how many tokens a request used: some for the prompt you sent and some for
            the reply that came back. The dataclass `Usage` is already in the editor with both numbers as
            fields.

            **Your job:** finish the method `total` of `Usage`. Its body is `...` for now. It gives back how
            many tokens the request used in all.

            **What goes in**
            - nothing except the object itself. The method reads two fields of the object it is called on:
              `prompt_tokens` and `completion_tokens`. Both are whole numbers, for example `5` and `2`.

            **What comes out**
            - one whole number: the two token counts added together. It is `7` for the example values.

            **Rules**
            - Each object uses its own numbers. Two `Usage` objects with different counts give different
              totals.
            - The method gives the number back. It does not print it.
            - `Usage(0, 0).total()` gives `0`.

            **Examples**
            ```python
            Usage(5, 2).total()      # returns 7
            Usage(100, 20).total()   # returns 120
            Usage(0, 0).total()      # returns 0
            ```
        ''',
        "starter": r'''
            from dataclasses import dataclass

            @dataclass
            class Usage:
                prompt_tokens: int
                completion_tokens: int

                def total(self):
                    ...
        ''',
        "tests": r'''
            from solution import Usage

            def test_total_adds_prompt_and_completion_tokens():
                got = Usage(5, 2).total()
                assert got == 7, f"got {got!r}"

            def test_zero_usage_totals_zero():
                assert Usage(0, 0).total() == 0

            def test_each_object_uses_its_own_numbers():
                a, b = Usage(1, 1), Usage(100, 20)
                assert (a.total(), b.total()) == (2, 120)
        ''',
        "solution": r'''
            from dataclasses import dataclass

            @dataclass
            class Usage:
                prompt_tokens: int
                completion_tokens: int

                def total(self):
                    return self.prompt_tokens + self.completion_tokens
        ''',
        "hints": [
            "Look at how `average` in the lesson got hold of the two numbers stored in its own object. Your method needs the same thing for two other fields.",
            "The two numbers you need are fields of the object the method belongs to. Read each one through the name that every method has as its first parameter, add them, and give the result back.",
            "In place of `...`, write the line that gives a value back from a function. After that keyword, put the first field of the object, a plus sign, and the second field of the object. Each field is written with the name of the first parameter, a dot, and the field name.",
        ],
    },
    {
        "id": "dataclasses-7",
        "title": "Typed cost lookup",
        "lesson": r'''
            ## Say what a list or a dict holds

            In the last steps, `x: int` said what kind of value a parameter takes. What about a parameter
            called `models`? A hint of `list` says that it is a list, but not what is inside. Model names?
            Messages? Numbers? A reader has to open the body to find out.

            Put the type of the items in square brackets after `list`:

            ```python
            def first_word(words: list[str]) -> str:
                return words[0]

            print(first_word(["rag", "agents"]))
            # rag
            print(first_word.__annotations__)
            # {'words': list[str], 'return': <class 'str'>}
            ```

            Read `list[str]` as "list of str": a list in which every item is a string. `list[int]` is a
            list of whole numbers.

            A dict holds two kinds of things, keys and values, so its hint takes two types, separated by a
            comma. The type of the keys comes first, then the type of the values:

            ```python
            def count_models(prices: dict[str, float]) -> int:
                return len(prices)

            print(count_models({"gpt-4o": 5.0, "haiku": 0.25}))
            # 2
            ```

            Read `dict[str, float]` as "dict from str to float": text keys and decimal values.

            ```quiz
            A function has the parameter `usage: dict[str, int]`. Which value fits that hint?
            - [x] `{"input": 120, "output": 45}` :: Right. The keys are strings and the values are whole numbers.
            - [ ] `{120: "input", 45: "output"}` :: The two types are in the wrong places. The first type in the brackets is for the keys and the second is for the values, and here the keys are numbers and the values are text.
            - [ ] `{"input": "120", "output": "45"}` :: The values are text that looks like numbers. The hint says `int`, and `"120"` is a `str`. This mix-up happens often with numbers that were read from a file.
            - [ ] `["input", 120]` :: This is a list. A hint that starts with `dict` describes a dict.
            ```

            As in the last step, Python does not check any of this. The brackets are for readers and for
            tools that read the code. They also stay stored with the function:

            ```fill
            def total(prices: ___) -> float:
                return sum(prices.values())

            print(total({"a": 1.5, "b": 2.0}))
            print(total.__annotations__["prices"])
            ---
            - [x] dict[str, float] :: Right. The argument is a dict with text keys and decimal values, and the last line prints that hint.
            - [ ] list[float] :: The function reads `prices.values()`, and a list has no `values`. The argument is a dict. The last line prints `list[float]`.
            - [ ] dict[float, str] :: The types are swapped. The keys are the text and the values are the numbers, so the last line should print `dict[str, float]`.
            - [ ] dict :: This says that it is a dict and nothing more, which is where this step started. The last line prints `<class 'dict'>`.
            ```

            Older code spells these `List[str]` and `Dict[str, float]` with capital letters, imported from
            `typing`. They mean the same. Since Python 3.9 the lowercase names work without an import.

            **Watch out:** separate the two types of a dict with a comma. `dict[str: float]` is accepted
            without an error, but Python then stores something that is not `dict[str, float]`, and a check
            that compares the hints fails. Printing the stored hint shows it as a `dict[slice(...)]`.

            **In short:** `list[str]` is a list of strings and `dict[str, float]` is a dict from strings to
            floats. The types in the brackets say what the container holds.
        ''',
        "difficulty": 1,
        "hints": [
            "The lesson shows how to say what is inside a list and what is inside a dict. Look at those two boxes again, then at the three places in the first line of your function that need a hint.",
            "Two jobs: the hints, and the body. For the hints, annotate both parameters and the result. For the body, keep a running total and add one price for every model in the list. The dict method that gives back a fallback value when a key is missing is the tool for the unknown models.",
            "First line: the hint of `models` is the type for a list with the type for strings in brackets. The hint of `prices` is the type for a dict with two types in brackets, keys first, then values. After the arrow comes the type for numbers with a decimal point. Body: start a total at zero, loop over the models, add the price of each one with the fallback, and give the total back.",
        ],
        "research": {
            "note": "Skim the start of the `typing` docs page - the part about annotating functions and the table of built-in generic types like `list[int]`. Then come back.",
            "links": [
                {"title": "typing - Support for type hints (Python docs)", "url": "https://docs.python.org/3/library/typing.html"},
                {"title": "Glossary: type hint (Python docs)", "url": "https://docs.python.org/3/glossary.html#term-type-hint"},
            ],
        },
        "prompt": r'''
            Estimate what a batch of requests costs. Each request used one model, and each model has a
            price for one request.

            **Your job:** write the function `total_price(models, prices)` that gives back the sum of the
            prices of all requests. Its first line must carry type hints that say what goes in and what
            comes out. The editor holds the function with no hints and no body.

            **What goes in**
            - `models`: a list of strings, the model used by each request, for example
              `["gpt-4o", "haiku", "gpt-4o"]`
            - `prices`: a dict from the name of a model (a string) to the price of one request (a number
              with a decimal point), for example `{"gpt-4o": 5.0, "haiku": 0.25}`

            **What comes out**
            - the total price, a number with a decimal point: `10.25` for the example values

            **Rules**
            - A model that appears twice in `models` is paid for twice.
            - A model that is missing from `prices` costs `0.0`.
            - An empty list of models gives `0.0`.
            - A check reads the hints that Python stored for the function. `models` must be hinted as a list
              of strings, `prices` as a dict from strings to floats, and the result as a float. Write them
              without quotes.

            **Examples**
            ```python
            total_price(["gpt-4o", "haiku", "gpt-4o"], {"gpt-4o": 5.0, "haiku": 0.25})   # returns 10.25
            total_price(["mystery"], {"gpt-4o": 5.0})                                   # returns 0.0
            total_price([], {"gpt-4o": 5.0})                                            # returns 0.0
            ```
        ''',
        "starter": r'''
            def total_price(models, prices):
                ...
        ''',
        "tests": r'''
            from solution import total_price

            def test_sums_price_of_every_request():
                got = total_price(["gpt-4o", "haiku", "gpt-4o"], {"gpt-4o": 5.0, "haiku": 0.25})
                assert got == 10.25, f"got {got!r}"

            def test_unknown_model_costs_zero():
                got = total_price(["mystery", "haiku"], {"haiku": 0.25})
                assert got == 0.25, f"got {got!r}"

            def test_empty_list_returns_zero():
                assert total_price([], {"gpt-4o": 5.0}) == 0.0

            def test_parameters_are_annotated_list_and_dict():
                hints = total_price.__annotations__
                assert hints.get("models") == list[str], f"models annotated as {hints.get('models')!r}"
                assert hints.get("prices") == dict[str, float], f"prices annotated as {hints.get('prices')!r}"

            def test_return_is_annotated_float():
                hints = total_price.__annotations__
                assert hints.get("return") is float, f"return annotated as {hints.get('return')!r}"
        ''',
        "solution": r'''
            def total_price(models: list[str], prices: dict[str, float]) -> float:
                total = 0.0
                for model in models:
                    total += prices.get(model, 0.0)
                return total
        ''',
    },
    {
        "id": "dataclasses-1",
        "title": "A message record",
        "lesson": r'''
            ## A field that may be empty

            A chat message always has a role and a text. Some messages also carry a name, for example the
            name of the tool that produced them. Most do not. What should the `name` field of a message
            without a name hold?

            Python has a value for "nothing here": `None`. So the field holds either a string or `None`,
            and the hint `str` is not true for the second case. A hint for "this or that" puts a bar
            between the two types:

            ```python
            from dataclasses import dataclass

            @dataclass
            class Ticket:
                title: str
                owner: str | None = None

            print(Ticket("Fix login"))
            # Ticket(title='Fix login', owner=None)
            print(Ticket("Fix login", "ada"))
            # Ticket(title='Fix login', owner='ada')
            ```

            Read `str | None` as "str or None". A hint that allows any one of several types is called a
            **union type**. Older code writes the same thing as `Optional[str]`.

            The `= None` at the end is a default, as in an earlier step. A ticket made without an owner
            gets `None`, so callers may leave the argument out.

            ```fill
            from dataclasses import dataclass

            @dataclass
            class Note:
                text: str
                author: ___ = None

            print(Note.__annotations__["author"])
            ---
            - [x] str | None :: Right. The author is a string or `None`, and the last line prints `str | None`.
            - [ ] str :: The hint would say that an author is always a string, but the default is `None`. The last line prints `<class 'str'>`.
            - [ ] None :: This says that the only possible value is `None`, so a name could never be stored. The last line prints `None`.
            - [ ] str or None :: Python reads `or` as an operator that picks the first value that counts as true, and that is `str`. The hint becomes just `str`, and the last line prints `<class 'str'>`. Between types, the bar is the sign to use.
            ```

            A hint like this is a promise to the reader. A value that may be `None` has to be handled by the
            code that uses it, as in an `if`:

            ```python
            def describe(owner: str | None) -> str:
                if owner is None:
                    return "nobody"
                return "owned by " + owner

            print(describe(None))
            # nobody
            print(describe("ada"))
            # owned by ada
            ```

            ```predict
            def shout(text: str | None) -> str:
                if text is None:
                    return "(no text)"
                return text.upper()

            print(shout("hi"))
            print(shout(None))
            print(shout("") == "")
            ---
            `shout("hi")` has text, so it gives `HI`. `shout(None)` takes the first branch and gives `(no text)`. An empty string is not `None`: it is a string with no characters. So `shout("")` skips the `if`, and `"".upper()` is `""`. The comparison with `""` is `True`.
            ```

            **Watch out:** `owner: str | None` on its own does not make the argument optional.
            `str | None` only says what the value may be. Without `= None`, the call `Ticket("Fix login")`
            stops with a `TypeError` that says `missing 1 required positional argument: 'owner'`.

            **In short:** `str | None` means a string or `None`, and `= None` after it lets the caller leave
            the field out.
        ''',
        "hints": [
            "Look at the class `Ticket` in the lesson. Its last field is the kind of field you need for `name`. The other two fields are like the ones in the step where you wrote `Chunk`.",
            "You need the import, the decorator and the class line, then three field lines in the order of the task. Two fields are always given and have one type. The third is a string or nothing, and it has a value to fall back on.",
            "Write the import first, then the decorator above the class line. Under the class line, indent three lines. The first two each have a name, a colon and the type of text. The third has the name, a colon, the type of text, a bar, the word for no value, and then an equals sign and that same word for no value.",
        ],
        "difficulty": 1,
        "prompt": r'''
            A chat API takes a list of messages. Each message has a role, a text, and sometimes the name of
            the tool that produced it.

            **Your job:** write a dataclass named `Message` with three fields. The editor holds only an
            empty class with that name, and nothing is imported yet.

            **What goes in**
            - `role`: who wrote the message, a string, for example `"user"`. Always given.
            - `content`: the text of the message, a string, for example `"Hi"`. Always given.
            - `name`: the name of the tool, a string, for example `"calc"`. It may be left out, and then
              it is `None`.

            **What comes out**
            - `Message("user", "Hi")` gives an object with `.role`, `.content` and `.name`. Here `.name` is
              `None`.

            **Rules**
            - `Message` is a dataclass. A check asks Python whether it is one.
            - The fields are in the order `role`, `content`, `name`.
            - The type hints are the type of text for `role` and `content`, and "text or `None`" for `name`.
              A check compares them with the real types, so write them without quotes.
            - You write no methods. Printing and `==` come from the dataclass: two messages are equal when
              all three fields are equal. A message prints with its class name and all three fields, as in
              the last example.

            **Examples**
            ```python
            m = Message("user", "Hi")
            m.name                                    # None
            m == Message("user", "Hi")                # True
            m == Message("user", "Hi", "bob")         # False
            Message("tool", "42", name="calc")        # Message(role='tool', content='42', name='calc')
            ```
        ''',
        "starter": r'''
            class Message:
                ...
        ''',
        "tests": r'''
            import dataclasses
            from solution import Message

            def test_message_is_a_dataclass():
                assert dataclasses.is_dataclass(Message), "Message must be decorated with @dataclass"

            def test_fields_are_role_content_name_in_order():
                names = [f.name for f in dataclasses.fields(Message)]
                assert names == ["role", "content", "name"], f"fields are {names}"

            def test_name_defaults_to_none():
                m = Message("user", "Hi")
                assert m.name is None, f"name is {m.name!r}"

            def test_equality_and_printed_form():
                assert Message("user", "Hi") == Message("user", "Hi")
                assert Message("user", "Hi") != Message("user", "Hi", "bob")
                r = repr(Message("tool", "42", name="calc"))
                assert r == "Message(role='tool', content='42', name='calc')", f"repr is {r}"

            def test_type_hints_are_str_str_and_optional_str():
                hints = Message.__annotations__
                assert hints.get("role") is str and hints.get("content") is str, f"annotations: {hints}"
                assert hints.get("name") == (str | None), f"name annotated as {hints.get('name')!r}"
        ''',
        "solution": r'''
            from dataclasses import dataclass


            @dataclass
            class Message:
                role: str
                content: str
                name: str | None = None
        ''',
    },
    {
        "id": "dataclasses-2",
        "title": "Mutable defaults",
        "lesson": r'''
            ## Give every object its own empty collection

            Two new chats both start with no messages. That does not mean they should share one empty list: adding a message to the first chat must not change the second. You need a new list each time an object is created.

            ```python
            from dataclasses import dataclass, field
            @dataclass
            class Folder:
                files: list[str] = field(default_factory=list)

            a = Folder()
            b = Folder()
            a.files.append("notes.txt")
            print(a.files, b.files)
            # ['notes.txt'] []
            ```

            `field` describes options for one dataclass field. The `default_factory` option receives a function that will make a default value when needed. A function used this way is called a **factory**. Passing `list` lets the generated constructor call it separately for each object that needs a default.

            ```fill
            from dataclasses import dataclass, field
            @dataclass
            class Folder:
                labels: dict[str, str] = field(default_factory=___)
            print(Folder().labels)
            ---
            - [x] dict :: Calling dict without arguments produces a fresh empty dictionary.
            - [ ] list :: That would produce an empty list, despite the dictionary type hint.
            - [ ] dict() :: That passes a dictionary value instead of a callable factory and fails during construction.
            ```

            An explicit value still wins. If the caller supplies a collection, the constructor stores that collection instead of calling the factory. The factory only answers the question, "What should this field contain when nothing was supplied?"

            Lists and dictionaries are **mutable**, meaning their contents can change. Dataclasses reject common mutable defaults such as an actual empty list in the class declaration, because sharing that object would usually be a mistake.

            **Watch out:** `default_factory=list()` calls the function too early. Construction later fails because the resulting list is not callable. Give Python the function, without parentheses.

            **In short:** a default factory creates a fresh collection for each object that needs a default.
        ''',
        "hints": [
            "Ask when each default collection must be created.",
            "Use field options that describe how to make a fresh collection, rather than supplying one already-created collection.",
            "Declare fields in the required order. Give the numeric setting its scalar default and give each collection a factory for its required type, without calling that factory yourself.",
        ],
        "difficulty": 1,
        "prompt": r'''
            A model config holds the settings sent with every LLM request, including a list
            of stop sequences and some free-form metadata.

            **Your job:** write a dataclass `class ModelConfig` with four fields, in this order:

            **What goes in**

            - `model`: type hint `str`, e.g. `"gpt-4o"` (required)
            - `temperature`: type hint `float`, e.g. `0.0`; defaults to `0.7`
            - `stop`: type hint `list[str]`, e.g. `["###"]`; defaults to an **empty list**
            - `metadata`: type hint `dict[str, str]`, e.g. `{"env": "prod"}`; defaults to an **empty dict**

            **What comes out**
            - A `ModelConfig` instance with the four fields above. Omitted collection fields receive independent fresh defaults, while explicitly supplied values are retained.

            **Rules**
            - Every new object must get its **own** fresh list and dict: appending to one
              config's `stop` (or adding a key to its `metadata`) must not change another's.
            - `stop` and `metadata` must use a *default factory* (`field(default_factory=...)`);
              a check looks for it.
            - All four fields can also be passed explicitly (by position or by keyword).

            **Examples**
            ```python
            ModelConfig("gpt-4o")
            # ModelConfig(model='gpt-4o', temperature=0.7, stop=[], metadata={})
            a = ModelConfig("gpt-4o")
            b = ModelConfig("gpt-4o")
            a.stop.append("END")
            b.stop        # []
            ModelConfig("claude", temperature=0.0, stop=["###"], metadata={"env": "prod"}).stop   # ["###"]
            ```
        ''',
        "starter": r'''
            from dataclasses import dataclass


            @dataclass
            class ModelConfig:
                ...
        ''',
        "tests": r'''
            import dataclasses
            from solution import ModelConfig

            def test_defaults_are_0_7_empty_list_empty_dict():
                c = ModelConfig("gpt-4o")
                assert (c.model, c.temperature, c.stop, c.metadata) == ("gpt-4o", 0.7, [], {}), f"got {c!r}"

            def test_stop_lists_are_not_shared():
                a, b = ModelConfig("m"), ModelConfig("m")
                a.stop.append("END")
                assert b.stop == [], f"b.stop changed to {b.stop!r} after appending to a.stop"

            def test_metadata_dicts_are_not_shared():
                a, b = ModelConfig("m"), ModelConfig("m")
                a.metadata["user"] = "x"
                assert b.metadata == {}, f"b.metadata is {b.metadata!r}"

            def test_explicit_values_are_used():
                c = ModelConfig("claude", temperature=0.0, stop=["###"], metadata={"env": "prod"})
                assert c.stop == ["###"] and c.metadata == {"env": "prod"} and c.temperature == 0.0

            def test_stop_and_metadata_use_default_factory():
                fs = {f.name: f for f in dataclasses.fields(ModelConfig)}
                assert fs["stop"].default_factory is not dataclasses.MISSING, "stop needs a default factory"
                assert fs["metadata"].default_factory is not dataclasses.MISSING, "metadata needs a default factory"
        ''',
        "solution": r'''
            from dataclasses import dataclass, field


            @dataclass
            class ModelConfig:
                model: str
                temperature: float = 0.7
                stop: list[str] = field(default_factory=list)
                metadata: dict[str, str] = field(default_factory=dict)
        ''',
    },
    {
        "id": "dataclasses-8",
        "title": "Reject bad chunks",
        "lesson": r'''
            ## Reject bad values during construction

            A record can have the correct field names but impossible values. A retry budget of negative five is still an integer. You need to reject it when the object is built, before another part of your program tries to use it.

            ```python
            from dataclasses import dataclass
            @dataclass
            class Budget:
                retries: int
                def __post_init__(self):
                    if self.retries < 0:
                        raise ValueError("negative retry budget")

            print(Budget(2))
            # Budget(retries=2)
            ```

            The generated constructor first stores the fields, then calls `__post_init__` if you defined it. That gives your method access to all the supplied values through `self`. Checking those values and rejecting unacceptable ones is called **validation**.

            ```quiz
            Does the annotation `retries: int` reject a negative number?
            - [x] No :: A type hint documents an expected type. It does not enforce a permitted range at runtime.
            - [ ] Yes, all integer fields must be positive :: Integers include negative numbers; the required range depends on your application.
            ```

            Raising an exception stops construction instead of returning a successfully created object to the caller. If the values are acceptable, let the method finish without returning anything. You do not need to rebuild the object: the generated constructor already stored its fields.

            Remember the string method `strip`? It returns a version without surrounding whitespace, so you can test whether text contains anything besides spaces or line breaks. Checking that result does not require replacing the original text.

            ```predict
            label = "  useful  "
            print(bool(label.strip()))
            print(repr(label))
            ---
            The stripped copy contains letters, so the first line is True. The original label still includes its surrounding spaces.
            ```

            **Watch out:** `__post_init__` runs at creation, not on later assignments. If you need every write checked, use the property approach from Classes.

            **In short:** validate stored fields in `__post_init__` and raise before invalid objects reach the rest of the app.
        ''',
        "difficulty": 1,
        "hints": [
            "The generated constructor has a hook for checks after field assignment.",
            "Check blankness independently from the page boundary. Valid text should keep its original spaces.",
            "Define the post-construction method, reject text with nothing left after surrounding whitespace is removed, then reject pages below the permitted minimum. Otherwise let construction finish.",
        ],
        "research": {
            "note": "Read the short 'Post-init processing' section of the dataclasses docs: when is `__post_init__` called, and what can it do? Then come back.",
            "links": [
                {"title": "dataclasses - Post-init processing (Python docs)", "url": "https://docs.python.org/3/library/dataclasses.html#post-init-processing"},
            ],
        },
        "prompt": r'''
            A chunk with no text, or on page `0`, is a bug upstream in your pipeline. Catch it
            the moment the object is created.

            **Your job:** write a `__post_init__(self)` method inside the `Chunk` dataclass (the fields
            are already there).

            **What goes in**

            - `self.text`: a `str`, the chunk's text, e.g. `"Hello"`
            - `self.page`: an `int`, e.g. `3`; defaults to `1`

            **What comes out**
            - nothing - it only checks

            **Rules**
            - If `text` is empty or only whitespace (e.g. `""`, `"   "`), raise `ValueError`.
            - If `page` is less than `1` (e.g. `0`, `-2`), raise `ValueError`.
            - Valid chunks are created normally, with their fields unchanged.

            **Examples**
            ```python
            Chunk("Hello")         # Chunk(text='Hello', page=1)
            Chunk("Bye", 3).page   # 3
            Chunk("   ")           # raises ValueError
            Chunk("Hello", 0)      # raises ValueError
            ```
        ''',
        "starter": r'''
            from dataclasses import dataclass


            @dataclass
            class Chunk:
                text: str
                page: int = 1
        ''',
        "tests": r'''
            from solution import Chunk

            def raises_value_error(*args):
                try:
                    Chunk(*args)
                except ValueError:
                    return True
                return False

            def test_valid_chunks_are_created_normally():
                c = Chunk("Hello")
                assert (c.text, c.page) == ("Hello", 1), f"got {c!r}"
                assert Chunk("Bye", 3).page == 3

            def test_empty_text_raises_value_error():
                assert raises_value_error(""), "Chunk('') should raise ValueError"

            def test_whitespace_only_text_raises_value_error():
                assert raises_value_error("   "), "Chunk('   ') should raise ValueError"

            def test_page_below_one_raises_value_error():
                assert raises_value_error("Hello", 0), "page 0 should raise ValueError"
                assert raises_value_error("Hello", -2), "page -2 should raise ValueError"
        ''',
        "solution": r'''
            from dataclasses import dataclass


            @dataclass
            class Chunk:
                text: str
                page: int = 1

                def __post_init__(self):
                    if not self.text.strip():
                        raise ValueError("chunk text is empty")
                    if self.page < 1:
                        raise ValueError(f"page must be >= 1, got {self.page}")
        ''',
    },
    {
        "id": "dataclasses-3",
        "title": "Roles and validation",
        "lesson": r'''
            ## Replace loose labels with known choices

            Your app accepts a small set of states, but incoming data contains ordinary strings. A typo should fail at the boundary instead of quietly becoming a new state. Python can represent each permitted choice as a named value.

            ```python
            from enum import Enum
            class Phase(Enum):
                QUEUED = "queued"
                DONE = "done"

            phase = Phase("done")
            print(phase is Phase.DONE)
            # True
            print(phase.value)
            # done
            ```

            This is an **enumeration**, or **Enum**. `Phase.DONE` is a member of that enumeration, not an ordinary string. Calling `Phase` with a known underlying value finds its member. Passing a member that already belongs to `Phase` keeps that same member.

            ```predict
            from enum import Enum
            class Phase(Enum):
                QUEUED = "queued"
                DONE = "done"
            print(Phase(Phase.QUEUED) is Phase.QUEUED)
            print(Phase("done").value)
            ---
            The constructor accepts the existing member unchanged. Reading value on the other member gives the plain string done.
            ```

            Putting this conversion in `__post_init__` lets callers use convenient strings while the rest of your program receives a consistent member type. An unknown value raises `ValueError`. When exporting ordinary data, read the member's `.value` rather than returning the member itself.

            Your validation can then depend on the selected member. For example, different states may permit different missing fields. Check a value's type before calling methods that require that type; otherwise your caller gets an accidental `AttributeError` instead of the intended error.

            ```quiz
            A field must contain text, but the caller passes a list. Which check should happen before testing whether the text is blank?
            - [x] Check that it is a string :: Only then can string-specific blank checks be used reliably.
            - [ ] Call strip immediately :: A list has no strip method, so this produces the wrong kind of error.
            ```

            **Watch out:** comparing an Enum member directly with its string value gives false. Compare members with members, or explicitly read `.value`.

            **In short:** normalize known labels into Enum members at creation, then export their plain values when needed.
        ''',
        "hints": [
            "Separate converting the role from checking the message content.",
            "Normalize the role to an Enum member first. Check the content type before any string operation, then apply the blank-content exception for tools.",
            "Declare the four members and two dataclass fields. In post-initialization, normalize the role, validate content type and blankness, and export a new dictionary using the member's plain value.",
        ],
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            Chat messages should only ever have a known role and real text. Catch bad
            messages the moment they are created, before they reach the API.

            **Your job:** write
            1. An Enum `class Role` with exactly four members, named `SYSTEM`, `USER`,
               `ASSISTANT`, `TOOL`, whose values are the lowercase strings `"system"`, `"user"`,
               `"assistant"`, `"tool"`.
            2. A dataclass `class ChatMessage` with two fields, in this order:
               - `role`: type hint `Role`; may be passed as a `Role` member (`Role.USER`) or as a
                 plain string (`"user"`)
               - `content`: type hint `str`, e.g. `"Hi"`
            3. A method `to_dict(self)`.
               - **What comes out:** a dict `{"role": <role as a plain string>, "content": <content>}`,
                 e.g. `{"role": "user", "content": "Hi"}`

            **What goes in**

            **What comes out**
            - A validated `ChatMessage` whose role is always a `Role` member. Its `to_dict()` result contains the plain role string and content.

            **Rules** (checked when the object is created, in `__post_init__`):
            - A string role is converted to the matching `Role` member, so `.role` is always a
              `Role` (e.g. `ChatMessage("assistant", "ok").role is Role.ASSISTANT`).
            - A role that is already a `Role` member is kept as it is.
            - An unknown role such as `"robot"` raises `ValueError`.
            - If `content` is not a `str` (e.g. `42`, `None`, `["hi"]`), raise `TypeError`.
            - If `content` is empty or only whitespace (e.g. `""`, `"   "`), raise `ValueError` -
              **except** when the role is `TOOL`, where empty content is allowed.
            - In `to_dict()`, the role must be the plain string value (`"user"`), not the `Role` member.

            **Examples**
            ```python
            ChatMessage("user", "Hi").role              # Role.USER
            ChatMessage(Role.SYSTEM, "Be brief").role   # Role.SYSTEM
            ChatMessage("user", "Hi").to_dict()         # {"role": "user", "content": "Hi"}
            ChatMessage(Role.TOOL, "").to_dict()        # {"role": "tool", "content": ""}
            ChatMessage("robot", "Hi")                  # raises ValueError
            ChatMessage("user", 42)                     # raises TypeError
            ChatMessage("user", "   ")                  # raises ValueError
            ```
        ''',
        "starter": r'''
            from dataclasses import dataclass
            from enum import Enum


            class Role(Enum):
                ...


            @dataclass
            class ChatMessage:
                ...
        ''',
        "tests": r'''
            import dataclasses
            from enum import Enum
            from solution import Role, ChatMessage

            def test_role_enum_has_four_members_with_lowercase_values():
                assert issubclass(Role, Enum), "Role must be an Enum"
                got = {m.name: m.value for m in Role}
                assert got == {"SYSTEM": "system", "USER": "user", "ASSISTANT": "assistant", "TOOL": "tool"}, f"got {got}"

            def test_string_role_converted_to_role_member():
                m = ChatMessage("assistant", "ok")
                assert m.role is Role.ASSISTANT, f"role is {m.role!r}"
                assert dataclasses.is_dataclass(ChatMessage)

            def test_role_member_kept_as_is():
                assert ChatMessage(Role.SYSTEM, "Be brief").role is Role.SYSTEM

            def test_unknown_role_raises_value_error():
                try:
                    ChatMessage("robot", "hi")
                except ValueError:
                    return
                assert False, "unknown role should raise ValueError"

            def test_non_string_content_raises_type_error():
                for bad in (42, None, ["hi"]):
                    try:
                        ChatMessage("user", bad)
                    except TypeError:
                        continue
                    assert False, f"content={bad!r} should raise TypeError"

            def test_blank_content_raises_value_error_except_for_tool():
                for role in ("user", Role.SYSTEM, "assistant"):
                    try:
                        ChatMessage(role, "   ")
                    except ValueError:
                        continue
                    assert False, f"blank content with role {role!r} should raise ValueError"
                assert ChatMessage("tool", "").content == ""

            def test_to_dict_uses_plain_string_role():
                got = ChatMessage("user", "Hi").to_dict()
                assert got == {"role": "user", "content": "Hi"}, f"got {got!r}"
                assert type(got["role"]) is str, "role in to_dict() must be a plain string"
        ''',
        "solution": r'''
            from dataclasses import dataclass
            from enum import Enum


            class Role(Enum):
                SYSTEM = "system"
                USER = "user"
                ASSISTANT = "assistant"
                TOOL = "tool"


            @dataclass
            class ChatMessage:
                role: Role
                content: str

                def __post_init__(self):
                    self.role = Role(self.role)
                    if not isinstance(self.content, str):
                        raise TypeError("content must be a string")
                    if not self.content.strip() and self.role is not Role.TOOL:
                        raise ValueError("content must not be empty")

                def to_dict(self) -> dict[str, str]:
                    return {"role": self.role.value, "content": self.content}
        ''',
    },
    {
        "id": "dataclasses-4",
        "title": "Frozen, ordered options",
        "lesson": r'''
            ## Create a changed record without changing the original

            A saved configuration may be used by several requests. Changing it for one request could alter all the others. You want a new version while keeping the original stable, and you may also want records to sort by their fields.

            ```python
            from dataclasses import dataclass, replace
            @dataclass(frozen=True, order=True)
            class Edition:
                major: int
                minor: int

            old = Edition(2, 1)
            new = replace(old, minor=3)
            print(old, new)
            # Edition(major=2, minor=1) Edition(major=2, minor=3)
            ```

            The option `frozen=True` prevents ordinary assignments to fields. `replace` constructs another object, copying the fields you did not mention. The original remains useful as a record of the previous configuration.

            The option `order=True` generates comparisons such as `<`. Fields are compared in declaration order: the first unequal field decides the result. Only when earlier fields tie do later ones matter.

            ```predict
            from dataclasses import dataclass
            @dataclass(order=True)
            class Edition:
                major: int
                minor: int
            print(Edition(1, 9) < Edition(2, 0))
            ---
            The major field is compared first. Since 1 is smaller than 2, the minor values never decide the comparison.
            ```

            Frozen records with hashable fields can also be keys in dictionaries or members of sets. **Hashable** means Python can calculate a stable lookup value for the object. Ordinary integers and strings support this; a list does not. Freezing a dataclass does not make a list inside it hashable or prevent changes to that list.

            ```quiz
            Two equal frozen records with integer fields are added to a set. How many distinct values remain?
            - [x] One :: Sets keep one representative of equal hashable values.
            - [ ] Two :: They may be separate objects, but set membership uses their value equality.
            ```

            **Watch out:** assigning directly to a frozen field raises `FrozenInstanceError`. Build a replacement instead of trying to edit it.

            **In short:** frozen records preserve old values, replacement creates new ones, and field order determines generated sorting.
        ''',
        "hints": [
            "Review the dataclass options for preventing assignment and generating comparisons.",
            "Declaration order supplies the sorting priority. A discount should create another object because the original is read-only.",
            "Declare the fields in the specified order with frozen and ordering enabled. Calculate and round the discounted cost, then construct a replacement retaining the other two fields.",
        ],
        "difficulty": 2,
        "prompt": r'''
            A router picks the cheapest, fastest model. Model each option as a read-only
            record that can be sorted and put in a set.

            **Your job:** write a dataclass `class ModelOption` with three fields, in this order:

            **What goes in**

            - `cost_per_1k`: a `float`, price per 1000 tokens, e.g. `0.5`
            - `latency_ms`: an `int`, e.g. `300`
            - `name`: a `str`, e.g. `"small"`

            and a method `discounted(self, pct)`:

            - `pct`: a number, the discount in percent, e.g. `20`
            - **What comes out:** a **new** `ModelOption` with the same `latency_ms` and `name` and cost
              `cost_per_1k * (1 - pct / 100)` **rounded to 6 decimals** (`round(x, 6)`)

            **What comes out**
            - A sortable, frozen `ModelOption`. `discounted()` gives back a new option with the rounded discounted cost and the other fields preserved.

            **Rules**
            - Options are **immutable** (*frozen*): assigning to a field, e.g. `o.cost_per_1k = 0.1`,
              must raise `dataclasses.FrozenInstanceError`.
            - Options are **hashable**: equal options count once in a set.
            - Options are **orderable**: `sorted()` and `min()` compare by `cost_per_1k`, then
              `latency_ms`, then `name`.
            - `discounted()` must not change the original option.

            **Examples**
            ```python
            a = ModelOption(0.5, 300, "small")
            b = ModelOption(0.5, 120, "fast")
            sorted([a, b])[0].name                       # "fast"
            a.discounted(20)            # ModelOption(cost_per_1k=0.4, latency_ms=300, name='small')
            a.cost_per_1k                                # 0.5 (unchanged)
            ModelOption(0.3, 10, "m").discounted(10).cost_per_1k   # 0.27
            len({a, ModelOption(0.5, 300, "small")})     # 1
            ```
        ''',
        "starter": r'''
            from dataclasses import dataclass


            class ModelOption:
                ...
        ''',
        "tests": r'''
            import dataclasses
            from solution import ModelOption

            def test_sorts_by_cost_then_latency_then_name():
                opts = [ModelOption(1.0, 100, "b"), ModelOption(0.5, 300, "small"),
                        ModelOption(0.5, 120, "fast"), ModelOption(1.0, 100, "a")]
                got = [o.name for o in sorted(opts)]
                assert got == ["fast", "small", "a", "b"], f"sorted order: {got}"
                assert min(opts).name == "fast"

            def test_assigning_a_field_raises_frozen_instance_error():
                o = ModelOption(0.5, 300, "small")
                try:
                    o.cost_per_1k = 0.1
                except dataclasses.FrozenInstanceError:
                    return
                assert False, "assigning to a field should raise FrozenInstanceError"

            def test_options_are_hashable_in_a_set():
                s = {ModelOption(0.5, 300, "x"), ModelOption(0.5, 300, "x"), ModelOption(0.1, 1, "y")}
                assert len(s) == 2, f"set has {len(s)} items"

            def test_discounted_returns_new_option_and_keeps_original():
                a = ModelOption(0.5, 300, "small")
                d = a.discounted(20)
                assert d == ModelOption(0.4, 300, "small"), f"got {d!r}"
                assert a.cost_per_1k == 0.5, "original must be unchanged"
                assert isinstance(d, ModelOption)

            def test_discounted_cost_rounded_to_6_decimals():
                d = ModelOption(0.3, 10, "m").discounted(10)
                assert d.cost_per_1k == 0.27, f"got {d.cost_per_1k!r}"
        ''',
        "solution": r'''
            from dataclasses import dataclass, replace


            @dataclass(frozen=True, order=True)
            class ModelOption:
                cost_per_1k: float
                latency_ms: int
                name: str

                def discounted(self, pct: float) -> "ModelOption":
                    return replace(self, cost_per_1k=round(self.cost_per_1k * (1 - pct / 100), 6))
        ''',
    },
    {
        "id": "dataclasses-5",
        "title": "Typed completion response",
        "lesson": r'''
            ## Put nested records together at the boundary

            A response dictionary contains several layers of data. You want the rest of your application to read named objects, while still being able to export ordinary dictionaries again. Plan the conversion one level at a time: each inner record must exist before you build the outer one.

            ```python
            from dataclasses import dataclass, asdict
            @dataclass
            class Limit:
                count: int
            @dataclass
            class Job:
                label: str
                limit: Limit

            print(asdict(Job("scan", Limit(4))))
            # {'label': 'scan', 'limit': {'count': 4}}
            ```

            `asdict` follows nested dataclasses and produces plain dictionaries. It includes declared fields, not every attribute-like operation your class provides. A value computed by a `@property`, such as a total derived from two fields, is not itself a dataclass field.

            A method that constructs an object from another data format often belongs to the class rather than an existing instance. `@classmethod` gives such a method the class as its first argument, conventionally called `cls`. Calling `cls(...)` builds the result.

            ```python
            from dataclasses import dataclass
            @dataclass
            class Limit:
                count: int
                @classmethod
                def from_text(cls, text):
                    return cls(int(text))
            print(Limit.from_text("8"))
            # Limit(count=8)
            ```

            For a field limited to exact values, `Literal` from `typing` can document the choices. `get_args` retrieves those choices, but validation still needs your own check.

            ```predict
            from typing import Literal, get_args
            Mode = Literal["brief", "full"]
            print("brief" in get_args(Mode))
            print("other" in get_args(Mode))
            ---
            get_args returns the declared choices. Membership can be used by your validation code; the annotation does not validate incoming values by itself.
            ```

            When reading optional data, distinguish absent data from a valid empty collection. Preserve `None` where it is meaningful, and read only the keys that belong to your records. Building new objects should not require deleting keys from the caller's dictionary.

            **Watch out:** passing a nested dictionary directly to a field annotated with a dataclass does not convert it. Python stores that dictionary unchanged unless your conversion code builds the inner object.

            **In short:** build inner records explicitly, use class methods for alternate constructors, and export declared fields with `asdict`.
        ''',
        "hints": [
            "Draw the response as an outer record containing lists and smaller records.",
            "Build the message inside each choice, and build choices before the completion. Keep the token total computed rather than stored as a field.",
            "Define the four records, validate allowed finish reasons on each choice, and add the computed property. In the class method, read needed keys and construct inner objects, preserving optional None values. Export with dataclass conversion.",
        ],
        "difficulty": 3,
        "prompt": r'''
            A chat-completion API returns a nested JSON dict. Turn it into typed objects so
            the rest of your app can use `c.choices[0].message.content` instead of raw keys.

            **Your job:** write four dataclasses (fields in exactly this order) and two methods:

            **What goes in**

            - `Usage`: `prompt_tokens` (int), `completion_tokens` (int), plus a read-only
              **property** `total_tokens` (their sum). It is **not** a field.
            - `Message`: `role: str`, `content` (str or None)
            - `Choice`: `index: int`, `message` (Message),
              `finish_reason: Literal["stop", "length", "tool_calls"] | None`
            - `Completion`: `id: str`, `model: str`, `choices` (list of Choice objects), `usage` (Usage or None)
            - a **classmethod** `Completion.from_dict(data)`
              - `data`: the raw response dict (see the example below)
              - **What comes out:** a `Completion` whose `choices` are `Choice` objects, each with a
                `Message` object, and whose `usage` is a `Usage` object (or `None`)
            - a method `to_dict(self)` on `Completion`
              - **What comes out:** a plain dict with exactly the keys `id`, `model`, `choices`, `usage`;
                each choice is `{"index": ..., "message": {"role": ..., "content": ...}, "finish_reason": ...}`
                and `usage` is `{"prompt_tokens": ..., "completion_tokens": ...}` or `None`

            **What comes out**
            - Nested dataclass objects for the response, a computed token total, and a plain dictionary export that can be read back without losing the specified data.

            **Rules**
            - Creating a `Choice` with a `finish_reason` other than `"stop"`, `"length"`,
              `"tool_calls"` or `None` raises `ValueError` (e.g. `Choice(0, m, "done")`).
            - `from_dict` ignores keys it does not need (`"object"`, `"created"`, `"logprobs"`, ...).
            - A missing `"usage"` key, or `"usage": None`, gives `usage=None`.
            - A message `content` of `None` stays `None`.
            - `Completion.from_dict(c.to_dict())` gives back the same data (round trip).
            - `from_dict` must not modify the dict it is given.

            **Examples**
            ```python
            raw = {"id": "c1", "object": "chat.completion", "model": "gpt-4o",
                   "choices": [{"index": 0, "finish_reason": "stop",
                                "message": {"role": "assistant", "content": "Hi"}}],
                   "usage": {"prompt_tokens": 5, "completion_tokens": 2}}
            c = Completion.from_dict(raw)
            c.choices[0].message.content     # "Hi"
            c.usage.total_tokens             # 7
            c.to_dict()
            # {"id": "c1", "model": "gpt-4o",
            #  "choices": [{"index": 0, "message": {"role": "assistant", "content": "Hi"},
            #               "finish_reason": "stop"}],
            #  "usage": {"prompt_tokens": 5, "completion_tokens": 2}}
            Choice(0, Message("assistant", "x"), "done")   # raises ValueError
            ```
        ''',
        "starter": r'''
            from dataclasses import dataclass
            from typing import Literal


            @dataclass
            class Usage:
                ...


            @dataclass
            class Message:
                ...


            @dataclass
            class Choice:
                ...


            @dataclass
            class Completion:
                ...
        ''',
        "tests": r'''
            import dataclasses
            from solution import Usage, Message, Choice, Completion

            RAW = {"id": "c1", "object": "chat.completion", "created": 1700000000, "model": "gpt-4o",
                   "choices": [
                       {"index": 0, "finish_reason": "stop", "logprobs": None,
                        "message": {"role": "assistant", "content": "Hi"}},
                       {"index": 1, "finish_reason": "tool_calls",
                        "message": {"role": "assistant", "content": None}},
                   ],
                   "usage": {"prompt_tokens": 5, "completion_tokens": 2}}

            def test_from_dict_builds_nested_objects():
                c = Completion.from_dict(RAW)
                assert isinstance(c, Completion)
                assert all(isinstance(ch, Choice) for ch in c.choices), "choices must be Choice objects"
                assert isinstance(c.choices[0].message, Message), "message must be a Message object"
                assert isinstance(c.usage, Usage), "usage must be a Usage object"
                assert c.choices[1].message.content is None

            def test_total_tokens_is_property_not_field():
                u = Usage(5, 2)
                assert u.total_tokens == 7, f"got {u.total_tokens!r}"
                names = [f.name for f in dataclasses.fields(Usage)]
                assert names == ["prompt_tokens", "completion_tokens"], f"Usage fields: {names}"

            def test_missing_or_null_usage_gives_none():
                raw = {k: v for k, v in RAW.items() if k != "usage"}
                assert Completion.from_dict(raw).usage is None
                assert Completion.from_dict({**RAW, "usage": None}).usage is None

            def test_invalid_finish_reason_raises_value_error():
                m = Message("assistant", "x")
                assert Choice(0, m, None).finish_reason is None
                assert Choice(0, m, "length").finish_reason == "length"
                try:
                    Choice(0, m, "done")
                except ValueError:
                    return
                assert False, "finish_reason 'done' should raise ValueError"

            def test_to_dict_gives_plain_dict_and_round_trips():
                got = Completion.from_dict(RAW).to_dict()
                expected = {"id": "c1", "model": "gpt-4o",
                            "choices": [
                                {"index": 0, "message": {"role": "assistant", "content": "Hi"}, "finish_reason": "stop"},
                                {"index": 1, "message": {"role": "assistant", "content": None}, "finish_reason": "tool_calls"},
                            ],
                            "usage": {"prompt_tokens": 5, "completion_tokens": 2}}
                assert got == expected, f"got {got!r}"
                assert Completion.from_dict(got).to_dict() == expected, "round trip changed the data"

            def test_from_dict_does_not_modify_input():
                import copy
                raw = copy.deepcopy(RAW)
                Completion.from_dict(raw)
                assert raw == RAW, "from_dict must not modify its input"
        ''',
        "solution": r'''
            from dataclasses import dataclass, asdict
            from typing import Literal, get_args

            FinishReason = Literal["stop", "length", "tool_calls"]


            @dataclass
            class Usage:
                prompt_tokens: int
                completion_tokens: int

                @property
                def total_tokens(self) -> int:
                    return self.prompt_tokens + self.completion_tokens


            @dataclass
            class Message:
                role: str
                content: str | None


            @dataclass
            class Choice:
                index: int
                message: Message
                finish_reason: FinishReason | None

                def __post_init__(self):
                    if self.finish_reason is not None and self.finish_reason not in get_args(FinishReason):
                        raise ValueError(f"invalid finish_reason: {self.finish_reason!r}")


            @dataclass
            class Completion:
                id: str
                model: str
                choices: list[Choice]
                usage: Usage | None

                @classmethod
                def from_dict(cls, data: dict) -> "Completion":
                    usage = data.get("usage")
                    return cls(
                        id=data["id"],
                        model=data["model"],
                        choices=[
                            Choice(
                                index=ch["index"],
                                message=Message(ch["message"]["role"], ch["message"].get("content")),
                                finish_reason=ch.get("finish_reason"),
                            )
                            for ch in data["choices"]
                        ],
                        usage=Usage(usage["prompt_tokens"], usage["completion_tokens"]) if usage else None,
                    )

                def to_dict(self) -> dict:
                    return asdict(self)
        ''',
    },
    {
        "id": "dataclasses-6",
        "title": "Generic dict-to-dataclass",
        "hints": [
            "How can you inspect a dataclass's fields and resolved type hints without knowing its name?",
            "Use a conversion helper that handles optional values, lists, and nested dataclasses. Leave ordinary values unchanged.",
            "Resolve hints, visit declared fields, and convert supplied values according to their hints. For absent fields, let existing defaults apply or raise for a required field. Construct the class from the converted named values; repeat the same process for nested records.",
        ],
        "difficulty": 3,
        "prompt": r'''
            Libraries like Pydantic turn nested JSON into typed objects automatically by reading
            the class's type hints. Build a small version that works for **any** dataclass.

            **Your job:** write `from_dict(cls, data)`

            **What goes in**

            - `cls`: a dataclass (the class itself, not an object), e.g. `Turn`
            - `data`: a dict, possibly nested, e.g. `{"role": "user", "reply_to": {"role": "assistant"}}`

            **What comes out**
            - an instance of `cls` built from `data`

            **Rules**
            - For each field of `cls`: if its key is in `data`, use (converted) `data[key]`.
            - If the key is missing, the field's default or default factory is used (a default
              factory must still give a **fresh** list per object).
            - If the key is missing and the field has no default, raise `ValueError` whose
              message contains the field name (e.g. `"settings"`).
            - A field whose type hint is a dataclass is converted from its dict with the same rule
              applied again to that inner dict (this is called *recursion*).
            - `list[X]` where `X` is a dataclass: convert every element. Lists of plain values
              (e.g. `list[str]`) are used unchanged.
            - `X | None` (or `Optional[X]`) with a dataclass `X`: `None` stays `None`, a dict is converted.
            - Anything else is used as-is. Keys in `data` that are not fields are ignored.
            - Must work from the type hints, not from specific class names. Note that
              `models.py` starts with `from __future__ import annotations`, a line that makes Python
              keep annotations as text, so its raw annotations are strings - `typing.get_type_hints(cls)` gives the real types.

            The tests use the dataclasses defined in `models.py` (already in your folder):

            ```python
            @dataclass
            class ToolCall:
                name: str
                arguments: dict[str, str] = field(default_factory=dict)

            @dataclass
            class Turn:
                role: str
                tool_calls: list[ToolCall] = field(default_factory=list)
                reply_to: "Turn | None" = None

            @dataclass
            class Settings:
                model: str
                temperature: float = 0.7
                tags: list[str] = field(default_factory=list)

            @dataclass
            class Conversation:
                id: str
                settings: Settings
                turns: list[Turn]
            ```

            **Examples**
            ```python
            from_dict(Settings, {"model": "gpt-4o"})
            # Settings(model='gpt-4o', temperature=0.7, tags=[])
            from_dict(Turn, {"role": "assistant", "tool_calls": [{"name": "search"}]})
            # Turn(role='assistant', tool_calls=[ToolCall(name='search', arguments={})], reply_to=None)
            from_dict(Turn, {"role": "user", "reply_to": {"role": "assistant"}}).reply_to
            # Turn(role='assistant', tool_calls=[], reply_to=None)
            from_dict(Conversation, {"id": "c1", "turns": []})
            # raises ValueError (message mentions "settings")
            ```
        ''',
        "starter": r'''
            def from_dict(cls, data):
                ...
        ''',
        "setup_files": {
            "models.py": r'''
                from __future__ import annotations

                from dataclasses import dataclass, field


                @dataclass
                class ToolCall:
                    name: str
                    arguments: dict[str, str] = field(default_factory=dict)


                @dataclass
                class Turn:
                    role: str
                    tool_calls: list[ToolCall] = field(default_factory=list)
                    reply_to: Turn | None = None


                @dataclass
                class Settings:
                    model: str
                    temperature: float = 0.7
                    tags: list[str] = field(default_factory=list)


                @dataclass
                class Conversation:
                    id: str
                    settings: Settings
                    turns: list[Turn]
            ''',
        },
        "tests": r'''
            from solution import from_dict
            from models import ToolCall, Turn, Settings, Conversation

            def test_flat_dataclass_uses_defaults_and_fresh_lists():
                s = from_dict(Settings, {"model": "gpt-4o"})
                assert s == Settings("gpt-4o", 0.7, []), f"got {s!r}"
                assert from_dict(Settings, {"model": "m"}).tags is not s.tags, "default factory must give fresh lists"

            def test_list_of_dataclasses_converted():
                t = from_dict(Turn, {"role": "assistant", "tool_calls": [{"name": "search", "arguments": {"q": "x"}}]})
                assert t == Turn("assistant", [ToolCall("search", {"q": "x"})]), f"got {t!r}"
                assert isinstance(t.tool_calls[0], ToolCall)

            def test_optional_dataclass_converted_or_stays_none():
                t = from_dict(Turn, {"role": "user", "reply_to": {"role": "assistant"}})
                assert isinstance(t.reply_to, Turn), f"reply_to is {t.reply_to!r}"
                assert t.reply_to.reply_to is None
                assert from_dict(Turn, {"role": "user", "reply_to": None}).reply_to is None

            def test_deep_nesting_and_unknown_keys_ignored():
                data = {"id": "c1", "extra": 1,
                        "settings": {"model": "claude", "tags": ["a"], "junk": True},
                        "turns": [{"role": "user"}, {"role": "assistant", "tool_calls": [{"name": "calc"}]}]}
                c = from_dict(Conversation, data)
                expected = Conversation("c1", Settings("claude", 0.7, ["a"]),
                                        [Turn("user"), Turn("assistant", [ToolCall("calc")])])
                assert c == expected, f"got {c!r}"

            def test_missing_required_field_raises_value_error_naming_it():
                try:
                    from_dict(Conversation, {"id": "c1", "turns": []})
                except ValueError as e:
                    assert "settings" in str(e), f"message should name the field: {e}"
                    return
                assert False, "missing required field should raise ValueError"

            def test_list_of_plain_values_unchanged():
                s = from_dict(Settings, {"model": "m", "tags": ["x", "y"]})
                assert s.tags == ["x", "y"]
        ''',
        "solution": r'''
            import dataclasses
            import types
            import typing


            def _convert(tp, value):
                if value is None:
                    return None
                origin = typing.get_origin(tp)
                if origin in (typing.Union, types.UnionType):
                    for arg in typing.get_args(tp):
                        if arg is not type(None):
                            return _convert(arg, value)
                if origin is list:
                    (item_type,) = typing.get_args(tp)
                    return [_convert(item_type, v) for v in value]
                if dataclasses.is_dataclass(tp) and isinstance(value, dict):
                    return from_dict(tp, value)
                return value


            def from_dict(cls, data):
                hints = typing.get_type_hints(cls)
                kwargs = {}
                for f in dataclasses.fields(cls):
                    if f.name in data:
                        kwargs[f.name] = _convert(hints[f.name], data[f.name])
                    elif (f.default is dataclasses.MISSING
                          and f.default_factory is dataclasses.MISSING):
                        raise ValueError(f"missing required field: {f.name}")
                return cls(**kwargs)
        ''',
    },
]
