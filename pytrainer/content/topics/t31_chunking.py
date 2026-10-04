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
            ## Read a long string a piece at a time

            Your search app should retrieve a relevant passage rather than an entire long document. Start with a predictable rule: take a fixed number of characters at each position, then move forward. Python slices make the shorter final piece work without special padding.

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

            ```quiz
            What happens if a slice stops beyond the end of the string?
            - [x] It returns the available characters :: Slices do not require their stop to be within the string.
            - [ ] It raises IndexError :: A direct out-of-range index does, but a slice is different.
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

            ```predict
            text = "notebook"
            print(text[6:10])
            print(len(text[6:10]))
            ---
            Only the last two characters exist in that range, so the slice is shorter than four.
            ```

            **Watch out:** The range produces starting positions, not the text pieces themselves. You still need to use each start to select a slice of the original text.

            **In short:** Start positions tell you where to cut; slices give you the available characters.
        ''',
        "prompt": r'''
            Read the program, then enter exactly what its print calls display, one output line per line.
        ''',
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
            Read the output from top to bottom. `range(0, 10, 4)` gives the starts `0, 4, 8`. The slices are `text[0:4]`,
            `text[4:8]` and `text[8:12]`; the last one runs past the end, so it only
            holds the remaining `"ij"`.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Find the start positions generated by the range.",
            "Each start selects at most the requested number of characters.",
            "Write the slices in order, then evaluate the list length and the final selected piece.",
        ],
    },
    {
        "id": "chunking-s2",
        "title": "Fixed-size chunks",
        "difficulty": 0,
        "lesson": r'''
            ## Make successive pieces meet without gaps

            You want every character to appear once across a list of equally sized pieces. The distance between starts must match the width of each piece. A smaller distance repeats characters, while a larger one leaves characters out.

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

            ```quiz
            What does a step larger than the slice width cause?
            - [x] Gaps :: The next start skips past characters not included in the previous piece.
            - [ ] More overlap :: Overlap occurs when starts are closer than the piece width.
            ```

            The list comprehension (from the comprehensions chapter) builds the whole
            list of chunks in one expression.

            Chunk size affects the amount of context in a result. Choose it by testing your documents and retrieval task; there is no single size that fits every application.

            Empty text needs no special case. `len("")` is `0`, and `range(0, 0, size)`
            produces no numbers, so the result is `[]`.

            ```order
            text = "abcdef"
            positions = range(0, len(text), 2)
            print([text[p:p + 2] for p in positions])
            ---
            The text length determines the starts, then each start selects its piece.
            ```

            **Watch out:** A size of zero cannot be a range step. This introductory task supplies valid positive sizes; later tasks require you to validate their settings.

            **In short:** For adjacent fixed-size pieces, advance by the same size you slice.
        ''',
        "prompt": r'''
            Cut text into pieces of a fixed number of characters. Complete the function by
            replacing the `___`.

            **Your job:** write `chunk_chars(text, size)`

            **What goes in**
            - `text`: a string, e.g. `"abcdefg"`
            - `size`: a positive int, the chunk length, e.g. `3`

            **What comes out**
            - Return a list of strings, each `size` characters long except possibly the last

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
            "The range step determines where the next piece begins.",
            "Adjacent pieces need a jump equal to their width.",
            "Match the distance between starts to the requested size while leaving the slicing expression intact.",
        ],
    },
    {
        "id": "chunking-s3",
        "title": "Fix: word chunks",
        "difficulty": 0,
        "lesson": r'''
            ## Keep whole words together

            A character cut can separate the beginning of a word from its ending. When you want whole words, split the text into a word list first. The familiar slice rules now count words, and joining each selected group turns it back into text.

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

            ```quiz
            Does splitting and rejoining preserve repeated spaces?
            - [x] No :: Whitespace splitting followed by a single-space join normalizes the spacing.
            - [ ] Yes :: The original separator characters are not retained in the word list.
            ```

            `text.split()` with no argument splits on any run of whitespace: spaces,
            newlines and tabs. It never returns empty strings. `" ".join(items)` builds
            one string from a list of strings, with a single space between the items.

            Words and characters are different measuring units. Neither is an exact count of model **tokens**, which depend on how the model tokenizer splits the text.

            The step of `range` must equal the chunk size. With a smaller step, a new
            chunk starts before the previous one ends, so words appear in more than one
            chunk.

            ```predict
            words = "one	two   three".split()
            print(len(words))
            print(" ".join(words))
            ---
            Whitespace runs separate words but are not kept as output items.
            ```

            **Watch out:** Word counts are not exact token counts. Tokens depend on the model tokenizer, and this exercise defines a chunk size in whitespace-separated words.

            **In short:** Split into words, group those words, then join each group using the required spacing.
        ''',
        "prompt": r'''
            `chunk_words` should split text into chunks of `size` words, but its chunks
            repeat words over and over. Fix the bug.

            **Your job:** write `chunk_words(text, size)`

            **What goes in**
            - `text`: a string, e.g. `"a b c d e"`
            - `size`: a positive int, words per chunk

            **What comes out**
            - Return a list of strings; each chunk is up to `size` words joined with single spaces

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
            "Inspect how far the loop advances through the word list.",
            "A new start at every word repeats words when a piece holds several words.",
            "Align the start spacing with the requested group size, then keep the existing joining behavior.",
        ],
    },
    {
        "id": "chunking-s4",
        "title": "How many chunks?",
        "difficulty": 0,
        "lesson": r'''
            ## Count a final partial piece

            You want to estimate the number of pieces before building them. Several full groups may fit, with a little text left over. That remainder still needs its own piece, so rounding to the nearest whole number is the wrong operation.

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

            ```quiz
            How many size-five pieces are needed for eleven characters?
            - [x] Three :: Two full pieces leave one character that still needs a third piece.
            - [ ] Two :: That would leave the final character uncounted.
            ```

            Adding `size - 1` moves any length that has a remainder up to or past the
            next multiple of `size`. A length that is already a multiple of `size`
            stays below the next multiple, so its result does not change.

            Ceiling division gives the number of non-overlapping chunks before you create them. The number of embedding calls also depends on how many chunks each call can process.

            `round(10 / 4)` returns `2`, not `3`. `round` rounds a value that ends in
            `.5` to the nearest even number.

            ```predict
            length, width = 13, 6
            print(length // width)
            print(length % width)
            ---
            There are two complete groups and one leftover character; the remainder is separate from the group count.
            ```

            **Watch out:** An exact multiple needs no extra piece. Check the empty case too: no content means no pieces, not one empty piece.

            **In short:** Count full groups and add one only when a remainder exists.
        ''',
        "prompt": r'''
            Before chunking, estimate how many chunks (and embedding calls) a document needs.

            **Your job:** write `count_chunks(length, size)`

            **What goes in**
            - `length`: an int >= 0, the text length in characters, e.g. `10`
            - `size`: a positive int, the chunk size, e.g. `4`

            **What comes out**
            - Return an int, the number of fixed-size chunks (the last one may be partial)

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
            "A leftover character still needs a whole piece.",
            "Use an operation that rounds the number of groups upward, not to the nearest integer.",
            "Compute the ceiling of the length divided by the width, preserving zero and exact multiples.",
        ],
    },
    {
        "id": "chunking-s5",
        "title": "Split into paragraphs",
        "difficulty": 0,
        "lesson": r'''
            ## Use blank lines as document boundaries

            A document already has paragraph breaks that may make better cut points than a fixed character count. Split at the precise separator this task defines, clean each resulting piece, and ignore pieces that contain no text after cleaning.

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

            ```quiz
            Why filter after stripping each piece?
            - [x] A piece containing only spaces becomes empty :: Filtering the original nonempty string would retain it.
            - [ ] Stripping creates new paragraph breaks :: It only removes whitespace at the edges.
            ```

            `text.split("\n\n")` cuts the string at every `"\n\n"`. Four newlines in a
            row contain two separators with nothing between them, so the list gets an
            empty string. `p.strip()` removes whitespace from both ends of a piece. The
            condition `if p.strip()` drops a piece that is empty after stripping,
            because an empty string counts as false.

            Cutting between the document's own parts is called **structure-aware**
            chunking. Each chunk then holds complete paragraphs.

            ```fill
            parts = [" intro ", "   "]
            print([p.strip() for p in parts if ___])
            ---
            - [x] p.strip() :: Only pieces with text after cleanup are retained.
            - [ ] p :: A spaces-only piece is nonempty before cleanup.
            ```

            **Watch out:** The task uses two consecutive newline characters as its separator. A blank line containing spaces is a different sequence; do not assume this rule recognizes every document format.

            **In short:** Split at the defined paragraph boundary, trim each piece, and discard empty results.
        ''',
        "prompt": r'''
            Split a document into its paragraphs.

            **Your job:** write `split_paragraphs(text)`

            **What goes in**
            - `text`: a string where paragraphs are separated by blank lines (`"\n\n"`)

            **What comes out**
            - Return a list of paragraph strings, in order

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
            "The separator is a pair of newline characters.",
            "Cleanup can turn a nonempty spaces-only piece into an empty one.",
            "Split at the specified boundary, strip every piece, and keep only cleaned pieces containing text.",
        ],
    },
    {
        "id": "chunking-s6",
        "title": "Overlapping chunks",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## Repeat some text across a cut

            A useful sentence may straddle the cut between two pieces. Repeating a small part of the previous piece gives the next one some nearby context. That changes how far you advance while leaving the maximum piece width unchanged.

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

            ```quiz
            If width is six and overlap is two, how far apart are starts?
            - [x] Four :: Each new piece repeats the last two positions of the previous one.
            - [ ] Eight :: That would skip characters rather than repeat them.
            ```

            `range(0, 10, 3)` gives the starts `0, 3, 6, 9`. The chunk at `3` begins with
            `"de"`, the last 2 characters of the chunk before it.

            Move the sliders to see how the step and the chunks change.

            ```diagram
            {"type":"chunks","title":"Chunks of text with size 5 and overlap 2","text":"abcdefghij","size":5,"overlap":2}
            ```

            More overlap repeats more text and increases storage. Its usefulness depends on the documents and should be measured.

            The overlap must be smaller than the size. If they are equal, the step is
            `0` and `range` raises `ValueError`. If the overlap is larger, the step is
            negative and `range` produces no starts.

            ```predict
            text = "abcdefgh"
            print(text[0:5])
            print(text[3:8])
            ---
            The two slices share the characters at positions three and four.
            ```

            **Watch out:** The overlap must allow forward progress. When it equals the width, the step is zero and range raises ValueError rather than generating useful starts.

            **In short:** Overlap reduces the distance between starts so neighboring chunks share text.
        ''',
        "prompt": r'''
            Read the program, then enter exactly what its print calls display, one output line per line.
        ''',
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
            Read the output from top to bottom. The step is `4 - 1 = 3`, so the starts are `0, 3, 6`. Each chunk is 4
            characters from its start: `abcd`, `defg` (it repeats the `d`), and `gh`,
            which runs out of text.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Work out the distance between starts before taking any slices.",
            "The piece width remains fixed while overlap shortens that distance.",
            "List the generated starts, select each corresponding slice, then follow the two print calls in order.",
        ],
    },
    # ------------------------------------------------------------------ difficulty 1
    {
        "id": "chunking-1",
        "title": "Overlap done right",
        "difficulty": 1,
        "lesson": r'''
            ## Stop after a piece covers the end

            Your overlapping slices cover every character, but the final slice sometimes repeats only text already covered. That extra piece adds storage without adding content. Notice when the piece you have just made already reaches the end, and stop there.

            With size 4 and overlap 1 on `"abcdefg"` (7 letters), `range(0, 7, 3)` gives
            the starts `0, 3, 6`. The chunks are `"abcd"`, `"defg"` and `"g"`. The last
            chunk holds only the `"g"` that `"defg"` already contains. It adds no new
            text.

            To avoid it, stop as soon as a chunk reaches the end of the text. A chunk
            that starts at `position` reaches the end when `position + size >= len(text)`.

            ```python
            text, size, step = "abcdefg", 4, 3
            position = 0
            while True:
                piece = text[position:position + size]
                print(position, piece)
                if position + size >= len(text):
                    break
                position += step
            # 0 abcd
            # 3 defg
            ```

            ```quiz
            When is another overlapping piece unnecessary?
            - [x] The current piece already reaches the end :: Any further piece would contain only previously covered trailing text.
            - [ ] The current piece overlaps the previous one :: Overlap itself is intentional.
            ```

            `while True` repeats until `break` runs. The loop takes a chunk first and
            checks the end condition after, so it always produces at least one chunk.
            Handle empty text before the loop.

            **Validating input** means checking the arguments at the position of a function
            and raising an exception such as `ValueError` when they are not usable. Here
            the overlap is not usable when it is negative or not smaller than the size.

            ```predict
            text = "abcdefgh"
            print(text[4:8])
            print(text[6:10])
            ---
            The second displayed slice adds no characters beyond those already in the first.
            ```

            **Watch out:** A loop that emits a piece before checking the end needs an explicit empty-input policy. Otherwise it can produce a spurious empty string for an empty document.

            **In short:** Keep overlap, but stop as soon as the current piece covers the end of the document.
        ''',
        "prompt": r'''
            Cut text into character chunks that overlap, without a useless extra chunk at the end.

            **Your job:** write `chunk_with_overlap(text, size, overlap)`

            **What goes in**
            - `text`: a string
            - `size`: a positive int, chunk length
            - `overlap`: an int, how many characters each chunk shares with the previous one

            **What comes out**
            - Return a list of strings

            **Rules**
            - The first chunk starts at the beginning. Each next start advances by the chunk size minus the overlap.
            - Each chunk contains at most `size` consecutive characters from its starting position.
            - Stop after the first chunk covering the final character; do not add a piece containing only repeated trailing text.
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
            "A piece that reaches the end has already covered all remaining text.",
            "Validate settings before entering a loop that must advance.",
            "Check overlap, handle empty text, produce each piece, stop after coverage reaches the end, and otherwise move forward by the overlap-adjusted distance.",
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
            ## Cut at the sentence boundaries the task defines

            A dot in a decimal or a website name should not always end a sentence. This step uses punctuation plus surrounding whitespace to decide where to cut. Read that rule as a precise text-processing contract, not a complete understanding of natural language.

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

            ```quiz
            Why does the rule keep a decimal such as 4.2 together?
            - [x] Its dot is followed by a digit :: There is no required whitespace boundary after that dot.
            - [ ] Numbers cannot contain sentence punctuation :: The characters overlap; context determines this rule's behavior.
            ```

            The loop adds each character to `current`. `nxt` is the following character,
            or a space when there is none. `nxt.isspace()` is `True` when the string holds
            only whitespace. When `ch` is `;` and `nxt` is whitespace, the
            loop appends `current` to `parts` and starts a new empty `current`. The `;`
            in `b;c` is followed by `c`, so no cut happens there.

            `re.split` can do the same in one call with a **lookbehind**. The pattern
            `(?<=X)` requires `X` directly before the match but does not include it in
            the match. See the research link.

            ```predict
            text = "4.2 done."
            print(text[2].isspace())
            print(" ".isspace())
            ---
            The character after the decimal point is not whitespace, while a space is.
            ```

            **Watch out:** Abbreviations and other writing conventions can fool this small rule. The exercise tests its stated behavior rather than a full language-aware sentence segmenter.

            **In short:** Use the complete boundary condition and preserve the punctuation attached to each sentence.
        ''',
        "prompt": r'''
            Split text into sentences, so chunks can be cut on sentence borders.

            **Your job:** write `split_sentences(text)`

            **What goes in**
            - `text`: a string, e.g. `"Hi there. How are you? Fine!"`

            **What comes out**
            - Return a list of sentence strings, in order

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
            "The punctuation alone is not the whole boundary rule.",
            "Keep punctuation with its sentence and use following whitespace to identify cuts.",
            "Find the permitted boundaries, preserve punctuation, strip resulting pieces, and discard empty pieces.",
        ],
    },
    {
        "id": "chunking-3",
        "title": "Label every chunk",
        "difficulty": 1,
        "lesson": r'''
            ## Keep the source beside each piece

            A search result is only a short string, but the user wants to open the document it came from. Store the document identity and the piece's position alongside the text when you create it. Trying to reconstruct that link later is harder and can be ambiguous.

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

            ```quiz
            What does a source-and-position identifier depend on?
            - [x] The source name and current chunk order :: Rechunking changed text can change what a position refers to.
            - [ ] Only the text's meaning :: These identifiers are not semantic fingerprints.
            ```

            `enumerate(chunks)` produces pairs of an index and an item, starting at
            index `0`. The loop assigns them to `i` and `text`.

            An id built from the source name and index is a **position-based id**. Processing unchanged text with unchanged settings produces the same ids. When you later store these
            chunks alongside their embeddings, the store can replace the old chunks
            instead of keeping duplicates.

            ```match
            text :: the passage itself
            source :: the document it came from
            index :: its position in that document
            id :: the identifier used to refer to the chunk
            ```

            **Watch out:** Position-based ids are stable only for the same source identity and chunking order. If a document changes, update or remove obsolete stored chunks rather than assuming all ids still describe the same text.

            **In short:** Attach source and position information when creating chunks, before that context is lost.
        ''',
        "prompt": r'''
            Attach metadata to each chunk of a document.

            **Your job:** write `with_metadata(chunks, source)`

            **What goes in**
            - `chunks`: a list of chunk strings
            - `source`: a string naming the document, e.g. `"faq.md"`

            **What comes out**
            - Return a list of dicts, one per chunk, in order:
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
            "Each output record needs both the text and its location in the input sequence.",
            "A counter paired with each chunk supplies the position.",
            "Visit chunks in order, build their source-based ids and positions, and return one new record per chunk.",
        ],
    },
    {
        "id": "chunking-4",
        "title": "Pack sentences into chunks",
        "difficulty": 1,
        "lesson": r'''
            ## Pack complete sentences while counting separators

            You have already split a document into sentences. Now you want to combine neighboring sentences without exceeding a target size where possible. Test the complete candidate, including the space you insert between sentences, before accepting another one.

            **Greedy packing** builds chunks from whole sentences. You go through the
            sentences in order and keep one current chunk. If the current chunk plus the
            next sentence is within the limit, the sentence joins the current chunk.
            Otherwise you close the current chunk and start a new one with that sentence.

            Each completed chunk ends at a sentence boundary. The choices are made in order without revisiting earlier grouping decisions.

            ```python
            limit = 12
            current = "Hi."
            for nxt in ["Yes.", "Goodbye now."]:
                candidate = current + " " + nxt
                print(repr(candidate), len(candidate), len(candidate) <= limit)
            # 'Hi. Yes.' 8 True
            # 'Hi. Goodbye now.' 16 False
            ```

            ```quiz
            Does joining two sentences add a character here?
            - [x] Yes :: The joining space is part of the new string and its measured length.
            - [ ] No :: Measuring only the separate sentences omits the separator.
            ```

            The **candidate** is the current chunk, a space, and the next sentence.
            Measure the candidate, not the two parts separately, because the joining
            space adds one character.

            A single sentence can be longer than the limit. This function does not
            split sentences, so that sentence becomes a chunk on its own.

            ```predict
            left, right = "Go.", "Wait."
            print(len(left) + len(right))
            print(len(left + " " + right))
            ---
            The second measurement includes the one-character separator.
            ```

            **Watch out:** This contract keeps a sentence intact even if that one sentence exceeds the limit. The size target is therefore not an absolute guarantee for every resulting chunk.

            **In short:** Measure the proposed joined string and keep a too-long single sentence intact as required.
        ''',
        "prompt": r'''
            Group sentences into chunks no longer than a character limit.

            **Your job:** write `pack_sentences(sentences, max_chars)`

            **What goes in**
            - `sentences`: a list of sentence strings, e.g. `["Hi.", "Yes.", "Goodbye now."]`
            - `max_chars`: a positive int

            **What comes out**
            - Return a list of chunk strings; each chunk is consecutive sentences joined with one space

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
            "Track the unfinished chunk separately from completed chunks.",
            "Measure the joined candidate, including the inserted space.",
            "Try adding each sentence, finish the current chunk when the candidate is too large, start the next one, and flush the final unfinished chunk.",
        ],
    },
    {
        "id": "chunking-5",
        "title": "Chunks with offsets",
        "difficulty": 1,
        "lesson": r'''
            ## Record the original start and stopping positions

            An answer cites a passage and your interface wants to highlight it inside the original document. Store the exact slice boundaries with the passage. Those numbers make sense only against the same original text and the same character-counting convention.

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

            ```quiz
            What does the stored end position identify?
            - [x] The boundary after the last included character :: It matches Python's exclusive slice stop.
            - [ ] The final included character :: That would need a different slicing convention.
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

            ```predict
            document = "Red green blue"
            start, stop = 4, 9
            print(document[start:stop])
            print(stop - start)
            ---
            The slice selects green and the boundary difference gives its five-character length.
            ```

            **Watch out:** A slice tolerates a stop beyond the string, but recorded metadata should not claim nonexistent characters. Cap the stored endpoint at the actual document length.

            **In short:** Offsets describe an exact slice of the original text, with an exclusive endpoint.
        ''',
        "prompt": r'''
            Cut text into fixed-size character chunks and record where each one came from.

            **Your job:** write `chunk_spans(text, size)`

            **What goes in**
            - `text`: a string
            - `size`: a positive int, chunk length

            **What comes out**
            - Return a list of dicts `{"start": int, "end": int, "text": str}`, in order

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
            "The slice boundaries also become the metadata.",
            "The final endpoint cannot exceed the length of the original text.",
            "Visit fixed-size start positions, determine each capped endpoint, and store the boundaries with the exact slice between them.",
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

            **Your job:** write `chunk_document(doc, size, overlap)`

            **What goes in**
            - `doc`: a dict `{"id": str, "title": str, "text": str}`
            - `size`: a positive int, words per chunk
            - `overlap`: an int, words shared with the previous chunk

            **What comes out**
            - Return a list of dicts, one per chunk, in order:
              `{"id": "<doc id>-<index>", "doc_id": ..., "title": ..., "index": int, "text": str}`

            **Rules**
            - Split `text` into words on any whitespace; chunk text is its words joined with single spaces.
            - The first chunk starts at the first word. Each subsequent start advances by the size minus overlap, with up to `size` words per chunk.
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
            "Combine word grouping, overlap stopping, and metadata from earlier steps.",
            "The same start position controls both the selected words and end-of-document stopping.",
            "Validate settings, split into words, produce ordered labeled groups, and stop after the group that reaches the final word.",
        ],
    },
    {
        "id": "chunking-7",
        "title": "Paragraph-aware chunks",
        "difficulty": 2,
        "prompt": r'''
            Chunk a document along its paragraphs: merge small paragraphs together, cut up
            paragraphs that are too big.

            **Your job:** write `paragraph_chunks(text, max_chars)`

            **What goes in**
            - `text`: a string with paragraphs separated by blank lines (`"\n\n"`)
            - `max_chars`: a positive int

            **What comes out**
            - Return a list of chunk strings, every one at most `max_chars` long

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
            "Oversized paragraphs need a different path from paragraphs that can be packed whole.",
            "Finish the current group before adding slices of an oversized paragraph.",
            "Clean paragraphs, split oversized ones as specified, greedily join the others with blank-line separators, and flush the final group.",
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

            **Your job:** write `markdown_chunks(markdown, title)`

            **What goes in**
            - `markdown`: a string of Markdown lines; `# ` lines are level-1 headings, `## ` lines are level-2 headings
            - `title`: the document title, e.g. `"Handbook"`

            **What comes out**
            - Return a list of dicts `{"heading": str, "text": str, "context_text": str}`, in document order

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
            "Headings affect the text after them, not text already collected.",
            "Finish the previous section before changing the active heading names.",
            "Track heading levels and body lines, flush on each new heading, reset the lower level where required, and flush once more at the end.",
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

            **Your job:** write `budget_chunks(sentences, max_tokens, count_tokens)`

            **What goes in**
            - `sentences`: a list of sentence strings
            - `max_tokens`: a positive int
            - `count_tokens`: a function `count_tokens(text) -> int` (the tokenizer, injected so tests can use a fake one)

            **What comes out**
            - Return a list of chunk strings

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
            "Use the supplied counter on complete candidate strings.",
            "An oversized sentence is split into words and packed using the same accounting principle.",
            "Process sentences in order, flush before oversized cases, pack their words as specified, then continue ordinary packing and finish the last chunk.",
        ],
    },
]
