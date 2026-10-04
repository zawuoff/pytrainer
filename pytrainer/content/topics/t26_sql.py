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
            ## A table that remembers

            A chat app has to keep every message. A Python list forgets everything when the program stops.
            A JSON file remembers, but to find one message you load the whole file and search it with a
            loop of your own. With a hundred thousand messages, you would rather ask a question and get
            back only the lines that answer it.

            Picture the documents of a search tool on a sheet of paper, with a heading over each column:

            ```text
            title | pages
            ------+------
            FAQ   |     3
            Guide |    12
            ```

            A program that keeps data in sheets like this one, and searches them for you, is called a
            **database**. Each sheet is a **table**, each line of it is a **row**, and each heading names a
            **column**.

            Python comes with a small database called SQLite, in the module `sqlite3`. This program builds
            that table and reads it back:

            ```python
            import sqlite3

            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE docs (title TEXT, pages INTEGER)")
            conn.execute("INSERT INTO docs VALUES ('FAQ', 3)")
            conn.execute("INSERT INTO docs VALUES ('Guide', 12)")
            rows = conn.execute("SELECT title, pages FROM docs").fetchall()
            print(rows)
            # [('FAQ', 3), ('Guide', 12)]
            ```

            `sqlite3.connect(":memory:")` opens a new, empty database. `":memory:"` means that it lives in
            the computer's memory and is gone when the program ends, which suits experiments. What you get
            back is a **connection**: the object you send your instructions through.

            The text inside `conn.execute(...)` is not Python. It is **SQL**, the language that databases
            understand, and one instruction in SQL is a **statement**. Inside SQL, text goes in single
            quotes, as in `'FAQ'`. That is why the Python string around each statement uses double quotes.

            ```match
            `CREATE TABLE docs (...)` :: makes a new, empty table with the columns you list
            `INSERT INTO docs VALUES (...)` :: adds one row, with a value for each column in order
            `SELECT title, pages FROM docs` :: reads those two columns of every row
            ---
            `TEXT` and `INTEGER` say what kind of value each column holds. The next step looks at them.
            ```

            Each line of a program like this needs what the lines above it made. Put these lines in an
            order that prints `[('small', 4)]`:

            ```order
            import sqlite3
            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE models (name TEXT, price INTEGER)")
            conn.execute("INSERT INTO models VALUES ('small', 4)")
            print(conn.execute("SELECT name, price FROM models").fetchall())
            ---
            First the module, then the connection, then the table, then a row in it. Only then is there something to read. An `INSERT` that runs before the `CREATE TABLE` stops with `sqlite3.OperationalError: no such table: models`.
            ```

            ### What comes back

            `.fetchall()` after a `SELECT` hands the rows to Python as a list. Each row is a tuple, and its
            values are in the order in which the `SELECT` names the columns.

            ```quiz
            `rows` is `[('FAQ', 3), ('Guide', 12)]`. What is `rows[1][0]`?
            - [x] `'Guide'` :: Yes. `rows[1]` is the second row, the tuple `('Guide', 12)`, and `[0]` is the first value in it.
            - [ ] `'FAQ'` :: That is `rows[0][0]`. Counting starts at 0, so `rows[1]` is the second row.
            - [ ] `3` :: That is `rows[0][1]`. The first index picks the row, and the second index picks the value inside that row.
            - [ ] `12` :: That is `rows[1][1]`. Index `[0]` inside a row is the first column that the `SELECT` named, which is `title`.
            ```

            **Watch out:** without the single quotes, SQLite reads a word as the name of a column.
            `VALUES (FAQ, 3)` stops with `sqlite3.OperationalError: no such column: FAQ`.

            **In short:** you send SQL statements through a connection, and a `SELECT` followed by
            `.fetchall()` hands the rows back as a list of tuples.
        ''',
        "prompt": r'''
            Read the program in the editor. Type exactly what it prints, one line for each `print`.
        ''',
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
            Two `INSERT` statements ran, so the table holds two rows and `fetchall()` hands back a list of
            2 tuples. That makes `len(rows)` equal to `2`.

            `rows[0]` is the first row. The `SELECT` names `role` first and `content` second, so the tuple
            is `('user', 'Hi')`. When `print` shows a whole tuple, you see the brackets and the quotes.

            `rows[1]` is the second row, `('assistant', 'Hello!')`, and `[1]` picks the second value in it.
            When `print` shows one string, you see only its text: `Hello!`.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "`fetchall()` hands back a list with one tuple for each row. How many rows were put into the table?",
            "Each tuple holds its values in the order in which the `SELECT` names the columns: the role first, then the content. Printing a whole tuple shows the brackets and the quotes. Printing one string shows only its text.",
            "Your first line is the number of rows. Your second line is the whole first row, written the way Python prints a tuple. Your third line is one value: go to the second row, then to the second value in it.",
        ],
    },
    {
        "id": "sql-s2",
        "title": "Create a usage table",
        "difficulty": 0,
        "lesson": r'''
            ## A table of your own design

            A search tool keeps a record of every document it knows: its title, how many pages it has, and
            a score for how useful it was. Before the first document can be stored, the table has to exist,
            and you are the one who decides what it looks like.

            ```python
            import sqlite3

            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE docs (title TEXT, pages INTEGER, score REAL)")
            conn.execute("INSERT INTO docs VALUES ('FAQ', 3, 0.5)")
            print(conn.execute("SELECT title, pages, score FROM docs").fetchall())
            # [('FAQ', 3, 0.5)]
            ```

            After the words `CREATE TABLE` comes the name of the table. Then, in brackets, comes one entry
            for each column, with commas in between. An entry is the name of the column followed by the
            kind of value it holds, which SQL calls its **type**.

            ```match
            `TEXT` :: a string, such as `'FAQ'`
            `INTEGER` :: a whole number, such as `3`
            `REAL` :: a number with a decimal point, such as `0.5`
            ```

            The names are yours to choose. Once chosen, every later statement has to spell them exactly the
            same way. The table below was created with one column too few. Repair it:

            ```try
            import sqlite3
            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE models (name TEXT)")
            conn.execute("INSERT INTO models VALUES ('small', 8000)")
            print(conn.execute("SELECT name, max_tokens FROM models").fetchall())
            ---
            The program stops with `table models has 1 columns but 2 values were supplied`. Give the table a second column called `max_tokens` that holds whole numbers, so that the program prints `[('small', 8000)]`.
            ---
            import sqlite3
            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE models (name TEXT, max_tokens INTEGER)")
            conn.execute("INSERT INTO models VALUES ('small', 8000)")
            print(conn.execute("SELECT name, max_tokens FROM models").fetchall())
            ---
            The `INSERT` and the `SELECT` did not change. They only started to work once the table had a column with the name they use.
            ```

            ### A number for every row

            Two rows can hold exactly the same values, and then nothing tells them apart. So most tables
            get one more column, which numbers the rows:

            ```python
            import sqlite3

            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE docs (id INTEGER PRIMARY KEY, title TEXT)")
            conn.execute("INSERT INTO docs (title) VALUES ('FAQ')")
            conn.execute("INSERT INTO docs (title) VALUES ('Guide')")
            print(conn.execute("SELECT id, title FROM docs").fetchall())
            # [(1, 'FAQ'), (2, 'Guide')]
            ```

            This `INSERT` names the columns it brings values for: `(title)`. It brings nothing for `id`,
            so SQLite fills that column in by itself: 1 for the first row, 2 for the next. A column whose
            value is different in every row is called a **primary key**, and `INTEGER PRIMARY KEY` asks
            SQLite to hand out the numbers.

            ```quiz
            A program runs `CREATE TABLE docs (title TEXT)`. A few lines later it runs the same statement again. What happens the second time?
            - [x] The program stops with an error :: Right. SQLite refuses to create a table that is already there: `sqlite3.OperationalError: table docs already exists`.
            - [ ] The old table is thrown away and an empty one takes its place :: `CREATE TABLE` never removes anything. It stops with an error, and the old table and its rows stay as they were.
            - [ ] Nothing happens, because the table is already there :: That would be convenient, but plain `CREATE TABLE` stops with an error when the name is taken.
            ```

            A program that may be started many times on the same database writes
            `CREATE TABLE IF NOT EXISTS docs (...)`. That statement creates the table only when it is
            missing.

            **Watch out:** SQLite does not guess at names. After `CREATE TABLE docs`, a statement that
            says `documents` stops with `sqlite3.OperationalError: no such table: documents`.

            **In short:** `CREATE TABLE name (column TYPE, ...)` creates an empty table, and every later
            statement must use exactly those names.
        ''',
        "prompt": r'''
            An AI app pays for every call to a model, and the price depends on the number of tokens. To
            see where the money goes, the app writes down every call: which model answered, how many tokens
            went in, and how many came out. Those records need a table.

            **Your job:** finish `create_usage_table(conn)` so that it creates that table. The statement is
            already written except for two gaps, each marked `___`. One gap is the name of the table and
            the other is the name of a column.

            **What goes in**
            - `conn`: an open connection to a database that has no tables yet

            **What comes out**
            - nothing. The function has no `return` line. Its result is the new, empty table in the
              database.

            **Rules**
            - The table is called `usage`.
            - It has three columns, in this order: `model` (text), `input_tokens` (a whole number) and
              `output_tokens` (a whole number).
            - The names must match letter for letter. The checks read the table under exactly these names.

            **Examples**
            ```python
            conn = sqlite3.connect(":memory:")
            create_usage_table(conn)
            conn.execute("INSERT INTO usage VALUES ('gpt-4o-mini', 120, 40)")
            conn.execute("SELECT model, input_tokens, output_tokens FROM usage").fetchall()
            # returns [('gpt-4o-mini', 120, 40)]
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
            "Look at the first example in the lesson. What comes directly after the words `CREATE TABLE`, and what stands in front of each type?",
            "The first gap is the place where the table gets its name. The second gap is the place where a column gets its name. Both names are in the Rules of the task.",
            "The Rules list three columns in order. Two of them are already written in the statement, and the gap between them is for the one that is missing. Names inside SQL are written without quotes.",
        ],
    },
    {
        "id": "sql-s3",
        "title": "Fix the unsafe insert",
        "difficulty": 0,
        "lesson": r'''
            ## A value from outside, stored safely

            So far you typed every value into the SQL yourself, as in `VALUES ('FAQ', 3)`. In a real app
            the value arrives in a variable. A visitor types a note, and your program has to store whatever
            they typed.

            The first idea is an f-string that pastes the value into the SQL text:

            ```python
            text = "It's done"
            sql = f"INSERT INTO notes (author, text) VALUES ('guest', '{text}')"
            print(sql)
            # INSERT INTO notes (author, text) VALUES ('guest', 'It's done')
            ```

            Look at the apostrophe in `It's`. To SQLite it is a single quote, and a single quote ends a
            piece of text.

            ```quiz
            What happens when `conn.execute(sql)` sends that statement to SQLite?
            - [x] The program stops with an error :: Right. The text ends after `It`. What follows, `s done')`, is not SQL, so SQLite stops with `sqlite3.OperationalError: near "s": syntax error`.
            - [ ] The note is stored as `It's done` :: Python knows where the note ends, but SQLite only receives the finished text. In that text the apostrophe closes the quote after `It`.
            - [ ] The note is stored as `It` :: SQLite does not keep the part it could read. A statement that it cannot read to the end fails as a whole, and nothing is stored.
            ```

            ### Keep the values out of the text

            Write a `?` in each place where a value belongs. Then pass the values in a tuple, as a second
            argument of `execute`:

            ```python
            import sqlite3

            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE notes (author TEXT, text TEXT)")
            text = "It's done"
            conn.execute("INSERT INTO notes (author, text) VALUES (?, ?)", ("guest", text))
            print(conn.execute("SELECT author, text FROM notes").fetchall())
            # [('guest', "It's done")]
            ```

            SQLite now receives two separate things: the statement with its two question marks, and the
            values. The first value goes to the first `?` and the second value to the second. A value that
            arrives this way is stored as data and is never read as SQL, so its apostrophe is an ordinary
            character. A `?` in a statement is called a **placeholder**, and the values in the tuple are
            the **parameters** of the statement.

            ```fill
            import sqlite3
            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE notes (author TEXT, text TEXT)")
            author = "ada"
            text = "Ship it"
            conn.execute("INSERT INTO notes (author, text) VALUES (?, ?)", ___)
            print(conn.execute("SELECT author, text FROM notes").fetchall())
            ---
            - [x] (author, text) :: Right. One tuple with a value for each `?`, in the order of the question marks. The program prints `[('ada', 'Ship it')]`.
            - [ ] (text, author) :: The values go to the question marks in order, so this stores the note as the author and the author as the note: `[('Ship it', 'ada')]`.
            - [ ] author, text :: Without the brackets these are two more arguments, and `execute` takes the SQL and one collection of values: `TypeError: execute expected at most 2 arguments, got 3`.
            ```

            ### Not only apostrophes

            An apostrophe is an accident. The same gap can be used on purpose. One `INSERT` may add several
            rows, each in its own brackets, and this visitor knows it:

            ```python
            import sqlite3

            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE notes (author TEXT, text TEXT)")
            typed = "hi'), ('boss', 'give the guest a raise"
            conn.execute(f"INSERT INTO notes (author, text) VALUES ('guest', '{typed}')")
            print(conn.execute("SELECT author, text FROM notes").fetchall())
            # [('guest', 'hi'), ('boss', 'give the guest a raise')]
            ```

            The typed text closed your quote and your bracket and then added a second row. The table now
            holds a note that the boss never wrote. Getting a database to run SQL that a user typed is
            called **SQL injection**.

            ```quiz
            The same `typed` text is stored with `VALUES (?, ?)` and the tuple `("guest", typed)`. How many rows does the table hold afterwards?
            - [x] One :: Right. The whole typed text, with its quotes and brackets, is stored as the note of `guest`. A parameter is never read as SQL.
            - [ ] Two :: That is what the f-string caused, because there the typed text became part of the statement. A parameter stays a value.
            - [ ] None, because the quotes in the text cause an error :: A parameter may hold any characters. Only text that is pasted into the statement can break it.
            ```

            **Watch out:** a placeholder has no quotes around it. `'?'` is the text of a question mark, so
            `VALUES ('?', '?')` with two parameters stops with `sqlite3.ProgrammingError: Incorrect number
            of bindings supplied. The current statement uses 0, and there are 2 supplied.`

            **In short:** never paste a value into SQL text. Write `?` in the statement and pass the values
            in a tuple.
        ''',
        "prompt": r'''
            A chat app saves every message in a table. The function that does the saving pastes its two
            values into the SQL text with an f-string. That works for `Hello`. It crashes for `It's fine`,
            and a user who types the right text can change what the statement does.

            **Your job:** fix `add_message(conn, role, content)` so that the two values no longer become
            part of the SQL text. The code is already in the editor.

            **What goes in**
            - `conn`: an open connection to a database that already has the table
              `messages (role TEXT, content TEXT)`
            - `role`: who wrote the message, a string such as `"user"`
            - `content`: the text of the message, a string. It may contain any characters.

            **What comes out**
            - nothing. The function has no `return` line. Its result is one new row in `messages`.

            **Rules**
            - Each call adds exactly one row, with `role` and `content` stored exactly as they were given.
            - An apostrophe, as in `It's fine`, is stored as part of the text.
            - Text that looks like SQL is stored as plain text too. One check stores
              `x'); DROP TABLE messages; --` and reads it back. (`DROP TABLE` is the SQL statement that
              deletes a whole table.)
            - One check reads your code. The SQL must contain `?` placeholders, and `{role}` and
              `{content}` must be gone from it.

            **Examples**
            ```python
            add_message(conn, "user", "Hello")
            add_message(conn, "user", "It's fine")
            conn.execute("SELECT role, content FROM messages").fetchall()
            # returns [("user", "Hello"), ("user", "It's fine")]
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
            "The lesson shows two ways to get a value into a statement: pasted into the text, or sent next to it. Which of the two does the code in the editor use?",
            "The SQL text should hold a mark in each place where a value belongs, and nothing of the values themselves. The values travel separately, as a second argument of `execute`.",
            "Make the SQL an ordinary string, without the `f` in front. Replace each of the two `{...}` parts with one placeholder mark, and take away the single quotes around it as well. After the string, add a comma and one tuple that holds the two values in the same order as the marks.",
        ],
    },
    {
        "id": "sql-s4",
        "title": "Unpack the rows",
        "difficulty": 0,
        "lesson": r'''
            ## Plain values out of the rows

            A menu in the search tool should list the title of every document. You ask the database for the
            titles, and what comes back is not quite a list of titles:

            ```python
            import sqlite3

            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE docs (id INTEGER PRIMARY KEY, title TEXT, words INTEGER)")
            conn.execute("INSERT INTO docs (title, words) VALUES ('FAQ', 300)")
            conn.execute("INSERT INTO docs (title, words) VALUES ('Guide', 1200)")
            rows = conn.execute("SELECT title FROM docs ORDER BY id").fetchall()
            print(rows)
            # [('FAQ',), ('Guide',)]
            ```

            You asked for one column, but every row is still a tuple. It is a tuple with a single item, and
            Python writes a one-item tuple with a comma after the item: `('FAQ',)`. So `rows` is a list of
            tuples, not a list of strings.

            The query ends with `ORDER BY id`. That hands the rows back sorted by their `id` number, which
            counts up from 1, so they come in the order in which they were saved. A later step explains
            sorting properly.

            Before you fix this, check that you can read the shape of the result:

            ```predict
            import sqlite3

            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE notes (id INTEGER PRIMARY KEY, text TEXT)")
            conn.execute("INSERT INTO notes (text) VALUES ('call Ada')")
            conn.execute("INSERT INTO notes (text) VALUES ('buy milk')")
            rows = conn.execute("SELECT text FROM notes ORDER BY id").fetchall()
            print(len(rows))
            print(rows[1])
            print(rows[1][0])
            ---
            Two notes were saved, so `fetchall()` gives a list of 2 tuples and `len(rows)` is `2`. `rows[1]` is the second tuple, shown with its brackets, quotes and comma: `('buy milk',)`. The extra `[0]` takes the one item out of that tuple, and `print` shows a string as plain text: `buy milk`.
            ```

            ### Taking the value out

            To get plain strings, take item 0 out of every row. You already know how to build a new list
            from an old one, with a list comprehension. A table with no rows has nothing to take out, so
            the new list is empty too:

            ```python
            import sqlite3

            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE docs (id INTEGER PRIMARY KEY, title TEXT)")
            conn.execute("CREATE TABLE trash (id INTEGER PRIMARY KEY, title TEXT)")
            conn.execute("INSERT INTO docs (title) VALUES ('FAQ')")
            conn.execute("INSERT INTO docs (title) VALUES ('Guide')")
            for sql in ("SELECT title FROM docs ORDER BY id", "SELECT title FROM trash ORDER BY id"):
                rows = conn.execute(sql).fetchall()
                print([row[0] for row in rows])
            # ['FAQ', 'Guide']
            # []
            ```

            This program prints tuples where it should print names. Repair it:

            ```try
            import sqlite3

            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE tags (id INTEGER PRIMARY KEY, name TEXT)")
            conn.execute("INSERT INTO tags (name) VALUES ('python')")
            conn.execute("INSERT INTO tags (name) VALUES ('sql')")
            rows = conn.execute("SELECT name FROM tags ORDER BY id").fetchall()
            names = []
            for row in rows:
                names.append(row)
            print(names)
            ---
            The program prints `[('python',), ('sql',)]`. Change one line so that it prints `['python', 'sql']`.
            ---
            import sqlite3

            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE tags (id INTEGER PRIMARY KEY, name TEXT)")
            conn.execute("INSERT INTO tags (name) VALUES ('python')")
            conn.execute("INSERT INTO tags (name) VALUES ('sql')")
            rows = conn.execute("SELECT name FROM tags ORDER BY id").fetchall()
            names = []
            for row in rows:
                names.append(row[0])
            print(names)
            ---
            `row` is the whole tuple. `row[0]` is the one item inside it, so that is what the list should collect.
            ```

            ### Two columns

            When the query names two columns, every row has two items. A `for` loop can **unpack** each row:
            it gives each item its own name, the way you unpacked pairs in the chapter on variables.

            ```python
            import sqlite3

            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE docs (id INTEGER PRIMARY KEY, title TEXT, words INTEGER)")
            conn.execute("INSERT INTO docs (title, words) VALUES ('FAQ', 300)")
            conn.execute("INSERT INTO docs (title, words) VALUES ('Guide', 1200)")
            rows = conn.execute("SELECT title, words FROM docs ORDER BY id").fetchall()
            for title, words in rows:
                print(title, "has", words, "words")
            # FAQ has 300 words
            # Guide has 1200 words
            ```

            Step through the loop to watch `title` and `words` change from one row to the next.

            ```diagram
            {"type": "trace", "title": "Unpacking each row of rows", "code": ["rows = [(\"FAQ\", 300), (\"Guide\", 1200)]", "for title, words in rows:", "    print(title, \"has\", words, \"words\")"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 2, "vars": {"rows": "[('FAQ', 300), ('Guide', 1200)]"}, "out": ""},
              {"line": 3, "vars": {"rows": "[('FAQ', 300), ('Guide', 1200)]", "title": "'FAQ'", "words": "300"}, "out": ""},
              {"line": 2, "vars": {"rows": "[('FAQ', 300), ('Guide', 1200)]", "title": "'FAQ'", "words": "300"}, "out": "FAQ has 300 words\n"},
              {"line": 3, "vars": {"rows": "[('FAQ', 300), ('Guide', 1200)]", "title": "'Guide'", "words": "1200"}, "out": "FAQ has 300 words\n"},
              {"line": 2, "vars": {"rows": "[('FAQ', 300), ('Guide', 1200)]", "title": "'Guide'", "words": "1200"}, "out": "FAQ has 300 words\nGuide has 1200 words\n"},
              {"line": null, "vars": {"rows": "[('FAQ', 300), ('Guide', 1200)]", "title": "'Guide'", "words": "1200"}, "out": "FAQ has 300 words\nGuide has 1200 words\n"}
            ]}
            ```

            **Watch out:** a query for one column does not give plain strings. If you hand back `rows` as it
            is, your list holds tuples, and `['FAQ'] == [('FAQ',)]` is `False`.

            **In short:** `fetchall()` always gives a list of tuples, so take the item out of each row
            (`row[0]` for the first column) when you want plain values.
        ''',
        "prompt": r'''
            A search tool shows the text of every saved chat message on a page. The database hands each
            message back inside a tuple, and the page wants plain strings.

            **Your job:** write `all_contents(conn)`, which gives back the text of every message in the table
            as a plain list of strings.

            **What goes in**
            - `conn`: an open connection to a database with a table `messages` that has the columns `id` (a
              whole number that counts up from 1), `role` (who wrote the message, such as `"user"`) and
              `content` (the text of the message)

            **What comes out**
            - a list of strings: the `content` of every row, in order of `id`, so the oldest message comes
              first. For example `["Hi", "Hello!"]`.

            **Rules**
            - The list holds plain strings, not tuples.
            - A table with no rows gives an empty list.

            **Examples**
            ```python
            # the table holds: (1, "user", "Hi"), (2, "assistant", "Hello!")
            all_contents(conn)     # returns ["Hi", "Hello!"]
            # the table holds no rows
            all_contents(conn)     # returns []
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
            "Think about the first example in the lesson. When a query asks for one column, what does each row look like? Your list needs the thing inside each row, not the row.",
            "Ask the database for only the column you need, with the rows in `id` order, and fetch all of them. Then build a new list that holds one item taken out of each row. A table with no rows needs no special case.",
            "In order: write a query that names only the content column and ends with the sorting clause for `id`; collect every row with the method that returns all of them; build the list with a comprehension that takes the item at position 0 of each row; return that list.",
        ],
    },
    {
        "id": "sql-s5",
        "title": "Filter with WHERE",
        "difficulty": 0,
        "lesson": r'''
            ## Only the rows you ask for

            A chat holds hundreds of messages, and you want only the ones the user wrote. You could fetch
            every message and filter them with a loop. With a hundred thousand messages it is better to tell
            the database what you want and let it send back only those rows.

            You do that with `WHERE` and a condition, the same kind of question an `if` asks:

            ```python
            import sqlite3

            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE docs (id INTEGER PRIMARY KEY, title TEXT, pages INTEGER)")
            conn.execute("INSERT INTO docs (title, pages) VALUES ('FAQ', 3)")
            conn.execute("INSERT INTO docs (title, pages) VALUES ('Guide', 12)")
            conn.execute("INSERT INTO docs (title, pages) VALUES ('Manual', 40)")
            rows = conn.execute("SELECT title FROM docs WHERE pages > 10 ORDER BY id").fetchall()
            print(rows)
            # [('Guide',), ('Manual',)]
            ```

            The database tests `pages > 10` on every row and keeps the rows where it is true. A part of a
            statement that starts with a keyword, such as `WHERE` or `ORDER BY`, is called a **clause**.
            `WHERE` comes before `ORDER BY`.

            The comparisons are `=`, `!=`, `<`, `>`, `<=` and `>=`. In SQL a single `=` asks "are these
            equal?" and nothing is assigned. On text, `=` is exact: `'faq'` is not equal to `'FAQ'`.

            ```predict
            import sqlite3

            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE docs (id INTEGER PRIMARY KEY, title TEXT, pages INTEGER)")
            conn.execute("INSERT INTO docs (title, pages) VALUES ('FAQ', 3)")
            conn.execute("INSERT INTO docs (title, pages) VALUES ('Guide', 12)")
            conn.execute("INSERT INTO docs (title, pages) VALUES ('Manual', 40)")
            print(conn.execute("SELECT title FROM docs WHERE pages <= 12 ORDER BY id").fetchall())
            print(conn.execute("SELECT title FROM docs WHERE title = 'manual' ORDER BY id").fetchall())
            print(conn.execute("SELECT title FROM docs WHERE title != 'FAQ' ORDER BY id").fetchall())
            ---
            `pages <= 12` keeps FAQ (3 pages) and Guide (12 pages): 12 is not above 12, so Guide stays. `=` compares text exactly and `'manual'` is not `'Manual'`, so no row passes and the answer is an empty list `[]`. `!=` keeps every row except the one titled FAQ.
            ```

            ### A value from a variable

            Remember the `?` placeholder from the unsafe-insert step. It works in `WHERE` too, and the
            values travel in a tuple:

            ```fill
            import sqlite3

            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE docs (id INTEGER PRIMARY KEY, title TEXT, pages INTEGER)")
            conn.execute("INSERT INTO docs (title, pages) VALUES ('FAQ', 3)")
            conn.execute("INSERT INTO docs (title, pages) VALUES ('Guide', 12)")
            limit = 5
            rows = conn.execute("SELECT title FROM docs WHERE pages > ? ORDER BY id", ___).fetchall()
            print(rows)
            ---
            - [x] (limit,) :: Right. A tuple with one item, written with a comma. It fills the one `?`, and the program prints `[('Guide',)]`.
            - [ ] (limit) :: Brackets around one name do not make a tuple. `execute` receives the number 5 itself and stops with `sqlite3.ProgrammingError: parameters are of unsupported type`.
            - [ ] ("limit",) :: That is a tuple, but it holds the text `limit`, not the number 5. No page count is above a piece of text, so the program prints `[]`.
            ```

            ### Part of a text

            `=` needs the whole text. To find rows whose text contains something, use `LIKE` with a pattern.
            In a pattern, `%` stands for any amount of any characters, even none. `LIKE` also ignores the
            difference between `a` and `A`. The pattern goes in as a parameter like any other value, for
            example `("%an%",)`.

            ```match
            `title = 'Guide'` :: titles that are exactly Guide
            `title LIKE '%ide%'` :: titles that contain ide anywhere
            `title LIKE 'G%'` :: titles that start with G
            `title LIKE '%de'` :: titles that end with de
            ```

            **Watch out:** `("user")` is only the text `"user"` in brackets, not a tuple. `sqlite3` then
            treats each of its four letters as a separate value and stops with `sqlite3.ProgrammingError:
            Incorrect number of bindings supplied. The current statement uses 1, and there are 4 supplied.`
            Write `("user",)`.

            **In short:** `WHERE condition` keeps only the rows where the condition is true, and a value
            from Python goes in through a `?` and a tuple.
        ''',
        "prompt": r'''
            A chat app stores every message together with the role of its writer: `"system"`, `"user"` or
            `"assistant"`. A page that shows only what the user typed needs just those messages.

            **Your job:** finish `messages_by_role(conn, role)`, which gives back the text of the messages
            written by one role. The function is already in the editor. The end of its SQL statement is
            missing, marked `___`: it must keep only the right rows.

            **What goes in**
            - `conn`: an open connection to a database with a table `messages` that has the columns `id` (a
              whole number that counts up from 1), `role` (text) and `content` (text)
            - `role`: the role to look for, for example `"user"`

            **What comes out**
            - a list of strings: the `content` of every message written by that role, in order of `id`

            **Rules**
            - Only messages whose `role` is exactly the given role come back.
            - If no message has that role, the list is empty.
            - The role reaches the database through the placeholder. The editor already passes it in a tuple.

            **Examples**
            ```python
            # the table holds: (1, "system", "Be brief"), (2, "user", "Hi"), (3, "assistant", "Hey"), (4, "user", "Bye")
            messages_by_role(conn, "user")     # returns ["Hi", "Bye"]
            messages_by_role(conn, "tool")     # returns []
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
            "Look at the first example in the lesson. Which keyword starts the part of a statement that keeps only some of the rows?",
            "The gap needs a condition that compares one column with the value that arrives through the placeholder. The tuple after the statement holds that value. If you also want the rows kept in `id` order, remember that the filtering clause comes before the sorting clause.",
            "Write the name of the column that holds the writer, then the SQL sign that asks whether two things are equal (one sign, not two), then the placeholder. Do not put quotes around the placeholder.",
        ],
    },
    {
        "id": "sql-s6",
        "title": "Top documents",
        "difficulty": 0,
        "lesson": r'''
            ## The best few, first

            A search finds two hundred documents and gives each one a score. The page has room for the best
            three. Python could sort all two hundred and cut the list, but the database can sort for you and
            hand over just three.

            ```python
            import sqlite3

            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE models (name TEXT, price REAL)")
            conn.execute("INSERT INTO models VALUES ('small', 0.5)")
            conn.execute("INSERT INTO models VALUES ('large', 8.0)")
            conn.execute("INSERT INTO models VALUES ('medium', 2.0)")
            print(list(conn.execute("SELECT name FROM models ORDER BY price")))
            # [('small',), ('medium',), ('large',)]
            print(list(conn.execute("SELECT name FROM models ORDER BY price DESC")))
            # [('large',), ('medium',), ('small',)]
            ```

            `ORDER BY price` sorts the rows by that column, smallest first. Smallest first is called
            **ascending** (`ASC`), and it is the default. Writing `DESC`, short for **descending**, turns
            the order around: largest first. Text sorts from A to Z.

            To keep only the first few rows, add `LIMIT`. SQLite sorts first and cuts afterwards, and
            `LIMIT` always comes last. The number may be a `?` placeholder like any other value.

            ```try
            import sqlite3

            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE models (name TEXT, price REAL)")
            conn.execute("INSERT INTO models VALUES ('small', 0.5)")
            conn.execute("INSERT INTO models VALUES ('large', 8.0)")
            conn.execute("INSERT INTO models VALUES ('medium', 2.0)")
            print(list(conn.execute("SELECT name FROM models ORDER BY price")))
            ---
            The program lists every model, cheapest first. Change the SQL so that it prints only the two most expensive models, the dearest first: `[('large',), ('medium',)]`.
            ---
            import sqlite3

            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE models (name TEXT, price REAL)")
            conn.execute("INSERT INTO models VALUES ('small', 0.5)")
            conn.execute("INSERT INTO models VALUES ('large', 8.0)")
            conn.execute("INSERT INTO models VALUES ('medium', 2.0)")
            print(list(conn.execute("SELECT name FROM models ORDER BY price DESC LIMIT 2")))
            ---
            Two changes were needed. `DESC` puts the dearest model first, and `LIMIT 2` keeps the first two rows of that sorted list. If the table held fewer than two rows, you would simply get fewer.
            ```

            ### When two rows tie

            Two models can cost the same. After `ORDER BY price DESC` you may list a second column, and
            SQLite looks at it only for rows that are equal in the first. The second column has its own
            direction, and `ASC` is the default there too.

            ```quiz
            A table of models has the columns `name` and `price`. Which ending lists the dearest models first and puts models with the same price in A to Z order?
            - [x] `ORDER BY price DESC, name` :: Yes. The rows are sorted by price, largest first, and `name` (A to Z) is used only to decide between rows that have the same price.
            - [ ] `ORDER BY price, name DESC` :: This sorts by price with the smallest first, because `DESC` belongs to `name` only. Equal prices then come back in Z to A order.
            - [ ] `ORDER BY name, price DESC` :: This sorts by name first. The price is used only to decide between rows that have exactly the same name.
            ```

            **Watch out:** the default is `ASC`, smallest first. If you ask for the best rows and forget
            `DESC`, you get the worst ones, and with `LIMIT` the right rows are cut off without any error.

            **In short:** `ORDER BY column DESC` sorts the largest first, and `LIMIT n` keeps the first `n`
            rows of the sorted result.
        ''',
        "prompt": r'''
            A search step has scored some documents, and the results page has room for only the best few.

            **Your job:** write `top_documents(conn, n)`, which gives back the titles of the `n`
            best-scoring documents, best first.

            **What goes in**
            - `conn`: an open connection to a database with a table `documents` that has the columns `title`
              (text) and `score` (a decimal number; a higher score is better)
            - `n`: how many titles you want, a whole number that is 0 or more, for example `2`

            **What comes out**
            - a list of strings: the titles of the `n` documents with the highest scores, the highest score
              first. For example `["blog", "guide"]`.

            **Rules**
            - If two documents have the same score, the one whose title comes first in the alphabet goes
              first.
            - If the table holds fewer than `n` documents, all of them come back.
            - `n = 0` gives an empty list.

            **Examples**
            ```python
            # the table holds: ("faq", 0.4), ("guide", 0.9), ("api", 0.7), ("blog", 0.9)
            top_documents(conn, 2)     # returns ["blog", "guide"]
            top_documents(conn, 10)    # returns ["blog", "guide", "api", "faq"]
            top_documents(conn, 0)     # returns []
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
            "You need two things from the lesson: a way to sort the rows by the score, and a way to keep only the first few rows of the sorted result. Which two clauses did the lesson use for them?",
            "Sort by score from the highest to the lowest. Name a second sorting column to settle ties by title in alphabetical order. Then cap the number of rows, with the number coming from `n` through a placeholder.",
            "In order: ask for the title column only; sort by score in descending order and then by title; end with the limit, passing `n` in a one-item tuple; fetch all the rows; build the list of plain strings from them, as you did in the step on unpacking rows.",
        ],
    },
    # ------------------------------------------------------------------ difficulty 1
    {
        "id": "sql-7",
        "title": "Total tokens used",
        "difficulty": 1,
        "lesson": r'''
            ## Ask the database for one total

            A table has one row for each request, but your dashboard needs a single number. You do not have to transfer every row to Python before adding it up. SQL can calculate the summary while reading the table.

            ```python
            import sqlite3
            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE jobs (pages INTEGER)")
            conn.executemany("INSERT INTO jobs VALUES (?)", [(4,), (7,)])
            print(next(conn.execute("SELECT COUNT(*), SUM(pages) FROM jobs")))
            # (2, 11)
            conn.execute("DELETE FROM jobs")
            print(next(conn.execute("SELECT COUNT(*), SUM(pages) FROM jobs")))
            # (0, None)
            ```

            A function that combines values from many rows is an **aggregate**. `COUNT(*)` counts rows and `SUM` adds the selected values. Other aggregates include `MIN`, `MAX`, and `AVG`. A query selecting only aggregates without grouping produces one summary row.

            `fetchone` returns that row as a tuple. Even one selected summary is still wrapped in a row, so distinguish the row from the scalar number your caller wants.

            ```quiz
            An empty table produces a SUM value of None in Python. Does this mean the query returned no row?
            - [x] No :: The summary row exists, but its sum is SQL NULL, represented by Python None.
            - [ ] Yes :: The row and the value inside it are different levels of the result.
            ```

            SQL `NULL` represents an absent value. Summing zero rows produces NULL, unlike Python's `sum` of an empty iterable. `COALESCE(value, fallback)` selects the first non-NULL value and can supply the output your interface requires.

            ```predict
            import sqlite3
            conn = sqlite3.connect(":memory:")
            print(next(conn.execute("SELECT COALESCE(NULL, 0), COALESCE(5, 0)")))
            ---
            The fallback is used only for NULL, so the row contains zero and five. An existing non-NULL value is retained.
            ```

            **Watch out:** use an aggregate over each row's intended calculation. Summing only one column silently omits the other part of a total.

            **In short:** aggregates summarize rows, and empty sums need an explicit absent-value policy.
        ''',
        "prompt": r'''
            Work out how many tokens the app has used in total, across all calls.

            **Your job:** write `total_tokens(conn)`

            **What goes in**

            - `conn`: an open connection with a table `usage (model TEXT, input_tokens INTEGER, output_tokens INTEGER)`

            **What comes out**
            - an `int`: the sum of `input_tokens` plus `output_tokens` over all rows

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
            "Which aggregate can summarize the value contributed by every row?",
            "Calculate the row contribution from both token columns, and decide how an empty aggregate should become zero.",
            "Run an aggregate query, handle its NULL result with a fallback, and extract the scalar from the returned summary row.",
        ],
    },
    {
        "id": "sql-8",
        "title": "Tokens per model",
        "difficulty": 1,
        "lesson": r'''
            ## Calculate a separate total for each category

            One overall total hides which jobs used the resources. You want a total for each category even when rows for that category are scattered throughout the table.

            ```python
            import sqlite3
            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE jobs (kind TEXT, pages INTEGER)")
            conn.executemany("INSERT INTO jobs VALUES (?, ?)", [("scan", 4), ("print", 2), ("scan", 7)])
            query = "SELECT kind, SUM(pages) FROM jobs GROUP BY kind ORDER BY kind"
            print(conn.execute(query).fetchall())
            # [('print', 2), ('scan', 11)]
            ```

            `GROUP BY` gathers rows sharing the chosen value into a group. The aggregate is calculated separately for every group, so the result has one row per category. The two scan rows contribute to one total even though another kind lies between them in the input.

            ```quiz
            A table contains five rows but only two distinct category names. How many rows does grouping by category produce?
            - [x] Two :: One result row represents each distinct grouping value.
            - [ ] Five :: That would still be one row per input, without combining groups.
            - [ ] One :: A single overall summary would omit the grouping.
            ```

            Every selected value should identify the group or summarize it. Selecting an unrelated column in SQLite can produce a value from an unspecified member row, which is rarely the report you meant.

            After grouping, each result tuple can become one dictionary entry or one report record. An empty table has no groups, so the grouped result has no rows. This differs from an ungrouped aggregate query's single summary row.

            ```match
            WHERE :: filters individual rows before grouping
            GROUP BY :: chooses which rows share a summary
            HAVING :: filters groups using their summary values
            ```

            **Watch out:** a condition on a group's sum belongs in HAVING, not WHERE. The sum does not exist at the earlier row-filtering stage.

            **In short:** group by the category, summarize within each group, and shape each result row for your caller.
        ''',
        "prompt": r'''
            Build a per-model token bill.

            **Your job:** write `tokens_by_model(conn)`

            **What goes in**

            - `conn`: an open connection with a table `usage (model TEXT, input_tokens INTEGER, output_tokens INTEGER)`

            **What comes out**
            - a `dict` mapping each model name (`str`) to its total tokens (`int`,
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
            "An overall aggregate needs one additional clause to produce a summary per category.",
            "Group by model while adding both token fields within each group.",
            "Select the model identifier and its aggregate total, then convert the result rows into dictionary entries. With no groups, the result should naturally be empty.",
        ],
    },
    {
        "id": "sql-9",
        "title": "Join conversations and messages",
        "difficulty": 1,
        "lesson": r'''
            ## Combine related rows from two tables

            A document title is stored once, while several notes refer to that document. To display a readable note list, you need the title and note text together without duplicating the title in storage.

            ```python
            import sqlite3
            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE docs (id INTEGER, title TEXT)")
            conn.execute("CREATE TABLE notes (doc_id INTEGER, text TEXT)")
            conn.execute("INSERT INTO docs VALUES (7, 'Guide')")
            conn.execute("INSERT INTO notes VALUES (7, 'Review this')")
            query = "SELECT d.title, n.text FROM notes n JOIN docs d ON d.id = n.doc_id"
            print(conn.execute(query).fetchall())
            # [('Guide', 'Review this')]
            ```

            `JOIN` pairs rows according to the `ON` condition. Here a note's stored document identifier chooses the corresponding document. A column referring to another table's identifying column is commonly called a **foreign key**. Enforcing that relationship requires the appropriate database constraint and settings; the join itself does not enforce it.

            The short names `d` and `n` are **aliases**. They let the query name each table's columns clearly without repeating the whole table name.

            ```quiz
            Both tables contain an id column. What does qualifying it as d.id accomplish?
            - [x] It selects the document table's id :: The prefix removes ambiguity about which table supplies the column.
            - [ ] It changes the stored column name :: An alias affects the query's references, not the table schema.
            ```

            Select the values the output needs, then order the result by the field promised to the caller. A join does not guarantee insertion order. If the output follows note order, sorting by document title instead would regroup it incorrectly.

            ```match
            JOIN :: combines matching rows
            ON :: states the matching relationship
            ORDER BY :: makes the result order explicit
            ```

            **Watch out:** an unqualified shared column name can raise `sqlite3.OperationalError: ambiguous column name`. Use the table alias wherever the source could be unclear.

            **In short:** join through the stored relationship, qualify shared names, and order the combined result explicitly.
        ''',
        "prompt": r'''
            Build a readable transcript of every stored message, labelled with its conversation title.

            **Your job:** write `transcript_lines(conn)`

            **What goes in**

            - `conn`: an open connection with two tables:
              `conversations (id INTEGER PRIMARY KEY, title TEXT)` and
              `messages (id INTEGER PRIMARY KEY, conversation_id INTEGER, role TEXT, content TEXT)`

            **What comes out**
            - a `list` of `str`, one per message, formatted `"<title> | <role>: <content>"`

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
            "Each output line needs data from two tables linked by a stored identifier.",
            "Join along the conversation relationship and choose message order rather than conversation order.",
            "Select the title, role, and content from matched rows, order by the message identifier, and format each result using the exact required separators.",
        ],
    },
    {
        "id": "sql-10",
        "title": "Save a chat, all or nothing",
        "difficulty": 1,
        "lesson": r'''
            ## Save related changes together or not at all

            Saving a record and its related details takes several inserts. If a later insert fails, leaving the earlier ones behind would create an incomplete result. You need those changes to succeed as one unit.

            ```python
            import sqlite3
            database = sqlite3.connect(":memory:")
            database.execute("CREATE TABLE jobs (label TEXT)")
            try:
                with database:
                    database.execute("INSERT INTO jobs VALUES ('draft')")
                    raise ValueError("invalid details")
            except ValueError:
                print("not saved")
            print(database.execute("SELECT COUNT(*) FROM jobs").fetchone())
            # not saved
            # (0,)
            ```

            A group of changes saved together is a **transaction**. A **commit** makes its changes permanent. A **rollback** discards its pending changes. With the standard connection behavior used here, `with database` commits on normal exit and rolls back when an exception leaves the block.

            ```quiz
            You catch and suppress a validation error inside the with block. What danger does that create?
            - [x] The block may finish normally and commit incomplete changes :: The context manager must see the failure to trigger its rollback behavior.
            - [ ] The connection is automatically closed :: The connection context manager handles transactions, not closing.
            ```

            The exception continues after rollback, so callers still know the operation failed. Place handling outside the transaction block when you want to report failure after its changes have been undone.

            An insert returns a cursor. Its `lastrowid` records the generated row identifier, allowing later inserts to refer to the newly stored parent row. Keep that identifier for the return value too.

            ```match
            commit :: saves pending transaction changes
            rollback :: discards pending transaction changes
            lastrowid :: identifies the row just inserted through the cursor
            ```

            **Watch out:** a connection may already contain pending work. Transaction boundaries cover that pending work too; this exercise uses a connection prepared for the operation's transaction.

            **In short:** keep related writes in one transaction and let failures leave the block so they roll back together.
        ''',
        "prompt": r'''
            Save a whole conversation (its title and its messages) so that either everything is
            saved, or nothing is.

            **Your job:** write `save_chat(conn, title, messages)`

            **What goes in**

            - `conn`: an open connection with tables
              `conversations (id INTEGER PRIMARY KEY, title TEXT)` and
              `messages (id INTEGER PRIMARY KEY, conversation_id INTEGER, role TEXT, content TEXT)`
            - `title`: a `str`
            - `messages`: a `list` of dicts like `{"role": "user", "content": "Hi"}`

            **What comes out**
            - the new conversation's `id` (an `int`)

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
            "Which mechanism makes several database changes succeed or fail together?",
            "Use one transaction for the conversation and all its messages, retaining the newly generated conversation id.",
            "Insert the parent, obtain its id, then validate and insert each message linked to that id. Let invalid roles raise out of the transaction block. Return the id only after successful commit.",
        ],
    },
    {
        "id": "sql-11",
        "title": "Paginate the history",
        "difficulty": 1,
        "lesson": r'''
            ## Read one page from an ordered result

            A long history should appear in manageable pages. You need to skip the rows shown earlier and take only the next page, while preserving a predictable ordering.

            ```python
            import sqlite3
            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE pages (number INTEGER)")
            conn.executemany("INSERT INTO pages VALUES (?)", [(1,), (2,), (3,), (4,), (5,)])
            query = "SELECT number FROM pages ORDER BY number LIMIT ? OFFSET ?"
            print(list(conn.execute(query, (2, 2))))
            # [(3,), (4,)]
            print(list(conn.execute(query, (2, 4))))
            # [(5,)]
            ```

            Dividing a result into pages is **pagination**. `LIMIT` is the maximum number of returned rows. `OFFSET` is how many ordered rows to skip first. The second example has only one remaining row, so returning a short final page is normal.

            For page numbers starting at one, the first page skips nothing. Each subsequent page skips one additional page's worth. Work from that relationship when converting a page number to an offset.

            ```predict
            per_page = 4
            for page in [1, 2, 3]:
                print((page - 1) * per_page)
            ---
            The pages skip zero, four, and eight rows. Subtracting one accounts for the first page having no earlier page.
            ```

            A page beyond the end returns no rows. This is different from an invalid page number: a valid but empty page should not raise an error unless your interface explicitly says so.

            ```quiz
            Why does a page query need ORDER BY?
            - [x] Pages need a defined row sequence :: Without it, the database makes no promise about which rows occupy a page.
            - [ ] LIMIT sorts rows automatically :: LIMIT only controls the amount, not the order.
            ```

            **Watch out:** multiplying the page number directly by page size skips the entire first page. Trace page one before testing later pages.

            **In short:** order the rows, skip earlier pages, and return at most one page of the remainder.
        ''',
        "prompt": r'''
            Return one page of the chat history.

            **Your job:** write `get_page(conn, page, per_page)`

            **What goes in**

            - `conn`: an open connection with a table `messages (id INTEGER PRIMARY KEY, role TEXT, content TEXT)`
            - `page`: an `int`, the page number, **starting at 1**
            - `per_page`: an `int`, how many messages per page (at least 1)

            **What comes out**
            - a `list` of `str`: the `content` of the messages on that page, in `id` order

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
            "Relate each page to the number of complete pages before it.",
            "Validate the page number, then use the page size for both the limit and calculation of how many rows to skip.",
            "Query contents in identifier order with the computed offset and limit. Extract each content value from its row, allowing a short or empty final result.",
        ],
    },
    {
        "id": "sql-12",
        "title": "Rows as dicts",
        "difficulty": 1,
        "lesson": r'''
            ## Give result values their column names

            A tuple such as `('Guide', 12)` does not tell an API caller what each position means. A dictionary can make that meaning explicit, using the names selected by the query itself.

            ```python
            import sqlite3
            conn = sqlite3.connect(":memory:")
            cursor = conn.execute("SELECT 'Guide' AS label, 12 AS pages")
            print([column[0] for column in cursor.description])
            # ['label', 'pages']
            print(cursor.fetchone())
            # ('Guide', 12)
            ```

            A cursor's `description` contains information for each result column. The first item in each column description is its name. These names follow the query's aliases, so `AS label` produces `label` even if the underlying table uses a different name.

            Pair those names with each row's values in the same order. The names belong to the result structure, so read them once rather than guessing field names from a particular query.

            ```predict
            names = ["label", "pages"]
            values = ("Guide", 12)
            print(dict(zip(names, values)))
            ---
            zip pairs corresponding positions. dict turns those name-value pairs into {'label': 'Guide', 'pages': 12}.
            ```

            Another option is a **row factory**, a connection setting controlling how result rows are represented. `sqlite3.Row` permits reading by name as well as position. It is still a specialized row object, not an ordinary dictionary. Converting it with `dict` makes the output suitable for JSON serialization when its values are JSON-compatible.

            ```quiz
            The query renames COUNT(*) to total. Which output dictionary key describes that result?
            - [x] total :: The selected column alias is the result's name.
            - [ ] COUNT(*) regardless of the alias :: That ignores the name the query explicitly requested.
            ```

            **Watch out:** changing a caller's connection row factory affects later queries too. Cursor metadata is useful when you want conversion without changing that shared setting.

            **In short:** read the query's column names and pair them with each row's ordered values.
        ''',
        "prompt": r'''
            Your API layer needs query results as JSON-ready dicts, not tuples.

            **Your job:** write `fetch_dicts(conn, query, params=())`

            **What goes in**

            - `conn`: an open `sqlite3` connection
            - `query`: a `str`, a `SELECT` statement (may contain `?` placeholders)
            - `params`: a `tuple` of values for the placeholders (default: empty)

            **What comes out**
            - a `list` of real `dict`s, one per row, keys are the column names

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
            "The selected column names are available even when the query returns no data rows.",
            "Use cursor metadata so aliases become keys automatically. Keep the supplied query parameters separate from SQL text.",
            "Execute and retain the cursor, read its column names in order, then pair those names with every row and create ordinary dictionaries.",
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

            **Your job:** write `usage_report(conn)`

            **What goes in**

            - `conn`: an open connection with a table `usage (model TEXT, input_tokens INTEGER, output_tokens INTEGER)`
              (one row per API call)

            **What comes out**
            - a `list` of dicts, one per model:
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
            "One grouped query can produce both a call count and separate token sums.",
            "Sorting must use both token columns together, with the model name as a secondary order.",
            "Collect each model's rows into a group, select the count and required sums, order by the full total descending and name ascending, then build the requested dictionary for each row.",
        ],
    },
    {
        "id": "sql-14",
        "title": "Keyword search",
        "difficulty": 2,
        "prompt": r'''
            A simple keyword search over stored documents (the "keyword" half of a search system).

            **Your job:** write `search_documents(conn, word, limit=5)`

            **What goes in**

            - `conn`: an open connection with a table `documents (id INTEGER PRIMARY KEY, title TEXT, body TEXT)`
            - `word`: a `str` to look for
            - `limit`: an `int`, the maximum number of results (default `5`)

            **What comes out**
            - a `list` of `str` titles of documents whose **body** contains `word`
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
            "LIKE can search a substring while placeholders keep user text separate from SQL structure.",
            "Trim the input before checking blankness, and bind the wildcard-bearing search value as data.",
            "Reject blank cleaned text, query body matches with the supplied pattern and limit parameters, sort by title, and extract only the titles.",
        ],
    },
    {
        "id": "sql-15",
        "title": "Conversations with zero messages",
        "difficulty": 2,
        "prompt": r'''
            List every conversation with its message count - including brand-new conversations
            that have no messages yet.

            **Your job:** write `conversation_stats(conn)`

            **What goes in**

            - `conn`: an open connection with tables
              `conversations (id INTEGER PRIMARY KEY, title TEXT)` and
              `messages (id INTEGER PRIMARY KEY, conversation_id INTEGER, role TEXT, content TEXT)`

            **What comes out**
            - a `list` of `(title, count)` tuples, one per conversation

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
            ## Keep parent records that have no children

            A report should show every folder, including empty ones. An ordinary join includes only matching folder-file pairs, so it silently drops empty folders. You need a join that keeps the parent even when there is no match.

            ```python
            import sqlite3
            conn = sqlite3.connect(":memory:")
            conn.execute("CREATE TABLE folders (id INTEGER, label TEXT)")
            conn.execute("CREATE TABLE files (id INTEGER, folder_id INTEGER)")
            conn.execute("INSERT INTO folders VALUES (1, 'empty'), (2, 'used')")
            conn.execute("INSERT INTO files VALUES (8, 2)")
            query = """SELECT f.label, COUNT(x.id) FROM folders f
            LEFT JOIN files x ON x.folder_id = f.id GROUP BY f.id ORDER BY f.label"""
            print(conn.execute(query).fetchall())
            # [('empty', 0), ('used', 1)]
            ```

            A **left join** preserves every row from the table written on its left. When no row on the right matches, the right-hand columns are NULL. This allows the empty parent to remain in the result without pretending a real child exists.

            ```quiz
            Why does COUNT of the child id give zero for an empty folder, while COUNT(*) would give one?
            - [x] Counting a column skips NULL values :: The preserved row exists, but its missing child id is NULL.
            - [ ] COUNT always subtracts one :: The difference comes from which values are counted, not a fixed adjustment.
            ```

            Putting it together means grouping by the parent's identifier, counting actual child identifiers, and ordering by the requested summary. The identifier matters: two distinct parents may have the same display name and should not be combined accidentally.

            If a condition on child data is added later, consider where it belongs. A WHERE condition that rejects NULL can remove the very empty parents the left join preserved. The matching condition and later filtering serve different purposes.

            **Watch out:** COUNT(*) counts the placeholder row for an unmatched parent. Count a non-NULL child identifier when the question is how many children exist.

            **In short:** left join keeps empty parents, and counting child identifiers gives their correct zero totals.
        ''',
        "hints": [
            "An ordinary join omits parents without matching children.",
            "Keep every conversation through a left join and count only actual message identifiers.",
            "Group by conversation identity, count the non-NULL child identifiers, and sort first by descending count then ascending title. Return each title-count pair.",
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

            **Your job:** write `list_documents(conn, order_by="title", descending=False)`

            **What goes in**

            - `conn`: an open connection with a table `documents (title TEXT, score REAL, created_at TEXT)`
            - `order_by`: a `str`, the column to sort by
            - `descending`: a `bool`, `True` for largest/latest first

            **What comes out**
            - a `list` of `str` titles, sorted as requested

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
            "Placeholders bind values, not SQL identifiers or ordering keywords.",
            "Validate the requested column against the fixed permitted names before constructing any query.",
            "Choose a direction from the Boolean input using fixed SQL words, combine it with the validated name, and always use ascending title order as the tie-break.",
        ],
    },
    # ------------------------------------------------------------------ difficulty 3
    {
        "id": "sql-17",
        "title": "A chat store class",
        "difficulty": 3,
        "prompt": r'''
            Wrap the database behind a small class, the way a real chat app would.

            **Your job:** write a class `ChatStore`

            **What goes in**

            - `ChatStore(path=":memory:")`: opens a connection to `path` and creates the tables it
              needs if they don't exist (your choice of schema). Opening the same file twice must work.
            - `new_conversation(title)`: stores a conversation, returns its id (`int`)
            - `add(conversation_id, role, content, tokens=0)`: stores one message; returns nothing
            - `history(conversation_id)`: returns a `list` of dicts `{"role": ..., "content": ...}`
              for that conversation, in the order they were added
            - `total_tokens(conversation_id)`: returns an `int`, the sum of `tokens` of its messages

            **What comes out**
            - New conversations give back their ids. History queries give ordered message dictionaries, token queries give integer totals, and writes persist for other connections.

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
            "Plan one method around each public operation, sharing a connection stored on the object.",
            "Store conversations separately from messages linked by their id. Commit writes and query each history using its conversation id.",
            "Create tables only if absent. Insert parents and return their generated ids. Validate parent existence before adding a parameterized message. Retrieve ordered history and an empty-safe token sum for the selected conversation.",
        ],
    },
]
