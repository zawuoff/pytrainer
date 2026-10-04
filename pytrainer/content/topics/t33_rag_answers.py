TOPIC = {
    "id": "rag-answers",
    "title": "RAG Answers",
    "track": "rag",
    "order": 4,
    "requires": ["retrieval"],
    "summary": """
        From retrieved chunks to a trustworthy answer: numbered sources, grounded prompts,
        context budgets, saying "I don't know", extracting and validating citations, and a
        full retrieve-then-generate pipeline with fake `embed` and `llm` functions.
    """,
    "concepts": ["numbered sources", "grounded prompt", "context budget", "similarity threshold",
                 "declining to answer",                  "citations", "citation validation", "retry with feedback",
                 "RAG pipeline"],
}

# The Library card for this chapter (shown once the chapter's steps are done).
# Every line that starts with `#` in an example is the real output of that example.
REFERENCE = {
    "keywords": ["rag", "citation", "cite", "source", "sources", "grounded", "prompt",
                 "budget", "threshold", "decline", "hallucination", "numbered",
                 "findall", "top-k"],
    "cards": [
        {
            "syntax": "enumerate(chunks, start=1)",
            "explain": "Pairs each item with a counter that starts at 1, so citation [n] refers to item n, not n - 1.",
            "example": r'''
                chunks = ["Paris is in France.", "Rome is in Italy."]
                for n, text in enumerate(chunks, start=1):
                    print(f"[{n}] {text}")
                # [1] Paris is in France.
                # [2] Rome is in Italy.
            ''',
        },
        {
            "syntax": '"\\n".join(lines)',
            "explain": "Returns one string with one line per item and a newline between them. It adds no newline at the end.",
            "example": r'''
                lines = ["[1] Paris is in France.", "[2] Rome is in Italy."]
                print(repr("\n".join(lines)))
                # '[1] Paris is in France.\n[2] Rome is in Italy.'
            ''',
        },
        {
            "syntax": 're.findall(r"\\[(\\d+)\\]", answer)',
            "explain": "Returns the digits inside every [n] citation as strings, in order, with duplicates. Convert each with int().",
            "example": r'''
                import re

                answer = "Paris is in France [1]. Rome [2][5]."
                print([int(n) for n in re.findall(r"\[(\d+)\]", answer)])
                # [1, 2, 5]
            ''',
        },
        {
            "syntax": "1 <= n <= n_sources",
            "explain": "Chained comparison: True when n is at least 1 and at most n_sources. A citation outside that range is invalid.",
            "example": r'''
                n_sources = 3
                for n in [0, 1, 3, 4]:
                    print(n, 1 <= n <= n_sources)
                # 0 False
                # 1 True
                # 3 True
                # 4 False
            ''',
        },
        {
            "syntax": "if max(scores) < threshold: decline",
            "explain": "Decline when the best score is below the threshold. One good chunk is enough, so compare max(scores), not min.",
            "example": r'''
                scores = [0.31, 0.72]
                print(max(scores) >= 0.5)
                # True
                print(max([0.12, 0.08]) >= 0.5)
                # False
            ''',
        },
        {
            "syntax": "if used + len(chunk) > budget: continue",
            "explain": "Greedy fill: skip a chunk that does not fit and keep going, so a later, shorter chunk can still be kept.",
            "example": r'''
                budget, used, kept = 10, 0, []
                for text in ["aaaa", "bbbbbbbb", "cc"]:
                    if used + len(text) > budget:
                        continue
                    kept.append(text)
                    used += len(text)
                print(kept, used)
                # ['aaaa', 'cc'] 6
            ''',
        },
    ],
}

LESSON = r'''
## The RAG steps

**RAG** (retrieval-augmented generation) is a program that answers a question in three
steps. It **retrieves** the chunks most similar to the question. It **augments** the prompt:
it adds those chunks to the prompt text. The model then **generates** an answer from that
prompt. The answer is based on the text of your documents, which is in the prompt.

Click each stage to see the text the program holds at that point.

```diagram
{"type":"flow","title":"From question to checked answer","steps":[
{"label":"Question","detail":"The user sends a question as a string.","code":"How long do refunds take?"},
{"label":"Retrieve","detail":"The retriever scores every stored chunk against the question and returns the k best ones. Here k is 2.","code":"0.81  Refunds take 5 business days.   (refunds.md)\n0.55  Shipping is free over 50 EUR.   (shipping.md)"},
{"label":"Number the sources","detail":"enumerate(chunks, start=1) gives each chunk a number. Each line holds the number, the source name and the text.","code":"[1] (refunds.md) Refunds take 5 business days.\n[2] (shipping.md) Shipping is free over 50 EUR."},
{"label":"Build the prompt","detail":"The prompt has three parts separated by empty lines: the instructions, the numbered sources and the question.","code":"Answer using only the numbered sources. Cite them like [1].\nIf the sources do not contain the answer, say you do not know.\n\nSources:\n[1] (refunds.md) Refunds take 5 business days.\n[2] (shipping.md) Shipping is free over 50 EUR.\n\nQuestion: How long do refunds take?"},
{"label":"Generate","detail":"The program calls the model once with the prompt. The reply contains citations in square brackets.","code":"Refunds take 5 business days [1]."},
{"label":"Check citations","detail":"re.findall extracts the numbers. Each one must be between 1 and the number of sources. Valid numbers are mapped back to source names.","code":"cited: [1]\ninvalid: []\nSources: refunds.md"}
]}
```

## The grounded prompt

A **source** is a retrieved chunk with a number in front of it. A **citation** is that
number in square brackets inside the answer, such as `[1]`. A **grounded prompt** tells
the model to answer only from the numbered sources and to cite them.

```python
chunks = [
    {"text": "Refunds take 5 business days.", "source": "refunds.md"},
    {"text": "Shipping is free over 50 EUR.", "source": "shipping.md"},
]
lines = [f"[{n}] ({c['source']}) {c['text']}" for n, c in enumerate(chunks, start=1)]
sources = "\n".join(lines)
question = "How long do refunds take?"
prompt = (
    "Answer using only the numbered sources. Cite them like [1].\n"
    "If the sources do not contain the answer, say you do not know.\n\n"
    f"Sources:\n{sources}\n\n"
    f"Question: {question}"
)
print(prompt)
# Answer using only the numbered sources. Cite them like [1].
# If the sources do not contain the answer, say you do not know.
#
# Sources:
# [1] (refunds.md) Refunds take 5 business days.
# [2] (shipping.md) Shipping is free over 50 EUR.
#
# Question: How long do refunds take?
```

`enumerate(chunks, start=1)` numbers the chunks from 1, so citation `[n]` refers to
source `n`. The empty lines and the `Sources:` and `Question:` labels separate the
instructions from the document text.

## Context budget

The **context budget** is the maximum amount of source text you allow in one prompt.
Go through the chunks in ranked order and keep each one that still fits. `continue`
skips a chunk that is too long, so a later, shorter chunk can still be kept.

```python
ranked = ["a" * 30, "b" * 80, "c" * 15]
budget = 50
kept, used = [], 0
for chunk in ranked:
    if used + len(chunk) > budget:
        continue
    kept.append(chunk)
    used += len(chunk)
print([len(chunk) for chunk in kept], used)
# [30, 15] 45
```

## Declining to answer

A **threshold** is the minimum similarity score you accept. If the best score is below
it, retrieval found nothing relevant. Return a fixed message and do not call the model.
That costs nothing, and the model cannot produce an invented answer.

```python
DECLINE = "I don't know based on the available documents."
results = [("Our CEO likes cats.", 0.12), ("We are hiring.", 0.08)]
best = max(score for text, score in results)
print(best)
# 0.12
if best < 0.5:
    print(DECLINE)
# I don't know based on the available documents.
```

## Checking the citations

`re.findall` with one group returns the digits of every citation, in order. A citation
is valid when `1 <= n <= n_sources`.

```python
import re

answer = "Yes [1]. Also [4] and [2][4]."
n_sources = 3
nums = [int(n) for n in re.findall(r"\[(\d+)\]", answer)]
print(nums)
# [1, 4, 2, 4]
print(sorted({n for n in nums if not 1 <= n <= n_sources}))
# [4]
```

A **hallucinated citation** is a citation to a source that was not in the prompt, such
as `[4]` with 3 sources. You can reject the answer, or call the model again with
feedback such as "Cite only sources [1] to [3]." A sentence with no citation at all is a
claim that no source supports, so flag it. To display the sources, map each valid
number back to its source name.

## Testing with fake models

To **inject** a function means to pass it in as an argument instead of calling a fixed
one. Pass `embed` and `llm` in as arguments. A test passes a fake `llm` that returns a
fixed reply and appends the prompt it received to a list. The test then checks both
the prompt and the result, with no network and no API key.

```python
calls = []

def fake_llm(prompt):
    calls.append(prompt)
    return "Refunds take 5 business days [1]."

def answer_question(question, llm):
    return llm(f"Sources:\n[1] Refunds take 5 business days.\n\nQuestion: {question}")

print(answer_question("How long do refunds take?", fake_llm))
# Refunds take 5 business days [1].
print(calls[0].endswith("Question: How long do refunds take?"))
# True
```

## Common mistakes

- Citation numbers start at 1 and list indexes start at 0. Source `n` is `sources[n - 1]`.
- A source cited twice must be listed once. Keep the order in which sources are first cited.
- Decline when the **best** score is below the threshold. Do not test the worst score.
- A retry loop needs a limit such as `max_attempts`. Without one, a model that keeps
  returning bad citations makes the loop run forever.
'''

EXERCISES = [
    # ---------------------------------------------------------------- difficulty 0
    {
        "id": "rag-answers-s1",
        "title": "What gets printed?",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## Give each supplied passage a citation number

            Your answer should point readers to the passages it used. Before asking for an answer, give each supplied passage a number that the model can mention. Keep that numbering attached to the exact ordered set of passages in this request.

            An LLM on its own generates an answer from what it learned before. When what it
            learned does not contain the answer, the model can still produce text that is
            wrong. **RAG** (retrieval-augmented generation) is a program that retrieves chunks
            of your documents and puts them in the prompt. The prompt tells the model to answer
            from those chunks.

            To let the model state which chunk it used, you number the chunks.
            `enumerate(chunks, start=1)` pairs each item with a counter that starts at 1.

            ```python
            chunks = ["Paris is in France.", "Rome is in Italy."]
            for n, text in enumerate(chunks, start=1):
                print(n, text)
            # 1 Paris is in France.
            # 2 Rome is in Italy.
            ```

            ```quiz
            What does citation number one refer to?
            - [x] The first passage supplied for this request :: Citation numbering is local to the ordered source list.
            - [ ] The second list item :: Python indexes begin at zero, but these citation numbers begin at one.
            ```

            A numbered chunk is called a **source**. A **citation** is a source number in
            square brackets inside the answer, such as `[2]`. Your app reads the citations
            to show the user which document each statement came from.

            Without `start=1`, `enumerate` starts at 0 and the first source gets number 0.

            ```predict
            passages = ["Open weekdays.", "Closed Sundays."]
            print(list(enumerate(passages, start=1)))
            ---
            The counter starts at one while preserving the order of the supplied passages.
            ```

            **Watch out:** A citation marker identifies a source but does not prove the source supports the surrounding claim. That requires checking the content of both.

            **In short:** Number the supplied passages consistently so citation numbers can point back to them.
        ''',
        "prompt": r'''
            Read the program, then enter exactly what its print calls display, one output line per line.
        ''',
        "code": r'''
            chunks = ["Refunds take 5 days.", "Shipping is free."]
            for n, text in enumerate(chunks, start=1):
                print(f"[{n}] {text}")
            print(len(chunks))
        ''',
        "solution": r'''
            [1] Refunds take 5 days.
            [2] Shipping is free.
            2
        ''',
        "explanation": r'''
            Read the output from top to bottom. `enumerate(chunks, start=1)` yields `(1, "Refunds take 5 days.")` then
            `(2, "Shipping is free.")`. The f-string puts the number in square brackets before
            the text. Finally `len(chunks)` is `2`.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Track the starting value of the enumeration counter.",
            "Each loop pass prints one source line before the final length print.",
            "Pair numbers with chunks in order, reproduce the bracketed format, then evaluate the final count.",
        ],
    },
    {
        "id": "rag-answers-s2",
        "title": "Number the sources",
        "difficulty": 0,
        "lesson": r'''
            ## Build the numbered source text

            The prompt needs one readable section containing all selected passages. Make a line for each passage and join those lines with newlines. Keeping separators between lines avoids an extra trailing newline and makes exact formatting predictable.

            The prompt needs all the sources as one string, with one source per line.
            `"\n".join(lines)` returns one string made of the items of `lines` with a newline
            between them. It adds no newline after the last item.

            ```python
            lines = ["[1] alpha", "[2] beta"]
            block = "\n".join(lines)
            print(block)
            # [1] alpha
            # [2] beta
            print(repr(block))
            # '[1] alpha\n[2] beta'
            ```

            ```quiz
            What does joining an empty list of lines produce?
            - [x] An empty string :: There are no items and no separators to insert.
            - [ ] One newline :: Join places separators between items, not around them.
            ```

            `join` also accepts a generator expression, so you do not need to build a list first.
            Joining zero items returns the empty string.

            ```python
            words = ["x", "y", "z"]
            print(", ".join(f"<{w}>" for w in words))
            # <x>, <y>, <z>
            print(repr("\n".join([])))
            # ''
            ```

            Citation numbers start at 1. If you number the sources from 0, the model's `[1]`
            refers to your second source and every citation is off by one.

            ```fill
            lines = ["first", "second"]
            print(___.join(lines))
            ---
            - [x] "\n" :: A newline places the two lines below each other.
            - [ ] " " :: A space keeps both items on the same line.
            ```

            **Watch out:** Do not confuse the display number with the original list index. Using zero-based numbering would shift the link between citations and source text.

            **In short:** Build one numbered line per passage and join those lines without extra separators.
        ''',
        "prompt": r'''
            Format retrieved chunks as a numbered list of sources for a prompt.

            **Your job:** write fill in the blank (`___`) in `format_sources(chunks)`

            **What goes in**
            - `chunks`: a list of strings, e.g. `["Refunds take 5 days.", "Shipping is free."]`

            **What comes out**
            - Return one string with a line `"[n] text"` per chunk, numbered from **1**,
              lines separated by `"\n"` (no newline at the end)

            **Rules**
            - Change only the `___`.
            - An empty list returns `""`.

            **Examples**
            ```python
            format_sources(["Refunds take 5 days.", "Shipping is free."])
            # returns "[1] Refunds take 5 days.\n[2] Shipping is free."
            format_sources(["Only one."])     # returns "[1] Only one."
            format_sources([])                # returns ""
            ```
        ''',
        "starter": r'''
            def format_sources(chunks):
                return "\n".join(f"[{n}] {text}" for n, text in enumerate(chunks, start=___))
        ''',
        "tests": r'''
            from solution import format_sources

            def test_two_chunks_numbered_from_one():
                got = format_sources(["Refunds take 5 days.", "Shipping is free."])
                assert got == "[1] Refunds take 5 days.\n[2] Shipping is free.", f"got {got!r}"

            def test_single_chunk():
                assert format_sources(["Only one."]) == "[1] Only one."

            def test_empty_list_gives_empty_string():
                assert format_sources([]) == ""
        ''',
        "solution": r'''
            def format_sources(chunks):
                return "\n".join(f"[{n}] {text}" for n, text in enumerate(chunks, start=1))
        ''',
        "hints": [
            "The gap controls the first displayed source number.",
            "The task uses human-facing one-based citation numbers.",
            "Set the counter to the requested starting convention and leave the line formatting and joining intact.",
        ],
    },
    {
        "id": "rag-answers-s3",
        "title": "The grounded prompt",
        "difficulty": 0,
        "lesson": r'''
            ## Separate instructions, sources, and the question

            You now have source text and a question, but their roles need to be clear inside the prompt. Put the answer instructions, the supplied evidence, and the question in recognizable sections. This makes the intended task readable for people as well as the model.

            A **grounded prompt** is a prompt that tells the model to answer only from the
            sources it contains. It has three parts in a fixed order:

            1. The **instructions**: answer only from the sources and cite them.
            2. The **sources**: the numbered chunks.
            3. The **question**.

            You separate the parts with empty lines and labels such as `Sources:`. The model
            reads the prompt as one string, so the labels are what mark where your
            instructions end and the document text begins.

            ```python
            sources = "[1] Paris is in France."
            question = "Where is Paris?"
            prompt = f"Use the sources.\n\nSources:\n{sources}\n\nQuestion: {question}"
            print(prompt)
            # Use the sources.
            #
            # Sources:
            # [1] Paris is in France.
            #
            # Question: Where is Paris?
            ```

            ```quiz
            Do source labels enforce factual correctness?
            - [x] No :: They communicate the intended structure; the response still needs checking.
            - [ ] Yes :: Formatting is not a guarantee that the model uses sources faithfully.
            ```

            `\n\n` produces an empty line. The first newline ends the current line. The second
            newline ends a line that has no characters in it.

            The string above does not end with `\n`. A newline after `{question}` would
            change the string, and a test that compares exact strings would fail.

            ```predict
            parts = ["Instructions", "Sources", "Question"]
            print("\n\n".join(parts))
            ---
            Each pair of sections is separated by an empty line, with no final separator.
            ```

            **Watch out:** The task compares exact prompt text. A missing blank line or extra final newline changes that text even when the screen looks almost the same.

            **In short:** Use a consistent layout to distinguish the task from its sources and question.
        ''',
        "prompt": r'''
            Build the grounded prompt that will be sent to the model.

            **Your job:** write `grounded_prompt(question, sources_text)`

            **What goes in**
            - `question`: the user's question (`str`), e.g. `"How long do refunds take?"`
            - `sources_text`: the already-numbered sources (`str`), e.g. `"[1] Refunds take 5 days."`

            **What comes out**
            - Return exactly this string (with the values filled in):

            ```text
            Answer the question using only the sources below. Cite sources like [1].

            Sources:
            <sources_text>

            Question: <question>
            ```

            **Rules**
            - Lines are separated by `"\n"`; there is one empty line between the three parts.
            - No newline at the very end.

            **Examples**
            ```python
            grounded_prompt("How long do refunds take?", "[1] Refunds take 5 days.")
            # returns "Answer the question using only the sources below. Cite sources like [1].\n\nSources:\n[1] Refunds take 5 days.\n\nQuestion: How long do refunds take?"
            ```
        ''',
        "starter": r'''
            def grounded_prompt(question, sources_text):
                ...
        ''',
        "tests": r'''
            from solution import grounded_prompt

            HEAD = "Answer the question using only the sources below. Cite sources like [1]."

            def test_exact_layout():
                got = grounded_prompt("How long do refunds take?", "[1] Refunds take 5 days.")
                want = HEAD + "\n\nSources:\n[1] Refunds take 5 days.\n\nQuestion: How long do refunds take?"
                assert got == want, f"got {got!r}"

            def test_multi_line_sources_are_inserted_as_is():
                got = grounded_prompt("Q?", "[1] a\n[2] b")
                want = HEAD + "\n\nSources:\n[1] a\n[2] b\n\nQuestion: Q?"
                assert got == want, f"got {got!r}"

            def test_no_trailing_newline():
                got = grounded_prompt("Q?", "[1] a")
                assert not got.endswith("\n"), f"got {got!r}"
        ''',
        "solution": r'''
            def grounded_prompt(question, sources_text):
                return (
                    "Answer the question using only the sources below. Cite sources like [1].\n\n"
                    f"Sources:\n{sources_text}\n\n"
                    f"Question: {question}"
                )
        ''',
        "hints": [
            "Treat the prompt as fixed sections separated by exact newline sequences.",
            "Instructions, sources, and the question each have a specified position.",
            "Build the required instruction line, source section, and question section with the exact spacing and no additional output.",
        ],
    },
    {
        "id": "rag-answers-s4",
        "title": "Fix the confidence check",
        "difficulty": 0,
        "lesson": r'''
            ## Decide whether any result passes the minimum score

            Your search returned several passages, and most are weak matches. A single acceptable passage may still be useful. Test whether the best score clears the chosen threshold instead of requiring every retrieved passage to be strong.

            Here an **unsupported claim** is a statement not established by the supplied sources. Model-generated false or unsupported claims are often described as hallucinations.
            When retrieval finds nothing relevant, the prompt contains only unrelated chunks,
            and the model is more likely to hallucinate. In that case a RAG app should
            reply that it does not know.

            The retriever returns a similarity score for each chunk. A **threshold** is the
            minimum score you accept, for example `0.5`. If the best score is below the
            threshold, you do not call the model. You return a fixed message such as
            "I don't know based on the available documents."

            ```python
            scores = [0.31, 0.72, 0.18]
            print(max(scores))
            # 0.72
            print(max(scores) >= 0.5)
            # True
            print(min(scores) >= 0.5)
            # False
            ```

            ```quiz
            Does a low score on one passage mean all passages are unusable?
            - [x] No :: This step asks whether at least one score reaches the minimum.
            - [ ] Yes :: That would test the weakest result instead of the strongest.
            ```

            This exercise treats one above-threshold chunk as sufficient to proceed, so you compare the best score,
            `max(scores)`, with the threshold. Comparing `min(scores)` rejects every result
            list that contains one weak chunk.

            The right threshold depends on your embedding model. You choose it by looking at
            the scores of real questions.

            ```predict
            scores = [0.1, 0.8, 0.2]
            print(max(scores) >= 0.7)
            print(min(scores) >= 0.7)
            ---
            The best-match condition passes even though some results are below the minimum.
            ```

            **Watch out:** Similarity is not calibrated answer confidence. The threshold is an application rule to evaluate on representative questions, not a proof that an answer will be supported.

            **In short:** Check for an acceptable best result and handle no results explicitly.
        ''',
        "prompt": r'''
            `has_good_match` decides whether retrieval found anything worth answering from.
            It refuses to answer far too often. Find and fix the bug.

            **Your job:** fix `has_good_match(scores, threshold)`

            **What goes in**
            - `scores`: a list of similarity scores (`float`), in any order
            - `threshold`: the minimum acceptable score (`float`), e.g. `0.5`

            **What comes out**
            - Return `True` if the **best** score is greater than or equal to `threshold`, else `False`

            **Rules**
            - An empty list returns `False`.
            - A score exactly equal to the threshold counts as good.

            **Examples**
            ```python
            has_good_match([0.31, 0.72, 0.18], 0.5)   # returns True
            has_good_match([0.31, 0.42], 0.5)         # returns False
            has_good_match([0.5], 0.5)                # returns True
            has_good_match([], 0.5)                   # returns False
            ```
        ''',
        "starter": r'''
            def has_good_match(scores, threshold):
                if not scores:
                    return False
                return min(scores) >= threshold
        ''',
        "tests": r'''
            from solution import has_good_match

            def test_one_good_score_is_enough():
                assert has_good_match([0.31, 0.72, 0.18], 0.5) is True

            def test_all_scores_below_threshold():
                assert has_good_match([0.31, 0.42], 0.5) is False

            def test_score_equal_to_threshold_counts():
                assert has_good_match([0.5], 0.5) is True

            def test_empty_scores_is_false():
                assert has_good_match([], 0.5) is False
        ''',
        "solution": r'''
            def has_good_match(scores, threshold):
                if not scores:
                    return False
                return max(scores) >= threshold
        ''',
        "hints": [
            "The question is whether any source reaches the minimum.",
            "The strongest result determines that condition, not the weakest.",
            "Keep the empty-input handling and compare the appropriate extreme score with the inclusive threshold.",
        ],
    },
    {
        "id": "rag-answers-s5",
        "title": "Find the citations",
        "difficulty": 0,
        "lesson": r'''
            ## Read citation numbers from an answer

            The answer contains bracketed source numbers among ordinary words. Your interface needs those numbers as data before it can link or validate them. Extract only the exact marker format this task defines, then turn the captured digits into integers.

            The model's answer is a string with citations in it, such as
            `"Paris is in France [1]. Rome is in Italy [2]."`. To check or display the
            citations, your code first extracts the numbers.

            When a pattern has one group `( )`, `re.findall` returns only the text matched
            inside the group. Square brackets have a special meaning in a regex, so you write
            a literal `[` as `\[` and a literal `]` as `\]`. `\d+` matches one or more digits.

            ```python
            import re

            answer = "Paris is in France [1]. Rome is in Italy [2][1]."
            print(re.findall(r"\[(\d+)\]", answer))
            # ['1', '2', '1']
            print([int(n) for n in re.findall(r"\[(\d+)\]", answer)])
            # [1, 2, 1]
            ```

            ```quiz
            Does extraction itself check that a cited source exists?
            - [x] No :: It recognizes the marker and reads its number; range checking is a later step.
            - [ ] Yes :: Finding digits does not reveal how many sources were supplied.
            ```

            `findall` returns strings, in the order they appear, with duplicates. Convert
            each one with `int()` before you compare it with a number.

            The pattern accepts only digits directly between the brackets. `[a]` and `[ 1 ]`
            do not match.

            ```python
            import re

            print(re.findall(r"\[(\d+)\]", "See [a] and [ 1 ] and [12]."))
            # ['12']
            ```

            ```predict
            matches = ["2", "2", "10"]
            print([int(value) for value in matches])
            ---
            Conversion changes strings to integers without sorting or removing duplicates.
            ```

            **Watch out:** The pattern deliberately ignores markers with spaces or letters inside the brackets. Preserve duplicate matches and their order when the extraction contract asks for all occurrences.

            **In short:** Extract the specified marker syntax first, then validate or display its numbers separately.
        ''',
        "prompt": r'''
            Extract the citation numbers from a model's answer.

            **Your job:** write `find_citations(answer)`

            **What goes in**
            - `answer`: the model's reply (`str`), e.g. `"Refunds take 5 days [1]. Free shipping [2][1]."`

            **What comes out**
            - Return a list of `int`s: every `[n]` citation (digits inside square
              brackets), in the order they appear

            **Rules**
            - Keep duplicates (`[1]` twice gives `1` twice).
            - Brackets with anything other than digits inside (like `[a]` or `[ 1 ]`) are not citations.
            - No citations returns `[]`.
            - `re` is already imported in the starter.

            **Examples**
            ```python
            find_citations("Refunds take 5 days [1]. Free shipping [2][1].")   # returns [1, 2, 1]
            find_citations("See [12] and [a].")                                # returns [12]
            find_citations("No sources here.")                                 # returns []
            ```
        ''',
        "starter": r'''
            import re


            def find_citations(answer):
                ...
        ''',
        "tests": r'''
            from solution import find_citations

            def test_finds_numbers_in_order_with_duplicates():
                got = find_citations("Refunds take 5 days [1]. Free shipping [2][1].")
                assert got == [1, 2, 1], f"got {got!r}"

            def test_returns_ints_and_multi_digit_numbers():
                got = find_citations("See [12] and [a].")
                assert got == [12], f"got {got!r}"

            def test_spaces_inside_brackets_do_not_count():
                assert find_citations("Odd [ 1 ] format") == []

            def test_no_citations_gives_empty_list():
                assert find_citations("No sources here.") == []
        ''',
        "solution": r'''
            import re


            def find_citations(answer):
                return [int(n) for n in re.findall(r"\[(\d+)\]", answer)]
        ''',
        "hints": [
            "A capture group can return only the digits inside each marker.",
            "Convert each captured string into a number while preserving its occurrence order.",
            "Find the exact bracketed-digit pattern, retain all matches including repeats, and return their integer values.",
        ],
    },
    {
        "id": "rag-answers-s6",
        "title": "What fits in the budget?",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## Stop when the next passage does not fit

            You have a ranked list of passages and a fixed allowance for source text. Walk through the list while tracking how much space you have used. In this introductory policy, the first passage that would exceed the allowance ends selection, even if later passages are shorter.

            A prompt has a size limit. The model's **context window** is the maximum number
            of tokens it accepts, and you pay for every token you send. You cannot add every
            retrieved chunk. The **context budget** is the maximum amount of source text you
            allow in one prompt. You add the best-ranked chunks first and stop when the next
            one would exceed the budget.

            This chapter counts characters with `len`. Actual context accounting uses the relevant tokenizer and also includes instructions, labels, and the question.

            ```python
            budget = 12
            used = 0
            for word in ["pack", "this", "stuff"]:
                used += len(word)
                print(word, used, used <= budget)
            # pack 4 True
            # this 8 True
            # stuff 13 False
            ```

            ```quiz
            What happens when a passage exactly fills the remaining allowance?
            - [x] Keep it :: Equality fits; only a total above the budget is too large.
            - [ ] Reject it :: That would leave unused space despite satisfying the stated limit.
            ```

            `break` ends a loop immediately. Python skips the rest of the loop body and all
            remaining items, then runs the first line after the loop.

            ```python
            for n in [3, 5, 9, 2]:
                if n > 8:
                    break
                print(n)
            # 3
            # 5
            print("done")
            # done
            ```

            `2` is never printed, because the loop ended at `9`.

            ```predict
            used, budget = 4, 9
            print(used + 5 > budget)
            print(used + 6 > budget)
            ---
            Exactly reaching the budget is allowed; passing it is not.
            ```

            **Watch out:** This step counts source characters only. A real prompt also includes labels, instructions, the question, and tokenization overhead, so this is not a complete model-context calculation.

            **In short:** Include ranked passages while they fit, and stop at the first over-budget candidate under this policy.
        ''',
        "prompt": r'''
            Read the program, then enter exactly what its print calls display, one output line per line.
        ''',
        "code": r'''
            chunks = ["aaaa", "bbbbbb", "cc", "dddddd"]
            budget = 10
            used = 0
            kept = []
            for c in chunks:
                if used + len(c) > budget:
                    break
                kept.append(c)
                used += len(c)
            print(kept)
            print(used)
        ''',
        "solution": r'''
            ['aaaa', 'bbbbbb']
            10
        ''',
        "explanation": r'''
            Read the output from top to bottom. `"aaaa"` fits (0 + 4 = 4). `"bbbbbb"` fits exactly (4 + 6 = 10, and `10 > 10` is
            False). `"cc"` would make 12, which is over the budget, so the loop `break`s:
            `"cc"` and everything after it are left out. `used` stays at `10`.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Track the used amount after each accepted passage.",
            "An exact fit is permitted; the first excessive candidate ends this loop.",
            "Evaluate each proposed total in order, stop where the condition breaks, and print the kept list and final used amount.",
        ],
    },
    # ---------------------------------------------------------------- difficulty 1
    {
        "id": "rag-answers-1",
        "title": "Fill the context budget",
        "difficulty": 1,
        "lesson": r'''
            ## Skip an oversized passage and consider the next one

            A high-ranked passage is too long for the remaining space, but a later short passage may still help. This selection policy skips the oversized passage and continues scanning. Compare it with the earlier stop-at-first-failure policy so the difference is deliberate.

            In the last exercise the loop ended at the first chunk that did not fit. A
            lower-ranked chunk that is short can still fit in the remaining budget, and it
            can still contain useful facts.

            `continue` skips the rest of the loop body for the current item. The loop then
            moves on to the next item. `break` would end the whole loop instead.

            ```python
            sizes = [5, 9, 2]
            room = 8
            for size in sizes:
                if size > room:
                    print("skip", size)
                    continue
                room -= size
                print("keep", size, "room left", room)
            # keep 5 room left 3
            # skip 9
            # keep 2 room left 1
            ```

            ```quiz
            Which loop control allows later passages to be considered?
            - [x] continue :: It skips only the current iteration.
            - [ ] break :: It ends the loop and prevents later candidates from being examined.
            ```

            Step through the loop and watch `room` when `size` is `9`.

            ```diagram
            {"type": "trace", "title": "continue skips the item that does not fit", "code": ["sizes = [5, 9, 2]", "room = 8", "for size in sizes:", "    if size > room:", "        print(\"skip\", size)", "        continue", "    room -= size", "    print(\"keep\", size, \"room left\", room)"], "steps": [
              {"line": 1, "vars": {}, "out": ""},
              {"line": 2, "vars": {"sizes": "[5, 9, 2]"}, "out": ""},
              {"line": 3, "vars": {"sizes": "[5, 9, 2]", "room": "8"}, "out": ""},
              {"line": 4, "vars": {"sizes": "[5, 9, 2]", "room": "8", "size": "5"}, "out": ""},
              {"line": 7, "vars": {"sizes": "[5, 9, 2]", "room": "8", "size": "5"}, "out": ""},
              {"line": 8, "vars": {"sizes": "[5, 9, 2]", "room": "3", "size": "5"}, "out": ""},
              {"line": 3, "vars": {"sizes": "[5, 9, 2]", "room": "3", "size": "5"}, "out": "keep 5 room left 3\n"},
              {"line": 4, "vars": {"sizes": "[5, 9, 2]", "room": "3", "size": "9"}, "out": "keep 5 room left 3\n"},
              {"line": 5, "vars": {"sizes": "[5, 9, 2]", "room": "3", "size": "9"}, "out": "keep 5 room left 3\n"},
              {"line": 6, "vars": {"sizes": "[5, 9, 2]", "room": "3", "size": "9"}, "out": "keep 5 room left 3\nskip 9\n"},
              {"line": 3, "vars": {"sizes": "[5, 9, 2]", "room": "3", "size": "9"}, "out": "keep 5 room left 3\nskip 9\n"},
              {"line": 4, "vars": {"sizes": "[5, 9, 2]", "room": "3", "size": "2"}, "out": "keep 5 room left 3\nskip 9\n"},
              {"line": 7, "vars": {"sizes": "[5, 9, 2]", "room": "3", "size": "2"}, "out": "keep 5 room left 3\nskip 9\n"},
              {"line": 8, "vars": {"sizes": "[5, 9, 2]", "room": "1", "size": "2"}, "out": "keep 5 room left 3\nskip 9\n"},
              {"line": 3, "vars": {"sizes": "[5, 9, 2]", "room": "1", "size": "2"}, "out": "keep 5 room left 3\nskip 9\nkeep 2 room left 1\n"},
              {"line": null, "vars": {"sizes": "[5, 9, 2]", "room": "1", "size": "2"}, "out": "keep 5 room left 3\nskip 9\nkeep 2 room left 1\n"}
            ]}
            ```

            This method is called a **greedy** fill: you go through the items once in ranked
            order, take each one that still fits, and never undo a choice.

            Keep the chunks in their ranked order. Do not sort them by size.

            ```predict
            remaining = 5
            for size in [8, 3]:
                if size > remaining:
                    continue
                remaining -= size
            print(remaining)
            ---
            The oversized item changes nothing; the later three-character item consumes space.
            ```

            **Watch out:** Only selected text consumes this budget. Skipping a candidate must leave the amount used unchanged, or later passages will be rejected for space never actually spent.

            **In short:** Skip candidates that do not fit while preserving the rank order of those you keep.
        ''',
        "prompt": r'''
            Choose which ranked chunks go into the prompt without going over a character budget.

            **Your job:** write `fit_context(chunks, max_chars)`

            **What goes in**
            - `chunks`: a list of strings, best-ranked first
            - `max_chars`: the budget (`int`): the total `len` of the kept chunks must not exceed it

            **What comes out**
            - Return a new list of the kept chunks, in their original order

            **Rules**
            - Go through the chunks in order. Keep a chunk if it still fits in the remaining budget.
            - A chunk that doesn't fit is **skipped**, and later (smaller) chunks may still be kept.
            - Using the budget exactly (total == `max_chars`) is allowed.
            - Don't change `chunks`.

            **Examples**
            ```python
            fit_context(["aaaa", "bbbbbb", "cc", "d"], 10)   # returns ["aaaa", "bbbbbb"]
            fit_context(["aaaa", "bbbbbbbb", "cc"], 7)       # returns ["aaaa", "cc"]
            fit_context(["toolong"], 3)                      # returns []
            fit_context([], 100)                             # returns []
            ```
        ''',
        "starter": r'''
            def fit_context(chunks, max_chars):
                ...
        ''',
        "tests": r'''
            from solution import fit_context

            def test_keeps_chunks_that_fit_exactly():
                got = fit_context(["aaaa", "bbbbbb", "cc", "d"], 10)
                assert got == ["aaaa", "bbbbbb"], f"got {got!r}"

            def test_skips_too_big_chunk_and_keeps_going():
                got = fit_context(["aaaa", "bbbbbbbb", "cc"], 7)
                assert got == ["aaaa", "cc"], f"got {got!r}"

            def test_keeps_ranked_order_not_size_order():
                got = fit_context(["ccc", "a", "bb"], 6)
                assert got == ["ccc", "a", "bb"], f"got {got!r}"

            def test_nothing_fits_or_nothing_given():
                assert fit_context(["toolong"], 3) == []
                assert fit_context([], 100) == []

            def test_input_not_changed():
                chunks = ["aaaa", "bbbbbbbb", "cc"]
                fit_context(chunks, 7)
                assert chunks == ["aaaa", "bbbbbbbb", "cc"], f"input changed to {chunks!r}"
        ''',
        "solution": r'''
            def fit_context(chunks, max_chars):
                kept = []
                used = 0
                for chunk in chunks:
                    if used + len(chunk) > max_chars:
                        continue
                    kept.append(chunk)
                    used += len(chunk)
                return kept
        ''',
        "hints": [
            "Unlike the earlier policy, later short passages can still be considered.",
            "A skipped candidate does not consume space.",
            "Track used space, keep each fitting passage in order, skip oversized ones, and return the collected passages.",
        ],
    },
    {
        "id": "rag-answers-2",
        "title": "Ask a fake LLM",
        "difficulty": 1,
        "lesson": r'''
            ## Test the answer request with a fake model function

            You want to know whether your app passes the right instructions, source numbering, and question to the model. A prepared local function can record its input and return fixed text. That lets you inspect the request without a network call or an unpredictable answer.

            Your RAG code does not call an API directly. It takes the model as a parameter
            named `llm`, which is a function. Passing a dependency in as an argument is called
            **injecting** it. In production you pass a function that calls the real API. In
            tests you pass a fake function that returns a fixed reply and appends its
            argument to a list.

            The LLM chapter defined messages: a list of dicts, each with a `"role"` and a
            `"content"`. The system message holds the instructions. The user message holds
            the sources and the question.

            ```python
            seen = []
            def fake_llm(messages):
                seen.append(messages)
                return "Paris [1]."
            reply = fake_llm([{"role": "user", "content": "Where is the Eiffel Tower?"}])
            print(reply)
            # Paris [1].
            print(len(seen))
            # 1
            print(seen[0][0]["role"])
            # user
            ```

            ```quiz
            What can this fake establish?
            - [x] That the app builds and sends the required messages :: It records ordinary Python values for the test to inspect.
            - [ ] That a real model answers faithfully :: The prepared return value does not measure real model behavior.
            ```

            `seen[0]` is the message list from the first call, and `seen[0][0]` is its first
            message. Because the fake stores its input, a test can check that your code built
            the right messages and called the model exactly once.

            ```order
            seen = []
            def fake(value): seen.append(value); return "recorded"
            print(fake("question"))
            print(len(seen))
            ---
            The callable records the supplied input and returns a predetermined reply.
            ```

            **Watch out:** Call the supplied function with the interface the task specifies. A fake is not an SDK object, and adding an unrequested API call would bypass the test dependency.

            **In short:** Inject a callable to make request construction and call count observable without contacting a model.
        ''',
        "prompt": r'''
            Send the question and its sources to an injected LLM function and return the reply.

            **Your job:** write `ask(question, chunks, llm)`

            **What goes in**
            - `question`: the user's question (`str`)
            - `chunks`: a list of retrieved texts (`str`), best first
            - `llm`: a function that takes a list of message dicts and returns the reply text (`str`)

            **What comes out**
            - Return whatever `llm` returns

            **Rules**
            - Call `llm` exactly once with a list of **two** messages:
              1. `{"role": "system", "content": SYSTEM}` (the `SYSTEM` constant from the starter)
              2. `{"role": "user", "content": ...}` where content is `"Sources:\n"`, then one
                 `"[n] text"` line per chunk numbered from 1 (joined with `"\n"`), then
                 `"\n\nQuestion: "` and the question.
            - Keep `SYSTEM` exactly as given.

            **Examples**
            ```python
            ask("How long do refunds take?", ["Refunds take 5 days.", "Shipping is free."], fake_llm)
            # calls fake_llm with:
            # [{"content": SYSTEM, "role": "system"},
            #  {"role": "user", "content": "Sources:\n[1] Refunds take 5 days.\n[2] Shipping is free.\n\nQuestion: How long do refunds take?"}]
            # and returns whatever fake_llm returned
            ```
        ''',
        "starter": r'''
            SYSTEM = "Answer only from the numbered sources and cite them like [1]."


            def ask(question, chunks, llm):
                ...
        ''',
        "tests": r'''
            from solution import ask, SYSTEM

            def make_llm(reply="Refunds take 5 days [1]."):
                calls = []
                def fake_llm(messages):
                    calls.append(messages)
                    return reply
                return fake_llm, calls

            def test_returns_the_llm_reply():
                llm, calls = make_llm("It takes 5 days [1].")
                got = ask("How long?", ["Refunds take 5 days."], llm)
                assert got == "It takes 5 days [1].", f"got {got!r}"

            def test_system_prompt_unchanged():
                assert SYSTEM == "Answer only from the numbered sources and cite them like [1]."

            def test_sends_system_and_user_messages():
                llm, calls = make_llm()
                ask("How long do refunds take?", ["Refunds take 5 days.", "Shipping is free."], llm)
                assert len(calls) == 1, f"llm was called {len(calls)} times"
                msgs = calls[0]
                assert msgs[0] == {"role": "system", "content": SYSTEM}, f"got {msgs[0]!r}"
                want = "Sources:\n[1] Refunds take 5 days.\n[2] Shipping is free.\n\nQuestion: How long do refunds take?"
                assert msgs[1] == {"role": "user", "content": want}, f"got {msgs[1]!r}"
                assert len(msgs) == 2, f"got {len(msgs)} messages"

            def test_single_chunk_numbered_one():
                llm, calls = make_llm()
                ask("Q?", ["Only."], llm)
                assert calls[0][1]["content"] == "Sources:\n[1] Only.\n\nQuestion: Q?", f"got {calls[0][1]!r}"
        ''',
        "solution": r'''
            SYSTEM = "Answer only from the numbered sources and cite them like [1]."


            def ask(question, chunks, llm):
                sources = "\n".join(f"[{n}] {text}" for n, text in enumerate(chunks, start=1))
                messages = [
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": f"Sources:\n{sources}\n\nQuestion: {question}"},
                ]
                return llm(messages)
        ''',
        "hints": [
            "Build the source block before placing it with the question into the user message.",
            "The model receives one instruction message and one question-with-sources message.",
            "Number and join passages, build the two required messages, call the supplied function once, and return its text.",
        ],
    },
    {
        "id": "rag-answers-3",
        "title": "Answer or decline",
        "difficulty": 1,
        "lesson": r'''
            ## Decline before calling when no source qualifies

            Your app should avoid asking for an answer when its retrieval step found no acceptable evidence under the chosen score rule. Filter the candidates first. If none remain, return the specified decline response without making a model call.

            The retriever returns each chunk together with its score, as a `(text, score)`
            tuple. Before you build the prompt, you remove every chunk whose score is below
            the threshold. If no chunk is left, you return a fixed message such as "I don't
            know based on the available documents." and you do not call the model. That call would have no accepted source evidence under the chosen threshold policy.

            ```python
            results = [("Rome is in Italy.", 0.81), ("Cats sleep a lot.", 0.12)]
            threshold = 0.5
            accepted = [text for text, score in results if score >= threshold]
            print(accepted)
            # ['Rome is in Italy.']
            print(not accepted)
            # False
            ```

            ```quiz
            When should you assign source numbers?
            - [x] After filtering :: Only passages actually sent should receive citation numbers.
            - [ ] Before filtering and preserve all gaps :: That complicates the local numbering contract used here.
            ```

            `for text, score in results` uses **tuple unpacking**: Python assigns the first
            item of each tuple to `text` and the second to `score`. That is easier to read
            than `pair[0]` and `pair[1]`.

            An empty list is falsy, so `not accepted` is `True` only when no chunk passed the
            filter.

            Number the sources after you filter. A low-scoring chunk left in the prompt is
            unrelated text that the model can cite as a source.

            ```predict
            results = [("weak", 0.1), ("usable", 0.7)]
            kept = [text for text, score in results if score >= 0.5]
            print(list(enumerate(kept, start=1)))
            ---
            The surviving source becomes number one, regardless of its old position.
            ```

            **Watch out:** A passing retrieval score is only a selection rule. The model can still make unsupported claims, so accepting sources does not establish answer correctness.

            **In short:** Filter first, decline on an empty selection, and number only the sources you actually send.
        ''',
        "prompt": r'''
            Only call the model when retrieval found good sources; otherwise decline.

            **Your job:** write `answer_or_decline(question, results, llm, threshold=0.5)`

            **What goes in**
            - `question`: the user's question (`str`)
            - `results`: a list of `(text, score)` tuples from the retriever, best first
            - `llm`: a function that takes a prompt **string** and returns the reply (`str`)
            - `threshold`: minimum score for a source to be used (`float`, default `0.5`)

            **What comes out**
            - Return the reply text (`str`)

            **Rules**
            - Keep only the results with `score >= threshold`, in their given order.
            - If none are kept, return the `DECLINE` constant from the starter and **don't call `llm`**.
            - Otherwise call `llm` once with the prompt `"Sources:\n"` + the kept texts as
              `"[n] text"` lines numbered from 1 (joined with `"\n"`) + `"\n\nQuestion: "` + question,
              and return its reply.

            **Examples**
            ```python
            results = [("Refunds take 5 days.", 0.81), ("Our CEO likes cats.", 0.12)]
            answer_or_decline("How long do refunds take?", results, fake_llm)
            # calls fake_llm("Sources:\n[1] Refunds take 5 days.\n\nQuestion: How long do refunds take?")
            answer_or_decline("Who won?", [("Our CEO likes cats.", 0.12)], fake_llm)
            # returns DECLINE, fake_llm not called
            answer_or_decline("Q?", [], fake_llm)      # returns DECLINE
            ```
        ''',
        "starter": r'''
            DECLINE = "I don't know based on the available documents."


            def answer_or_decline(question, results, llm, threshold=0.5):
                ...
        ''',
        "tests": r'''
            from solution import answer_or_decline, DECLINE

            def make_llm(reply="Five days [1]."):
                calls = []
                def fake_llm(prompt):
                    calls.append(prompt)
                    return reply
                return fake_llm, calls

            def test_uses_only_good_sources():
                llm, calls = make_llm()
                results = [("Refunds take 5 days.", 0.81), ("Our CEO likes cats.", 0.12)]
                got = answer_or_decline("How long do refunds take?", results, llm)
                assert got == "Five days [1].", f"got {got!r}"
                assert calls == ["Sources:\n[1] Refunds take 5 days.\n\nQuestion: How long do refunds take?"], f"llm got {calls!r}"

            def test_declines_without_calling_llm():
                llm, calls = make_llm()
                got = answer_or_decline("Who won?", [("Our CEO likes cats.", 0.12)], llm)
                assert got == DECLINE, f"got {got!r}"
                assert calls == [], "llm should not be called when nothing is good enough"

            def test_empty_results_decline():
                llm, calls = make_llm()
                assert answer_or_decline("Q?", [], llm) == DECLINE
                assert calls == []

            def test_threshold_is_inclusive_and_configurable():
                llm, calls = make_llm()
                results = [("a", 0.3), ("b", 0.2), ("c", 0.35)]
                answer_or_decline("Q?", results, llm, threshold=0.3)
                assert calls == ["Sources:\n[1] a\n[2] c\n\nQuestion: Q?"], f"llm got {calls!r}"

            def test_decline_message_unchanged():
                assert DECLINE == "I don't know based on the available documents."
        ''',
        "solution": r'''
            DECLINE = "I don't know based on the available documents."


            def answer_or_decline(question, results, llm, threshold=0.5):
                good = [text for text, score in results if score >= threshold]
                if not good:
                    return DECLINE
                sources = "\n".join(f"[{n}] {text}" for n, text in enumerate(good, start=1))
                return llm(f"Sources:\n{sources}\n\nQuestion: {question}")
        ''',
        "hints": [
            "Whether to call the model depends on the filtered set, not the original set.",
            "Only accepted passages belong in the numbered prompt.",
            "Filter using the inclusive threshold, return the fixed decline for an empty result, otherwise build the required prompt and call once.",
        ],
    },
    {
        "id": "rag-answers-4",
        "title": "Catch invented citations",
        "difficulty": 1,
        "lesson": r'''
            ## Find citation numbers outside the supplied range

            The answer points to source five, but the prompt supplied only two sources. That marker cannot point to one of the supplied passages. Check the citation range separately from extracting the digits, and report invalid numbers in the predictable form the caller expects.

            Given 3 sources, a model sometimes cites `[4]` or `[0]`. A **hallucinated
            citation** is a citation to a source that was not in the prompt. If you show one
            to users, it links a statement to a document that does not exist.

            A citation `n` is valid when `1 <= n <= n_sources`. Python accepts chained
            comparisons: `1 <= n <= n_sources` means `1 <= n and n <= n_sources`.

            ```python
            n_sources = 3
            for n in [0, 1, 3, 4]:
                print(n, 1 <= n <= n_sources)
            # 0 False
            # 1 True
            # 3 True
            # 4 False
            ```

            ```quiz
            Does an in-range citation prove its sentence is supported?
            - [x] No :: It proves only that the numbered source exists in the supplied set.
            - [ ] Yes :: A real source can still be irrelevant to the cited claim.
            ```

            To report each invalid number once, put the numbers in a set. A set keeps one copy
            of each value. `sorted()` returns a new list with the values in ascending order.

            ```python
            print(sorted({9, 0, 9, 5}))
            # [0, 5, 9]
            ```

            With two sets, `a - b` gives the values that are in `a` and not in `b`.

            ```python
            cited = {1, 5, 9}
            valid = {1, 2, 3}
            print(sorted(cited - valid))
            # [5, 9]
            ```

            Select `-` to see the cited numbers that are not valid, then `&` to see the valid ones.

            ```diagram
            {"type":"set-ops","title":"Cited numbers and valid source numbers","a":{"name":"cited","items":[1,5,9]},"b":{"name":"valid","items":[1,2,3]}}
            ```

            You decide what to do with invalid citations: remove them, flag the answer, or
            call the model again. A later exercise covers the retry.

            ```predict
            numbers = [0, 2, 5, 5]
            print(sorted(set(n for n in numbers if not 1 <= n <= 3)))
            ---
            The invalid numbers are deduplicated and sorted; the in-range two is omitted.
            ```

            **Watch out:** Zero is outside this one-based citation range. Do not let Python's negative indexing accidentally map it to the last passage.

            **In short:** Range validation checks whether a citation can refer to a supplied source, not whether it supports a claim.
        ''',
        "prompt": r'''
            Find the citation numbers that point at sources that don't exist.

            **Your job:** write `invalid_citations(answer, n_sources)`

            **What goes in**
            - `answer`: the model's reply (`str`), containing citations like `[1]`
            - `n_sources`: how many sources were in the prompt (`int`)

            **What comes out**
            - Return a sorted list of the **distinct** cited numbers (`int`) that are
              not between `1` and `n_sources` (inclusive)

            **Rules**
            - A citation is digits inside square brackets, e.g. `[3]` (same as `find_citations`).
            - Each invalid number appears once, smallest first.
            - With `n_sources == 0`, every citation is invalid.
            - No invalid citations returns `[]`.

            **Examples**
            ```python
            invalid_citations("Yes [1]. Also [4] and [4]. See [0].", 3)   # returns [0, 4]
            invalid_citations("Fine [1][3].", 3)                          # returns []
            invalid_citations("Hmm [1].", 0)                              # returns [1]
            ```
        ''',
        "starter": r'''
            import re


            def invalid_citations(answer, n_sources):
                ...
        ''',
        "tests": r'''
            from solution import invalid_citations

            def test_out_of_range_numbers_sorted_and_unique():
                got = invalid_citations("Yes [1]. Also [4] and [4]. See [0].", 3)
                assert got == [0, 4], f"got {got!r}"

            def test_all_valid_gives_empty_list():
                assert invalid_citations("Fine [1][3].", 3) == []

            def test_no_sources_means_all_invalid():
                got = invalid_citations("Hmm [1].", 0)
                assert got == [1], f"got {got!r}"

            def test_no_citations():
                assert invalid_citations("No citations.", 2) == []

            def test_multi_digit_citation():
                got = invalid_citations("See [10] and [2].", 9)
                assert got == [10], f"got {got!r}"
        ''',
        "solution": r'''
            import re


            def invalid_citations(answer, n_sources):
                cited = {int(n) for n in re.findall(r"\[(\d+)\]", answer)}
                return sorted(n for n in cited if not 1 <= n <= n_sources)
        ''',
        "hints": [
            "Extraction and range checking are separate operations.",
            "Repeated bad numbers should appear only once in the report.",
            "Read the marker numbers, retain those outside the permitted one-based range, remove duplicates, and sort the report.",
        ],
    },
    {
        "id": "rag-answers-5",
        "title": "Show the cited sources",
        "difficulty": 1,
        "lesson": r'''
            ## Link citations back to the selected sources

            A reader clicks a citation and expects the actual source. Translate the one-based citation number into the correct position in the selected source list. Repeated citations should not create repeated entries in the displayed source list when the contract asks for first appearances only.

            The text `[2]` alone tells the user nothing. Your app shows the source itself, for example
            "Source: shipping.md" with a link. After the model replies, you map each citation
            number back to the source it refers to.

            Citation `[1]` is the first source, and list indexes start at 0. Source `n` is at
            `sources[n - 1]`.

            ```python
            sources = [{"title": "France"}, {"title": "Italy"}]
            n = 2
            print(sources[n - 1]["title"])
            # Italy
            ```

            ```quiz
            How should repeated citations affect the output ordering?
            - [x] Keep each valid source at its first cited position :: A set tracks repeats while a list preserves order.
            - [ ] Sort all sources alphabetically :: That loses the order in which citations first appeared.
            ```

            If the model cites `[2]` three times, you list that source once. Keep the order in
            which the sources are first cited, which usually matches the order of the
            statements in the answer. A set records which numbers you have already added. A
            list keeps the order.

            ```python
            seen, order = set(), []
            for n in [2, 1, 2]:
                if n not in seen:
                    seen.add(n)
                    order.append(n)
            print(order)
            # [2, 1]
            ```

            Check the range before you index. With `n = 0`, `sources[n - 1]` is `sources[-1]`.
            That returns the last source and raises no error.

            ```predict
            sources = ["north.md", "south.md"]
            number = 2
            print(sources[number - 1])
            ---
            Citation two refers to the second source, whose Python index is one.
            ```

            **Watch out:** Validate the number before subtracting for the list index. Zero would otherwise become a valid negative index and return the wrong source without raising an error.

            **In short:** Map valid numbers into the same source list and keep the first appearance order.
        ''',
        "research": {
            "note": "Read how Anthropic's API can return citations that point at the exact passages of the documents you provided. Compare it with the [n] markers you parse by hand here.",
            "links": [
                {"title": "Citations - Anthropic docs", "url": "https://docs.anthropic.com/en/docs/build-with-claude/citations"},
            ],
        },
        "prompt": r'''
            Turn the citations in an answer into the list of source records to display.

            **Your job:** write `cited_sources(answer, sources)`

            **What goes in**
            - `answer`: the model's reply (`str`), with citations like `[2]`
            - `sources`: the list of source dicts that were numbered `[1]`, `[2]`, ... in the
              prompt, e.g. `[{"title": "Refunds", "url": "https://x/refunds"}, ...]`

            **What comes out**
            - Return a list of the cited source dicts, each **once**, in the order they
              were **first** cited

            **Rules**
            - Citation `[n]` refers to `sources[n - 1]`.
            - Ignore citations outside `1..len(sources)` (e.g. `[0]`, `[9]`).
            - No valid citations returns `[]`.

            **Examples**
            ```python
            sources = [{"title": "Refunds"}, {"title": "Shipping"}, {"title": "Careers"}]
            cited_sources("Free shipping [2]. Refunds in 5 days [1][2].", sources)
            # returns [{"title": "Shipping"}, {"title": "Refunds"}]
            cited_sources("Made up [7]. Also [0].", sources)      # returns []
            cited_sources("No citations.", sources)               # returns []
            ```
        ''',
        "starter": r'''
            import re


            def cited_sources(answer, sources):
                ...
        ''',
        "tests": r'''
            from solution import cited_sources

            SOURCES = [{"title": "Refunds"}, {"title": "Shipping"}, {"title": "Careers"}]

            def test_first_cited_order_without_duplicates():
                got = cited_sources("Free shipping [2]. Refunds in 5 days [1][2].", SOURCES)
                assert got == [{"title": "Shipping"}, {"title": "Refunds"}], f"got {got!r}"

            def test_one_based_numbering():
                got = cited_sources("Jobs [3].", SOURCES)
                assert got == [{"title": "Careers"}], f"got {got!r}"

            def test_invalid_numbers_are_ignored():
                assert cited_sources("Made up [7]. Also [0].", SOURCES) == []
                got = cited_sources("Mixed [4] [1].", SOURCES)
                assert got == [{"title": "Refunds"}], f"got {got!r}"

            def test_no_citations():
                assert cited_sources("No citations.", SOURCES) == []
        ''',
        "solution": r'''
            import re


            def cited_sources(answer, sources):
                seen = set()
                result = []
                for match in re.findall(r"\[(\d+)\]", answer):
                    n = int(match)
                    if 1 <= n <= len(sources) and n not in seen:
                        seen.add(n)
                        result.append(sources[n - 1])
                return result
        ''',
        "hints": [
            "The displayed number and Python list index use different starting conventions.",
            "Keep a record of already included citations while walking the matches in appearance order.",
            "Ignore invalid or repeated numbers, translate each accepted number into its source position, and append that source to the result.",
        ],
    },
    # ---------------------------------------------------------------- difficulty 2
    {
        "id": "rag-answers-6",
        "title": "Budgeted grounded prompt",
        "difficulty": 2,
        "placement": True,
        "lesson": r'''
            ## Select sources before building the final layout

            Your final prompt must combine a source-text budget, source names, citation numbering, and exact section formatting. Keep those responsibilities separate while planning. First choose the passages, then describe the chosen list, and only then assemble the full prompt.

            This exercise combines three earlier steps. First you select the ranked chunks
            that fit in the budget. Then you number the kept chunks from 1 and add each
            chunk's source name to its line. Last you place the lines between the
            instructions and the question.

            ```python
            chunks = [
                {"text": "Paris is in France.", "source": "france.md"},
                {"text": "Rome is in Italy.", "source": "italy.md"},
            ]
            for n, c in enumerate(chunks, start=1):
                print(f"[{n}] ({c['source']}) {c['text']}")
            # [1] (france.md) Paris is in France.
            # [2] (italy.md) Rome is in Italy.
            ```

            ```quiz
            Which list determines citation numbering?
            - [x] The kept passages :: Skipped passages must not consume numbers in the final source block.
            - [ ] All original candidates :: The model cannot cite passages that were not supplied.
            ```

            Number the chunks after you select them. A skipped chunk gets no number because it is absent from the final prompt.

            ```predict
            selected = ["brief note", "short fact"]
            print([number for number, text in enumerate(selected, start=1)])
            ---
            Numbers are assigned to the selected list, so they are consecutive.
            ```

            **Watch out:** The exercise budget measures only chunk text. Adding source labels and instructions makes the whole prompt longer than that amount, which is expected under this narrow contract.

            **In short:** Select under the stated budget, number that selection, then format its labels and question.
        ''',
        "prompt": r'''
            Build the full grounded prompt from ranked chunks, respecting a character budget.

            **Your job:** write `build_prompt(question, chunks, max_chars)`

            **What goes in**
            - `question`: the user's question (`str`)
            - `chunks`: a list of dicts `{"text": ..., "source": ...}`, best-ranked first
            - `max_chars`: the budget for the **texts** of the chunks (`int`)

            **What comes out**
            - Return the prompt string (see layout below)

            **Rules**
            - Choose chunks greedily in order: keep a chunk if the total `len(text)` of the kept
              chunks stays `<= max_chars`; skip one that doesn't fit and keep going.
            - Number the **kept** chunks from 1, one line each: `"[n] (source) text"`.
            - Layout: `HEADER` (the starter constant), an empty line, `Sources:`, the numbered
              lines, an empty line, then `Question: <question>`. Lines joined with `"\n"`,
              no newline at the end.
            - If no chunk fits (or `chunks` is empty), raise `ValueError`.

            **Examples**
            ```python
            chunks = [
                {"text": "Refunds take 5 days.", "source": "refunds.md"},   # 20 chars
                {"text": "x" * 50, "source": "big.md"},                    # 50 chars
                {"text": "Shipping is free.", "source": "shipping.md"},    # 17 chars
            ]
            build_prompt("How long do refunds take?", chunks, 40)
            # returns HEADER + "\n\nSources:\n[1] (refunds.md) Refunds take 5 days.\n[2] (shipping.md) Shipping is free.\n\nQuestion: How long do refunds take?"
            build_prompt("Q?", chunks, 5)      # raises ValueError
            ```
        ''',
        "starter": r'''
            HEADER = "Answer using only the numbered sources. Cite them like [1]. If they don't contain the answer, say \"I don't know\"."


            def build_prompt(question, chunks, max_chars):
                ...
        ''',
        "tests": r'''
            from solution import build_prompt, HEADER

            CHUNKS = [
                {"text": "Refunds take 5 days.", "source": "refunds.md"},
                {"text": "x" * 50, "source": "big.md"},
                {"text": "Shipping is free.", "source": "shipping.md"},
            ]

            def test_header_unchanged():
                assert HEADER == "Answer using only the numbered sources. Cite them like [1]. If they don't contain the answer, say \"I don't know\"."

            def test_skips_chunk_over_budget_and_renumbers():
                got = build_prompt("How long do refunds take?", CHUNKS, 40)
                want = (HEADER + "\n\nSources:\n[1] (refunds.md) Refunds take 5 days.\n"
                        "[2] (shipping.md) Shipping is free.\n\nQuestion: How long do refunds take?")
                assert got == want, f"got {got!r}"

            def test_big_budget_keeps_everything_in_order():
                got = build_prompt("Q?", CHUNKS, 1000)
                assert "[2] (big.md) " + "x" * 50 in got, f"got {got!r}"
                assert got.index("[1] (refunds.md)") < got.index("[3] (shipping.md)"), f"got {got!r}"
                assert got.endswith("\n\nQuestion: Q?"), f"got {got!r}"

            def test_exact_budget_is_allowed():
                got = build_prompt("Q?", CHUNKS[:1], 20)
                assert got == HEADER + "\n\nSources:\n[1] (refunds.md) Refunds take 5 days.\n\nQuestion: Q?", f"got {got!r}"

            def test_nothing_fits_raises_value_error():
                for chunks, budget in ((CHUNKS, 5), ([], 100)):
                    try:
                        build_prompt("Q?", chunks, budget)
                    except ValueError:
                        continue
                    assert False, f"expected ValueError for budget={budget}, chunks={len(chunks)}"
        ''',
        "solution": r'''
            HEADER = "Answer using only the numbered sources. Cite them like [1]. If they don't contain the answer, say \"I don't know\"."


            def build_prompt(question, chunks, max_chars):
                kept = []
                used = 0
                for chunk in chunks:
                    size = len(chunk["text"])
                    if used + size > max_chars:
                        continue
                    kept.append(chunk)
                    used += size
                if not kept:
                    raise ValueError("no chunk fits in the context budget")
                lines = [f"[{n}] ({c['source']}) {c['text']}" for n, c in enumerate(kept, start=1)]
                sources = "\n".join(lines)
                return f"{HEADER}\n\nSources:\n{sources}\n\nQuestion: {question}"
        ''',
        "hints": [
            "Keep selection, numbering, and final formatting as separate stages.",
            "Only passage text counts toward the specified budget.",
            "Choose fitting passages in order, reject an empty selection, number the kept records with source names, and assemble the exact prompt layout.",
        ],
    },
    {
        "id": "rag-answers-7",
        "title": "Flag unsupported sentences",
        "difficulty": 2,
        "lesson": r'''
            ## Flag missing citation markers for review

            A sentence has no visible citation marker. Your interface can flag it for review, but absence of a marker alone does not tell you whether the claim is true or supported somewhere in the sources. This step checks that narrow formatting signal.

            The task's title uses "unsupported" as a short label, but the implemented test is deliberately narrower: it looks for sentences without a bracketed number. It does not read the sources or decide whether a sentence follows from them.

            ```python
            import re
            lines = ["Delivery takes a week [2].", "Delivery takes a week."]
            for line in lines:
                print(bool(re.search(r"\[\d+\]", line)))
            # True
            # False
            ```

            ```quiz
            What does this detector establish about a flagged sentence?
            - [x] It lacks the required marker syntax :: Determining factual support requires a separate content check.
            - [ ] It is definitely invented :: A missing marker is not proof that a claim is false.
            ```

            The two sentences make the same claim. The pattern finds a marker only in the first one. This is a useful distinction when building a review interface: you can show what was checked without claiming more than the check establishes.

            First divide the answer using the task's stated sentence-boundary rule. Skip empty pieces, then apply the marker test to each remaining piece. Return flagged sentences in their original order so a reviewer can locate them in the answer. This is a **heuristic**, a limited rule that detects one signal rather than deciding the entire question of factual support.

            ```predict
            import re
            print(bool(re.search(r"\[\d+\]", "A fact [3].")))
            print(bool(re.search(r"\[\d+\]", "A fact.")))
            ---
            The pattern detects marker syntax and does not inspect the underlying claim.
            ```

            **Watch out:** A sentence with a marker may still cite an unrelated source. Treat both presence and absence checks as limited signals, not as factual verification.

            **In short:** Use missing markers to identify sentences needing review, without claiming to verify their meaning.
        ''',
        "prompt": r'''
            Find the sentences of an answer that don't cite any source.

            **Your job:** write `uncited_sentences(answer)`

            **What goes in**
            - `answer`: the model's reply (`str`)

            **What comes out**
            - Return a list of the sentences (`str`) that contain no citation, in order

            **Rules**
            - Split sentences with exactly `re.split(r"(?<=[.!?])\s+", answer.strip())`
              (it splits on whitespace that follows `.`, `!` or `?`, and keeps the punctuation).
            - A sentence is cited if it contains `[digits]`, e.g. `[1]` or `[12]`.
            - Skip empty sentences. An empty or blank answer returns `[]`.

            **Examples**
            ```python
            uncited_sentences("Refunds take 5 days [1]. Shipping is free! Returns are easy [2].")
            # returns ["Shipping is free!"]
            uncited_sentences("All good [1]. Really [2].")     # returns []
            uncited_sentences("Nothing cited. At all?")        # returns ["Nothing cited.", "At all?"]
            uncited_sentences("   ")                           # returns []
            ```
        ''',
        "starter": r'''
            import re


            def uncited_sentences(answer):
                ...
        ''',
        "tests": r'''
            from solution import uncited_sentences

            def test_flags_sentence_without_citation():
                got = uncited_sentences("Refunds take 5 days [1]. Shipping is free! Returns are easy [2].")
                assert got == ["Shipping is free!"], f"got {got!r}"

            def test_all_cited_gives_empty_list():
                assert uncited_sentences("All good [1]. Really [2].") == []

            def test_all_uncited_keeps_order_and_punctuation():
                got = uncited_sentences("Nothing cited. At all?")
                assert got == ["Nothing cited.", "At all?"], f"got {got!r}"

            def test_brackets_without_digits_are_not_citations():
                got = uncited_sentences("See [a]. Ok [3].")
                assert got == ["See [a]."], f"got {got!r}"

            def test_blank_answer():
                assert uncited_sentences("   ") == []
                assert uncited_sentences("") == []
        ''',
        "solution": r'''
            import re


            def uncited_sentences(answer):
                sentences = re.split(r"(?<=[.!?])\s+", answer.strip())
                return [s for s in sentences if s and not re.search(r"\[\d+\]", s)]
        ''',
        "hints": [
            "Check the sentence list produced by the specified splitting rule.",
            "An empty piece is not a sentence to report.",
            "Split and trim as specified, ignore empty pieces, and retain the sentences with no bracketed-number match.",
        ],
    },
    {
        "id": "rag-answers-8",
        "title": "Retry bad citations",
        "difficulty": 2,
        "lesson": r'''
            ## Retry marker failures without an endless loop

            The answer either omits citations or refers to unavailable sources. Tell the next attempt what citation format is required, but limit the number of calls. A successful syntax-and-range check should end the loop immediately rather than consume the remaining attempts.

            The structured-output chapter introduced retries. Here you retry when the reply
            cites no source, or cites a source that does not exist. The retry prompt states
            what was wrong. The loop stops after a fixed number of attempts.

            Step through the stages, including the path back to the first stage.

            ```diagram
            {"type":"flow","title":"Retry loop for bad citations","steps":[
            {"label":"Call the model","detail":"The first call sends the original prompt. Each retry sends the original prompt plus the feedback text.","code":"llm(current)"},
            {"label":"Extract citations","detail":"re.findall returns the cited numbers as strings. int() converts them.","code":"reply: Yes [5].\nnums:  [5]"},
            {"label":"Check citations","detail":"The reply is good when there is at least one number and every number is between 1 and n_sources.","code":"n_sources = 3\nbool([5]) is True\n1 <= 5 <= 3 is False"},
            {"label":"Return or retry","detail":"A good reply is returned. A bad reply starts another attempt. When no attempts remain, the function raises ValueError.","code":"good reply  -> return it\nbad reply   -> next attempt\nno attempts -> ValueError"}
            ],"loop":{"from":3,"to":0,"label":"while the citations are bad and attempts remain"}}
            ```

            `all()` of an empty sequence is `True`, so test separately that the list of
            numbers is not empty.

            ```python
            print(all(1 <= n <= 3 for n in []))
            # True
            print(bool([]))
            # False
            ```

            ```quiz
            Why is an all-in-range check insufficient by itself?
            - [x] An empty list passes all :: You must also require at least one citation.
            - [ ] All always rejects empty lists :: Its empty-input result is True.
            ```



            ```predict
            numbers = []
            print(all(1 <= n <= 2 for n in numbers))
            print(bool(numbers))
            ---
            Every item in an empty list satisfies the condition vacuously, but there is no citation present.
            ```

            **Watch out:** The feedback prompt is based on the original prompt plus the stated feedback. Repeatedly appending feedback can unintentionally grow it on every attempt.

            **In short:** Require nonempty valid-range citations, stop on success, and cap the total attempts.
        ''',
        "prompt": r'''
            Call the model, check its citations, and retry with feedback when they're bad.

            **Your job:** write `answer_with_retry(prompt, llm, n_sources, max_attempts=2)`

            **What goes in**
            - `prompt`: the grounded prompt (`str`)
            - `llm`: a function `llm(prompt_text) -> reply (str)`
            - `n_sources`: how many numbered sources the prompt contains (`int`)
            - `max_attempts`: the maximum number of `llm` calls (`int`, default `2`)

            **What comes out**
            - Return the first reply whose citations are good

            **Rules**
            - A reply is good if it has **at least one** citation `[n]` and **every** citation is
              between `1` and `n_sources`.
            - The first call sends `prompt` unchanged.
            - Every retry sends `prompt + FEEDBACK.format(n=n_sources)` (`FEEDBACK` is the
              starter constant), i.e. always the **original** prompt plus the feedback once.
            - If no reply is good after `max_attempts` calls, raise `ValueError`.

            **Examples**
            ```python
            # fake llm replies "Yes [5]." first, then "Yes [1]."
            answer_with_retry("P", llm, 3)
            # 1st call: llm("P")                                   -> "Yes [5]."  (invalid)
            # 2nd call: llm("P" + FEEDBACK.format(n=3))            -> "Yes [1]."  (good)
            # returns "Yes [1]."
            answer_with_retry("P", always_uncited_llm, 3)          # raises ValueError after 2 calls
            ```
        ''',
        "starter": r'''
            import re

            FEEDBACK = "\n\nYour previous answer had missing or invalid citations. Cite only sources [1] to [{n}]."


            def answer_with_retry(prompt, llm, n_sources, max_attempts=2):
                ...
        ''',
        "tests": r'''
            from solution import answer_with_retry, FEEDBACK

            def scripted(*replies):
                calls = []
                def llm(prompt):
                    calls.append(prompt)
                    return replies[len(calls) - 1]
                return llm, calls

            def test_good_first_answer_is_returned_after_one_call():
                llm, calls = scripted("Yes [1][2].")
                assert answer_with_retry("P", llm, 2) == "Yes [1][2]."
                assert calls == ["P"], f"llm calls: {calls!r}"

            def test_invalid_citation_triggers_retry_with_feedback():
                llm, calls = scripted("Yes [5].", "Yes [1].")
                got = answer_with_retry("P", llm, 3)
                assert got == "Yes [1].", f"got {got!r}"
                assert calls == ["P", "P" + FEEDBACK.format(n=3)], f"llm calls: {calls!r}"

            def test_missing_citations_trigger_retry():
                llm, calls = scripted("No sources at all.", "Now cited [2].")
                assert answer_with_retry("P", llm, 2) == "Now cited [2]."

            def test_feedback_added_to_original_prompt_only_once():
                llm, calls = scripted("bad", "bad [0]", "ok [1]")
                assert answer_with_retry("P", llm, 1, max_attempts=3) == "ok [1]"
                assert calls[2] == "P" + FEEDBACK.format(n=1), f"llm calls: {calls!r}"

            def test_gives_up_with_value_error():
                llm, calls = scripted("bad", "still bad", "never reached [1]")
                try:
                    answer_with_retry("P", llm, 2)
                except ValueError:
                    assert len(calls) == 2, f"llm was called {len(calls)} times"
                    return
                assert False, "expected ValueError"
        ''',
        "solution": r'''
            import re

            FEEDBACK = "\n\nYour previous answer had missing or invalid citations. Cite only sources [1] to [{n}]."


            def citations_ok(reply, n_sources):
                nums = [int(n) for n in re.findall(r"\[(\d+)\]", reply)]
                return bool(nums) and all(1 <= n <= n_sources for n in nums)


            def answer_with_retry(prompt, llm, n_sources, max_attempts=2):
                current = prompt
                for _ in range(max_attempts):
                    reply = llm(current)
                    if citations_ok(reply, n_sources):
                        return reply
                    current = prompt + FEEDBACK.format(n=n_sources)
                raise ValueError(f"no answer with valid citations after {max_attempts} attempts")
        ''',
        "hints": [
            "A usable marker list must be nonempty and entirely within range.",
            "Every retry uses the original prompt plus the required feedback.",
            "Call within the limit, check markers, return an accepted reply immediately, otherwise prepare the retry prompt and raise on exhaustion.",
        ],
    },
    # ---------------------------------------------------------------- difficulty 3
    {
        "id": "rag-answers-9",
        "title": "End-to-end RAG pipeline",
        "difficulty": 3,
        "lesson": r'''
            ## Connect retrieval, answering, and source display

            You can now turn stored passages into an answer with source names. Plan the data passed between stages so the source list used for numbering is also the list used to resolve citations. Otherwise an apparently valid number can link to the wrong document.

            This exercise combines every step of the chapter in one class. `add` stores each
            chunk with its vector. `ask` scores the chunks by cosine similarity, declines
            when no score reaches the threshold, builds the numbered prompt, calls the model
            and maps the citations to source names. Both `embed` and `llm` are injected, so
            the whole pipeline runs in a test with no network.

            Sorting `(score, name)` pairs by score with `reverse=True` puts the best first.
            `sort` keeps the original order of pairs with equal scores.

            ```python
            scored = [(0.7, "a.md"), (0.2, "b.md"), (1.0, "c.md"), (0.7, "d.md")]
            accepted = [pair for pair in scored if pair[0] >= 0.5]
            accepted.sort(key=lambda pair: pair[0], reverse=True)
            print(accepted[:2])
            # [(1.0, 'c.md'), (0.7, 'a.md')]
            ```

            ```quiz
            Why keep the selected sources until after the model replies?
            - [x] Citation numbers refer to that exact ordered selection :: Re-running or reordering retrieval can change their meaning.
            - [ ] Citation numbers are permanent document ids :: They are local numbers assigned for this request.
            ```



            ```match
            embedding function :: turns supplied text into a test vector
            retrieval stage :: selects and orders eligible passages
            model function :: receives the constructed prompt
            citation mapping :: links reply numbers to that selection
            ```

            **Watch out:** The fake embedding and model functions test the pipeline's mechanics. They do not prove retrieval quality, factual grounding, or resistance to malicious source text.

            **In short:** Use one consistent selected-source list from prompt construction through final citation mapping.
        ''',
        "research": {
            "note": "Read Anthropic's write-up on contextual retrieval: how adding context to chunks, hybrid (embeddings + BM25) search and re-ranking reduce failed retrievals. Map each idea to a function you wrote in the retrieval chapter.",
            "links": [
                {"title": "Introducing Contextual Retrieval - Anthropic", "url": "https://www.anthropic.com/news/contextual-retrieval"},
            ],
        },
        "prompt": r'''
            Build a complete retrieve-then-generate pipeline with injected models.

            **Your job:** write a class `RagPipeline`

            **What goes in**
            - `RagPipeline(embed, llm, k=3, threshold=0.5)`:
              `embed(text) -> list of numbers`, `llm(prompt) -> reply str`
            - `.add(text, source)`: stores a chunk; calls `embed(text)` once
            - `.ask(question)`: returns a dict `{"answer": str, "sources": list, "declined": bool}`

            **What `ask` does**
            1. Calls `embed(question)` once. Scores every stored chunk with cosine similarity
               (a zero vector scores `0.0`).
            2. Keeps chunks with `score >= threshold`, best first (ties: the order they were
               added), at most `k` of them.
            3. If none are kept: returns `{"answer": DECLINE, "sources": [], "declined": True}`
               **without calling `llm`**.
            4. Otherwise calls `llm` once with
               `"Sources:\n[1] text\n[2] text...\n\nQuestion: <question>"` (kept chunks, numbered from 1).
            5. Returns `{"answer": reply, "sources": [...], "declined": False}` where `sources`
               lists the `source` of each chunk the reply cites: citation `[n]` means the n-th
               kept chunk; ignore numbers outside `1..len(kept)`; each source name once, in
               first-cited order.

            **Examples**
            ```python
            def fake_embed(text):
                words = text.lower().split()
                return [words.count("refund"), words.count("shipping")]

            def fake_llm(prompt):
                return "Refunds take 5 days [1]. See also [9]."

            rag = RagPipeline(fake_embed, fake_llm, k=2)
            rag.add("refund takes 5 days", "refunds.md")
            rag.add("shipping is free", "shipping.md")
            rag.ask("refund time?")
            # llm gets "Sources:\n[1] refund takes 5 days\n\nQuestion: refund time?"
            # returns {"answer": "Refunds take 5 days [1]. See also [9].", "sources": ["refunds.md"], "declined": False}
            rag.ask("what about pizza?")
            # returns {"answer": DECLINE, "sources": [], "declined": True}
            ```
        ''',
        "starter": r'''
            import math
            import re

            DECLINE = "I don't know based on the available documents."


            class RagPipeline:
                def __init__(self, embed, llm, k=3, threshold=0.5):
                    ...
        ''',
        "tests": r'''
            from solution import RagPipeline, DECLINE

            def fake_embed_factory():
                calls = []
                def embed(text):
                    calls.append(text)
                    words = text.lower().split()
                    return [words.count("refund"), words.count("shipping"), words.count("free")]
                return embed, calls

            def fake_llm_factory(reply):
                calls = []
                def llm(prompt):
                    calls.append(prompt)
                    return reply
                return llm, calls

            def build(reply="Refunds take 5 days [1].", k=3, threshold=0.5):
                embed, ecalls = fake_embed_factory()
                llm, lcalls = fake_llm_factory(reply)
                rag = RagPipeline(embed, llm, k=k, threshold=threshold)
                rag.add("refund takes 5 days", "refunds.md")
                rag.add("shipping is free", "shipping.md")
                rag.add("free shipping over 50", "promo.md")
                return rag, ecalls, lcalls

            def test_answers_with_only_relevant_chunks():
                rag, ecalls, lcalls = build()
                got = rag.ask("refund time?")
                assert lcalls == ["Sources:\n[1] refund takes 5 days\n\nQuestion: refund time?"], f"llm got {lcalls!r}"
                assert got == {"answer": "Refunds take 5 days [1].", "sources": ["refunds.md"], "declined": False}, f"got {got!r}"

            def test_declines_without_calling_llm():
                rag, ecalls, lcalls = build()
                got = rag.ask("what about pizza?")
                assert got == {"answer": DECLINE, "sources": [], "declined": True}, f"got {got!r}"
                assert lcalls == [], "llm must not be called when declining"

            def test_ranks_by_cosine_and_respects_k():
                rag, ecalls, lcalls = build(reply="x [2][1][2]", k=2)
                got = rag.ask("free shipping")
                # both shipping chunks score 1.0 (tie keeps insertion order); k=2
                assert lcalls == ["Sources:\n[1] shipping is free\n[2] free shipping over 50\n\nQuestion: free shipping"], f"llm got {lcalls!r}"
                assert got["sources"] == ["promo.md", "shipping.md"], f"got {got!r}"

            def test_invalid_citations_are_ignored():
                rag, ecalls, lcalls = build(reply="Yes [1]. Also [5] and [0].")
                got = rag.ask("refund")
                assert got["sources"] == ["refunds.md"], f"got {got!r}"
                assert got["answer"] == "Yes [1]. Also [5] and [0].", f"got {got!r}"

            def test_threshold_filters_weak_chunks():
                rag, ecalls, lcalls = build(reply="ok [1]", threshold=0.9)
                rag.ask("shipping")
                # "shipping" -> [0,1,0]: cos with both shipping chunks is about 0.707 < 0.9
                assert lcalls == [], f"llm got {lcalls!r}"

            def test_embed_called_once_per_add_and_per_ask():
                rag, ecalls, lcalls = build()
                assert ecalls == ["refund takes 5 days", "shipping is free", "free shipping over 50"], f"embed calls: {ecalls!r}"
                rag.ask("refund")
                assert ecalls[3:] == ["refund"], f"embed calls: {ecalls!r}"

            def test_empty_pipeline_declines():
                embed, _ = fake_embed_factory()
                llm, lcalls = fake_llm_factory("x")
                got = RagPipeline(embed, llm).ask("refund")
                assert got["declined"] is True and lcalls == [], f"got {got!r}"
        ''',
        "solution": r'''
            import math
            import re

            DECLINE = "I don't know based on the available documents."


            def cosine(a, b):
                norm_a = math.sqrt(sum(x * x for x in a))
                norm_b = math.sqrt(sum(x * x for x in b))
                if norm_a == 0 or norm_b == 0:
                    return 0.0
                return sum(x * y for x, y in zip(a, b)) / (norm_a * norm_b)


            class RagPipeline:
                def __init__(self, embed, llm, k=3, threshold=0.5):
                    self.embed = embed
                    self.llm = llm
                    self.k = k
                    self.threshold = threshold
                    self.chunks = []

                def add(self, text, source):
                    self.chunks.append({"text": text, "source": source, "vector": self.embed(text)})

                def retrieve(self, question):
                    q = self.embed(question)
                    scored = [(cosine(q, c["vector"]), c) for c in self.chunks]
                    good = [pair for pair in scored if pair[0] >= self.threshold]
                    good.sort(key=lambda pair: pair[0], reverse=True)
                    return [c for _, c in good[: self.k]]

                def ask(self, question):
                    kept = self.retrieve(question)
                    if not kept:
                        return {"answer": DECLINE, "sources": [], "declined": True}
                    sources_text = "\n".join(f"[{n}] {c['text']}" for n, c in enumerate(kept, start=1))
                    reply = self.llm(f"Sources:\n{sources_text}\n\nQuestion: {question}")
                    names = []
                    for match in re.findall(r"\[(\d+)\]", reply):
                        n = int(match)
                        if 1 <= n <= len(kept) and kept[n - 1]["source"] not in names:
                            names.append(kept[n - 1]["source"])
                    return {"answer": reply, "sources": names, "declined": False}
        ''',
        "hints": [
            "Keep retrieval results available for both numbering and later source mapping.",
            "The no-source branch must avoid calling the model.",
            "Store passage vectors, embed each question once, select ranked qualifying passages, build and send the prompt, then map valid citations to distinct source names.",
        ],
    },
]
