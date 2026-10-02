TOPIC = {
    "id": "sql",
    "title": "SQL & SQLite",
    "track": "apis-data",
    "order": 4,
    "requires": ["dicts", "errors"],
    "summary": """
        Storing and querying data with SQL using Python's built-in sqlite3: tables, safe
        parameters, filtering, sorting, aggregates, joins, transactions and pagination -
        applied to chat logs, token usage and documents.
    """,
    "concepts": ["tables and rows", "sqlite3.connect", "CREATE TABLE", "INSERT", "? parameters",
                 "SQL injection", "SELECT", "WHERE", "ORDER BY", "LIMIT", "OFFSET", "COUNT/SUM",
                 "GROUP BY", "JOIN", "LEFT JOIN", "transactions", "commit/rollback", "sqlite3.Row"],
}

# The Library card for this chapter (shown once the chapter's steps are done).
# Every line that starts with `#` in an example is the real output of that example.
REFERENCE = {
    "keywords": ["sql", "sqlite", "sqlite3", "database", "table", "row", "select", "insert",
                 "where", "order by", "group by", "join", "placeholder", "commit", "fetchall",
                 "sql injection"],
    "cards": [
        {
            "syntax": 'conn = sqlite3.connect(":memory:")',
            "explain": "Opens a database and returns a connection. conn.execute(sql) runs one statement. A file path stores the data on disk.",
            "example": r'''
                import sqlite3
                conn = sqlite3.connect(":memory:")
                conn.execute("CREATE TABLE notes (id INTEGER PRIMARY KEY, text TEXT)")
                conn.execute("INSERT INTO notes (text) VALUES ('hello')")
                print(conn.execute("SELECT id, text FROM notes").fetchall())
                # [(1, 'hello')]
            ''',
        },
        {
            "syntax": 'conn.execute("... VALUES (?, ?)", (a, b))',
            "explain": "Each ? takes one value from the tuple. The values are never read as SQL. One value needs a comma: (a,).",
            "example": r'''
                import sqlite3
                conn = sqlite3.connect(":memory:")
                conn.execute("CREATE TABLE msgs (role TEXT, content TEXT)")
                conn.execute("INSERT INTO msgs VALUES (?, ?)", ("user", "It's ok"))
                sql = "SELECT content FROM msgs WHERE role = ?"
                print(conn.execute(sql, ("user",)).fetchall())
                # [("It's ok",)]
            ''',
        },
        {
            "syntax": "SELECT cols FROM t WHERE cond ORDER BY col LIMIT n",
            "explain": "WHERE keeps the rows where the condition is true. ORDER BY sorts them (DESC: largest first). LIMIT keeps the first n.",
            "example": r'''
                import sqlite3
                conn = sqlite3.connect(":memory:")
                conn.execute("CREATE TABLE d (title TEXT, score REAL)")
                conn.execute("INSERT INTO d VALUES ('a', 0.2), ('b', 0.9), ('c', 0.5)")
                q = "SELECT title FROM d WHERE score > ? ORDER BY score DESC LIMIT 1"
                print(conn.execute(q, (0.3,)).fetchall())
                # [('b',)]
            ''',
        },
        {
            "syntax": "SELECT col, SUM(x) FROM t GROUP BY col",
            "explain": "Computes one value per group of rows with the same col. COUNT(*) counts rows. fetchone() returns one row or None.",
            "example": r'''
                import sqlite3
                conn = sqlite3.connect(":memory:")
                conn.execute("CREATE TABLE usage (model TEXT, tokens INTEGER)")
                conn.execute("INSERT INTO usage VALUES ('gpt', 100), ('gpt', 40)")
                sql = "SELECT model, COUNT(*), SUM(tokens) FROM usage GROUP BY model"
                print(conn.execute(sql).fetchone())
                # ('gpt', 2, 140)
            ''',
        },
        {
            "syntax": "FROM a LEFT JOIN b ON b.a_id = a.id",
            "explain": "LEFT JOIN keeps every row of a, also rows with no match in b (b's columns are NULL there). A plain JOIN drops them.",
            "example": r'''
                import sqlite3
                conn = sqlite3.connect(":memory:")
                conn.execute("CREATE TABLE chats (id INTEGER PRIMARY KEY, t TEXT)")
                conn.execute("CREATE TABLE msgs (chat_id INTEGER, x TEXT)")
                conn.execute("INSERT INTO chats (t) VALUES ('Trip')")
                q = "SELECT c.t, m.x FROM chats c LEFT JOIN msgs m ON m.chat_id = c.id"
                print(conn.execute(q).fetchall())
                # [('Trip', None)]
            ''',
        },
        {
            "syntax": "with conn:",
            "explain": "Runs the block as one transaction and commits when it finishes. If the block raises, the changes are rolled back (discarded).",
            "example": r'''
                import sqlite3
                conn = sqlite3.connect(":memory:")
                conn.execute("CREATE TABLE t (n INTEGER)")
                with conn:
                    conn.execute("INSERT INTO t VALUES (1)")
                    conn.execute("INSERT INTO t VALUES (2)")
                print(conn.execute("SELECT COUNT(*) FROM t").fetchone())
                # (2,)
            ''',
        },
    ],
}

LESSON = r'''
## Chapter notes: SQL with sqlite3

A **database** stores data in tables. A **table** has a name and a fixed set of columns. A
**column** has a name and a type. A **row** is one record: one value for each column.

**SQL** (Structured Query Language) is the language you write to create tables, add rows and
read rows. One SQL instruction is a **statement**. A statement that reads rows is a **query**.

**SQLite** is a database that stores every table in one file. Python includes the `sqlite3`
module, so you need no install and no server.

## Running a statement

`sqlite3.connect(path)` opens the database file and returns a **connection**: the object you
send statements through. The path `":memory:"` creates a temporary database in the
computer's memory (RAM) instead of a file. It is gone when the program ends.
`conn.execute(sql)` runs one statement. Inside SQL, a string is written in single quotes.
`execute` returns a **cursor**: an object that produces the rows the statement found.
`cur.lastrowid` is an attribute of the cursor. After an `INSERT`, it holds the primary
key number SQLite assigned to the new row.

A column declared `INTEGER PRIMARY KEY` is the **primary key**: a number that is different
for every row. SQLite assigns it when an `INSERT` does not give one.
Each `?` in the INSERT marks where one value goes. The values come in a tuple as the second
argument. "Parameters" below explains this.

```python
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE messages (id INTEGER PRIMARY KEY, role TEXT, content TEXT)")
cur = conn.execute("INSERT INTO messages (role, content) VALUES (?, ?)", ("user", "Hi"))
print(cur.lastrowid)
# 1
conn.commit()
rows = conn.execute("SELECT id, role, content FROM messages WHERE role = ?", ("user",)).fetchall()
print(rows)
# [(1, 'user', 'Hi')]
conn.close()
```

Step through the stages to see the code and the data at each point of that program.

```diagram
{"type":"flow","title":"One query with sqlite3, from connect to close","steps":[
{"label":"connect","detail":"sqlite3.connect opens the database and returns a connection object. The path \":memory:\" creates an empty database in RAM.","code":"conn = sqlite3.connect(\":memory:\")"},
{"label":"execute with ?","detail":"The SQL text contains one ? for each value. The values travel in a separate tuple. SQLite stores them as data and never reads them as SQL.","code":"conn.execute(\"INSERT INTO messages (role, content) VALUES (?, ?)\", (\"user\", \"Hi\"))\n\nmessages table now holds: (1, 'user', 'Hi')"},
{"label":"commit","detail":"The INSERT is pending until you commit. conn.commit() makes the change permanent and visible to other connections.","code":"conn.commit()"},
{"label":"execute SELECT","detail":"execute returns a cursor. The cursor produces the rows that match the WHERE condition.","code":"cur = conn.execute(\"SELECT id, role, content FROM messages WHERE role = ?\", (\"user\",))"},
{"label":"fetch rows","detail":"fetchall() returns a list with one tuple per row. Each tuple holds the selected columns in the order you listed them.","code":"rows = cur.fetchall()\n\nrows is [(1, 'user', 'Hi')]"},
{"label":"close","detail":"conn.close() releases the database file. Changes that were not committed are lost.","code":"conn.close()"}
]}
```

## Parameters

A `?` in the SQL text is a **placeholder**: a position where a value goes. You pass the values
as a tuple in the second argument of `execute`. These values are called **parameters**. A
single parameter still needs a tuple, so you write `("user",)` with the comma.

Never build SQL from user text with an f-string. The user can type SQL that changes what your
statement does. That attack is called **SQL injection**. A `?` only stands for a value. It
cannot stand for a table name or a column name, so check those names against a fixed list of
allowed names.

## Reading rows

`conn.execute` returns a **cursor**: an object that produces the result rows. `.fetchall()`
returns them as a list of tuples. `.fetchone()` returns the first row as one tuple, or `None`
when the query has no rows. `cur.lastrowid` is the id of the row an `INSERT` created.
The SQL value `NULL` (no value) arrives in Python as `None`.

```python
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE usage (model TEXT, tokens INTEGER)")
conn.execute("INSERT INTO usage VALUES ('gpt', 100)")
print(conn.execute("SELECT model, tokens FROM usage").fetchone())
# ('gpt', 100)
print(conn.execute("SELECT model FROM usage WHERE tokens > 500").fetchone())
# None
print(conn.execute("SELECT SUM(tokens) FROM usage WHERE tokens > 500").fetchone())
# (None,)
print(conn.execute("SELECT COALESCE(SUM(tokens), 0) FROM usage WHERE tokens > 500").fetchone())
# (0,)
```

No row has more than 500 tokens. `SUM` over zero rows returns `NULL`, so the row is
`(None,)`. `COALESCE(x, 0)` returns `x` when `x` is not `NULL` and `0` otherwise.

## The clauses of SELECT

A **clause** is one part of a statement that starts with a keyword, such as `WHERE` or
`ORDER BY`. `WHERE condition` keeps only the rows where the condition is true. `GROUP BY column` puts rows
with the same value into one group, and an **aggregate function** such as `COUNT(*)` or
`SUM(tokens)` computes one value per group. `ORDER BY column DESC` sorts the result. `LIMIT n`
keeps the first `n` rows, and `LIMIT n OFFSET k` skips `k` rows first.
`conn.executemany(sql, tuples)` runs the statement once for each tuple in the list.

```python
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE usage (model TEXT, tokens INTEGER)")
conn.executemany("INSERT INTO usage VALUES (?, ?)",
                 [("gpt", 300), ("claude", 250), ("gpt", 40), ("llama", 5), ("llama", 60)])
sql = """SELECT model, SUM(tokens) FROM usage
         WHERE tokens >= ?
         GROUP BY model
         ORDER BY SUM(tokens) DESC
         LIMIT 2"""
print(conn.execute(sql, (10,)).fetchall())
# [('gpt', 340), ('claude', 250)]
```

SQLite does not evaluate the clauses in the order you write them. Step through the stages to
see which rows are left after each clause of that query.

```diagram
{"type":"flow","title":"The order in which a SELECT is evaluated","steps":[
{"label":"FROM","detail":"SQLite starts with every row of the table named after FROM.","code":"FROM usage\n\n('gpt', 300)\n('claude', 250)\n('gpt', 40)\n('llama', 5)\n('llama', 60)"},
{"label":"WHERE","detail":"WHERE tests each row on its own. Rows where the condition is false are removed. The row ('llama', 5) fails tokens >= 10.","code":"WHERE tokens >= 10\n\n('gpt', 300)\n('claude', 250)\n('gpt', 40)\n('llama', 60)"},
{"label":"GROUP BY","detail":"Rows with the same model go into one group. Four rows become three groups.","code":"GROUP BY model\n\nclaude: 250\ngpt:    300, 40\nllama:  60"},
{"label":"SELECT","detail":"The SELECT list is computed once per group. SUM(tokens) adds the tokens of the rows in that group. Each group becomes one result row.","code":"SELECT model, SUM(tokens)\n\n('claude', 250)\n('gpt', 340)\n('llama', 60)"},
{"label":"ORDER BY","detail":"The result rows are sorted. DESC puts the largest sum first.","code":"ORDER BY SUM(tokens) DESC\n\n('gpt', 340)\n('claude', 250)\n('llama', 60)"},
{"label":"LIMIT","detail":"LIMIT keeps the first 2 rows of the sorted result and drops the rest.","code":"LIMIT 2\n\n('gpt', 340)\n('claude', 250)"}
]}
```

## Two tables

`JOIN` combines rows of two tables that satisfy an `ON` condition. A plain `JOIN` drops rows
that have no match. `LEFT JOIN` keeps every row of the first table and fills the missing
columns with `NULL`. `chats c` gives the table the short name `c` for the rest of the query,
so `c.title` is the `title` column of `chats`.

```python
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE chats (id INTEGER PRIMARY KEY, title TEXT)")
conn.execute("CREATE TABLE msgs (id INTEGER PRIMARY KEY, chat_id INTEGER, content TEXT)")
conn.executemany("INSERT INTO chats (title) VALUES (?)", [("Trip plan",), ("Empty chat",)])
conn.execute("INSERT INTO msgs (chat_id, content) VALUES (1, 'Book a train')")
join = "SELECT c.title, m.content FROM chats c JOIN msgs m ON m.chat_id = c.id"
print(conn.execute(join).fetchall())
# [('Trip plan', 'Book a train')]
left = "SELECT c.title, m.content FROM chats c LEFT JOIN msgs m ON m.chat_id = c.id ORDER BY c.id"
print(conn.execute(left).fetchall())
# [('Trip plan', 'Book a train'), ('Empty chat', None)]
```

`WHERE title LIKE ?` with the parameter `"%" + word + "%"` matches every title that contains
`word`. The `%` in a `LIKE` pattern stands for any text.

## Transactions

A **transaction** is a group of changes that the database saves together or not at all.
Changes are pending until `conn.commit()`. `with conn:` commits when the block finishes and
**rolls back** (discards the pending changes) when the block raises. Other connections see
only committed data.

## Rows as dicts

`conn.row_factory = sqlite3.Row` makes each row a `sqlite3.Row` object. You can read it by
column name or by position, and `dict(row)` converts it to a dict.

## Common mistakes

- `SUM` over zero rows returns `NULL`, which is `None` in Python. Write `COALESCE(SUM(x), 0)` to get `0`.
- `COUNT(*)` counts rows. `COUNT(m.id)` counts only the rows where `m.id` is not `NULL`. Use it after a `LEFT JOIN`.
- Without `ORDER BY`, the order of the rows is not guaranteed.
- In SQLite, `LIKE` ignores case for ASCII letters. `=` does not ignore case.
- In a `GROUP BY` query, select only the grouped columns and aggregates.
- `("user")` is a string, not a tuple. Pass `("user",)` as the parameters.
'''

EXERCISES = [
    # ------------------------------------------------------------------ difficulty 0
    {
        "id": "sql-s1",
        "title": "Your first table",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## Tables, rows and SQL

            A **database** stores data in tables. A **table** has a name and a fixed set of **columns**.
            Each **row** is one record with one value per column. A table `messages` with the columns
            `role` and `content` holds one row per chat message.

            You give the database instructions in **SQL** (Structured Query Language). One instruction
            is a **statement**. Python includes the `sqlite3` module, which runs **SQLite**: a database
            that keeps all its tables in a single file. The path `":memory:"` keeps the database in
            the computer's memory (RAM) instead, so nothing is written to disk and the data is gone
            when the program ends.

            ```python
            import sqlite3

            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE notes (text TEXT)")
            conn.execute("INSERT INTO notes VALUES ('check the token limit')")
            rows = conn.execute("SELECT text FROM notes").fetchall()
            print(rows)
            # [('check the token limit',)]
            print(rows[0][0])
            # check the token limit
            ```

            `sqlite3.connect(...)` returns a **connection**: the object that sends statements to the
            database. `conn.execute(sql)` runs one statement. `CREATE TABLE` creates a table,
            `INSERT INTO` adds a row and `SELECT` reads rows. Inside SQL, a string is written in
            single quotes, so the Python string around the SQL uses double quotes.

            `.fetchall()` returns the rows as a list of tuples. Each tuple is one row. It has one item
            for each column you selected, in the order you listed them.

            A `SELECT` of one column still returns tuples. The row above is `('check the token limit',)`,
            a tuple with one item. `rows[0][0]` reads the string inside it.
        ''',
        "prompt": r'''Read the code and type exactly what it prints.''',
        "code": r'''
            import sqlite3
            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE messages (role TEXT, content TEXT)")
            conn.execute("INSERT INTO messages VALUES ('user', 'Hi')")
            conn.execute("INSERT INTO messages VALUES ('assistant', 'Hello!')")
            rows = conn.execute("SELECT role, content FROM messages").fetchall()
            print(len(rows))
            print(rows[0])
            print(rows[1][1])
        ''',
        "solution": r'''
            2
            ('user', 'Hi')
            Hello!
        ''',
        "explanation": r'''
            Two rows were inserted, so `fetchall()` returns a list of 2 tuples. `rows[0]` is the
            first row as a tuple `('user', 'Hi')`. `rows[1][1]` is the second row, second column:
            the assistant's content `Hello!`.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "fetchall() returns a list with one tuple per row.",
            "Each tuple holds the columns in the order you listed them in SELECT: role, then content.",
            "Line 1 is the number of rows, line 2 prints a whole tuple (with quotes and brackets), line 3 picks one value out of the second tuple.",
        ],
    },
    {
        "id": "sql-s2",
        "title": "Create a usage table",
        "difficulty": 0,
        "lesson": r'''
            ## CREATE TABLE and column types

            `CREATE TABLE name (column TYPE, column TYPE, ...)` creates an empty table. You write each
            column name followed by its type.

            SQLite has three common types. `TEXT` holds strings. `INTEGER` holds whole numbers. `REAL`
            holds numbers with a decimal point. A column declared `INTEGER PRIMARY KEY` is the table's
            **primary key**: a value that is different for every row. SQLite assigns it when you insert
            a row without giving one.

            ```python
            import sqlite3

            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE documents (id INTEGER PRIMARY KEY, title TEXT, score REAL)")
            for row in conn.execute("PRAGMA table_info(documents)"):
                print(row[1], row[2])
            # id INTEGER
            # title TEXT
            # score REAL
            ```

            The list of a table's columns and their types is the table's **schema**.
            `PRAGMA table_info(documents)` is a SQLite statement that returns one row per column. The
            `for` loop reads those rows from the result of `execute`, one tuple at a time. Item
            `1` of each row is the column name and item `2` is its type.

            `CREATE TABLE` raises `sqlite3.OperationalError: table documents already exists` when
            the table already exists. `CREATE TABLE IF NOT EXISTS` does nothing in that case, so
            it is safe to run every time your program starts.
        ''',
        "prompt": r'''
            An AI app records how many tokens each model call used. Create the table for it.

            **Write:** `create_usage_table(conn)`

            - `conn`: an open `sqlite3` connection (the checks pass in an empty in-memory database)
            - **Returns:** nothing (`None`) - it only creates the table

            **Rules**
            - The table is called exactly `usage`.
            - It has exactly three columns, in this order: `model TEXT`, `input_tokens INTEGER`,
              `output_tokens INTEGER`.

            **Examples**
            ```python
            conn = sqlite3.connect(":memory:")
            create_usage_table(conn)
            conn.execute("INSERT INTO usage VALUES ('gpt-4o-mini', 120, 40)")   # now works
            ```
        ''',
        "starter": r'''
            def create_usage_table(conn):
                conn.execute("CREATE TABLE ___ (model TEXT, ___ INTEGER, output_tokens INTEGER)")
        ''',
        "tests": r'''
            import sqlite3
            from solution import create_usage_table

            def fresh():
                conn = sqlite3.connect(":memory:")
                create_usage_table(conn)
                return conn

            def test_table_named_usage_exists():
                conn = fresh()
                names = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")]
                assert "usage" in names, f"tables found: {names}"

            def test_column_names_in_order():
                cols = [r[1] for r in fresh().execute("PRAGMA table_info(usage)")]
                assert cols == ["model", "input_tokens", "output_tokens"], f"got columns {cols}"

            def test_column_types():
                types = [r[2].upper() for r in fresh().execute("PRAGMA table_info(usage)")]
                assert types == ["TEXT", "INTEGER", "INTEGER"], f"got types {types}"

            def test_rows_can_be_inserted():
                conn = fresh()
                conn.execute("INSERT INTO usage VALUES ('gpt-4o-mini', 120, 40)")
                got = conn.execute("SELECT * FROM usage").fetchall()
                assert got == [("gpt-4o-mini", 120, 40)], f"got {got}"
        ''',
        "solution": r'''
            def create_usage_table(conn):
                conn.execute("CREATE TABLE usage (model TEXT, input_tokens INTEGER, output_tokens INTEGER)")
        ''',
        "hints": [
            "Fill both blanks with names from the prompt: one table name, one column name.",
            "The table is `usage`; the missing column is the one that counts tokens sent to the model.",
            "Replace the first `___` with `usage` and the second with `input_tokens`. No quotes needed around names inside the SQL.",
        ],
    },
    {
        "id": "sql-s3",
        "title": "Fix the unsafe insert",
        "difficulty": 0,
        "lesson": r'''
            ## Placeholders and parameters

            A **placeholder** is a `?` in the SQL text that marks where a value goes. You pass the values
            as a tuple in the second argument of `execute`. These values are called **query parameters**.
            SQLite uses the first value for the first `?`, the second value for the second `?`, and so on.

            ```python
            import sqlite3

            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE messages (role TEXT, content TEXT)")
            text = "It's done"
            conn.execute("INSERT INTO messages (role, content) VALUES (?, ?)", ("user", text))
            print(conn.execute("SELECT role, content FROM messages").fetchall())
            # [('user', "It's done")]
            ```

            SQLite receives the SQL text and the values separately. It never reads a parameter as SQL, so
            the apostrophe in `It's done` is stored as an ordinary character.

            An f-string puts the value into the SQL text itself. The apostrophe then ends the SQL string
            after `It`, and the rest is not valid SQL. This program raises on purpose.

            ```python
            import sqlite3

            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE messages (role TEXT, content TEXT)")
            text = "It's done"
            sql = f"INSERT INTO messages (role, content) VALUES ('user', '{text}')"
            print(sql)
            # INSERT INTO messages (role, content) VALUES ('user', 'It's done')
            conn.execute(sql)
            # sqlite3.OperationalError: near "s": syntax error
            ```

            The same mechanism lets a user change your statement: the text they type becomes part of the
            SQL. This attack is called **SQL injection**. Text a user types is untrusted: it can
            contain quotes and SQL words. Always pass it as parameters.
        ''',
        "prompt": r'''
            This function saves a chat message, but it builds the SQL with an f-string. It crashes
            on messages like `"It's fine"` and is open to SQL injection.

            **Write:** fix `add_message(conn, role, content)`

            - `conn`: an open connection that already has a table `messages (role TEXT, content TEXT)`
            - `role`: a `str` such as `"user"`
            - `content`: a `str`, any text the user typed
            - **Returns:** nothing (`None`)

            **Rules**
            - Insert one row with the given role and content, stored **exactly** as given.
            - Use `?` placeholders (a check looks for them in your code); no f-strings in the SQL.
            - Text containing quotes or SQL must be stored as plain text and must not break anything.

            **Examples**
            ```python
            add_message(conn, "user", "It's fine")
            conn.execute("SELECT * FROM messages").fetchall()   # [("user", "It's fine")]
            ```
        ''',
        "starter": r'''
            def add_message(conn, role, content):
                conn.execute(f"INSERT INTO messages (role, content) VALUES ('{role}', '{content}')")
        ''',
        "tests": r'''
            import sqlite3
            from solution import add_message

            def fresh():
                conn = sqlite3.connect(":memory:")
                conn.execute("CREATE TABLE messages (role TEXT, content TEXT)")
                return conn

            def test_plain_message_is_stored():
                conn = fresh()
                add_message(conn, "user", "Hello")
                got = conn.execute("SELECT role, content FROM messages").fetchall()
                assert got == [("user", "Hello")], f"got {got}"

            def test_apostrophe_is_stored_exactly():
                conn = fresh()
                add_message(conn, "user", "It's fine")
                got = conn.execute("SELECT content FROM messages").fetchall()
                assert got == [("It's fine",)], f"got {got}"

            def test_sql_in_the_text_is_just_text():
                conn = fresh()
                evil = "x'); DROP TABLE messages; --"
                add_message(conn, "user", evil)
                got = conn.execute("SELECT content FROM messages").fetchall()
                assert got == [(evil,)], f"got {got}"

            def test_uses_question_mark_placeholders():
                src = source()
                assert "?" in src, "use ? placeholders in the SQL"
                assert "{content}" not in src and "{role}" not in src, "don't paste values into the SQL string"
        ''',
        "solution": r'''
            def add_message(conn, role, content):
                conn.execute("INSERT INTO messages (role, content) VALUES (?, ?)", (role, content))
        ''',
        "hints": [
            "The values should not be part of the SQL text at all.",
            "Put one `?` where each value goes, and pass the real values as a second argument to execute.",
            "Remove the `f` and the `'{...}'` parts, write `VALUES (?, ?)`, and pass the tuple `(role, content)` after the SQL string.",
        ],
    },
    {
        "id": "sql-s4",
        "title": "Unpack the rows",
        "difficulty": 0,
        "lesson": r'''
            ## Rows are tuples

            `fetchall()` returns a list of tuples. Each tuple is one row. It holds the columns you
            selected, in the order you listed them.

            ```python
            import sqlite3

            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE docs (title TEXT, words INTEGER)")
            conn.execute("INSERT INTO docs VALUES ('FAQ', 300), ('Guide', 1200)")
            rows = conn.execute("SELECT title, words FROM docs").fetchall()
            print(rows)
            # [('FAQ', 300), ('Guide', 1200)]
            print(rows[0][0])
            # FAQ
            titles = []
            for title, words in rows:
                titles.append(title)
                print(title, "has", words, "words")
            # FAQ has 300 words
            # Guide has 1200 words
            print(titles)
            # ['FAQ', 'Guide']
            ```

            One `INSERT` can add several rows: write one `(...)` group per row after `VALUES`, with
            commas between the groups.

            `rows[0]` is the first row and `rows[0][0]` is its first column. To **unpack** a tuple is to
            assign each of its items to its own name. `for title, words in rows` unpacks every row into
            `title` and `words`.

            Step through the loop to see `title` and `words` change for each row.

            ```diagram
            {"type": "trace", "title": "Unpacking each row of rows", "code": ["rows = [(\"FAQ\", 300), (\"Guide\", 1200)]", "titles = []", "for title, words in rows:", "    titles.append(title)", "    print(title, \"has\", words, \"words\")", "print(titles)"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 2, "vars": {"rows": "[('FAQ', 300), ('Guide', 1200)]"}, "out": ""},
              {"line": 3, "vars": {"rows": "[('FAQ', 300), ('Guide', 1200)]", "titles": "[]"}, "out": ""},
              {"line": 4, "vars": {"rows": "[('FAQ', 300), ('Guide', 1200)]", "titles": "[]", "title": "'FAQ'", "words": "300"}, "out": ""},
              {"line": 5, "vars": {"rows": "[('FAQ', 300), ('Guide', 1200)]", "titles": "['FAQ']", "title": "'FAQ'", "words": "300"}, "out": ""},
              {"line": 3, "vars": {"rows": "[('FAQ', 300), ('Guide', 1200)]", "titles": "['FAQ']", "title": "'FAQ'", "words": "300"}, "out": "FAQ has 300 words\n"},
              {"line": 4, "vars": {"rows": "[('FAQ', 300), ('Guide', 1200)]", "titles": "['FAQ']", "title": "'Guide'", "words": "1200"}, "out": "FAQ has 300 words\n"},
              {"line": 5, "vars": {"rows": "[('FAQ', 300), ('Guide', 1200)]", "titles": "['FAQ', 'Guide']", "title": "'Guide'", "words": "1200"}, "out": "FAQ has 300 words\n"},
              {"line": 3, "vars": {"rows": "[('FAQ', 300), ('Guide', 1200)]", "titles": "['FAQ', 'Guide']", "title": "'Guide'", "words": "1200"}, "out": "FAQ has 300 words\nGuide has 1200 words\n"},
              {"line": 6, "vars": {"rows": "[('FAQ', 300), ('Guide', 1200)]", "titles": "['FAQ', 'Guide']", "title": "'Guide'", "words": "1200"}, "out": "FAQ has 300 words\nGuide has 1200 words\n"},
              {"line": null, "vars": {"rows": "[('FAQ', 300), ('Guide', 1200)]", "titles": "['FAQ', 'Guide']", "title": "'Guide'", "words": "1200"}, "out": "FAQ has 300 words\nGuide has 1200 words\n['FAQ', 'Guide']\n"}
            ]}
            ```

            `conn.execute(...)` returns a **cursor**: an object that produces the result rows one at a
            time. You can loop over the cursor directly, without `fetchall()`.

            A `SELECT` of one column gives tuples with one item, such as `('FAQ',)`. It does not give
            plain strings. Read the value with `row[0]`.
        ''',
        "prompt": r'''
            Get the text of every stored chat message as a plain list of strings.

            **Write:** `all_contents(conn)`

            - `conn`: an open connection with a table `messages (id INTEGER PRIMARY KEY, role TEXT, content TEXT)`
            - **Returns:** a `list` of `str`: the `content` of every row, in `id` order

            **Rules**
            - Return plain strings, not tuples.
            - If the table is empty, return `[]`.

            **Examples**
            ```python
            # rows: (1, "user", "Hi"), (2, "assistant", "Hello!")
            all_contents(conn)   # returns ["Hi", "Hello!"]
            all_contents(empty)  # returns []
            ```
        ''',
        "starter": r'''
            def all_contents(conn):
                ...
        ''',
        "tests": r'''
            import sqlite3
            from solution import all_contents

            def fresh(rows):
                conn = sqlite3.connect(":memory:")
                conn.execute("CREATE TABLE messages (id INTEGER PRIMARY KEY, role TEXT, content TEXT)")
                conn.executemany("INSERT INTO messages (role, content) VALUES (?, ?)", rows)
                return conn

            def test_returns_contents_in_order():
                conn = fresh([("user", "Hi"), ("assistant", "Hello!"), ("user", "Thanks")])
                got = all_contents(conn)
                assert got == ["Hi", "Hello!", "Thanks"], f"got {got!r}"

            def test_items_are_strings_not_tuples():
                got = all_contents(fresh([("user", "Hi")]))
                assert got and isinstance(got[0], str), f"got {got!r}"

            def test_empty_table_returns_empty_list():
                got = all_contents(fresh([]))
                assert got == [], f"got {got!r}"
        ''',
        "solution": r'''
            def all_contents(conn):
                rows = conn.execute("SELECT content FROM messages ORDER BY id").fetchall()
                return [row[0] for row in rows]
        ''',
        "hints": [
            "SELECT just the content column, then turn each 1-item tuple into its value.",
            "fetchall() gives tuples like ('Hi',); take the first item of each.",
            "Run `SELECT content FROM messages`, fetch all rows, and build a new list with `row[0]` for each row (a list comprehension works well).",
        ],
    },
    {
        "id": "sql-s5",
        "title": "Filter with WHERE",
        "difficulty": 0,
        "lesson": r'''
            ## WHERE

            `WHERE condition` goes after the table name in a `SELECT`. SQLite tests the condition on
            every row and returns only the rows where it is true.

            ```python
            import sqlite3

            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE usage (model TEXT, tokens INTEGER)")
            conn.executemany("INSERT INTO usage VALUES (?, ?)",
                             [("gpt", 100), ("claude", 250), ("gpt", 40)])
            rows = conn.execute("SELECT tokens FROM usage WHERE model = ?", ("gpt",)).fetchall()
            print(rows)
            # [(100,), (40,)]
            print(conn.execute("SELECT model FROM usage WHERE tokens > 90").fetchall())
            # [('gpt',), ('claude',)]
            print(conn.execute("SELECT tokens FROM usage WHERE model = 'gpt' AND tokens < 90").fetchall())
            # [(40,)]
            ```

            `executemany(sql, tuples)` runs the statement once for each tuple in the list.

            The SQL comparison operators are `=`, `!=`, `<`, `>`, `<=` and `>=`. SQL compares with a
            single `=`, not `==`. `AND` and `OR` combine two conditions.

            The parameters must be a tuple. `("gpt")` is the string `"gpt"` in parentheses. `("gpt",)`,
            with the comma, is a tuple with one item. If you pass the string, `sqlite3` treats each of
            its 3 characters as one parameter and raises `sqlite3.ProgrammingError: Incorrect number
            of bindings supplied. The current statement uses 1, and there are 3 supplied.`
        ''',
        "prompt": r'''
            Fetch only the messages written by one role.

            **Write:** `messages_by_role(conn, role)`

            - `conn`: an open connection with a table `messages (id INTEGER PRIMARY KEY, role TEXT, content TEXT)`
            - `role`: a `str`, e.g. `"user"`
            - **Returns:** a `list` of `str`: the `content` of every message with that role, in `id` order

            **Rules**
            - Pass `role` as a `?` parameter.
            - If no message has that role, return `[]`.

            **Examples**
            ```python
            # rows: (1, "system", "Be brief"), (2, "user", "Hi"), (3, "assistant", "Hey"), (4, "user", "Bye")
            messages_by_role(conn, "user")    # returns ["Hi", "Bye"]
            messages_by_role(conn, "tool")    # returns []
            ```
        ''',
        "starter": r'''
            def messages_by_role(conn, role):
                rows = conn.execute("SELECT content FROM messages WHERE ___", (role,)).fetchall()
                return [row[0] for row in rows]
        ''',
        "tests": r'''
            import sqlite3
            from solution import messages_by_role

            def fresh():
                conn = sqlite3.connect(":memory:")
                conn.execute("CREATE TABLE messages (id INTEGER PRIMARY KEY, role TEXT, content TEXT)")
                conn.executemany("INSERT INTO messages (role, content) VALUES (?, ?)",
                                 [("system", "Be brief"), ("user", "Hi"), ("assistant", "Hey"), ("user", "Bye")])
                return conn

            def test_user_messages():
                got = messages_by_role(fresh(), "user")
                assert got == ["Hi", "Bye"], f"got {got!r}"

            def test_single_match():
                got = messages_by_role(fresh(), "system")
                assert got == ["Be brief"], f"got {got!r}"

            def test_no_match_returns_empty_list():
                got = messages_by_role(fresh(), "tool")
                assert got == [], f"got {got!r}"
        ''',
        "solution": r'''
            def messages_by_role(conn, role):
                rows = conn.execute("SELECT content FROM messages WHERE role = ? ORDER BY id", (role,)).fetchall()
                return [row[0] for row in rows]
        ''',
        "hints": [
            "The blank is a condition comparing a column with the parameter.",
            "Which column holds the role? Compare it to a `?` placeholder.",
            "Replace `___` with `role = ?` (a single `=` in SQL). The tuple `(role,)` fills the `?`.",
        ],
    },
    {
        "id": "sql-s6",
        "title": "Top documents",
        "difficulty": 0,
        "lesson": r'''
            ## ORDER BY and LIMIT

            `ORDER BY column` sorts the result rows by that column. `ASC` (ascending) sorts from small
            to large or from A to Z, and it is the default. `DESC` (descending) sorts from large to small.

            `LIMIT n` keeps only the first `n` rows of the result. SQLite sorts first and applies
            `LIMIT` afterwards.

            ```python
            import sqlite3

            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE docs (title TEXT, score REAL)")
            conn.executemany("INSERT INTO docs VALUES (?, ?)",
                             [("a", 0.2), ("b", 0.9), ("c", 0.5), ("d", 0.9)])
            print(conn.execute("SELECT title, score FROM docs ORDER BY score").fetchall())
            # [('a', 0.2), ('c', 0.5), ('b', 0.9), ('d', 0.9)]
            sql = "SELECT title, score FROM docs ORDER BY score DESC, title ASC LIMIT ?"
            print(conn.execute(sql, (3,)).fetchall())
            # [('b', 0.9), ('d', 0.9), ('c', 0.5)]
            ```

            You can list more than one column after `ORDER BY`. SQLite sorts by the first column. It
            uses the second column only for rows that have the same value in the first. Here `b` and
            `d` both have the score `0.9`, so `title ASC` puts `b` before `d`.

            `LIMIT ?` takes its number from a parameter, like any other value.

            A search system uses this query shape to return its best results: it sorts the documents by
            score and keeps the first k.

            Without `ORDER BY`, the database can return the rows in any order.
        ''',
        "prompt": r'''
            A search step scored some documents. Return the best ones.

            **Write:** `top_documents(conn, n)`

            - `conn`: an open connection with a table `documents (title TEXT, score REAL)`
            - `n`: an `int`, how many titles to return (at least 0)
            - **Returns:** a `list` of `str` titles: the `n` highest-scoring documents, highest first

            **Rules**
            - Documents with the same score are ordered by title, A to Z.
            - If there are fewer than `n` documents, return all of them.
            - `n = 0` returns `[]`.

            **Examples**
            ```python
            # rows: ("faq", 0.4), ("guide", 0.9), ("api", 0.7), ("blog", 0.9)
            top_documents(conn, 2)    # returns ["blog", "guide"]
            top_documents(conn, 10)   # returns ["blog", "guide", "api", "faq"]
            ```
        ''',
        "starter": r'''
            def top_documents(conn, n):
                ...
        ''',
        "tests": r'''
            import sqlite3
            from solution import top_documents

            def fresh():
                conn = sqlite3.connect(":memory:")
                conn.execute("CREATE TABLE documents (title TEXT, score REAL)")
                conn.executemany("INSERT INTO documents VALUES (?, ?)",
                                 [("faq", 0.4), ("guide", 0.9), ("api", 0.7), ("blog", 0.9)])
                return conn

            def test_top_two_with_tie_broken_by_title():
                got = top_documents(fresh(), 2)
                assert got == ["blog", "guide"], f"got {got!r}"

            def test_top_three():
                got = top_documents(fresh(), 3)
                assert got == ["blog", "guide", "api"], f"got {got!r}"

            def test_more_than_available_returns_all():
                got = top_documents(fresh(), 10)
                assert got == ["blog", "guide", "api", "faq"], f"got {got!r}"

            def test_zero_returns_empty():
                got = top_documents(fresh(), 0)
                assert got == [], f"got {got!r}"
        ''',
        "solution": r'''
            def top_documents(conn, n):
                rows = conn.execute(
                    "SELECT title FROM documents ORDER BY score DESC, title ASC LIMIT ?", (n,)
                ).fetchall()
                return [row[0] for row in rows]
        ''',
        "hints": [
            "You need ORDER BY (with a tie-breaker) and LIMIT.",
            "Sort by score from high to low, then by title from A to Z, and keep only n rows.",
            "SELECT title, add `ORDER BY score DESC, title ASC LIMIT ?`, pass `(n,)`, then take `row[0]` from each row.",
        ],
    },
    # ------------------------------------------------------------------ difficulty 1
    {
        "id": "sql-7",
        "title": "Total tokens used",
        "difficulty": 1,
        "lesson": r'''
            ## Aggregate functions

            An **aggregate function** takes the values of many rows and returns one value. `COUNT(*)`
            returns the number of rows. `SUM(col)` adds the values of a column. `AVG(col)`, `MIN(col)`
            and `MAX(col)` return the average, the smallest and the largest value. (In this
            example `tokens` is just a number in a table. Services that charge for text
            count pieces of text called tokens for billing. That is all the word means.)

            ```python
            import sqlite3

            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE usage (model TEXT, tokens INTEGER)")
            conn.executemany("INSERT INTO usage VALUES (?, ?)", [("gpt", 100), ("gpt", 50)])
            count, total = conn.execute("SELECT COUNT(*), SUM(tokens) FROM usage").fetchone()
            print(count, total)
            # 2 150
            print(conn.execute("SELECT SUM(tokens * 2) FROM usage").fetchone())
            # (300,)
            conn.execute("DELETE FROM usage")
            print(conn.execute("SELECT COUNT(*), SUM(tokens) FROM usage").fetchone())
            # (0, None)
            print(conn.execute("SELECT COALESCE(SUM(tokens), 0) FROM usage").fetchone())
            # (0,)
            ```

            A query that selects only aggregates returns exactly one row. `.fetchone()` returns the
            first row of the result as one tuple, so you do not need to index into a list.

            You can write a calculation inside an aggregate. `SUM(tokens * 2)` doubles the value of each
            row and then adds the results. `SUM(a + b)` adds two columns for each row in the same way.

            `DELETE FROM usage` removes every row. `SUM` over zero rows returns the SQL value `NULL`,
            which means "no value" and arrives in Python as `None`, not `0`. `COALESCE(x, 0)` returns `x`
            when `x` is not `NULL` and `0` otherwise.
        ''',
        "prompt": r'''
            Work out how many tokens the app has used in total, across all calls.

            **Write:** `total_tokens(conn)`

            - `conn`: an open connection with a table `usage (model TEXT, input_tokens INTEGER, output_tokens INTEGER)`
            - **Returns:** an `int`: the sum of `input_tokens` plus `output_tokens` over all rows

            **Rules**
            - If the table is empty, return `0` (not `None`).

            **Examples**
            ```python
            # rows: ("gpt-4o-mini", 100, 20), ("claude-haiku", 300, 80)
            total_tokens(conn)    # returns 500
            total_tokens(empty)   # returns 0
            ```
        ''',
        "starter": r'''
            def total_tokens(conn):
                ...
        ''',
        "tests": r'''
            import sqlite3
            from solution import total_tokens

            def fresh(rows):
                conn = sqlite3.connect(":memory:")
                conn.execute("CREATE TABLE usage (model TEXT, input_tokens INTEGER, output_tokens INTEGER)")
                conn.executemany("INSERT INTO usage VALUES (?, ?, ?)", rows)
                return conn

            def test_sums_input_and_output():
                got = total_tokens(fresh([("gpt-4o-mini", 100, 20), ("claude-haiku", 300, 80)]))
                assert got == 500, f"got {got!r}"

            def test_single_row():
                got = total_tokens(fresh([("gpt-4o-mini", 7, 3)]))
                assert got == 10, f"got {got!r}"

            def test_empty_table_returns_zero_not_none():
                got = total_tokens(fresh([]))
                assert got == 0 and got is not None, f"got {got!r}"
        ''',
        "solution": r'''
            def total_tokens(conn):
                row = conn.execute(
                    "SELECT COALESCE(SUM(input_tokens + output_tokens), 0) FROM usage"
                ).fetchone()
                return row[0]
        ''',
        "hints": [
            "One aggregate query can add up both columns for every row.",
            "SUM the two columns added together, and deal with the empty-table case where SUM gives None.",
            "Run `SELECT SUM(input_tokens + output_tokens) FROM usage`, use `fetchone()[0]`, and return 0 if that is None (or wrap the SUM in COALESCE(..., 0)).",
        ],
    },
    {
        "id": "sql-8",
        "title": "Tokens per model",
        "difficulty": 1,
        "lesson": r'''
            ## GROUP BY

            `GROUP BY column` puts the rows that have the same value in that column into one group.
            An aggregate such as `SUM` or `COUNT` is then computed once for each group. The result has
            **one row per group**.

            ```python
            import sqlite3

            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE usage (model TEXT, tokens INTEGER)")
            conn.executemany("INSERT INTO usage VALUES (?, ?)",
                             [("gpt", 100), ("claude", 250), ("gpt", 40)])
            sql = "SELECT model, COUNT(*), SUM(tokens) FROM usage GROUP BY model ORDER BY model"
            for model, calls, tokens in conn.execute(sql):
                print(model, calls, tokens)
            # claude 1 250
            # gpt 2 140
            having = "SELECT model, SUM(tokens) FROM usage GROUP BY model HAVING SUM(tokens) > 200"
            print(conn.execute(having).fetchall())
            # [('claude', 250)]
            ```

            The two `gpt` rows form one group, so `COUNT(*)` is `2` and `SUM(tokens)` is `140`.

            Every column you select should either appear in the `GROUP BY` or be inside an aggregate.
            Here `model` is the grouped column and the other two values are aggregates. SQLite raises
            no error for any other column. It returns that column's value from one row of the group,
            and you cannot rely on which row.

            Each result row is a tuple such as `('gpt', 2, 140)`. To build a dict from the result, loop
            over the rows and store one entry per row.

            `WHERE` filters rows before they are grouped, so it cannot test a group's total. `HAVING`
            filters the groups after the aggregates are computed. `HAVING SUM(tokens) > 200` keeps only
            the `claude` group.
        ''',
        "prompt": r'''
            Build a per-model token bill.

            **Write:** `tokens_by_model(conn)`

            - `conn`: an open connection with a table `usage (model TEXT, input_tokens INTEGER, output_tokens INTEGER)`
            - **Returns:** a `dict` mapping each model name (`str`) to its total tokens (`int`,
              input plus output, summed over all that model's rows)

            **Rules**
            - Each model appears once.
            - An empty table gives `{}`.

            **Examples**
            ```python
            # rows: ("gpt", 100, 20), ("claude", 300, 80), ("gpt", 50, 10)
            tokens_by_model(conn)    # returns {"gpt": 180, "claude": 380}
            tokens_by_model(empty)   # returns {}
            ```
        ''',
        "starter": r'''
            def tokens_by_model(conn):
                ...
        ''',
        "tests": r'''
            import sqlite3
            from solution import tokens_by_model

            def fresh(rows):
                conn = sqlite3.connect(":memory:")
                conn.execute("CREATE TABLE usage (model TEXT, input_tokens INTEGER, output_tokens INTEGER)")
                conn.executemany("INSERT INTO usage VALUES (?, ?, ?)", rows)
                return conn

            def test_groups_by_model():
                got = tokens_by_model(fresh([("gpt", 100, 20), ("claude", 300, 80), ("gpt", 50, 10)]))
                assert got == {"gpt": 180, "claude": 380}, f"got {got!r}"

            def test_single_model():
                got = tokens_by_model(fresh([("gpt", 1, 2), ("gpt", 3, 4)]))
                assert got == {"gpt": 10}, f"got {got!r}"

            def test_empty_table_returns_empty_dict():
                got = tokens_by_model(fresh([]))
                assert got == {}, f"got {got!r}"
        ''',
        "solution": r'''
            def tokens_by_model(conn):
                sql = "SELECT model, SUM(input_tokens + output_tokens) FROM usage GROUP BY model"
                return {model: total for model, total in conn.execute(sql)}
        ''',
        "hints": [
            "GROUP BY the model column and SUM the tokens.",
            "Your query returns (model, total) rows; turn those rows into a dict.",
            "SELECT model and SUM(input_tokens + output_tokens) with GROUP BY model, then loop over the rows and set `result[model] = total` (or use `dict(rows)`).",
        ],
    },
    {
        "id": "sql-9",
        "title": "Join conversations and messages",
        "difficulty": 1,
        "lesson": r'''
            ## JOIN

            Related data is often split across two tables. In the example below, `chats` has one row per
            conversation and `msgs` has one row per message. Each message stores the id of its chat in
            the column `chat_id`. A column that holds the id of a row in another table is a
            **foreign key**. The title is stored once, not on every message.

            `JOIN` builds each result row from one row of each table. The `ON` condition states which
            rows belong together.

            ```python
            import sqlite3

            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE chats (id INTEGER PRIMARY KEY, title TEXT)")
            conn.execute("CREATE TABLE msgs (id INTEGER PRIMARY KEY, chat_id INTEGER, content TEXT)")
            conn.execute("INSERT INTO chats (title) VALUES ('Trip plan'), ('Bug report')")
            conn.execute("INSERT INTO msgs (chat_id, content) VALUES (2, 'It crashes'), (1, 'Book a train')")
            sql = """SELECT c.title, m.content FROM msgs m
                     JOIN chats c ON c.id = m.chat_id ORDER BY m.id"""
            print(conn.execute(sql).fetchall())
            # [('Bug report', 'It crashes'), ('Trip plan', 'Book a train')]
            ```

            `msgs m` gives the table an **alias**: a short name, `m`, that you use in the rest of the
            query. For each row of `msgs`, SQLite finds the row of `chats` whose `id` equals `m.chat_id`.
            The result row can use the columns of both rows.

            Both tables have a column named `id`. You must write `m.id` or `c.id` to say which one you
            mean. A bare `id` in this query raises `sqlite3.OperationalError: ambiguous column name: id`.
        ''',
        "prompt": r'''
            Print a readable transcript of every stored message, labelled with its conversation title.

            **Write:** `transcript_lines(conn)`

            - `conn`: an open connection with two tables:
              `conversations (id INTEGER PRIMARY KEY, title TEXT)` and
              `messages (id INTEGER PRIMARY KEY, conversation_id INTEGER, role TEXT, content TEXT)`
            - **Returns:** a `list` of `str`, one per message, formatted `"<title> | <role>: <content>"`

            **Rules**
            - Order the lines by the message `id`.
            - Messages from every conversation are included.
            - No messages gives `[]`.

            **Examples**
            ```python
            # conversations: (1, "Refund"), (2, "Recipe")
            # messages: (1, 2, "user", "Pasta?"), (2, 1, "user", "Where is my money"), (3, 2, "assistant", "Try carbonara")
            transcript_lines(conn)
            # returns ["Recipe | user: Pasta?",
            #          "Refund | user: Where is my money",
            #          "Recipe | assistant: Try carbonara"]
            ```
        ''',
        "starter": r'''
            def transcript_lines(conn):
                ...
        ''',
        "tests": r'''
            import sqlite3
            from solution import transcript_lines

            def fresh(messages):
                conn = sqlite3.connect(":memory:")
                conn.execute("CREATE TABLE conversations (id INTEGER PRIMARY KEY, title TEXT)")
                conn.execute("CREATE TABLE messages (id INTEGER PRIMARY KEY, conversation_id INTEGER, role TEXT, content TEXT)")
                conn.executemany("INSERT INTO conversations VALUES (?, ?)", [(1, "Refund"), (2, "Recipe")])
                conn.executemany("INSERT INTO messages VALUES (?, ?, ?, ?)", messages)
                return conn

            def test_lines_labelled_and_ordered_by_message_id():
                conn = fresh([(1, 2, "user", "Pasta?"), (2, 1, "user", "Where is my money"),
                              (3, 2, "assistant", "Try carbonara")])
                got = transcript_lines(conn)
                assert got == ["Recipe | user: Pasta?", "Refund | user: Where is my money",
                               "Recipe | assistant: Try carbonara"], f"got {got!r}"

            def test_order_follows_message_id_not_insert_order():
                conn = fresh([(5, 1, "assistant", "Sorry"), (2, 1, "user", "Help")])
                got = transcript_lines(conn)
                assert got == ["Refund | user: Help", "Refund | assistant: Sorry"], f"got {got!r}"

            def test_no_messages_returns_empty_list():
                got = transcript_lines(fresh([]))
                assert got == [], f"got {got!r}"
        ''',
        "solution": r'''
            def transcript_lines(conn):
                sql = """
                    SELECT c.title, m.role, m.content
                    FROM messages m
                    JOIN conversations c ON c.id = m.conversation_id
                    ORDER BY m.id
                """
                return [f"{title} | {role}: {content}" for title, role, content in conn.execute(sql)]
        ''',
        "hints": [
            "You need columns from both tables in one query: that is a JOIN.",
            "Join messages to conversations where the conversation's id equals the message's conversation_id, and order by the message id.",
            "SELECT c.title, m.role, m.content FROM messages m JOIN conversations c ON c.id = m.conversation_id ORDER BY m.id; then format each row with an f-string.",
        ],
    },
    {
        "id": "sql-10",
        "title": "Save a chat, all or nothing",
        "difficulty": 1,
        "lesson": r'''
            ## Transactions

            A **transaction** is a group of changes that the database saves together. `sqlite3` starts
            a transaction before an `INSERT`. The changes are pending until you **commit**, which
            makes them permanent. A **rollback** discards every pending change of the transaction.

            `with conn:` commits when the block finishes without an exception. It rolls back when an
            exception leaves the block, and the exception is then raised out of the block. `with conn:`
            does not close the connection.

            ```python
            import sqlite3

            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE usage (id INTEGER PRIMARY KEY, model TEXT, tokens INTEGER)")
            try:
                with conn:
                    conn.execute("INSERT INTO usage (model, tokens) VALUES ('gpt', 100)")
                    raise ValueError("bad row")
            except ValueError as err:
                print("error:", err)
            # error: bad row
            print(conn.execute("SELECT COUNT(*) FROM usage").fetchone())
            # (0,)
            with conn:
                cur = conn.execute("INSERT INTO usage (model, tokens) VALUES ('claude', 250)")
            print(cur.lastrowid)
            # 1
            ```

            Step through the stages to see what happens to the `gpt` row in the first `with` block.

            ```diagram
            {"type":"flow","title":"A with conn: block that raises","steps":[
            {"label":"INSERT","detail":"sqlite3 starts a transaction and runs the INSERT. The new row is pending. It is not saved yet.","code":"conn.execute(\"INSERT INTO usage (model, tokens) VALUES ('gpt', 100)\")\n\npending: (1, 'gpt', 100)"},
            {"label":"raise","detail":"The ValueError leaves the with block before the block finishes.","code":"raise ValueError(\"bad row\")"},
            {"label":"rollback","detail":"Because an exception left the block, with conn: rolls the transaction back. The pending row is discarded.","code":"pending: nothing\nusage table: 0 rows"},
            {"label":"except","detail":"The exception continues after the rollback. The except clause catches it and prints the message.","code":"except ValueError as err:\n    print(\"error:\", err)\n\nerror: bad row"},
            {"label":"SELECT","detail":"The table is empty. No change from the failed block remains.","code":"conn.execute(\"SELECT COUNT(*) FROM usage\").fetchone()\n\n(0,)"}
            ]}
            ```

            Other connections see only committed data. Another program that reads the same database
            file does not see pending rows.

            `conn.execute` returns a cursor. After an `INSERT`, `cur.lastrowid` is the id that the new
            row received.
        ''',
        "prompt": r'''
            Save a whole conversation (its title and its messages) so that either everything is
            saved, or nothing is.

            **Write:** `save_chat(conn, title, messages)`

            - `conn`: an open connection with tables
              `conversations (id INTEGER PRIMARY KEY, title TEXT)` and
              `messages (id INTEGER PRIMARY KEY, conversation_id INTEGER, role TEXT, content TEXT)`
            - `title`: a `str`
            - `messages`: a `list` of dicts like `{"role": "user", "content": "Hi"}`
            - **Returns:** the new conversation's `id` (an `int`)

            **Rules**
            - Insert one `conversations` row, then one `messages` row per message (in list order),
              each with `conversation_id` set to the new conversation's id.
            - Allowed roles are `"system"`, `"user"`, `"assistant"`. If any message has another
              role, raise `ValueError`, and **nothing** from this call may remain in the database
              (not even the conversation row).
            - On success the data must be **committed** (a second connection to the same file
              must see it).

            **Examples**
            ```python
            save_chat(conn, "Trip", [{"role": "user", "content": "Train times?"}])   # returns 1
            save_chat(conn, "Bad", [{"role": "user", "content": "a"},
                                    {"role": "robot", "content": "b"}])             # raises ValueError
            ```
        ''',
        "research": {
            "note": "Read how a sqlite3 connection works as a context manager (`with conn:`) - "
                    "what it does on success and on an exception - then come back.",
            "links": [{"title": "sqlite3: how to use the connection context manager - Python docs",
                       "url": "https://docs.python.org/3/library/sqlite3.html#sqlite3-connection-context-manager"}],
        },
        "starter": r'''
            def save_chat(conn, title, messages):
                ...
        ''',
        "tests": r'''
            import sqlite3
            from solution import save_chat

            SCHEMA = [
                "CREATE TABLE IF NOT EXISTS conversations (id INTEGER PRIMARY KEY, title TEXT)",
                "CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, conversation_id INTEGER, role TEXT, content TEXT)",
            ]

            def fresh(path=":memory:"):
                conn = sqlite3.connect(path)
                for sql in SCHEMA:
                    conn.execute(sql)
                conn.commit()
                return conn

            def test_saves_conversation_and_messages():
                conn = fresh()
                cid = save_chat(conn, "Trip", [{"role": "user", "content": "Train times?"},
                                               {"role": "assistant", "content": "Hourly."}])
                assert conn.execute("SELECT title FROM conversations WHERE id = ?", (cid,)).fetchone() == ("Trip",)
                got = conn.execute("SELECT conversation_id, role, content FROM messages ORDER BY id").fetchall()
                assert got == [(cid, "user", "Train times?"), (cid, "assistant", "Hourly.")], f"got {got!r}"

            def test_returns_new_ids():
                conn = fresh()
                first = save_chat(conn, "A", [])
                second = save_chat(conn, "B", [{"role": "user", "content": "x"}])
                assert isinstance(first, int) and first != second, f"got {first!r}, {second!r}"
                got = conn.execute("SELECT conversation_id FROM messages").fetchall()
                assert got == [(second,)], f"got {got!r}"

            def test_bad_role_raises_and_saves_nothing():
                conn = fresh()
                try:
                    save_chat(conn, "Bad", [{"role": "user", "content": "a"}, {"role": "robot", "content": "b"}])
                except ValueError:
                    pass
                else:
                    assert False, "expected ValueError for role 'robot'"
                convs = conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
                msgs = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
                assert (convs, msgs) == (0, 0), f"left behind {convs} conversation(s) and {msgs} message(s)"

            def test_success_is_committed_for_other_connections():
                conn = fresh("chat.db")
                save_chat(conn, "Saved", [{"role": "user", "content": "persist"}])
                other = sqlite3.connect("chat.db")
                got = other.execute("SELECT content FROM messages").fetchall()
                assert got == [("persist",)], f"another connection sees {got!r}"
        ''',
        "solution": r'''
            ALLOWED_ROLES = ("system", "user", "assistant")

            def save_chat(conn, title, messages):
                with conn:
                    cur = conn.execute("INSERT INTO conversations (title) VALUES (?)", (title,))
                    conversation_id = cur.lastrowid
                    for message in messages:
                        if message["role"] not in ALLOWED_ROLES:
                            raise ValueError(f"bad role: {message['role']}")
                        conn.execute(
                            "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
                            (conversation_id, message["role"], message["content"]),
                        )
                return conversation_id
        ''',
        "hints": [
            "Use `with conn:` around all the inserts, and `cursor.lastrowid` for the new id.",
            "Insert the conversation first, keep its id, then insert each message. If a role is bad, raise inside the `with` block so everything is rolled back.",
            "Open `with conn:`; run the conversation INSERT and save `cur.lastrowid`; loop over messages, raise ValueError if the role is not allowed, otherwise INSERT with `?` params; return the id after the block.",
        ],
    },
    {
        "id": "sql-11",
        "title": "Paginate the history",
        "difficulty": 1,
        "lesson": r'''
            ## LIMIT and OFFSET

            A chat app with 10,000 messages does not load them all at once. It reads one page at a
            time. Splitting a result into pages of a fixed size is called **pagination**.

            `LIMIT n` returns at most `n` rows. `OFFSET k` skips the first `k` rows before `LIMIT`
            counts. `LIMIT 3 OFFSET 6` skips 6 rows and returns the next 3.

            With 3 rows per page, page 1 skips 0 rows, page 2 skips 3 rows and page 3 skips 6 rows.
            Page `page` skips `(page - 1) * per_page` rows.

            ```python
            import sqlite3

            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE t (n INTEGER)")
            conn.executemany("INSERT INTO t VALUES (?)", [(i,) for i in range(1, 11)])
            per_page = 3
            for page in (1, 2, 4, 5):
                skip = (page - 1) * per_page
                rows = conn.execute("SELECT n FROM t ORDER BY n LIMIT ? OFFSET ?", (per_page, skip)).fetchall()
                print(page, skip, rows)
            # 1 0 [(1,), (2,), (3,)]
            # 2 3 [(4,), (5,), (6,)]
            # 4 9 [(10,)]
            # 5 12 []
            ```

            The table has 10 rows. Page 4 has only one row left, so the last page is shorter. Page 5
            starts after the last row, so the result is an empty list. No error is raised.

            Always use `ORDER BY` with pages. Without a fixed order, the same row can appear on two
            pages or on none.
        ''',
        "prompt": r'''
            Return one page of the chat history.

            **Write:** `get_page(conn, page, per_page)`

            - `conn`: an open connection with a table `messages (id INTEGER PRIMARY KEY, role TEXT, content TEXT)`
            - `page`: an `int`, the page number, **starting at 1**
            - `per_page`: an `int`, how many messages per page (at least 1)
            - **Returns:** a `list` of `str`: the `content` of the messages on that page, in `id` order

            **Rules**
            - Page 1 is the first `per_page` messages, page 2 the next `per_page`, and so on.
            - A page past the end returns `[]`; the last page may be shorter.
            - If `page` is less than 1, raise `ValueError`.

            **Examples**
            ```python
            # contents in id order: "m1", "m2", "m3", "m4", "m5"
            get_page(conn, 1, 2)   # returns ["m1", "m2"]
            get_page(conn, 3, 2)   # returns ["m5"]
            get_page(conn, 4, 2)   # returns []
            get_page(conn, 0, 2)   # raises ValueError
            ```
        ''',
        "research": {
            "note": "Skim the LIMIT and OFFSET part of SQLite's SELECT documentation, then come back.",
            "links": [{"title": "SELECT (see the LIMIT clause) - SQLite docs",
                       "url": "https://www.sqlite.org/lang_select.html"}],
        },
        "starter": r'''
            def get_page(conn, page, per_page):
                ...
        ''',
        "tests": r'''
            import sqlite3
            from solution import get_page

            def fresh(n=5):
                conn = sqlite3.connect(":memory:")
                conn.execute("CREATE TABLE messages (id INTEGER PRIMARY KEY, role TEXT, content TEXT)")
                conn.executemany("INSERT INTO messages (role, content) VALUES (?, ?)",
                                 [("user", f"m{i}") for i in range(1, n + 1)])
                return conn

            def test_first_page():
                got = get_page(fresh(), 1, 2)
                assert got == ["m1", "m2"], f"got {got!r}"

            def test_second_page():
                got = get_page(fresh(), 2, 2)
                assert got == ["m3", "m4"], f"got {got!r}"

            def test_last_page_can_be_shorter():
                got = get_page(fresh(), 3, 2)
                assert got == ["m5"], f"got {got!r}"

            def test_page_past_the_end_is_empty():
                got = get_page(fresh(), 4, 2)
                assert got == [], f"got {got!r}"

            def test_page_below_one_raises_value_error():
                try:
                    get_page(fresh(), 0, 2)
                except ValueError:
                    return
                assert False, "expected ValueError for page 0"
        ''',
        "solution": r'''
            def get_page(conn, page, per_page):
                if page < 1:
                    raise ValueError("page starts at 1")
                offset = (page - 1) * per_page
                rows = conn.execute(
                    "SELECT content FROM messages ORDER BY id LIMIT ? OFFSET ?", (per_page, offset)
                ).fetchall()
                return [row[0] for row in rows]
        ''',
        "hints": [
            "LIMIT is how many rows to take; OFFSET is how many to skip first.",
            "For a 1-based page number, the number of rows to skip is (page - 1) times per_page. Check the page number before querying.",
            "Raise ValueError if page < 1; compute offset = (page - 1) * per_page; SELECT content ... ORDER BY id LIMIT ? OFFSET ? with (per_page, offset); return the first item of each row.",
        ],
    },
    {
        "id": "sql-12",
        "title": "Rows as dicts",
        "difficulty": 1,
        "lesson": r'''
            ## Rows with column names

            A tuple row gives you values by position only. You have to know that item `1` is the role.
            For a JSON API you usually want dicts with the column names as keys.

            A **row factory** is a setting on the connection that decides which object each row
            becomes. Set `conn.row_factory = sqlite3.Row` to get `sqlite3.Row` objects.

            ```python
            import json
            import sqlite3

            conn = sqlite3.connect(":memory:")
            conn.row_factory = sqlite3.Row
            conn.execute("CREATE TABLE docs (title TEXT, words INTEGER)")
            conn.execute("INSERT INTO docs VALUES ('FAQ', 300)")
            row = conn.execute("SELECT title, words FROM docs").fetchone()
            print(row["title"], row[1])
            # FAQ 300
            print(json.dumps(dict(row)))
            # {"title": "FAQ", "words": 300}
            ```

            You can read a `sqlite3.Row` by column name or by position. `dict(row)` builds a real dict
            from it.

            Without a row factory, you can read the column names from the cursor. `cur.description` has
            one tuple per selected column, and item `0` of each tuple is the column name. In the
            query, `words AS n` gives the column the new name `n` in the result.

            ```python
            import sqlite3

            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE docs (title TEXT, words INTEGER)")
            cur = conn.execute("SELECT title, words AS n FROM docs")
            print(cur.description[0][0], cur.description[1][0])
            # title n
            ```

            A `sqlite3.Row` is not a dict. `json.dumps(row)` raises
            `TypeError: Object of type Row is not JSON serializable`. Convert it with `dict(row)` first.
        ''',
        "prompt": r'''
            Your API layer needs query results as JSON-ready dicts, not tuples.

            **Write:** `fetch_dicts(conn, query, params=())`

            - `conn`: an open `sqlite3` connection
            - `query`: a `str`, a `SELECT` statement (may contain `?` placeholders)
            - `params`: a `tuple` of values for the placeholders (default: empty)
            - **Returns:** a `list` of real `dict`s, one per row, keys are the column names

            **Rules**
            - Keys follow the names in the query, including aliases (`SUM(x) AS total` gives the key `"total"`).
            - Each item must be a plain `dict` (so `json.dumps` works on the list).
            - No rows gives `[]`.

            **Examples**
            ```python
            fetch_dicts(conn, "SELECT role, content FROM messages WHERE role = ?", ("user",))
            # returns [{"role": "user", "content": "Hi"}]
            fetch_dicts(conn, "SELECT COUNT(*) AS n FROM messages")   # returns [{"n": 2}]
            ```
        ''',
        "starter": r'''
            def fetch_dicts(conn, query, params=()):
                ...
        ''',
        "tests": r'''
            import json
            import sqlite3
            from solution import fetch_dicts

            def fresh():
                conn = sqlite3.connect(":memory:")
                conn.execute("CREATE TABLE messages (role TEXT, content TEXT)")
                conn.executemany("INSERT INTO messages VALUES (?, ?)", [("user", "Hi"), ("assistant", "Hey")])
                return conn

            def test_rows_become_dicts_with_column_names():
                got = fetch_dicts(fresh(), "SELECT role, content FROM messages WHERE role = ?", ("user",))
                assert got == [{"role": "user", "content": "Hi"}], f"got {got!r}"

            def test_alias_becomes_the_key():
                got = fetch_dicts(fresh(), "SELECT COUNT(*) AS n FROM messages")
                assert got == [{"n": 2}], f"got {got!r}"

            def test_items_are_plain_dicts_and_json_serialisable():
                got = fetch_dicts(fresh(), "SELECT role FROM messages")
                assert all(type(item) is dict for item in got), f"got types {[type(i) for i in got]}"
                json.dumps(got)

            def test_no_rows_returns_empty_list():
                got = fetch_dicts(fresh(), "SELECT role FROM messages WHERE role = ?", ("tool",))
                assert got == [], f"got {got!r}"
        ''',
        "solution": r'''
            def fetch_dicts(conn, query, params=()):
                cur = conn.execute(query, params)
                names = [col[0] for col in cur.description]
                return [dict(zip(names, row)) for row in cur.fetchall()]
        ''',
        "hints": [
            "The cursor knows the column names: look at `cursor.description` (or use sqlite3.Row).",
            "Get the list of column names once, then pair each row's values with those names.",
            "Run the query with params and keep the cursor; names = [col[0] for col in cur.description]; build `dict(zip(names, row))` for every row.",
        ],
    },
    # ------------------------------------------------------------------ difficulty 2
    {
        "id": "sql-13",
        "title": "Usage report",
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            Build the usage report behind an "AI spend" dashboard.

            **Write:** `usage_report(conn)`

            - `conn`: an open connection with a table `usage (model TEXT, input_tokens INTEGER, output_tokens INTEGER)`
              (one row per API call)
            - **Returns:** a `list` of dicts, one per model:
              `{"model": str, "calls": int, "input_tokens": int, "output_tokens": int}`

            **Rules**
            - `calls` is the number of rows for that model; the token fields are sums.
            - Sort by total tokens (input + output) from most to least; ties by model name A to Z.
            - An empty table gives `[]`.

            **Examples**
            ```python
            # rows: ("gpt", 100, 20), ("claude", 50, 10), ("gpt", 30, 5), ("mistral", 40, 20)
            usage_report(conn)
            # returns [{"model": "gpt", "calls": 2, "input_tokens": 130, "output_tokens": 25},
            #          {"model": "claude", "calls": 1, "input_tokens": 50, "output_tokens": 10},
            #          {"model": "mistral", "calls": 1, "input_tokens": 40, "output_tokens": 20}]
            ```
        ''',
        "starter": r'''
            def usage_report(conn):
                ...
        ''',
        "tests": r'''
            import sqlite3
            from solution import usage_report

            def fresh(rows):
                conn = sqlite3.connect(":memory:")
                conn.execute("CREATE TABLE usage (model TEXT, input_tokens INTEGER, output_tokens INTEGER)")
                conn.executemany("INSERT INTO usage VALUES (?, ?, ?)", rows)
                return conn

            def test_report_with_tie_broken_by_name():
                got = usage_report(fresh([("gpt", 100, 20), ("claude", 50, 10), ("gpt", 30, 5), ("mistral", 40, 20)]))
                assert got == [
                    {"model": "gpt", "calls": 2, "input_tokens": 130, "output_tokens": 25},
                    {"model": "claude", "calls": 1, "input_tokens": 50, "output_tokens": 10},
                    {"model": "mistral", "calls": 1, "input_tokens": 40, "output_tokens": 20},
                ], f"got {got!r}"

            def test_sorted_by_total_not_by_input_only():
                got = usage_report(fresh([("a", 10, 100), ("b", 50, 0)]))
                assert [r["model"] for r in got] == ["a", "b"], f"got {got!r}"

            def test_empty_table():
                got = usage_report(fresh([]))
                assert got == [], f"got {got!r}"
        ''',
        "solution": r'''
            def usage_report(conn):
                sql = """
                    SELECT model, COUNT(*), SUM(input_tokens), SUM(output_tokens)
                    FROM usage
                    GROUP BY model
                    ORDER BY SUM(input_tokens + output_tokens) DESC, model ASC
                """
                return [
                    {"model": m, "calls": c, "input_tokens": i, "output_tokens": o}
                    for m, c, i, o in conn.execute(sql)
                ]
        ''',
        "hints": [
            "One GROUP BY query can produce every number; ORDER BY can sort by an aggregate.",
            "Group by model, select COUNT(*) and the two SUMs, and sort by the sum of both token columns descending, then model.",
            "SELECT model, COUNT(*), SUM(input_tokens), SUM(output_tokens) ... GROUP BY model ORDER BY SUM(input_tokens + output_tokens) DESC, model; then build one dict per row.",
        ],
    },
    {
        "id": "sql-14",
        "title": "Keyword search",
        "difficulty": 2,
        "prompt": r'''
            A simple keyword search over stored documents (the "keyword" half of a search system).

            **Write:** `search_documents(conn, word, limit=5)`

            - `conn`: an open connection with a table `documents (id INTEGER PRIMARY KEY, title TEXT, body TEXT)`
            - `word`: a `str` to look for
            - `limit`: an `int`, the maximum number of results (default `5`)
            - **Returns:** a `list` of `str` titles of documents whose **body** contains `word`
              anywhere, ignoring upper/lower case

            **Rules**
            - Sort the titles A to Z, and return at most `limit` of them.
            - `word` is passed as a `?` parameter (it comes from a user); use SQL's `LIKE`.
            - If `word` is empty or only spaces, raise `ValueError`.
            - Surrounding spaces in `word` are ignored (`"  refund "` searches for `"refund"`).

            **Examples**
            ```python
            # bodies: "Refund policy..." (title "Refunds"), "How to get a REFUND" (title "FAQ"), "Shipping" (title "Ship")
            search_documents(conn, "refund")            # returns ["FAQ", "Refunds"]
            search_documents(conn, "refund", limit=1)   # returns ["FAQ"]
            search_documents(conn, "   ")               # raises ValueError
            ```
        ''',
        "starter": r'''
            def search_documents(conn, word, limit=5):
                ...
        ''',
        "tests": r'''
            import sqlite3
            from solution import search_documents

            def fresh():
                conn = sqlite3.connect(":memory:")
                conn.execute("CREATE TABLE documents (id INTEGER PRIMARY KEY, title TEXT, body TEXT)")
                conn.executemany("INSERT INTO documents (title, body) VALUES (?, ?)", [
                    ("Refunds", "Refund policy: 30 days."),
                    ("FAQ", "How to get a REFUND fast"),
                    ("Ship", "Shipping takes 3 days"),
                    ("Refund title only", "nothing here"),
                ])
                return conn

            def test_finds_matches_case_insensitively_sorted():
                got = search_documents(fresh(), "refund")
                assert got == ["FAQ", "Refunds"], f"got {got!r}"

            def test_searches_body_not_title():
                got = search_documents(fresh(), "nothing")
                assert got == ["Refund title only"], f"got {got!r}"

            def test_limit_is_applied():
                got = search_documents(fresh(), "refund", limit=1)
                assert got == ["FAQ"], f"got {got!r}"

            def test_surrounding_spaces_ignored():
                got = search_documents(fresh(), "  days ")
                assert got == ["Refunds", "Ship"], f"got {got!r}"

            def test_quote_in_word_is_safe():
                got = search_documents(fresh(), "it's")
                assert got == [], f"got {got!r}"

            def test_blank_word_raises_value_error():
                for bad in ("", "   "):
                    try:
                        search_documents(fresh(), bad)
                    except ValueError:
                        continue
                    assert False, f"expected ValueError for {bad!r}"
        ''',
        "solution": r'''
            def search_documents(conn, word, limit=5):
                word = word.strip()
                if not word:
                    raise ValueError("search word is empty")
                rows = conn.execute(
                    "SELECT title FROM documents WHERE body LIKE ? ORDER BY title LIMIT ?",
                    ("%" + word + "%", limit),
                ).fetchall()
                return [row[0] for row in rows]
        ''',
        "hints": [
            "`LIKE` with `%` wildcards matches text anywhere in a column, and is case-insensitive for ASCII in SQLite.",
            "Clean the word first, reject it if empty, then put the % signs around it in Python and pass that as the parameter.",
            "Strip the word; raise ValueError if nothing is left; run `SELECT title FROM documents WHERE body LIKE ? ORDER BY title LIMIT ?` with `(\"%\" + word + \"%\", limit)`; return the titles.",
        ],
    },
    {
        "id": "sql-15",
        "title": "Conversations with zero messages",
        "difficulty": 2,
        "prompt": r'''
            List every conversation with its message count - including brand-new conversations
            that have no messages yet.

            **Write:** `conversation_stats(conn)`

            - `conn`: an open connection with tables
              `conversations (id INTEGER PRIMARY KEY, title TEXT)` and
              `messages (id INTEGER PRIMARY KEY, conversation_id INTEGER, role TEXT, content TEXT)`
            - **Returns:** a `list` of `(title, count)` tuples, one per conversation

            **Rules**
            - Conversations without messages appear with count `0`.
            - Sort by count, most first; ties by title A to Z.
            - No conversations gives `[]`.

            **Examples**
            ```python
            # conversations: (1, "Refund"), (2, "Recipe"), (3, "Empty")
            # messages: two in conversation 2, one in conversation 1
            conversation_stats(conn)   # returns [("Recipe", 2), ("Refund", 1), ("Empty", 0)]
            ```
        ''',
        "starter": r'''
            def conversation_stats(conn):
                ...
        ''',
        "tests": r'''
            import sqlite3
            from solution import conversation_stats

            def fresh(convs, msgs):
                conn = sqlite3.connect(":memory:")
                conn.execute("CREATE TABLE conversations (id INTEGER PRIMARY KEY, title TEXT)")
                conn.execute("CREATE TABLE messages (id INTEGER PRIMARY KEY, conversation_id INTEGER, role TEXT, content TEXT)")
                conn.executemany("INSERT INTO conversations VALUES (?, ?)", convs)
                conn.executemany("INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)", msgs)
                return conn

            def test_counts_include_empty_conversations():
                conn = fresh([(1, "Refund"), (2, "Recipe"), (3, "Empty")],
                             [(2, "user", "a"), (1, "user", "b"), (2, "assistant", "c")])
                got = conversation_stats(conn)
                assert got == [("Recipe", 2), ("Refund", 1), ("Empty", 0)], f"got {got!r}"

            def test_ties_sorted_by_title():
                conn = fresh([(1, "b"), (2, "a"), (3, "c")], [(1, "user", "x"), (2, "user", "y")])
                got = conversation_stats(conn)
                assert got == [("a", 1), ("b", 1), ("c", 0)], f"got {got!r}"

            def test_no_conversations():
                got = conversation_stats(fresh([], []))
                assert got == [], f"got {got!r}"
        ''',
        "solution": r'''
            def conversation_stats(conn):
                sql = """
                    SELECT c.title, COUNT(m.id) AS n
                    FROM conversations c
                    LEFT JOIN messages m ON m.conversation_id = c.id
                    GROUP BY c.id
                    ORDER BY n DESC, c.title ASC
                """
                return [(title, n) for title, n in conn.execute(sql)]
        ''',
        "lesson": r'''
            ## LEFT JOIN

            A plain `JOIN` returns only the pairs of rows that match. A conversation with no messages
            has no pair, so it is missing from the result.

            `LEFT JOIN` keeps **every** row of the table on its left. When no row of the right table
            matches, the right table's columns are `NULL` in that result row.

            `COUNT(m.id)` counts only the rows where `m.id` is not `NULL`, so a conversation without
            messages gets `0`. `COUNT(*)` counts rows, so it would count that `NULL` row as `1`.
        ''',
        "hints": [
            "An ordinary JOIN drops conversations that have no messages. Which JOIN keeps them?",
            "LEFT JOIN messages onto conversations, group by conversation, and count a messages column (not *) so missing messages count as 0.",
            "FROM conversations c LEFT JOIN messages m ON m.conversation_id = c.id GROUP BY c.id, SELECT c.title and COUNT(m.id), ORDER BY the count DESC then title; return tuples.",
        ],
    },
    {
        "id": "sql-16",
        "title": "Safe sort column",
        "difficulty": 2,
        "prompt": r'''
            An admin page lets users choose how to sort the documents list. `?` placeholders only
            work for **values**, not for column names or `ASC`/`DESC` - so those must be checked
            against an allow-list before they go into the SQL text.

            **Write:** `list_documents(conn, order_by="title", descending=False)`

            - `conn`: an open connection with a table `documents (title TEXT, score REAL, created_at TEXT)`
            - `order_by`: a `str`, the column to sort by
            - `descending`: a `bool`, `True` for largest/latest first
            - **Returns:** a `list` of `str` titles, sorted as requested

            **Rules**
            - Allowed `order_by` values: exactly `"title"`, `"score"`, `"created_at"`.
            - Anything else (e.g. `"score; DROP TABLE documents"` or `"body"`) raises `ValueError`
              and the query is never run.
            - Ties are broken by title A to Z (whatever the direction).

            **Examples**
            ```python
            # rows: ("b", 0.5, "2026-01-02"), ("a", 0.9, "2026-01-03"), ("c", 0.5, "2026-01-01")
            list_documents(conn)                          # returns ["a", "b", "c"]
            list_documents(conn, "score", True)           # returns ["a", "b", "c"]
            list_documents(conn, "created_at")            # returns ["c", "b", "a"]
            list_documents(conn, "score; DROP TABLE x")   # raises ValueError
            ```
        ''',
        "starter": r'''
            def list_documents(conn, order_by="title", descending=False):
                ...
        ''',
        "tests": r'''
            import sqlite3
            from solution import list_documents

            def fresh():
                conn = sqlite3.connect(":memory:")
                conn.execute("CREATE TABLE documents (title TEXT, score REAL, created_at TEXT)")
                conn.executemany("INSERT INTO documents VALUES (?, ?, ?)", [
                    ("b", 0.5, "2026-01-02"), ("a", 0.9, "2026-01-03"), ("c", 0.5, "2026-01-01")])
                return conn

            def test_default_is_title_ascending():
                got = list_documents(fresh())
                assert got == ["a", "b", "c"], f"got {got!r}"

            def test_score_descending_ties_by_title():
                got = list_documents(fresh(), "score", True)
                assert got == ["a", "b", "c"], f"got {got!r}"

            def test_score_ascending_ties_by_title():
                got = list_documents(fresh(), "score", False)
                assert got == ["b", "c", "a"], f"got {got!r}"

            def test_created_at_both_directions():
                assert list_documents(fresh(), "created_at") == ["c", "b", "a"]
                assert list_documents(fresh(), "created_at", True) == ["a", "b", "c"]

            def test_unknown_column_raises_and_table_survives():
                conn = fresh()
                for bad in ("body", "score; DROP TABLE documents", "title DESC"):
                    try:
                        list_documents(conn, bad)
                    except ValueError:
                        continue
                    assert False, f"expected ValueError for {bad!r}"
                assert conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0] == 3
        ''',
        "solution": r'''
            ALLOWED = ("title", "score", "created_at")

            def list_documents(conn, order_by="title", descending=False):
                if order_by not in ALLOWED:
                    raise ValueError(f"cannot sort by {order_by!r}")
                direction = "DESC" if descending else "ASC"
                sql = f"SELECT title FROM documents ORDER BY {order_by} {direction}, title ASC"
                return [row[0] for row in conn.execute(sql)]
        ''',
        "hints": [
            "Check the column name against a fixed list before building any SQL.",
            "Once the name is known to be one of the allowed ones, it is safe to put it (and ASC/DESC chosen by your own code) into the SQL text.",
            "Raise ValueError if order_by is not in the allowed tuple; pick \"DESC\" or \"ASC\" from `descending`; build `ORDER BY <col> <dir>, title ASC` and return the titles.",
        ],
    },
    # ------------------------------------------------------------------ difficulty 3
    {
        "id": "sql-17",
        "title": "A chat store class",
        "difficulty": 3,
        "prompt": r'''
            Wrap the database behind a small class, the way a real chat app would.

            **Write:** a class `ChatStore`

            - `ChatStore(path=":memory:")`: opens a connection to `path` and creates the tables it
              needs if they don't exist (your choice of schema). Opening the same file twice must work.
            - `new_conversation(title)`: stores a conversation, returns its id (`int`)
            - `add(conversation_id, role, content, tokens=0)`: stores one message; returns nothing
            - `history(conversation_id)`: returns a `list` of dicts `{"role": ..., "content": ...}`
              for that conversation, in the order they were added
            - `total_tokens(conversation_id)`: returns an `int`, the sum of `tokens` of its messages

            **Rules**
            - `add` with an id that has no conversation raises `ValueError`.
            - `history` / `total_tokens` of a conversation with no messages give `[]` / `0`.
            - Conversations are separate: one's messages never appear in another's history.
            - Every write is committed: a second `ChatStore` on the same file sees it.
            - Use `?` parameters for every value.

            **Examples**
            ```python
            store = ChatStore()
            cid = store.new_conversation("Trip")
            store.add(cid, "user", "Train times?", tokens=5)
            store.add(cid, "assistant", "Every hour.", tokens=4)
            store.history(cid)        # [{"role": "user", "content": "Train times?"},
                                      #  {"role": "assistant", "content": "Every hour."}]
            store.total_tokens(cid)   # 9
            store.add(999, "user", "hi")   # raises ValueError
            ```
        ''',
        "starter": r'''
            import sqlite3


            class ChatStore:
                def __init__(self, path=":memory:"):
                    ...
        ''',
        "tests": r'''
            from solution import ChatStore

            def test_history_in_order():
                store = ChatStore()
                cid = store.new_conversation("Trip")
                store.add(cid, "user", "Train times?", tokens=5)
                store.add(cid, "assistant", "Every hour.", tokens=4)
                got = store.history(cid)
                assert got == [{"role": "user", "content": "Train times?"},
                               {"role": "assistant", "content": "Every hour."}], f"got {got!r}"

            def test_total_tokens_and_default_zero():
                store = ChatStore()
                cid = store.new_conversation("Trip")
                store.add(cid, "user", "a", tokens=5)
                store.add(cid, "assistant", "b", tokens=4)
                store.add(cid, "user", "c")
                assert store.total_tokens(cid) == 9, f"got {store.total_tokens(cid)!r}"

            def test_empty_conversation():
                store = ChatStore()
                cid = store.new_conversation("New")
                assert store.history(cid) == [], f"got {store.history(cid)!r}"
                got = store.total_tokens(cid)
                assert got == 0, f"got {got!r}"

            def test_conversations_are_separate():
                store = ChatStore()
                a = store.new_conversation("A")
                b = store.new_conversation("B")
                assert a != b, "each conversation needs its own id"
                store.add(a, "user", "only in A", tokens=1)
                store.add(b, "user", "only in B", tokens=2)
                assert store.history(a) == [{"role": "user", "content": "only in A"}]
                assert store.total_tokens(b) == 2

            def test_unknown_conversation_raises_value_error():
                store = ChatStore()
                try:
                    store.add(999, "user", "hi")
                except ValueError:
                    return
                assert False, "expected ValueError"

            def test_data_is_committed_to_the_file():
                first = ChatStore("chat.db")
                cid = first.new_conversation("Saved")
                first.add(cid, "user", "persist me", tokens=3)
                second = ChatStore("chat.db")
                assert second.history(cid) == [{"role": "user", "content": "persist me"}]
                assert second.total_tokens(cid) == 3

            def test_uses_placeholders():
                assert "?" in source(), "use ? placeholders for values"
        ''',
        "solution": r'''
            import sqlite3


            class ChatStore:
                def __init__(self, path=":memory:"):
                    self.conn = sqlite3.connect(path)
                    with self.conn:
                        self.conn.execute(
                            "CREATE TABLE IF NOT EXISTS conversations (id INTEGER PRIMARY KEY, title TEXT)"
                        )
                        self.conn.execute(
                            "CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, "
                            "conversation_id INTEGER, role TEXT, content TEXT, tokens INTEGER)"
                        )

                def new_conversation(self, title):
                    with self.conn:
                        cur = self.conn.execute("INSERT INTO conversations (title) VALUES (?)", (title,))
                    return cur.lastrowid

                def add(self, conversation_id, role, content, tokens=0):
                    found = self.conn.execute(
                        "SELECT 1 FROM conversations WHERE id = ?", (conversation_id,)
                    ).fetchone()
                    if found is None:
                        raise ValueError(f"no conversation {conversation_id}")
                    with self.conn:
                        self.conn.execute(
                            "INSERT INTO messages (conversation_id, role, content, tokens) VALUES (?, ?, ?, ?)",
                            (conversation_id, role, content, tokens),
                        )

                def history(self, conversation_id):
                    rows = self.conn.execute(
                        "SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY id",
                        (conversation_id,),
                    )
                    return [{"role": role, "content": content} for role, content in rows]

                def total_tokens(self, conversation_id):
                    row = self.conn.execute(
                        "SELECT COALESCE(SUM(tokens), 0) FROM messages WHERE conversation_id = ?",
                        (conversation_id,),
                    ).fetchone()
                    return row[0]
        ''',
        "hints": [
            "Keep the connection on `self`, create tables with CREATE TABLE IF NOT EXISTS, and commit every write (`with self.conn:`).",
            "Two tables: conversations and messages (with conversation_id and tokens). `add` first checks the conversation exists with a SELECT.",
            "In __init__ connect and create both tables; new_conversation inserts and returns lastrowid; add SELECTs the id (ValueError if fetchone() is None) then INSERTs; history SELECTs role, content WHERE conversation_id = ? ORDER BY id; total_tokens uses COALESCE(SUM(tokens), 0).",
        ],
    },
]
