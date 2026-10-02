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
                 "declining to answer", "citations", "citation validation", "retry with feedback",
                 "RAG pipeline"],
}

LESSON = r'''
## RAG in one picture

**Retrieve** the best chunks -> **augment** the prompt with them -> **generate** the answer.
The model answers from *your* documents, like a student in an open-book exam.

## The grounded prompt

```text
Answer using only the numbered sources. Cite them like [1].
If the sources don't contain the answer, say "I don't know".

Sources:
[1] (refunds.md) Refunds take 5 business days.
[2] (shipping.md) Shipping is free over 50 EUR.

Question: How long do refunds take?
```

- Number sources with `enumerate(chunks, start=1)`: citation `[n]` points at source `n`.
- Keep instructions, sources and question clearly separated.
- **Context budget**: prompts have limited room (and cost per token). Pack the best-ranked
  chunks first; skip a chunk that doesn't fit, a later smaller one may still fit.

## Knowing when not to answer

If the **best** similarity score is below a threshold, retrieval found nothing useful.
Return a fixed "I don't know" message *without* calling the LLM: cheaper, and it can't
make something up.

## Checking the answer

```python
import re
answer, n_sources = "Yes [1]. Also [4] and [2][4].", 3
nums = [int(n) for n in re.findall(r"\[(\d+)\]", answer)]   # citations, in order
print(nums)
print(sorted({n for n in nums if not 1 <= n <= n_sources}))   # invalid ones
```

- A citation to a source that doesn't exist (`[7]` with 3 sources) is a **hallucinated
  citation**: reject it, or retry with feedback ("only cite [1] to [3]").
- Sentences with no citation at all are unsupported claims worth flagging.
- Map valid numbers back to source names to show "Sources: refunds.md".

## Testing it

Inject `embed` and `llm` as functions. In tests, a fake `llm` returns a canned answer and
records the prompt it received, so you can assert on the prompt *and* the post-processing
without a network or an API key.

## Gotchas

- Numbers in `[n]` are 1-based; Python lists are 0-based: source `n` is `sources[n - 1]`.
- De-duplicate cited sources but keep first-cited order.
- Decline based on the **best** score, not the worst.
- Retries need a limit (`max_attempts`), or a stubborn model loops forever.
'''

EXERCISES = [
    # ---------------------------------------------------------------- difficulty 0
    {
        "id": "rag-answers-s1",
        "title": "What gets printed?",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## The open-book exam

            An LLM on its own is a student taking a closed-book exam: it answers from memory,
            and when memory fails it may confidently make something up. **RAG**
            (retrieval-augmented generation) turns it into an **open-book** exam: you hand the
            model a few index cards (the retrieved chunks) and tell it to answer from those.

            To let the model say *which* card it used, number the cards. `enumerate` gives you
            a counter next to each item; `start=1` makes it count like humans do:

            ```python
            cards = ["Paris is in France.", "Rome is in Italy."]
            for n, card in enumerate(cards, start=1):
                print(n, card)
            ```

            The numbered cards are called **sources**. The model can then point at a card
            with a **citation** like `[2]`, and your app can show the user where the answer
            came from.
        ''',
        "prompt": r'''Read the code and type exactly what it prints.''',
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
            `enumerate(chunks, start=1)` yields `(1, "Refunds take 5 days.")` then
            `(2, "Shipping is free.")`. The f-string puts the number in square brackets before
            the text. Finally `len(chunks)` is `2`.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "`enumerate(..., start=1)` pairs each item with a counter that starts at 1, not 0.",
            "The loop prints one line per chunk: the number in square brackets, a space, then the text. Then one more line with the length.",
            "Line 1: [1] followed by the first chunk. Line 2: [2] followed by the second chunk. Line 3: how many chunks there are.",
        ],
    },
    {
        "id": "rag-answers-s2",
        "title": "Number the sources",
        "difficulty": 0,
        "lesson": r'''
            ## One block of numbered cards

            The prompt needs all the sources as **one string**, one per line. Remember
            `"\n".join(...)` from the strings chapter: it glues a list of strings together
            with a newline between them (not after the last one).

            ```python
            lines = ["[1] alpha", "[2] beta"]
            block = "\n".join(lines)
            print(block)
            print(repr(block))
            ```

            You can feed `join` a generator expression directly, no temporary list needed:

            ```python
            words = ["x", "y", "z"]
            print(", ".join(f"<{w}>" for w in words))
            ```

            Watch out: citations are **1-based**. If you number from 0, the model's `[1]`
            points at the wrong card.
        ''',
        "prompt": r'''
            Format retrieved chunks as a numbered list of sources for a prompt.

            **Write:** fill in the blank (`___`) in `format_sources(chunks)`

            - `chunks`: a list of strings, e.g. `["Refunds take 5 days.", "Shipping is free."]`
            - **Returns:** one string with a line `"[n] text"` per chunk, numbered from **1**,
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
            "The blank is the number `enumerate` starts counting from.",
            "Citations are numbered like humans count, so the first source must be number 1.",
            "Replace `___` with the integer one.",
        ],
    },
    {
        "id": "rag-answers-s3",
        "title": "The grounded prompt",
        "difficulty": 0,
        "lesson": r'''
            ## The exam rules at the top of the paper

            An open-book exam paper starts with the rules: "Use only the provided material.
            Cite your sources." A RAG prompt does the same, in a fixed layout:

            1. the **instructions** (answer only from the sources, cite them),
            2. the **sources** (the numbered cards),
            3. the **question**.

            Keeping these three parts clearly separated (with blank lines and labels like
            `Sources:`) helps the model tell *your instructions* apart from *the documents*.
            A prompt built like this is called a **grounded prompt**: the answer is grounded
            in (tied to) the sources.

            ```python
            sources = "[1] Paris is in France."
            question = "Where is Paris?"
            prompt = f"Use the sources.\n\nSources:\n{sources}\n\nQuestion: {question}"
            print(prompt)
            ```

            `\n\n` makes a blank line: one newline ends the line, the second one is the empty line.
        ''',
        "prompt": r'''
            Build the grounded prompt that will be sent to the model.

            **Write:** `grounded_prompt(question, sources_text)`

            - `question`: the user's question (`str`), e.g. `"How long do refunds take?"`
            - `sources_text`: the already-numbered sources (`str`), e.g. `"[1] Refunds take 5 days."`
            - **Returns:** exactly this string (with the values filled in):

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
            "One f-string (or a few joined together) with `\\n` for line breaks is enough.",
            "Write the instruction line, then a blank line, then `Sources:` on its own line followed by the sources, then a blank line, then `Question: ` and the question.",
            "Return: the exact instruction sentence + \"\\n\\n\" + \"Sources:\\n\" + sources_text + \"\\n\\n\" + \"Question: \" + question. Copy the instruction sentence character by character.",
        ],
    },
    {
        "id": "rag-answers-s4",
        "title": "Fix the confidence check",
        "difficulty": 0,
        "lesson": r'''
            ## "I'm not sure" is a good answer

            A good doctor says "I don't know, let's run a test" instead of guessing. A RAG app
            should too. If retrieval found nothing relevant, handing the model weak cards
            invites it to make something up (a **hallucination**).

            The retriever's scores tell you how good the cards are. The rule is simple: if the
            **best** card scores below a **threshold** (say `0.5`), don't call the model.
            Just reply "I don't know based on the available documents."

            ```python
            scores = [0.31, 0.72, 0.18]
            print(max(scores))
            print(max(scores) >= 0.5)
            print(min(scores) >= 0.5)
            ```

            It only takes **one** good card to answer well, so it's the best score that
            matters, not the worst. The right threshold depends on your embedding model;
            you pick it by looking at real examples (that's what evals are for, later).
        ''',
        "prompt": r'''
            `has_good_match` decides whether retrieval found anything worth answering from.
            It refuses to answer far too often. Find and fix the bug.

            **Write:** fix `has_good_match(scores, threshold)`

            - `scores`: a list of similarity scores (`float`), in any order
            - `threshold`: the minimum acceptable score (`float`), e.g. `0.5`
            - **Returns:** `True` if the **best** score is greater than or equal to `threshold`, else `False`

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
            "Look at which score the function compares with the threshold.",
            "It checks the worst score. One strong source is enough, so it should check the best score.",
            "Replace `min` with `max` in the last line.",
        ],
    },
    {
        "id": "rag-answers-s5",
        "title": "Find the citations",
        "difficulty": 0,
        "lesson": r'''
            ## Footnotes you can check

            The model's answer comes back with citations, like footnotes in a book:
            `"Refunds take 5 days [1]. Shipping is free [2]."`. To check or display them, your
            code needs to pull the numbers out.

            Remember regex groups? With `re.findall`, if the pattern has one group `( )`,
            you get back only the part inside the group. Square brackets are special in regex,
            so a literal `[` is written `\[`:

            ```python
            import re

            answer = "Refunds take 5 days [1]. Free shipping [2][1]."
            print(re.findall(r"\[(\d+)\]", answer))
            print([int(n) for n in re.findall(r"\[(\d+)\]", answer)])
            ```

            `\d+` means "one or more digits". `findall` returns **strings**, so convert them
            with `int()` if you want to compare them with numbers.

            Watch out: `"[a]"` or `"[ 1 ]"` are not citations. The pattern only accepts digits
            directly inside the brackets.
        ''',
        "prompt": r'''
            Extract the citation numbers from a model's answer.

            **Write:** `find_citations(answer)`

            - `answer`: the model's reply (`str`), e.g. `"Refunds take 5 days [1]. Free shipping [2][1]."`
            - **Returns:** a list of `int`s: every `[n]` citation (digits inside square
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
            "Use `re.findall` with a pattern that has a group around the digits.",
            "The pattern is: a literal opening bracket, one or more digits (captured), a literal closing bracket. Then convert every match to an int.",
            "1) matches = re.findall(r\"\\[(\\d+)\\]\", answer). 2) Return a list comprehension that applies `int()` to each match.",
        ],
    },
    {
        "id": "rag-answers-s6",
        "title": "What fits in the budget?",
        "difficulty": 0,
        "mode": "predict",
        "lesson": r'''
            ## Packing a suitcase

            A prompt is a suitcase with a size limit: the model's **context window**, and your
            bill (you pay per token). You can't pack every chunk you found. So you pack the
            most important things first (the best-ranked chunks) and stop when the suitcase
            is full. The limit is called the **context budget**.

            Real apps count tokens; here we count characters, which is a fine rough stand-in
            (about 4 characters per token in English).

            ```python
            budget = 12
            used = 0
            for word in ["pack", "this", "stuff"]:
                used += len(word)
                print(word, used, used <= budget)
            ```

            `break` stops a loop immediately, which is one way to "stop when full".
        ''',
        "prompt": r'''Read the code and type exactly what it prints.''',
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
            `"aaaa"` fits (0 + 4 = 4). `"bbbbbb"` fits exactly (4 + 6 = 10, and `10 > 10` is
            False). `"cc"` would make 12, which is over the budget, so the loop `break`s:
            `"cc"` and everything after it are left out. `used` stays at `10`.
        ''',
        "starter": "", "tests": "",
        "hints": [
            "Track `used` after each chunk, and remember `>` is strict: exactly 10 is not over 10.",
            "The first chunk brings `used` to 4, the second to 10. The third would push it past 10, which triggers `break`.",
            "Line 1: the list of the chunks kept before the break, in list notation with quotes. Line 2: the total length of those kept chunks.",
        ],
    },
    # ---------------------------------------------------------------- difficulty 1
    {
        "id": "rag-answers-1",
        "title": "Fill the context budget",
        "difficulty": 1,
        "lesson": r'''
            ## Squeezing in one more small thing

            In the last step, packing stopped at the first chunk that didn't fit. But
            suitcases are smarter than that: if the big jumper doesn't fit, you skip it and
            still squeeze in the socks. With ranked chunks, a lower-ranked but *short* chunk
            can still carry useful facts.

            So instead of `break`, use `continue`: skip this chunk, keep checking the rest.

            ```python
            sizes = [5, 9, 2]
            room = 8
            for size in sizes:
                if size > room:
                    print("skip", size)
                    continue
                room -= size
                print("pack", size, "room left", room)
            ```

            This is called a **greedy** fill: go in order of importance, take whatever still
            fits, never go back. It's simple and good enough for context packing.

            Watch out: keep the chunks in their **ranked order**, don't sort them by size.
        ''',
        "prompt": r'''
            Choose which ranked chunks go into the prompt without going over a character budget.

            **Write:** `fit_context(chunks, max_chars)`

            - `chunks`: a list of strings, best-ranked first
            - `max_chars`: the budget (`int`): the total `len` of the kept chunks must not exceed it
            - **Returns:** a new list of the kept chunks, in their original order

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
            "Loop over the chunks with a running total, and use `continue` (not `break`) when one doesn't fit.",
            "Start with an empty result and a total of 0. For each chunk: if adding its length would go over the budget, skip it; otherwise keep it and add its length to the total.",
            "1) kept, used = [], 0. 2) for chunk in chunks: if used + len(chunk) > max_chars: continue. 3) Otherwise append it and add len(chunk) to used. 4) Return kept.",
        ],
    },
    {
        "id": "rag-answers-2",
        "title": "Ask a fake LLM",
        "difficulty": 1,
        "lesson": r'''
            ## Rehearsing with a stand-in actor

            Theatre companies rehearse with a stand-in before the star arrives. Your RAG code
            does the same: it **receives** the model as a function (`llm`) instead of calling
            an API directly. In production you pass a function that calls the real API; in
            tests you pass a fake that returns a canned reply and remembers what it was sent.

            Remember messages from the LLM chapter: a list of dicts with a `role` and `content`.
            The system message holds the rules; the user message holds the sources and question.

            ```python
            seen = []

            def fake_llm(messages):
                seen.append(messages)
                return "Paris [1]."

            reply = fake_llm([{"role": "user", "content": "Where is the Eiffel Tower?"}])
            print(reply)
            print(seen[0][0]["role"])
            ```

            Because the fake records its input, a test can check that your code built the
            prompt correctly, not just that it returned *something*.
        ''',
        "prompt": r'''
            Send the question and its sources to an injected LLM function and return the reply.

            **Write:** `ask(question, chunks, llm)`

            - `question`: the user's question (`str`)
            - `chunks`: a list of retrieved texts (`str`), best first
            - `llm`: a function that takes a list of message dicts and returns the reply text (`str`)
            - **Returns:** whatever `llm` returns

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
            # [{"role": "system", "content": SYSTEM},
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
            "Reuse the numbered-sources idea (`enumerate(..., start=1)` + `\"\\n\".join`) and build a list of two dicts.",
            "Build the sources block, put it into the user content with the question, make the system and user message dicts, then return the result of calling `llm` with that list.",
            "1) sources = \"\\n\".join of f\"[{n}] {text}\" over enumerate(chunks, start=1). 2) user content = f\"Sources:\\n{sources}\\n\\nQuestion: {question}\". 3) messages = [system dict, user dict]. 4) return llm(messages).",
        ],
    },
    {
        "id": "rag-answers-3",
        "title": "Answer or decline",
        "difficulty": 1,
        "lesson": r'''
            ## The bouncer at the door

            Put a bouncer in front of the model: only good-enough sources get in. Each
            retrieved chunk arrives with its score. Chunks below the threshold are turned away.
            If nobody gets in, the bouncer answers for the model: "I don't know based on the
            available documents." and the model is never called (no cost, no made-up answer).

            ```python
            results = [("Refunds take 5 days.", 0.81), ("Our CEO likes cats.", 0.12)]
            threshold = 0.5
            good = [text for text, score in results if score >= threshold]
            print(good)
            print(len(good) == 0)
            ```

            Looping over `(text, score)` pairs and unpacking them in the `for` is called
            **tuple unpacking**. It reads much better than `pair[0]` and `pair[1]`.

            Watch out: filter out the weak chunks from the prompt too. A weak chunk in the
            prompt is noise the model may quote as if it were relevant.
        ''',
        "prompt": r'''
            Only call the model when retrieval found good sources; otherwise decline.

            **Write:** `answer_or_decline(question, results, llm, threshold=0.5)`

            - `question`: the user's question (`str`)
            - `results`: a list of `(text, score)` tuples from the retriever, best first
            - `llm`: a function that takes a prompt **string** and returns the reply (`str`)
            - `threshold`: minimum score for a source to be used (`float`, default `0.5`)
            - **Returns:** the reply text (`str`)

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
            "Filter first with a comprehension that unpacks `(text, score)`, then decide whether to call the model.",
            "Keep the texts whose score is at least the threshold. If that list is empty, return DECLINE straight away. Otherwise number the kept texts, build the prompt and return llm(prompt).",
            "1) good = [text for text, score in results if score >= threshold]. 2) if not good: return DECLINE. 3) sources = \"\\n\".join(f\"[{n}] {text}\" ...enumerate(good, start=1)). 4) return llm(f\"Sources:\\n{sources}\\n\\nQuestion: {question}\").",
        ],
    },
    {
        "id": "rag-answers-4",
        "title": "Catch invented citations",
        "difficulty": 1,
        "lesson": r'''
            ## Trust, but verify

            A student who cites "page 400" of a 120-page book has made it up. Models do this
            too: given 3 sources, they sometimes cite `[4]` or `[0]`. That's a **hallucinated
            citation**, and showing it to users destroys trust.

            The check is cheap: a valid citation `n` satisfies `1 <= n <= number_of_sources`.
            Python lets you chain the comparisons, just like in maths:

            ```python
            n_sources = 3
            for n in [0, 1, 3, 4]:
                print(n, 1 <= n <= n_sources)
            ```

            To report each bad number once, collect them in a **set** (duplicates vanish),
            then `sorted()` turns the set into a tidy list:

            ```python
            print(sorted({4, 0, 4, 9}))
            ```

            What to do with bad citations is your choice: drop them, flag the answer, or ask
            the model to try again (later in this chapter).
        ''',
        "prompt": r'''
            Find the citation numbers that point at sources that don't exist.

            **Write:** `invalid_citations(answer, n_sources)`

            - `answer`: the model's reply (`str`), containing citations like `[1]`
            - `n_sources`: how many sources were in the prompt (`int`)
            - **Returns:** a sorted list of the **distinct** cited numbers (`int`) that are
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
            "Extract the numbers with the same regex as before, then keep the ones outside the valid range.",
            "Turn every match into an int and put them in a set so duplicates disappear. Keep the numbers that are NOT between 1 and n_sources, and return them sorted.",
            "1) cited = {int(n) for n in re.findall(r\"\\[(\\d+)\\]\", answer)}. 2) Return sorted(n for n in cited if not 1 <= n <= n_sources).",
        ],
    },
    {
        "id": "rag-answers-5",
        "title": "Show the cited sources",
        "difficulty": 1,
        "lesson": r'''
            ## From footnote numbers to a reading list

            Users don't want to see `[2]`. They want "Source: shipping.md" with a link. So after
            the answer comes back, map each citation number back to the source it points at.

            Careful with counting: citation `[1]` is the **first** source, but Python lists
            start at index 0. So source `n` lives at `sources[n - 1]`.

            ```python
            sources = [{"title": "Refunds"}, {"title": "Shipping"}]
            n = 2
            print(sources[n - 1]["title"])
            ```

            If the model cites `[2]` three times, list the source once. Keep the order in which
            they were **first** cited: that usually matches the order of the answer's claims.
            A set can remember "already added", while a list keeps the order:

            ```python
            seen, order = set(), []
            for n in [2, 1, 2]:
                if n not in seen:
                    seen.add(n)
                    order.append(n)
            print(order)
            ```
        ''',
        "research": {
            "note": "Read how Anthropic's API can return citations that point at the exact passages of the documents you provided. Compare it with the [n] markers you parse by hand here.",
            "links": [
                {"title": "Citations - Anthropic docs", "url": "https://docs.anthropic.com/en/docs/build-with-claude/citations"},
            ],
        },
        "prompt": r'''
            Turn the citations in an answer into the list of source records to display.

            **Write:** `cited_sources(answer, sources)`

            - `answer`: the model's reply (`str`), with citations like `[2]`
            - `sources`: the list of source dicts that were numbered `[1]`, `[2]`, ... in the
              prompt, e.g. `[{"title": "Refunds", "url": "https://x/refunds"}, ...]`
            - **Returns:** a list of the cited source dicts, each **once**, in the order they
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
            "Extract the numbers in order, and use a set to remember which ones you already added.",
            "Walk through the citation numbers in order. Skip a number if it's out of range or already seen; otherwise mark it seen and append sources[n - 1].",
            "1) seen, result = set(), []. 2) for each match of r\"\\[(\\d+)\\]\": n = int(match). 3) if 1 <= n <= len(sources) and n not in seen: add to seen, append sources[n - 1]. 4) Return result.",
        ],
    },
    # ---------------------------------------------------------------- difficulty 2
    {
        "id": "rag-answers-6",
        "title": "Budgeted grounded prompt",
        "difficulty": 2,
        "placement": True,
        "lesson": r'''
            Putting it together: pack the ranked chunks into the budget, number the ones that
            made it, label each with where it came from, and wrap them in the instructions and
            the question.
        ''',
        "prompt": r'''
            Build the full grounded prompt from ranked chunks, respecting a character budget.

            **Write:** `build_prompt(question, chunks, max_chars)`

            - `question`: the user's question (`str`)
            - `chunks`: a list of dicts `{"text": ..., "source": ...}`, best-ranked first
            - `max_chars`: the budget for the **texts** of the chunks (`int`)
            - **Returns:** the prompt string (see layout below)

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
            "Three stages: greedy packing (like fit_context), numbering with enumerate, then one f-string for the layout.",
            "Pack by len(chunk[\"text\"]), skipping chunks that don't fit. If nothing was kept, raise ValueError. Otherwise build one \"[n] (source) text\" line per kept chunk and join them with newlines inside the template.",
            "1) kept, used = [], 0; loop: skip if used + len(text) > max_chars, else keep and add. 2) if not kept: raise ValueError. 3) lines = [f\"[{n}] ({c['source']}) {c['text']}\" for n, c in enumerate(kept, start=1)]. 4) return f\"{HEADER}\\n\\nSources:\\n\" + joined lines + f\"\\n\\nQuestion: {question}\".",
        ],
    },
    {
        "id": "rag-answers-7",
        "title": "Flag unsupported sentences",
        "difficulty": 2,
        "lesson": r'''
            Putting it together: a grounded answer should back **every** claim with a source.
            Split the answer into sentences and flag the ones without any `[n]`: those are the
            claims the model may have invented.
        ''',
        "prompt": r'''
            Find the sentences of an answer that don't cite any source.

            **Write:** `uncited_sentences(answer)`

            - `answer`: the model's reply (`str`)
            - **Returns:** a list of the sentences (`str`) that contain no citation, in order

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
            "Split with the given `re.split` call, then test each sentence with `re.search`.",
            "After splitting, keep the sentences that are not empty and in which a search for a bracketed number finds nothing.",
            "1) sentences = re.split(r\"(?<=[.!?])\\s+\", answer.strip()). 2) Return [s for s in sentences if s and not re.search(r\"\\[\\d+\\]\", s)].",
        ],
    },
    {
        "id": "rag-answers-8",
        "title": "Retry bad citations",
        "difficulty": 2,
        "lesson": r'''
            Putting it together (remember retries from the structured-output chapter): if the
            answer cites no sources, or cites sources that don't exist, ask again and tell the
            model exactly what was wrong. Stop after a fixed number of attempts.
        ''',
        "prompt": r'''
            Call the model, check its citations, and retry with feedback when they're bad.

            **Write:** `answer_with_retry(prompt, llm, n_sources, max_attempts=2)`

            - `prompt`: the grounded prompt (`str`)
            - `llm`: a function `llm(prompt_text) -> reply (str)`
            - `n_sources`: how many numbered sources the prompt contains (`int`)
            - `max_attempts`: the maximum number of `llm` calls (`int`, default `2`)
            - **Returns:** the first reply whose citations are good

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
            "Write a small helper that says whether a reply's citations are good, then loop at most `max_attempts` times.",
            "The helper extracts the citation numbers and returns True only if there's at least one and all are in range. In the loop, call the model with the current prompt; return a good reply; otherwise switch the prompt to original + feedback. After the loop, raise.",
            "1) citations_ok: nums = ints from re.findall; return bool(nums) and all(1 <= n <= n_sources ...). 2) current = prompt. 3) for _ in range(max_attempts): reply = llm(current); if ok: return reply; current = prompt + FEEDBACK.format(n=n_sources). 4) raise ValueError(...).",
        ],
    },
    # ---------------------------------------------------------------- difficulty 3
    {
        "id": "rag-answers-9",
        "title": "End-to-end RAG pipeline",
        "difficulty": 3,
        "lesson": r'''
            Putting it together: store chunks with their vectors, retrieve by cosine, decline
            when nothing is good enough, build the numbered prompt, call the model, and turn
            its citations into source names. Both models are injected, so the whole pipeline
            runs in a test with no network.
        ''',
        "research": {
            "note": "Read Anthropic's write-up on contextual retrieval: how adding context to chunks, hybrid (embeddings + BM25) search and re-ranking reduce failed retrievals. Map each idea to a function you wrote in the retrieval chapter.",
            "links": [
                {"title": "Introducing Contextual Retrieval - Anthropic", "url": "https://www.anthropic.com/news/contextual-retrieval"},
            ],
        },
        "prompt": r'''
            Build a complete retrieve-then-generate pipeline with injected models.

            **Write:** a class `RagPipeline`

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
            "Split the work into small methods: `add`, a `retrieve` helper that returns the kept chunks, and `ask`. Reuse your `cosine` function.",
            "`add` stores text, source and embed(text). `retrieve` embeds the question, scores every chunk, keeps scores >= threshold, sorts best first and slices to k. `ask` declines on an empty result, otherwise builds the numbered prompt, calls llm, and maps valid citation numbers to source names without duplicates.",
            "1) __init__ saves embed, llm, k, threshold and self.chunks = []. 2) add appends {text, source, vector}. 3) retrieve: q = embed(question); pairs (score, chunk); filter by threshold; sort by score reverse=True; take [:k]. 4) ask: if not kept return the declined dict; build \"Sources:\\n...\\n\\nQuestion: ...\"; reply = llm(prompt); loop over re.findall citations, keep in-range ones, append kept[n - 1][\"source\"] if not already listed.",
        ],
    },
]
