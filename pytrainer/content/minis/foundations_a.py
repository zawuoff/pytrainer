"""Chapter projects (minis) for the first foundations chapters:
basics, variables, data-types, conditionals, fstrings."""

MINIS = [
    # ------------------------------------------------------------------ basics
    {
        "id": "mini-basics",
        "chapter": "basics",
        "title": "Robot Speech Bubble",
        "estimated_hours": 0.5,
        "main": "app.py",
        "files": ["app.py"],
        "brief": r'''
            Every good robot needs a way to talk. You'll build a tiny text-art kit that
            puts whatever the robot says inside a speech bubble, in capital letters, with
            the robot standing underneath. Some functions **return** text, some **print**
            it - getting that difference right is half the project.

            ## What to build

            Write these five functions in **`app.py`**:

            1. `shout(text)`
               - `text`: a string, e.g. `"hello"`
               - **Returns:** the same text in CAPITAL letters with one `!` added at the end, e.g. `"HELLO!"`
            2. `border(text)`
               - `text`: a string, e.g. `"hi"`
               - **Returns:** a string: `+`, then dashes, then `+`. The number of dashes is the
                 length of `text` **plus 2**. `border("hi")` returns `"+----+"`.
            3. `middle(text)`
               - `text`: a string, e.g. `"hi"`
               - **Returns:** a string: `|`, one space, the text, one space, `|`, e.g. `"| hi |"`
            4. `bubble(text)`
               - **Prints** three lines: `border(text)`, `middle(text)`, `border(text)`.
            5. `robot_says(text)`
               - **Prints** the bubble of the **shouted** text, then one more line: two
                 spaces followed by `[o_o]`, i.e. `"  [o_o]"`.

            ## Rules
            - `shout`, `border` and `middle` **return** their string and print nothing.
            - `bubble` and `robot_says` **print** their lines (each line exactly as shown, no extra spaces at the end, no extra lines).
            - `shout` only changes letters: digits, spaces and punctuation stay as they are (`"r2d2 ok"` gives `"R2D2 OK!"`).
            - `shout` always adds exactly one `!`, even for empty text: `shout("")` returns `"!"`.
            - For empty text the bubble is still drawn: `border("")` returns `"+--+"` and `middle("")` returns `"|  |"`.
            - `border(text)` and `middle(text)` always have the same length, so the bubble lines up.

            ## Examples
            ```python
            shout("hello")      # returns "HELLO!"
            shout("r2d2 ok")    # returns "R2D2 OK!"
            border("hi")        # returns "+----+"
            middle("hi")        # returns "| hi |"
            border("")          # returns "+--+"
            ```

            `bubble("hi")` prints:
            ```
            +----+
            | hi |
            +----+
            ```

            `robot_says("beep boop")` prints:
            ```
            +------------+
            | BEEP BOOP! |
            +------------+
              [o_o]
            ```

            ## You'll need to find out
            - how to turn a piece of text into all capital letters (Python has this built in for strings)
            - how to repeat a piece of text a number of times without typing it out (e.g. make `"-----"` from `"-"` and the number `5`)

            ## Try it yourself
            Add a line like `robot_says("hello world")` at the bottom of `app.py` (not indented)
            and press **Run** to see your robot talk. Try a long sentence and an empty one.
        ''',
        "explore": r'''
            - Give the robot a second line of body under its face, e.g. `"  /| |"`.
            - Write `whisper(text)` that makes everything lowercase and adds `...` instead of `!`.
            - Make `robot_says` take a second parameter for the robot's face, so you can
              pass `"[^_^]"` or `"[x_x]"`.
        ''',
        "rubric": [
            "shout, border and middle return strings; only bubble and robot_says print",
            "bubble reuses border and middle instead of rebuilding the lines by hand",
            "robot_says reuses shout and bubble",
            "Readable names and no leftover debugging prints inside the functions",
        ],
        "starter_files": {"app.py": r'''
            # Robot Speech Bubble - write shout, border, middle, bubble and robot_says here.


            def shout(text):
                ...
        '''},
        "solution_files": {"app.py": r'''
            # Robot Speech Bubble: text art for a talking robot.


            def shout(text):
                return text.upper() + "!"


            def border(text):
                return "+" + "-" * (len(text) + 2) + "+"


            def middle(text):
                return "| " + text + " |"


            def bubble(text):
                print(border(text))
                print(middle(text))
                print(border(text))


            def robot_says(text):
                bubble(shout(text))
                print("  [o_o]")
        '''},
        "tests": r'''
            from app import shout, border, middle, bubble, robot_says


            def lines_printed(fn, text):
                value, out = capture(fn, text)
                return out.rstrip("\n").split("\n")


            def test_shout_makes_capitals_and_adds_one_exclamation_mark():
                got = shout("hello")
                assert got == "HELLO!", f"shout('hello') returned {got!r}"


            def test_shout_keeps_digits_spaces_and_punctuation():
                got = shout("r2d2 ok?")
                assert got == "R2D2 OK?!", f"shout('r2d2 ok?') returned {got!r}"


            def test_shout_of_empty_text_is_just_the_exclamation_mark():
                got = shout("")
                assert got == "!", f"shout('') returned {got!r}"


            def test_shout_returns_instead_of_printing():
                value, out = capture(shout, "hi")
                assert out == "", f"shout printed {out!r} - it should only return"
                assert value == "HI!", f"shout('hi') returned {value!r}"


            def test_border_has_two_more_dashes_than_the_text_length():
                got = border("hi")
                assert got == "+----+", f"border('hi') returned {got!r}"
                got = border("hello world")
                assert got == "+-------------+", f"border('hello world') returned {got!r}"


            def test_border_of_empty_text():
                got = border("")
                assert got == "+--+", f"border('') returned {got!r}"


            def test_middle_wraps_text_in_bars_and_spaces():
                got = middle("hi")
                assert got == "| hi |", f"middle('hi') returned {got!r}"
                got = middle("")
                assert got == "|  |", f"middle('') returned {got!r}"


            def test_border_and_middle_return_without_printing():
                for fn in (border, middle):
                    value, out = capture(fn, "abc")
                    assert out == "", f"{fn.__name__} printed {out!r} - it should only return"
                    assert isinstance(value, str), f"{fn.__name__}('abc') returned {value!r}"


            def test_border_and_middle_line_up_for_any_text():
                for text in ("a", "robots rule", "x" * 40):
                    assert len(border(text)) == len(middle(text)), f"lengths differ for {text!r}"


            def test_bubble_prints_exactly_three_lines():
                got = lines_printed(bubble, "hi")
                assert got == ["+----+", "| hi |", "+----+"], f"bubble('hi') printed {got!r}"


            def test_bubble_does_not_shout():
                got = lines_printed(bubble, "calm")
                assert got == ["+------+", "| calm |", "+------+"], f"bubble('calm') printed {got!r}"


            def test_robot_says_shouts_inside_the_bubble():
                got = lines_printed(robot_says, "beep boop")
                assert got[:3] == ["+------------+", "| BEEP BOOP! |", "+------------+"], (
                    f"robot_says('beep boop') printed {got!r}")


            def test_robot_stands_under_the_bubble():
                got = lines_printed(robot_says, "hi")
                assert len(got) == 4, f"robot_says('hi') printed {len(got)} lines: {got!r}"
                assert got[3] == "  [o_o]", f"the robot line is {got[3]!r}"
        ''',
    },
    # --------------------------------------------------------------- variables
    {
        "id": "mini-variables",
        "chapter": "variables",
        "title": "Pocket Arena",
        "estimated_hours": 0.75,
        "main": "app.py",
        "files": ["app.py"],
        "brief": r'''
            A tiny turn-based battle game, the kind every game dev writes first. Each
            fighter is a tuple `(name, hp, power)`: a name, hit points and attack power.
            Your job is the game engine: the functions that take fighters apart
            (*unpacking*), change their numbers, and hand back updated fighters.

            ## What to build

            In **`app.py`**:

            **Two constants** at the top of the file:
            - `LEVEL_UP_HP = 20`
            - `LEVEL_UP_POWER = 5`

            **Five functions.** Every "fighter" below is a tuple `(name, hp, power)`,
            e.g. `("Ada", 30, 7)` - `name` is a string, `hp` and `power` are whole numbers.

            1. `hit(attacker, defender)`
               - **Returns:** the defender as a new fighter tuple, with `hp` lowered by the attacker's `power`.
            2. `clash(first, second)`
               - Both fighters hit each other at the same moment.
               - **Returns:** a tuple of two fighters: `(first after being hit, second after being hit)`.
            3. `heal(fighter, amount, max_hp)`
               - `amount`: hit points to add, `max_hp`: the most hp this fighter can have.
               - **Returns:** the fighter with `hp` raised by `amount`.
            4. `level_up(fighter)`
               - **Returns:** the fighter with `LEVEL_UP_HP` added to `hp` and `LEVEL_UP_POWER` added to `power`.
            5. `hits_to_win(attacker, defender)`
               - **Returns:** how many hits (an `int`) the attacker needs to bring the defender's `hp` to 0.

            ## Rules
            - The name always stays the same; only the numbers change.
            - Return fighters as tuples in the order `(name, hp, power)`.
            - `hp` never goes below `0`: a hit of 10 on a fighter with 4 hp leaves `0`.
            - `heal` never goes above `max_hp`: healing 50 on 90 hp with `max_hp` 100 gives 100.
            - In `clash` both hits use the fighters as they were **before** the clash.
            - `level_up` must use the two constants, not the numbers typed again (a check
              changes the constants and expects `level_up` to follow).
            - `hits_to_win` counts a final hit that does less than full damage as a whole hit
              (7 power vs 30 hp needs `5` hits). A defender already at 0 hp needs `0` hits.
              The attacker's power is always at least 1.

            ## Examples
            ```python
            ada = ("Ada", 30, 7)
            bot = ("Bot", 12, 4)

            hit(ada, bot)                  # returns ("Bot", 5, 4)
            hit(ada, ("Imp", 4, 1))        # returns ("Imp", 0, 1)
            clash(ada, bot)                # returns (("Ada", 26, 7), ("Bot", 5, 4))
            heal(("Ada", 90, 7), 50, 100)  # returns ("Ada", 100, 7)
            heal(("Ada", 10, 7), 5, 100)   # returns ("Ada", 15, 7)
            level_up(ada)                  # returns ("Ada", 50, 12)
            hits_to_win(ada, bot)          # returns 2
            hits_to_win(bot, ada)          # returns 8
            ```

            ## You'll need to find out
            - how to pick the **smaller** of two numbers with a built-in (you've met its opposite already)
            - how to divide and round the result **up** to the next whole number (e.g. 30 / 7 -> 5), without an `if`

            ## Try it yourself
            Put a mini battle at the bottom of `app.py`, e.g.
            `print(clash(("Ada", 30, 7), ("Bot", 12, 4)))`, press **Run**, then feed the result
            back into `clash` a few times to see who wins.
        ''',
        "explore": r'''
            - Add a `defence` number to each fighter that is subtracted from incoming damage.
            - Write `rest(fighter)` that heals 10% of `max_hp`, rounded.
            - Write a `duel(first, second)` that clashes three times in a row and returns
              both fighters (no loops needed - just three lines).
        ''',
        "rubric": [
            "Fighters are unpacked into well-named variables instead of indexed like f[1]",
            "LEVEL_UP_HP and LEVEL_UP_POWER are defined once at the top and used by level_up",
            "clash reuses hit instead of repeating the damage maths",
            "No magic numbers left in the functions",
        ],
        "starter_files": {"app.py": r'''
            # Pocket Arena - a fighter is a tuple (name, hp, power).
            # Define LEVEL_UP_HP and LEVEL_UP_POWER here, then write the five functions.


            def hit(attacker, defender):
                ...
        '''},
        "solution_files": {"app.py": r'''
            # Pocket Arena - a fighter is a tuple (name, hp, power).
            import math

            LEVEL_UP_HP = 20
            LEVEL_UP_POWER = 5


            def hit(attacker, defender):
                attacker_name, attacker_hp, damage = attacker
                name, hp, power = defender
                hp = max(0, hp - damage)
                return name, hp, power


            def clash(first, second):
                return hit(second, first), hit(first, second)


            def heal(fighter, amount, max_hp):
                name, hp, power = fighter
                hp = min(hp + amount, max_hp)
                return name, hp, power


            def level_up(fighter):
                name, hp, power = fighter
                hp += LEVEL_UP_HP
                power += LEVEL_UP_POWER
                return name, hp, power


            def hits_to_win(attacker, defender):
                attacker_name, attacker_hp, damage = attacker
                name, hp, power = defender
                return math.ceil(hp / damage)
        '''},
        "tests": r'''
            import app
            from app import hit, clash, heal, level_up, hits_to_win

            ADA = ("Ada", 30, 7)
            BOT = ("Bot", 12, 4)


            def test_hit_lowers_defender_hp_by_attacker_power():
                got = hit(ADA, BOT)
                assert got == ("Bot", 5, 4), f"hit(ADA, BOT) returned {got!r}"


            def test_hit_returns_a_tuple_with_name_hp_power():
                got = hit(BOT, ADA)
                assert isinstance(got, tuple), f"hit returned a {type(got).__name__}, expected a tuple"
                assert got == ("Ada", 26, 7), f"hit(BOT, ADA) returned {got!r}"


            def test_hp_never_goes_below_zero():
                got = hit(ADA, ("Imp", 4, 1))
                assert got == ("Imp", 0, 1), f"hit on a 4 hp fighter returned {got!r}"
                got = hit(ADA, ("Imp", 7, 1))
                assert got == ("Imp", 0, 1), f"hit on a 7 hp fighter returned {got!r}"


            def test_clash_hits_both_fighters_at_once():
                got = clash(ADA, BOT)
                assert got == (("Ada", 26, 7), ("Bot", 5, 4)), f"clash(ADA, BOT) returned {got!r}"


            def test_clash_keeps_the_order_of_fighters():
                got = clash(BOT, ADA)
                assert got == (("Bot", 5, 4), ("Ada", 26, 7)), f"clash(BOT, ADA) returned {got!r}"


            def test_heal_adds_hp():
                got = heal(("Ada", 10, 7), 5, 100)
                assert got == ("Ada", 15, 7), f"heal(('Ada', 10, 7), 5, 100) returned {got!r}"


            def test_heal_stops_at_max_hp():
                got = heal(("Ada", 90, 7), 50, 100)
                assert got == ("Ada", 100, 7), f"heal(('Ada', 90, 7), 50, 100) returned {got!r}"
                got = heal(("Ada", 40, 7), 10, 50)
                assert got == ("Ada", 50, 7), f"heal(('Ada', 40, 7), 10, 50) returned {got!r}"


            def test_constants_exist_with_the_right_values():
                assert getattr(app, "LEVEL_UP_HP", None) == 20, "LEVEL_UP_HP is missing or not 20"
                assert getattr(app, "LEVEL_UP_POWER", None) == 5, "LEVEL_UP_POWER is missing or not 5"


            def test_level_up_adds_hp_and_power():
                got = level_up(ADA)
                assert got == ("Ada", 50, 12), f"level_up(ADA) returned {got!r}"


            def test_level_up_uses_the_constants():
                old = (app.LEVEL_UP_HP, app.LEVEL_UP_POWER)
                try:
                    app.LEVEL_UP_HP, app.LEVEL_UP_POWER = 1, 2
                    got = level_up(ADA)
                finally:
                    app.LEVEL_UP_HP, app.LEVEL_UP_POWER = old
                assert got == ("Ada", 31, 9), (
                    f"with LEVEL_UP_HP=1 and LEVEL_UP_POWER=2, level_up(ADA) returned {got!r}")


            def test_hits_to_win_rounds_up_a_partial_hit():
                got = hits_to_win(ADA, BOT)
                assert got == 2, f"hits_to_win(ADA, BOT) returned {got!r}"
                got = hits_to_win(ADA, ("Ogre", 30, 9))
                assert got == 5, f"7 power vs 30 hp: hits_to_win returned {got!r}"


            def test_hits_to_win_exact_division():
                got = hits_to_win(BOT, ("Ada", 28, 7))
                assert got == 7, f"4 power vs 28 hp: hits_to_win returned {got!r}"
                assert type(got) is int, f"hits_to_win returned a {type(got).__name__}, expected int"


            def test_hits_to_win_against_a_knocked_out_fighter_is_zero():
                got = hits_to_win(ADA, ("Imp", 0, 1))
                assert got == 0, f"hits_to_win vs 0 hp returned {got!r}"


            def test_functions_do_not_change_the_name():
                for got in (hit(ADA, BOT), heal(BOT, 1, 99), level_up(BOT)):
                    assert got[0] == "Bot", f"the name changed: {got!r}"
        ''',
    },
    # -------------------------------------------------------------- data-types
    {
        "id": "mini-data-types",
        "chapter": "data-types",
        "title": "Dinner Bill Splitter",
        "estimated_hours": 0.75,
        "main": "app.py",
        "files": ["app.py"],
        "brief": r'''
            Five friends, one bill, one person who always "forgets" the tip. You'll build
            the maths behind a bill-splitting app. Money arrives as messy **text** typed by
            humans (`" $1,250.50 "`), and floats are not exact, so real money apps work in
            whole **cents** (`int`). You'll convert carefully, then split fairly.

            ## What to build

            Write these functions in **`app.py`**:

            1. `parse_amount(text)`
               - `text`: a money amount typed by a person, e.g. `" $1,250.50 "`
               - **Returns:** the amount as a `float`, e.g. `1250.5`
            2. `to_cents(amount)`
               - `amount`: a `float` in dollars, e.g. `19.99`
               - **Returns:** the amount in cents as an `int`, rounded to the nearest cent, e.g. `1999`
            3. `tip_cents(bill_cents, percent)`
               - `bill_cents`: an `int`, `percent`: a whole number like `15` (meaning 15%)
               - **Returns:** the tip in cents as an `int`, rounded to the nearest cent
            4. `split(total_cents, people)`
               - `total_cents`: an `int`, `people`: an `int` of at least 1
               - **Returns:** a tuple of two `int`s `(each, extra)`: everyone pays `each` cents, and
                 `extra` is how many cents are left over (so `extra` people pay one cent more)
            5. `splits_evenly(total_cents, people)`
               - **Returns:** `True` if the total divides between the people with no cents left over, else `False`
            6. `split_bill(bill_text, percent, people)`
               - `bill_text`: text like `parse_amount` takes, `percent`: tip percent (int), `people`: int
               - **Returns:** the `(each, extra)` tuple for the bill **plus** tip, all in cents
            7. `shared_dishes(order_a, order_b)`
               - `order_a`, `order_b`: tuples of dish names, e.g. `("pizza", "salad")`
               - **Returns:** a `set` of the dishes that appear in **both** orders

            ## Rules
            - `parse_amount` accepts spaces/newlines around the text, an optional `$` at the
              start, and commas as thousands separators. It always returns a `float` (`"12"` gives `12.0`).
            - `to_cents` must round, not cut: `0.29` is `29` cents and `19.99` is `1999`
              (watch out: `0.29 * 100` is not exactly `29` in Python).
            - `tip_cents` returns an `int` (use rounding to the nearest cent; `0`% gives `0`).
            - `split` and `split_bill` return whole numbers (`int`), never floats.
            - `split_bill` works out: bill in cents -> tip in cents -> total = bill + tip -> split.
            - `splits_evenly` returns a real `bool` (`True`/`False`), not a number.
            - `shared_dishes` returns an empty set when nothing is shared; each dish appears once.

            ## Examples
            ```python
            parse_amount(" $1,250.50 ")     # returns 1250.5
            parse_amount("12")              # returns 12.0
            to_cents(19.99)                 # returns 1999
            to_cents(0.29)                  # returns 29
            tip_cents(5000, 15)             # returns 750
            tip_cents(1999, 18)             # returns 360   (359.82 rounded)
            split(1000, 3)                  # returns (333, 1)
            splits_evenly(1000, 4)          # returns True
            split_bill(" $59.99\n", 15, 4)  # returns (1724, 3)
            shared_dishes(("pizza", "salad"), ("salad", "soup", "pizza"))
            # returns {"pizza", "salad"}
            ```

            ## You'll need to find out
            - how to remove a specific character (like `$`) from the **ends** of a string - the tool you
              already know for trimming spaces can do more than spaces
            - how to remove **every** occurrence of a character (like `,`) from anywhere inside a string

            ## Try it yourself
            At the bottom of `app.py` add `print(split_bill("$84.20", 20, 3))` and press **Run**.
            Then try `print(0.29 * 100)` to see why rounding matters.
        ''',
        "explore": r'''
            - Write `cents_to_text(cents)` that turns `1724` into `"17.24"` using `//` and `%`
              (careful with `5` cents: it must show as `"0.05"`).
            - Let each person pick their own tip percent.
            - Write `all_dishes(order_a, order_b)`: every dish that anyone ordered.
        ''',
        "rubric": [
            "Money is converted to int cents early and the maths stays in ints",
            "split_bill reuses parse_amount, to_cents, tip_cents and split",
            "Float rounding is handled with round() rather than int() truncation",
            "Clear variable names for each step (bill_cents, tip, total...)",
        ],
        "starter_files": {"app.py": r'''
            # Dinner Bill Splitter - work in whole cents (int) wherever you can.


            def parse_amount(text):
                ...
        '''},
        "solution_files": {"app.py": r'''
            # Dinner Bill Splitter - work in whole cents (int) wherever you can.


            def parse_amount(text):
                cleaned = text.strip().lstrip("$").replace(",", "")
                return float(cleaned)


            def to_cents(amount):
                return round(amount * 100)


            def tip_cents(bill_cents, percent):
                return round(bill_cents * percent / 100)


            def split(total_cents, people):
                return total_cents // people, total_cents % people


            def splits_evenly(total_cents, people):
                return total_cents % people == 0


            def split_bill(bill_text, percent, people):
                bill = to_cents(parse_amount(bill_text))
                total = bill + tip_cents(bill, percent)
                return split(total, people)


            def shared_dishes(order_a, order_b):
                return set(order_a) & set(order_b)
        '''},
        "tests": r'''
            from app import (parse_amount, to_cents, tip_cents, split, splits_evenly,
                             split_bill, shared_dishes)


            def test_parse_amount_handles_dollar_sign_commas_and_spaces():
                got = parse_amount(" $1,250.50 ")
                assert got == 1250.5, f"parse_amount(' $1,250.50 ') returned {got!r}"
                got = parse_amount("$2,000,000\n")
                assert got == 2000000.0, f"parse_amount('$2,000,000\\n') returned {got!r}"


            def test_parse_amount_always_returns_a_float():
                got = parse_amount("12")
                assert got == 12.0 and type(got) is float, f"parse_amount('12') returned {got!r}"
                got = parse_amount("3.75")
                assert got == 3.75, f"parse_amount('3.75') returned {got!r}"


            def test_to_cents_rounds_instead_of_cutting():
                for amount, want in ((19.99, 1999), (0.29, 29), (4.35, 435), (1.0, 100)):
                    got = to_cents(amount)
                    assert got == want, f"to_cents({amount}) returned {got!r}"


            def test_to_cents_returns_an_int():
                got = to_cents(12.5)
                assert type(got) is int, f"to_cents(12.5) returned {got!r} ({type(got).__name__})"


            def test_tip_cents_is_percent_of_bill_rounded():
                got = tip_cents(5000, 15)
                assert got == 750 and type(got) is int, f"tip_cents(5000, 15) returned {got!r}"
                got = tip_cents(1999, 18)
                assert got == 360, f"tip_cents(1999, 18) returned {got!r}"
                got = tip_cents(1234, 0)
                assert got == 0, f"tip_cents(1234, 0) returned {got!r}"


            def test_split_gives_each_share_and_leftover_cents():
                got = split(1000, 3)
                assert got == (333, 1), f"split(1000, 3) returned {got!r}"
                got = split(999, 4)
                assert got == (249, 3), f"split(999, 4) returned {got!r}"


            def test_split_returns_ints_not_floats():
                got = split(1000, 4)
                assert got == (250, 0), f"split(1000, 4) returned {got!r}"
                assert all(type(x) is int for x in got), f"split(1000, 4) returned {got!r}"


            def test_split_for_one_person():
                got = split(5, 1)
                assert got == (5, 0), f"split(5, 1) returned {got!r}"


            def test_splits_evenly_returns_a_bool():
                assert splits_evenly(1000, 4) is True, "splits_evenly(1000, 4) should be True"
                assert splits_evenly(1000, 3) is False, "splits_evenly(1000, 3) should be False"


            def test_split_bill_parses_tips_and_splits():
                got = split_bill(" $59.99\n", 15, 4)
                assert got == (1724, 3), f"split_bill(' $59.99\\n', 15, 4) returned {got!r}"


            def test_split_bill_with_commas_and_no_tip():
                got = split_bill("$1,000.00", 0, 3)
                assert got == (33333, 1), f"split_bill('$1,000.00', 0, 3) returned {got!r}"
                assert all(type(x) is int for x in got), f"split_bill returned {got!r}"


            def test_shared_dishes_are_in_both_orders():
                got = shared_dishes(("pizza", "salad"), ("salad", "soup", "pizza"))
                assert got == {"pizza", "salad"}, f"shared_dishes returned {got!r}"
                assert isinstance(got, set), f"shared_dishes returned a {type(got).__name__}, expected a set"


            def test_shared_dishes_empty_when_nothing_in_common():
                got = shared_dishes(("soup", "soup"), ("cake",))
                assert got == set(), f"shared_dishes returned {got!r}"
        ''',
    },
    # ------------------------------------------------------------ conditionals
    {
        "id": "mini-conditionals",
        "chapter": "conditionals",
        "title": "Rock Paper Scissors Referee",
        "estimated_hours": 0.75,
        "main": "app.py",
        "files": ["app.py"],
        "brief": r'''
            Two players type their moves and your code is the referee. Players are sloppy:
            they type `" ROCK "`, `"sc"` or `"p"`, and sometimes nonsense. A good referee
            understands shortcuts, rejects nonsense, announces who won and knows when the
            whole match is over.

            ## What to build

            Write these functions in **`app.py`**:

            1. `clean_move(text)`
               - `text`: whatever a player typed (always a string), e.g. `" Sc "`
               - **Returns:** `"rock"`, `"paper"` or `"scissors"`, or `None` if it isn't a move
            2. `judge(text1, text2)`
               - `text1`, `text2`: what player 1 and player 2 typed (raw, not cleaned)
               - **Returns:** `"player 1"`, `"player 2"`, `"draw"` or `"invalid"`
            3. `commentary(move1, move2)`
               - `move1`, `move2`: two **clean** moves (`"rock"`, `"paper"` or `"scissors"`)
               - **Returns:** a sentence about what happened (see the table)
            4. `parse_best_of(text)`
               - `text`: how many games the match lasts, as typed, e.g. `" 5 "`
               - **Returns:** the number as an `int`, or `None` if it isn't valid
            5. `match_status(wins1, wins2, best_of)`
               - `wins1`, `wins2`: games won so far by each player (ints), `best_of`: a valid odd int
               - **Returns:** `"player 1 wins the match"`, `"player 2 wins the match"`,
                 `"match point"` or `"keep playing"`

            ## Rules
            - `clean_move` ignores spaces around the text and upper/lower case.
            - `clean_move` accepts a move written in full **or any beginning of it**: `"r"`, `"ro"`,
              `"roc"` and `"rock"` all mean `"rock"`; `"sc"` and `"sciss"` mean `"scissors"`.
            - Anything else is `None`: empty or blank text, `"rocks"` (longer than the move),
              `"stone"`, `"x"`.
            - Rock beats scissors, scissors beats paper, paper beats rock. Same move = `"draw"`.
            - `judge` returns `"invalid"` if **either** player's move is not a move.
            - `commentary` uses exactly these sentences, whichever player played the winning move:

              | moves (either order) | returns |
              | --- | --- |
              | rock and scissors | `"rock crushes scissors"` |
              | scissors and paper | `"scissors cut paper"` |
              | paper and rock | `"paper covers rock"` |
              | the same move twice | `"it's a tie"` |

            - `parse_best_of` ignores spaces around the text. Valid means: only digits, and the
              number is odd and at least 1. `"abc"`, `""`, `"-3"`, `"2.5"`, `"4"` and `"0"` all give `None`.
            - `match_status`: a player needs **more than half** of `best_of` games to win the match
              (best of 5 -> 3 wins). Check for a match winner first. If nobody has won yet but at
              least one player is exactly one win away, return `"match point"`.

            ## Examples
            ```python
            clean_move(" ROCK ")         # returns "rock"
            clean_move("sc")             # returns "scissors"
            clean_move("rocks")          # returns None
            clean_move("   ")            # returns None
            judge("p", " Rock")          # returns "player 1"
            judge("scissors", "R")       # returns "player 2"
            judge("paper", "PAP")        # returns "draw"
            judge("rock", "lizard")      # returns "invalid"
            commentary("paper", "scissors")  # returns "scissors cut paper"
            parse_best_of(" 5 ")         # returns 5
            parse_best_of("4")           # returns None
            match_status(3, 1, 5)        # returns "player 1 wins the match"
            match_status(2, 0, 5)        # returns "match point"
            match_status(1, 1, 5)        # returns "keep playing"
            ```

            ## You'll need to find out
            - how to check whether one string is the **beginning** of another string (there is a string method for it)
            - how to check whether a string is made **only of digits** (also a string method), so you can
              reject bad input before calling `int()` on it

            ## Try it yourself
            At the bottom of `app.py` add
            `print(judge("sc", "paper"), "-", commentary("scissors", "paper"))` and press **Run**.
            Try all nine move pairs.
        ''',
        "explore": r'''
            - Add lizard and Spock (look up the rules). Watch out: "s" is now ambiguous
              between scissors and Spock - what should `clean_move("s")` do?
            - Write `score_line(wins1, wins2)` that returns `"2 - 1"`.
            - Let the computer play: look up how to pick a random item.
        ''',
        "rubric": [
            "judge reuses clean_move instead of repeating the cleaning logic",
            "The win rules are written once (e.g. a helper or one clear condition), not copied in many places",
            "Early returns / elif keep the branches easy to follow and every path returns a value",
            "Empty input is handled deliberately in clean_move",
        ],
        "starter_files": {"app.py": r'''
            # Rock Paper Scissors Referee


            def clean_move(text):
                ...
        '''},
        "solution_files": {"app.py": r'''
            # Rock Paper Scissors Referee


            def clean_move(text):
                text = text.strip().lower()
                if not text:
                    return None
                if "rock".startswith(text):
                    return "rock"
                if "paper".startswith(text):
                    return "paper"
                if "scissors".startswith(text):
                    return "scissors"
                return None


            def beats(a, b):
                return (a, b) in (("rock", "scissors"), ("scissors", "paper"), ("paper", "rock"))


            def judge(text1, text2):
                move1 = clean_move(text1)
                move2 = clean_move(text2)
                if move1 is None or move2 is None:
                    return "invalid"
                if move1 == move2:
                    return "draw"
                return "player 1" if beats(move1, move2) else "player 2"


            def commentary(move1, move2):
                if move1 == move2:
                    return "it's a tie"
                winner, loser = (move1, move2) if beats(move1, move2) else (move2, move1)
                match winner:
                    case "rock":
                        return "rock crushes scissors"
                    case "scissors":
                        return "scissors cut paper"
                    case _:
                        return "paper covers rock"


            def parse_best_of(text):
                text = text.strip()
                if not text.isdigit():
                    return None
                number = int(text)
                if number < 1 or number % 2 == 0:
                    return None
                return number


            def match_status(wins1, wins2, best_of):
                needed = best_of // 2 + 1
                if wins1 >= needed:
                    return "player 1 wins the match"
                if wins2 >= needed:
                    return "player 2 wins the match"
                if wins1 == needed - 1 or wins2 == needed - 1:
                    return "match point"
                return "keep playing"
        '''},
        "tests": r'''
            from app import clean_move, judge, commentary, parse_best_of, match_status


            def test_clean_move_ignores_case_and_spaces():
                for text, want in ((" ROCK ", "rock"), ("Paper", "paper"), ("\tscissors\n", "scissors")):
                    got = clean_move(text)
                    assert got == want, f"clean_move({text!r}) returned {got!r}"


            def test_clean_move_accepts_any_beginning_of_a_move():
                cases = (("r", "rock"), ("ro", "rock"), ("P", "paper"), ("pap", "paper"),
                         ("sc", "scissors"), ("sciss", "scissors"), ("s", "scissors"))
                for text, want in cases:
                    got = clean_move(text)
                    assert got == want, f"clean_move({text!r}) returned {got!r}"


            def test_clean_move_rejects_nonsense_with_none():
                for text in ("rocks", "stone", "x", "rp", "papers"):
                    got = clean_move(text)
                    assert got is None, f"clean_move({text!r}) returned {got!r}"


            def test_clean_move_rejects_empty_and_blank_text():
                for text in ("", "   "):
                    got = clean_move(text)
                    assert got is None, f"clean_move({text!r}) returned {got!r}"


            def test_judge_finds_the_winner_either_way_round():
                cases = (("rock", "scissors", "player 1"), ("scissors", "rock", "player 2"),
                         ("scissors", "paper", "player 1"), ("paper", "scissors", "player 2"),
                         ("paper", "rock", "player 1"), ("rock", "paper", "player 2"))
                for a, b, want in cases:
                    got = judge(a, b)
                    assert got == want, f"judge({a!r}, {b!r}) returned {got!r}"


            def test_judge_cleans_raw_input():
                got = judge("p", " Rock")
                assert got == "player 1", f"judge('p', ' Rock') returned {got!r}"
                got = judge("scissors", "R")
                assert got == "player 2", f"judge('scissors', 'R') returned {got!r}"


            def test_judge_same_move_is_a_draw():
                got = judge("paper", "PAP")
                assert got == "draw", f"judge('paper', 'PAP') returned {got!r}"


            def test_judge_invalid_if_either_move_is_bad():
                for a, b in (("rock", "lizard"), ("", "rock"), ("stone", "stone")):
                    got = judge(a, b)
                    assert got == "invalid", f"judge({a!r}, {b!r}) returned {got!r}"


            def test_commentary_names_the_winning_move_in_any_order():
                cases = (("rock", "scissors", "rock crushes scissors"),
                         ("scissors", "rock", "rock crushes scissors"),
                         ("paper", "scissors", "scissors cut paper"),
                         ("scissors", "paper", "scissors cut paper"),
                         ("rock", "paper", "paper covers rock"),
                         ("paper", "rock", "paper covers rock"))
                for a, b, want in cases:
                    got = commentary(a, b)
                    assert got == want, f"commentary({a!r}, {b!r}) returned {got!r}"


            def test_commentary_same_move_is_a_tie():
                got = commentary("rock", "rock")
                assert got == "it's a tie", f"commentary('rock', 'rock') returned {got!r}"


            def test_parse_best_of_reads_odd_numbers():
                for text, want in ((" 5 ", 5), ("1", 1), ("7\n", 7), ("11", 11)):
                    got = parse_best_of(text)
                    assert got == want and type(got) is int, f"parse_best_of({text!r}) returned {got!r}"


            def test_parse_best_of_rejects_bad_input_with_none():
                for text in ("abc", "", "  ", "-3", "2.5", "4", "0", "5 games"):
                    got = parse_best_of(text)
                    assert got is None, f"parse_best_of({text!r}) returned {got!r}"


            def test_match_status_reports_a_match_winner():
                got = match_status(3, 1, 5)
                assert got == "player 1 wins the match", f"match_status(3, 1, 5) returned {got!r}"
                got = match_status(0, 2, 3)
                assert got == "player 2 wins the match", f"match_status(0, 2, 3) returned {got!r}"


            def test_match_status_match_point_and_keep_playing():
                for args, want in (((2, 0, 5), "match point"), ((1, 2, 5), "match point"),
                                   ((1, 1, 5), "keep playing"), ((0, 0, 1), "match point"),
                                   ((2, 2, 7), "keep playing")):
                    got = match_status(*args)
                    assert got == want, f"match_status{args} returned {got!r}"
        ''',
    },
    # ---------------------------------------------------------------- fstrings
    {
        "id": "mini-fstrings",
        "chapter": "fstrings",
        "title": "Café Receipt Printer",
        "estimated_hours": 1.0,
        "main": "app.py",
        "files": ["app.py"],
        "brief": r'''
            The café down the road needs its receipt printer software. A receipt is
            32 characters wide, every line must line up to the character, prices sit
            flush right, and the shop name is centred in a row of stars. This is exactly
            what format specs are for.

            ## What to build

            Write these functions in **`app.py`** (all of them **return** strings, none of them print):

            1. `money(amount)`
               - `amount`: a number of dollars (int or float), e.g. `1234.5`
               - **Returns:** `"$1,234.50"`: a `$`, thousands commas, exactly 2 decimals
            2. `row(label, amount)`
               - `label`: a string, `amount`: a number
               - **Returns:** a 32-character line: `label` left-aligned in 20 characters, then
                 `money(amount)` right-aligned in 12 characters
            3. `header(shop)`
               - `shop`: the shop name, e.g. `"Bean There"`
               - **Returns:** the name in CAPITALS with one space on each side, centred in 32
                 characters and filled with `*` on both sides
            4. `stamp(number, day)`
               - `number`: the receipt number (int), `day`: a `datetime.date`, e.g. `date(2026, 9, 28)`
               - **Returns:** `"Receipt #000042 | 28 Sep 2026"`
            5. `item_line(name, qty, unit_price)`
               - `name`: dish name, `qty`: how many (int, at least 1), `unit_price`: price of one
               - **Returns:** a `row` whose label is the name (or `"<qty> x <name>"` when `qty` is more
                 than 1) and whose amount is `qty * unit_price`
            6. `summary(subtotal, discount, tax_rate)`
               - `subtotal`: dollars, `discount`: dollars taken off (`0` for none), `tax_rate`: a fraction, e.g. `0.08`
               - **Returns:** several lines joined by newlines (`"\n"`), no newline at the end:
                 1. 32 dashes
                 2. `row("Subtotal", subtotal)`
                 3. **only if** `discount` is more than 0: `row("Discount", -discount)`
                 4. `row("Tax (8.0%)", tax)` - the rate as a percentage with 1 decimal
                 5. `row("TOTAL", total)`

            ## Rules
            - `money` of a negative amount puts the minus sign **before** the `$`: `money(-2)` is `"-$2.00"`.
            - `row`: a label longer than 20 characters is **cut** to its first 20, so the row stays 32 wide.
              (A money text wider than 12 characters may make the row longer - that's fine.)
            - `header`: if the stars can't be split evenly, the extra star goes on the **right**.
              A name too long for 32 characters is shown in full with no stars.
            - `stamp`: the receipt number is zero-padded to 6 digits; the date is day (2 digits),
              short English month name, 4-digit year.
            - `item_line`: quantity 1 shows just the name (no `"1 x "`).
            - `summary`: `tax = (subtotal - discount) * tax_rate` and
              `total = subtotal - discount + tax`. Round only when displaying (the `money` format does it).

            ## Examples
            ```python
            money(1234.5)      # returns "$1,234.50"
            money(3)           # returns "$3.00"
            money(-2)          # returns "-$2.00"
            row("Flat white", 4.5)
            # returns "Flat white                 $4.50"
            header("Bean There")
            # returns "********** BEAN THERE **********"
            from datetime import date
            stamp(42, date(2026, 9, 28))   # returns "Receipt #000042 | 28 Sep 2026"
            item_line("Croissant", 3, 2.8)
            # returns "3 x Croissant              $8.40"
            print(summary(20.0, 2.0, 0.08))
            ```
            prints:
            ```
            --------------------------------
            Subtotal                  $20.00
            Discount                  -$2.00
            Tax (8.0%)                 $1.44
            TOTAL                     $19.44
            ```

            ## You'll need to find out
            - how to **centre** a value inside a fixed width and fill the empty space with a character
              of your choice (not just spaces) - it's part of the format spec mini-language
            - how to format a **date** inside an f-string, choosing which parts (day, month name, year)
              are shown - look for the date format codes in the `datetime` docs

            ## Try it yourself
            At the bottom of `app.py`:
            ```python
            from datetime import date
            print(header("Bean There"))
            print(stamp(42, date(2026, 9, 28)))
            print(item_line("Flat white", 2, 4.5))
            print(summary(9.0, 0, 0.08))
            ```
            Press **Run** and check every line is exactly 32 characters wide.
        ''',
        "explore": r'''
            - Add a `footer(message)` that centres a thank-you message between `=` signs.
            - Show the tip suggestions (15%, 18%, 20%) as three rows under the total.
            - Once you know lists and loops: write `receipt(shop, items)` that prints a whole
              receipt from a list of `(name, qty, price)` tuples.
        ''',
        "rubric": [
            "row is the single place that knows the column widths; item_line and summary reuse it",
            "Widths (20, 12, 32) come from named constants or are clearly consistent",
            "money handles the negative case with a clear condition",
            "No manual space counting like ' ' * n where a format spec does the job",
        ],
        "starter_files": {"app.py": r'''
            # Café Receipt Printer - every line is 32 characters wide.


            def money(amount):
                ...
        '''},
        "solution_files": {"app.py": r'''
            # Café Receipt Printer - every line is 32 characters wide.

            WIDTH = 32
            LABEL_WIDTH = 20
            PRICE_WIDTH = 12


            def money(amount):
                if amount < 0:
                    return f"-${-amount:,.2f}"
                return f"${amount:,.2f}"


            def row(label, amount):
                return f"{label:<{LABEL_WIDTH}.{LABEL_WIDTH}}{money(amount):>{PRICE_WIDTH}}"


            def header(shop):
                name = f" {shop.upper()} "
                return f"{name:*^{WIDTH}}"


            def stamp(number, day):
                return f"Receipt #{number:06} | {day:%d %b %Y}"


            def item_line(name, qty, unit_price):
                label = name if qty == 1 else f"{qty} x {name}"
                return row(label, qty * unit_price)


            def summary(subtotal, discount, tax_rate):
                taxable = subtotal - discount
                tax = taxable * tax_rate
                text = "-" * WIDTH + "\n" + row("Subtotal", subtotal) + "\n"
                if discount > 0:
                    text += row("Discount", -discount) + "\n"
                text += row(f"Tax ({tax_rate:.1%})", tax) + "\n"
                text += row("TOTAL", taxable + tax)
                return text
        '''},
        "tests": r'''
            from datetime import date
            from app import money, row, header, stamp, item_line, summary


            def test_money_has_dollar_commas_and_two_decimals():
                for amount, want in ((1234.5, "$1,234.50"), (3, "$3.00"), (0.456, "$0.46"),
                                     (1000000, "$1,000,000.00")):
                    got = money(amount)
                    assert got == want, f"money({amount!r}) returned {got!r}"


            def test_money_puts_the_minus_before_the_dollar():
                got = money(-2)
                assert got == "-$2.00", f"money(-2) returned {got!r}"
                got = money(-1500.25)
                assert got == "-$1,500.25", f"money(-1500.25) returned {got!r}"


            def test_row_is_32_characters_with_price_on_the_right():
                got = row("Flat white", 4.5)
                assert got == "Flat white                 $4.50", f"row('Flat white', 4.5) returned {got!r}"
                assert len(got) == 32, f"row is {len(got)} characters wide"


            def test_row_cuts_long_labels_to_20_characters():
                got = row("Extra large oat milk cappuccino", 6)
                assert got == "Extra large oat milk       $6.00", f"row returned {got!r}"


            def test_header_centres_the_capitalised_name_in_stars():
                got = header("Bean There")
                assert got == "********** BEAN THERE **********", f"header('Bean There') returned {got!r}"


            def test_header_puts_the_odd_star_on_the_right():
                got = header("Tea")
                assert got == "************* TEA **************", f"header('Tea') returned {got!r}"
                assert len(got) == 32, f"header is {len(got)} characters wide"


            def test_header_with_a_very_long_name_has_no_stars():
                name = "The Extremely Long Named Coffee House"
                got = header(name)
                assert got == " " + name.upper() + " ", f"header({name!r}) returned {got!r}"


            def test_stamp_pads_number_and_formats_the_date():
                got = stamp(42, date(2026, 9, 28))
                assert got == "Receipt #000042 | 28 Sep 2026", f"stamp(42, date(2026, 9, 28)) returned {got!r}"
                got = stamp(7, date(2025, 1, 5))
                assert got == "Receipt #000007 | 05 Jan 2025", f"stamp(7, date(2025, 1, 5)) returned {got!r}"


            def test_item_line_with_one_item_shows_just_the_name():
                got = item_line("Flat white", 1, 4.5)
                assert got == "Flat white                 $4.50", f"item_line('Flat white', 1, 4.5) returned {got!r}"


            def test_item_line_with_several_items_shows_quantity_and_total_price():
                got = item_line("Croissant", 3, 2.8)
                assert got == "3 x Croissant              $8.40", f"item_line('Croissant', 3, 2.8) returned {got!r}"


            def test_item_line_cuts_a_long_label():
                got = item_line("Blueberry muffin deluxe", 12, 3.25)
                assert got == "12 x Blueberry muffi      $39.00", f"item_line returned {got!r}"


            def test_summary_with_discount():
                got = summary(20.0, 2.0, 0.08)
                want = "\n".join([
                    "-" * 32,
                    "Subtotal                  $20.00",
                    "Discount                  -$2.00",
                    "Tax (8.0%)                 $1.44",
                    "TOTAL                     $19.44",
                ])
                assert got == want, "summary(20.0, 2.0, 0.08) returned:\n" + repr(got)


            def test_summary_without_discount_has_no_discount_line():
                got = summary(9.0, 0, 0.1)
                want = "\n".join([
                    "-" * 32,
                    "Subtotal                   $9.00",
                    "Tax (10.0%)                $0.90",
                    "TOTAL                      $9.90",
                ])
                assert got == want, "summary(9.0, 0, 0.1) returned:\n" + repr(got)
                assert not got.endswith("\n"), "summary should not end with a newline"


            def test_functions_return_without_printing():
                for fn, args in ((money, (1,)), (row, ("a", 1)), (header, ("x",)),
                                 (item_line, ("a", 2, 1)), (summary, (1, 0, 0.1))):
                    value, out = capture(fn, *args)
                    assert out == "", f"{fn.__name__} printed {out!r} - it should return a string"
                    assert isinstance(value, str), f"{fn.__name__} returned {value!r}"
        ''',
    },
]
