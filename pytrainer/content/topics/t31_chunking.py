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

# The Library card for this chapter (shown once the chapter's steps are done).
# Every line that starts with `#` in an example is the real output of that example.
REFERENCE = {
    "keywords": ["chunk", "chunking", "split", "slice", "range", "size", "overlap", "step",
                 "ceiling division", "paragraph", "sentence", "re.split", "greedy packing",
                 "metadata", "offset", "token budget"],
    "cards": [
        {
            "syntax": "[text[i:i + size] for i in range(0, len(text), size)]",
            "explain": "Fixed-size chunks: range gives the start index of each chunk and the slice returns it. The last chunk can be shorter.",
            "example": r'''
                text = "Refunds take 5 days."
                size = 8
                print([text[i:i + size] for i in range(0, len(text), size)])
                # ['Refunds ', 'take 5 d', 'ays.']
            ''',
        },
        {
            "syntax": "(length + size - 1) // size",
            "explain": "Ceiling division: divides and rounds up. It gives the number of fixed-size chunks, with a partial last chunk counted.",
            "example": r'''
                print((10 + 4 - 1) // 4)
                # 3
                print((8 + 4 - 1) // 4)
                # 2
            ''',
        },
        {
            "syntax": "step = size - overlap",
            "explain": "Overlap: each chunk repeats the last `overlap` characters of the previous one. Needs 0 <= overlap < size.",
            "example": r'''
                text = "abcdefghij"
                size, overlap = 5, 2
                step = size - overlap
                print([text[i:i + size] for i in range(0, len(text), step)])
                # ['abcde', 'defgh', 'ghij', 'j']
            ''',
        },
        {
            "syntax": 'text.split("\\n\\n")',
            "explain": "Splits text into paragraphs at blank lines. Strip each piece and drop the pieces that are empty.",
            "example": r'''
                text = "Intro line.\n\n Second part. \n\n\n\nThird."
                parts = text.split("\n\n")
                print([p.strip() for p in parts if p.strip()])
                # ['Intro line.', 'Second part.', 'Third.']
            ''',
        },
        {
            "syntax": 're.split(r"(?<=[.!?])\\s+", text)',
            "explain": "Splits text into sentences: cuts at whitespace that follows . ! or ? and keeps the punctuation.",
            "example": r'''
                import re

                text = "Refunds take 3.5 days. Contact support!"
                print(re.split(r"(?<=[.!?])\s+", text))
                # ['Refunds take 3.5 days.', 'Contact support!']
            ''',
        },
        {
            "syntax": 'len(current + " " + piece) <= limit',
            "explain": "Greedy packing test: the piece joins the current chunk only if the joined text, separator included, fits the limit.",
            "example": r'''
                limit = 12
                current = "Hi."
                for piece in ["Yes.", "Goodbye now."]:
                    candidate = current + " " + piece
                    print(len(candidate), len(candidate) <= limit)
                # 8 True
                # 16 False
            ''',
        },
    ],
}

LESSON = r'''
## Why documents are chunked

A **chunk** is a piece of a longer document. A **RAG** (retrieval-augmented generation) app answers questions from your own
documents by finding the relevant text first and giving it to a language model. It splits each document into chunks, computes one embedding (a list of numbers
that represents the text) per chunk, and later puts only the most relevant chunks in the
prompt.

There are two reasons. A model's context window (the most tokens it can read in one
request) is limited, and every token in it costs money. One embedding for a 100-page manual
also has to represent every subject in the manual, so it is not very similar to the
embedding of any single question.

Large chunks match a question less precisely and use more tokens. Small chunks can lose the
surrounding text that a reader needs to understand them.

## Fixed-size chunks

**Fixed-size chunking** cuts the text every `size` characters. `range(0, len(text), size)`
produces the start index of each chunk, and the slice `text[i:i + size]` returns the chunk.

```python
text = "Refunds take 5 days."
size = 8
chunks = [text[i:i + size] for i in range(0, len(text), size)]
print(chunks)
# ['Refunds ', 'take 5 d', 'ays.']
```

To keep words whole, split the text into a list of words, slice the list, and join each
slice with spaces.

```python
words = "refunds are processed within five days".split()
size = 4
chunks = [" ".join(words[i:i + size]) for i in range(0, len(words), size)]
print(chunks)
# ['refunds are processed within', 'five days']
```

## Counting chunks

**Ceiling division** is division that rounds up. `(length + size - 1) // size` gives the
number of fixed-size chunks, and it counts a partial last chunk as one chunk.

```python
length, size = 10, 4
print((length + size - 1) // size)
# 3
```

10 characters with size 4 give chunks of 4, 4 and 2 characters. The formula computes
`(10 + 4 - 1) // 4`, which is `13 // 4`, which is `3`.

## Overlap

**Overlap** is the number of characters (or words) that a chunk repeats from the end of the
previous chunk. Text near a cut then appears in both chunks, so a sentence that is cut at the end of one
chunk can appear whole in the next one if the overlap is large enough. The distance between two chunk starts is the **step**: `size - overlap`.

```python
text = "Refunds take 5 days. Contact support."
size, overlap = 12, 4
step = size - overlap
chunks = [text[i:i + size] for i in range(0, len(text), step)]
print(step)
# 8
print(chunks)
# ['Refunds take', 'take 5 days.', 'ays. Contact', 'tact support', 'port.']
```

Move the sliders to see how size and overlap change the step and the chunks.

```diagram
{"type":"chunks","title":"Chunks of text with size 12 and overlap 4","text":"Refunds take 5 days. Contact support.","size":12,"overlap":4}
```

The overlap must be smaller than the size. Otherwise the step is zero or negative.

This formula can produce a last chunk that holds only repeated characters. The exercises
"Overlap done right" and "Chunk a document" use a different rule for the end: they stop
after the first chunk that reaches the end of the text (`start + size >= len(text)`).

```python
text = "abcdefg"
size, overlap = 4, 1
print([text[i:i + size] for i in range(0, len(text), size - overlap)])
# ['abcd', 'defg', 'g']
```

With the stop rule the result is `['abcd', 'defg']`, because `"defg"` already reaches the end.

## Structure-aware splitting

**Structure-aware chunking** cuts the text between the parts the document already has.
Paragraphs are separated by a blank line, which is the string `"\n\n"`. A sentence ends at
`.`, `!` or `?` followed by whitespace.

```python
import re

text = "Billing is monthly.\n\n\n\nRefunds take 5 days. Contact support!"
paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
print(paragraphs)
# ['Billing is monthly.', 'Refunds take 5 days. Contact support!']
print(re.split(r"(?<=[.!?])\s+", paragraphs[1]))
# ['Refunds take 5 days.', 'Contact support!']
```

`p.strip()` removes whitespace from both ends, and `if p.strip()` drops the empty pieces
that extra blank lines produce.

In the pattern, `\s+` matches a run of whitespace, and `re.split` cuts there. `(?<=[.!?])`
is a **lookbehind**: it requires `.`, `!` or `?` directly before the whitespace and does not
include that character in the match. The punctuation therefore stays in the sentence.

## Greedy packing

**Greedy packing** builds chunks from pieces such as sentences. You add the next piece to
the current chunk if the result is within the limit. Otherwise you close the current chunk
and start a new one with that piece. Measure the joined candidate, because the separator
counts too.

```python
limit = 20
current = "Billing is monthly."
candidate = current + " " + "Ok."
print(len(candidate), len(candidate) <= limit)
# 23 False
```

The current chunk has 19 characters, the space is 1 and `"Ok."` has 3. That is 23, which is
over the limit of 20, so `"Ok."` starts a new chunk.

A piece that is longer than the limit on its own has to be split further.

## Metadata

**Metadata** is the data you store next to the chunk text: `source` or `doc_id`, `index`,
`title`, and the **character offsets** `start` and `end`, which are the indexes in the
original text where the chunk begins and stops. Without metadata your app cannot show which
document a chunk came from.
An id built from the document and the index, such as `"faq-1"`, lets you update or delete
the chunk later.

```python
text = "Refunds take 5 days."
chunk = {"id": "faq-1", "source": "faq.md", "index": 1, "start": 8, "end": 12}
print(text[chunk["start"]:chunk["end"]])
# take
```

## Heading context

A chunk such as "It costs $5 per month." does not say what costs $5. Put the document title
and the **heading path** in front of the text you embed. The heading path is the list of
headings the chunk is under, from the outer one to the inner one. (Adding text to the
chunk before embedding it, so the chunk is findable on its own, is the same idea that
Anthropic calls contextual retrieval.)

```python
title, heading, text = "Handbook", "Pricing > Pro plan", "It costs $5 per month."
print(f"{title} > {heading}\n\n{text}")
# Handbook > Pricing > Pro plan
#
# It costs $5 per month.
```

Step through the stages to see what the data looks like after each one.

```diagram
{"type":"flow","title":"From document to stored chunks","steps":[
{"label":"Read","detail":"The document is one string. Blank lines separate its paragraphs.","code":"text = \"Billing is monthly.\\n\\n\\n\\nRefunds take 5 days. Contact support!\""},
{"label":"Split","detail":"text.split(\"\\n\\n\") cuts at blank lines. Each piece is stripped and empty pieces are dropped.","code":"['Billing is monthly.', 'Refunds take 5 days. Contact support!']"},
{"label":"Chunk","detail":"Small pieces are packed together up to the limit. With a limit of 40 characters the two paragraphs do not fit in one chunk, so each one becomes a chunk.","code":"chunks = ['Billing is monthly.', 'Refunds take 5 days. Contact support!']"},
{"label":"Attach metadata","detail":"Each chunk becomes a dict with an id, its source and its index.","code":"{'id': 'faq-0', 'source': 'faq.md', 'index': 0, 'text': 'Billing is monthly.'}\n{'id': 'faq-1', 'source': 'faq.md', 'index': 1, 'text': 'Refunds take 5 days. Contact support!'}"},
{"label":"Embed and store","detail":"The app computes one embedding per chunk text and stores it together with the metadata."}
]}
```

## Token budgets

Model limits are counted in tokens, not characters. Pass a `count_tokens(text)` function
to your chunker: a real **tokenizer** (the program that splits text into tokens and so can
count them), or an estimate such as `len(text) // 4`. Measure the
joined candidate chunk. The token counts of two pieces do not always add up to the count
of the joined text.

```python
def count_tokens(text):
    return len(text) // 4

print(count_tokens("Hi.") + count_tokens("Yes."))
# 1
print(count_tokens("Hi. Yes."))
# 2
```

`"Hi."` has 3 characters and `3 // 4` is `0`. `"Yes."` has 4 characters, which gives `1`.
The joined text has 8 characters, which gives `2`.

## Common mistakes

- `range(0, n, 0)` raises `ValueError`, and a negative step produces no starts at all.
  Check that `0 <= overlap < size` before you loop.
- `" ".join(words)` replaces newlines and repeated spaces with single spaces. Character
  offsets are only correct for chunks that are exact slices of the text.
- Empty input should return `[]`, not `[""]`. `"".split("\n\n")` returns `['']`, so filter
  out empty pieces.
'''

EXERCISES = [
    # ------------------------------------------------------------------ difficulty 0
    {
        "id": "chunking-s1",
        "title": "Slices in steps",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## Chunks and slices

            A **chunk** is a piece of a longer document. A RAG app splits each document
            into chunks so that each chunk can be embedded on its own and fits in the
            model's prompt.

            **Fixed-size chunking** cuts the text every `size` characters.
            `range(start, stop, step)` produces the index where each chunk starts. The
            slice `text[i:i + size]` returns the characters from index `i` up to, but not
            including, index `i + size`.

            ```python
            text = "hello world!"
            print(list(range(0, len(text), 5)))
            # [0, 5, 10]
            for i in range(0, len(text), 5):
                print(repr(text[i:i + 5]))
            # 'hello'
            # ' worl'
            # 'd!'
            ```

            Drag the handles to see which characters one slice returns.

            ```diagram
            {"type":"slice","title":"One chunk of text as a slice","name":"text","value":"hello world!","start":5,"stop":10}
            ```

            A slice whose stop is past the end of the string does not raise an error.
            Python returns the characters that exist. `text[10:15]` is `'d!'`, so the
            last chunk can be shorter than the others.

            Fixed-size chunking ignores words and sentences. Other chunking methods
            are usually compared against it.
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
            ## Chunk size

            The **chunk size** is the number of characters in each chunk. Store it in a
            variable so you can change it. Each chunk starts `size` characters after the
            previous one, and each slice is `size` characters long.

            ```python
            text = "retrieval"
            size = 3
            starts = list(range(0, len(text), size))
            print(starts)
            # [0, 3, 6]
            print([text[s:s + size] for s in starts])
            # ['ret', 'rie', 'val']
            ```

            The list comprehension (from the comprehensions chapter) builds the whole
            list of chunks in one expression.

            Chunk size is one of the most important settings in a RAG system. Real apps use a
            few hundred to a couple of thousand characters.

            Empty text needs no special case. `len("")` is `0`, and `range(0, 0, size)`
            produces no numbers, so the result is `[]`.
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
            ## Word chunks

            Slicing by characters can cut "refund" into "ref" and "und". A **word
            chunk** holds a fixed number of whole words instead. You split the text into
            a list of words, slice the list, and join each slice with spaces.

            ```python
            words = "the quick\nbrown   fox jumps".split()
            print(words)
            # ['the', 'quick', 'brown', 'fox', 'jumps']
            print(words[0:2])
            # ['the', 'quick']
            print(" ".join(words[0:2]))
            # the quick
            print(" ".join(words[4:6]))
            # jumps
            ```

            `text.split()` with no argument splits on any run of whitespace: spaces,
            newlines and tabs. It never returns empty strings. `" ".join(items)` builds
            one string from a list of strings, with a single space between the items.

            The number of words is a closer estimate of the number of **tokens** (the
            units a model counts) than the number of characters is.

            The step of `range` must equal the chunk size. With a smaller step, a new
            chunk starts before the previous one ends, so words appear in more than one
            chunk.
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
            ## Ceiling division

            A text of 10 characters with a chunk size of 4 gives chunks of 4, 4 and 2
            characters. That is 3 chunks. `10 / 4` is `2.5`, so the chunk count is the
            division result rounded up.

            Floor division `//` rounds down. To round up, add `size - 1` to the length
            before you divide. This is called **ceiling division**.

            ```python
            print(10 // 4)
            # 2
            print((10 + 4 - 1) // 4)
            # 3
            print((8 + 4 - 1) // 4)
            # 2
            print((0 + 4 - 1) // 4)
            # 0
            ```

            Adding `size - 1` moves any length that has a remainder up to or past the
            next multiple of `size`. A length that is already a multiple of `size`
            stays below the next multiple, so its result does not change.

            Ceiling division gives the number of chunks, and so the number of embedding
            calls, before you create any chunk. You can use it to estimate cost.

            `round(10 / 4)` returns `2`, not `3`. `round` rounds a value that ends in
            `.5` to the nearest even number.
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
            ## Paragraphs

            Fixed-size chunks can end in the middle of a sentence. A document is already
            divided into parts, and you can cut between them. A **paragraph** is a block of text separated
            from the next block by a blank line. A blank line is two newline characters
            in a row: `"\n\n"`.

            ```python
            text = "Intro line.\n\n Second part. \n\n\n\nThird."
            parts = text.split("\n\n")
            print(parts)
            # ['Intro line.', ' Second part. ', '', 'Third.']
            print([p.strip() for p in parts if p.strip()])
            # ['Intro line.', 'Second part.', 'Third.']
            ```

            `text.split("\n\n")` cuts the string at every `"\n\n"`. Four newlines in a
            row contain two separators with nothing between them, so the list gets an
            empty string. `p.strip()` removes whitespace from both ends of a piece. The
            condition `if p.strip()` drops a piece that is empty after stripping,
            because an empty string counts as false.

            Cutting between the document's own parts is called **structure-aware**
            chunking. Each chunk then holds complete paragraphs.
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
            ## Overlap

            A fixed-size cut can split a sentence across two chunks. Then neither chunk
            contains the whole sentence.

            **Overlap** is the number of characters (or words) that a chunk repeats from
            the end of the previous chunk. Text near a cut then appears in both chunks.
            The distance between two chunk starts is no longer `size`. It is
            `size - overlap`, which is called the **step**.

            ```python
            text = "abcdefghij"
            size, overlap = 5, 2
            step = size - overlap
            print(step)
            # 3
            print([text[i:i + size] for i in range(0, len(text), step)])
            # ['abcde', 'defgh', 'ghij', 'j']
            ```

            `range(0, 10, 3)` gives the starts `0, 3, 6, 9`. The chunk at `3` begins with
            `"de"`, the last 2 characters of the chunk before it.

            Move the sliders to see how the step and the chunks change.

            ```diagram
            {"type":"chunks","title":"Chunks of text with size 5 and overlap 2","text":"abcdefghij","size":5,"overlap":2}
            ```

            A common setting is an overlap of 10 to 20 percent of the chunk size.

            The overlap must be smaller than the size. If they are equal, the step is
            `0` and `range` raises `ValueError`. If the overlap is larger, the step is
            negative and `range` produces no starts.
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
            ## Stopping at the end of the text

            With size 4 and overlap 1 on `"abcdefg"` (7 letters), `range(0, 7, 3)` gives
            the starts `0, 3, 6`. The chunks are `"abcd"`, `"defg"` and `"g"`. The last
            chunk holds only the `"g"` that `"defg"` already contains. It adds no new
            text.

            To avoid it, stop as soon as a chunk reaches the end of the text. A chunk
            that starts at `start` reaches the end when `start + size >= len(text)`.

            ```python
            text, size, step = "abcdefg", 4, 3
            start = 0
            while True:
                piece = text[start:start + size]
                print(start, piece)
                if start + size >= len(text):
                    break
                start += step
            # 0 abcd
            # 3 defg
            ```

            `while True` repeats until `break` runs. The loop takes a chunk first and
            checks the end condition after, so it always produces at least one chunk.
            Handle empty text before the loop.

            **Validating input** means checking the arguments at the start of a function
            and raising an exception such as `ValueError` when they are not usable. Here
            the overlap is not usable when it is negative or not smaller than the size.
        ''',
        "prompt": r'''
            Cut text into character chunks that overlap, without a useless extra chunk at the end.

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
            chunk_with_overlap("abcdefg", 4, 1)    # returns ["abcd", "defg"]   (no "g" chunk)
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
            ## Sentences

            A paragraph can be longer than the chunk size you want. The next smaller
            unit is the **sentence**. In this chapter a sentence ends at `.`, `!` or `?`
            when that character is followed by whitespace or by the end of the text.

            The "followed by whitespace" condition is required. `3.5` and `example.com`
            contain dots, but no sentence ends there.

            This example uses the same rule with a different character. It cuts after
            every `;` that is followed by whitespace, and it keeps the `;`.

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
            # ['a;', 'b;c;', 'd']
            ```

            The loop adds each character to `current`. `nxt` is the following character,
            or a space when there is none. `nxt.isspace()` is `True` when the string holds
            only whitespace. When `ch` is `;` and `nxt` is whitespace, the
            loop appends `current` to `parts` and starts a new empty `current`. The `;`
            in `b;c` is followed by `c`, so no cut happens there.

            `re.split` can do the same in one call with a **lookbehind**. The pattern
            `(?<=X)` requires `X` directly before the match but does not include it in
            the match. See the research link.
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
            ## Chunk metadata

            **Metadata** is data about a chunk that you store next to its text: which
            document it came from and its position in that document. When a search
            result is only a string, your app cannot show which document it came from.
            You also cannot find and delete it when its document changes.

            Store each chunk as a dict that holds the text and the metadata.

            ```python
            chunks = ["Billing is monthly.", "Cancel any time."]
            for i, text in enumerate(chunks):
                print({"id": f"pricing:{i}", "index": i, "text": text})
            # {'id': 'pricing:0', 'index': 0, 'text': 'Billing is monthly.'}
            # {'id': 'pricing:1', 'index': 1, 'text': 'Cancel any time.'}
            ```

            `enumerate(chunks)` produces pairs of an index and an item, starting at
            index `0`. The loop assigns them to `i` and `text`.

            An id built from the source name and the index is a **stable id**. Chunking
            the same document again produces the same ids. When you later store these
            chunks alongside their embeddings, the store can replace the old chunks
            instead of keeping duplicates.
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
            ## Greedy packing

            **Greedy packing** builds chunks from whole sentences. You go through the
            sentences in order and keep one current chunk. If the current chunk plus the
            next sentence is within the limit, the sentence joins the current chunk.
            Otherwise you close the current chunk and start a new one with that sentence.

            Every chunk then ends at the end of a sentence and is as long as the limit
            allows.

            ```python
            limit = 12
            current = "Hi."
            for nxt in ["Yes.", "Goodbye now."]:
                candidate = current + " " + nxt
                print(repr(candidate), len(candidate), len(candidate) <= limit)
            # 'Hi. Yes.' 8 True
            # 'Hi. Goodbye now.' 16 False
            ```

            The **candidate** is the current chunk, a space, and the next sentence.
            Measure the candidate, not the two parts separately, because the joining
            space adds one character.

            A single sentence can be longer than the limit. This function does not
            split sentences, so that sentence becomes a chunk on its own.
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
            ## Character offsets

            A **character offset** is an index into the original text. A chunk has two
            offsets: `start`, where the chunk begins, and `end`, where it stops. With
            both stored, your app can highlight the exact passage an answer came from.

            ```python
            text = "Plans: Free, Pro, Team."
            start, end = 7, 11
            print(text[start:end])
            # Free
            print({"start": start, "end": end, "text": text[start:end]})
            # {'start': 7, 'end': 11, 'text': 'Free'}
            ```

            By convention `end` is **exclusive**: it is the index after the last
            character of the chunk, the same as the stop of a slice. The chunk is
            `text[start:end]` and its length is `end - start`.

            `start + size` can be larger than `len(text)` for the last chunk. The slice
            still works, but the stored `end` would be wrong, so `end` must not exceed
            `len(text)`.

            Offsets are only correct when the chunk is an exact slice of the original
            text. This exercise uses character chunks for that reason. Chunks built
            with `" ".join` of words can differ from the original spacing.
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
