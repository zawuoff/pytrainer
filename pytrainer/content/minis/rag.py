"""Chapter projects for the RAG module: vectors, chunking, retrieval, rag-answers."""

MINIS = [
    # ------------------------------------------------------------------ vectors
    {
        "id": "mini-vectors",
        "chapter": "vectors",
        "title": "Which Movie Is This?",
        "estimated_hours": 0.75,
        "main": "app.py",
        "files": ["app.py"],
        "brief": r'''
            Every movie gets a tiny "plot vector": how much action, romance, space, comedy and
            scare it has. You describe a movie in a few words ("space, very scary") and your
            program guesses which one you mean, then recommends what to watch next - the same
            nearest-neighbour idea that powers embedding search, just with 5 numbers you can read.

            ## What to build

            A file `app.py` with:

            - `FEATURES`: the list `["action", "romance", "space", "comedy", "scary"]` (this order
              is the order of the numbers in every movie vector).
            - `cosine(a, b)`: cosine similarity of two lists of numbers. **Returns** a `float`.
            - `clue_vector(clue)`: `clue` is a dict like `{"space": 1, "scary": 0.5}`.
              **Returns** a list of 5 numbers in `FEATURES` order.
            - `guess(clue, movies, k=3)`: `clue` is a clue dict, `movies` is a dict of
              title -> vector (list of 5 numbers). **Returns** a list of at most `k`
              `(title, score)` tuples, best match first.
            - `recommend(liked, movies, k=2)`: `liked` is a list of titles.
              **Returns** a list of at most `k` titles (strings) to watch next.
            - `report(clue, movies, k=3)`: **Returns** the `guess` results as a printable
              multi-line string (format below).

            ## Rules

            - `cosine`: if the lists have different lengths, raise `ValueError`. If either vector
              is all zeros, return `0.0` (don't divide by zero).
            - `clue_vector`: features missing from the clue are `0`. A key that isn't in
              `FEATURES` raises `ValueError`. Don't change the clue dict.
            - `guess`: the score is the cosine similarity between the clue vector and the movie
              vector, **rounded to 3 decimals**. Sort by that rounded score, highest first; equal
              scores are in alphabetical title order. If `k` is bigger than the number of movies,
              return them all; if `k` is `0` or negative, return `[]`.
            - `recommend`: raise `ValueError` if `liked` is empty or contains a title that isn't
              in `movies`. Build a "taste vector" by averaging the liked movies' vectors position
              by position (*mean pooling*). Rank every movie **not** in `liked` by cosine
              similarity to the taste vector (not rounded), highest first, ties in alphabetical
              order, and return the top `k` titles.
            - `report`: one line per result, lines joined with `"\n"` (no newline at the end).
              Each line is: the rank (starting at 1), `". "`, the title **padded on the right
              with dots to exactly 24 characters**, one space, then the score as a whole-number
              percentage **right-aligned in 4 characters** (e.g. `" 91%"`).
            - `report`: if there are no results, return `"No match found."`.

            ## Examples

            ```python
            MOVIES = {
                "Interstellar": [0.3, 0.4, 1.0, 0.1, 0.1],
                "Alien": [0.6, 0.0, 0.9, 0.0, 1.0],
                "The Notebook": [0.0, 1.0, 0.0, 0.2, 0.0],
                "Mad Max: Fury Road": [1.0, 0.1, 0.0, 0.1, 0.2],
                "Shaun of the Dead": [0.4, 0.2, 0.0, 1.0, 0.7],
                "WALL-E": [0.2, 0.6, 0.8, 0.6, 0.0],
            }
            cosine([3, 4], [6, 8])                 # 1.0
            cosine([0, 0], [1, 1])                 # 0.0
            cosine([1, 2], [1, 2, 3])              # raises ValueError
            clue_vector({"space": 1, "scary": 0.5})   # [0, 0, 1, 0, 0.5]
            clue_vector({"musical": 1})            # raises ValueError
            guess({"space": 1, "scary": 1}, MOVIES)
            # [("Alien", 0.912), ("Interstellar", 0.69), ("WALL-E", 0.478)]
            guess({"space": 1}, MOVIES, k=0)       # []
            recommend(["Alien"], MOVIES)           # ["Interstellar", "Mad Max: Fury Road"]
            recommend(["The Notebook", "Interstellar"], MOVIES, k=3)
            # ["WALL-E", "Alien", "Shaun of the Dead"]
            recommend(["Titanic"], MOVIES)         # raises ValueError
            print(report({"space": 1, "scary": 1}, MOVIES))
            ```
            prints:
            ```text
            1. Alien...................  91%
            2. Interstellar............  69%
            3. WALL-E..................  48%
            ```

            ## You'll need to find out

            - How to pad a value to a fixed width inside an f-string using a **fill character
              other than a space** (here: dots). You already know how to align in a width;
              look up how the format spec lets you choose the padding character.

            ## Try it yourself

            Paste the `MOVIES` dict above into `app.py`, add
            `print(report({"space": 1, "scary": 1}, MOVIES))` under
            `if __name__ == "__main__":` and run `python3 app.py`. Then invent your own movies.
        ''',
        "explore": r'''
            - Add a `why(title, clue, movies)` that names the feature contributing most to the
              match (the biggest `clue[i] * movie[i]`).
            - Turn a free-text clue ("a funny zombie movie") into a clue dict with a small
              keyword -> feature table.
            - Compare cosine ranking with Euclidean distance (`math.dist`) - do they ever disagree?
        ''',
        "rubric": [
            "cosine guards both the length mismatch and the zero-vector case",
            "guess and recommend reuse cosine instead of repeating the math",
            "Mean pooling is written clearly (position by position), without modifying the input vectors",
            "report builds lines with f-string format specs rather than manual space/dot counting",
        ],
        "starter_files": {"app.py": r'''
            # Which Movie Is This? - see the brief for the exact rules.

            FEATURES = ["action", "romance", "space", "comedy", "scary"]


            def cosine(a, b):
                ...


            def clue_vector(clue):
                ...


            def guess(clue, movies, k=3):
                ...


            def recommend(liked, movies, k=2):
                ...


            def report(clue, movies, k=3):
                ...
        '''},
        "solution_files": {"app.py": r'''
            import math

            FEATURES = ["action", "romance", "space", "comedy", "scary"]


            def cosine(a, b):
                if len(a) != len(b):
                    raise ValueError("vectors must have the same length")
                dot = sum(x * y for x, y in zip(a, b))
                norm_a = math.sqrt(sum(x * x for x in a))
                norm_b = math.sqrt(sum(x * x for x in b))
                if norm_a == 0 or norm_b == 0:
                    return 0.0
                return dot / (norm_a * norm_b)


            def clue_vector(clue):
                for name in clue:
                    if name not in FEATURES:
                        raise ValueError(f"unknown feature: {name}")
                return [clue.get(name, 0) for name in FEATURES]


            def guess(clue, movies, k=3):
                if k <= 0:
                    return []
                target = clue_vector(clue)
                scored = [(title, round(cosine(target, vec), 3)) for title, vec in movies.items()]
                scored.sort(key=lambda pair: (-pair[1], pair[0]))
                return scored[:k]


            def recommend(liked, movies, k=2):
                if not liked:
                    raise ValueError("like at least one movie")
                for title in liked:
                    if title not in movies:
                        raise ValueError(f"unknown movie: {title}")
                vectors = [movies[title] for title in liked]
                taste = [sum(column) / len(vectors) for column in zip(*vectors)]
                scored = [(title, cosine(taste, vec)) for title, vec in movies.items()
                          if title not in liked]
                scored.sort(key=lambda pair: (-pair[1], pair[0]))
                return [title for title, _ in scored[:k]]


            def report(clue, movies, k=3):
                results = guess(clue, movies, k)
                if not results:
                    return "No match found."
                lines = [f"{rank}. {title:.<24} {score:>4.0%}"
                         for rank, (title, score) in enumerate(results, start=1)]
                return "\n".join(lines)


            if __name__ == "__main__":
                MOVIES = {
                    "Interstellar": [0.3, 0.4, 1.0, 0.1, 0.1],
                    "Alien": [0.6, 0.0, 0.9, 0.0, 1.0],
                    "The Notebook": [0.0, 1.0, 0.0, 0.2, 0.0],
                    "Mad Max: Fury Road": [1.0, 0.1, 0.0, 0.1, 0.2],
                    "Shaun of the Dead": [0.4, 0.2, 0.0, 1.0, 0.7],
                    "WALL-E": [0.2, 0.6, 0.8, 0.6, 0.0],
                }
                print(report({"space": 1, "scary": 1}, MOVIES))
        '''},
        "tests": r'''
            import math
            from app import FEATURES, cosine, clue_vector, guess, recommend, report

            def movies():
                return {
                    "Interstellar": [0.3, 0.4, 1.0, 0.1, 0.1],
                    "Alien": [0.6, 0.0, 0.9, 0.0, 1.0],
                    "The Notebook": [0.0, 1.0, 0.0, 0.2, 0.0],
                    "Mad Max: Fury Road": [1.0, 0.1, 0.0, 0.1, 0.2],
                    "Shaun of the Dead": [0.4, 0.2, 0.0, 1.0, 0.7],
                    "WALL-E": [0.2, 0.6, 0.8, 0.6, 0.0],
                }

            def raises_value_error(fn, *args):
                try:
                    fn(*args)
                except ValueError:
                    return True
                return False

            def test_features_list_is_in_the_given_order():
                assert FEATURES == ["action", "romance", "space", "comedy", "scary"], f"got {FEATURES!r}"

            def test_cosine_of_parallel_and_perpendicular_vectors():
                assert math.isclose(cosine([3, 4], [6, 8]), 1.0), f"got {cosine([3, 4], [6, 8])!r}"
                assert math.isclose(cosine([1, 0], [0, 1]), 0.0, abs_tol=1e-12)
                assert math.isclose(cosine([1, 2], [2, 1]), 0.8), f"got {cosine([1, 2], [2, 1])!r}"

            def test_cosine_zero_vector_is_zero_and_length_mismatch_raises():
                assert cosine([0, 0], [1, 1]) == 0.0, f"got {cosine([0, 0], [1, 1])!r}"
                assert cosine([1, 1], [0, 0]) == 0.0
                assert raises_value_error(cosine, [1, 2], [1, 2, 3]), "expected ValueError for different lengths"

            def test_clue_vector_fills_missing_features_with_zero():
                clue = {"space": 1, "scary": 0.5}
                got = clue_vector(clue)
                assert got == [0, 0, 1, 0, 0.5], f"got {got!r}"
                assert clue == {"space": 1, "scary": 0.5}, "the clue dict was modified"
                assert clue_vector({}) == [0, 0, 0, 0, 0]

            def test_clue_vector_unknown_feature_raises_value_error():
                assert raises_value_error(clue_vector, {"musical": 1}), "expected ValueError for 'musical'"

            def test_guess_returns_top_three_rounded_scores():
                got = guess({"space": 1, "scary": 1}, movies())
                want = [("Alien", 0.912), ("Interstellar", 0.69), ("WALL-E", 0.478)]
                assert got == want, f"got {got!r}"

            def test_guess_respects_k_including_zero_and_too_big():
                got = guess({"space": 1, "romance": 1}, movies(), k=2)
                assert got == [("Interstellar", 0.878), ("WALL-E", 0.837)], f"got {got!r}"
                assert guess({"space": 1}, movies(), k=0) == []
                assert len(guess({"comedy": 1}, movies(), k=10)) == 6

            def test_guess_breaks_ties_alphabetically():
                films = {"Zeta": [1, 0, 0, 0, 0], "Beta": [2, 0, 0, 0, 0], "Alpha": [0, 1, 0, 0, 0]}
                got = guess({"action": 1}, films)
                assert got == [("Beta", 1.0), ("Zeta", 1.0), ("Alpha", 0.0)], f"got {got!r}"

            def test_recommend_uses_the_single_liked_movie():
                got = recommend(["Alien"], movies())
                assert got == ["Interstellar", "Mad Max: Fury Road"], f"got {got!r}"

            def test_recommend_averages_several_liked_movies():
                got = recommend(["The Notebook", "Interstellar"], movies(), k=3)
                assert got == ["WALL-E", "Alien", "Shaun of the Dead"], f"got {got!r}"

            def test_recommend_never_returns_a_liked_movie_and_keeps_input():
                films = movies()
                liked = ["Alien", "WALL-E"]
                got = recommend(liked, films, k=10)
                assert len(got) == 4 and "Alien" not in got and "WALL-E" not in got, f"got {got!r}"
                assert liked == ["Alien", "WALL-E"] and films == movies(), "inputs were modified"

            def test_recommend_empty_or_unknown_raises_value_error():
                assert raises_value_error(recommend, [], movies()), "expected ValueError for []"
                assert raises_value_error(recommend, ["Titanic"], movies()), "expected ValueError for 'Titanic'"

            def test_report_pads_titles_with_dots_and_aligns_percent():
                got = report({"space": 1, "scary": 1}, movies())
                want = ("1. Alien...................  91%\n"
                        "2. Interstellar............  69%\n"
                        "3. WALL-E..................  48%")
                assert got == want, f"got:\n{got}\nwant:\n{want}"

            def test_report_full_score_and_no_results():
                got = report({"action": 1}, {"Rambo": [1, 0, 0, 0, 0]}, k=1)
                assert got == "1. Rambo................... 100%", f"got {got!r}"
                assert report({"space": 1}, movies(), k=0) == "No match found."
                assert report({"space": 1}, {}) == "No match found."
        ''',
    },
    # ----------------------------------------------------------------- chunking
    {
        "id": "mini-chunking",
        "chapter": "chunking",
        "title": "Book Shredder",
        "estimated_hours": 0.75,
        "main": "app.py",
        "files": ["app.py"],
        "brief": r'''
            You want to chat with a novel, so first it has to be cut into chunks a retriever
            can find. A chunk that says "she walked to the café" is much more useful when it
            also knows it came from "Chapter 2: The Café". Build a book shredder that splits a
            book at its chapter headings, chunks each chapter by words with overlap, labels every
            chunk, and saves them as a JSON Lines file ready for embedding.

            ## What to build

            A file `app.py` with:

            - `split_chapters(text)`: **Returns** a list of `(title, body)` tuples, in book order.
            - `chunk_words(text, max_words, overlap=0)`: **Returns** a list of chunk strings.
            - `chunk_book(text, book_id, max_words=40, overlap=5)`: **Returns** a list of chunk
              dicts `{"id": str, "chapter": str, "part": int, "text": str, "word_count": int}`.
            - `save_jsonl(chunks, path)`: writes the chunks to the file `path`.
              **Returns** the number of lines written (`int`).

            ## Rules

            `split_chapters`
            - A chapter heading is a line that **starts with `"# "`** (hash + space). The title
              is the rest of that line, stripped. Lines like `"## Notes"` or `"#hashtag"` are
              ordinary text.
            - A chapter's body is all the lines after its heading up to the next heading, joined
              with `"\n"`, then stripped.
            - Text before the first heading becomes a chapter titled `"Front matter"`, but only
              if it isn't empty after stripping.
            - A chapter with an empty body is still returned (body `""`). Empty text returns `[]`.

            `chunk_words`
            - Split `text` into words with `.split()`; a chunk is at most `max_words` words
              joined by single spaces.
            - Each chunk starts `max_words - overlap` words after the previous one (so the last
              `overlap` words of a chunk start the next one).
            - Stop after the chunk that contains the last word (no extra tail chunk made only
              of overlap). Text with no words returns `[]`.
            - Raise `ValueError` if `max_words < 1`, `overlap < 0`, or `overlap >= max_words`.

            `chunk_book`
            - Chunks never cross chapters: chunk each chapter body separately with `chunk_words`.
            - `"id"` is `f"{book_id}-{n}"` where `n` counts chunks across the **whole book**
              starting at `0`. `"part"` counts chunks **within the chapter** starting at `1`.
            - `"chapter"` is the chapter title; `"word_count"` is the number of words in `"text"`.
            - Chapters with an empty body produce no chunks. Bad `max_words`/`overlap` raise
              `ValueError` (same rules as `chunk_words`).

            `save_jsonl`
            - One chunk per line: the chunk dict as JSON, followed by `"\n"`.
            - Write the file as UTF-8, and write non-ASCII characters **as they are**
              (the file must contain `café`, not `café`).
            - An empty list writes an empty file and returns `0`.

            ## Examples

            ```python
            BOOK = """The Lighthouse Keeper, a very short novel.

            # Chapter 1: The Storm
            Rain hit the glass all night. Mara climbed the stairs
            with a lamp and a flask of coffee.

            # Chapter 2: The Café
            In the morning she walked to the café by the harbour.
            Nobody believed her story about the ship.

            # Chapter 3: Silence
            """
            split_chapters(BOOK)
            # [("Front matter", "The Lighthouse Keeper, a very short novel."),
            #  ("Chapter 1: The Storm", "Rain hit the glass all night. Mara climbed the stairs\nwith a lamp and a flask of coffee."),
            #  ("Chapter 2: The Café", "In the morning she walked to the café by the harbour.\nNobody believed her story about the ship."),
            #  ("Chapter 3: Silence", "")]
            chunk_words("a b c d e f g", 3, 1)     # ["a b c", "c d e", "e f g"]
            chunk_words("a b c d e", 3, 1)         # ["a b c", "c d e"]
            chunk_words("", 5)                     # []
            chunk_words("a b", 3, 3)               # raises ValueError
            chunk_book(BOOK, "keeper", max_words=8, overlap=2)[:3]
            # [{"id": "keeper-0", "chapter": "Front matter", "part": 1,
            #   "text": "The Lighthouse Keeper, a very short novel.", "word_count": 7},
            #  {"id": "keeper-1", "chapter": "Chapter 1: The Storm", "part": 1,
            #   "text": "Rain hit the glass all night. Mara climbed", "word_count": 8},
            #  {"id": "keeper-2", "chapter": "Chapter 1: The Storm", "part": 2,
            #   "text": "Mara climbed the stairs with a lamp and", "word_count": 8}]
            # ...7 chunks in total; Chapter 3 gives none.
            save_jsonl(chunk_book(BOOK, "keeper", 8, 2), "keeper.jsonl")   # returns 7
            ```

            ## You'll need to find out

            - How to make the standard `json` module write characters like `é` or `’` as
              they are, instead of turning them into `\u....` escape codes.

            ## Try it yourself

            Paste `BOOK` into `app.py` and, under `if __name__ == "__main__":`, print each chunk
            of `chunk_book(BOOK, "keeper", max_words=8, overlap=2)`. Then call `save_jsonl` and
            open the `.jsonl` file in your editor.
        ''',
        "explore": r'''
            - Read a real public-domain book from a `.txt` file (Project Gutenberg) and detect
              its `CHAPTER I.` headings with a regex instead of `"# "`.
            - Add `"start"`/`"end"` character offsets so each chunk can be highlighted in the book.
            - Add a `for_embedding(chunk, book_title)` that prefixes `"Book > Chapter"` to the text
              (contextual retrieval) and compare search results with and without it.
        ''',
        "rubric": [
            "split_chapters, chunk_words and chunk_book each do one job and chunk_book reuses the other two",
            "The overlap/step logic is easy to follow and validates bad sizes up front",
            "Files are opened with a with-block and an explicit UTF-8 encoding",
            "Names (title, body, part, step) make the chunk metadata self-explanatory",
        ],
        "starter_files": {"app.py": r'''
            # Book Shredder - see the brief for the exact rules.
            import json


            def split_chapters(text):
                ...


            def chunk_words(text, max_words, overlap=0):
                ...


            def chunk_book(text, book_id, max_words=40, overlap=5):
                ...


            def save_jsonl(chunks, path):
                ...
        '''},
        "solution_files": {"app.py": r'''
            import json


            def split_chapters(text):
                chapters = []
                title = None
                body_lines = []

                def close():
                    body = "\n".join(body_lines).strip()
                    if title is not None:
                        chapters.append((title, body))
                    elif body:
                        chapters.append(("Front matter", body))

                for line in text.splitlines():
                    if line.startswith("# "):
                        close()
                        title = line[2:].strip()
                        body_lines = []
                    else:
                        body_lines.append(line)
                close()
                return chapters


            def chunk_words(text, max_words, overlap=0):
                if max_words < 1:
                    raise ValueError("max_words must be at least 1")
                if overlap < 0 or overlap >= max_words:
                    raise ValueError("overlap must be 0 or more and smaller than max_words")
                words = text.split()
                step = max_words - overlap
                chunks = []
                for start in range(0, len(words), step):
                    chunks.append(" ".join(words[start:start + max_words]))
                    if start + max_words >= len(words):
                        break
                return chunks


            def chunk_book(text, book_id, max_words=40, overlap=5):
                chunks = []
                for title, body in split_chapters(text):
                    for part, piece in enumerate(chunk_words(body, max_words, overlap), start=1):
                        chunks.append({
                            "id": f"{book_id}-{len(chunks)}",
                            "chapter": title,
                            "part": part,
                            "text": piece,
                            "word_count": len(piece.split()),
                        })
                return chunks


            def save_jsonl(chunks, path):
                with open(path, "w", encoding="utf-8") as fh:
                    for chunk in chunks:
                        fh.write(json.dumps(chunk, ensure_ascii=False) + "\n")
                return len(chunks)


            if __name__ == "__main__":
                BOOK = "Intro line.\n\n# Chapter 1: The Storm\nRain hit the glass all night.\n"
                for chunk in chunk_book(BOOK, "keeper", max_words=4, overlap=1):
                    print(chunk)
        '''},
        "tests": r'''
            import json
            from app import split_chapters, chunk_words, chunk_book, save_jsonl

            BOOK = """The Lighthouse Keeper, a very short novel.

            # Chapter 1: The Storm
            Rain hit the glass all night. Mara climbed the stairs
            with a lamp and a flask of coffee.

            # Chapter 2: The Café
            In the morning she walked to the café by the harbour.
            Nobody believed her story about the ship.

            # Chapter 3: Silence
            """
            BOOK = "\n".join(line.strip() for line in BOOK.splitlines()) + "\n"

            def raises_value_error(fn, *args):
                try:
                    fn(*args)
                except ValueError:
                    return True
                return False

            def test_split_chapters_finds_titles_bodies_and_front_matter():
                got = split_chapters(BOOK)
                want = [
                    ("Front matter", "The Lighthouse Keeper, a very short novel."),
                    ("Chapter 1: The Storm", "Rain hit the glass all night. Mara climbed the stairs\nwith a lamp and a flask of coffee."),
                    ("Chapter 2: The Café", "In the morning she walked to the café by the harbour.\nNobody believed her story about the ship."),
                    ("Chapter 3: Silence", ""),
                ]
                assert got == want, f"got {got!r}"

            def test_split_chapters_skips_empty_front_matter_and_ignores_subheadings():
                got = split_chapters("\n\n#  Intro  \n## Notes\n#hashtag here\n")
                assert got == [("Intro", "## Notes\n#hashtag here")], f"got {got!r}"
                assert split_chapters("") == [], f"got {split_chapters('')!r}"
                assert split_chapters("Just a note.") == [("Front matter", "Just a note.")]

            def test_chunk_words_without_overlap():
                got = chunk_words("one two three four five", 2)
                assert got == ["one two", "three four", "five"], f"got {got!r}"
                assert chunk_words("a b c", 5) == ["a b c"]

            def test_chunk_words_with_overlap_has_no_extra_tail():
                assert chunk_words("a b c d e f g", 3, 1) == ["a b c", "c d e", "e f g"], f"got {chunk_words('a b c d e f g', 3, 1)!r}"
                assert chunk_words("a b c d e", 3, 1) == ["a b c", "c d e"], f"got {chunk_words('a b c d e', 3, 1)!r}"

            def test_chunk_words_empty_text_gives_empty_list():
                assert chunk_words("", 5) == []
                assert chunk_words("  \n ", 5, 2) == []

            def test_chunk_words_bad_sizes_raise_value_error():
                assert raises_value_error(chunk_words, "a b", 3, 3), "overlap == max_words should raise"
                assert raises_value_error(chunk_words, "a b", 0), "max_words 0 should raise"
                assert raises_value_error(chunk_words, "a b", 3, -1), "negative overlap should raise"

            def test_chunk_book_labels_every_chunk():
                chunks = chunk_book(BOOK, "keeper", max_words=8, overlap=2)
                assert len(chunks) == 7, f"expected 7 chunks, got {len(chunks)}: {chunks!r}"
                assert chunks[0] == {"id": "keeper-0", "chapter": "Front matter", "part": 1,
                                     "text": "The Lighthouse Keeper, a very short novel.", "word_count": 7}, f"got {chunks[0]!r}"
                assert chunks[2] == {"id": "keeper-2", "chapter": "Chapter 1: The Storm", "part": 2,
                                     "text": "Mara climbed the stairs with a lamp and", "word_count": 8}, f"got {chunks[2]!r}"

            def test_chunk_book_ids_count_whole_book_and_parts_restart_per_chapter():
                chunks = chunk_book(BOOK, "keeper", max_words=8, overlap=2)
                assert [c["id"] for c in chunks] == [f"keeper-{n}" for n in range(7)], f"got {[c['id'] for c in chunks]!r}"
                assert [c["part"] for c in chunks] == [1, 1, 2, 3, 1, 2, 3], f"got {[c['part'] for c in chunks]!r}"

            def test_chunk_book_never_crosses_chapters_and_skips_empty_ones():
                chunks = chunk_book(BOOK, "keeper", max_words=8, overlap=2)
                cafe = [c for c in chunks if c["chapter"] == "Chapter 2: The Café"]
                assert cafe[0]["text"] == "In the morning she walked to the café", f"got {cafe[0]!r}"
                assert cafe[-1]["text"] == "believed her story about the ship.", f"got {cafe[-1]!r}"
                assert all(c["chapter"] != "Chapter 3: Silence" for c in chunks), "an empty chapter produced a chunk"
                assert chunk_book("", "x") == []

            def test_chunk_book_bad_sizes_raise_value_error():
                assert raises_value_error(chunk_book, BOOK, "keeper", 5, 5), "overlap == max_words should raise"

            def test_save_jsonl_writes_one_json_object_per_line():
                chunks = chunk_book(BOOK, "keeper", max_words=8, overlap=2)
                count = save_jsonl(chunks, "keeper.jsonl")
                assert count == 7, f"returned {count!r}"
                with open("keeper.jsonl", encoding="utf-8") as fh:
                    raw = fh.read()
                assert raw.endswith("\n"), "every line (including the last) should end with a newline"
                lines = raw.splitlines()
                assert len(lines) == 7, f"expected 7 lines, got {len(lines)}"
                assert [json.loads(line) for line in lines] == chunks, "the lines don't load back to the same chunks"

            def test_save_jsonl_keeps_accents_as_real_characters():
                save_jsonl([{"id": "c-0", "text": "the café’s menu"}], "cafe.jsonl")
                with open("cafe.jsonl", encoding="utf-8") as fh:
                    raw = fh.read()
                assert "café’s" in raw, f"file contains {raw!r} - write non-ASCII characters as they are"
                assert "\\u00e9" not in raw

            def test_save_jsonl_empty_list_writes_empty_file():
                assert save_jsonl([], "empty.jsonl") == 0
                with open("empty.jsonl", encoding="utf-8") as fh:
                    assert fh.read() == ""
        ''',
    },
    # ---------------------------------------------------------------- retrieval
    {
        "id": "mini-retrieval",
        "chapter": "retrieval",
        "title": "HelpDesk Hound",
        "estimated_hours": 1.0,
        "main": "app.py",
        "files": ["app.py"],
        "brief": r'''
            Customers never phrase questions like your FAQ does. "I want my money back" shares
            no words with "How do I get a refund?", and "CAFÉ" isn't "cafe" to a naive
            computer. Build a FAQ search bot that sniffs out the right answer with **hybrid
            scoring**: exact keyword matches plus meaning from an (injected, fake) embedding
            model - and admits when it has no idea.

            ## What to build

            A file `app.py` with (keep the `STOPWORDS` and `FALLBACK` constants from the starter):

            - `fold(text)`: **Returns** `text` lowercased with accents removed (`"Café"` -> `"cafe"`).
            - `tokenize(text)`: **Returns** a list of words (strings).
            - `keyword_score(query, text)`: **Returns** a `float` from `0.0` to `1.0`.
            - `cosine(a, b)`: cosine similarity of two equal-length lists of numbers (`float`).
            - A class `FaqBot`:
              - `FaqBot(faqs, embed, alpha=0.5, min_score=0.25)`: `faqs` is a list of dicts
                `{"id": str, "question": str, "answer": str, "tags": [str, ...]}`;
                `embed(text)` is a function returning a list of numbers.
              - `.search(query, k=3, tag=None)`: **Returns** a list of at most `k` dicts
                `{"id": ..., "question": ..., "score": float}`, best first.
              - `.ask(query, tag=None)`: **Returns** the best FAQ's `"answer"` string, or `FALLBACK`.

            ## Rules

            - `fold`: lowercase, and turn accented letters into their plain letters
              (`"Crème Brûlée"` -> `"creme brulee"`).
            - `tokenize`: fold the text, take every run of letters `a-z` and digits `0-9` as a word
              (in order, duplicates kept), and drop words that are in `STOPWORDS`.
            - `keyword_score`: the fraction of the query's **distinct** tokens that also appear
              among the text's tokens. If the query has no tokens, return `0.0`.
            - `cosine`: return `0.0` if either vector is all zeros.
            - A FAQ's **text** is `question + " " + answer`. Both the keyword score and the
              embedding use this text.
            - `FaqBot(...)` raises `ValueError` if `alpha` is below `0` or above `1`.
            - `FaqBot(...)` calls `embed` exactly **once per FAQ** (on its text), in the
              constructor. Each `.search()` calls `embed` exactly **once** (on the query).
            - A FAQ's hybrid score is `alpha * cosine(query vector, FAQ vector) + (1 - alpha) *
              keyword_score(query, FAQ text)`, **rounded to 3 decimals**.
            - `search`: with a `tag`, only FAQs whose `"tags"` list contains it are scored
              (filter **before** ranking). Leave out results whose score is `0`. Sort by score,
              highest first; equal scores keep the order of the `faqs` list.
            - `ask`: takes the top result of `search(query, k=1, tag=tag)`. If there is none, or
              its score is below `min_score`, return `FALLBACK`; otherwise return that FAQ's answer.

            ## Examples

            ```python
            FAQS = [
                {"id": "refunds", "question": "How do I get a refund?",
                 "answer": "Refunds go back to your card within 5 days.", "tags": ["billing"]},
                {"id": "shipping", "question": "How long does delivery take?",
                 "answer": "Parcels arrive in 2-4 working days.", "tags": ["orders"]},
                {"id": "password", "question": "I forgot my password",
                 "answer": "Use the 'Forgot password' link on the login page.", "tags": ["account"]},
                {"id": "cafe", "question": "Is there a café at the store?",
                 "answer": "Yes! The café on floor 2 serves coffee until 6pm.", "tags": ["store"]},
            ]
            CONCEPTS = [{"refund", "refunds", "money", "back", "card"},
                        {"delivery", "shipping", "parcel", "parcels", "arrive"},
                        {"password", "login", "account"},
                        {"cafe", "coffee", "drink"}]

            def fake_embed(text):     # counts words per "concept" - a toy embedding
                words = tokenize(text)
                return [sum(1 for w in words if w in concept) for concept in CONCEPTS]

            fold("Café Crème")                              # "cafe creme"
            tokenize("How do I reset my Café PASSWORD?")    # ["reset", "cafe", "password"]
            keyword_score("refund card please", "Refunds go to your card")   # 0.333... (1 of 3)
            keyword_score("the a", "anything")              # 0.0

            bot = FaqBot(FAQS, fake_embed)
            bot.search("I want my money back")
            # [{"id": "refunds", "question": "How do I get a refund?", "score": 0.667}]
            bot.search("How long for my parcel?")
            # [{"id": "shipping", "question": "How long does delivery take?", "score": 0.75}]
            bot.search("refund", tag="orders")              # []
            bot.ask("Where can I get a CAFÉ latte?")        # "Yes! The café on floor 2 serves coffee until 6pm."
            bot.ask("tell me a joke")                       # FALLBACK
            FaqBot(FAQS, fake_embed, alpha=1.5)             # raises ValueError
            ```

            ## You'll need to find out

            - How to remove accents from letters (turn `é` into `e`) using the standard
              library's **Unicode tools**: look for how a character can be *decomposed* into a
              base letter plus a separate accent mark, and how to recognise (and drop) those marks.

            ## Try it yourself

            Put `FAQS`, `CONCEPTS` and `fake_embed` from the examples into `app.py` and, under
            `if __name__ == "__main__":`, print `bot.search(...)` and `bot.ask(...)` for a few
            questions of your own. Try `alpha=0.0` (keywords only) and `alpha=1.0` (meaning only).
        ''',
        "explore": r'''
            - Replace the keyword score with TF-IDF so rare words ("password") count more than common ones.
            - Combine the two rankings with reciprocal rank fusion instead of a weighted sum.
            - Add a tiny stemmer (strip a trailing `"s"`) and see whether "refunds" now matches "refund".
        ''',
        "rubric": [
            "Embeddings of the FAQs are computed once and cached, not recomputed on every search",
            "Tag filtering happens before scoring, and ties rely on a stable sort",
            "tokenize/keyword_score/cosine are small reusable functions the class builds on",
            "ask reuses search instead of duplicating the scoring logic",
        ],
        "starter_files": {"app.py": r'''
            # HelpDesk Hound - see the brief for the exact rules.
            import math
            import re

            STOPWORDS = {"a", "an", "the", "is", "are", "do", "does", "i", "my", "me", "to",
                         "how", "what", "can", "you", "of", "for", "in", "on", "it"}

            FALLBACK = "Sorry, I don't know that one yet. Try asking a human at help@example.com."


            def fold(text):
                ...


            def tokenize(text):
                ...


            def keyword_score(query, text):
                ...


            def cosine(a, b):
                ...


            class FaqBot:
                def __init__(self, faqs, embed, alpha=0.5, min_score=0.25):
                    ...

                def search(self, query, k=3, tag=None):
                    ...

                def ask(self, query, tag=None):
                    ...
        '''},
        "solution_files": {"app.py": r'''
            import math
            import re
            import unicodedata

            STOPWORDS = {"a", "an", "the", "is", "are", "do", "does", "i", "my", "me", "to",
                         "how", "what", "can", "you", "of", "for", "in", "on", "it"}

            FALLBACK = "Sorry, I don't know that one yet. Try asking a human at help@example.com."


            def fold(text):
                decomposed = unicodedata.normalize("NFKD", text.lower())
                return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


            def tokenize(text):
                return [word for word in re.findall(r"[a-z0-9]+", fold(text)) if word not in STOPWORDS]


            def keyword_score(query, text):
                wanted = set(tokenize(query))
                if not wanted:
                    return 0.0
                return len(wanted & set(tokenize(text))) / len(wanted)


            def cosine(a, b):
                dot = sum(x * y for x, y in zip(a, b))
                norm_a = math.sqrt(sum(x * x for x in a))
                norm_b = math.sqrt(sum(x * x for x in b))
                if norm_a == 0 or norm_b == 0:
                    return 0.0
                return dot / (norm_a * norm_b)


            class FaqBot:
                def __init__(self, faqs, embed, alpha=0.5, min_score=0.25):
                    if not 0 <= alpha <= 1:
                        raise ValueError("alpha must be between 0 and 1")
                    self.faqs = faqs
                    self.embed = embed
                    self.alpha = alpha
                    self.min_score = min_score
                    self.texts = [faq["question"] + " " + faq["answer"] for faq in faqs]
                    self.vectors = [embed(text) for text in self.texts]

                def search(self, query, k=3, tag=None):
                    query_vector = self.embed(query)
                    results = []
                    for faq, text, vector in zip(self.faqs, self.texts, self.vectors):
                        if tag is not None and tag not in faq["tags"]:
                            continue
                        score = (self.alpha * cosine(query_vector, vector)
                                 + (1 - self.alpha) * keyword_score(query, text))
                        score = round(score, 3)
                        if score > 0:
                            results.append({"id": faq["id"], "question": faq["question"], "score": score})
                    results.sort(key=lambda r: r["score"], reverse=True)
                    return results[:k]

                def ask(self, query, tag=None):
                    results = self.search(query, k=1, tag=tag)
                    if not results or results[0]["score"] < self.min_score:
                        return FALLBACK
                    for faq in self.faqs:
                        if faq["id"] == results[0]["id"]:
                            return faq["answer"]
                    return FALLBACK


            if __name__ == "__main__":
                faqs = [{"id": "cafe", "question": "Is there a café?", "answer": "Yes, floor 2.", "tags": []}]
                bot = FaqBot(faqs, lambda text: [len(text)])
                print(bot.search("cafe"), bot.ask("cafe"))
        '''},
        "tests": r'''
            import math
            from app import fold, tokenize, keyword_score, cosine, FaqBot, FALLBACK

            FAQS = [
                {"id": "refunds", "question": "How do I get a refund?",
                 "answer": "Refunds go back to your card within 5 days.", "tags": ["billing"]},
                {"id": "shipping", "question": "How long does delivery take?",
                 "answer": "Parcels arrive in 2-4 working days.", "tags": ["orders"]},
                {"id": "password", "question": "I forgot my password",
                 "answer": "Use the 'Forgot password' link on the login page.", "tags": ["account"]},
                {"id": "cafe", "question": "Is there a café at the store?",
                 "answer": "Yes! The café on floor 2 serves coffee until 6pm.", "tags": ["store"]},
            ]
            CONCEPTS = [{"refund", "refunds", "money", "back", "card"},
                        {"delivery", "shipping", "parcel", "parcels", "arrive"},
                        {"password", "login", "account"},
                        {"cafe", "coffee", "drink"}]

            def make_embed():
                calls = []
                def fake_embed(text):
                    calls.append(text)
                    words = text.lower().replace("é", "e").split()
                    words = ["".join(ch for ch in w if ch.isalnum()) for w in words]
                    return [sum(1 for w in words if w in concept) for concept in CONCEPTS]
                return fake_embed, calls

            def test_fold_lowercases_and_removes_accents():
                assert fold("Café Crème") == "cafe creme", f"got {fold('Café Crème')!r}"
                assert fold("Crème Brûlée") == "creme brulee", f"got {fold('Crème Brûlée')!r}"
                assert fold("NAÏVE Señor") == "naive senor", f"got {fold('NAÏVE Señor')!r}"

            def test_tokenize_splits_folds_and_drops_stopwords():
                got = tokenize("How do I reset my Café PASSWORD?")
                assert got == ["reset", "cafe", "password"], f"got {got!r}"
                got = tokenize("Error E42: e42 again!")
                assert got == ["error", "e42", "e42", "again"], f"got {got!r}"
                assert tokenize("") == []

            def test_keyword_score_is_fraction_of_distinct_query_words():
                got = keyword_score("refund card please", "Refunds go to your card")
                assert math.isclose(got, 1 / 3), f"got {got!r}"
                got = keyword_score("card card", "your CARD")
                assert math.isclose(got, 1.0), f"got {got!r}"
                assert keyword_score("the a", "anything") == 0.0

            def test_cosine_handles_zero_vectors():
                assert math.isclose(cosine([1, 2], [2, 4]), 1.0)
                assert cosine([0, 0], [1, 2]) == 0.0

            def test_alpha_out_of_range_raises_value_error():
                embed, calls = make_embed()
                for bad in (1.5, -0.1):
                    try:
                        FaqBot(FAQS, embed, alpha=bad)
                    except ValueError:
                        continue
                    assert False, f"expected ValueError for alpha={bad}"

            def test_embeds_each_faq_once_and_each_query_once():
                embed, calls = make_embed()
                bot = FaqBot(FAQS, embed)
                assert len(calls) == 4, f"constructor called embed {len(calls)} times, expected 4"
                assert calls[0] == "How do I get a refund? Refunds go back to your card within 5 days.", f"got {calls[0]!r}"
                bot.search("refund")
                bot.search("parcel", tag="orders")
                assert len(calls) == 6, f"expected 1 embed call per search, total 6 - got {len(calls)}"

            def test_semantic_side_finds_paraphrase_with_no_shared_words():
                embed, calls = make_embed()
                got = FaqBot(FAQS, embed).search("I want my money back")
                assert got == [{"id": "refunds", "question": "How do I get a refund?", "score": 0.667}], f"got {got!r}"

            def test_alpha_controls_the_blend():
                embed, calls = make_embed()
                keyword_only = FaqBot(FAQS, embed, alpha=0.0).search("I want my money back")
                assert keyword_only == [{"id": "refunds", "question": "How do I get a refund?", "score": 0.333}], f"got {keyword_only!r}"
                meaning_only = FaqBot(FAQS, embed, alpha=1.0).search("I want my money back")
                assert meaning_only == [{"id": "refunds", "question": "How do I get a refund?", "score": 1.0}], f"got {meaning_only!r}"

            def test_search_ranks_best_first_and_respects_k():
                embed, calls = make_embed()
                bot = FaqBot(FAQS, embed)
                got = bot.search("Where can I get a CAFÉ latte?")
                assert [r["id"] for r in got] == ["cafe", "refunds"], f"got {got!r}"
                assert got[0]["score"] == 0.625 and got[1]["score"] == 0.125, f"got {got!r}"
                assert len(bot.search("Where can I get a CAFÉ latte?", k=1)) == 1

            def test_equal_scores_keep_faq_order_and_zero_scores_are_dropped():
                embed, calls = make_embed()
                got = FaqBot(FAQS, embed).search("password card", k=5)
                assert [(r["id"], r["score"]) for r in got] == [("refunds", 0.604), ("password", 0.604)], f"got {got!r}"

            def test_tag_filter_runs_before_ranking():
                embed, calls = make_embed()
                bot = FaqBot(FAQS, embed)
                assert bot.search("refund", tag="orders") == [], f"got {bot.search('refund', tag='orders')!r}"
                got = bot.search("refund", tag="billing")
                assert [r["id"] for r in got] == ["refunds"], f"got {got!r}"

            def test_ask_returns_best_answer():
                embed, calls = make_embed()
                bot = FaqBot(FAQS, embed)
                assert bot.ask("How long for my parcel?") == "Parcels arrive in 2-4 working days."
                assert bot.ask("Where can I get a CAFÉ latte?") == "Yes! The café on floor 2 serves coffee until 6pm."

            def test_ask_falls_back_when_nothing_good_enough():
                embed, calls = make_embed()
                bot = FaqBot(FAQS, embed)
                assert bot.ask("tell me a joke") == FALLBACK
                assert bot.ask("refund", tag="store") == FALLBACK
                strict = FaqBot(FAQS, embed, min_score=0.9)
                assert strict.ask("I want my money back") == FALLBACK
        ''',
    },
    # -------------------------------------------------------------- rag-answers
    {
        "id": "mini-rag-answers",
        "chapter": "rag-answers",
        "title": "Ask the Ship's Computer",
        "estimated_hours": 1.25,
        "main": "app.py",
        "files": ["app.py"],
        "brief": r'''
            Your starship has a manual, and the crew wants to ask it questions. The ship's
            computer must answer **only** from the manual, cite the pages it used like `[1]`,
            refuse politely when the manual has nothing on the topic, and never show an answer
            whose citations point at pages that don't exist. The console is an old 40-column
            screen, so replies must be wrapped. The embedding model and the LLM are injected
            functions, so you can test everything with fakes.

            ## What to build

            A file `app.py` with (keep the `DECLINE`, `INSTRUCTIONS` and `FEEDBACK` constants
            from the starter):

            - `cosine(a, b)`: cosine similarity (`float`).
            - `retrieve(question, kb, embed, k=3, threshold=0.3)`: `kb` is a list of dicts
              `{"title": str, "text": str}`. **Returns** a list of dicts
              `{"title": ..., "text": ..., "score": float}`, best first.
            - `build_prompt(question, sources)`: `sources` is a list returned by `retrieve`.
              **Returns** the grounded prompt (`str`).
            - `citations(answer)`: **Returns** the list of cited numbers (`int`s) in `answer`.
            - `ask(question, kb, embed, llm, k=3, threshold=0.3, max_attempts=2)`:
              `llm(prompt) -> str`. **Returns** a dict
              `{"answer": str, "sources": [title, ...], "status": "ok" | "declined" | "unverified"}`.
            - `format_reply(result, width=40)`: `result` is a dict returned by `ask`.
              **Returns** the text to show on the console (`str`).

            ## Rules

            - `cosine`: return `0.0` if either vector is all zeros.
            - `retrieve`: score every kb entry by `cosine(embed(question), embed(entry text))`.
              Keep entries with `score >= threshold`, best first (ties keep `kb` order), at most `k`.
              `"score"` is **not** rounded.
            - `build_prompt` returns exactly: `INSTRUCTIONS`, a blank line, `Sources:`, one line per
              source `[n] (title) text` numbered from 1, a blank line, then `Question: <question>`
              (no newline at the end). See the example.
            - `citations`: every `[number]` in the text, in order, duplicates kept
              (`"[2] and [2][10]"` -> `[2, 2, 10]`).
            - `ask`, step 1: retrieve. If **nothing** passes the threshold, return
              `{"answer": DECLINE, "sources": [], "status": "declined"}` **without calling `llm`**.
            - `ask`, step 2: call `llm` with the grounded prompt. A reply is **good** if it has at
              least one citation and **every** citation is between `1` and the number of sources.
            - `ask`, step 3: if the reply isn't good, call `llm` again with
              `prompt + FEEDBACK.format(n=<number of sources>)` (always the **original** prompt
              plus the feedback once). `llm` is called at most `max_attempts` times in total.
            - A good reply returns `{"answer": reply, "sources": [...], "status": "ok"}` where
              `sources` lists the title of each cited source (`[n]` means `sources[n - 1]`), each
              title once, in the order first cited.
            - If no reply is good after `max_attempts` calls, return
              `{"answer": DECLINE, "sources": [], "status": "unverified"}`.
            - `format_reply`: wrap `result["answer"]` into lines of at most `width` characters,
              breaking only at spaces (lines joined with `"\n"`, no trailing spaces). If
              `result["sources"]` isn't empty, add a blank line and then
              `Sources: ` + the titles joined with `", "` (this line is not wrapped).

            ## Examples

            ```python
            MANUAL = [
                {"title": "engines.md", "text": "The warp engine needs 3 hours to cool down after a jump."},
                {"title": "galley.md", "text": "The galley serves soup at 18:00 ship time. Coffee is always available."},
                {"title": "airlock.md", "text": "Never open the airlock without a suit. The airlock cycles in 90 seconds."},
            ]
            TOPICS = ["engine", "warp", "jump", "soup", "coffee", "galley", "airlock", "suit"]

            def fake_embed(text):          # a toy embedding: counts topic words
                words = re.findall(r"[a-z]+", text.lower())
                return [words.count(t) for t in TOPICS]

            [(s["title"], round(s["score"], 3)) for s in retrieve("airlock suit coffee", MANUAL, fake_embed)]
            # [("airlock.md", 0.775), ("galley.md", 0.333)]
            retrieve("Who won the space race?", MANUAL, fake_embed)      # []

            print(build_prompt("When is soup?", retrieve("When is soup?", MANUAL, fake_embed)))
            ```
            prints:
            ```text
            You are the ship's computer. Answer using only the numbered sources and cite them like [1].
            If the sources don't contain the answer, say "I don't know".

            Sources:
            [1] (galley.md) The galley serves soup at 18:00 ship time. Coffee is always available.

            Question: When is soup?
            ```
            ```python
            citations("Yes [2]. Also [10] and [2][1].")      # [2, 10, 2, 1]

            def fake_llm(prompt):
                return "After a jump the warp engine needs 3 hours to cool down [1]."

            result = ask("How long must the warp engine cool after a jump?", MANUAL, fake_embed, fake_llm)
            # {"answer": "After a jump the warp engine needs 3 hours to cool down [1].",
            #  "sources": ["engines.md"], "status": "ok"}
            print(format_reply(result))
            ```
            prints:
            ```text
            After a jump the warp engine needs 3
            hours to cool down [1].

            Sources: engines.md
            ```
            ```python
            ask("Who won the space race?", MANUAL, fake_embed, fake_llm)
            # {"answer": DECLINE, "sources": [], "status": "declined"}   (fake_llm never called)
            # An llm that answers "Soup at six [4]." and then "Soup at 18:00 [1]." -> status "ok"
            # after 2 calls; the 2nd call got the prompt + FEEDBACK.format(n=1).
            ```

            ## You'll need to find out

            - How to wrap a long paragraph into lines of at most N characters, breaking only at
              spaces. There is a standard-library module for exactly this (or you can write the
              greedy "add words while they fit" loop yourself).

            ## Try it yourself

            Put `MANUAL`, `TOPICS`, `fake_embed` and `fake_llm` into `app.py` (with `import re`)
            and print `format_reply(ask(...))` for a few questions under
            `if __name__ == "__main__":`. Then write a fake llm that invents a `[7]` and watch the
            retry kick in.
        ''',
        "explore": r'''
            - Add a context budget: only include sources while the prompt stays under N characters.
            - Flag sentences in the answer that have no citation at all.
            - Swap `fake_llm` for a real API call behind the same `llm(prompt)` signature.
        ''',
        "rubric": [
            "The decline path returns before the LLM is called",
            "The retry loop is bounded by max_attempts and always resends the original prompt plus feedback",
            "Citation numbers are mapped to titles 1-based, de-duplicated in first-cited order",
            "Retrieval, prompt building, validation and formatting are separate, testable functions",
        ],
        "starter_files": {"app.py": r'''
            # Ask the Ship's Computer - see the brief for the exact rules.
            import math
            import re

            DECLINE = "I don't know. That isn't in the ship's manual."
            INSTRUCTIONS = ("You are the ship's computer. Answer using only the numbered sources and cite them like [1].\n"
                            "If the sources don't contain the answer, say \"I don't know\".")
            FEEDBACK = "\n\nYour last answer had missing or invalid citations. Cite only [1] to [{n}]."


            def cosine(a, b):
                ...


            def retrieve(question, kb, embed, k=3, threshold=0.3):
                ...


            def build_prompt(question, sources):
                ...


            def citations(answer):
                ...


            def ask(question, kb, embed, llm, k=3, threshold=0.3, max_attempts=2):
                ...


            def format_reply(result, width=40):
                ...
        '''},
        "solution_files": {"app.py": r'''
            import math
            import re
            import textwrap

            DECLINE = "I don't know. That isn't in the ship's manual."
            INSTRUCTIONS = ("You are the ship's computer. Answer using only the numbered sources and cite them like [1].\n"
                            "If the sources don't contain the answer, say \"I don't know\".")
            FEEDBACK = "\n\nYour last answer had missing or invalid citations. Cite only [1] to [{n}]."


            def cosine(a, b):
                dot = sum(x * y for x, y in zip(a, b))
                norm_a = math.sqrt(sum(x * x for x in a))
                norm_b = math.sqrt(sum(x * x for x in b))
                if norm_a == 0 or norm_b == 0:
                    return 0.0
                return dot / (norm_a * norm_b)


            def retrieve(question, kb, embed, k=3, threshold=0.3):
                question_vector = embed(question)
                kept = []
                for entry in kb:
                    score = cosine(question_vector, embed(entry["text"]))
                    if score >= threshold:
                        kept.append({"title": entry["title"], "text": entry["text"], "score": score})
                kept.sort(key=lambda s: s["score"], reverse=True)
                return kept[:k]


            def build_prompt(question, sources):
                lines = [f"[{n}] ({s['title']}) {s['text']}" for n, s in enumerate(sources, start=1)]
                return INSTRUCTIONS + "\n\nSources:\n" + "\n".join(lines) + "\n\nQuestion: " + question


            def citations(answer):
                return [int(n) for n in re.findall(r"\[(\d+)\]", answer)]


            def ask(question, kb, embed, llm, k=3, threshold=0.3, max_attempts=2):
                sources = retrieve(question, kb, embed, k, threshold)
                if not sources:
                    return {"answer": DECLINE, "sources": [], "status": "declined"}
                prompt = build_prompt(question, sources)
                n = len(sources)
                for attempt in range(max_attempts):
                    reply = llm(prompt if attempt == 0 else prompt + FEEDBACK.format(n=n))
                    nums = citations(reply)
                    if nums and all(1 <= x <= n for x in nums):
                        cited = []
                        for x in nums:
                            title = sources[x - 1]["title"]
                            if title not in cited:
                                cited.append(title)
                        return {"answer": reply, "sources": cited, "status": "ok"}
                return {"answer": DECLINE, "sources": [], "status": "unverified"}


            def format_reply(result, width=40):
                text = textwrap.fill(result["answer"], width=width)
                if result["sources"]:
                    text += "\n\nSources: " + ", ".join(result["sources"])
                return text


            if __name__ == "__main__":
                manual = [{"title": "engines.md", "text": "The warp engine needs 3 hours to cool down."}]
                embed = lambda text: [text.lower().count("warp")]
                llm = lambda prompt: "It needs 3 hours [1]."
                print(format_reply(ask("warp cooling?", manual, embed, llm)))
        '''},
        "tests": r'''
            import math
            import re
            from app import cosine, retrieve, build_prompt, citations, ask, format_reply, DECLINE, INSTRUCTIONS, FEEDBACK

            MANUAL = [
                {"title": "engines.md", "text": "The warp engine needs 3 hours to cool down after a jump."},
                {"title": "galley.md", "text": "The galley serves soup at 18:00 ship time. Coffee is always available."},
                {"title": "airlock.md", "text": "Never open the airlock without a suit. The airlock cycles in 90 seconds."},
            ]
            TOPICS = ["engine", "warp", "jump", "soup", "coffee", "galley", "airlock", "suit"]

            def fake_embed(text):
                words = re.findall(r"[a-z]+", text.lower())
                return [words.count(t) for t in TOPICS]

            def scripted_llm(*replies):
                prompts = []
                def llm(prompt):
                    prompts.append(prompt)
                    return replies[min(len(prompts), len(replies)) - 1]
                return llm, prompts

            def test_cosine_handles_zero_vectors():
                assert math.isclose(cosine([1, 1], [2, 2]), 1.0)
                assert cosine([0, 0], [1, 0]) == 0.0

            def test_retrieve_keeps_sources_above_threshold_best_first():
                got = retrieve("airlock suit coffee", MANUAL, fake_embed)
                assert [s["title"] for s in got] == ["airlock.md", "galley.md"], f"got {got!r}"
                assert math.isclose(got[0]["score"], 0.7745966692414834), f"got {got[0]!r}"
                assert got[0]["text"] == MANUAL[2]["text"]
                assert retrieve("Who won the space race?", MANUAL, fake_embed) == []

            def test_retrieve_respects_k_threshold_and_tie_order():
                kb = [{"title": "a.md", "text": "soup"}, {"title": "b.md", "text": "soup soup"},
                      {"title": "c.md", "text": "coffee"}]
                got = retrieve("soup", kb, fake_embed, k=5)
                assert [s["title"] for s in got] == ["a.md", "b.md"], f"got {got!r}"
                assert len(retrieve("soup", kb, fake_embed, k=1)) == 1
                got = retrieve("airlock suit coffee", MANUAL, fake_embed, threshold=0.5)
                assert [s["title"] for s in got] == ["airlock.md"], f"got {got!r}"

            def test_build_prompt_has_exact_layout():
                sources = [{"title": "galley.md", "text": "Soup at 18:00.", "score": 0.9},
                           {"title": "engines.md", "text": "Warp needs 3 hours.", "score": 0.4}]
                got = build_prompt("When is soup?", sources)
                want = (INSTRUCTIONS + "\n\nSources:\n[1] (galley.md) Soup at 18:00.\n"
                        "[2] (engines.md) Warp needs 3 hours.\n\nQuestion: When is soup?")
                assert got == want, f"got:\n{got}\n\nwant:\n{want}"

            def test_citations_in_order_with_duplicates():
                assert citations("Yes [2]. Also [10] and [2][1].") == [2, 10, 2, 1], f"got {citations('Yes [2]. Also [10] and [2][1].')!r}"
                assert citations("No sources here, only [x] and (1).") == []

            def test_ask_declines_without_calling_the_llm():
                llm, prompts = scripted_llm("Nobody [1].")
                got = ask("Who won the space race?", MANUAL, fake_embed, llm)
                assert got == {"answer": DECLINE, "sources": [], "status": "declined"}, f"got {got!r}"
                assert prompts == [], "the llm must not be called when nothing is retrieved"

            def test_ask_sends_grounded_prompt_and_returns_cited_titles():
                llm, prompts = scripted_llm("After a jump the warp engine needs 3 hours to cool down [1].")
                q = "How long must the warp engine cool after a jump?"
                got = ask(q, MANUAL, fake_embed, llm)
                assert got == {"answer": "After a jump the warp engine needs 3 hours to cool down [1].",
                               "sources": ["engines.md"], "status": "ok"}, f"got {got!r}"
                assert prompts == [build_prompt(q, retrieve(q, MANUAL, fake_embed))], f"llm got {prompts!r}"

            def test_ask_lists_each_cited_source_once_in_first_cited_order():
                llm, prompts = scripted_llm("Coffee is fine [2], suit up [1][1], coffee again [2].")
                got = ask("airlock suit coffee", MANUAL, fake_embed, llm)
                assert got["status"] == "ok" and got["sources"] == ["galley.md", "airlock.md"], f"got {got!r}"

            def test_ask_retries_with_feedback_after_invalid_citation():
                llm, prompts = scripted_llm("Soup at six [4].", "Soup at 18:00 [1].")
                got = ask("When is soup?", MANUAL, fake_embed, llm)
                assert got == {"answer": "Soup at 18:00 [1].", "sources": ["galley.md"], "status": "ok"}, f"got {got!r}"
                assert len(prompts) == 2, f"expected 2 llm calls, got {len(prompts)}"
                assert prompts[1] == prompts[0] + FEEDBACK.format(n=1), f"2nd prompt was:\n{prompts[1]}"

            def test_uncited_reply_counts_as_bad():
                llm, prompts = scripted_llm("Soup is at 18:00.", "Soup is at 18:00 [1].")
                got = ask("When is soup?", MANUAL, fake_embed, llm)
                assert got["status"] == "ok" and len(prompts) == 2, f"got {got!r} after {len(prompts)} calls"

            def test_ask_gives_up_after_max_attempts():
                llm, prompts = scripted_llm("Soup [9].")
                got = ask("When is soup?", MANUAL, fake_embed, llm, max_attempts=3)
                assert got == {"answer": DECLINE, "sources": [], "status": "unverified"}, f"got {got!r}"
                assert len(prompts) == 3, f"expected exactly 3 llm calls, got {len(prompts)}"
                assert prompts[2] == prompts[0] + FEEDBACK.format(n=1), "every retry should be the original prompt + feedback once"

            def test_format_reply_wraps_answer_and_adds_sources():
                result = {"answer": "After a jump the warp engine needs 3 hours to cool down [1].",
                          "sources": ["engines.md"], "status": "ok"}
                got = format_reply(result)
                want = "After a jump the warp engine needs 3\nhours to cool down [1].\n\nSources: engines.md"
                assert got == want, f"got {got!r}"

            def test_format_reply_custom_width_and_no_sources_line_when_declined():
                result = {"answer": "Coffee is fine [2], suit up [1].", "sources": ["galley.md", "airlock.md"], "status": "ok"}
                got = format_reply(result, width=15)
                assert got == "Coffee is fine\n[2], suit up\n[1].\n\nSources: galley.md, airlock.md", f"got {got!r}"
                declined = {"answer": DECLINE, "sources": [], "status": "declined"}
                got = format_reply(declined)
                assert got == "I don't know. That isn't in the ship's\nmanual.", f"got {got!r}"
        ''',
    },
]
