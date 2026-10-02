TOPIC = {
    "id": "chunking",
    "title": "Chunking Documents",
    "track": "rag",
    "order": 2,
    "requires": ["vectors"],
    "summary": """
        Cutting documents into pieces a retriever can find and a model can read: fixed-size
        chunks by characters and words, overlap, paragraph and sentence-aware splitting,
        metadata and offsets, heading context and token budgets.
    """,
    "concepts": ["why chunk", "fixed-size chunks", "ceiling division", "overlap", "step",
                 "paragraph splitting", "sentence splitting", "greedy packing", "chunk metadata",
                 "character offsets", "heading context", "token budget"],
}

LESSON = r'''
## Why chunk?

A model's context window is limited and costs money per token, and an embedding of a whole
100-page manual is a blurry average of everything in it. So RAG apps cut documents into
**chunks**, embed each chunk, and later put only the few most relevant chunks in the prompt.
Chunks too big: blurry matches, wasted tokens. Too small: a chunk loses the context it
needs to make sense.

## Fixed size

```python
text, size = "one two three four five", 2
print([text[i:i + size] for i in range(0, len(text), size)][:3])       # characters
words = text.split()
print([" ".join(words[i:i + size]) for i in range(0, len(words), size)])  # words
```
Number of chunks = ceiling division: `(n + size - 1) // size`.

## Overlap

Repeat the last `overlap` items at the start of the next chunk so a sentence cut at a border
still appears whole somewhere. **step = size - overlap** (must be > 0, so `overlap < size`).
Stop after the chunk that reaches the end, or you get a tiny tail that is pure overlap.

## Structure-aware splitting

- Paragraphs: `text.split("\n\n")`, strip, drop empties.
- Sentences: end at `.`, `!` or `?` followed by whitespace (`re.split(r"(?<=[.!?])\s+", text)`).
- **Greedy packing**: add pieces to the current chunk while it still fits the limit; otherwise
  close it and start a new one. A piece bigger than the limit on its own gets split further.

## Metadata

A chunk without its origin can't be cited. Keep `source`/`doc_id`, `index`, `title`, and
character offsets `start`/`end` (so `text[start:end] == chunk`). A stable id like
`"handbook-3"` lets you update or delete chunks later.

## Context

A chunk like "It costs $5 per month." is useless alone. Prefix the document title and heading
path ("Pricing > Pro plan") to the text you embed - the idea behind Anthropic's
*contextual retrieval*.

## Token budgets

Limits are really in tokens, not characters. Pass a `count_tokens(text)` function in (a
real tokenizer, or a rough `len(text) // 4`) and measure the joined candidate chunk - token
counts don't simply add up.

## Gotchas

- `range(0, n, step)` with `step <= 0` fails: validate overlap first.
- `" ".join(words)` loses the original newlines; offsets need character chunks.
- Empty input should give `[]`, not `[""]`.
'''

EXERCISES = [
    # ------------------------------------------------------------------ difficulty 0
    {
        "id": "chunking-s1",
        "title": "Slices in steps",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## Cutting the loaf

            A long document is like a loaf of bread: nobody eats it whole. You cut it into
            slices so each one fits in your hand. In a RAG app each slice is a **chunk**:
            small enough to embed precisely and to fit in the model's prompt.

            The simplest cut is by characters. `range(start, stop, step)` gives the start
            of each slice, and slicing `text[i:i + size]` cuts it out:

            ```python
            text = "hello world!"
            print(list(range(0, len(text), 5)))
            for i in range(0, len(text), 5):
                print(repr(text[i:i + 5]))
            ```

            Slicing past the end is fine in Python: `"abc"[2:10]` is just `"c"`. So the
            last chunk is simply shorter.

            This is called **fixed-size chunking**. It's crude, but it's the baseline
            every other method is compared to.
        ''',
        "prompt": r'''Read the code and type exactly what it prints.''',
        "code": r'''
            text = "abcdefghij"
            chunks = [text[i:i + 4] for i in range(0, len(text), 4)]
            print(chunks)
            print(len(chunks))
            print(chunks[-1])
        ''',
        "solution": r'''
            ['abcd', 'efgh', 'ij']
            3
            ij
        ''',
        "explanation": r'''
            `range(0, 10, 4)` gives the starts `0, 4, 8`. The slices are `text[0:4]`,
            `text[4:8]` and `text[8:12]`; the last one runs past the end, so it only
            holds the remaining `"ij"`.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "First work out which numbers range(0, 10, 4) produces.",
            "Each start i gives the slice from i up to (not including) i + 4. Slicing past the end just stops at the end.",
            "Starts are 0, 4, 8. Write the three slices as a list with single quotes, then the count, then the last slice without quotes.",
        ],
    },
    {
        "id": "chunking-s2",
        "title": "Fixed-size chunks",
        "difficulty": 0,
        "lesson": r'''
            ## Same knife, any size

            Remember the loaf? Now make the slice thickness a setting. The starts jump by
            `size` each time, and each slice is `size` characters long.

            ```python
            text = "retrieval"
            size = 3
            starts = list(range(0, len(text), size))
            print(starts)
            print([text[s:s + size] for s in starts])
            ```

            A list comprehension (from the comprehensions chapter) builds the whole list
            in one line.

            The **chunk size** is the most important knob in a RAG system. Real apps
            use a few hundred to a couple of thousand characters.

            Watch out: with empty text, `range(0, 0, size)` is empty, so you get `[]` -
            exactly what you want, no special case needed.
        ''',
        "prompt": r'''
            Cut text into pieces of a fixed number of characters. Complete the function by
            replacing the `___`.

            **Write:** `chunk_chars(text, size)`

            - `text`: a string, e.g. `"abcdefg"`
            - `size`: a positive int, the chunk length, e.g. `3`
            - **Returns:** a list of strings, each `size` characters long except possibly the last

            **Rules**
            - Joining the chunks back together gives the original text.
            - Empty text returns `[]`.

            **Examples**
            ```python
            chunk_chars("abcdefg", 3)   # returns ["abc", "def", "g"]
            chunk_chars("abcdef", 3)    # returns ["abc", "def"]
            chunk_chars("", 3)          # returns []
            ```
        ''',
        "starter": r'''
            def chunk_chars(text, size):
                return [text[i:i + size] for i in range(0, len(text), ___)]
        ''',
        "tests": r'''
            from solution import chunk_chars

            def test_last_chunk_is_shorter():
                got = chunk_chars("abcdefg", 3)
                assert got == ["abc", "def", "g"], f"got {got!r}"

            def test_exact_fit():
                got = chunk_chars("abcdef", 3)
                assert got == ["abc", "def"], f"got {got!r}"

            def test_empty_text():
                got = chunk_chars("", 3)
                assert got == [], f"got {got!r}"

            def test_joins_back_to_original():
                text = "Refunds are processed within 5 days."
                got = chunk_chars(text, 7)
                assert "".join(got) == text and all(len(c) == 7 for c in got[:-1]), f"got {got!r}"
        ''',
        "solution": r'''
            def chunk_chars(text, size):
                return [text[i:i + size] for i in range(0, len(text), size)]
        ''',
        "hints": [
            "The blank is the third argument of range: how far to jump between chunk starts.",
            "Each chunk is size characters long, so the next chunk starts size characters later.",
            "Replace ___ with the parameter size.",
        ],
    },
    {
        "id": "chunking-s3",
        "title": "Fix: word chunks",
        "difficulty": 0,
        "lesson": r'''
            ## Don't cut words in half

            Slicing by characters can cut "refund" into "ref" and "und". Cutting by
            **words** keeps each word whole: split the text into a list of words, slice
            the list, and glue each slice back with spaces.

            ```python
            words = "the quick brown fox jumps".split()
            print(words[0:2])
            print(" ".join(words[0:2]))
            print(" ".join(words[4:6]))
            ```

            `str.split()` with no argument splits on any whitespace (spaces, newlines,
            tabs) and drops the empty bits. `" ".join(list)` is its opposite.

            Word counts are a better stand-in for **tokens** (what models actually
            count) than characters are.

            Watch out: the jump between starts must match the chunk size, or chunks
            repeat words.
        ''',
        "prompt": r'''
            `chunk_words` should split text into chunks of `size` words, but its chunks
            repeat words over and over. Fix the bug.

            **Write:** `chunk_words(text, size)`

            - `text`: a string, e.g. `"a b c d e"`
            - `size`: a positive int, words per chunk
            - **Returns:** a list of strings; each chunk is up to `size` words joined with single spaces

            **Rules**
            - Every word appears in exactly one chunk, in order.
            - Any whitespace (spaces, newlines) separates words.
            - Empty or whitespace-only text returns `[]`.

            **Examples**
            ```python
            chunk_words("a b c d e", 2)          # returns ["a b", "c d", "e"]
            chunk_words("one\ntwo  three", 3)    # returns ["one two three"]
            chunk_words("   ", 2)                # returns []
            ```
        ''',
        "starter": r'''
            def chunk_words(text, size):
                words = text.split()
                chunks = []
                for i in range(0, len(words), 1):
                    chunks.append(" ".join(words[i:i + size]))
                return chunks
        ''',
        "tests": r'''
            from solution import chunk_words

            def test_two_words_per_chunk():
                got = chunk_words("a b c d e", 2)
                assert got == ["a b", "c d", "e"], f"got {got!r}"

            def test_any_whitespace_separates():
                got = chunk_words("one\ntwo  three", 3)
                assert got == ["one two three"], f"got {got!r}"

            def test_blank_text():
                got = chunk_words("   ", 2)
                assert got == [], f"got {got!r}"

            def test_no_word_repeated():
                got = chunk_words("w1 w2 w3 w4 w5 w6 w7", 3)
                assert got == ["w1 w2 w3", "w4 w5 w6", "w7"], f"got {got!r}"
        ''',
        "solution": r'''
            def chunk_words(text, size):
                words = text.split()
                chunks = []
                for i in range(0, len(words), size):
                    chunks.append(" ".join(words[i:i + size]))
                return chunks
        ''',
        "hints": [
            "Look at how far the loop jumps between chunk starts.",
            "With a step of 1 a new chunk starts at every word, so each word lands in several chunks.",
            "Change the step of range from 1 to size.",
        ],
    },
    {
        "id": "chunking-s4",
        "title": "How many chunks?",
        "difficulty": 0,
        "lesson": r'''
            ## Counting boxes

            You're packing 10 books into boxes that hold 4. That's 2 full boxes plus one
            box for the last 2 books: 3 boxes. Normal division gives 2.5; you need to
            **round up**.

            Floor division `//` rounds *down*. A classic trick rounds up instead: add
            `size - 1` before dividing.

            ```python
            print(10 // 4)
            print((10 + 4 - 1) // 4)
            print((8 + 4 - 1) // 4)
            print((0 + 4 - 1) // 4)
            ```

            This is called **ceiling division**. It tells you how many chunks (and so how
            many embedding calls) a document will need before you make them - useful for
            estimating cost.

            Watch out: `round(10 / 4)` gives `2` (Python rounds 2.5 to the even number),
            not `3`.
        ''',
        "prompt": r'''
            Before chunking, estimate how many chunks (and embedding calls) a document needs.

            **Write:** `count_chunks(length, size)`

            - `length`: an int >= 0, the text length in characters, e.g. `10`
            - `size`: a positive int, the chunk size, e.g. `4`
            - **Returns:** an int, the number of fixed-size chunks (the last one may be partial)

            **Rules**
            - Round up: a partial chunk still counts as one.
            - A length of `0` needs `0` chunks.

            **Examples**
            ```python
            count_chunks(10, 4)   # returns 3
            count_chunks(8, 4)    # returns 2
            count_chunks(0, 4)    # returns 0
            ```
        ''',
        "starter": r'''
            def count_chunks(length, size):
                ...
        ''',
        "tests": r'''
            from solution import count_chunks

            def test_partial_chunk_counts():
                got = count_chunks(10, 4)
                assert got == 3, f"got {got!r}"

            def test_exact_fit():
                got = count_chunks(8, 4)
                assert got == 2, f"got {got!r}"

            def test_zero_length():
                got = count_chunks(0, 4)
                assert got == 0, f"got {got!r}"

            def test_returns_an_int():
                got = count_chunks(1001, 500)
                assert got == 3 and isinstance(got, int), f"got {got!r}"
        ''',
        "solution": r'''
            def count_chunks(length, size):
                return (length + size - 1) // size
        ''',
        "hints": [
            "Plain division gives a float and floor division rounds down. You need to round up.",
            "Add size - 1 to the length before using floor division.",
            "Return (length + size - 1) // size.",
        ],
    },
    {
        "id": "chunking-s5",
        "title": "Split into paragraphs",
        "difficulty": 0,
        "lesson": r'''
            ## Cut along the dotted lines

            Fixed-size cuts ignore meaning. But writers already cut their text for you:
            **paragraphs**, separated by a blank line. A blank line is two newlines in a
            row: `"\n\n"`.

            ```python
            text = "Intro line.\n\nSecond part.\n\n\n\nThird."
            parts = text.split("\n\n")
            print(parts)
            print([p.strip() for p in parts if p.strip()])
            ```

            Extra blank lines create empty strings, and paragraphs often carry stray
            spaces or newlines at their edges. `.strip()` cleans the edges, and
            `if p.strip()` drops the empty pieces.

            Splitting on the document's own structure is called **structure-aware** (or
            *semantic*) chunking. It keeps each idea together.
        ''',
        "prompt": r'''
            Split a document into its paragraphs.

            **Write:** `split_paragraphs(text)`

            - `text`: a string where paragraphs are separated by blank lines (`"\n\n"`)
            - **Returns:** a list of paragraph strings, in order

            **Rules**
            - Strip whitespace from both ends of every paragraph.
            - Drop paragraphs that are empty after stripping (extra blank lines, spaces).
            - Single newlines inside a paragraph are kept.
            - Empty text returns `[]`.

            **Examples**
            ```python
            split_paragraphs("First.\n\nSecond.")               # returns ["First.", "Second."]
            split_paragraphs("  A\nstill A \n\n\n\nB\n")       # returns ["A\nstill A", "B"]
            split_paragraphs("")                               # returns []
            ```
        ''',
        "starter": r'''
            def split_paragraphs(text):
                ...
        ''',
        "tests": r'''
            from solution import split_paragraphs

            def test_two_paragraphs():
                got = split_paragraphs("First.\n\nSecond.")
                assert got == ["First.", "Second."], f"got {got!r}"

            def test_strips_and_drops_empty():
                got = split_paragraphs("  A\nstill A \n\n\n\nB\n")
                assert got == ["A\nstill A", "B"], f"got {got!r}"

            def test_whitespace_only_paragraphs_dropped():
                got = split_paragraphs("A\n\n   \n\nB")
                assert got == ["A", "B"], f"got {got!r}"

            def test_empty_text():
                got = split_paragraphs("")
                assert got == [], f"got {got!r}"
        ''',
        "solution": r'''
            def split_paragraphs(text):
                return [p.strip() for p in text.split("\n\n") if p.strip()]
        ''',
        "hints": [
            "str.split can split on any separator string, including two newlines.",
            "After splitting, clean each piece with strip and throw away the ones that end up empty.",
            "Split text on \"\\n\\n\", then build a list of p.strip() for each piece p where p.strip() is not empty.",
        ],
    },
    {
        "id": "chunking-s6",
        "title": "Overlapping chunks",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## Shingles on a roof

            Roof shingles overlap so rain can't slip through the gaps. Chunks overlap for
            the same reason: if a key sentence is cut at a border, the overlap makes sure
            it still appears whole in one of the chunks.

            With **overlap**, each chunk repeats the last few characters (or words) of
            the one before. The starts no longer jump by `size`, but by
            `size - overlap`:

            ```python
            text = "abcdefghij"
            size, overlap = 5, 2
            step = size - overlap
            print(step)
            print([text[i:i + size] for i in range(0, len(text), step)])
            ```

            `size - overlap` is called the **step** (or *stride*). A common setting is an
            overlap of 10-20% of the chunk size.

            Watch out: the overlap must be smaller than the size, or the step is zero or
            negative and `range` fails or goes nowhere.
        ''',
        "prompt": r'''Read the code and type exactly what it prints.''',
        "code": r'''
            text = "abcdefgh"
            size, overlap = 4, 1
            step = size - overlap
            starts = list(range(0, len(text), step))
            print(step, starts)
            print([text[s:s + size] for s in starts])
        ''',
        "solution": r'''
            3 [0, 3, 6]
            ['abcd', 'defg', 'gh']
        ''',
        "explanation": r'''
            The step is `4 - 1 = 3`, so the starts are `0, 3, 6`. Each chunk is 4
            characters from its start: `abcd`, `defg` (it repeats the `d`), and `gh`,
            which runs out of text.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Compute step first, then the numbers range(0, 8, step) produces.",
            "Each chunk starts at one of those numbers and is 4 characters long (or shorter at the end).",
            "Line 1: the step and the list of starts. Line 2: the list of three slices in single quotes.",
        ],
    },
    # ------------------------------------------------------------------ difficulty 1
    {
        "id": "chunking-1",
        "title": "Overlap done right",
        "difficulty": 1,
        "lesson": r'''
            ## No crumbs at the end

            Look at the last predict step again: with size 4 and overlap 1 on
            `"abcdefg"` (7 letters), the starts are `0, 3, 6` and the last chunk is just
            `"g"` - a crumb that is *entirely* overlap. It adds nothing new.

            The fix: stop as soon as a chunk reaches the end of the text.

            ```python
            text, size, step = "abcdefg", 4, 3
            start = 0
            while True:
                piece = text[start:start + size]
                print(start, piece)
                if start + size >= len(text):
                    break
                start += step
            ```

            A `while` loop with `break` fits "keep going until the chunk reaches the
            end". Remember to handle empty text before the loop.

            Checking arguments up front and raising `ValueError` is called
            **validating input** - here, an overlap that isn't smaller than the size.
        ''',
        "prompt": r'''
            Cut text into character chunks that overlap, without a useless crumb at the end.

            **Write:** `chunk_with_overlap(text, size, overlap)`

            - `text`: a string
            - `size`: a positive int, chunk length
            - `overlap`: an int, how many characters each chunk shares with the previous one
            - **Returns:** a list of strings

            **Rules**
            - Chunks start at `0`, `step`, `2 * step`, ... where `step = size - overlap`.
            - Each chunk is `text[start:start + size]`.
            - Stop right after the first chunk that reaches the end of the text (`start + size >= len(text)`).
            - If `overlap < 0` or `overlap >= size`, raise `ValueError`.
            - Empty text returns `[]`.

            **Examples**
            ```python
            chunk_with_overlap("abcdefgh", 4, 1)   # returns ["abcd", "defg", "gh"]
            chunk_with_overlap("abcdefg", 4, 1)    # returns ["abcd", "defg"]   (no "g" crumb)
            chunk_with_overlap("abc", 5, 2)        # returns ["abc"]
            chunk_with_overlap("abc", 3, 3)        # raises ValueError
            ```
        ''',
        "starter": r'''
            def chunk_with_overlap(text, size, overlap):
                ...
        ''',
        "tests": r'''
            from solution import chunk_with_overlap

            def raises_value_error(*args):
                try:
                    chunk_with_overlap(*args)
                except ValueError:
                    return True
                return False

            def test_overlap_repeats_characters():
                got = chunk_with_overlap("abcdefgh", 4, 1)
                assert got == ["abcd", "defg", "gh"], f"got {got!r}"

            def test_no_crumb_at_the_end():
                got = chunk_with_overlap("abcdefg", 4, 1)
                assert got == ["abcd", "defg"], f"got {got!r}"

            def test_short_text_one_chunk():
                got = chunk_with_overlap("abc", 5, 2)
                assert got == ["abc"], f"got {got!r}"

            def test_zero_overlap_is_plain_chunking():
                got = chunk_with_overlap("abcdef", 2, 0)
                assert got == ["ab", "cd", "ef"], f"got {got!r}"

            def test_empty_text():
                got = chunk_with_overlap("", 4, 1)
                assert got == [], f"got {got!r}"

            def test_bad_overlap_raises():
                assert raises_value_error("abc", 3, 3), "overlap == size should raise ValueError"
                assert raises_value_error("abc", 3, 5), "overlap > size should raise ValueError"
                assert raises_value_error("abc", 3, -1), "negative overlap should raise ValueError"
        ''',
        "solution": r'''
            def chunk_with_overlap(text, size, overlap):
                if overlap < 0 or overlap >= size:
                    raise ValueError("overlap must be >= 0 and smaller than size")
                if not text:
                    return []
                step = size - overlap
                chunks = []
                start = 0
                while True:
                    chunks.append(text[start:start + size])
                    if start + size >= len(text):
                        break
                    start += step
                return chunks
        ''',
        "hints": [
            "Validate the overlap first, then handle empty text, then loop.",
            "A while loop that appends a chunk, then checks whether that chunk reached the end, then moves the start forward by the step.",
            "Raise ValueError if overlap < 0 or overlap >= size; return [] for empty text; step = size - overlap; start = 0; loop: append text[start:start+size], break if start + size >= len(text), else start += step.",
        ],
    },
    {
        "id": "chunking-2",
        "title": "Split into sentences",
        "difficulty": 1,
        "research": {
            "note": "Read about `re.split` and lookbehind assertions `(?<=...)` in the `re` docs. They give "
                    "a one-line way to split after punctuation while keeping it. A plain loop works too.",
            "links": [{"title": "re.split - Python docs", "url": "https://docs.python.org/3/library/re.html#re.split"},
                      {"title": "Regular expression syntax - Python docs",
                       "url": "https://docs.python.org/3/library/re.html#regular-expression-syntax"}],
        },
        "lesson": r'''
            ## Where does a thought end?

            Paragraphs can be long. The next natural cut is the **sentence**: a
            complete thought. A sentence usually ends with `.`, `!` or `?` *followed by
            a space or a newline*.

            That "followed by" part matters: `3.5` or `example.com` contain dots but no
            sentence ends there.

            Here is the idea with a different separator - cut after every `;` that is
            followed by a space, keeping the `;`:

            ```python
            text = "a; b;c; d"
            parts, current = [], ""
            for i, ch in enumerate(text):
                current += ch
                nxt = text[i + 1] if i + 1 < len(text) else " "
                if ch == ";" and nxt.isspace():
                    parts.append(current.strip())
                    current = ""
            parts.append(current.strip())
            print(parts)
            ```

            With the regex chapter you can do the same in one `re.split` call using a
            **lookbehind** (see the research link).
        ''',
        "prompt": r'''
            Split text into sentences, so chunks can be cut on sentence borders.

            **Write:** `split_sentences(text)`

            - `text`: a string, e.g. `"Hi there. How are you? Fine!"`
            - **Returns:** a list of sentence strings, in order

            **Rules**
            - A sentence ends at `.`, `!` or `?` that is followed by whitespace (space, newline...) or by the end of the text.
            - Keep the punctuation at the end of its sentence.
            - Strip whitespace from each sentence; drop empty ones.
            - Punctuation not followed by whitespace (like `3.5` or `a.b`) does not end a sentence.
            - Text after the last punctuation mark is a final sentence too.
            - Empty or whitespace-only text returns `[]`.

            **Examples**
            ```python
            split_sentences("Hi there. How are you?  Fine!")   # returns ["Hi there.", "How are you?", "Fine!"]
            split_sentences("Version 3.5 is out.\nUpdate now")  # returns ["Version 3.5 is out.", "Update now"]
            split_sentences("")                                 # returns []
            ```
        ''',
        "starter": r'''
            def split_sentences(text):
                ...
        ''',
        "tests": r'''
            from solution import split_sentences

            def test_three_kinds_of_ending():
                got = split_sentences("Hi there. How are you?  Fine!")
                assert got == ["Hi there.", "How are you?", "Fine!"], f"got {got!r}"

            def test_dot_inside_number_does_not_split():
                got = split_sentences("Version 3.5 is out.\nUpdate now")
                assert got == ["Version 3.5 is out.", "Update now"], f"got {got!r}"

            def test_newline_counts_as_whitespace():
                got = split_sentences("One.\nTwo.\n\nThree.")
                assert got == ["One.", "Two.", "Three."], f"got {got!r}"

            def test_leading_and_trailing_space():
                got = split_sentences("   Wait... what?   ")
                assert got == ["Wait...", "what?"], f"got {got!r}"

            def test_empty_text():
                assert split_sentences("") == [] and split_sentences("  \n ") == []
        ''',
        "solution": r'''
            import re

            def split_sentences(text):
                parts = re.split(r"(?<=[.!?])\s+", text.strip())
                return [p.strip() for p in parts if p.strip()]
        ''',
        "hints": [
            "Either loop over the characters and cut when you see ., ! or ? followed by whitespace, or use re.split with a lookbehind.",
            "With re.split, the pattern should match the whitespace AFTER the punctuation (so the punctuation stays in the sentence). Strip the text first so there is no empty piece at the edges.",
            "Strip the text; re.split on one-or-more whitespace characters that come right after one of . ! ? (lookbehind (?<=[.!?]) then \\s+); strip each piece and keep only the non-empty ones.",
        ],
    },
    {
        "id": "chunking-3",
        "title": "Label every chunk",
        "difficulty": 1,
        "lesson": r'''
            ## Luggage tags

            At the airport, every suitcase gets a tag saying whose it is and where it's
            going. Without it, the bag is just a bag. A chunk without **metadata** is the
            same: when it shows up in a search result, you can't say which document it
            came from, cite it, or delete it when the document changes.

            ```python
            chunks = ["Refunds take 5 days.", "Contact support."]
            for i, text in enumerate(chunks):
                print({"id": f"faq:{i}", "index": i, "text": text})
            ```

            `enumerate` gives you the position and the item together.

            The `id` built from the source and the position is a **stable id**: chunking
            the same document again gives the same ids, so a vector store can update
            the chunks instead of duplicating them.
        ''',
        "prompt": r'''
            Attach metadata to each chunk of a document.

            **Write:** `with_metadata(chunks, source)`

            - `chunks`: a list of chunk strings
            - `source`: a string naming the document, e.g. `"faq.md"`
            - **Returns:** a list of dicts, one per chunk, in order:
              `{"id": "<source>:<index>", "source": source, "index": index, "text": chunk}`

            **Rules**
            - `index` counts from `0`.
            - `id` is the source, a colon, then the index (e.g. `"faq.md:0"`).
            - Empty `chunks` returns `[]`.

            **Examples**
            ```python
            with_metadata(["Refunds take 5 days.", "Contact support."], "faq.md")
            # returns [{"id": "faq.md:0", "source": "faq.md", "index": 0, "text": "Refunds take 5 days."},
            #          {"id": "faq.md:1", "source": "faq.md", "index": 1, "text": "Contact support."}]
            with_metadata([], "faq.md")   # returns []
            ```
        ''',
        "starter": r'''
            def with_metadata(chunks, source):
                ...
        ''',
        "tests": r'''
            from solution import with_metadata

            def test_two_chunks():
                got = with_metadata(["Refunds take 5 days.", "Contact support."], "faq.md")
                want = [{"id": "faq.md:0", "source": "faq.md", "index": 0, "text": "Refunds take 5 days."},
                        {"id": "faq.md:1", "source": "faq.md", "index": 1, "text": "Contact support."}]
                assert got == want, f"got {got!r}"

            def test_index_is_an_int_and_counts_up():
                got = with_metadata(["a", "b", "c"], "x")
                assert [c["index"] for c in got] == [0, 1, 2], f"got {got!r}"

            def test_empty():
                got = with_metadata([], "faq.md")
                assert got == [], f"got {got!r}"
        ''',
        "solution": r'''
            def with_metadata(chunks, source):
                return [{"id": f"{source}:{i}", "source": source, "index": i, "text": text}
                        for i, text in enumerate(chunks)]
        ''',
        "hints": [
            "enumerate(chunks) gives you each position together with each chunk.",
            "Build one dict per chunk; the id is an f-string made from the source and the position.",
            "Loop with for i, text in enumerate(chunks), build {\"id\": f\"{source}:{i}\", \"source\": ..., \"index\": i, \"text\": text}, collect them in a list and return it.",
        ],
    },
    {
        "id": "chunking-4",
        "title": "Pack sentences into chunks",
        "difficulty": 1,
        "lesson": r'''
            ## Filling suitcases

            You're packing clothes into suitcases with a weight limit. You put items in
            one by one; when the next item would go over the limit, you close that
            suitcase and open a new one. That's **greedy packing**.

            For chunks, the items are sentences and the limit is characters. Chunks end
            on sentence borders, yet stay close to the size limit.

            ```python
            limit = 12
            current = "Hi."
            for nxt in ["Yes.", "Goodbye now."]:
                candidate = current + " " + nxt
                print(repr(candidate), len(candidate), len(candidate) <= limit)
            ```

            Always measure the **candidate** (current + space + next), because the
            joining space counts too.

            Watch out: one sentence may be longer than the limit by itself. It can't be
            split here, so it becomes a chunk on its own.
        ''',
        "prompt": r'''
            Group sentences into chunks no longer than a character limit.

            **Write:** `pack_sentences(sentences, max_chars)`

            - `sentences`: a list of sentence strings, e.g. `["Hi.", "Yes.", "Goodbye now."]`
            - `max_chars`: a positive int
            - **Returns:** a list of chunk strings; each chunk is consecutive sentences joined with one space

            **Rules**
            - Go through the sentences in order. Add the next sentence to the current chunk if the
              result (with the joining space) is at most `max_chars` long; otherwise start a new chunk with it.
            - A sentence longer than `max_chars` on its own still becomes a chunk (don't split it).
            - Empty `sentences` returns `[]`.

            **Examples**
            ```python
            pack_sentences(["Hi.", "Yes.", "Goodbye now."], 12)   # returns ["Hi. Yes.", "Goodbye now."]
            pack_sentences(["Hi.", "Yes."], 8)                    # returns ["Hi. Yes."]   (exactly 8 fits)
            pack_sentences(["A very long sentence.", "Ok."], 5)   # returns ["A very long sentence.", "Ok."]
            pack_sentences([], 10)                                # returns []
            ```
        ''',
        "starter": r'''
            def pack_sentences(sentences, max_chars):
                ...
        ''',
        "tests": r'''
            from solution import pack_sentences

            def test_packs_until_full():
                got = pack_sentences(["Hi.", "Yes.", "Goodbye now."], 12)
                assert got == ["Hi. Yes.", "Goodbye now."], f"got {got!r}"

            def test_exact_limit_fits():
                got = pack_sentences(["Hi.", "Yes."], 8)
                assert got == ["Hi. Yes."], f"got {got!r}"

            def test_one_over_limit_starts_new_chunk():
                got = pack_sentences(["Hi.", "Yes."], 7)
                assert got == ["Hi.", "Yes."], f"got {got!r}"

            def test_long_sentence_alone():
                got = pack_sentences(["A very long sentence.", "Ok.", "Go."], 7)
                assert got == ["A very long sentence.", "Ok. Go."], f"got {got!r}"

            def test_empty():
                assert pack_sentences([], 10) == []
        ''',
        "solution": r'''
            def pack_sentences(sentences, max_chars):
                chunks = []
                current = ""
                for sentence in sentences:
                    candidate = sentence if not current else current + " " + sentence
                    if len(candidate) <= max_chars or not current:
                        current = candidate
                    else:
                        chunks.append(current)
                        current = sentence
                if current:
                    chunks.append(current)
                return chunks
        ''',
        "hints": [
            "Keep a `current` chunk string and a list of finished chunks.",
            "For each sentence, build the candidate (current plus a space plus the sentence, or just the sentence if current is empty) and check its length.",
            "If the candidate fits (or current is empty) make it current; otherwise append current to the list and start current with the sentence. After the loop, append current if it is not empty.",
        ],
    },
    {
        "id": "chunking-5",
        "title": "Chunks with offsets",
        "difficulty": 1,
        "lesson": r'''
            ## Page and line numbers

            A good quote comes with a page number so readers can find it. For chunks,
            the "page number" is the **character offset**: where the chunk starts and
            ends in the original text. With it, your app can highlight the exact passage
            the answer came from.

            ```python
            text = "Plans: Free, Pro, Team."
            start, end = 7, 11
            print(text[start:end])
            print({"start": start, "end": end, "text": text[start:end]})
            ```

            By convention `end` is **exclusive**, just like slicing: the chunk is
            `text[start:end]`, and its length is `end - start`.

            Offsets are only reliable if the chunk text is an exact slice of the
            original - that's why this step uses character chunks, not `" ".join`
            of words (joining would change the spacing).
        ''',
        "prompt": r'''
            Cut text into fixed-size character chunks and record where each one came from.

            **Write:** `chunk_spans(text, size)`

            - `text`: a string
            - `size`: a positive int, chunk length
            - **Returns:** a list of dicts `{"start": int, "end": int, "text": str}`, in order

            **Rules**
            - Chunks are consecutive and don't overlap: starts are `0`, `size`, `2 * size`, ...
            - `end` is exclusive and never past the end of the text, so `text[start:end] == chunk["text"]`.
            - Empty text returns `[]`.

            **Examples**
            ```python
            chunk_spans("abcdefg", 3)
            # returns [{"start": 0, "end": 3, "text": "abc"},
            #          {"start": 3, "end": 6, "text": "def"},
            #          {"start": 6, "end": 7, "text": "g"}]
            chunk_spans("", 3)   # returns []
            ```
        ''',
        "starter": r'''
            def chunk_spans(text, size):
                ...
        ''',
        "tests": r'''
            from solution import chunk_spans

            def test_three_spans():
                got = chunk_spans("abcdefg", 3)
                want = [{"start": 0, "end": 3, "text": "abc"}, {"start": 3, "end": 6, "text": "def"},
                        {"start": 6, "end": 7, "text": "g"}]
                assert got == want, f"got {got!r}"

            def test_end_never_past_text():
                got = chunk_spans("hello", 4)
                assert got[-1] == {"start": 4, "end": 5, "text": "o"}, f"got {got!r}"

            def test_slices_match_text():
                text = "Refunds take\n5 business days."
                for c in chunk_spans(text, 6):
                    assert text[c["start"]:c["end"]] == c["text"], f"span {c!r} does not match the text"

            def test_empty():
                assert chunk_spans("", 3) == []
        ''',
        "solution": r'''
            def chunk_spans(text, size):
                spans = []
                for start in range(0, len(text), size):
                    end = min(start + size, len(text))
                    spans.append({"start": start, "end": end, "text": text[start:end]})
                return spans
        ''',
        "hints": [
            "Same starts as plain fixed-size chunking; you just keep more information per chunk.",
            "The end is start + size, but capped at the length of the text (min helps).",
            "Loop start over range(0, len(text), size); end = min(start + size, len(text)); append {\"start\": start, \"end\": end, \"text\": text[start:end]}; return the list.",
        ],
    },
    # ------------------------------------------------------------------ difficulty 2
    {
        "id": "chunking-6",
        "title": "Chunk a document",
        "difficulty": 2,
        "placement": True,
        "prompt": r'''
            Turn one document into word chunks with overlap and metadata, ready to embed.

            **Write:** `chunk_document(doc, size, overlap)`

            - `doc`: a dict `{"id": str, "title": str, "text": str}`
            - `size`: a positive int, words per chunk
            - `overlap`: an int, words shared with the previous chunk
            - **Returns:** a list of dicts, one per chunk, in order:
              `{"id": "<doc id>-<index>", "doc_id": ..., "title": ..., "index": int, "text": str}`

            **Rules**
            - Split `text` into words on any whitespace; chunk text is its words joined with single spaces.
            - Chunks start at word `0`, `step`, `2 * step`, ... where `step = size - overlap`, each up to `size` words.
            - Stop right after the first chunk that reaches the last word (no chunk made only of overlap).
            - `index` counts from `0`; `id` is e.g. `"faq-0"`.
            - If `size < 1`, `overlap < 0` or `overlap >= size`, raise `ValueError`.
            - A document with no words returns `[]`.

            **Examples**
            ```python
            doc = {"id": "faq", "title": "FAQ", "text": "a b c d e f g"}
            [c["text"] for c in chunk_document(doc, 3, 1)]   # returns ["a b c", "c d e", "e f g"]
            chunk_document(doc, 3, 1)[0]
            # returns {"id": "faq-0", "doc_id": "faq", "title": "FAQ", "index": 0, "text": "a b c"}
            [c["text"] for c in chunk_document(doc, 4, 1)]   # returns ["a b c d", "d e f g"]
            chunk_document({"id": "x", "title": "X", "text": "  "}, 3, 1)   # returns []
            ```
        ''',
        "starter": r'''
            def chunk_document(doc, size, overlap):
                ...
        ''',
        "tests": r'''
            from solution import chunk_document

            DOC = {"id": "faq", "title": "FAQ", "text": "a b c d e f g"}

            def texts(chunks):
                return [c["text"] for c in chunks]

            def test_overlapping_word_chunks():
                got = texts(chunk_document(DOC, 3, 1))
                assert got == ["a b c", "c d e", "e f g"], f"got {got!r}"

            def test_metadata_on_each_chunk():
                got = chunk_document(DOC, 3, 1)
                assert got[0] == {"id": "faq-0", "doc_id": "faq", "title": "FAQ", "index": 0, "text": "a b c"}, f"got {got[0]!r}"
                assert [c["id"] for c in got] == ["faq-0", "faq-1", "faq-2"], f"got {got!r}"

            def test_no_overlap_only_tail():
                got = texts(chunk_document(DOC, 4, 1))
                assert got == ["a b c d", "d e f g"], f"got {got!r}"

            def test_short_doc_and_messy_whitespace():
                got = texts(chunk_document({"id": "x", "title": "X", "text": " hi\n\nthere "}, 5, 2))
                assert got == ["hi there"], f"got {got!r}"

            def test_empty_doc():
                assert chunk_document({"id": "x", "title": "X", "text": "  "}, 3, 1) == []

            def test_bad_settings_raise():
                for size, overlap in [(3, 3), (0, 0), (3, -1)]:
                    try:
                        chunk_document(DOC, size, overlap)
                    except ValueError:
                        continue
                    assert False, f"size={size}, overlap={overlap} should raise ValueError"
        ''',
        "solution": r'''
            def chunk_document(doc, size, overlap):
                if size < 1 or overlap < 0 or overlap >= size:
                    raise ValueError("bad chunk settings")
                words = doc["text"].split()
                step = size - overlap
                chunks = []
                start = 0
                while words:
                    i = len(chunks)
                    chunks.append({"id": f"{doc['id']}-{i}", "doc_id": doc["id"], "title": doc["title"],
                                   "index": i, "text": " ".join(words[start:start + size])})
                    if start + size >= len(words):
                        break
                    start += step
                return chunks
        ''',
        "hints": [
            "This combines word chunking, 'Overlap done right' and 'Label every chunk'.",
            "Validate the settings, split into words, then walk the starts by step and stop after the chunk that reaches the last word. Build the metadata dict as you go.",
            "Raise ValueError for bad settings; words = text.split(); if no words return []; start = 0; loop: append the dict with id f\"{doc id}-{index}\" and text \" \".join(words[start:start+size]); break when start + size >= len(words); else start += size - overlap.",
        ],
    },
    {
        "id": "chunking-7",
        "title": "Paragraph-aware chunks",
        "difficulty": 2,
        "prompt": r'''
            Chunk a document along its paragraphs: merge small paragraphs together, cut up
            paragraphs that are too big.

            **Write:** `paragraph_chunks(text, max_chars)`

            - `text`: a string with paragraphs separated by blank lines (`"\n\n"`)
            - `max_chars`: a positive int
            - **Returns:** a list of chunk strings, every one at most `max_chars` long

            **Rules**
            - Paragraphs: split on `"\n\n"`, strip each, drop empty ones.
            - Pack consecutive paragraphs greedily, joined with `"\n\n"`: add the next paragraph to
              the current chunk if the joined result is at most `max_chars`; otherwise close the chunk and start a new one.
            - A paragraph longer than `max_chars` is never merged: close the current chunk (if any), then
              add the paragraph cut into fixed-size pieces of `max_chars` characters (the last may be shorter);
              packing then continues with a fresh chunk.
            - Empty text returns `[]`.

            **Examples**
            ```python
            paragraph_chunks("Aa.\n\nBb.\n\nCc.", 8)        # returns ["Aa.\n\nBb.", "Cc."]
            paragraph_chunks("Hi.\n\nabcdefghij\n\nOk.", 4)  # returns ["Hi.", "abcd", "efgh", "ij", "Ok."]
            paragraph_chunks("", 10)                         # returns []
            ```
        ''',
        "starter": r'''
            def paragraph_chunks(text, max_chars):
                ...
        ''',
        "tests": r'''
            from solution import paragraph_chunks

            def test_merges_small_paragraphs():
                got = paragraph_chunks("Aa.\n\nBb.\n\nCc.", 8)
                assert got == ["Aa.\n\nBb.", "Cc."], f"got {got!r}"

            def test_join_counts_two_newlines():
                got = paragraph_chunks("Aa.\n\nBb.", 7)
                assert got == ["Aa.", "Bb."], f"got {got!r}"

            def test_big_paragraph_is_cut():
                got = paragraph_chunks("Hi.\n\nabcdefghij\n\nOk.", 4)
                assert got == ["Hi.", "abcd", "efgh", "ij", "Ok."], f"got {got!r}"

            def test_big_paragraph_not_merged_with_neighbours():
                got = paragraph_chunks("a\n\nbcdefg\n\nh\n\ni", 5)
                assert got == ["a", "bcdef", "g", "h\n\ni"], f"got {got!r}"

            def test_messy_blank_lines_and_limit():
                text = "\n\nOne para.\n\n\n\n  Two para.  \n\nThree para is longer.\n"
                got = paragraph_chunks(text, 22)
                assert got == ["One para.\n\nTwo para.", "Three para is longer."], f"got {got!r}"
                assert all(len(c) <= 22 for c in got)

            def test_empty():
                assert paragraph_chunks("", 10) == [] and paragraph_chunks("\n\n  \n\n", 10) == []
        ''',
        "solution": r'''
            def paragraph_chunks(text, max_chars):
                paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
                chunks = []
                current = ""
                for para in paragraphs:
                    if len(para) > max_chars:
                        if current:
                            chunks.append(current)
                            current = ""
                        chunks.extend(para[i:i + max_chars] for i in range(0, len(para), max_chars))
                        continue
                    candidate = para if not current else current + "\n\n" + para
                    if len(candidate) <= max_chars:
                        current = candidate
                    else:
                        chunks.append(current)
                        current = para
                if current:
                    chunks.append(current)
                return chunks
        ''',
        "hints": [
            "Reuse three earlier ideas: splitting paragraphs, greedy packing, and fixed-size character chunks.",
            "Loop over paragraphs keeping a `current` chunk. Oversized paragraphs are a special case handled first: flush current, then add their pieces directly.",
            "Get the cleaned paragraphs; for each: if longer than max_chars, append current (if any), reset it, extend the list with slices of max_chars and continue; else build candidate joined with \"\\n\\n\", keep it if it fits, otherwise append current and start over with the paragraph. Append the last current.",
        ],
    },
    {
        "id": "chunking-8",
        "title": "Chunks that know their heading",
        "difficulty": 2,
        "research": {
            "note": "Read Anthropic's article on contextual retrieval: why a chunk on its own often lacks "
                    "the context needed to be found, and how prepending context before embedding helps.",
            "links": [{"title": "Introducing Contextual Retrieval - Anthropic",
                       "url": "https://www.anthropic.com/news/contextual-retrieval"}],
        },
        "prompt": r'''
            Chunk a Markdown document by section and give every chunk its context: the
            document title and the heading path. The `context_text` is what you would embed.

            **Write:** `markdown_chunks(markdown, title)`

            - `markdown`: a string of Markdown lines; `# ` lines are level-1 headings, `## ` lines are level-2 headings
            - `title`: the document title, e.g. `"Handbook"`
            - **Returns:** a list of dicts `{"heading": str, "text": str, "context_text": str}`, in document order

            **Rules**
            - A line starting with `"# "` starts a new section and sets the level-1 heading (the rest of the line,
              stripped); it also clears the level-2 heading. A line starting with `"## "` starts a new section and
              sets the level-2 heading.
            - `heading` is `"H1 > H2"` when both are set, just the one that is set otherwise, or `""` before any heading.
            - `text` is the section's non-heading lines joined with `"\n"`, then stripped.
            - Sections whose `text` is empty are skipped.
            - `context_text` is `f"{title} > {heading}\n\n{text}"`, or `f"{title}\n\n{text}"` when `heading` is `""`.

            **Examples**
            ```python
            md = "Welcome!\n# Billing\nWe bill monthly.\n## Refunds\nWithin 5 days.\n# Support\n## Email\nhelp@x.io"
            markdown_chunks(md, "Handbook")
            # returns [
            #  {"heading": "", "text": "Welcome!", "context_text": "Handbook\n\nWelcome!"},
            #  {"heading": "Billing", "text": "We bill monthly.", "context_text": "Handbook > Billing\n\nWe bill monthly."},
            #  {"heading": "Billing > Refunds", "text": "Within 5 days.",
            #   "context_text": "Handbook > Billing > Refunds\n\nWithin 5 days."},
            #  {"heading": "Support > Email", "text": "help@x.io", "context_text": "Handbook > Support > Email\n\nhelp@x.io"}]
            ```
            (The `# Support` section has no text of its own, so it is skipped.)
        ''',
        "starter": r'''
            def markdown_chunks(markdown, title):
                ...
        ''',
        "tests": r'''
            from solution import markdown_chunks

            MD = "Welcome!\n# Billing\nWe bill monthly.\n## Refunds\nWithin 5 days.\n# Support\n## Email\nhelp@x.io"

            def test_full_example():
                got = markdown_chunks(MD, "Handbook")
                want = [
                    {"heading": "", "text": "Welcome!", "context_text": "Handbook\n\nWelcome!"},
                    {"heading": "Billing", "text": "We bill monthly.", "context_text": "Handbook > Billing\n\nWe bill monthly."},
                    {"heading": "Billing > Refunds", "text": "Within 5 days.",
                     "context_text": "Handbook > Billing > Refunds\n\nWithin 5 days."},
                    {"heading": "Support > Email", "text": "help@x.io", "context_text": "Handbook > Support > Email\n\nhelp@x.io"},
                ]
                assert got == want, f"got {got!r}"

            def test_new_h1_clears_h2():
                md = "# A\n## B\nb text\n# C\nc text"
                got = [c["heading"] for c in markdown_chunks(md, "T")]
                assert got == ["A > B", "C"], f"got {got!r}"

            def test_multiline_text_is_joined_and_stripped():
                md = "# A\n\nline one\nline two\n\n"
                got = markdown_chunks(md, "T")
                assert got == [{"heading": "A", "text": "line one\nline two",
                                "context_text": "T > A\n\nline one\nline two"}], f"got {got!r}"

            def test_h2_without_h1():
                got = markdown_chunks("## Only\ntext", "T")
                assert got[0]["heading"] == "Only" and got[0]["context_text"] == "T > Only\n\ntext", f"got {got!r}"

            def test_hash_without_space_is_text():
                got = markdown_chunks("# A\n#hashtag here", "T")
                assert got[0]["text"] == "#hashtag here", f"got {got!r}"

            def test_empty_document():
                assert markdown_chunks("", "T") == [] and markdown_chunks("# Just a heading", "T") == []
        ''',
        "solution": r'''
            def markdown_chunks(markdown, title):
                chunks = []
                h1 = h2 = ""
                lines = []

                def flush():
                    text = "\n".join(lines).strip()
                    if not text:
                        return
                    heading = " > ".join(h for h in (h1, h2) if h)
                    prefix = f"{title} > {heading}" if heading else title
                    chunks.append({"heading": heading, "text": text, "context_text": f"{prefix}\n\n{text}"})

                for line in markdown.split("\n"):
                    if line.startswith("# "):
                        flush()
                        lines = []
                        h1, h2 = line[2:].strip(), ""
                    elif line.startswith("## "):
                        flush()
                        lines = []
                        h2 = line[3:].strip()
                    else:
                        lines.append(line)
                flush()
                return chunks
        ''',
        "hints": [
            "Walk the lines once, remembering the current level-1 and level-2 headings and the lines of the current section.",
            "Every time a heading line appears, first finish (\"flush\") the section collected so far using the headings that were active for it, then update the headings. Flush once more at the end.",
            "Keep h1, h2 and a list of lines; on \"# \" flush, reset lines, set h1 and clear h2; on \"## \" flush, reset lines, set h2; else append the line. Flushing joins the lines with \"\\n\", strips, skips empty text, builds heading from the non-empty of h1/h2 joined by \" > \", and the context_text prefix.",
        ],
    },
    # ------------------------------------------------------------------ difficulty 3
    {
        "id": "chunking-9",
        "title": "Chunks within a token budget",
        "difficulty": 3,
        "prompt": r'''
            Your embedding model accepts at most `max_tokens` tokens per input. Pack
            sentences into chunks under that budget, measuring with the tokenizer you are given.

            **Write:** `budget_chunks(sentences, max_tokens, count_tokens)`

            - `sentences`: a list of sentence strings
            - `max_tokens`: a positive int
            - `count_tokens`: a function `count_tokens(text) -> int` (the tokenizer, injected so tests can use a fake one)
            - **Returns:** a list of chunk strings

            **Rules**
            - Pack sentences greedily, joined with one space: add the next sentence if
              `count_tokens(current + " " + sentence) <= max_tokens`; otherwise close the chunk and start a new one.
              Always measure the joined text with `count_tokens` (don't add up per-sentence counts).
            - A sentence with `count_tokens(sentence) > max_tokens` is split by words: close the current chunk
              (if any), then pack that sentence's words greedily (joined with one space) under the same budget,
              and add those pieces as chunks. A single word over budget is its own piece. Packing then
              continues with a fresh chunk.
            - Empty `sentences` returns `[]`.

            **Examples**
            ```python
            def words(text):
                return len(text.split())

            budget_chunks(["a b.", "c d.", "e."], 4, words)          # returns ["a b. c d.", "e."]
            budget_chunks(["x.", "a b c d e f g.", "y."], 3, words)
            # returns ["x.", "a b c", "d e f", "g.", "y."]
            budget_chunks([], 5, words)                               # returns []
            ```
        ''',
        "starter": r'''
            def budget_chunks(sentences, max_tokens, count_tokens):
                ...
        ''',
        "tests": r'''
            from solution import budget_chunks

            def words(text):
                return len(text.split())

            def chars4(text):
                return (len(text) + 3) // 4

            def test_packs_by_word_count():
                got = budget_chunks(["a b.", "c d.", "e."], 4, words)
                assert got == ["a b. c d.", "e."], f"got {got!r}"

            def test_long_sentence_split_by_words():
                got = budget_chunks(["x.", "a b c d e f g.", "y."], 3, words)
                assert got == ["x.", "a b c", "d e f", "g.", "y."], f"got {got!r}"

            def test_uses_the_given_tokenizer():
                got = budget_chunks(["Hello there.", "Hi.", "Refunds take five days."], 4, chars4)
                assert got == ["Hello there. Hi.", "Refunds take", "five days."], f"got {got!r}"

            def test_measures_joined_text():
                calls = []
                def spy(text):
                    calls.append(text)
                    return len(text.split())
                budget_chunks(["a.", "b."], 5, spy)
                assert "a. b." in calls, f"count_tokens was called with {calls!r}"

            def test_single_huge_word():
                got = budget_chunks(["tiny.", "supercalifragilistic word."], 2, chars4)
                assert got == ["tiny.", "supercalifragilistic", "word."], f"got {got!r}"

            def test_empty():
                assert budget_chunks([], 5, words) == []
        ''',
        "solution": r'''
            def pack(pieces, max_tokens, count_tokens):
                chunks = []
                current = ""
                for piece in pieces:
                    candidate = piece if not current else current + " " + piece
                    if not current or count_tokens(candidate) <= max_tokens:
                        current = candidate
                    else:
                        chunks.append(current)
                        current = piece
                if current:
                    chunks.append(current)
                return chunks

            def budget_chunks(sentences, max_tokens, count_tokens):
                chunks = []
                current = ""
                for sentence in sentences:
                    if count_tokens(sentence) > max_tokens:
                        if current:
                            chunks.append(current)
                            current = ""
                        chunks.extend(pack(sentence.split(), max_tokens, count_tokens))
                        continue
                    candidate = sentence if not current else current + " " + sentence
                    if count_tokens(candidate) <= max_tokens:
                        current = candidate
                    else:
                        chunks.append(current)
                        current = sentence
                if current:
                    chunks.append(current)
                return chunks
        ''',
        "hints": [
            "It's 'Pack sentences into chunks' with len() replaced by count_tokens, plus the oversized-sentence rule from 'Paragraph-aware chunks'.",
            "Write a small greedy packing helper that takes pieces, the budget and the counter. Use it for the words of an oversized sentence; the main loop handles sentences.",
            "Main loop: if count_tokens(sentence) > max_tokens, flush current and extend chunks with the helper's result on sentence.split(), then continue; else build the candidate, keep it if count_tokens(candidate) <= max_tokens, otherwise append current and restart with the sentence. Append the last current. In the helper, a piece always goes into an empty current even if it's too big.",
        ],
    },
]
