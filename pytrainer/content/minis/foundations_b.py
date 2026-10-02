"""Chapter projects for the second half of the foundations module:
lists, loops, dicts, functions, errors."""

MINIS = [
    # ------------------------------------------------------------------ lists
    {
        "id": "mini-lists",
        "chapter": "lists",
        "title": "Playlist DJ",
        "estimated_hours": 0.5,
        "main": "app.py",
        "files": ["app.py"],
        "brief": r'''
            You're writing the queue logic for a tiny music player. A playlist is just a
            list of song titles: the song at index `0` is the one **playing now**, and
            everything after it is the queue. No loops needed: list methods, slicing,
            `in`, `len` and an `if` or two will do it.

            ## What to build

            In **`app.py`**, write these five functions. `playlist` is always a list of
            strings, e.g. `["Intro", "Blue", "Gold"]`.

            **`add_song(playlist, song)`**
            - Adds `song` to the **end** of `playlist` (changes the list you were given).
            - **Returns:** `True` if it was added, `False` if it was already in the playlist.

            **`queue_next(playlist, song)`**
            - Puts `song` so it plays **right after** the current song (at index `1`).
            - Changes the list you were given. **Returns:** `None`.

            **`skip(playlist)`**
            - Removes the song that is playing now (index `0`).
            - **Returns:** the new current song (a string), or `None` if nothing is left.

            **`up_next(playlist, n)`**
            - **Returns:** a **new** list with the next `n` songs after the current one.

            **`shuffled(playlist, seed)`**
            - **Returns:** a **new** list: the current song stays first, the rest of the
              queue is shuffled in a repeatable way using `seed` (an int).

            **`status(playlist)`**
            - **Returns:** a one-line string describing the player (formats below).

            ## Rules
            - `add_song`: a song already in the playlist is not added again (no duplicates).
            - `queue_next`: if the song is already somewhere later in the queue, **move** it
              to index `1` (it must not appear twice).
            - `queue_next`: if the song is the one playing now (index `0`), change nothing.
            - `queue_next` on an empty playlist makes `song` the only song.
            - `skip` on an empty playlist returns `None` and doesn't crash.
            - `up_next`: if fewer than `n` songs are queued, return all of them; `n = 0`
              gives `[]`. Don't change `playlist`.
            - `shuffled`: shuffle **only the songs after index 0**, by first seeding
              Python's random number generator with `seed` and then using the standard
              library's function that shuffles a list **in place**. The same seed must
              always give the same order. Don't change `playlist`.
            - `shuffled` on an empty or one-song playlist returns a copy of it.
            - `status` formats (exact text):
              - empty playlist: `"Nothing playing"`
              - one song: `"Now playing: Intro (last song)"`
              - more songs: `"Now playing: Intro | next: Blue | 3 queued"` where the number
                is how many songs come after the current one.

            ## Examples
            ```python
            songs = ["Intro", "Blue", "Gold"]
            add_song(songs, "Neon")        # returns True  -> ["Intro", "Blue", "Gold", "Neon"]
            add_song(songs, "Blue")        # returns False -> unchanged
            queue_next(songs, "Neon")      # songs is now ["Intro", "Neon", "Blue", "Gold"]
            up_next(songs, 2)              # returns ["Neon", "Blue"]
            status(songs)                  # returns "Now playing: Intro | next: Neon | 3 queued"
            skip(songs)                    # returns "Neon" -> ["Neon", "Blue", "Gold"]

            shuffled(["Intro", "Blue", "Gold", "Neon", "Rain"], 42)
            # returns ["Intro", "Neon", "Gold", "Rain", "Blue"]   (on Python 3.14)
            skip([])                       # returns None
            ```

            ## You'll need to find out
            - How to use a module from Python's **standard library** in your file (you need
              one line at the top to make it available).
            - Which standard-library module makes random choices, how to **seed** it so the
              "random" result is the same every run, and which of its functions shuffles
              a list in place.

            ## Try it yourself
            Add a few lines at the bottom of `app.py`, e.g.
            `songs = ["Intro", "Blue"]`, `queue_next(songs, "Gold")`, `print(songs, status(songs))`,
            then run `python3 app.py`. Remove or keep them - the checks only call your functions.
        ''',
        "explore": r'''
            - Add `remove_song(playlist, song)` that returns `True`/`False`.
            - Add `repeat_one(playlist)` that puts a copy of the current song at index 1.
            - What happens to your `shuffled` results with seed `0` vs seed `1`? Try it.
        ''',
        "rubric": [
            "Uses list methods (append, insert, remove, pop) and slicing instead of rebuilding lists by hand",
            "Functions that must not change the input work on a copy or slice",
            "Edge cases (empty playlist, song already playing) are handled with clear, early checks",
            "Readable names and f-strings for the status text",
        ],
        "starter_files": {"app.py": r'''
            # Playlist DJ - index 0 is the song playing now.


            def add_song(playlist, song):
                ...


            def queue_next(playlist, song):
                ...


            def skip(playlist):
                ...


            def up_next(playlist, n):
                ...


            def shuffled(playlist, seed):
                ...


            def status(playlist):
                ...
        '''},
        "solution_files": {"app.py": r'''
            import random


            def add_song(playlist, song):
                if song in playlist:
                    return False
                playlist.append(song)
                return True


            def queue_next(playlist, song):
                if not playlist:
                    playlist.append(song)
                    return None
                if playlist[0] == song:
                    return None
                if song in playlist:
                    playlist.remove(song)
                playlist.insert(1, song)
                return None


            def skip(playlist):
                if not playlist:
                    return None
                playlist.pop(0)
                if not playlist:
                    return None
                return playlist[0]


            def up_next(playlist, n):
                return playlist[1:n + 1]


            def shuffled(playlist, seed):
                rest = playlist[1:]
                random.seed(seed)
                random.shuffle(rest)
                return playlist[:1] + rest


            def status(playlist):
                if not playlist:
                    return "Nothing playing"
                if len(playlist) == 1:
                    return f"Now playing: {playlist[0]} (last song)"
                return f"Now playing: {playlist[0]} | next: {playlist[1]} | {len(playlist) - 1} queued"
        '''},
        "tests": r'''
            import random
            from app import add_song, queue_next, skip, up_next, shuffled, status


            def test_add_song_appends_and_returns_true():
                songs = ["Intro", "Blue"]
                got = add_song(songs, "Gold")
                assert got is True, f"add_song returned {got!r}"
                assert songs == ["Intro", "Blue", "Gold"], f"playlist is now {songs!r}"


            def test_add_song_refuses_duplicates():
                songs = ["Intro", "Blue"]
                got = add_song(songs, "Blue")
                assert got is False, f"add_song returned {got!r} for a song already there"
                assert songs == ["Intro", "Blue"], f"playlist is now {songs!r}"


            def test_queue_next_inserts_after_current_song():
                songs = ["Intro", "Blue", "Gold"]
                queue_next(songs, "Neon")
                assert songs == ["Intro", "Neon", "Blue", "Gold"], f"playlist is now {songs!r}"


            def test_queue_next_moves_a_song_already_queued():
                songs = ["Intro", "Blue", "Gold", "Neon"]
                queue_next(songs, "Neon")
                assert songs == ["Intro", "Neon", "Blue", "Gold"], f"playlist is now {songs!r}"


            def test_queue_next_leaves_the_playing_song_alone():
                songs = ["Intro", "Blue", "Gold"]
                queue_next(songs, "Intro")
                assert songs == ["Intro", "Blue", "Gold"], f"playlist is now {songs!r}"


            def test_queue_next_on_empty_playlist():
                songs = []
                queue_next(songs, "Solo")
                assert songs == ["Solo"], f"playlist is now {songs!r}"


            def test_skip_returns_the_new_current_song():
                songs = ["Intro", "Blue", "Gold"]
                got = skip(songs)
                assert got == "Blue", f"skip returned {got!r}"
                assert songs == ["Blue", "Gold"], f"playlist is now {songs!r}"


            def test_skip_last_and_empty_playlist_return_none():
                songs = ["Solo"]
                got = skip(songs)
                assert got is None and songs == [], f"skip returned {got!r}, playlist {songs!r}"
                got = skip(songs)
                assert got is None, f"skip on an empty playlist returned {got!r}"


            def test_up_next_returns_new_list_of_next_n():
                songs = ["Intro", "Blue", "Gold", "Neon"]
                assert up_next(songs, 2) == ["Blue", "Gold"], f"got {up_next(songs, 2)!r}"
                assert up_next(songs, 10) == ["Blue", "Gold", "Neon"], f"got {up_next(songs, 10)!r}"
                assert up_next(songs, 0) == [], f"n=0 gave {up_next(songs, 0)!r}"
                assert songs == ["Intro", "Blue", "Gold", "Neon"], f"playlist changed to {songs!r}"


            def test_shuffled_keeps_current_song_first_and_uses_the_seed():
                songs = ["Intro", "Blue", "Gold", "Neon", "Rain", "Dawn", "Echo"]
                for seed in (1, 42, 2024):
                    rest = songs[1:]
                    random.Random(seed).shuffle(rest)
                    got = shuffled(songs, seed)
                    assert got == ["Intro"] + rest, f"shuffled(..., {seed}) returned {got!r}"


            def test_shuffled_is_repeatable_and_does_not_change_input():
                songs = ["Intro", "Blue", "Gold", "Neon", "Rain"]
                a = shuffled(songs, 7)
                b = shuffled(songs, 7)
                assert a == b, f"same seed gave {a!r} then {b!r}"
                assert songs == ["Intro", "Blue", "Gold", "Neon", "Rain"], f"input changed to {songs!r}"
                assert a is not songs, "shuffled returned the same list object, not a new list"


            def test_shuffled_tiny_playlists():
                assert shuffled([], 3) == [], f"got {shuffled([], 3)!r}"
                one = ["Solo"]
                got = shuffled(one, 3)
                assert got == ["Solo"] and got is not one, f"got {got!r} (must be a new list)"


            def test_status_formats():
                cases = [
                    ([], "Nothing playing"),
                    (["Intro"], "Now playing: Intro (last song)"),
                    (["Intro", "Blue"], "Now playing: Intro | next: Blue | 1 queued"),
                    (["Intro", "Blue", "Gold", "Neon"], "Now playing: Intro | next: Blue | 3 queued"),
                ]
                for songs, want in cases:
                    got = status(songs)
                    assert got == want, f"status({songs!r}) returned {got!r}"
        ''',
    },
    # ------------------------------------------------------------------ loops
    {
        "id": "mini-loops",
        "chapter": "loops",
        "title": "Word-Guess Game Engine",
        "estimated_hours": 0.75,
        "main": "app.py",
        "files": ["app.py"],
        "brief": r'''
            Build the engine of a classic word-guessing game (think hangman, minus the
            drawing). The engine doesn't ask anyone for input: it gets the secret word and
            a list of guesses, plays the game turn by turn and writes a log of what
            happened - which makes it easy to test, and easy to hook up to a real UI later.

            ## What to build

            In **`app.py`**, write four functions. `secret` is a lowercase word that may
            contain non-letters such as `-` or `'` (e.g. `"t-rex"`). `guessed` is a list of
            lowercase single letters.

            **`mask(secret, guessed)`**
            - **Returns:** a string showing every character of `secret`, separated by
              **one space**: a letter appears if it's in `guessed`, otherwise `_`.
              Non-letters are always shown.

            **`is_solved(secret, guessed)`**
            - **Returns:** `True` if every letter of `secret` is in `guessed`, else `False`.

            **`count_misses(secret, guessed)`**
            - **Returns:** how many letters in `guessed` are **not** in `secret` (an int).

            **`play(secret, guesses, max_misses)`**
            - `guesses`: the list of letters the player typed, in order (may be uppercase).
            - `max_misses`: an int, how many wrong guesses lose the game.
            - **Returns:** a list of strings, one log line per turn, plus a final line.

            ## Rules
            - `mask` never has a space at the start or end.
            - `is_solved` ignores non-letters (they never need guessing).
            - `play` treats uppercase guesses as lowercase (`"E"` is the same as `"e"`),
              and the log shows the lowercase letter.
            - `play` log lines (exact text), where `<mask>` is `mask(...)` **after** this guess:
              - letter in the word: `"e: yes -> _ e _ _ e"`
              - letter not in the word: `"z: no (1/6) -> _ e _ _ e"` (misses so far / `max_misses`)
              - letter guessed before: `"e: already guessed"` (not a miss, mask not shown)
            - As soon as the word is solved, add `"You win!"` and stop - ignore any remaining guesses.
            - As soon as the misses reach `max_misses`, add `"You lose! The word was <secret>."` and stop.
            - If the guesses run out before either happens, add `"Game not finished."`.
            - Don't change the `guesses` list you were given.

            ## Examples
            ```python
            mask("apple", ["p", "e"])          # returns "_ p p _ e"
            mask("t-rex", ["r"])               # returns "_ - r _ _"
            mask("hi", [])                     # returns "_ _"
            is_solved("t-rex", ["t", "r", "e", "x"])   # returns True
            count_misses("apple", ["a", "z", "q"])     # returns 2

            play("apple", ["E", "z", "e", "p", "a", "l", "q"], 3)
            # returns [
            #     "e: yes -> _ _ _ _ e",
            #     "z: no (1/3) -> _ _ _ _ e",
            #     "e: already guessed",
            #     "p: yes -> _ p p _ e",
            #     "a: yes -> a p p _ e",
            #     "l: yes -> a p p l e",
            #     "You win!",
            # ]

            play("cat", ["x", "y"], 2)
            # returns ["x: no (1/2) -> _ _ _", "y: no (2/2) -> _ _ _", "You lose! The word was cat."]
            ```

            ## You'll need to find out
            - How to check whether a single character is a **letter** (and not a symbol
              like `-`), without listing the whole alphabet yourself.
            - (Optional, but neat) how to glue a list of strings together with a
              separator between them in one step.

            ## Try it yourself
            At the bottom of `app.py`:
            `for line in play("apple", ["e", "z", "p", "a", "l"], 6): print(line)`
            then run `python3 app.py`.
        ''',
        "explore": r'''
            - Turn it into a real game: pick a secret from a list and read guesses with `input()`
              in a `while` loop until `play`-style rules say the game is over.
            - Show the wrong letters so far, e.g. `"misses: q z"`.
            - Reject guesses that are not exactly one letter with a log line like `"42: not a letter"`.
        ''',
        "rubric": [
            "Loops use the accumulator pattern clearly (result built before, updated inside, used after)",
            "play reuses mask / is_solved instead of duplicating that logic",
            "break (or return) ends the game at the right moment; no extra turns are processed",
            "Log lines are built with f-strings and match the spec exactly",
        ],
        "starter_files": {"app.py": r'''
            # Word-Guess Game Engine


            def mask(secret, guessed):
                ...


            def is_solved(secret, guessed):
                ...


            def count_misses(secret, guessed):
                ...


            def play(secret, guesses, max_misses):
                ...
        '''},
        "solution_files": {"app.py": r'''
            def mask(secret, guessed):
                shown = []
                for ch in secret:
                    if ch.isalpha() and ch not in guessed:
                        shown.append("_")
                    else:
                        shown.append(ch)
                return " ".join(shown)


            def is_solved(secret, guessed):
                for ch in secret:
                    if ch.isalpha() and ch not in guessed:
                        return False
                return True


            def count_misses(secret, guessed):
                misses = 0
                for letter in guessed:
                    if letter not in secret:
                        misses += 1
                return misses


            def play(secret, guesses, max_misses):
                log = []
                guessed = []
                misses = 0
                for raw in guesses:
                    letter = raw.lower()
                    if letter in guessed:
                        log.append(f"{letter}: already guessed")
                        continue
                    guessed.append(letter)
                    if letter in secret:
                        log.append(f"{letter}: yes -> {mask(secret, guessed)}")
                    else:
                        misses += 1
                        log.append(f"{letter}: no ({misses}/{max_misses}) -> {mask(secret, guessed)}")
                    if is_solved(secret, guessed):
                        log.append("You win!")
                        break
                    if misses >= max_misses:
                        log.append(f"You lose! The word was {secret}.")
                        break
                else:
                    log.append("Game not finished.")
                return log
        '''},
        "tests": r'''
            from app import mask, is_solved, count_misses, play


            def test_mask_hides_unguessed_letters():
                assert mask("apple", ["p", "e"]) == "_ p p _ e", f"got {mask('apple', ['p', 'e'])!r}"
                assert mask("hi", []) == "_ _", f"got {mask('hi', [])!r}"


            def test_mask_always_shows_non_letters():
                got = mask("t-rex", ["r"])
                assert got == "_ - r _ _", f"got {got!r}"
                got = mask("o'neil", [])
                assert got == "_ ' _ _ _ _", f"got {got!r}"


            def test_mask_fully_guessed_word():
                got = mask("cat", ["t", "a", "c", "z"])
                assert got == "c a t", f"got {got!r}"


            def test_is_solved_true_and_false():
                assert is_solved("apple", ["a", "p", "l", "e"]) is True, "all letters guessed should be solved"
                assert is_solved("apple", ["a", "p", "e"]) is False, "a missing letter should not be solved"
                assert is_solved("cat", []) is False, "nothing guessed should not be solved"


            def test_is_solved_ignores_non_letters():
                assert is_solved("t-rex", ["t", "r", "e", "x"]) is True, "the '-' should not need guessing"


            def test_count_misses():
                assert count_misses("apple", ["a", "z", "q"]) == 2, f"got {count_misses('apple', ['a', 'z', 'q'])!r}"
                assert count_misses("apple", []) == 0, f"got {count_misses('apple', [])!r}"
                assert count_misses("apple", ["p", "l"]) == 0, f"got {count_misses('apple', ['p', 'l'])!r}"


            def test_play_winning_game_log():
                got = play("apple", ["E", "z", "e", "p", "a", "l", "q"], 3)
                want = [
                    "e: yes -> _ _ _ _ e",
                    "z: no (1/3) -> _ _ _ _ e",
                    "e: already guessed",
                    "p: yes -> _ p p _ e",
                    "a: yes -> a p p _ e",
                    "l: yes -> a p p l e",
                    "You win!",
                ]
                assert got == want, f"got {got!r}"


            def test_play_losing_game_stops_at_max_misses():
                got = play("cat", ["x", "y", "c", "a", "t"], 2)
                want = ["x: no (1/2) -> _ _ _", "y: no (2/2) -> _ _ _", "You lose! The word was cat."]
                assert got == want, f"got {got!r}"


            def test_play_repeated_miss_is_not_counted_twice():
                got = play("dog", ["z", "z", "d"], 2)
                want = ["z: no (1/2) -> _ _ _", "z: already guessed", "d: yes -> d _ _", "Game not finished."]
                assert got == want, f"got {got!r}"


            def test_play_unfinished_and_empty_game():
                assert play("dog", [], 3) == ["Game not finished."], f"got {play('dog', [], 3)!r}"


            def test_play_word_with_hyphen():
                got = play("t-rex", ["t", "R", "x", "e"], 5)
                want = ["t: yes -> t - _ _ _", "r: yes -> t - r _ _", "x: yes -> t - r _ x",
                        "e: yes -> t - r e x", "You win!"]
                assert got == want, f"got {got!r}"


            def test_play_does_not_change_guesses():
                guesses = ["A", "b", "c"]
                play("abc", guesses, 3)
                assert guesses == ["A", "b", "c"], f"guesses changed to {guesses!r}"
        ''',
    },
    # ------------------------------------------------------------------ dicts
    {
        "id": "mini-dicts",
        "chapter": "dicts",
        "title": "Adventurer's Backpack",
        "estimated_hours": 0.75,
        "main": "app.py",
        "files": ["app.py"],
        "brief": r'''
            Every text adventure needs a backpack. Yours is a dict that maps item names to
            how many you carry, like `{"torch": 1, "stick": 3}`. You'll add and drop loot,
            weigh the pack, craft new items from recipes, sort the pack into pockets - and
            make a **save game** that really is safe from later changes.

            ## What to build

            In **`app.py`**, write six functions. `inv` is always an inventory dict
            `{item name (str): count (int)}`.

            **`add_item(inv, item, qty)`**
            - Adds `qty` (a positive int) of `item` to `inv` (changes the dict you were given).
            - **Returns:** the new count of that item (an int).

            **`drop_item(inv, item, qty)`**
            - Removes `qty` of `item` from `inv`.
            - **Returns:** `True` if it worked, `False` if you don't have enough.

            **`carried_weight(inv, weights)`**
            - `weights`: a dict `{item name: weight of ONE item}` like `{"sword": 5}`.
            - **Returns:** the total weight (count x weight, added up for every item).

            **`craft(inv, recipe)`**
            - `recipe`: a dict like `{"needs": {"stick": 1, "cloth": 1}, "makes": "torch"}`,
              optionally with `"amount": 2` (how many it makes).
            - **Returns:** `True` if crafted, `False` if something is missing.

            **`pockets(inv, kinds)`**
            - `kinds`: a dict `{item name: kind}` like `{"sword": "weapon", "apple": "food"}`.
            - **Returns:** a new dict `{kind: [item names in alphabetical order]}`.

            **`save_game(state)`**
            - `state`: the whole game, nested, e.g.
              `{"room": "cave", "hp": 10, "inventory": {"torch": 1}, "visited": ["gate", "cave"]}`.
            - **Returns:** a copy of `state` that is **completely independent** of it.

            ## Rules
            - `add_item` works for new items and items you already have.
            - `drop_item` with too few (or none) of the item returns `False` and changes nothing.
            - `drop_item`: when an item's count reaches `0`, its key is **removed** from `inv`.
            - `carried_weight`: an item missing from `weights` weighs `1` each. Empty inventory -> `0`.
            - `craft`: only if you have **every** needed item in the needed count: remove them
              (removing keys that reach `0`), then add `amount` (default `1` if the key is
              missing) of `"makes"`. Otherwise return `False` and change **nothing**.
            - `pockets`: items missing from `kinds` go in the `"misc"` pocket. Only kinds that
              have items appear. Don't change `inv`.
            - `save_game`: changing anything in the original afterwards - even inside its
              inner dicts and lists - must not change the save, and changing the save must
              not change the original.

            ## Examples
            ```python
            inv = {"stick": 2}
            add_item(inv, "cloth", 1)      # returns 1  -> {"stick": 2, "cloth": 1}
            add_item(inv, "stick", 3)      # returns 5  -> {"stick": 5, "cloth": 1}
            drop_item(inv, "stick", 9)     # returns False (unchanged)
            drop_item(inv, "cloth", 1)     # returns True  -> {"stick": 5}

            carried_weight({"sword": 1, "apple": 3}, {"sword": 5})   # returns 8

            inv = {"stick": 1, "cloth": 2}
            craft(inv, {"needs": {"stick": 1, "cloth": 1}, "makes": "torch"})
            # returns True -> {"cloth": 1, "torch": 1}

            pockets({"sword": 1, "apple": 3, "bread": 1, "rope": 1},
                    {"sword": "weapon", "apple": "food", "bread": "food"})
            # returns {"weapon": ["sword"], "food": ["apple", "bread"], "misc": ["rope"]}

            state = {"room": "cave", "inventory": {"torch": 1}}
            saved = save_game(state)
            state["inventory"]["torch"] = 0
            saved["inventory"]["torch"]    # still 1
            ```

            ## You'll need to find out
            - How to make a **deep** copy of nested data - a copy where the inner dicts and
              lists are copied too (the chapter's `.copy()` is only *shallow*). There's a
              standard-library module for exactly this.

            ## Try it yourself
            At the bottom of `app.py`, build a small inventory, call your functions and
            `print` the dict after each step, then run `python3 app.py`.
        ''',
        "explore": r'''
            - Add `can_craft(inv, recipe)` that returns the list of missing items instead of just `False`.
            - Add a weight limit: `add_item` refuses loot that would make the pack too heavy.
            - Write `load_game(saved)` and check that a load, a change and a second load behave.
        ''',
        "rubric": [
            "Uses .get() with defaults and `in` checks instead of try/except or long if chains",
            "craft checks everything first and only then changes the inventory",
            "pockets uses a grouping pattern (setdefault or equivalent) and returns sorted lists",
            "save_game produces a real deep copy, not a shallow .copy()",
        ],
        "starter_files": {"app.py": r'''
            # Adventurer's Backpack - inventories are {item: count} dicts.


            def add_item(inv, item, qty):
                ...


            def drop_item(inv, item, qty):
                ...


            def carried_weight(inv, weights):
                ...


            def craft(inv, recipe):
                ...


            def pockets(inv, kinds):
                ...


            def save_game(state):
                ...
        '''},
        "solution_files": {"app.py": r'''
            import copy


            def add_item(inv, item, qty):
                inv[item] = inv.get(item, 0) + qty
                return inv[item]


            def drop_item(inv, item, qty):
                if inv.get(item, 0) < qty:
                    return False
                inv[item] -= qty
                if inv[item] == 0:
                    del inv[item]
                return True


            def carried_weight(inv, weights):
                total = 0
                for item, count in inv.items():
                    total += count * weights.get(item, 1)
                return total


            def craft(inv, recipe):
                needs = recipe["needs"]
                for item, qty in needs.items():
                    if inv.get(item, 0) < qty:
                        return False
                for item, qty in needs.items():
                    drop_item(inv, item, qty)
                add_item(inv, recipe["makes"], recipe.get("amount", 1))
                return True


            def pockets(inv, kinds):
                groups = {}
                for item in inv:
                    groups.setdefault(kinds.get(item, "misc"), []).append(item)
                for kind in groups:
                    groups[kind] = sorted(groups[kind])
                return groups


            def save_game(state):
                return copy.deepcopy(state)
        '''},
        "tests": r'''
            from app import add_item, drop_item, carried_weight, craft, pockets, save_game


            def test_add_item_new_and_existing():
                inv = {"stick": 2}
                got = add_item(inv, "cloth", 1)
                assert got == 1 and inv == {"stick": 2, "cloth": 1}, f"returned {got!r}, inv {inv!r}"
                got = add_item(inv, "stick", 3)
                assert got == 5 and inv == {"stick": 5, "cloth": 1}, f"returned {got!r}, inv {inv!r}"


            def test_drop_item_reduces_count():
                inv = {"stick": 5, "cloth": 1}
                got = drop_item(inv, "stick", 2)
                assert got is True and inv == {"stick": 3, "cloth": 1}, f"returned {got!r}, inv {inv!r}"


            def test_drop_item_removes_key_at_zero():
                inv = {"stick": 5, "cloth": 1}
                got = drop_item(inv, "cloth", 1)
                assert got is True, f"returned {got!r}"
                assert inv == {"stick": 5}, f"inv is {inv!r} (a count of 0 should disappear)"


            def test_drop_item_not_enough_changes_nothing():
                inv = {"stick": 2}
                assert drop_item(inv, "stick", 3) is False, "dropping more than you have should fail"
                assert drop_item(inv, "gem", 1) is False, "dropping an item you don't have should fail"
                assert inv == {"stick": 2}, f"inv changed to {inv!r}"


            def test_carried_weight_with_unknown_items():
                got = carried_weight({"sword": 1, "apple": 3}, {"sword": 5})
                assert got == 8, f"got {got!r}"
                got = carried_weight({"sword": 2, "shield": 1}, {"sword": 5, "shield": 7})
                assert got == 17, f"got {got!r}"
                assert carried_weight({}, {"sword": 5}) == 0, "an empty pack should weigh 0"


            def test_craft_success_uses_up_ingredients():
                inv = {"stick": 1, "cloth": 2}
                got = craft(inv, {"needs": {"stick": 1, "cloth": 1}, "makes": "torch"})
                assert got is True, f"returned {got!r}"
                assert inv == {"cloth": 1, "torch": 1}, f"inv is {inv!r}"


            def test_craft_with_amount_adds_to_existing():
                inv = {"flint": 3, "arrow": 2}
                got = craft(inv, {"needs": {"flint": 2}, "makes": "arrow", "amount": 5})
                assert got is True and inv == {"flint": 1, "arrow": 7}, f"returned {got!r}, inv {inv!r}"


            def test_craft_missing_ingredient_changes_nothing():
                inv = {"stick": 3, "cloth": 1}
                recipe = {"needs": {"stick": 2, "cloth": 2}, "makes": "tent"}
                got = craft(inv, recipe)
                assert got is False, f"returned {got!r}"
                assert inv == {"stick": 3, "cloth": 1}, f"inv changed to {inv!r}"
                assert recipe == {"needs": {"stick": 2, "cloth": 2}, "makes": "tent"}, "recipe was changed"


            def test_pockets_groups_and_sorts():
                inv = {"sword": 1, "apple": 3, "rope": 1, "bread": 1, "axe": 1}
                kinds = {"sword": "weapon", "axe": "weapon", "bread": "food", "apple": "food"}
                got = pockets(inv, kinds)
                want = {"weapon": ["axe", "sword"], "food": ["apple", "bread"], "misc": ["rope"]}
                assert got == want, f"got {got!r}"
                assert inv == {"sword": 1, "apple": 3, "rope": 1, "bread": 1, "axe": 1}, "inv was changed"


            def test_pockets_only_used_kinds_and_empty():
                got = pockets({"apple": 1}, {"apple": "food", "sword": "weapon"})
                assert got == {"food": ["apple"]}, f"got {got!r}"
                assert pockets({}, {"apple": "food"}) == {}, f"got {pockets({}, {'apple': 'food'})!r}"


            def test_save_game_is_equal_to_the_state():
                state = {"room": "cave", "hp": 10, "inventory": {"torch": 1}, "visited": ["gate", "cave"]}
                saved = save_game(state)
                assert saved == state, f"save is {saved!r}"
                assert saved is not state, "save_game returned the same dict, not a copy"


            def test_save_game_survives_changes_to_nested_data():
                state = {"room": "cave", "hp": 10, "inventory": {"torch": 1}, "visited": ["gate", "cave"]}
                saved = save_game(state)
                state["hp"] = 3
                state["inventory"]["torch"] = 0
                state["visited"].append("pit")
                want = {"room": "cave", "hp": 10, "inventory": {"torch": 1}, "visited": ["gate", "cave"]}
                assert saved == want, f"the save changed to {saved!r} when the game changed"
                saved["inventory"]["gem"] = 1
                assert "gem" not in state["inventory"], "changing the save changed the original"
        ''',
    },
    # ------------------------------------------------------------------ functions
    {
        "id": "mini-functions",
        "chapter": "functions",
        "title": "Chat-Log Detective",
        "estimated_hours": 0.75,
        "main": "app.py",
        "files": ["app.py"],
        "brief": r'''
            A group chat was exported as plain text lines like `"ada: who ate my sandwich?"`.
            Build a small toolkit to load the log and investigate it: count who talks the
            most and search with **filters you can combine** - little functions made by
            other functions. The same pattern (build a filter, pass it in) shows up
            everywhere in AI apps, e.g. filtering retrieved documents before a prompt.

            ## What to build

            In **`app.py`**. A *message* is a dict `{"user": "ada", "text": "who ate my sandwich?"}`;
            a *log* is a list of messages.

            **`parse_line(line)`**
            - `line`: a string like `"Ada: who ate my sandwich?"`.
            - **Returns:** a message dict, or `None` if the line is not a valid message.

            **`load_log(lines)`**
            - `lines`: a list of strings. **Returns:** a log (list of message dicts).

            **`count_messages(log, user=None)`**
            - **Returns:** how many messages are in `log`; if `user` is given, only that user's.

            **`make_filter(*, user=None, contains=None)`**
            - Both parameters are **keyword-only** (calling `make_filter("ada")` must raise `TypeError`).
            - **Returns:** a **function** that takes one message and returns `True` or `False`.

            **`search(log, *filters)`**
            - Any number of filter functions (made by `make_filter`, or your own).
            - **Returns:** a new list with the messages for which **every** filter returns `True`.

            **`most_active(log)`**
            - **Returns:** the user name with the most messages.

            ## Rules
            - `parse_line` splits at the **first** `": "` (colon + space) only: in
              `"bob: meet at 10: 30"` the text is `"meet at 10: 30"`.
            - `parse_line`: the user name is stripped of spaces and lowercased; the text is
              stripped of spaces (case kept).
            - `parse_line` returns `None` when there is no `": "`, or the user or the text is
              empty after stripping.
            - `load_log` skips invalid lines and keeps the order of the valid ones.
            - `count_messages`: `user` matching ignores case (`"Ada"` counts `"ada"`'s messages).
            - The filter from `make_filter` checks `user` (ignoring case) if given, and checks that
              the text contains `contains` (ignoring case) if given. With neither, it accepts
              every message.
            - `search` with no filters returns all messages (as a new list). It never changes `log`.
            - `most_active`: on a tie, the user whose **first** message comes earliest in the log
              wins. Empty log -> `None`.

            ## Examples
            ```python
            parse_line("Ada: who ate my sandwich?")  # returns {"user": "ada", "text": "who ate my sandwich?"}
            parse_line("bob: meet at 10: 30")         # returns {"user": "bob", "text": "meet at 10: 30"}
            parse_line("just some noise")             # returns None
            parse_line("cy:   ")                      # returns None

            log = load_log(["ada: who ate my sandwich?", "bob: not me", "--- day 2 ---",
                            "ada: BOB.", "cy: it was the cat"])
            count_messages(log)                       # returns 4
            count_messages(log, "ADA")                # returns 2

            by_ada = make_filter(user="ada")
            about_bob = make_filter(contains="bob")
            search(log, by_ada, about_bob)            # returns [{"user": "ada", "text": "BOB."}]
            most_active(log)                          # returns "ada"
            ```

            ## You'll need to find out
            - How to cut a string into two parts at the **first** place a separator appears
              (and know whether the separator was there at all). Strings have a method for it.

            ## Try it yourself
            At the bottom of `app.py`, load a few lines, then try
            `print(search(log, make_filter(contains="cat")))` and run `python3 app.py`.
        ''',
        "explore": r'''
            - Add `make_filter(..., min_words=None)` for messages with at least that many words.
            - Write `any_of(*filters)` that returns a filter accepting a message if ANY filter does.
            - Print a leaderboard of the three chattiest users.
        ''',
        "rubric": [
            "parse_line is small and reused by load_log instead of duplicating the parsing",
            "make_filter returns an inner function (closure) that remembers user/contains",
            "Defaults, keyword-only parameters and *args are used as specified, with no mutable defaults",
            "Functions have clear names, a docstring or type hints, and return instead of print",
        ],
        "starter_files": {"app.py": r'''
            # Chat-Log Detective


            def parse_line(line):
                ...


            def load_log(lines):
                ...


            def count_messages(log, user=None):
                ...


            def make_filter(*, user=None, contains=None):
                ...


            def search(log, *filters):
                ...


            def most_active(log):
                ...
        '''},
        "solution_files": {"app.py": r'''
            def parse_line(line: str) -> dict | None:
                """Turn "name: text" into a message dict, or None if it isn't one."""
                user, sep, text = line.partition(": ")
                user = user.strip().lower()
                text = text.strip()
                if not sep or not user or not text:
                    return None
                return {"user": user, "text": text}


            def load_log(lines: list[str]) -> list[dict]:
                log = []
                for line in lines:
                    message = parse_line(line)
                    if message is not None:
                        log.append(message)
                return log


            def count_messages(log: list[dict], user: str | None = None) -> int:
                if user is None:
                    return len(log)
                total = 0
                for message in log:
                    if message["user"] == user.lower():
                        total += 1
                return total


            def make_filter(*, user=None, contains=None):
                def accept(message):
                    if user is not None and message["user"] != user.lower():
                        return False
                    if contains is not None and contains.lower() not in message["text"].lower():
                        return False
                    return True
                return accept


            def search(log, *filters):
                found = []
                for message in log:
                    keep = True
                    for check in filters:
                        if not check(message):
                            keep = False
                            break
                    if keep:
                        found.append(message)
                return found


            def most_active(log):
                counts = {}
                for message in log:
                    counts[message["user"]] = counts.get(message["user"], 0) + 1
                best = None
                for user, n in counts.items():
                    if best is None or n > counts[best]:
                        best = user
                return best
        '''},
        "tests": r'''
            import inspect
            from app import parse_line, load_log, count_messages, make_filter, search, most_active

            LINES = [
                "ada: who ate my sandwich?",
                "bob: not me",
                "--- day 2 ---",
                "Ada: BOB.",
                "cy: it was the cat",
                "bob: the CAT? really?",
                "cy:   ",
            ]


            def test_parse_line_valid_message():
                got = parse_line("Ada: who ate my sandwich?")
                assert got == {"user": "ada", "text": "who ate my sandwich?"}, f"got {got!r}"
                got = parse_line("  Bob :  hi there  ")
                assert got == {"user": "bob", "text": "hi there"}, f"got {got!r}"


            def test_parse_line_splits_at_first_separator_only():
                got = parse_line("bob: meet at 10: 30")
                assert got == {"user": "bob", "text": "meet at 10: 30"}, f"got {got!r}"


            def test_parse_line_invalid_lines_return_none():
                for line in ["just some noise", "cy:   ", ": hello", "time:10", ""]:
                    got = parse_line(line)
                    assert got is None, f"parse_line({line!r}) returned {got!r}"


            def test_load_log_skips_invalid_lines_in_order():
                log = load_log(LINES)
                users = [m["user"] for m in log]
                assert users == ["ada", "bob", "ada", "cy", "bob"], f"users in order: {users!r}"
                assert load_log([]) == [], "an empty list of lines should give an empty log"


            def test_count_messages_all_and_per_user():
                log = load_log(LINES)
                assert count_messages(log) == 5, f"got {count_messages(log)!r}"
                assert count_messages(log, "ADA") == 2, f"got {count_messages(log, 'ADA')!r}"
                assert count_messages(log, user="zed") == 0, f"got {count_messages(log, user='zed')!r}"


            def test_make_filter_parameters_are_keyword_only():
                try:
                    make_filter("ada")
                except TypeError:
                    pass
                else:
                    raise AssertionError("make_filter('ada') should raise TypeError (keyword-only)")


            def test_make_filter_returns_a_function():
                f = make_filter(user="ada")
                assert callable(f), f"make_filter returned {f!r}, not a function"
                assert f({"user": "ada", "text": "x"}) is True, "filter rejected a matching message"
                assert f({"user": "bob", "text": "x"}) is False, "filter accepted another user's message"


            def test_filters_ignore_case():
                by_user = make_filter(user="BOB")
                about_cat = make_filter(contains="cat")
                assert by_user({"user": "bob", "text": "hi"}) is True, "user filter should ignore case"
                assert about_cat({"user": "bob", "text": "the CAT? really?"}) is True, "contains should ignore case"
                assert about_cat({"user": "bob", "text": "not me"}) is False, "contains matched wrong text"


            def test_filter_with_no_criteria_accepts_everything():
                everything = make_filter()
                assert everything({"user": "zed", "text": "anything"}) is True, "an empty filter should accept all"


            def test_search_combines_filters():
                log = load_log(LINES)
                got = search(log, make_filter(user="ada"), make_filter(contains="bob"))
                assert got == [{"user": "ada", "text": "BOB."}], f"got {got!r}"
                got = search(log, make_filter(contains="cat"))
                assert [m["user"] for m in got] == ["cy", "bob"], f"got {got!r}"
                got = search(log, make_filter(user="bob", contains="cat"))
                assert got == [{"user": "bob", "text": "the CAT? really?"}], f"got {got!r}"


            def test_search_with_no_filters_returns_new_list():
                log = load_log(LINES)
                before = list(log)
                got = search(log)
                assert got == log and got is not log, "search(log) should return all messages in a new list"
                search(log, make_filter(user="ada"))
                assert log == before, "search changed the log"


            def test_search_accepts_any_function_as_filter():
                log = load_log(LINES)
                def short(message):
                    return len(message["text"]) < 8
                got = search(log, short)
                assert got == [{"user": "bob", "text": "not me"}, {"user": "ada", "text": "BOB."}], f"got {got!r}"


            def test_most_active_and_ties():
                log = load_log(["cy: a", "bob: b", "cy: c", "bob: d", "ada: e"])
                assert most_active(log) == "cy", f"tie should go to the earliest user, got {most_active(log)!r}"
                log = load_log(["cy: a", "bob: b", "bob: c"])
                assert most_active(log) == "bob", f"got {most_active(log)!r}"
                assert most_active([]) is None, f"empty log gave {most_active([])!r}"


            def test_count_messages_user_is_optional():
                params = inspect.signature(count_messages).parameters
                assert "user" in params and params["user"].default is None, "count_messages needs user=None"
        ''',
    },
    # ------------------------------------------------------------------ errors
    {
        "id": "mini-errors",
        "chapter": "errors",
        "title": "The Uncrashable Calculator",
        "estimated_hours": 0.75,
        "main": "app.py",
        "files": ["app.py"],
        "brief": r'''
            Users type anything. Your job: a calculator that understands lines like
            `"12 / 4"`, gives **precise, typed errors** to other code, and a friendly layer
            on top that **never crashes**, whatever garbage comes in. This two-layer idea
            (strict core that raises, safe wrapper that reports) is exactly how you'll wrap
            LLM API calls later.

            ## What to build

            In **`app.py`**:

            **Three exception classes**
            - `CalcError` (a sub-type of `Exception`), and two sub-types of it:
              `ParseError` (the input is badly written) and `MathError` (the maths fails).

            **`parse(expr)`**
            - `expr`: a string like `"12 / 4"`: a number, an operator, a number, separated by spaces.
            - **Returns:** a tuple `(left, op, right)` with both numbers as floats, e.g. `(12.0, "/", 4.0)`.

            **`calculate(expr)`**
            - **Returns:** the result as a float. Operators: `+`, `-`, `*`, `/`, `**` (power).

            **`format_result(x)`**
            - **Returns:** a string: whole numbers without decimals (`7.0` -> `"7"`), others
              rounded to 4 decimals (`1/3` -> `"0.3333"`).

            **`safe_calculate(expr)`**
            - **Returns:** `"= <result>"` using `format_result`, or `"error: <message>"`.
              It **never raises**.

            **`run_session(lines)`**
            - `lines`: a list of strings typed by a user.
            - **Returns:** a list of output strings (one per calculation, plus a summary).

            ## Rules
            - `parse` checks in this order and raises `ParseError` with this exact message:
              1. not exactly 3 parts -> `"expected: number operator number"`
              2. operator not one of the five -> `"unknown operator: <op>"`
              3. left, then right, not a number -> `"not a number: <text>"`, raised
                 **from** the original `ValueError` (so the error's `__cause__` is that `ValueError`).
            - Extra spaces between parts are fine (`"  2   +  3 "` works).
            - `calculate` raises the errors from `parse` unchanged, and `MathError`:
              - dividing by zero (including `0 ** -1`) -> `"division by zero"`, raised from the original error
              - a result too large for a float (e.g. `"10 ** 400"`) -> `"result too large"`, raised from the original error
            - `safe_calculate` catches `CalcError` (and its sub-types) only; the message is `str(error)`.
            - `safe_calculate` given something that is not a string returns `"error: expected text"`.
            - `run_session`: strip each line; skip blank lines; stop at the line `"quit"`
              (ignore everything after it); every other line gives one `safe_calculate` output.
              Finally add a summary line `"<n> ok, <m> errors"`, e.g. `"2 ok, 1 errors"`.

            ## Examples
            ```python
            parse("12 / 4")         # returns (12.0, "/", 4.0)
            parse("3 x 4")          # raises ParseError("unknown operator: x")
            calculate("2 ** 10")    # returns 1024.0
            calculate("5 / 0")      # raises MathError("division by zero")

            safe_calculate("7 * 6")       # returns "= 42"
            safe_calculate("10 / 4")      # returns "= 2.5"
            safe_calculate("1 / 3")       # returns "= 0.3333"
            safe_calculate("ten + 1")     # returns "error: not a number: ten"
            safe_calculate("10 ** 400")   # returns "error: result too large"
            safe_calculate(None)          # returns "error: expected text"

            run_session(["1 + 1", "", "2 / 0", "quit", "3 * 3"])
            # returns ["= 2", "error: division by zero", "1 ok, 1 errors"]
            ```

            ## You'll need to find out
            - How to split a string into parts on whitespace, however many spaces there are.
            - Which built-in exception Python raises when a float calculation's result is too
              big to represent (try `10.0 ** 400` in a Python shell and read the error).

            ## Try it yourself
            At the bottom of `app.py`:
            `for line in run_session(["1 + 2", "oops", "8 / 0", "2 ** 0.5"]): print(line)`,
            then run `python3 app.py`.
        ''',
        "explore": r'''
            - Make it interactive: read lines with `input()` in a loop until `quit` (and handle Ctrl+D).
            - Support `%` (remainder) and `//` (whole-number division).
            - Keep a `last` value so `"_ * 2"` reuses the previous result.
        ''',
        "rubric": [
            "Custom exceptions form a small hierarchy (CalcError -> ParseError / MathError)",
            "try blocks are small and catch specific exceptions, never a bare except",
            "Low-level errors are translated with `raise ... from ...` so the cause is kept",
            "safe_calculate is the only place that turns errors into text; parse/calculate raise",
        ],
        "starter_files": {"app.py": r'''
            # The Uncrashable Calculator


            def parse(expr):
                ...


            def calculate(expr):
                ...


            def format_result(x):
                ...


            def safe_calculate(expr):
                ...


            def run_session(lines):
                ...
        '''},
        "solution_files": {"app.py": r'''
            OPERATORS = ("+", "-", "*", "/", "**")


            class CalcError(Exception):
                pass


            class ParseError(CalcError):
                pass


            class MathError(CalcError):
                pass


            def to_number(text):
                try:
                    return float(text)
                except ValueError as e:
                    raise ParseError(f"not a number: {text}") from e


            def parse(expr):
                parts = expr.split()
                if len(parts) != 3:
                    raise ParseError("expected: number operator number")
                left, op, right = parts
                if op not in OPERATORS:
                    raise ParseError(f"unknown operator: {op}")
                return to_number(left), op, to_number(right)


            def calculate(expr):
                left, op, right = parse(expr)
                try:
                    if op == "+":
                        return left + right
                    if op == "-":
                        return left - right
                    if op == "*":
                        return left * right
                    if op == "/":
                        return left / right
                    return left ** right
                except ZeroDivisionError as e:
                    raise MathError("division by zero") from e
                except OverflowError as e:
                    raise MathError("result too large") from e


            def format_result(x):
                if x == int(x):
                    return str(int(x))
                return str(round(x, 4))


            def safe_calculate(expr):
                if not isinstance(expr, str):
                    return "error: expected text"
                try:
                    result = calculate(expr)
                except CalcError as e:
                    return f"error: {e}"
                return f"= {format_result(result)}"


            def run_session(lines):
                out = []
                ok = 0
                errors = 0
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    if line == "quit":
                        break
                    result = safe_calculate(line)
                    if result.startswith("error"):
                        errors += 1
                    else:
                        ok += 1
                    out.append(result)
                out.append(f"{ok} ok, {errors} errors")
                return out
        '''},
        "tests": r'''
            import app
            from app import parse, calculate, format_result, safe_calculate, run_session


            def raises(fn, arg, exc_type):
                try:
                    fn(arg)
                except exc_type as e:
                    return e
                except Exception as e:
                    raise AssertionError(f"{fn.__name__}({arg!r}) raised {type(e).__name__}: {e}") from None
                raise AssertionError(f"{fn.__name__}({arg!r}) raised nothing")


            def test_exception_hierarchy():
                for name in ("CalcError", "ParseError", "MathError"):
                    assert hasattr(app, name), f"app.py has no class {name}"
                assert issubclass(app.CalcError, Exception), "CalcError must be a sub-type of Exception"
                assert issubclass(app.ParseError, app.CalcError), "ParseError must be a sub-type of CalcError"
                assert issubclass(app.MathError, app.CalcError), "MathError must be a sub-type of CalcError"
                assert not issubclass(app.ParseError, app.MathError), "ParseError should not be a MathError"


            def test_parse_valid_expressions():
                assert parse("12 / 4") == (12.0, "/", 4.0), f"got {parse('12 / 4')!r}"
                got = parse("  -2.5   **  3 ")
                assert got == (-2.5, "**", 3.0), f"got {got!r}"
                assert isinstance(parse("1 + 2")[0], float), "numbers should be floats"


            def test_parse_wrong_number_of_parts():
                for expr in ["", "3 +", "3+4", "1 + 2 + 3"]:
                    e = raises(parse, expr, app.ParseError)
                    assert str(e) == "expected: number operator number", f"parse({expr!r}) message: {str(e)!r}"


            def test_parse_unknown_operator_checked_before_numbers():
                e = raises(parse, "3 x 4", app.ParseError)
                assert str(e) == "unknown operator: x", f"message: {str(e)!r}"
                e = raises(parse, "a ^ b", app.ParseError)
                assert str(e) == "unknown operator: ^", f"message: {str(e)!r}"


            def test_parse_bad_number_keeps_the_cause():
                e = raises(parse, "ten + 1", app.ParseError)
                assert str(e) == "not a number: ten", f"message: {str(e)!r}"
                assert isinstance(e.__cause__, ValueError), f"__cause__ is {e.__cause__!r}, raise it from the ValueError"
                e = raises(parse, "1 + 2x", app.ParseError)
                assert str(e) == "not a number: 2x", f"message: {str(e)!r}"


            def test_calculate_all_operators():
                cases = {"2 + 3": 5.0, "2 - 3": -1.0, "4 * 2.5": 10.0, "9 / 2": 4.5, "2 ** 10": 1024.0}
                for expr, want in cases.items():
                    got = calculate(expr)
                    assert got == want, f"calculate({expr!r}) returned {got!r}"


            def test_calculate_division_by_zero_is_math_error():
                for expr in ["5 / 0", "0 ** -1"]:
                    e = raises(calculate, expr, app.MathError)
                    assert str(e) == "division by zero", f"calculate({expr!r}) message: {str(e)!r}"
                    assert isinstance(e.__cause__, ZeroDivisionError), f"__cause__ is {e.__cause__!r}"


            def test_calculate_too_large_is_math_error():
                e = raises(calculate, "10 ** 400", app.MathError)
                assert str(e) == "result too large", f"message: {str(e)!r}"
                assert e.__cause__ is not None, "raise the MathError from the original error"


            def test_calculate_passes_parse_errors_through():
                raises(calculate, "3 x 4", app.ParseError)


            def test_format_result():
                cases = [(7.0, "7"), (2.5, "2.5"), (1 / 3, "0.3333"), (-4.0, "-4"), (0.0, "0"), (2 / 3, "0.6667")]
                for x, want in cases:
                    got = format_result(x)
                    assert got == want, f"format_result({x!r}) returned {got!r}"


            def test_safe_calculate_results_and_errors():
                cases = {
                    "7 * 6": "= 42",
                    "10 / 4": "= 2.5",
                    "1 / 3": "= 0.3333",
                    "ten + 1": "error: not a number: ten",
                    "5 / 0": "error: division by zero",
                    "10 ** 400": "error: result too large",
                    "hello": "error: expected: number operator number",
                    "3 % 2": "error: unknown operator: %",
                }
                for expr, want in cases.items():
                    got = safe_calculate(expr)
                    assert got == want, f"safe_calculate({expr!r}) returned {got!r}"


            def test_safe_calculate_never_raises():
                for junk in [None, 42, ["1", "+", "1"], "", "   ", "+ + +", "1 / 0.0", "0 ** -2"]:
                    try:
                        got = safe_calculate(junk)
                    except Exception as e:
                        raise AssertionError(f"safe_calculate({junk!r}) raised {type(e).__name__}") from None
                    assert isinstance(got, str), f"safe_calculate({junk!r}) returned {got!r}"
                assert safe_calculate(None) == "error: expected text", f"got {safe_calculate(None)!r}"


            def test_run_session_stops_at_quit_and_summarises():
                got = run_session(["1 + 1", "", "2 / 0", "quit", "3 * 3"])
                assert got == ["= 2", "error: division by zero", "1 ok, 1 errors"], f"got {got!r}"


            def test_run_session_strips_lines_and_handles_no_quit():
                got = run_session(["  2 ** 3  ", "   ", "oops", "1.5 + 1.5"])
                assert got == ["= 8", "error: expected: number operator number", "= 3", "2 ok, 1 errors"], f"got {got!r}"
                assert run_session([]) == ["0 ok, 0 errors"], f"got {run_session([])!r}"
        ''',
    },
]
