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
            ## A value that carries its own data

            A chat has a model name and a count of the turns so far. You could pass both values separately to each function. With several chats, loose variables make it hard to keep each count with its chat.

            Python lets you describe once what a chat is, and then build as many chats as you need. Each
            one carries its own data:

            ```python
            class Chat:
                def __init__(self, model):
                    self.model = model
                    self.turns = 0

            a = Chat("gpt")
            print(a.model)
            # gpt
            print(a.turns)
            # 0
            ```

            Take it one piece at a time.

            - `class Chat:` starts the description. You know that every value has a type, such as `str`
              or `list`. A **class** is a type that you write yourself.
            - `Chat("gpt")` builds one chat from the description. What you get back is called an
              **object**.
            - `__init__` has two underscores on each side. It is a function inside the class, and you
              never call it. Python calls it by itself each time an object is built, to give the new
              object its starting values.
            - `self` is the new object. `self.turns = 0` stores `0` on that object under the name
              `turns`. A value stored on an object is called an **attribute**, and you read it with a
              dot: `a.turns`.

            Click through the stages to see what Python does for the line `a = Chat("gpt")`:

            ```diagram
            {"type":"flow","title":"What Python does for a = Chat(\"gpt\")","steps":[{"label":"Build an empty object","detail":"Python builds a new Chat object. Nothing is stored on it yet.","code":"a new, empty Chat object"},{"label":"Call __init__","detail":"Python calls __init__ by itself. The new object goes in as self, and \"gpt\" goes in as model.","code":"self  = the new object\nmodel = \"gpt\""},{"label":"Store the values","detail":"The two lines in the body of __init__ run. Each one stores a value on the object.","code":"self.model = model   # \"gpt\"\nself.turns = 0"},{"label":"Hand the object back","detail":"__init__ is finished. Chat(\"gpt\") hands the object back, and the name a now refers to it.","code":"a.model  ->  \"gpt\"\na.turns  ->  0"}]}
            ```

            An attribute behaves like a variable that lives on the object. You can read it, and you can
            give it a new value with `=`. A second chat gets attributes of its own:

            ```predict
            class Chat:
                def __init__(self, model):
                    self.model = model
                    self.turns = 0

            a = Chat("gpt")
            b = Chat("claude")
            a.turns = 5
            print(a.model, a.turns)
            print(b.model, b.turns)
            ---
            `__init__` ran twice, once for each object, so each chat has its own `model` and its own `turns`. The line `a.turns = 5` changes the attribute on `a` only. `b.turns` is still the `0` that `__init__` stored.
            ```

            ### Functions that belong to the class

            Since the Lists chapter you have called methods such as `tools.append("email")`: a function
            after a dot that works on the value in front of the dot. A function that you write inside a
            class is a method of your own objects, and you call it the same way.

            ```python
            class Chat:
                def __init__(self, model):
                    self.model = model
                    self.turns = 0
                def send(self):
                    self.turns += 1
            a = Chat("gpt")
            a.send()
            a.send()
            print(a.turns)
            # 2
            ```

            For `a.send()`, Python runs `send` with `self` set to `a`, the object in front of the dot.
            So `self.turns += 1` adds 1 to the `turns` of `a`, and of no other chat.

            ```quiz
            Two chats are built with `a = Chat("gpt")` and `b = Chat("claude")`. Then `a.send()` runs three times. What is `b.turns`?
            - [x] `0` :: Right. `send` ran with `self` set to `a` each time. `b` is a separate object, and its `turns` is still the `0` from `__init__`.
            - [ ] `3` :: `turns` is not one number shared by all chats. Each object has its own, and only `a` stood in front of the dot.
            - [ ] Reading it is an error :: `b` has a `turns` attribute from the moment it is built, because `__init__` stores one on every new object.
            ```

            **Watch out:** `__init__` needs two underscores on each side. Spelled `_init_` or `__int__`,
            it is an ordinary function that Python never calls by itself, and `Chat("gpt")` stops with
            `TypeError: Chat() takes no arguments`.

            **In short:** a class describes a kind of object, `__init__` gives every new object its own
            attributes, and a method works on the object in front of the dot.
        ''',
        "difficulty": 0,
        "mode": "predict",
        "prompt": r'''
            Read the program in the editor. Type exactly what it prints, one line for each `print`.
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
            `Counter()` is called twice, so `a` and `b` are two separate objects. `__init__` ran once for
            each of them and stored a `count` of 0 on it. `a.add()` runs `add` with `self` set to `a`, so
            `self.count += 1` adds 1 to the count of `a` only. `add` is called twice on `a` and once on
            `b`. The first `print` shows the count of `a`, which is 2. The second shows the count of `b`,
            which is 1.
        ''',
        "starter": "",
        "tests": "",
        "hints": [
            "Each `Counter()` builds a new object, and `__init__` stores a `count` on it. How many objects does this program build?",
            "In `a.add()`, the `self` inside `add` is `a`, the object in front of the dot. That call changes the count of `a` and leaves `b` alone.",
            "Both counts start at 0. Count how often `add` is called on `a`, and how often on `b`. Your first line is the count of `a` and your second line is the count of `b`.",
        ],
    },
    {
        "id": "classes-s2",
        "title": "Store the attributes",
        "lesson": r'''
            ## Making an object remember what you pass in

            In the last step you wrote `Chat("gpt")`, and afterwards `a.model` was `"gpt"`. How did the
            value get from the parentheses onto the object?

            It takes two moves. First, the values in the parentheses arrive in `__init__` as its
            parameters. `self` stands first in the `def` line, and Python fills it in with the new
            object. Your own values go to the parameters after `self`, in order.

            Second, `__init__` stores each value on the object:

            ```python
            class Model:
                def __init__(self, name, price):
                    self.name = name
                    self.price = price

            mini = Model("mini", 1)
            print(mini.name)
            # mini
            print(mini.price)
            # 1
            ```

            ```quiz
            In `Model("mini", 1)`, which parameter of `__init__` receives the `1`?
            - [x] `price` :: Right. Python fills `self` by itself, so `"mini"` goes to `name` and `1` goes to `price`.
            - [ ] `name` :: `name` receives the first value that you wrote, `"mini"`. The `1` is the second value.
            - [ ] `self` :: You never pass anything for `self`. Python fills it with the new object, and your own values start at the parameter after it.
            ```

            Read `self.name = name` from right to left. On the right is the parameter `name`, which
            holds `"mini"`. On the left is `self.name`, the attribute `name` on the new object. The line
            copies the value from the parameter onto the object.

            The two share a name out of habit, but they are different things. The parameter is a local
            variable, so it is gone as soon as `__init__` finishes. The attribute stays for as long as
            the object exists.

            ```try
            class Model:
                def __init__(self, name, price):
                    self.name = name

            big = Model("max", 15)
            print(big.name, big.price)
            ---
            This program stops with `AttributeError: 'Model' object has no attribute 'price'`. The price is passed in, but it is never stored. Add one line so that the program prints `max 15`.
            ---
            class Model:
                def __init__(self, name, price):
                    self.name = name
                    self.price = price

            big = Model("max", 15)
            print(big.name, big.price)
            ---
            The parameter `price` held 15 all along. It only became part of the object when a line stored it on `self`.
            ```

            An object built from a class is also called an **instance** of that class, and an attribute
            stored on one object is an **instance attribute**. Each instance keeps its own values:

            ```predict
            class Model:
                def __init__(self, name, price):
                    self.name = name
                    self.price = price

            mini = Model("mini", 1)
            big = Model("max", 15)
            print(mini.name, big.price)
            print(big.name, mini.price)
            ---
            Building `big` did not touch `mini`. Each instance has its own `name` and its own `price`, so the first line prints `mini 15` and the second prints `max 1`.
            ```

            **Watch out:** `name = name`, without `self.`, runs without any complaint and stores nothing.
            It assigns the parameter to itself. The error comes later, on the line that reads the
            attribute: `AttributeError: 'Model' object has no attribute 'name'`.

            **In short:** `self.name = name` in `__init__` copies a value that was passed in onto the
            object, where it stays.
        ''',
        "difficulty": 0,
        "prompt": r'''
            A chat message has two parts: who is speaking, and what they say. A `Message` object should
            keep both, so that the rest of a program can read them later as `m.role` and `m.content`.

            **Your job:** finish the `__init__` of the class `Message`. The class is already in the
            editor, with two gaps marked `___`. Replace each gap so that a new message remembers the two
            values it was given.

            **What goes in**
            - `role`: who is speaking, a string such as `"user"`
            - `content`: the text of the message, a string such as `"Hi"`

            **What comes out**
            - `Message(role, content)` builds an object with two attributes: `role` holds the role, and
              `content` holds the text

            **Rules**
            - Every message keeps its own values. Building a second message does not change the first.

            **Examples**
            ```python
            m = Message("user", "Hi")
            m.role                           # "user"
            m.content                        # "Hi"
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
            "Look at the first example in the lesson. What stands on the right-hand side of each line inside `__init__`?",
            "The values that you pass to `Message(...)` arrive as the parameters of `__init__`. Each gap needs the parameter whose value belongs in the attribute on that line.",
            "Go line by line. The first line fills the attribute for the role, so its gap is the parameter that received the role. The second line does the same for the text of the message.",
        ],
    },
    {
        "id": "classes-s3",
        "title": "Fix the bug: missing self",
        "lesson": r'''
            ## Why every method starts with self

            `a.send()` has nothing between its parentheses. Yet the code inside `send` knew which chat to
            change. How?

            Python passes the object in front of the dot to the method, by itself, as the first
            argument. Both calls below do exactly the same thing:

            ```python
            class Note:
                def __init__(self, text):
                    self.text = text

                def describe(self):
                    return "Note: " + self.text

            n = Note("buy milk")
            print(n.describe())
            # Note: buy milk
            print(Note.describe(n))
            # Note: buy milk
            ```

            `n.describe()` is the short form that everybody writes. Python turns it into the long form:
            find `describe` in the class `Note`, and call it with `n` as the first argument. The first
            parameter in the `def` line receives that object. Calling it `self` is a habit that every
            Python programmer follows.

            ```predict
            class Note:
                def __init__(self, text):
                    self.text = text

                def describe(self):
                    return "Note: " + self.text

            a = Note("buy milk")
            b = Note("call Sam")
            print(b.describe())
            print(Note.describe(a))
            ---
            In `b.describe()`, the object in front of the dot is `b`, so `self.text` is `"call Sam"`. In the long form, `a` is passed in by hand, so `self.text` is `"buy milk"`.
            ```

            So every method needs that first parameter, even a method that takes nothing else. This
            class has a method without it. The program catches the error and prints its message:

            ```python
            class Greeter:
                def hello():
                    return "hello"

            g = Greeter()
            try:
                g.hello()
            except TypeError as e:
                print(e)
            # Greeter.hello() takes 0 positional arguments but 1 was given
            ```

            Positional arguments are the values that a call passes in, in order. `hello` accepts 0 of
            them, because its parentheses in the `def` line are empty.

            ```quiz
            The call `g.hello()` has empty parentheses. What is the `1` in "but 1 was given"?
            - [x] `g`, the object in front of the dot :: Right. Python passes it by itself on every method call, and `hello` has no parameter to receive it.
            - [ ] The string `"hello"` :: That is what the method would hand back. It is never passed in.
            - [ ] A mistake in the count, because the call passes nothing :: The call looks empty, but Python always adds the object in front of the dot as the first argument.
            ```

            **Watch out:** the message points at the call, but the mistake is in the `def` line. When a
            method call "takes 0 positional arguments but 1 was given", or takes 1 when 2 were given,
            look for a missing `self`.

            **In short:** `obj.method()` passes `obj` in as the first argument, so the first parameter
            of every method is `self`.
        ''',
        "difficulty": 0,
        "prompt": r'''
            A `Prompt` object holds the text of a prompt. Its method `shout()` should give that text back
            in capital letters. Instead, `Prompt("hi").shout()` stops with
            `TypeError: Prompt.shout() takes 0 positional arguments but 1 was given`.

            **Your job:** find the one bug in the class `Prompt` and fix it. The code is already in the
            editor.

            **What goes in**
            - `Prompt(text)`: `text` is a string, for example `"hi"`. The class already stores it as the
              attribute `text`.
            - `shout()` is called with empty parentheses.

            **What comes out**
            - `shout()` gives back the text of its own object in upper case: `"HI"` for the example value

            **Rules**
            - Each prompt shouts its own text.
            - `shout()` does not change the attribute `text`. After the call, it still holds the original
              text.

            **Examples**
            ```python
            Prompt("hi").shout()               # returns "HI"
            Prompt("Summarize this").shout()   # returns "SUMMARIZE THIS"
            p = Prompt("abc")
            p.shout()                          # returns "ABC"
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
            "The message says that 1 argument was given, although the call has empty parentheses. The lesson explains what that one argument is.",
            "Python passes the object in front of the dot to every method, and the method needs a parameter to receive it. Compare the `def` line of `shout` with the `def` line of `__init__`.",
            "Only the `def` line of `shout` changes. Give it the first parameter that every method has. The body already uses that name, so leave the body as it is.",
        ],
    },
    {
        "id": "classes-s4",
        "title": "A method that counts words",
        "lesson": r'''
            ## Asking an object a question

            You have an object that holds some text, and you want to know how many characters are in it. With what you know so far, you would write a function that takes the text as a parameter, and then call it with the text of the object. That works, but the data and the code that works on it live in two places, and you have to carry the data over every time.

            A method keeps them together. You do not hand the text to anything. You ask the object:

            ```python
            class Chunk:
                def __init__(self, text):
                    self.text = text
                def char_count(self):
                    return len(self.text)
            a = Chunk("Summarize this")
            b = Chunk("Hi")
            print(a.char_count())
            # 14
            print(b.char_count())
            # 2
            ```

            `char_count` receives nothing from the call, yet it knows which text to measure. Remember that `self` is the object in front of the dot. Inside the method, `self.text` is the `text` attribute of that object. So `a.char_count()` measures the text of `a`, `b.char_count()` measures the text of `b`, and one method gives a different answer for each object.

            Fill the gap so that the method looks at the text of its own object:

            ```fill
            class Chunk:
                def __init__(self, text):
                    self.text = text

                def is_empty(self):
                    return len(___) == 0

            print(Chunk("").is_empty())
            ---
            - [x] self.text :: Right. The text of this object is the attribute `text`, and it is reached through `self`.
            - [ ] text :: `text` was only a parameter of `__init__`, and it is gone once `__init__` finishes. In this method Python stops with `NameError: name 'text' is not defined`.
            - [ ] self :: `self` is the whole object, not its text. `len(self)` stops with `TypeError: object of type 'Chunk' has no len()`.
            ```

            A method is a function, so everything you know about functions applies to it. It can use `if`, loops and string methods. And it has to `return` its answer, or the call gives back `None`.

            ```try
            class Note:
                def __init__(self, text):
                    self.text = text

                def length(self):
                    len(self.text)

            n = Note("buy milk")
            print(n.length())
            ---
            This program prints `None`, because `length` works out the number and then throws it away. Change the method so that the program prints `8`.
            ---
            class Note:
                def __init__(self, text):
                    self.text = text

                def length(self):
                    return len(self.text)

            n = Note("buy milk")
            print(n.length())
            ---
            A method that never reaches a `return` hands back `None`, exactly like a function does.
            ```

            **Watch out:** inside a method, write `self.text`, not `text`. The name `text` belongs to `__init__` and stopped existing when `__init__` finished, so the method stops with `NameError: name 'text' is not defined`.

            **In short:** a method reaches the data of its own object through `self`, and hands its answer back with `return`.
        ''',
        "difficulty": 0,
        "prompt": r'''
            A `Document` holds a title and some text, for example a page that an AI app is going to read. The app wants to know how long each document is, counted in words.

            **Your job:** finish the method `word_count` of the class `Document`. The class and its `__init__` are already in the editor, and the body of `word_count` is still a placeholder (`...`). Replace it so that the method gives back how many words are in the text of its own document.

            **What goes in**
            - `word_count()` takes no values. It works on the `text` attribute of the document it is called on, a string such as `"Summarize this page"`.

            **What comes out**
            - An int: the number of words in that text.

            **Rules**
            - Words are separated by whitespace: spaces, tabs or new lines.
            - Empty text has `0` words.
            - Each document counts its own text. Two documents with different texts give different numbers.

            **Examples**
            ```python
            Document("notes", "Summarize this page").word_count()   # returns 3
            Document("a", "one two\nthree").word_count()            # returns 3
            Document("empty", "").word_count()                      # returns 0
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
            "Look again at how `char_count` in the lesson gets at the text of its own object. You need that same text here.",
            "Get the separate words out of the text first, then count them. In the Strings chapter you met the string method that cuts a text at its whitespace and hands back a list of the words.",
            "In order: take the text of this document through `self`. Cut it into a list of words with that string method, called with empty parentheses. Count the items in that list with the built-in that counts items. Return that number.",
        ],
    },
    {
        "id": "classes-s5",
        "title": "A tiny chat",
        "lesson": r'''
            ## An object that remembers

            A chat grows over time. You send one message, then another, and the chat still knows the first. Where does it keep the first one in the meantime? Not in a variable inside a method, because those variables disappear when the method returns. The answer is an attribute: it belongs to the object, so it is still there when the next method call arrives.

            Here is a `History` that remembers whatever it is told:

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
            ```

            `__init__` runs once, when the object is built, and stores an empty list on it. Every call to `remember` then adds to that same list. The list survives between the calls because it lives on `self`, not inside the method. The values that an object holds at a given moment are its **state**. Methods are how the rest of the program changes that state.

            `remember` has no `return`, because its job is to change the object, not to hand something back. Try this one:

            ```predict
            class History:
                def __init__(self):
                    self.items = []

                def remember(self, thing):
                    self.items.append(thing)

            a = History()
            b = History()
            print(a.remember("x"))
            a.remember("y")
            b.remember("z")
            print(a.items)
            print(b.items)
            ---
            `remember` has no `return`, so the first `print` shows `None`. `a` and `b` were built separately, and `__init__` gave each of them a new empty list. `x` and `y` went into the list of `a`, and `z` went into the list of `b`.
            ```

            Where the list is created matters:

            ```quiz
            A programmer puts the line `self.items = []` at the top of `remember`, just before the `append`. After three calls to `remember`, what does `items` hold?
            - [x] Only the thing from the last call :: Right. Every call starts by replacing the list with a new empty one, so whatever was remembered before is thrown away.
            - [ ] All three things :: That would need the list to be created once. Here the line runs again on every call, so each call starts from a new empty list.
            - [ ] An empty list :: The `append` runs after the new list is created, so the latest thing is in it.
            ```

            **Watch out:** build the list in `__init__` and reach it as `self.items` everywhere. Writing `items = []` without `self.` makes an ordinary variable that is gone when `__init__` ends, and the next method that reads `self.items` stops with `AttributeError: 'History' object has no attribute 'items'`.

            **In short:** an object remembers through its attributes: create them in `__init__`, change them in methods, and each object keeps its own.
        ''',
        "difficulty": 0,
        "prompt": r'''
            A chat has to remember the messages that were sent to it, in order, so that a later step can send the whole history to a model. Here a message is just a piece of text, such as `"Hi"`.

            **Your job:** write the two methods of the class `Chat`. The class is in the editor with both bodies still empty (`...`). Make a new chat start with an empty history, and make `add` put a message at the end of it.

            **What goes in**
            - `Chat()`: no values.
            - `add(text)`: `text` is a string such as `"Hi"`.

            **What comes out**
            - `Chat()` gives an object with an attribute `messages` that holds an empty list.
            - `add` gives back nothing. It changes `messages` instead.

            **Rules**
            - A new chat has `messages` equal to `[]`.
            - Messages stay in the order they were added, with the newest at the end.
            - Every chat has its own list. Adding a message to one chat must not change another chat.

            **Examples**
            ```python
            c = Chat()
            c.messages       # []
            c.add("Hi")
            c.add("How are you?")
            c.messages       # ["Hi", "How are you?"]

            other = Chat()
            other.messages   # [] (the messages of c are not here)
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
            "Look at `History` in the lesson. Ask yourself where its list is created, and where it is changed.",
            "Create the empty list once, in `__init__`, and store it on the object under the name `messages`. In `add`, change that same list by putting the new text at its end.",
            "In `__init__`, assign an empty list to the attribute `messages` of `self`. In `add`, reach `messages` through `self` and call the list method that adds one item at the end, passing it `text`. Neither method needs a `return`.",
        ],
    },
    {
        "id": "classes-s6",
        "title": "Make len() and print() work",
        "lesson": r'''
            ## Make len() and print() work on your own objects

            Try the built-in `len()` on an object that you built yourself, and Python refuses:

            ```python
            class Batch:
                def __init__(self, items):
                    self.items = items

            b = Batch(["a", "b", "c"])
            try:
                len(b)
            except TypeError as e:
                print(e)
            # object of type 'Batch' has no len()
            ```

            Python cannot guess what the length of a `Batch` should mean. Is it the number of items, or the number of characters in all of them? You decide, and you tell Python by writing a method with a name that Python looks for. When your code runs `len(b)`, Python looks for a method called `__len__` on `b` and calls it:

            ```python
            class Batch:
                def __init__(self, items):
                    self.items = items

                def __len__(self):
                    return len(self.items)

            b = Batch(["a", "b", "c"])
            print(len(b))
            # 3
            ```

            The name has two underscores on each side, like `__init__`. A method with a name like this is a **special method**. Programmers also call it a **dunder** method, short for "double underscore". You write it, and Python calls it at the right moment. You never call it yourself: you write `len(b)`, not `b.__len__()`.

            ```fill
            class Playlist:
                def __init__(self, songs):
                    self.songs = songs

                def ___(self):
                    return len(self.songs)

            print(len(Playlist(["a", "b"])))
            ---
            - [x] __len__ :: Right. `len(playlist)` looks for a method with exactly this name.
            - [ ] len :: This is an ordinary method, and `len(playlist)` does not look for it. Python stops with `TypeError: object of type 'Playlist' has no len()`.
            - [ ] __length__ :: Python looks for one exact name, and this is not it. The call stops with `TypeError: object of type 'Playlist' has no len()`.
            ```

            `print` has the same problem. `print(b)` shows something like `<__main__.Batch object at 0x7f3a2c>`, the kind of object and a memory address, which tells you nothing. Before `print` shows an object, it turns it into text. For your own objects it looks for the special method `__str__`, which has to give the text back:

            ```python
            class Batch:
                def __init__(self, items):
                    self.items = items

                def __str__(self):
                    return f"Batch with {len(self.items)} items"

            b = Batch(["a", "b", "c"])
            print(b)
            # Batch with 3 items
            print(str(b))
            # Batch with 3 items
            ```

            ```match
            `len(b)` :: Python calls `__len__`
            `print(b)` :: Python calls `__str__`
            `Batch(["a"])` :: Python calls `__init__`
            ---
            Each of these three lines looks like an ordinary call, but behind each one Python looks for a method with a fixed name on your object.
            ```

            Now fix a `__str__` that shows the right text but does not give it back:

            ```try
            class Batch:
                def __init__(self, items):
                    self.items = items

                def __str__(self):
                    print(f"Batch of {len(self.items)}")

            b = Batch(["a", "b"])
            print(b)
            ---
            The text appears, but then the program stops with an error. Change the method so that `print(b)` shows `Batch of 2` and the program ends without an error.
            ---
            class Batch:
                def __init__(self, items):
                    self.items = items

                def __str__(self):
                    return f"Batch of {len(self.items)}"

            b = Batch(["a", "b"])
            print(b)
            ---
            `print` inside `__str__` shows the text and gives back `None`. `__str__` has to `return` the text, and then `print(b)` shows it.
            ```

            **Watch out:** `__str__` must return a string, not print one. A `__str__` that only prints gives back `None`, and Python stops with `TypeError: __str__ returned non-string (type NoneType)`.

            **In short:** write `__len__` so that `len(obj)` works and `__str__` so that `print(obj)` shows readable text, and make both of them return their answer.
        ''',
        "difficulty": 0,
        "prompt": r'''
            A `Snippet` holds a piece of text that you might paste into a prompt. You want the built-in `len()` and `print()` to understand it, so that `len(snippet)` gives its size and `print(snippet)` shows something readable instead of a memory address.

            **Your job:** finish the class `Snippet`. It is already in the editor, with two special methods whose answers are missing (`___`). Fill in both gaps so that `len()` and `str()` (and therefore `print()`) work on a snippet.

            **What goes in**
            - `Snippet(text)`: `text` is a string such as `"hello"`. The class already stores it as the attribute `text`.

            **What comes out**
            - `len(snippet)` gives an int: the number of characters in the text.
            - `str(snippet)` gives the string `"Snippet: "` followed by the text, and `print(snippet)` prints that same line.

            **Rules**
            - An empty snippet has length `0`, and `str` of it gives `"Snippet: "`.
            - The two methods give their answers back. They do not print them.

            **Examples**
            ```python
            s = Snippet("hello")
            len(s)             # returns 5
            str(s)             # returns "Snippet: hello"
            print(s)           # prints Snippet: hello
            len(Snippet(""))   # returns 0
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
            "Look at `Batch` in the lesson. What does each of its two special methods use to get at the data of the object?",
            "`__len__` gives back how many characters the text has. `__str__` builds a new string that begins with the label and continues with the text. Both give their answer back with `return`.",
            "First gap: the built-in that counts, applied to the text attribute of `self`. Second gap: an f-string that holds the label, a colon and a space, and then the text attribute of `self` inside curly braces.",
        ],
    },
    {
        "id": "classes-1",
        "title": "Message class",
        "lesson": r'''
            ## See what an object contains

            You print a list of objects while checking a chat history, but Python shows memory addresses instead of their contents. You need a useful description of each object so you can tell which data reached this part of your program.

            ```python
            class Label:
                def __init__(self, text):
                    self.text = text
                def __repr__(self):
                    return f"Label({self.text!r})"

            print([Label("ready"), Label("")])
            # [Label('ready'), Label('')]
            ```

            Python asks each object for its developer-facing description by calling `__repr__`. That description is called its **representation**. You return a string; Python decides when to display it. Lists and dictionaries use these representations for the objects inside them.

            The `!r` inside the braces asks for the value's own representation. For a string, that includes quotes and makes empty text visible. It also handles text containing quotation marks without you deciding which kind of quote to add.

            ```predict
            text = "it's ready"
            print(repr(text))
            print(repr(""))
            ---
            The first representation uses double quotes because the text contains an apostrophe. The second shows two single quotes, making the empty string visible.
            ```

            Remember the earlier `__str__` method? That is intended for a person using your app. `__repr__` is intended for someone inspecting its data. If you define only `__repr__`, Python also uses it when you print the object directly.

            ```quiz
            What must your `__repr__` method give back?
            - [x] A string describing the object :: Python can display that string wherever a representation is needed.
            - [ ] A call to print :: Printing has a side effect but does not supply the required string.
            - [ ] The object itself :: Python needs text, not another request to describe the same object.
            ```

            **Watch out:** returning a dictionary from `__repr__` raises `TypeError: __repr__ returned non-string`. Build text even when the object holds dictionary-shaped data.

            **In short:** `__repr__` supplies useful debugging text, and `!r` preserves the visible form of each value.
        ''',
        "hints": [
            "Revisit the difference between an object's stored data and its displayed representation.",
            "Each requested method has a separate job: remember values, export data, or describe it as text.",
            "Store the two inputs during construction. Build a fresh dictionary for export. Format the description with the values' own representations so quotes are handled correctly.",
        ],
        "difficulty": 1,
        "prompt": r'''
            A chat message object, the kind you send to an LLM API.

            **Your job:** write the class `Message`

            **What goes in**

            - `Message(role, content)`: `role` is a string like `"user"`, `content` is a
              string like `"hi"`. Store them as the attributes `role` and `content`.
            - `to_dict()`: **Gives back** a dict `{"role": <role>, "content": <content>}`.
            - `repr(msg)` (write the special method `__repr__`): **Gives back** a string like
              `Message(role='user', content='hi')`.

            **What comes out**
            - Each instance stores its own role and content. `to_dict()` gives back the two-field dictionary; `repr()` gives back the exact developer-facing description specified above.

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
            ## Share a setting without sharing a running total

            Several text processors should start with the same size limit, but each needs to remember its own name. Keeping the shared setting on the class lets you change that default once instead of updating every object separately.

            ```python
            class Reader:
                limit = 80
                def __init__(self, label):
                    self.label = label

            first = Reader("notes")
            second = Reader("email")
            Reader.limit = 40
            print(first.limit, second.limit)
            # 40 40
            ```

            The assignment directly inside the class creates a **class attribute**. It belongs to `Reader`, rather than to one reader. The assignment to `self.label` creates an instance attribute, as you learned earlier.

            When you read `first.limit`, Python looks on `first` first. If that object has no `limit` of its own, Python looks on its class. The same lookup works through `self.limit` inside a method. This is why changing the class setting affects later calculations.

            ```predict
            class Reader:
                limit = 80

            a = Reader()
            b = Reader()
            a.limit = 15
            print(a.limit, b.limit, Reader.limit)
            ---
            Assigning through a creates an attribute on that one object. It hides the class setting for a, while b still reads the class value of 80.
            ```

            Keep changing data, such as a running count, on each instance. Otherwise two independent jobs can accidentally share one list or total. A class setting is appropriate when all instances should read the same default.

            For rough size estimates, `math.ceil` rounds a division upward: an unfinished group still needs a whole slot.

            ```fill
            import math
            print(math.___(9 / 4))
            ---
            - [x] ceil :: Three slots are needed to hold nine items in groups of four.
            - [ ] floor :: Two rounds downward and leaves one item unaccounted for.
            ```

            **Watch out:** writing a fixed number inside a method ignores future changes to the setting. The code runs, but gives a stale estimate.

            **In short:** class attributes hold shared settings; instance attributes hold each object's changing data.
        ''',
        "hints": [
            "Which data should all counters share, and which data must belong to one counter?",
            "Keep the estimate ratio on the class and the running total on each object. An estimate for one call is different from the accumulated total.",
            "Set up the shared ratio and initial total. For add, divide the text length by the current ratio, round upward, update the total, and give back this call's estimate. Reset only the running total.",
        ],
        "difficulty": 1,
        "prompt": r'''
            A chat app wants an estimate of how much text each session has sent. This is a rough character-based estimate, not a model tokenizer.

            **Your job:** write `TokenCounter`, which remembers a running total and estimates each new piece of text.

            **What goes in**
            - `TokenCounter()` creates a counter with no arguments.
            - `add(text)` receives a string, such as `"hello world"`.
            - `reset()` receives no extra values.

            **What comes out**
            - `add` gives back the integer estimate for that one text.
            - The attribute `total` reports the accumulated estimates.

            **Rules**
            - The class attribute `chars_per_token` starts at `4` and is shared by counters.
            - Estimate tokens by dividing the character count by the current ratio and rounding upward to a whole number. The standard-library function `math.ceil` performs upward rounding.
            - Read the current ratio: changing `TokenCounter.chars_per_token` to `2` makes five characters count as three tokens.
            - Each instance starts with its own total of zero. Adding to one does not change another.
            - Empty text contributes zero. Reset makes the running total zero again.

            **Examples**
            ```python
            c = TokenCounter()
            c.add("hello world")  # returns 3
            c.add("hi")           # returns 1
            c.total               # 4
            c.add("")             # returns 0
            c.reset()
            c.total               # 0
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
            ## Decide when two records mean the same thing

            You load the same record twice. Python creates two objects, but you want to treat them as equal when their contents agree. Without your own comparison method, two separate objects of a plain class usually compare as different.

            ```python
            class Tag:
                def __init__(self, text):
                    self.text = text
                def __eq__(self, other):
                    return self.text == other.text if isinstance(other, Tag) else NotImplemented

            print(Tag("draft") == Tag("draft"))
            # True
            ```

            The `==` operation asks the special method `__eq__` to compare this object with the other value. Here, equality means equal text. You decide which attributes matter; two different records should not become equal merely because one attribute happens to match.

            The `isinstance` check answers whether the other value belongs to the expected class. Do that before reading its attributes, because an unrelated value may not have them.

            ```quiz
            A record has a file name and a version. Both determine its identity. Which comparison is sufficient?
            - [x] Both file name and version agree :: A change to either part describes a different record.
            - [ ] Only the file names agree :: This would treat two versions of a file as the same record.
            - [ ] The objects were created next to each other :: Creation order says nothing about their contents.
            ```

            Returning the special value `NotImplemented` says your method does not support that other type. Python can try the other value's comparison method. If neither supports equality, distinct objects compare as false. This is different from throwing an exception.

            ```match
            `==` :: asks whether values compare equal
            `is` :: asks whether names refer to the same object
            `NotImplemented` :: tells Python this comparison is unsupported
            ```

            **Watch out:** reading `other.text` before checking the type can raise `AttributeError`. Also, `NotImplementedError` is an exception, not the value used to decline a comparison.

            **In short:** define equality from the relevant attributes and handle unrelated types before accessing their data.
        ''',
        "difficulty": 1,
        "prompt": r'''
            Token-usage records from two runs should count as the same when they describe the
            same model and the same number of tokens.

            **Your job:** write the class `Usage`

            **What goes in**

            - `Usage(model, tokens)`: `model` is a string like `"gpt-4o"`, `tokens` an int
              like `120`. Store them as the attributes `model` and `tokens`.
            - `==` (special method `__eq__`): two `Usage` objects are equal when **both**
              `model` and `tokens` are equal.

            **What comes out**
            - A `Usage` record stores its own two inputs. Comparing records gives a Boolean based on both fields; unrelated types compare as unequal.

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
            "Review the special method Python uses for equality.",
            "Compare types before you compare attributes. Both fields matter for these records.",
            "If the other value is unsupported, give Python the special unsupported-comparison value. Otherwise test that both stored fields agree.",
        ],
    },
    {
        "id": "classes-8",
        "title": "Guarded max_tokens",
        "lesson": r'''
            ## Check a value whenever someone changes it

            A limit can be valid when an object is created and become invalid later. You want the same check to run both times, while callers still write an ordinary-looking assignment.

            ```python
            class Meter:
                @property
                def amount(self):
                    return self._amount
                @amount.setter
                def amount(self, value):
                    if value < 0:
                        raise ValueError("negative amount")
                    self._amount = value
            m = Meter()
            m.amount = 7
            print(m.amount)  # 7
            ```

            The read method and write method together make a **property**. Reading `m.amount` calls the first method, called the **getter**. Assigning to it calls the second, called the **setter**. The setter receives the proposed value and decides whether to store it.

            A line beginning with `@` changes how the following function is installed; this is a **decorator**. Here, `@property` creates the property and `@amount.setter` attaches its write method.

            ```quiz
            The meter currently holds 7. A caller assigns -2 and catches the ValueError. What should the meter hold afterwards?
            - [x] 7 :: The check raises before any assignment to the stored value happens.
            - [ ] -2 :: That would mean invalid data was stored before validation finished.
            - [ ] Nothing :: Raising an error does not erase an existing attribute.
            ```

            The underlying value lives in `_amount`. The leading underscore tells other programmers this is an internal detail. It does not enforce privacy. In a class with `__init__`, assigning through the public property in that method applies the same validation during construction.

            ```match
            getter :: runs when the property is read
            setter :: runs when the property is assigned
            internal attribute :: stores the value behind the property
            ```

            **Watch out:** assigning to the public property inside its own setter calls the setter again. Eventually Python raises `RecursionError`. Store the accepted value under the internal name instead.

            **In short:** a setter checks proposed values before replacing the stored value.
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

            **Your job:** write the class `Request`

            **What goes in**

            - `Request(prompt, max_tokens=256)`: `prompt` is a string, stored as the
              attribute `prompt`. `max_tokens` is an int, default `256`.
            - `max_tokens`: must be a **property** (`@property` plus a setter) so every
              assignment is checked: in `__init__` and later (`req.max_tokens = 50`).

            **What comes out**
            - A `Request` stores the prompt and exposes the accepted token limit through a property. Invalid writes raise while preserving the previous limit.

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
            "A constructor check alone cannot protect later assignments. Which feature intercepts writes?",
            "Let the public property validate the number and keep its accepted value in a separate internal attribute.",
            "Create the getter and setter. In the setter, reject values below the allowed boundary before storing anything. Have construction assign through that property too.",
        ],
    },
    {
        "id": "classes-9",
        "title": "Tools that inherit",
        "lesson": r'''
            ## Reuse a class and change one operation

            Several tools may need the same label and setup but do different work. Copying every method into each tool makes later fixes harder. You can start from an existing class and replace only the behavior that differs.

            ```python
            class Formatter:
                def format(self, text):
                    return text
                def show(self, text):
                    return "result: " + self.format(text)
            class QuietFormatter(Formatter):
                def format(self, text):
                    return text.lower()

            print(QuietFormatter().show("HELLO"))
            # result: hello
            ```

            `QuietFormatter(Formatter)` makes the new class inherit methods from the existing one. This is **inheritance**. The original class is the **base class**; the new one is a **subclass**. Defining `format` again **overrides** that method.

            Notice that the inherited `show` still calls the new `format`. Its `self` is a `QuietFormatter`, so method lookup begins with that object's class. One shared operation can therefore adapt to the actual kind of object. This is **polymorphism**.

            ```predict
            class Formatter:
                def format(self, text):
                    return text
            class QuietFormatter(Formatter):
                def format(self, text):
                    return text.lower()
            f = QuietFormatter()
            print(isinstance(f, Formatter))
            print(f.format("READY"))
            ---
            A subclass instance also belongs to its base class, so the first result is True. The subclass's replacement format method makes the second result ready.
            ```

            Sometimes a subclass needs extra setup. Inside its `__init__`, `super().__init__(...)` runs the base class's setup on the same object. You then store the additional fields. `super()` lets you reuse the original behavior without copying it.

            ```quiz
            The subclass does not define a method that the base class provides. What happens when you call it?
            - [x] Python uses the inherited method :: Missing methods are looked up on the base class.
            - [ ] Python always raises AttributeError :: Inheritance is precisely what makes the existing method available.
            - [ ] Python builds a separate base-class object :: The inherited method works on the original subclass object.
            ```

            **Watch out:** overriding `__init__` does not automatically run the base version. Missing its setup can cause an `AttributeError` when inherited methods read the absent attributes.

            **In short:** inherit shared behavior, override differences, and use `super()` when you need the original method too.
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

            **Your job:** write the subclasses `UpperTool` and `PrefixTool` (the base class `Tool` is
            in the starter: don't change it)

            **What goes in**

            **`UpperTool`**, a subclass of `Tool`
            - `run(text)`: **Gives back** `text` in upper case.

            **`PrefixTool`**, a subclass of `Tool`
            - `PrefixTool(name, prefix)`: stores `name` by calling the parent's `__init__`
              with `super()`, and stores `prefix` (a string) as the attribute `prefix`.
            - `run(text)`: **Gives back** `prefix + text`.

            **What comes out**
            - Instances expose the inherited description and each subclass's required text-processing result. The base `Tool` stays unchanged.

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
            "Which methods are shared, and which methods need a different result?",
            "The uppercase tool can reuse all the parent setup. The prefix tool needs additional data, so it extends the setup as well as the run behavior.",
            "Declare both subclasses with the given parent. Override their run methods. In the prefix tool's constructor, call the parent setup through super before storing the extra value. Leave describe inherited.",
        ],
    },
    {
        "id": "classes-3",
        "title": "Conversation",
        "hints": [
            "Think about the list that belongs to each conversation and the special methods for len and str.",
            "Validate a role before changing the history. Treat an empty history explicitly when looking for its last message.",
            "Start each instance with its own list and add an optional system message. Append accepted messages, report the list length, return the last item when present, and join display lines without a trailing newline.",
        ],
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            A conversation object that keeps the message history you would send to a chat
            model. Each message is a dict like `{"role": "user", "content": "Hi"}`.

            **Your job:** write the class `Conversation`

            **What goes in**

            - `Conversation(system=None)`: `system` is an optional string like
              `"Be brief."`. If it is given, the conversation starts with the message
              `{"role": "system", "content": <system>}`; otherwise it starts empty.
            - `messages` (attribute): the list of message dicts, oldest first.
            - `add(role, content)`: appends `{"role": role, "content": content}` to
              `messages`. **What comes out:** nothing.
            - `len(conv)` (special method `__len__`): **Gives back** the number of messages (an int).
            - `last()`: **Gives back** the last message dict, or `None` if there are no messages.
            - `str(conv)` (special method `__str__`): **Gives back** one line per message in
              the form `role: content`, lines joined with `"\n"` (no newline at the end).

            **What comes out**
            - A conversation exposes its ordered history. Its length, last-message lookup, and string display reflect that same history, including the empty cases.

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
            "Combine the property, equality, and representation ideas from this chapter.",
            "Check type before range. A Boolean needs explicit rejection because Python also treats it as an integer.",
            "Validate through the setter during construction and later writes, storing only accepted values. Compare both fields for compatible objects, and build the specified representation using quoted model text.",
        ],
        "difficulty": 2,
        "prompt": r'''
            A model config that refuses bad temperature values, so a typo can't reach the API.

            **Your job:** write the class `ModelConfig`

            **What goes in**

            - `ModelConfig(model, temperature=0.7)`: `model` is a string like `"gpt-4o"`,
              stored as the attribute `model`. `temperature` is a number, default `0.7`.
            - `temperature`: must be a **property** (use `@property` plus a setter), so
              every assignment is checked: in `__init__` and later (`cfg.temperature = 1.5`).
            - `==` (special method `__eq__`): two configs are equal when both `model` and
              `temperature` are equal.
            - `repr(cfg)` (special method `__repr__`): **Gives back** a string like
              `ModelConfig('gpt-4o', temperature=0.7)`.

            **What comes out**
            - A config stores a valid model and temperature, supports value equality, and provides the exact representation shown in the examples.

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
            "The shared ask method should be able to work with a subclass you have never seen.",
            "Let ask call the current object's completion method instead of checking which subclass it is.",
            "Put shared model storage and display formatting in the base. Give each subclass its own completion behavior and name; extend parent setup for the stored reply. Ask every provider in input order.",
        ],
        "difficulty": 3,
        "prompt": r'''
            Apps often support several LLM providers behind one shared interface. Build a
            small class hierarchy for that (this is *inheritance*; calling the same method
            on different classes is *polymorphism*).

            **Your job:** write the classes `LLMProvider`, `EchoProvider`, `CannedProvider` and the
            function `ask_all(providers, prompt)`

            **What goes in**

            **`LLMProvider`** (the base class)
            - class attribute `name` containing `"base"`
            - `LLMProvider(model)`: `model` is a string like `"e1"`, stored as the attribute `model`
            - `complete(prompt)`: raises `NotImplementedError` (subclasses replace it)
            - `ask(prompt)`: **Returns** the string `"[<name>/<model>] <completion>"`, where
              `<completion>` is what `self.complete(prompt)` returns

            **`EchoProvider`**, a subclass of `LLMProvider`
            - class attribute `name` containing `"echo"`
            - `complete(prompt)` returns the prompt unchanged

            **`CannedProvider`**, a subclass of `LLMProvider`
            - class attribute `name` containing `"canned"`
            - `CannedProvider(model, reply)`: stores `model` (via `super().__init__`) and
              `reply` (a string) as attributes
            - `complete(prompt)` returns `reply`, whatever the prompt

            **`ask_all(providers, prompt)`**
            - `providers`: a list of provider objects (any subclass of `LLMProvider`)
            - **Returns:** a list with each provider's `ask(prompt)` result, in the same order

            **What comes out**
            - Provider calls give back labelled completion strings. `ask_all` gives back one such string per provider, in the supplied order.

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
            "An inherited constructor may call a method that your subclass overrides. What must already exist when that happens?",
            "Initialize your trimming settings before running parent setup. Let the parent validate and append each message, then enforce your limit.",
            "Check the limit, prepare your attributes, and reuse parent construction. After each accepted addition, count only non-system entries and remove the oldest of those until within the limit, counting each removal.",
        ],
        "difficulty": 3,
        "prompt": r'''
            A model can only read a limited amount of text at once (its *context window*), so long
            chats must forget old messages.
            The starter contains a working `Conversation` class. Do not change it.

            **Your job:** write a subclass `TrimmedConversation` of `Conversation` that caps the history

            **What goes in**

            - `TrimmedConversation(max_messages, system=None)`: `max_messages` is an int
              like `2`, the most **non-system** messages to keep. `system` works exactly
              as in `Conversation`.
            - `add(role, content)`: adds the message like the parent does, then trims.
            - `dropped` (attribute): an int, how many messages have been dropped so far
              (starts at `0`).
            - `messages` and `len(...)` still work as inherited.

            **What comes out**
            - A conversation retains the allowed recent messages and all system messages. Its `dropped` attribute records how many non-system messages were removed.

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
