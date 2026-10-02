TOPIC = {
    "id": "classes",
    "title": "Classes & Objects",
    "track": "production-python",
    "order": 1,
    "requires": ["functions", "dicts"],
    "summary": """
        Modelling things with classes: __init__, instance vs class attributes, methods,
        dunder methods, properties with validation, inheritance, super() and polymorphism.
    """,
    "concepts": ["class", "__init__", "self", "instance attributes", "class attributes",
                 "methods", "__repr__", "__str__", "__eq__", "__len__", "property",
                 "inheritance", "super()", "polymorphism", "NotImplementedError"],
}

# The Library card for this chapter (shown once the chapter's steps are done).
# Every line that starts with `#` in an example is the real output of that example.
REFERENCE = {
    "keywords": ["class", "object", "instance", "self", "__init__", "attribute", "method",
                 "__repr__", "__str__", "__eq__", "__len__", "property", "inheritance",
                 "subclass", "super", "attributeerror"],
    "cards": [
        {
            "syntax": "def __init__(self, name):  self.name = name",
            "explain": "Python calls __init__ on every new instance. self is the new object. self.name = ... stores an attribute on it.",
            "example": r'''
                class Chat:
                    def __init__(self, model):
                        self.model = model
                        self.turns = 0

                a = Chat("gpt")
                print(a.model, a.turns)
                # gpt 0
            ''',
        },
        {
            "syntax": "def method(self):",
            "explain": "A function in a class. obj.method() passes obj as self, so the method reads that object's attributes.",
            "example": r'''
                class Prompt:
                    def __init__(self, text):
                        self.text = text
                    def char_count(self):
                        return len(self.text)

                print(Prompt("Hi").char_count())
                # 2
            ''',
        },
        {
            "syntax": "size = 100   (in the class body)",
            "explain": "A class attribute: stored once on the class. Every instance reads the same value through obj.size.",
            "example": r'''
                class Chunker:
                    size = 100

                a = Chunker()
                b = Chunker()
                Chunker.size = 50
                print(a.size, b.size)
                # 50 50
            ''',
        },
        {
            "syntax": "def __len__(self):  /  def __str__(self):",
            "explain": "Special methods. Python calls them for len(obj) and print(obj). __repr__ serves repr(obj), __eq__ serves ==.",
            "example": r'''
                class Pair:
                    def __len__(self):
                        return 2
                    def __str__(self):
                        return "a pair"

                print(len(Pair()), Pair())
                # 2 a pair
            ''',
        },
        {
            "syntax": "@property",
            "explain": "Makes the method below it run when you read obj.name, with no (). A second method under @name.setter runs on assignment.",
            "example": r'''
                class Circle:
                    def __init__(self, r):
                        self.r = r
                    @property
                    def area(self):
                        return 3 * self.r * self.r
                print(Circle(2).area)
                # 12
            ''',
        },
        {
            "syntax": "class Child(Parent):",
            "explain": "Child gets every method of Parent. A method defined again overrides it. super().__init__() calls the parent's.",
            "example": r'''
                class Model:
                    def kind(self):
                        return "generic"
                class ChatModel(Model):
                    def kind(self):
                        return "chat"
                print(ChatModel().kind(), isinstance(ChatModel(), Model))
                # chat True
            ''',
        },
    ],
}

LESSON = r'''
## Chapter notes: Classes & Objects

### Classes and instances

A **class** is a new type that you define. Calling the class creates an **instance**: a new
object of that type. An **attribute** is a value stored on an object under a name. A
**method** is a function defined inside a class.

```python
class Message:
    def __init__(self, role, content):
        self.role = role
        self.content = content

    def describe(self):
        return f"{self.role}: {self.content}"

    def __repr__(self):
        return f"Message({vars(self)})"

m = Message("user", "Hi")
print(m.role)
# user
print(m.describe())
# user: Hi
print(m)
# Message({'role': 'user', 'content': 'Hi'})
```

`Message("user", "Hi")` does three things. Python creates a new `Message` object with no
attributes. Python calls `__init__` with that object as `self`, `"user"` as `role` and
`"Hi"` as `content`. Then the call returns the object, and `m` refers to it.

`self.role = role` stores an **instance attribute**: a value that belongs to this one
object. You read it with a dot, as in `m.role`.

`m.describe()` calls `Message.describe(m)`. The object before the dot is passed as the
first argument, `self`. Every method needs `self` as its first parameter.

`__repr__` returns the text that Python shows for the object. Here it uses `vars(self)`,
which returns a dict of the object's instance attributes.

Step through the code and watch the attributes appear on `self`.

```diagram
{"type": "trace", "title": "Creating a Message and calling its methods", "code": ["class Message:", "    def __init__(self, role, content):", "        self.role = role", "        self.content = content", "", "    def describe(self):", "        return f\"{self.role}: {self.content}\"", "", "    def __repr__(self):", "        return f\"Message({vars(self)})\"", "", "m = Message(\"user\", \"Hi\")", "print(m.role)", "print(m.describe())", "print(m)"], "steps": [
  {"line": 1, "vars": {}, "out": ""},
  {"line": 1, "vars": {}, "out": ""},
  {"line": 2, "vars": {}, "out": ""},
  {"line": 6, "vars": {}, "out": ""},
  {"line": 9, "vars": {}, "out": ""},
  {"line": 12, "vars": {}, "out": ""},
  {"line": 3, "vars": {"self": "Message({})", "role": "'user'", "content": "'Hi'"}, "out": "", "note": "Python created a Message object with no attributes and called __init__ with it as self."},
  {"line": 4, "vars": {"self": "Message({'role': 'user'})", "role": "'user'", "content": "'Hi'"}, "out": ""},
  {"line": 13, "vars": {"m": "Message({'role': 'user', 'content': 'Hi'})"}, "out": "", "note": "The call returned the object. The name m refers to it."},
  {"line": 14, "vars": {"m": "Message({'role': 'user', 'content': 'Hi'})"}, "out": "user\n"},
  {"line": 7, "vars": {"self": "Message({'role': 'user', 'content': 'Hi'})"}, "out": "user\n", "note": "m.describe() runs describe with self set to m."},
  {"line": 15, "vars": {"m": "Message({'role': 'user', 'content': 'Hi'})"}, "out": "user\nuser: Hi\n"},
  {"line": 10, "vars": {"self": "Message({'role': 'user', 'content': 'Hi'})"}, "out": "user\nuser: Hi\n", "note": "print(m) calls __repr__ because the class has no __str__."},
  {"line": null, "vars": {"m": "Message({'role': 'user', 'content': 'Hi'})"}, "out": "user\nuser: Hi\nMessage({'role': 'user', 'content': 'Hi'})\n"}
]}
```

### Class attributes

A **class attribute** is a name assigned in the class body, outside any method. Python
stores it once, on the class. Reading `obj.size` looks on the object first and then on the
class, so every instance reads the same value.

```python
class Chunker:
    size = 100

    def __init__(self, name):
        self.name = name

a = Chunker("a")
b = Chunker("b")
print(a.size, b.size)
# 100 100
Chunker.size = 50
print(a.size, b.size)
# 50 50
```

### Special methods

A **special method** has two underscores on each side of its name. It is also called a
**dunder** method. Python calls it when you use a built-in operation on the object.

| You write | Python calls |
| --- | --- |
| `len(obj)` | `obj.__len__()` |
| `str(obj)`, `print(obj)` | `obj.__str__()`, or `obj.__repr__()` if the class has no `__str__` |
| `repr(obj)` | `obj.__repr__()` |
| `a == b` | `a.__eq__(b)` |

```python
class Batch:
    def __init__(self, items):
        self.items = items

    def __len__(self):
        return len(self.items)

    def __repr__(self):
        return f"Batch({self.items!r})"

    def __eq__(self, other):
        if not isinstance(other, Batch):
            return NotImplemented
        return self.items == other.items

b = Batch(["a", "b"])
print(len(b))
# 2
print(b)
# Batch(['a', 'b'])
print(b == Batch(["a", "b"]))
# True
print(b == ["a", "b"])
# False
```

In an f-string, `{value!r}` inserts `repr(value)`, so strings keep their quotes.
`isinstance(other, Batch)` is `True` when `other` is a `Batch`. For any other type,
`__eq__` returns the built-in value `NotImplemented`, and `==` then gives `False`.

### Properties

A **property** is an attribute that calls one method when you read it and another method
when you assign to it. The setter can raise an exception before it stores a bad value.
The value itself is stored in a second attribute, `self._name`.

A line that starts with `@` above a `def` is a **decorator**: it changes how the method
below it works. `@property` makes that method the **getter**, which runs when you
read the attribute. `@name.setter` makes the second method the **setter**, which runs when
you assign to it. In `__init__`, `self.name = name` also calls the setter, so the first
value is checked too.

```python
class Agent:
    def __init__(self, name):
        self.name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if value == "":
            raise ValueError("name must not be empty")
        self._name = value

a = Agent("helper")
print(a.name)
# helper
try:
    a.name = ""
except ValueError as e:
    print("refused:", e)
# refused: name must not be empty
```

### Inheritance

`class ChatModel(Model):` makes `ChatModel` a **subclass** of `Model`, and `Model` is its
**base class**. A `ChatModel` instance can use every method of `Model`. A method defined again in the subclass
**overrides** the one in the base class. `super().__init__(name)` calls the base class's
`__init__` on the same object. A base method that every subclass must override raises
`NotImplementedError`.

```python
class Model:
    def __init__(self, name):
        self.name = name

    def kind(self):
        raise NotImplementedError("subclasses must define kind()")

    def label(self):
        return f"{self.name} ({self.kind()})"

class ChatModel(Model):
    def __init__(self, name, max_turns):
        super().__init__(name)
        self.max_turns = max_turns

    def kind(self):
        return "chat"

m = ChatModel("gpt-4o", 10)
print(m.label())
# gpt-4o (chat)
print(m.max_turns, isinstance(m, Model))
# 10 True
```

`label` is defined in `Model`, but `self.kind()` runs `ChatModel.kind` because `self` is a
`ChatModel`. One call that runs a different method depending on the object's class is
**polymorphism**.

### Common mistakes

- A method defined without `self`, such as `def describe():`, raises
  `TypeError: Message.describe() takes 0 positional arguments but 1 was given` when you call it.
- `role = role` in `__init__` stores nothing on the object. Write `self.role = role`.
- `messages = []` in the class body creates one list that every instance uses. Create
  lists in `__init__`.
- Without `__eq__`, `a == b` is `True` only when `a` and `b` are the same object.
- Inside a property setter, assign to `self._name`. Assigning to `self.name` calls the
  setter again and ends in `RecursionError`.
'''


EXERCISES = [
    {
        "id": "classes-s1",
        "title": "Two counters",
        "lesson": r'''
            ## Classes and instances

            A **class** is a new type that you define with the `class` keyword. You call a class
            the same way you call a function. Each call creates a new object of that type. That
            object is an **instance** of the class.

            ```python
            class Chat:
                def __init__(self, model):
                    self.model = model
                    self.turns = 0

            a = Chat("gpt")
            b = Chat("claude")
            a.turns = 5
            print(a.model, a.turns)
            # gpt 5
            print(b.model, b.turns)
            # claude 0
            ```

            `__init__` is the **initializer**: a function in the class that Python calls on every
            new instance. Many people call it the constructor. Its first parameter, `self`, is the
            new object. `self.turns = 0` stores the value `0` on that object under the name `turns`.

            Click each stage to see what Python does for `a = Chat("gpt")`.

            ```diagram
            {"type":"flow","title":"What Python does on a = Chat(\"gpt\")","steps":[{"label":"Create the object","detail":"Python creates a new Chat object. It has no attributes yet.","code":"vars(new object) -> {}"},{"label":"Call __init__","detail":"Python calls Chat.__init__. It passes the new object as self and 'gpt' as model.","code":"self = the new Chat object\nmodel = 'gpt'"},{"label":"Store the attributes","detail":"The two assignments in __init__ store two values on the object.","code":"self.model = model   # 'gpt'\nself.turns = 0"},{"label":"Return the object","detail":"__init__ ends. The call Chat(\"gpt\") returns the object, and the name a refers to it.","code":"a.model -> 'gpt'\na.turns -> 0"}]}
            ```

            `a` and `b` are two separate objects. Each one has its own `turns`, so `a.turns = 5`
            does not change `b.turns`.

            A function defined inside a class is a **method**. You call it with a dot, for example
            `a.send()`. Python runs the method with `self` set to `a`. A line such as
            `self.turns += 1` inside the method then changes `a.turns` and no other object.
        ''',
        "difficulty": 0,
        "mode": "predict",
        "prompt": r'''
            Read the code and type exactly what it prints.
        ''',
        "code": r'''
            class Counter:
                def __init__(self):
                    self.count = 0

                def add(self):
                    self.count += 1

            a = Counter()
            b = Counter()
            a.add()
            a.add()
            b.add()
            print(a.count)
            print(b.count)
        ''',
        "solution": r'''
            2
            1
        ''',
        "explanation": r'''
            `Counter()` is called twice, so `a` and `b` refer to two separate objects. `__init__`
            ran once for each object and stored `count = 0` on it. `a.add()` runs `add` with
            `self` set to `a`, so `self.count += 1` changes only `a.count`. `add` is called twice
            on `a` and once on `b`, so `a.count` is `2` and `b.count` is `1`.
        ''',
        "starter": "",
        "tests": "",
        "hints": [
            "Each `Counter()` call creates a new object with its own `count`.",
            "When you call `a.add()`, `self` inside `add` is `a`, so only `a.count` changes.",
            "Count how many times `add()` is called on `a` and on `b` separately; both start at 0.",
        ],
    },
    {
        "id": "classes-s2",
        "title": "Store the attributes",
        "lesson": r'''
            ## Instance attributes

            An **attribute** is a value stored on an object under a name. Inside `__init__`, the
            statement `self.name = name` creates the attribute `name` on the new object and stores
            the value of the parameter `name` in it. You read an attribute with a dot: `gpt.name`.

            ```python
            class Model:
                def __init__(self, name, context):
                    self.name = name
                    self.context = context

            gpt = Model("gpt-4o", 128000)
            llama = Model("llama", 8000)
            print(gpt.name)
            # gpt-4o
            print(gpt.context)
            # 128000
            print(llama.name)
            # llama
            ```

            The arguments you pass to `Model(...)` arrive in `__init__` as its parameters, after
            `self`. Python fills in `self` with the new object. Parameters are local variables:
            they stop existing when `__init__` returns. A value is kept only if you assign it to
            an attribute on `self`.

            An attribute that belongs to one instance is an **instance attribute**. `gpt` and
            `llama` each have their own `name` and `context`.

            `name = name` inside `__init__` assigns the parameter to itself and stores nothing on
            the object. Reading `gpt.name` then raises `AttributeError`. Write `self.name = name`.
        ''',
        "difficulty": 0,
        "prompt": r'''
            A `Message` object should remember the role and text of a chat message.

            **Write:** fill in the blanks (`___`) in `Message.__init__`

            - `role`: a string like `"user"`
            - `content`: a string like `"Hi"`

            **Rules**
            - After `m = Message(role, content)`, `m.role` is the role and `m.content` is the content.
            - Two messages keep their own values (one does not overwrite the other).

            **Examples**
            ```python
            m = Message("user", "Hi")
            m.role      # "user"
            m.content   # "Hi"
            Message("assistant", "b").role   # "assistant"
            ```
        ''',
        "starter": r'''
            class Message:
                def __init__(self, role, content):
                    self.role = ___
                    self.content = ___
        ''',
        "tests": r'''
            from solution import Message

            def test_role_is_stored_on_the_object():
                m = Message("user", "Hi")
                assert m.role == "user", f"m.role is {m.role!r}"

            def test_content_is_stored_on_the_object():
                m = Message("user", "Hi")
                assert m.content == "Hi", f"m.content is {m.content!r}"

            def test_two_messages_keep_their_own_values():
                a = Message("user", "a")
                b = Message("assistant", "b")
                assert (a.role, a.content, b.role, b.content) == ("user", "a", "assistant", "b")
        ''',
        "solution": r'''
            class Message:
                def __init__(self, role, content):
                    self.role = role
                    self.content = content
        ''',
        "hints": [
            "`__init__` receives the values you pass to `Message(...)` as its parameters.",
            "Each attribute on `self` should get the value of the matching parameter.",
            "Replace the first `___` with the parameter `role` and the second with the parameter `content`.",
        ],
    },
    {
        "id": "classes-s3",
        "title": "Fix the bug: missing self",
        "lesson": r'''
            ## Methods and `self`

            A **method** is a function defined inside a class. When you write `m.describe()`,
            Python calls `Message.describe(m)`. The object before the dot is passed as the first
            argument.

            ```python
            class Message:
                def __init__(self, text):
                    self.text = text

                def describe(self):
                    return "Message: " + self.text

            m = Message("Hi")
            print(m.describe())
            # Message: Hi
            print(Message.describe(m))
            # Message: Hi
            ```

            The first parameter of a method receives that object. By convention it is named
            `self`. Every method needs it, including a method that takes no other arguments.

            A method defined without `self` raises `TypeError` when you call it, because Python
            still passes the object. This example catches the error and prints its message.

            ```python
            class Greeter:
                def hello():
                    return "hello"

            try:
                Greeter().hello()
            except TypeError as e:
                print(e)
            # Greeter.hello() takes 0 positional arguments but 1 was given
            ```

            The `1` in the message is the object that Python passed. When you see this message on
            a method call, check the `def` line for `self`.
        ''',
        "difficulty": 0,
        "prompt": r'''
            `Prompt("hi").shout()` should return the prompt's text in capitals, but it
            crashes with a `TypeError`. Find and fix the one bug.

            **Write:** fix the method `shout()` of the class `Prompt`

            - **Returns:** the object's own `text` in upper case, e.g. `"HI"`

            **Rules**
            - `shout()` must not change `text` itself (it returns a new string).

            **Examples**
            ```python
            Prompt("hi").shout()               # "HI"
            Prompt("Summarize this").shout()   # "SUMMARIZE THIS"
            p = Prompt("abc")
            p.shout()                          # "ABC"
            p.text                             # still "abc"
            ```
        ''',
        "starter": r'''
            class Prompt:
                def __init__(self, text):
                    self.text = text

                def shout():
                    return self.text.upper()
        ''',
        "tests": r'''
            from solution import Prompt

            def test_shout_returns_uppercase_text():
                got = Prompt("hi").shout()
                assert got == "HI", f"got {got!r}"

            def test_shout_uses_the_objects_own_text():
                got = Prompt("Summarize this").shout()
                assert got == "SUMMARIZE THIS", f"got {got!r}"

            def test_shout_does_not_change_text_attribute():
                p = Prompt("abc")
                p.shout()
                assert p.text == "abc"
        ''',
        "solution": r'''
            class Prompt:
                def __init__(self, text):
                    self.text = text

                def shout(self):
                    return self.text.upper()
        ''',
        "hints": [
            "Compare the `def` line of `shout` with the `def` line of `__init__`.",
            "Python always passes the object as the first argument to a method, so every method needs a parameter to receive it.",
            "Add `self` as the parameter of `shout`: the body already uses it.",
        ],
    },
    {
        "id": "classes-s4",
        "title": "A method that counts words",
        "lesson": r'''
            ## Methods that return a value

            A method can read the object's attributes and return a result computed from them.
            Inside the method, you reach each attribute through `self`.

            ```python
            class Prompt:
                def __init__(self, text):
                    self.text = text

                def char_count(self):
                    return len(self.text)

            p = Prompt("Summarize this")
            q = Prompt("Hi")
            print(p.char_count())
            # 14
            print(q.char_count())
            # 2
            ```

            `p.char_count()` runs the method with `self` set to `p`. `q.char_count()` runs it with
            `self` set to `q`. The same method returns two different results because `self.text`
            is a different string in each call.

            A method that only reads attributes and returns a result is sometimes called a
            **query method**. A method is a function, so everything you know about functions
            applies. It can use `if`, loops and string methods, and it must `return` its result.

            Writing `text` instead of `self.text` inside `char_count` raises `NameError`. `text`
            was a parameter of `__init__`, and it stopped existing when `__init__` returned. Only
            the attribute `self.text` still exists.
        ''',
        "difficulty": 0,
        "prompt": r'''
            A `Document` (like one you would index for RAG) should be able to count its words.

            **Write:** the method `word_count()` of the class `Document`

            - **Returns:** an int, the number of words in the document's own `text`
              (words are separated by whitespace: spaces, tabs, newlines)

            **Rules**
            - Empty text has `0` words.
            - Each document counts its **own** text.

            **Examples**
            ```python
            Document("notes", "RAG uses retrieval").word_count()   # 3
            Document("a", "one two").word_count()                  # 2
            Document("empty", "").word_count()                     # 0
            ```
        ''',
        "starter": r'''
            class Document:
                def __init__(self, title, text):
                    self.title = title
                    self.text = text

                def word_count(self):
                    ...
        ''',
        "tests": r'''
            from solution import Document

            def test_counts_words_in_text():
                got = Document("notes", "RAG uses retrieval").word_count()
                assert got == 3, f"got {got!r}"

            def test_empty_text_has_zero_words():
                got = Document("empty", "").word_count()
                assert got == 0, f"got {got!r}"

            def test_each_document_counts_its_own_text():
                a = Document("a", "one two")
                b = Document("b", "one two three four")
                assert (a.word_count(), b.word_count()) == (2, 4)
        ''',
        "solution": r'''
            class Document:
                def __init__(self, title, text):
                    self.title = title
                    self.text = text

                def word_count(self):
                    return len(self.text.split())
        ''',
        "hints": [
            "Inside the method, the document's text is `self.text`.",
            "Split the text into a list of words, then count the items in that list.",
            "Return `len(...)` of `self.text.split()`.",
        ],
    },
    {
        "id": "classes-s5",
        "title": "A tiny chat",
        "lesson": r'''
            ## State

            An object keeps its attributes after a method returns. One method call can change an
            attribute, and a later call can read the new value. The attribute values that an
            object holds are its **state**.

            ```python
            class History:
                def __init__(self):
                    self.items = []

                def remember(self, thing):
                    self.items.append(thing)

            h = History()
            h.remember("first")
            h.remember("second")
            print(h.items)
            # ['first', 'second']
            print(History().items)
            # []
            ```

            `h.remember("first")` runs `self.items.append("first")` with `self` set to `h`, so the
            string is added to the list stored on `h`. `History()` on the last line creates a
            second object. Its `__init__` creates a second list, which is empty.

            A method that changes the state is called a **mutating method**. It usually has no
            `return` statement, so it returns `None`.

            Create lists and dicts inside `__init__`. `__init__` runs once for each instance, so
            every instance gets a new list.

            `items = []` in the class body, outside any method, creates one list stored on the
            class. `self.items` then refers to that same list in every instance, so an item
            appended through one instance appears in all of them.
        ''',
        "difficulty": 0,
        "prompt": r'''
            A chat object that remembers the messages sent to it, in order.

            **Write:** the class `Chat` (the starter has the two methods to fill in)

            - `Chat()`: takes no arguments. It creates the attribute `messages`, a new
              empty list.
            - `add(text)`: `text` is a string like `"Hi"`. Puts it at the end of `messages`.
              **Returns:** nothing.

            **Rules**
            - A new chat's `messages` is `[]`.
            - Messages stay in the order they were added.
            - Every chat has its **own** list: adding to one chat must not change another.

            **Examples**
            ```python
            c = Chat()
            c.messages       # []
            c.add("Hi")
            c.add("How are you?")
            c.messages       # ["Hi", "How are you?"]

            other = Chat()
            other.messages   # [] (c's messages are not here)
            ```
        ''',
        "starter": r'''
            class Chat:
                def __init__(self):
                    ...

                def add(self, text):
                    ...
        ''',
        "tests": r'''
            from solution import Chat

            def test_new_chat_has_empty_messages_list():
                assert Chat().messages == []

            def test_add_appends_messages_in_order():
                c = Chat()
                c.add("Hi")
                c.add("How are you?")
                assert c.messages == ["Hi", "How are you?"], f"messages: {c.messages!r}"

            def test_chats_do_not_share_messages():
                a = Chat()
                b = Chat()
                a.add("only in a")
                assert b.messages == [], f"b.messages is {b.messages!r}"
        ''',
        "solution": r'''
            class Chat:
                def __init__(self):
                    self.messages = []

                def add(self, text):
                    self.messages.append(text)
        ''',
        "hints": [
            "Data that each object owns is created in `__init__` and stored on `self`.",
            "In `__init__`, give `self.messages` a new empty list. In `add`, put `text` at the end of that same list.",
            "1) `__init__`: set `self.messages` to `[]`. 2) `add`: call `.append(text)` on `self.messages`.",
        ],
    },
    {
        "id": "classes-s6",
        "title": "Make len() and print() work",
        "lesson": r'''
            ## Special methods

            Built-in functions such as `len()` and `str()` work on lists and strings. They also
            work on your own objects when the class defines the matching **special method**. A
            special method has two underscores on each side of its name, so it is also called a
            **dunder** method (short for double underscore). `__init__` is one of them.

            ```python
            class Batch:
                def __init__(self, items):
                    self.items = items

                def __len__(self):
                    return len(self.items)

                def __str__(self):
                    return f"Batch of {len(self.items)}"

            b = Batch(["a", "b", "c"])
            print(len(b))
            # 3
            print(str(b))
            # Batch of 3
            print(b)
            # Batch of 3
            ```

            `len(b)` calls `b.__len__()` and returns its result. `str(b)` calls `b.__str__()`.
            `print(b)` converts `b` with `str()` first, so it prints the same text. You define
            special methods and Python calls them. You do not normally call them yourself.

            The Python documentation describes all special methods under the name "data model".

            `__len__` must return an int and `__str__` must return a string. A `__str__` that
            prints the text and returns nothing makes `str(b)` raise
            `TypeError: __str__ returned non-string (type NoneType)`.
        ''',
        "difficulty": 0,
        "prompt": r'''
            A `Snippet` holds a piece of text you might paste into a prompt. Make it work with
            the built-in `len()` and `str()`/`print()`.

            **Write:** fill in the two blanks (`___`) in the class `Snippet`

            - `Snippet(text)`: `text` is a string like `"hello"`, stored as `self.text`
            - `len(snippet)` (special method `__len__`): **Returns** the number of characters
              in `text` (an int)
            - `str(snippet)` (special method `__str__`): **Returns** the string
              `"Snippet: <text>"`

            **Rules**
            - An empty snippet has length `0` and `str` gives `"Snippet: "`.
            - `print(snippet)` therefore prints `Snippet: <text>`.

            **Examples**
            ```python
            s = Snippet("hello")
            len(s)      # 5
            str(s)      # "Snippet: hello"
            print(s)    # prints: Snippet: hello
            len(Snippet(""))   # 0
            ```
        ''',
        "starter": r'''
            class Snippet:
                def __init__(self, text):
                    self.text = text

                def __len__(self):
                    return ___

                def __str__(self):
                    return ___
        ''',
        "tests": r'''
            from solution import Snippet

            def test_len_is_number_of_characters():
                got = len(Snippet("hello"))
                assert got == 5, f"len -> {got!r}"

            def test_str_has_snippet_prefix():
                got = str(Snippet("hello"))
                assert got == "Snippet: hello", f"str -> {got!r}"

            def test_print_shows_the_str_version():
                s = Snippet("RAG")
                _, out = capture(print, s)
                assert out.strip() == "Snippet: RAG", f"printed {out!r}"

            def test_empty_snippet():
                s = Snippet("")
                assert len(s) == 0 and str(s) == "Snippet: ", f"len={len(s)!r} str={str(s)!r}"
        ''',
        "solution": r'''
            class Snippet:
                def __init__(self, text):
                    self.text = text

                def __len__(self):
                    return len(self.text)

                def __str__(self):
                    return f"Snippet: {self.text}"
        ''',
        "hints": [
            "Inside both methods the snippet's text is `self.text`.",
            "`__len__` hands back the length of that text; `__str__` builds a new string with the label in front.",
            "1) First blank: `len(...)` of `self.text`. 2) Second blank: an f-string with `Snippet: ` followed by `self.text` in braces.",
        ],
    },
    {
        "id": "classes-1",
        "title": "Message class",
        "lesson": r'''
            ## `__repr__`

            `__str__` returns the text meant for users. `__repr__` returns the text meant for
            developers. Python calls `obj.__repr__()` when you call `repr(obj)` and when you print a
            list or a dict that contains the object.
            A class without `__repr__` gets the default text `<__main__.Tool object at 0x7f...>`,
            which shows no attribute values.

            Write `__repr__` so that it returns the code that would create the object.

            ```python
            class Tool:
                def __init__(self, name, cost):
                    self.name = name
                    self.cost = cost

                def __repr__(self):
                    return f"Tool(name={self.name!r}, cost={self.cost!r})"

            print(repr(Tool("search", 2)))
            # Tool(name='search', cost=2)
            print([Tool("calc", 0)])
            # [Tool(name='calc', cost=0)]
            ```

            Inside an f-string, `{value!r}` inserts `repr(value)` instead of `str(value)`. The
            `repr` of a string includes its quotes, so the name appears as `'search'` and not as
            `search`. The string `"2"` then appears as `'2'` and the int `2` as `2`, so you can
            tell them apart.

            If a class has `__repr__` but no `__str__`, `str(obj)` and `print(obj)` use `__repr__`.

            `f"{self.name}"` leaves the quotes out. Use `f"{self.name!r}"`.
        ''',
        "hints": [
            "You need three methods: `__init__` to store the values, `to_dict`, and `__repr__` (what `repr()` shows).",
            "`__init__` stores `role` and `content` on `self`; `to_dict` builds a dict from `self.role` and `self.content`; `__repr__` returns a string built with an f-string.",
            "In `__repr__`, put `!r` after each value inside the f-string braces (for example `self.role!r`) so the values get quotes exactly like `repr()` gives them, and match the format `Message(role=..., content=...)`.",
        ],
        "difficulty": 1,
        "prompt": r'''
            A chat message object, the kind you send to an LLM API.

            **Write:** the class `Message`

            - `Message(role, content)`: `role` is a string like `"user"`, `content` is a
              string like `"hi"`. Store them as the attributes `role` and `content`.
            - `to_dict()`: **Returns** a dict `{"role": <role>, "content": <content>}`.
            - `repr(msg)` (write the special method `__repr__`): **Returns** a string like
              `Message(role='user', content='hi')`.

            **Rules**
            - In the `repr` string each value appears as its own `repr()` would show it
              (with quotes). For example the content `it's` appears as `"it's"`, because
              that is what `repr("it's")` gives.
            - Each `Message` object keeps its own `role` and `content`.

            **Examples**
            ```python
            m = Message("user", "hi")
            m.role                                  # "user"
            m.content                               # "hi"
            Message("assistant", "Hello!").to_dict()  # {"role": "assistant", "content": "Hello!"}
            repr(m)                                 # "Message(role='user', content='hi')"
            print(repr(Message("user", "it's")))    # prints: Message(role='user', content="it's")
            ```
        ''',
        "starter": r'''
            class Message:
                ...
        ''',
        "tests": r'''
            from solution import Message

            def test_role_and_content_stored_as_attributes():
                m = Message("user", "hi")
                assert (m.role, m.content) == ("user", "hi"), f"got role={getattr(m, 'role', None)!r} content={getattr(m, 'content', None)!r}"

            def test_to_dict_returns_role_and_content():
                got = Message("assistant", "Hello!").to_dict()
                assert got == {"role": "assistant", "content": "Hello!"}, f"got {got!r}"

            def test_repr_has_exact_format():
                got = repr(Message("user", "hi"))
                assert got == "Message(role='user', content='hi')", f"got {got!r}"

            def test_repr_shows_values_with_their_own_repr_quotes():
                got = repr(Message("user", "it's"))
                assert got == "Message(role='user', content=" + repr("it's") + ")", f"got {got!r}"

            def test_each_message_keeps_its_own_values():
                a, b = Message("user", "a"), Message("system", "b")
                assert a.content == "a" and b.role == "system"
        ''',
        "solution": r'''
            class Message:
                def __init__(self, role, content):
                    self.role = role
                    self.content = content

                def to_dict(self):
                    return {"role": self.role, "content": self.content}

                def __repr__(self):
                    return f"Message(role={self.role!r}, content={self.content!r})"
        ''',
    },
    {
        "id": "classes-2",
        "title": "Token counter",
        "lesson": r'''
            ## Class attributes

            An instance attribute is stored separately on each instance. A **class attribute** is
            stored once, on the class. You create it by assigning a name directly in the class
            body, outside any method.

            ```python
            class Chunker:
                size = 100            # class attribute

                def __init__(self, name):
                    self.name = name  # instance attribute

            a = Chunker("a")
            b = Chunker("b")
            print(a.size, b.size)
            # 100 100
            Chunker.size = 50
            print(a.size, b.size)
            # 50 50
            ```

            Click each stage to see how Python finds the value of `a.size`.

            ```diagram
            {"type":"flow","title":"How Python reads a.size","steps":[{"label":"Look on the instance","detail":"Python looks for the name size among the attributes stored on a. The only attribute stored there is name.","code":"vars(a) -> {'name': 'a'}"},{"label":"Look on the class","detail":"size is not stored on a, so Python looks on the class of a, which is Chunker. It finds size there.","code":"Chunker.size -> 100"},{"label":"Return the value","detail":"a.size evaluates to 100. Reading b.size takes the same two lookups and reads the same class attribute.","code":"a.size -> 100\nb.size -> 100"}]}
            ```

            The same lookup happens for `self.size` inside a method. That is why a method can
            read a class attribute through `self`, and why `Chunker.size = 50` changes the value
            that every instance reads.

            Use class attributes for settings and constants that belong to the whole class, such
            as a `chars_per_token` ratio.

            Do not write the number a second time inside a method. Read it through `self.`, so
            that a change to the class attribute takes effect. A list assigned as a class
            attribute is one list that every instance uses.
        ''',
        "hints": [
            "A class attribute is written directly in the class body (not in `__init__`); per-object data goes on `self` inside `__init__`.",
            "Put `chars_per_token = 4` in the class body and `self.total = 0` in `__init__`. `add` works out the tokens, adds them to the total and returns them.",
            "1) `import math`; `math.ceil(...)` rounds up. 2) tokens = ceil of `len(text)` divided by `self.chars_per_token`. 3) Add tokens to `self.total` with `+=` and return tokens. 4) `reset` sets `self.total` back to 0.",
        ],
        "difficulty": 1,
        "prompt": r'''
            A rough token counter, to keep track of how much text you have sent to a model.

            **Write:** the class `TokenCounter`

            - `chars_per_token`: a **class attribute** (written in the class body, shared
              by all counters) with the value `4`.
            - `TokenCounter()`: takes no arguments. Each counter gets its own attribute
              `total`, starting at `0`.
            - `add(text)`: `text` is a string like `"hello world"`. Estimates its tokens as
              `len(text)` divided by `chars_per_token`, **rounded up** to a whole number
              (`math.ceil` from the `math` module rounds up: write `import math` at the top
  of the file). Adds that to `total`.
              **Returns:** the token estimate for this text (an int).
            - `reset()`: sets `total` back to `0`.

            **Rules**
            - Read `chars_per_token` through the object/class (e.g. `self.chars_per_token`),
              not a hard-coded `4`: if someone changes `TokenCounter.chars_per_token` to `2`,
              `add("abcde")` must return `3`.
            - Empty text is `0` tokens.
            - Each counter has its own `total`: adding to one does not change another.

            **Examples**
            ```python
            c = TokenCounter()
            c.add("hello world")   # 3   (11 chars / 4 = 2.75, rounded up)
            c.add("hi")            # 1
            c.total                # 4
            c.add("")              # 0
            c.reset()
            c.total                # 0
            TokenCounter().total   # 0
            ```
        ''',
        "starter": r'''
            class TokenCounter:
                ...
        ''',
        "tests": r'''
            from solution import TokenCounter

            def test_add_returns_rounded_up_tokens_and_updates_total():
                c = TokenCounter()
                got = c.add("hello world")
                assert got == 3, f"add('hello world') returned {got!r}"
                got = c.add("hi")
                assert got == 1, f"add('hi') returned {got!r}"
                assert c.total == 4, f"total is {c.total}"

            def test_empty_text_is_zero_tokens():
                c = TokenCounter()
                assert c.add("") == 0 and c.total == 0

            def test_each_counter_has_its_own_total():
                a, b = TokenCounter(), TokenCounter()
                a.add("abcdefgh")
                assert b.total == 0, f"a second counter's total is {b.total}"

            def test_reset_sets_total_to_zero():
                c = TokenCounter()
                c.add("abcdef")
                c.reset()
                assert c.total == 0, f"total is {c.total} after reset()"

            def test_chars_per_token_is_a_class_attribute_used_by_add():
                assert "chars_per_token" in vars(TokenCounter), "chars_per_token must be a class attribute"
                old = TokenCounter.chars_per_token
                try:
                    TokenCounter.chars_per_token = 2
                    c = TokenCounter()
                    got = c.add("abcde")
                    assert got == 3, f"with chars_per_token=2, add('abcde') returned {got}"
                finally:
                    TokenCounter.chars_per_token = old
        ''',
        "solution": r'''
            import math


            class TokenCounter:
                chars_per_token = 4

                def __init__(self):
                    self.total = 0

                def add(self, text):
                    tokens = math.ceil(len(text) / self.chars_per_token)
                    self.total += tokens
                    return tokens

                def reset(self):
                    self.total = 0
        ''',
    },
    {
        "id": "classes-7",
        "title": "Equal usage records",
        "lesson": r'''
            ## `__eq__`

            By default, `a == b` on your own objects is `True` only when `a` and `b` are the same
            object. Two separate instances are not equal, even if every attribute has the same
            value.

            ```python
            class Point:
                def __init__(self, x):
                    self.x = x

            print(Point(1) == Point(1))
            # False

            class Coord:
                def __init__(self, x):
                    self.x = x

                def __eq__(self, other):
                    if not isinstance(other, Coord):
                        return NotImplemented
                    return self.x == other.x

            print(Coord(1) == Coord(1))
            # True
            print(Coord(1) == 1)
            # False
            ```

            `a == b` calls `a.__eq__(b)`. When you define `__eq__(self, other)`, you decide what
            equal means for your class. Usually it means that the attributes that matter are
            equal. To check several attributes at once, compare two tuples:
            `(self.x, self.y) == (other.x, other.y)`.

            `isinstance(other, Coord)` is `True` when `other` is an instance of `Coord`.

            `NotImplemented` is a built-in value, not an exception. Returning it means that this
            method cannot compare `self` with `other`. Python then uses its default comparison
            (are they the same object?), so `==` gives `False` and no exception is raised.

            Do not `raise NotImplementedError` here. That is an exception with a different
            purpose. `__eq__` returns the value `NotImplemented`.
        ''',
        "difficulty": 1,
        "prompt": r'''
            Token-usage records from two runs should count as the same when they describe the
            same model and the same number of tokens.

            **Write:** the class `Usage`

            - `Usage(model, tokens)`: `model` is a string like `"gpt-4o"`, `tokens` an int
              like `120`. Store them as the attributes `model` and `tokens`.
            - `==` (special method `__eq__`): two `Usage` objects are equal when **both**
              `model` and `tokens` are equal.

            **Rules**
            - Same model but different tokens -> not equal. Same tokens but different
              model -> not equal.
            - Comparing with something that is not a `Usage` gives `False` (no error),
              e.g. `Usage("a", 1) == ("a", 1)` is `False`.
            - `!=` works automatically once `==` works.

            **Examples**
            ```python
            Usage("gpt-4o", 120) == Usage("gpt-4o", 120)   # True
            Usage("gpt-4o", 120) == Usage("gpt-4o", 99)    # False
            Usage("gpt-4o", 120) == Usage("haiku", 120)    # False
            Usage("gpt-4o", 120) == "gpt-4o"               # False
            ```
        ''',
        "starter": r'''
            class Usage:
                def __init__(self, model, tokens):
                    self.model = model
                    self.tokens = tokens
        ''',
        "tests": r'''
            from solution import Usage

            def test_same_model_and_tokens_are_equal():
                assert Usage("gpt-4o", 120) == Usage("gpt-4o", 120), "two identical records are not equal"

            def test_different_tokens_are_not_equal():
                assert Usage("gpt-4o", 120) != Usage("gpt-4o", 99)

            def test_different_model_is_not_equal():
                assert Usage("gpt-4o", 120) != Usage("haiku", 120)

            def test_comparing_with_other_types_gives_false():
                assert (Usage("a", 1) == ("a", 1)) is False
                assert (Usage("a", 1) == "a") is False

            def test_attributes_are_stored():
                u = Usage("m", 7)
                assert (u.model, u.tokens) == ("m", 7)
        ''',
        "solution": r'''
            class Usage:
                def __init__(self, model, tokens):
                    self.model = model
                    self.tokens = tokens

                def __eq__(self, other):
                    if not isinstance(other, Usage):
                        return NotImplemented
                    return (self.model, self.tokens) == (other.model, other.tokens)
        ''',
        "hints": [
            "Add a special method `__eq__(self, other)` to the class; Python calls it for `==`.",
            "First make sure `other` is a `Usage` at all; if not, return the value that means the comparison is not supported. Otherwise compare both attributes of `self` with both attributes of `other`.",
            "1) If `not isinstance(other, Usage)`, return `NotImplemented`. 2) Return whether `(self.model, self.tokens)` equals `(other.model, other.tokens)`.",
        ],
    },
    {
        "id": "classes-8",
        "title": "Guarded max_tokens",
        "lesson": r'''
            ## Properties

            A normal attribute accepts any value. `agent.max_turns = -5` succeeds, and the error
            appears only later, when other code uses that bad number.

            A **property** is an attribute that runs a method each time you read it or assign to it.
            You write two methods. Reading the attribute calls the **getter**.
            Assigning to it calls the **setter**, which can check the value and raise an exception
            before it stores anything.

            ```python
            class Agent:
                def __init__(self, name):
                    self.name = name          # calls the setter below

                @property
                def name(self):               # getter: runs on a.name
                    return self._name

                @name.setter
                def name(self, value):        # setter: runs on a.name = ...
                    if value == "":
                        raise ValueError("name must not be empty")
                    self._name = value

            a = Agent("helper")
            print(a.name)
            # helper
            try:
                a.name = ""
            except ValueError as e:
                print("refused:", e)
            # refused: name must not be empty
            print(a.name)
            # helper
            ```

            A line that starts with `@` above a `def` is a **decorator**: Python passes the
            function below it to the decorator and uses the result in its place. `@property`
            makes `name` a property with that method as its getter. `@name.setter` adds the
            second method as its setter.

            The value itself is stored in `self._name`. A leading underscore is a convention: it
            marks an attribute as internal, so code outside the class should not use it.

            `__init__` assigns `self.name`, which calls the setter. The value passed to
            `Agent(...)` is therefore checked too.

            Inside the setter, assign to `self._name`, not `self.name`. Assigning to `self.name`
            calls the setter again, which calls it again, until Python raises `RecursionError`.
        ''',
        "research": {
            "note": "Skim the official description of the built-in `property` - look at the example with a getter, a setter and the `@x.setter` form - then come back.",
            "links": [
                {"title": "property - Python built-in functions", "url": "https://docs.python.org/3/library/functions.html#property"},
            ],
        },
        "difficulty": 1,
        "prompt": r'''
            An LLM request whose `max_tokens` can never be set to a nonsense value.

            **Write:** the class `Request`

            - `Request(prompt, max_tokens=256)`: `prompt` is a string, stored as the
              attribute `prompt`. `max_tokens` is an int, default `256`.
            - `max_tokens`: must be a **property** (`@property` plus a setter) so every
              assignment is checked: in `__init__` and later (`req.max_tokens = 50`).

            **Rules**
            - A value below `1` raises `ValueError` (`0` and negative numbers are refused;
              `1` is allowed).
            - The constructor checks too: `Request("hi", 0)` raises `ValueError`.
            - A refused assignment leaves the old value in place.

            **Examples**
            ```python
            req = Request("Summarize this")
            req.max_tokens          # 256
            req.max_tokens = 50
            req.max_tokens          # 50
            req.max_tokens = 0      # raises ValueError
            req.max_tokens          # still 50
            Request("hi", -3)       # raises ValueError
            ```
        ''',
        "starter": r'''
            class Request:
                ...
        ''',
        "tests": r'''
            from solution import Request

            def _raises_value_error(fn):
                try:
                    fn()
                except ValueError:
                    return True
                return False

            def test_default_and_setting_a_valid_value():
                req = Request("Summarize this")
                assert req.prompt == "Summarize this"
                assert req.max_tokens == 256, f"default is {req.max_tokens!r}"
                req.max_tokens = 50
                assert req.max_tokens == 50
                req.max_tokens = 1
                assert req.max_tokens == 1, "1 must be allowed"

            def test_zero_or_negative_raises_and_keeps_old_value():
                req = Request("x", 50)
                assert _raises_value_error(lambda: setattr(req, "max_tokens", 0)), "0 was accepted"
                assert _raises_value_error(lambda: setattr(req, "max_tokens", -5)), "-5 was accepted"
                assert req.max_tokens == 50, f"max_tokens is now {req.max_tokens!r}"

            def test_constructor_also_checks():
                assert _raises_value_error(lambda: Request("hi", -3)), "Request('hi', -3) was accepted"

            def test_max_tokens_is_a_property():
                assert isinstance(vars(Request).get("max_tokens"), property), "max_tokens must be a property"
        ''',
        "solution": r'''
            class Request:
                def __init__(self, prompt, max_tokens=256):
                    self.prompt = prompt
                    self.max_tokens = max_tokens

                @property
                def max_tokens(self):
                    return self._max_tokens

                @max_tokens.setter
                def max_tokens(self, value):
                    if value < 1:
                        raise ValueError(f"max_tokens must be at least 1, got {value}")
                    self._max_tokens = value
        ''',
        "hints": [
            "You need a getter decorated with `@property` and a setter decorated with `@max_tokens.setter`, both named `max_tokens`.",
            "Keep the real number in a hidden attribute like `self._max_tokens`. The setter checks the value before storing it; `__init__` just assigns `self.max_tokens` so it goes through the setter.",
            "1) `__init__`: store `prompt`, then `self.max_tokens = max_tokens`. 2) Getter returns `self._max_tokens`. 3) Setter: if the value is below 1, raise `ValueError`; otherwise store it in `self._max_tokens`.",
        ],
    },
    {
        "id": "classes-9",
        "title": "Tools that inherit",
        "lesson": r'''
            ## Inheritance

            **Inheritance** lets you define a class that starts with every method of an existing
            class. You write `class Child(Parent):`. Instances of `Child` can use all the methods
            of `Parent`, so in `Child` you write only what is different.

            ```python
            class Model:
                def __init__(self, name):
                    self.name = name

                def label(self):
                    return f"model {self.name} ({self.kind()})"

                def kind(self):
                    return "generic"

            class ChatModel(Model):
                def __init__(self, name, max_turns):
                    super().__init__(name)      # run the parent's __init__
                    self.max_turns = max_turns

                def kind(self):                 # override one method
                    return "chat"

            m = ChatModel("gpt-4o", 10)
            print(m.label())
            # model gpt-4o (chat)
            print(m.max_turns, isinstance(m, Model))
            # 10 True
            ```

            `Model` is the **base class** (or parent) and `ChatModel` is the **subclass** (or
            child). Defining `kind` again in the subclass **overrides** it: `ChatModel` objects
            use the new version.

            Click each stage to see which methods Python runs for `m.label()`.

            ```diagram
            {"type":"flow","title":"What Python does on m.label()","steps":[{"label":"Find label","detail":"Python looks for label on the class of m, which is ChatModel. ChatModel does not define it, so Python looks on the base class Model and finds it.","code":"m.label  ->  Model.label"},{"label":"Run Model.label","detail":"Python calls Model.label with m as self. The f-string needs the value of self.kind().","code":"self = m   # a ChatModel\nf\"model {self.name} ({self.kind()})\""},{"label":"Find kind","detail":"self is a ChatModel, so the lookup starts at ChatModel again. ChatModel defines kind, so Model.kind is not used.","code":"self.kind  ->  ChatModel.kind\nself.kind() -> 'chat'"},{"label":"Return the string","detail":"Model.label returns the finished string and print shows it.","code":"model gpt-4o (chat)"}]}
            ```

            `label` is written once, in `Model`, and still calls the subclass's `kind`. One call
            that runs a different method depending on the object's class is **polymorphism**.

            `super().__init__(name)` calls the parent's `__init__` on the same object. The parent
            stores `name`, and then the child stores its own attribute. `isinstance(m, Model)` is
            `True` because an instance of a subclass is also an instance of the base class.

            A base class can require every subclass to define a method. It defines the method
            with a body that raises `NotImplementedError`. A subclass that does not override the
            method raises that exception when the method is called.
        ''',
        "research": {
            "note": "Read the tutorial section on inheritance and the entry for `super()`, then come back.",
            "links": [
                {"title": "Inheritance - Python tutorial", "url": "https://docs.python.org/3/tutorial/classes.html#inheritance"},
                {"title": "super() - Python built-in functions", "url": "https://docs.python.org/3/library/functions.html#super"},
            ],
        },
        "difficulty": 1,
        "prompt": r'''
            An agent has several tools. They share a base class, and each subclass only
            changes what is different.

            **Write:** the subclasses `UpperTool` and `PrefixTool` (the base class `Tool` is
            in the starter: don't change it)

            **`UpperTool`**, a subclass of `Tool`
            - `run(text)`: **Returns** `text` in upper case.

            **`PrefixTool`**, a subclass of `Tool`
            - `PrefixTool(name, prefix)`: stores `name` by calling the parent's `__init__`
              with `super()`, and stores `prefix` (a string) as the attribute `prefix`.
            - `run(text)`: **Returns** `prefix + text`.

            **Rules**
            - Both must inherit from `Tool`.
            - Neither subclass defines its own `describe`; they reuse the parent's.
            - `PrefixTool.__init__` must call `super().__init__(...)` (a check looks for it).

            **Examples**
            ```python
            u = UpperTool("shout")
            u.run("hi")          # "HI"
            u.describe()         # "tool shout"
            p = PrefixTool("tag", ">> ")
            p.name, p.prefix     # ("tag", ">> ")
            p.run("hello")       # ">> hello"
            p.describe()         # "tool tag"
            ```
        ''',
        "starter": r'''
            class Tool:
                def __init__(self, name):
                    self.name = name

                def describe(self):
                    return f"tool {self.name}"

                def run(self, text):
                    raise NotImplementedError("subclasses must implement run()")


            class UpperTool:
                ...


            class PrefixTool:
                ...
        ''',
        "tests": r'''
            from solution import Tool, UpperTool, PrefixTool

            def test_upper_tool_runs_and_describes():
                u = UpperTool("shout")
                assert u.run("hi") == "HI", f"run -> {u.run('hi')!r}"
                assert u.describe() == "tool shout", f"describe -> {u.describe()!r}"

            def test_prefix_tool_stores_name_and_prefix():
                p = PrefixTool("tag", ">> ")
                assert (p.name, p.prefix) == ("tag", ">> ")

            def test_prefix_tool_run_and_describe():
                p = PrefixTool("tag", ">> ")
                assert p.run("hello") == ">> hello", f"run -> {p.run('hello')!r}"
                assert p.describe() == "tool tag"

            def test_both_inherit_and_reuse_describe():
                assert issubclass(UpperTool, Tool) and issubclass(PrefixTool, Tool), "inherit from Tool"
                for cls in (UpperTool, PrefixTool):
                    assert "describe" not in vars(cls), f"{cls.__name__} redefines describe"

            def test_prefix_tool_calls_super():
                import ast
                tree = ast.parse(source())
                cls = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "PrefixTool"][0]
                assert any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "super"
                           for n in ast.walk(cls)), "PrefixTool.__init__ should call super().__init__"
        ''',
        "solution": r'''
            class Tool:
                def __init__(self, name):
                    self.name = name

                def describe(self):
                    return f"tool {self.name}"

                def run(self, text):
                    raise NotImplementedError("subclasses must implement run()")


            class UpperTool(Tool):
                def run(self, text):
                    return text.upper()


            class PrefixTool(Tool):
                def __init__(self, name, prefix):
                    super().__init__(name)
                    self.prefix = prefix

                def run(self, text):
                    return self.prefix + text
        ''',
        "hints": [
            "Put the parent class in brackets after the subclass name: `class UpperTool(Tool):`.",
            "`UpperTool` only needs its own `run`. `PrefixTool` needs an `__init__` that lets the parent store the name, then stores the prefix itself, plus its own `run`.",
            "1) `class UpperTool(Tool):` with `run` returning `text.upper()`. 2) `class PrefixTool(Tool):` with `__init__(self, name, prefix)` calling `super().__init__(name)` then setting `self.prefix`. 3) Its `run` returns `self.prefix + text`.",
        ],
    },
    {
        "id": "classes-3",
        "title": "Conversation",
        "hints": [
            "Keep the messages in a list created in `__init__`. `len(obj)` and `str(obj)` call the special methods `__len__` and `__str__`.",
            "`add` checks the role against the three allowed ones before appending a dict. `__init__` can reuse `add` for the system message. `last` looks at the end of the list.",
            "1) `__init__`: `self.messages = []`; if `system` is not None, call `self.add(\"system\", system)`. 2) `add`: raise `ValueError` for an unknown role, else append the dict. 3) `__len__`: length of the list. 4) `last`: the last item, or None when empty. 5) `__str__`: join `role: content` lines with a newline.",
        ],
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            A conversation object that keeps the message history you would send to a chat
            model. Each message is a dict like `{"role": "user", "content": "Hi"}`.

            **Write:** the class `Conversation`

            - `Conversation(system=None)`: `system` is an optional string like
              `"Be brief."`. If it is given, the conversation starts with the message
              `{"role": "system", "content": <system>}`; otherwise it starts empty.
            - `messages` (attribute): the list of message dicts, oldest first.
            - `add(role, content)`: appends `{"role": role, "content": content}` to
              `messages`. **Returns:** nothing.
            - `len(conv)` (special method `__len__`): **Returns** the number of messages (an int).
            - `last()`: **Returns** the last message dict, or `None` if there are no messages.
            - `str(conv)` (special method `__str__`): **Returns** one line per message in
              the form `role: content`, lines joined with `"\n"` (no newline at the end).

            **Rules**
            - `role` must be `"system"`, `"user"` or `"assistant"`. Any other role raises
              `ValueError`, and the message is **not** added.
            - Every conversation has its own message list (adding to one does not change another).

            **Examples**
            ```python
            c = Conversation(system="Be brief.")
            c.add("user", "Hi")
            c.messages   # [{"role": "system", "content": "Be brief."}, {"role": "user", "content": "Hi"}]
            len(c)       # 2
            c.last()     # {"role": "user", "content": "Hi"}
            str(c)       # "system: Be brief.\nuser: Hi"

            empty = Conversation()
            len(empty)       # 0
            empty.last()     # None
            empty.add("tool", "x")   # raises ValueError; len(empty) is still 0
            ```
        ''',
        "starter": r'''
            class Conversation:
                ...
        ''',
        "tests": r'''
            from solution import Conversation

            def test_system_message_comes_first_in_messages():
                c = Conversation(system="Be brief.")
                c.add("user", "Hi")
                assert c.messages == [{"role": "system", "content": "Be brief."},
                                      {"role": "user", "content": "Hi"}], f"messages: {c.messages!r}"

            def test_len_and_last_including_empty_conversation():
                c = Conversation()
                assert len(c) == 0 and c.last() is None
                c.add("user", "Hi")
                c.add("assistant", "Hello")
                assert len(c) == 2, f"len is {len(c)}"
                assert c.last() == {"role": "assistant", "content": "Hello"}, f"last() -> {c.last()!r}"

            def test_invalid_role_raises_value_error_and_is_not_added():
                c = Conversation()
                try:
                    c.add("tool", "x")
                except ValueError:
                    pass
                else:
                    raise AssertionError("no ValueError for role 'tool'")
                assert len(c) == 0, "an invalid message was still added"

            def test_str_is_role_colon_content_lines():
                c = Conversation(system="Be brief.")
                c.add("user", "Hi")
                assert str(c) == "system: Be brief.\nuser: Hi", f"str -> {str(c)!r}"

            def test_instances_do_not_share_messages():
                a, b = Conversation(), Conversation()
                a.add("user", "only in a")
                assert len(b) == 0, "two conversations share the same message list"
        ''',
        "solution": r'''
            ROLES = {"system", "user", "assistant"}


            class Conversation:
                def __init__(self, system=None):
                    self.messages = []
                    if system is not None:
                        self.add("system", system)

                def add(self, role, content):
                    if role not in ROLES:
                        raise ValueError(f"invalid role: {role!r}")
                    self.messages.append({"role": role, "content": content})

                def last(self):
                    return self.messages[-1] if self.messages else None

                def __len__(self):
                    return len(self.messages)

                def __str__(self):
                    return "\n".join(f"{m['role']}: {m['content']}" for m in self.messages)
        ''',
    },
    {
        "id": "classes-4",
        "title": "Validated model config",
        "hints": [
            "Use `@property` for the getter and `@temperature.setter` for the setter, and keep the real value in a 'private' attribute such as `self._temperature`.",
            "The setter checks the type first (reject bools explicitly: `True` counts as an int), then the range, and only stores the value when both checks pass. Assigning `self.temperature` in `__init__` goes through the setter too.",
            "1) `__init__` stores `model` and assigns `self.temperature`. 2) Setter: bool or not int/float -> `TypeError`; outside 0.0..2.0 -> `ValueError`; else store in `self._temperature`. 3) `__eq__`: non-ModelConfig -> `NotImplemented`, else compare `(model, temperature)` tuples. 4) `__repr__` with `!r` on the model.",
        ],
        "difficulty": 2,
        "prompt": r'''
            A model config that refuses bad temperature values, so a typo can't reach the API.

            **Write:** the class `ModelConfig`

            - `ModelConfig(model, temperature=0.7)`: `model` is a string like `"gpt-4o"`,
              stored as the attribute `model`. `temperature` is a number, default `0.7`.
            - `temperature`: must be a **property** (use `@property` plus a setter), so
              every assignment is checked: in `__init__` and later (`cfg.temperature = 1.5`).
            - `==` (special method `__eq__`): two configs are equal when both `model` and
              `temperature` are equal.
            - `repr(cfg)` (special method `__repr__`): **Returns** a string like
              `ModelConfig('gpt-4o', temperature=0.7)`.

            **Rules**
            - A value that is not an `int` or `float` raises `TypeError`. `True`/`False`
              count as not allowed (raise `TypeError`), and so does a string like `"0.5"`.
            - A number below `0.0` or above `2.0` raises `ValueError`. `0`, `0.0` and
              `2.0` themselves are allowed.
            - The constructor checks too: `ModelConfig("x", 5.0)` raises `ValueError`.
            - A rejected assignment leaves the old value in place.
            - Comparing with something that is not a `ModelConfig` gives `False`
              (no error): `ModelConfig("a") == "a"` is `False`.
            - In the `repr`, the model is shown with quotes (its `repr`).

            **Examples**
            ```python
            cfg = ModelConfig("gpt-4o", 0.3)
            cfg.temperature          # 0.3
            cfg.temperature = 3      # raises ValueError
            cfg.temperature          # still 0.3
            cfg.temperature = True   # raises TypeError
            cfg.temperature = 2.0    # ok
            ModelConfig("gpt-4o").temperature                 # 0.7
            ModelConfig("a", 0.2) == ModelConfig("a", 0.2)    # True
            ModelConfig("a", 0.2) == ModelConfig("b", 0.2)    # False
            repr(ModelConfig("gpt-4o", 0.7))                  # "ModelConfig('gpt-4o', temperature=0.7)"
            ```
        ''',
        "starter": r'''
            class ModelConfig:
                ...
        ''',
        "tests": r'''
            from solution import ModelConfig

            def _raises(exc, fn):
                try:
                    fn()
                except exc:
                    return True
                except Exception as e:
                    raise AssertionError(f"expected {exc.__name__}, got {type(e).__name__}: {e}")
                return False

            def test_default_temperature_and_setting_a_valid_value():
                cfg = ModelConfig("gpt-4o")
                assert cfg.model == "gpt-4o" and cfg.temperature == 0.7
                cfg.temperature = 1.5
                assert cfg.temperature == 1.5

            def test_out_of_range_raises_value_error_and_keeps_old_value():
                cfg = ModelConfig("gpt-4o", 0.3)
                assert _raises(ValueError, lambda: setattr(cfg, "temperature", 3)), "3 was accepted"
                assert _raises(ValueError, lambda: setattr(cfg, "temperature", -0.1)), "-0.1 was accepted"
                assert cfg.temperature == 0.3, f"temperature is now {cfg.temperature!r}"
                cfg.temperature = 2.0
                cfg.temperature = 0

            def test_constructor_also_validates_temperature():
                assert _raises(ValueError, lambda: ModelConfig("x", 5.0)), "ModelConfig('x', 5.0) was accepted"

            def test_string_or_bool_raises_type_error():
                cfg = ModelConfig("x")
                assert _raises(TypeError, lambda: setattr(cfg, "temperature", "0.5")), "a string was accepted"
                assert _raises(TypeError, lambda: setattr(cfg, "temperature", True)), "a bool was accepted"

            def test_temperature_is_a_property():
                assert isinstance(vars(ModelConfig).get("temperature"), property), "temperature must be a property"

            def test_equality_and_repr_format():
                assert ModelConfig("a", 0.2) == ModelConfig("a", 0.2)
                assert ModelConfig("a", 0.2) != ModelConfig("a", 0.3)
                assert ModelConfig("a", 0.2) != ModelConfig("b", 0.2)
                assert (ModelConfig("a") == "a") is False
                got = repr(ModelConfig("gpt-4o", 0.7))
                assert got == "ModelConfig('gpt-4o', temperature=0.7)", f"repr -> {got!r}"
        ''',
        "solution": r'''
            class ModelConfig:
                def __init__(self, model, temperature=0.7):
                    self.model = model
                    self.temperature = temperature

                @property
                def temperature(self):
                    return self._temperature

                @temperature.setter
                def temperature(self, value):
                    if isinstance(value, bool) or not isinstance(value, (int, float)):
                        raise TypeError(f"temperature must be a number, got {type(value).__name__}")
                    if not 0.0 <= value <= 2.0:
                        raise ValueError(f"temperature must be between 0 and 2, got {value}")
                    self._temperature = value

                def __eq__(self, other):
                    if not isinstance(other, ModelConfig):
                        return NotImplemented
                    return (self.model, self.temperature) == (other.model, other.temperature)

                def __repr__(self):
                    return f"ModelConfig({self.model!r}, temperature={self.temperature!r})"
        ''',
    },
    {
        "id": "classes-5",
        "title": "Provider polymorphism",
        "hints": [
            "This is inheritance: the subclasses reuse `ask` from the base class and only replace `complete`.",
            "The base `ask` calls `self.complete(prompt)`, so whichever subclass `self` is, its own `complete` runs. `CannedProvider` needs an extra `reply`, so its `__init__` first hands `model` to the parent's `__init__`.",
            "1) `LLMProvider`: `name = \"base\"`, `__init__` stores model, `complete` raises `NotImplementedError`, `ask` formats `[name/model] ` plus `self.complete(prompt)`. 2) `EchoProvider(LLMProvider)`: its name, `complete` returns the prompt. 3) `CannedProvider`: `super().__init__(model)`, store reply, `complete` returns it. 4) `ask_all`: list of each provider's `ask(prompt)`.",
        ],
        "difficulty": 3,
        "prompt": r'''
            Apps often support several LLM providers behind one shared interface. Build a
            small class hierarchy for that (this is *inheritance*; calling the same method
            on different classes is *polymorphism*).

            **Write:** the classes `LLMProvider`, `EchoProvider`, `CannedProvider` and the
            function `ask_all(providers, prompt)`

            **`LLMProvider`** (the base class)
            - class attribute `name = "base"`
            - `LLMProvider(model)`: `model` is a string like `"e1"`, stored as the attribute `model`
            - `complete(prompt)`: raises `NotImplementedError` (subclasses replace it)
            - `ask(prompt)`: **Returns** the string `"[<name>/<model>] <completion>"`, where
              `<completion>` is what `self.complete(prompt)` returns

            **`EchoProvider`**, a subclass of `LLMProvider`
            - class attribute `name = "echo"`
            - `complete(prompt)` returns the prompt unchanged

            **`CannedProvider`**, a subclass of `LLMProvider`
            - class attribute `name = "canned"`
            - `CannedProvider(model, reply)`: stores `model` (via `super().__init__`) and
              `reply` (a string) as attributes
            - `complete(prompt)` returns `reply`, whatever the prompt

            **`ask_all(providers, prompt)`**
            - `providers`: a list of provider objects (any subclass of `LLMProvider`)
            - **Returns:** a list with each provider's `ask(prompt)` result, in the same order

            **Rules**
            - `EchoProvider` and `CannedProvider` must inherit from `LLMProvider`.
            - The subclasses must **not** define their own `ask`; they only define `complete`.
            - `CannedProvider.__init__` must call `super().__init__(...)`.
            - `ask_all` must work with any other subclass too (one that defines its own
              `name` and `complete`).

            **Examples**
            ```python
            EchoProvider("e1").ask("hi")                # "[echo/e1] hi"
            p = CannedProvider("c1", "42")
            p.model, p.reply                            # ("c1", "42")
            p.ask("meaning?")                           # "[canned/c1] 42"
            LLMProvider("x").ask("hi")                  # raises NotImplementedError
            ask_all([EchoProvider("e"), CannedProvider("c", "ok")], "yo")
            # ["[echo/e] yo", "[canned/c] ok"]
            ```
        ''',
        "starter": r'''
            class LLMProvider:
                ...


            class EchoProvider:
                ...


            class CannedProvider:
                ...


            def ask_all(providers, prompt):
                ...
        ''',
        "tests": r'''
            from solution import LLMProvider, EchoProvider, CannedProvider, ask_all

            def test_echo_provider_ask_returns_prompt():
                got = EchoProvider("e1").ask("hi")
                assert got == "[echo/e1] hi", f"got {got!r}"

            def test_canned_provider_stores_reply_and_returns_it():
                p = CannedProvider("c1", "42")
                assert p.model == "c1" and p.reply == "42"
                got = p.ask("meaning of life?")
                assert got == "[canned/c1] 42", f"got {got!r}"

            def test_base_raises_not_implemented():
                try:
                    LLMProvider("x").ask("hi")
                except NotImplementedError:
                    pass
                else:
                    raise AssertionError("the base class should raise NotImplementedError")

            def test_subclasses_inherit_and_do_not_override_ask():
                assert issubclass(EchoProvider, LLMProvider) and issubclass(CannedProvider, LLMProvider)
                assert LLMProvider.name == "base"
                for cls in (EchoProvider, CannedProvider):
                    assert "ask" not in vars(cls), f"{cls.__name__} overrides ask; implement complete instead"

            def test_canned_provider_init_calls_super():
                import ast
                src = source()
                tree = ast.parse(src)
                cls = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "CannedProvider"][0]
                uses = any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "super"
                           for n in ast.walk(cls))
                assert uses, "CannedProvider.__init__ should call super().__init__"

            def test_ask_all_works_with_any_provider_subclass():
                class Shout(LLMProvider):
                    name = "shout"
                    def complete(self, prompt):
                        return prompt.upper()
                got = ask_all([EchoProvider("e"), CannedProvider("c", "ok"), Shout("s")], "yo")
                assert got == ["[echo/e] yo", "[canned/c] ok", "[shout/s] YO"], f"got {got!r}"
        ''',
        "solution": r'''
            class LLMProvider:
                name = "base"

                def __init__(self, model):
                    self.model = model

                def complete(self, prompt):
                    raise NotImplementedError(f"{type(self).__name__} must implement complete()")

                def ask(self, prompt):
                    return f"[{self.name}/{self.model}] {self.complete(prompt)}"


            class EchoProvider(LLMProvider):
                name = "echo"

                def complete(self, prompt):
                    return prompt


            class CannedProvider(LLMProvider):
                name = "canned"

                def __init__(self, model, reply):
                    super().__init__(model)
                    self.reply = reply

                def complete(self, prompt):
                    return self.reply


            def ask_all(providers, prompt):
                return [p.ask(prompt) for p in providers]
        ''',
    },
    {
        "id": "classes-6",
        "title": "Trimmed conversation",
        "hints": [
            "Override both `__init__` and `add` in the subclass, and use `super()` to call the parent's versions instead of copying their code.",
            "Set up your own attributes (`max_messages`, `dropped`) BEFORE calling `super().__init__`, because the parent may call `self.add` for the system message. After `super().add(...)`, while there are too many non-system messages, delete the first non-system one.",
            "1) `__init__`: raise `ValueError` if `max_messages < 1`, store it, `self.dropped = 0`, then `super().__init__(system=system)`. 2) `add`: `super().add(role, content)` (keeps the role check). 3) While the count of non-system messages is above the max: find the index of the first non-system message, `del` it, add 1 to `dropped`.",
        ],
        "difficulty": 3,
        "prompt": r'''
            A model can only read a limited amount of text at once (its *context window*), so long
            chats must forget old messages.
            The starter contains a working `Conversation` class. Do not change it.

            **Write:** a subclass `TrimmedConversation` of `Conversation` that caps the history

            - `TrimmedConversation(max_messages, system=None)`: `max_messages` is an int
              like `2`, the most **non-system** messages to keep. `system` works exactly
              as in `Conversation`.
            - `add(role, content)`: adds the message like the parent does, then trims.
            - `dropped` (attribute): an int, how many messages have been dropped so far
              (starts at `0`).
            - `messages` and `len(...)` still work as inherited.

            **Rules**
            - If `max_messages` is less than `1`, raise `ValueError`.
            - After an add, if there are more than `max_messages` non-system messages,
              remove the **oldest non-system** message(s) until there are exactly
              `max_messages`. Each removed message adds 1 to `dropped`.
            - System messages are never dropped, never counted, and stay in their place.
            - Invalid roles must still raise `ValueError` (reuse the parent's `add`).
            - Use `super()` to reuse the parent's `__init__` and `add`.
            - `TrimmedConversation` objects are also `Conversation` objects.

            **Examples**
            ```python
            c = TrimmedConversation(2, system="Be brief.")
            c.add("user", "1"); c.add("assistant", "2"); c.add("user", "3")
            [m["content"] for m in c.messages]   # ["Be brief.", "2", "3"]
            c.dropped                             # 1

            c = TrimmedConversation(2, system="S1")
            c.add("user", "a"); c.add("system", "S2"); c.add("user", "b"); c.add("assistant", "c")
            [m["content"] for m in c.messages]   # ["S1", "S2", "b", "c"]

            TrimmedConversation(3).dropped        # 0
            TrimmedConversation(0)                # raises ValueError
            ```
        ''',
        "starter": r'''
            class Conversation:
                ROLES = ("system", "user", "assistant")

                def __init__(self, system=None):
                    self.messages = []
                    if system is not None:
                        self.add("system", system)

                def add(self, role, content):
                    if role not in self.ROLES:
                        raise ValueError(f"invalid role: {role!r}")
                    self.messages.append({"role": role, "content": content})

                def __len__(self):
                    return len(self.messages)


            class TrimmedConversation(Conversation):
                ...
        ''',
        "tests": r'''
            from solution import Conversation, TrimmedConversation

            def contents(c):
                return [m["content"] for m in c.messages]

            def test_trims_oldest_non_system_message_and_counts_dropped():
                c = TrimmedConversation(2, system="Be brief.")
                c.add("user", "1"); c.add("assistant", "2"); c.add("user", "3")
                assert contents(c) == ["Be brief.", "2", "3"], f"messages: {contents(c)!r}"
                assert c.dropped == 1, f"dropped = {getattr(c, 'dropped', None)!r}"

            def test_is_a_conversation_starting_with_zero_dropped():
                c = TrimmedConversation(3)
                assert isinstance(c, Conversation)
                assert len(c) == 0 and c.dropped == 0

            def test_max_one_keeps_only_the_latest_message():
                c = TrimmedConversation(1)
                for i in range(5):
                    c.add("user", str(i))
                assert contents(c) == ["4"], f"messages: {contents(c)!r}"
                assert c.dropped == 4

            def test_system_messages_never_dropped_or_counted():
                c = TrimmedConversation(2, system="S1")
                c.add("user", "a"); c.add("system", "S2"); c.add("user", "b"); c.add("assistant", "c")
                assert contents(c) == ["S1", "S2", "b", "c"], f"messages: {contents(c)!r}"

            def test_max_below_one_and_invalid_role_raise_value_error():
                try:
                    TrimmedConversation(0)
                except ValueError:
                    pass
                else:
                    raise AssertionError("max_messages=0 was accepted")
                c = TrimmedConversation(2)
                try:
                    c.add("robot", "x")
                except ValueError:
                    pass
                else:
                    raise AssertionError("invalid role accepted - reuse the parent's add()")

            def test_uses_super_to_reuse_parent():
                assert "super()" in source(), "use super() to reuse the parent class"
        ''',
        "solution": r'''
            class Conversation:
                ROLES = ("system", "user", "assistant")

                def __init__(self, system=None):
                    self.messages = []
                    if system is not None:
                        self.add("system", system)

                def add(self, role, content):
                    if role not in self.ROLES:
                        raise ValueError(f"invalid role: {role!r}")
                    self.messages.append({"role": role, "content": content})

                def __len__(self):
                    return len(self.messages)


            class TrimmedConversation(Conversation):
                def __init__(self, max_messages, system=None):
                    if max_messages < 1:
                        raise ValueError("max_messages must be at least 1")
                    self.max_messages = max_messages
                    self.dropped = 0
                    super().__init__(system=system)

                def add(self, role, content):
                    super().add(role, content)
                    while self._count_non_system() > self.max_messages:
                        for i, m in enumerate(self.messages):
                            if m["role"] != "system":
                                del self.messages[i]
                                self.dropped += 1
                                break

                def _count_non_system(self):
                    return len([m for m in self.messages if m["role"] != "system"])
        ''',
    },
]
