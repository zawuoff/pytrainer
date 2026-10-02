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
            ## Dataclasses

            Many classes in an AI app only hold data: a chat message, a model config, an API response.
            Each one needs an `__init__`, a `__repr__` and an `__eq__`. Python can generate those three
            methods for you.

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

            Each `name: type` line inside the class is a **field**: one piece of data that every
            instance stores.

            The `@dataclass` line is a **decorator**: a function that Python applies to the class
            written below it. `dataclass` reads the fields and adds three methods to the class:

            - `__init__` takes one argument per field, in field order, and stores each one on `self`.
            - `__repr__` returns the class name and every field as `name=value`.
            - `__eq__` makes `==` return `True` when two instances have equal values in every field.

            A class without `__eq__` gives `True` for `==` only when both sides are the same object.
            Two separately created objects are never equal, even with the same values.

            `print(m)` uses `__repr__`, and `__repr__` formats each value with `repr()`. A string field
            appears in single quotes: `name='gpt-4o'`. `print(m.name)` prints the string itself, without quotes.
        ''',
        "difficulty": 0,
        "mode": "predict",
        "prompt": r'''
            Read the code and type exactly what it prints.
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
            `print(m)` calls the `__repr__` that `@dataclass` generated. It returns the class name
            and every field as `name=value`, with each value formatted by `repr()`, so the strings
            appear in single quotes. `print(m.content)` prints the string itself: `Hi`. The
            generated `__eq__` compares the fields of the two objects. Both have the role `"user"`
            and the content `"Hi"`, so `==` returns `True`.
        ''',
        "starter": "",
        "tests": "",
        "hints": [
            "`@dataclass` gives the class a readable print and an `==` that compares fields.",
            "Printing the object shows `ClassName(field=value, ...)` with strings in single quotes; `m.content` is just the plain string.",
            "Line 1: the class name with both fields and their quoted values. Line 2: the content without quotes. Line 3: whether the fields match.",
        ],
    },
    {
        "id": "dataclasses-s2",
        "title": "Add the decorator",
        "lesson": r'''
            ## The `@dataclass` decorator

            You apply a decorator by writing `@` and its name on the line directly above `class`.

            Without the decorator, the field lines only record type hints. Python generates no
            `__init__`, so the class accepts no arguments. This example catches the `TypeError` and
            prints its message.

            ```python
            class Plain:
                title: str

            try:
                Plain("Intro")
            except TypeError as e:
                print("error:", e)
            # error: Plain() takes no arguments
            ```

            With the decorator, the same fields produce an `__init__`, a `__repr__` and an `__eq__`.

            ```python
            from dataclasses import dataclass

            @dataclass
            class Decorated:
                title: str

            print(Decorated("Intro"))
            # Decorated(title='Intro')
            ```

            `dataclass` is a function in the **standard library** module `dataclasses`. The standard
            library is the set of modules that is installed with Python. You must import the function
            before you use it: `from dataclasses import dataclass`.

            Python runs the class body first, then calls `dataclass` with the new class. The function
            adds the generated methods and returns the class. If you leave out the `@dataclass` line,
            nothing calls the function and no methods are added.
        ''',
        "difficulty": 0,
        "prompt": r'''
            `Document` holds a title and a text for a RAG pipeline. It lists its fields, but
            it is not a dataclass yet, so it has no constructor.

            **Write:** replace the `___` so that `Document` becomes a dataclass.

            - `title`: a `str`, e.g. `"Intro"`
            - `text`: a `str`, e.g. `"Hello"`

            **Rules**
            - Change only the `___` line; keep the two fields as they are.
            - `Document("Intro", "Hello")` must work, and two documents with the same fields
              must be equal with `==`.

            **Examples**
            ```python
            d = Document("Intro", "Hello")
            d.title                              # "Intro"
            d.text                               # "Hello"
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
            "A decorator is written on the line directly above the class and starts with `@`.",
            "The name you need is already imported at the top of the file.",
            "Replace `___` with `@dataclass`.",
        ],
    },
    {
        "id": "dataclasses-s6",
        "title": "Label a function",
        "lesson": r'''
            ## Type hints on functions

            A **type hint** is a type written in your code to state what kind of value is expected.
            You already wrote type hints in dataclass fields: `title: str`. Functions take them too.

            ```python
            def shout(text: str) -> str:
                return text.upper() + "!"

            def word_count(text: str) -> int:
                return len(text.split())

            print(shout("hi"))
            # HI!
            print(word_count("tokens are not words"))
            # 4
            ```

            A **parameter annotation** is a colon and a type after a parameter name: `text: str`.
            It states the type of the argument the function expects.

            A **return annotation** is an arrow and a type after the `)` and before the final `:`.
            `-> int` states that the function returns an `int`.

            **Annotation** is the formal name for a type hint. Python stores a function's annotations
            in a dict named `__annotations__`. The return annotation is stored under the key `"return"`.

            ```python
            def word_count(text: str) -> int:
                return len(text.split())

            print(word_count.__annotations__)
            # {'text': <class 'str'>, 'return': <class 'int'>}
            ```

            The common simple types are `str`, `int`, `float` and `bool`. Write the type name itself,
            with no quotes: `str`, not `"str"`.
        ''',
        "difficulty": 0,
        "prompt": r'''
            Counting words is a cheap stand-in for counting tokens. The function works, but
            its type hints are blanks.

            **Write:** fill in the two blanks (`___`) in `count_words(text)`.

            - `text`: a `str`, e.g. `"tokens are not words"`
            - **Returns:** an `int`, the number of whitespace-separated words, e.g. `4`

            **Rules**
            - The parameter annotation must be exactly `str`.
            - The return annotation must be exactly `int`.
            - Don't change the body.

            **Examples**
            ```python
            count_words("tokens are not words")   # returns 4
            count_words("")                       # returns 0
            count_words.__annotations__           # {"text": str, "return": int}
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
            "The first blank describes what `text` is; the second, after `->`, describes what the function gives back.",
            "`text` is a piece of text, and `len(...)` always gives back a whole number.",
            "Replace the first `___` with `str` and the second with `int` - type names, no quotes, no brackets.",
        ],
    },
    {
        "id": "dataclasses-s7",
        "title": "Signs, not fences",
        "lesson": r'''
            ## Hints are not checked at runtime

            Python stores type hints but never checks them while the program runs. The time while
            a program runs is called **runtime**. A call with the wrong type still executes the
            function body.

            ```python
            def add_tokens(a: int, b: int) -> int:
                return a + b

            print(add_tokens(2, 3))
            # 5
            print(add_tokens("2", "3"))
            # 23
            ```

            The second call passes two strings. Python runs `"2" + "3"`, which joins the strings, and
            prints `23`. No error is raised.

            Hints are still worth writing, for three reasons:

            - They tell the next reader which types you intended.
            - Your editor uses them to suggest names and to show warnings as you type.
            - A **type checker** is a tool that reads your code without running it and reports type
              mistakes. `mypy` and `pyright` are type checkers. Many AI codebases run one automatically
              on every change.

            You can read the stored hints from `__annotations__`. Each value is the type object itself.

            ```python
            def f(n: int) -> str:
                return str(n)

            print(f.__annotations__)
            # {'n': <class 'int'>, 'return': <class 'str'>}
            print(f.__annotations__["n"])
            # <class 'int'>
            ```

            If a type must be correct at runtime, for example for API input, you check it yourself.
            You do that later in this chapter with `__post_init__`.
        ''',
        "difficulty": 0,
        "mode": "predict",
        "prompt": r'''
            Read the code and type exactly what it prints.
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
            `double(4)` returns `4 * 2`, which is `8`. Python does not check type hints when the
            code runs, so `double("ab")` evaluates `"ab" * 2`. Multiplying a string by 2 repeats
            it: `abab`. The hint is still stored in the dict `double.__annotations__`. The value
            under the key `"n"` is the type `int`, and printing a type shows `<class 'int'>`.
        ''',
        "starter": "",
        "tests": "",
        "hints": [
            "Does Python stop you from passing a string to a parameter hinted `int`?",
            "No - the body runs as written. Multiplying a string by 2 repeats it. The last line prints the stored hint, which is the type itself.",
            "Line 1: 4 doubled. Line 2: the string written twice in a row. Line 3: how Python prints the type `int` (`<class '...'>`).",
        ],
    },
    {
        "id": "dataclasses-s3",
        "title": "Fix the bug: field order",
        "lesson": r'''
            ## Default values and field order

            A function parameter can have a default value: `def ask(prompt, temperature=0.7)`. A
            dataclass field can have one too. Write `= value` after the type.

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
            print(Request("Hi", max_tokens=10))
            # Request(prompt='Hi', max_tokens=10)
            ```

            The order of the fields is the order of the parameters of the generated `__init__`. For
            `Request` it is `__init__(self, prompt, max_tokens=256)`. The first positional argument
            goes to `prompt`, the second to `max_tokens`.

            Functions require parameters without a default to come before parameters with one. The
            generated `__init__` is a function, so fields follow the same rule: fields without a
            default first, fields with a default after them.

            If you break the rule, `@dataclass` raises `TypeError` while the class is being created,
            before any object exists. This example catches the error and prints its message.

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
        ''',
        "difficulty": 0,
        "prompt": r'''
            This model config crashes with a `TypeError` as soon as the file is loaded.
            Read the error message and fix the class.

            **Write:** fix the dataclass `ModelConfig` so it has these fields, in this order:

            - `model`: a `str`, e.g. `"gpt-4o"` (required, first argument)
            - `temperature`: a `float`, e.g. `0.0`; defaults to `0.7`

            **Rules**
            - The fields must be declared in the order `model`, then `temperature`.
            - Keep the default `0.7` for `temperature`.

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
            "Read the error message: it complains about a field without a default coming after one with a default.",
            "Required fields (no default) must be listed before fields that have a default.",
            "Swap the two field lines so `model: str` comes first and `temperature: float = 0.7` second.",
        ],
    },
    {
        "id": "dataclasses-s4",
        "title": "A chunk record",
        "lesson": r'''
            ## Writing a complete dataclass

            A complete dataclass has three parts: the `@dataclass` decorator, the `class` line, and
            one line per field. Each field line is `name: type` or `name: type = default`.

            ```python
            from dataclasses import dataclass

            @dataclass
            class Embedding:
                doc_id: str
                model: str
                dims: int = 1536

            e = Embedding("doc-1", "text-embed")
            print(e)
            # Embedding(doc_id='doc-1', model='text-embed', dims=1536)
            print(Embedding.__annotations__)
            # {'doc_id': <class 'str'>, 'model': <class 'str'>, 'dims': <class 'int'>}
            ```

            The class keeps its type hints in `Embedding.__annotations__`, a dict that maps each field
            name to its type. Tools read this dict, and so do the checks for this exercise.

            Write the type itself in a hint: `int`. A value such as `1` or a string such as `"int"` is
            a different annotation and does not equal `int`.
        ''',
        "difficulty": 0,
        "prompt": r'''
            A RAG pipeline splits documents into chunks. Model one chunk as a typed record.

            **Write:** a dataclass `class Chunk` with three fields, in this order:

            - `text`: type hint `str`, the chunk's text, e.g. `"Hello"` (required)
            - `source`: type hint `str`, the file it came from, e.g. `"guide.pdf"` (required)
            - `page`: type hint `int`, e.g. `7`; defaults to `1`

            **Rules**
            - Decorate the class with `@dataclass` (a check verifies it).
            - Fields in exactly the order `text`, `source`, `page`.
            - Type hints exactly `str`, `str`, `int`.

            **Examples**
            ```python
            Chunk("Hello", "guide.pdf")          # Chunk(text='Hello', source='guide.pdf', page=1)
            Chunk("Bye", "guide.pdf", 7).page    # 7
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
            "Start with `@dataclass`, then `class Chunk:`, then one line per field.",
            "Each field line is `name: type`; the field with a default adds `= value` and must come last.",
            "Write three indented lines under the class: `text` and `source` hinted as `str`, and `page` hinted as `int` with a default of `1`.",
        ],
    },
    {
        "id": "dataclasses-s5",
        "title": "Total tokens",
        "lesson": r'''
            ## Methods on a dataclass

            A dataclass is a normal class. `@dataclass` only adds methods to it. You can define your
            own methods below the fields, the same way as in the classes chapter.

            A **method** is a function defined inside a class. Its first parameter, `self`, is the
            **instance** the method was called on. Inside a method you read a field as `self.field_name`.

            ```python
            from dataclasses import dataclass

            @dataclass
            class Price:
                input_per_1k: float
                output_per_1k: float

                def average(self) -> float:
                    return (self.input_per_1k + self.output_per_1k) / 2

            print(Price(1.0, 3.0).average())
            # 2.0
            print(Price(0.5, 0.5).average())
            # 0.5
            ```

            `Price(1.0, 3.0).average()` creates an instance and calls `average` with that instance as
            `self`. The method reads `self.input_per_1k` and `self.output_per_1k`, which are `1.0` and
            `3.0` for this instance. Each instance has its own field values, so the second call returns `0.5`.

            If you write `input_per_1k` without `self.`, Python looks for a variable with that name,
            finds none, and raises `NameError: name 'input_per_1k' is not defined`.
        ''',
        "difficulty": 0,
        "prompt": r'''
            An LLM API reports how many tokens a request used. The `Usage` dataclass is
            already written; you only complete one method.

            **Write:** the method `total(self)` inside `Usage`

            - `self.prompt_tokens`: an `int`, tokens in the prompt, e.g. `5`
            - `self.completion_tokens`: an `int`, tokens in the reply, e.g. `2`
            - **Returns:** an `int`: `prompt_tokens + completion_tokens`

            **Rules**
            - Use the numbers of the object the method is called on (each object has its own).
            - `Usage(0, 0).total()` returns `0`.

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
            "A dataclass method works like any class method: the fields are attributes on `self`.",
            "Read both fields through `self` and add them together.",
            "Return `self.prompt_tokens` plus `self.completion_tokens`.",
        ],
    },
    {
        "id": "dataclasses-7",
        "title": "Typed cost lookup",
        "lesson": r'''
            ## Hints for lists and dicts

            A hint for a collection can also state the type of the values inside it. Write the inner
            types in square brackets after the collection type.

            | hint | meaning |
            | --- | --- |
            | `list[str]` | a list of strings |
            | `dict[str, float]` | a dict with `str` keys and `float` values |
            | `tuple[int, int]` | a tuple of exactly two ints |
            | `set[str]` | a set of strings |

            A type written with square brackets is a **generic type**. The types inside the brackets
            are its **type parameters**.

            ```python
            def longest(words: list[str]) -> str:
                return max(words, key=len)

            def lookup(prices: dict[str, float], name: str) -> float:
                return prices.get(name, 0.0)

            print(longest(["rag", "agents"]))
            # agents
            print(lookup({"gpt-4o": 5.0}, "gpt-4o"))
            # 5.0
            print(lookup({"gpt-4o": 5.0}, "llama"))
            # 0.0
            print(longest.__annotations__)
            # {'words': list[str], 'return': <class 'str'>}
            ```

            `prices.get(name, 0.0)` returns the value for `name`, or `0.0` when the key is missing.

            Older code writes `List[str]` and `Dict[str, float]`, imported from `typing`. Since
            Python 3.9 the built-in lowercase names work, and they are the preferred form.
        ''',
        "difficulty": 1,
        "hints": [
            "Collection hints put the item types in square brackets: a list of X is `list[X]`, a dict from K to V is `dict[K, V]`.",
            "Annotate `models` as a list of strings, `prices` as a dict from strings to floats, and the return as `float`. For the body, loop over the models and look each one up with a default.",
            "1) Signature: `models: list[str]`, `prices: dict[str, float]`, `-> float`. 2) Start `total = 0.0`. 3) For each model add `prices.get(model, 0.0)`. 4) Return `total`.",
        ],
        "research": {
            "note": "Skim the start of the `typing` docs page - the part about annotating functions and the table of built-in generic types like `list[int]`. Then come back.",
            "links": [
                {"title": "typing - Support for type hints (Python docs)", "url": "https://docs.python.org/3/library/typing.html"},
                {"title": "Glossary: type hint (Python docs)", "url": "https://docs.python.org/3/glossary.html#term-type-hint"},
            ],
        },
        "prompt": r'''
            Estimate what a batch of requests costs. Typed code is easier to trust, so this
            function must be fully annotated.

            **Write:** `total_price(models, prices)`

            - `models`: type hint `list[str]` - the model used by each request, e.g. `["gpt-4o", "haiku", "gpt-4o"]`
            - `prices`: type hint `dict[str, float]` - price per request for each model, e.g. `{"gpt-4o": 5.0, "haiku": 0.25}`
            - **Returns:** type hint `float` - the sum of the prices of all requests

            **Rules**
            - A model that is missing from `prices` costs `0.0`.
            - An empty `models` list returns `0.0`.
            - The annotations must be exactly `list[str]`, `dict[str, float]` and return `float`
              (a check reads them).

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
            ## Optional values: `str | None`

            Some values can be absent. The hint `str | None` states that a value is either a string
            or `None`. Read the `|` as "or". This spelling needs Python 3.10 or newer.

            ```python
            from dataclasses import dataclass

            @dataclass
            class User:
                id: str
                nickname: str | None = None

            print(User("u1"))
            # User(id='u1', nickname=None)
            print(User("u2", "ada"))
            # User(id='u2', nickname='ada')

            def greet(name: str | None) -> str:
                if name is None:
                    return "Hi there"
                return "Hi " + name

            print(greet(None))
            # Hi there
            ```

            An optional field usually gets the default `None`, so callers can leave it out.
            `User("u1")` passes no nickname, and the generated `__init__` stores `None`.

            `str | None` is a **union type**: a hint that allows any one of several types. Older code
            writes `Optional[str]`, imported from `typing`. It means the same thing.

            `str | None` is only a hint. Python does not check it, and your code still has to handle
            `None`. `"Hi " + None` raises `TypeError`, so `greet` tests `name is None` first.
        ''',
        "hints": [
            "Import `dataclass` from the `dataclasses` module and put `@dataclass` on the line above the class.",
            "Inside the class, list each field as `name: type`, in the order given. The decorator writes `__init__`, `__repr__` and `__eq__` for you.",
            "1) Import `dataclass`. 2) Decorate the class. 3) Write the three fields in order with their type hints; the last one is hinted `str | None` and has `= None` as its default. No methods needed.",
        ],
        "difficulty": 1,
        "prompt": r'''
            A chat API takes a list of messages. Model one message as a typed record.

            **Write:** a dataclass `class Message` with three fields, in this order:

            - `role`: type hint `str`, e.g. `"user"` (required)
            - `content`: type hint `str`, e.g. `"Hi"` (required)
            - `name`: type hint `str | None`, e.g. `"calc"`; defaults to `None`

            **Rules**
            - Decorate the class with `@dataclass` (a check verifies it is a dataclass).
            - The fields must be declared in exactly the order `role`, `content`, `name`.
            - The type hints must be exactly `str`, `str` and `str | None`.
            - No methods needed: `@dataclass` provides the constructor, `==` and the printed form.

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
            ## Mutable defaults and `default_factory`

            A default value is created once, when the class is defined. If it is a list, every object
            built without an argument would refer to the same list object.

            ```python
            a_ids = []
            b_ids = a_ids
            b_ids.append(1)
            print(a_ids)
            # [1]
            print(a_ids is b_ids)
            # True
            ```

            In the diagram below, run `b_ids.append(1)` in each of the two modes. In the first mode,
            `b_ids = a_ids` makes both names refer to one list, which is what a shared default list
            does. In the second mode, `b_ids = a_ids.copy()` gives each name its own list object.

            ```diagram
            {"type":"alias-copy","title":"One shared list or two separate lists","a":"a_ids","b":"b_ids","items":[],"append":1}
            ```

            A list, a dict and a set are **mutable**: they can be changed after they are created.
            Dataclasses refuse a list, dict or set as a default for this reason. `@dataclass` raises
            `ValueError` when the class is created. This example catches it and prints the message.

            ```python
            from dataclasses import dataclass

            try:
                @dataclass
                class Bad:
                    tags: list[str] = []
            except ValueError as e:
                print("error:", e)
            # error: mutable default <class 'list'> for field tags is not allowed: use default_factory
            ```

            `field(...)` from `dataclasses` sets options for one field. Its `default_factory` option
            takes a **factory**: a function that Python calls, with no arguments, each time an object
            needs a default. `list()` returns a new `[]` and `dict()` returns a new `{}`.

            ```python
            from dataclasses import dataclass, field

            @dataclass
            class Chat:
                turns: list[str] = field(default_factory=list)

            a = Chat()
            b = Chat()
            a.turns.append("Hi")
            print(a.turns)
            # ['Hi']
            print(b.turns)
            # []
            ```

            Pass the function `list`, not the call `list()`.
        ''',
        "hints": [
            "A plain `= []` default is not allowed in a dataclass (it would be shared). Look at `field(default_factory=...)`.",
            "`default_factory` takes a function that is called fresh for every new object - `list` and `dict` are exactly such functions.",
            "1) Import `field` along with `dataclass`. 2) `model: str` with no default. 3) `temperature: float = 0.7`. 4) `stop` and `metadata` with their type hints and `field(default_factory=list)` / `field(default_factory=dict)`.",
        ],
        "difficulty": 1,
        "prompt": r'''
            A model config holds the settings sent with every LLM request, including a list
            of stop sequences and some free-form metadata.

            **Write:** a dataclass `class ModelConfig` with four fields, in this order:

            - `model`: type hint `str`, e.g. `"gpt-4o"` (required)
            - `temperature`: type hint `float`, e.g. `0.0`; defaults to `0.7`
            - `stop`: type hint `list[str]`, e.g. `["###"]`; defaults to an **empty list**
            - `metadata`: type hint `dict[str, str]`, e.g. `{"env": "prod"}`; defaults to an **empty dict**

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
            ## Validation with `__post_init__`

            The generated `__init__` stores whatever it receives, including an empty chunk or page `-3`.
            Type hints do not stop it, because Python does not check hints at runtime.

            If the class defines a method named `__post_init__(self)`, the generated `__init__` calls it
            after it has stored all the fields. Inside it you read `self.field_name` and `raise` an
            error when a value is not acceptable.

            ```python
            from dataclasses import dataclass

            @dataclass
            class Temperature:
                value: float

                def __post_init__(self):
                    if self.value < 0 or self.value > 2:
                        raise ValueError(f"temperature out of range: {self.value}")

            print(Temperature(0.7))
            # Temperature(value=0.7)
            try:
                Temperature(5)
            except ValueError as e:
                print("rejected:", e)
            # rejected: temperature out of range: 5
            ```

            Step through what happens during the call `Temperature(5)`.

            ```diagram
            {"type":"flow","title":"What happens when Temperature(5) is called","steps":[
            {"label":"Temperature(5) is called","detail":"Python creates a new Temperature object and calls the generated __init__ with value set to 5.","code":"Temperature(5)"},
            {"label":"__init__ stores the field","detail":"The generated __init__ stores the argument on the object. It does not check the type or the range.","code":"self.value = 5"},
            {"label":"__post_init__ runs","detail":"The generated __init__ then calls self.__post_init__(). The condition is True because 5 is greater than 2.","code":"if self.value < 0 or self.value > 2:\n# False or True -> True"},
            {"label":"ValueError is raised","detail":"The raise statement ends __post_init__ and __init__. The call Temperature(5) raises the error instead of returning an object.","code":"ValueError: temperature out of range: 5"},
            {"label":"Compare: Temperature(0.7)","detail":"With 0.7 the condition is False. __post_init__ returns without raising, and the call returns the new object.","code":"print(Temperature(0.7))\n# Temperature(value=0.7)"}
            ]}
            ```

            Checking data and rejecting bad values is called **validation**. When every object is
            validated at creation, the rest of your app can rely on the values of any object it
            receives. Pydantic, a library used in many AI codebases, validates objects the same way.

            `__post_init__` needs no `return`. When every check passes, it ends and the object is created.
        ''',
        "difficulty": 1,
        "hints": [
            "Define a method named `__post_init__(self)` in the class - the dataclass calls it right after storing the fields.",
            "Inside it, look at `self.text` and `self.page`; when one is bad, `raise ValueError(...)` with any message. When both are fine, do nothing.",
            "1) `def __post_init__(self):`. 2) If `self.text.strip()` is empty, raise `ValueError`. 3) If `self.page < 1`, raise `ValueError`. No `return` value needed.",
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

            **Write:** a `__post_init__(self)` method inside the `Chunk` dataclass (the fields
            are already there).

            - `self.text`: a `str`, the chunk's text, e.g. `"Hello"`
            - `self.page`: an `int`, e.g. `3`; defaults to `1`
            - **Returns:** nothing - it only checks

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
            ## Enums

            An **Enum** is a class with a fixed set of named **members**, each with a value. You
            subclass `Enum` and write one `NAME = value` line per member.

            ```python
            from enum import Enum

            class Size(Enum):
                SMALL = "small"
                LARGE = "large"

            print(Size.SMALL)
            # Size.SMALL
            print(Size.SMALL.value)
            # small
            print(Size("large") is Size.LARGE)
            # True
            try:
                Size("huge")
            except ValueError as e:
                print("error:", e)
            # error: 'huge' is not a valid Size
            ```

            `Size("large")` looks a member up by its value. A value that no member has raises
            `ValueError`. `Size(Size.LARGE)` receives a member and returns that same member.
            `.value` gives the plain value of a member.

            Each member exists once, so you compare members with `is`: `Size("large") is Size.LARGE`.

            In this exercise you call the Enum inside `__post_init__` to convert and check a field.
        ''',
        "hints": [
            "An Enum member can be looked up by value: `Role(\"user\")` gives `Role.USER`, and an unknown value raises `ValueError` for you. `__post_init__` runs right after the generated `__init__`.",
            "In `__post_init__`, convert `self.role` with `Role(...)` (it also accepts a `Role` that is already a member), then check the content's type, then check for blank content unless the role is `TOOL`. `to_dict` uses `.value` to get the plain string.",
            "1) `Role(Enum)` with four `NAME = \"value\"` lines. 2) `@dataclass ChatMessage` with `role: Role` and `content: str`. 3) `__post_init__`: `self.role = Role(self.role)`; not a str -> `TypeError`; empty after `.strip()` and not `Role.TOOL` -> `ValueError`. 4) `to_dict` returns the role's `.value` and the content.",
        ],
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            Chat messages should only ever have a known role and real text. Catch bad
            messages the moment they are created, before they reach the API.

            **Write:**
            1. An Enum `class Role` with exactly four members, named `SYSTEM`, `USER`,
               `ASSISTANT`, `TOOL`, whose values are the lowercase strings `"system"`, `"user"`,
               `"assistant"`, `"tool"`.
            2. A dataclass `class ChatMessage` with two fields, in this order:
               - `role`: type hint `Role`; may be passed as a `Role` member (`Role.USER`) or as a
                 plain string (`"user"`)
               - `content`: type hint `str`, e.g. `"Hi"`
            3. A method `to_dict(self)`.
               - **Returns:** a dict `{"role": <role as a plain string>, "content": <content>}`,
                 e.g. `{"role": "user", "content": "Hi"}`

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
            ## `frozen`, `order` and `replace`

            `dataclass` accepts options in parentheses: `@dataclass(frozen=True, order=True)`.

            `frozen=True` makes instances read-only: assigning to a field raises
            `dataclasses.FrozenInstanceError`. Frozen instances are also **hashable**, which means
            you can put them in a set or use them as dict keys.

            `order=True` adds `<`, `<=`, `>` and `>=`. They compare the fields one by one, in the
            order the fields are declared. `sorted()` and `min()` use `<`.

            `replace(obj, field=new)` from `dataclasses` returns a new object with that field changed.
            The original is not modified.

            ```python
            from dataclasses import dataclass, replace

            @dataclass(frozen=True, order=True)
            class Version:
                major: int
                minor: int

            v = Version(1, 2)
            print(sorted([Version(2, 0), v]))
            # [Version(major=1, minor=2), Version(major=2, minor=0)]
            print(replace(v, minor=3))
            # Version(major=1, minor=3)
            print(v)
            # Version(major=1, minor=2)
            print(len({v, Version(1, 2)}))
            # 1
            ```

            The last line builds a set from two `Version(1, 2)` objects. They are equal and
            hashable, and a set keeps only one of several equal items, so its length is `1`.
        ''',
        "hints": [
            "`@dataclass` accepts options: look at `frozen=True` and `order=True`.",
            "With `order=True`, objects compare field by field in the order the fields are declared, so that order decides the sort. Frozen objects can't be changed - to 'change' one, build a new one (`dataclasses.replace` helps).",
            "1) `@dataclass(frozen=True, order=True)`. 2) Fields in the order `cost_per_1k`, `latency_ms`, `name`. 3) `discounted`: compute `round(cost * (1 - pct / 100), 6)` and return `replace(self, cost_per_1k=...)` - a new object with the other fields copied.",
        ],
        "difficulty": 2,
        "prompt": r'''
            A router picks the cheapest, fastest model. Model each option as a read-only
            record that can be sorted and put in a set.

            **Write:** a dataclass `class ModelOption` with three fields, in this order:

            - `cost_per_1k`: a `float`, price per 1000 tokens, e.g. `0.5`
            - `latency_ms`: an `int`, e.g. `300`
            - `name`: a `str`, e.g. `"small"`

            and a method `discounted(self, pct)`:

            - `pct`: a number, the discount in percent, e.g. `20`
            - **Returns:** a **new** `ModelOption` with the same `latency_ms` and `name` and cost
              `cost_per_1k * (1 - pct / 100)` **rounded to 6 decimals** (`round(x, 6)`)

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
            ## Properties, `Literal`, class methods and `asdict`

            `@property` on a method lets you read it without parentheses: `r.words`. Python runs the
            method on every read. A property is not a field, so `asdict` and `__repr__` leave it out.

            `Literal["fast", "slow"]` from `typing` is a hint that allows only those exact values.
            Python does not check it. `get_args` from `typing` returns the allowed values as a tuple.

            A **class method** is a method decorated with `@classmethod`. Python passes it the class,
            named `cls`, instead of an instance. Calling `cls(...)` builds a new object.

            `asdict(obj)` from `dataclasses` converts a dataclass instance, including nested
            dataclasses, into plain dicts and lists.

            ```python
            from dataclasses import dataclass, asdict
            from typing import Literal, get_args

            Mode = Literal["fast", "slow"]

            @dataclass
            class Limits:
                max_tokens: int
                mode: Mode

            @dataclass
            class Request:
                prompt: str
                limits: Limits

                @property
                def words(self) -> int:
                    return len(self.prompt.split())

                @classmethod
                def short(cls, prompt):
                    return cls(prompt, Limits(50, "fast"))

            r = Request.short("Say hi")
            print(get_args(Mode))
            # ('fast', 'slow')
            print(r.words)
            # 2
            print(asdict(r))
            # {'prompt': 'Say hi', 'limits': {'max_tokens': 50, 'mode': 'fast'}}
            ```
        ''',
        "hints": [
            "Build one dataclass per level (Usage, Message, Choice, Completion). `from_dict` is a `@classmethod`: it receives the class as `cls` and returns `cls(...)`.",
            "`total_tokens` is a `@property`, not a field. Validate `finish_reason` in `Choice.__post_init__` (`typing.get_args` lists a Literal's allowed values). `from_dict` builds the inner objects first, using `.get` for optional keys; `dataclasses.asdict` turns nested dataclasses back into dicts.",
            "1) `Usage` with two int fields plus the property. 2) `Message(role, content)`. 3) `Choice.__post_init__` raises `ValueError` if `finish_reason` is not None and not allowed. 4) `from_dict`: `usage = data.get(\"usage\")`; build the choices with a comprehension creating `Message` and `Choice`; `Usage(...)` only if usage is truthy. 5) `to_dict` returns `asdict(self)`.",
        ],
        "difficulty": 3,
        "prompt": r'''
            A chat-completion API returns a nested JSON dict. Turn it into typed objects so
            the rest of your app can use `c.choices[0].message.content` instead of raw keys.

            **Write:** four dataclasses (fields in exactly this order) and two methods:

            - `Usage`: `prompt_tokens: int`, `completion_tokens: int`, plus a read-only
              **property** `total_tokens` (their sum). It is **not** a field.
            - `Message`: `role: str`, `content: str | None`
            - `Choice`: `index: int`, `message: Message`,
              `finish_reason: Literal["stop", "length", "tool_calls"] | None`
            - `Completion`: `id: str`, `model: str`, `choices: list[Choice]`, `usage: Usage | None`
            - a **classmethod** `Completion.from_dict(data)`
              - `data`: the raw response dict (see the example below)
              - **Returns:** a `Completion` whose `choices` are `Choice` objects, each with a
                `Message` object, and whose `usage` is a `Usage` object (or `None`)
            - a method `to_dict(self)` on `Completion`
              - **Returns:** a plain dict with exactly the keys `id`, `model`, `choices`, `usage`;
                each choice is `{"index": ..., "message": {"role": ..., "content": ...}, "finish_reason": ...}`
                and `usage` is `{"prompt_tokens": ..., "completion_tokens": ...}` or `None`

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
            "`typing.get_type_hints(cls)` gives each field's real type, `dataclasses.fields(cls)` lists the fields, and `typing.get_origin` / `typing.get_args` take apart types like `list[X]` and `X | None`.",
            "Write a helper `convert(tp, value)`: None stays None; a union -> convert with its non-None member; `list[X]` -> convert every element; a dataclass type with a dict value -> call `from_dict` recursively; anything else -> unchanged. `from_dict` loops over the fields collecting keyword arguments.",
            "1) `hints = get_type_hints(cls)`. 2) For each field: if its name is in `data`, store `convert(hints[name], data[name])` in a kwargs dict. 3) Else if both `default` and `default_factory` are `dataclasses.MISSING`, raise `ValueError` naming the field. 4) Otherwise skip it. 5) Return `cls(**kwargs)`. A union's origin is `typing.Union` or `types.UnionType`.",
        ],
        "difficulty": 3,
        "prompt": r'''
            Libraries like Pydantic turn nested JSON into typed objects automatically by reading
            the class's type hints. Build a small version that works for **any** dataclass.

            **Write:** `from_dict(cls, data)`

            - `cls`: a dataclass (the class itself, not an object), e.g. `Turn`
            - `data`: a dict, possibly nested, e.g. `{"role": "user", "reply_to": {"role": "assistant"}}`
            - **Returns:** an instance of `cls` built from `data`

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
