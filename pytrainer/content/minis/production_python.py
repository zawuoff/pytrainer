"""Chapter projects for the production-python module (classes .. async)."""

# ---------------------------------------------------------------------------
# classes: Pocket Pets
# ---------------------------------------------------------------------------

_PETS_SOLUTION = r'''
class Pet:
    species = "pet"

    def __init__(self, name):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("a pet needs a name")
        self.name = name.strip()
        self.hunger = 50
        self.energy = 50
        self.happiness = 50
        self.age = 0

    def _change(self, hunger=0, energy=0, happiness=0):
        self.hunger = max(0, min(100, self.hunger + hunger))
        self.energy = max(0, min(100, self.energy + energy))
        self.happiness = max(0, min(100, self.happiness + happiness))

    def feed(self):
        self._change(hunger=-30, happiness=5)

    def play(self):
        if self.energy < 20:
            raise ValueError(f"{self.name} is too tired to play")
        self._change(hunger=10, energy=-20, happiness=15)

    def sleep(self):
        self._change(hunger=10, energy=40)

    def tick(self, hours=1):
        if hours < 0:
            raise ValueError("time only goes forward")
        self.age += hours
        self._change(hunger=5 * hours, energy=-3 * hours, happiness=-4 * hours)

    @property
    def mood(self):
        if self.hunger >= 80:
            return "hungry"
        if self.energy <= 20:
            return "sleepy"
        if self.happiness >= 70:
            return "happy"
        return "fine"

    def speak(self):
        raise NotImplementedError("each kind of pet makes its own sound")

    def __str__(self):
        return (f"{self.name} the {self.species} is {self.mood} "
                f"(hunger {self.hunger}, energy {self.energy}, happiness {self.happiness})")

    def __repr__(self):
        return f"{type(self).__name__}({self.name!r})"

    def __lt__(self, other):
        return self.happiness < other.happiness


class Dog(Pet):
    species = "dog"

    def speak(self):
        return "Woof!"

    def play(self):
        super().play()
        self._change(happiness=10)


class Cat(Pet):
    species = "cat"

    def speak(self):
        return "Meow."

    def sleep(self):
        super().sleep()
        self._change(happiness=5)


class Home:
    def __init__(self):
        self.pets = []

    def adopt(self, pet):
        if pet.name in self:
            raise ValueError(f"you already have a pet called {pet.name}")
        self.pets.append(pet)

    def __len__(self):
        return len(self.pets)

    def __contains__(self, name):
        return any(pet.name == name for pet in self.pets)

    def tick(self, hours=1):
        for pet in self.pets:
            pet.tick(hours)

    def ranking(self):
        return [pet.name for pet in sorted(self.pets, reverse=True)]

    def chorus(self):
        return " ".join(pet.speak() for pet in self.pets)


if __name__ == "__main__":
    home = Home()
    rex, tom = Dog("Rex"), Cat("Tom")
    home.adopt(rex)
    home.adopt(tom)
    rex.play()
    tom.feed()
    home.tick(3)
    for pet in home.pets:
        print(pet)
    print(home.ranking(), home.chorus())
'''

_PETS_TESTS = r'''
from app import Pet, Dog, Cat, Home


def stats(pet):
    return (pet.hunger, pet.energy, pet.happiness)


def test_new_pet_starts_at_50_50_50_and_age_0_with_a_stripped_name():
    p = Dog("  Rex ")
    assert p.name == "Rex", f"name should be stripped, got {p.name!r}"
    assert stats(p) == (50, 50, 50), f"(hunger, energy, happiness) = {stats(p)}, expected (50, 50, 50)"
    assert p.age == 0, f"age = {p.age!r}, expected 0"


def test_empty_or_blank_name_raises_value_error():
    for bad in ["", "   "]:
        try:
            Pet(bad)
        except ValueError:
            continue
        assert False, f"Pet({bad!r}) should raise ValueError"


def test_feed_play_and_sleep_change_the_stats():
    p = Pet("Bo")
    p.feed()
    assert stats(p) == (20, 50, 55), f"after feed(): {stats(p)}, expected (20, 50, 55)"
    p = Pet("Bo")
    p.play()
    assert stats(p) == (60, 30, 65), f"after play(): {stats(p)}, expected (60, 30, 65)"
    p = Pet("Bo")
    p.sleep()
    assert stats(p) == (60, 90, 50), f"after sleep(): {stats(p)}, expected (60, 90, 50)"
    assert p.feed() is None, "feed() should return None"


def test_stats_always_stay_between_0_and_100():
    p = Pet("Bo")
    for _ in range(5):
        p.feed()
    assert p.hunger == 0, f"hunger after 5 feeds = {p.hunger}, expected 0 (never below 0)"
    assert p.happiness == 75, f"happiness after 5 feeds = {p.happiness}, expected 75"
    p.sleep()
    p.sleep()
    assert p.energy == 100, f"energy after 2 sleeps = {p.energy}, expected 100 (never above 100)"
    p.tick(100)
    assert stats(p) == (100, 0, 0), f"after tick(100): {stats(p)}, expected (100, 0, 0)"


def test_play_when_too_tired_raises_value_error_and_changes_nothing():
    p = Pet("Bo")
    p.play()
    p.play()          # energy 50 -> 30 -> 10
    before = stats(p)
    try:
        p.play()
    except ValueError as err:
        assert str(err) == "Bo is too tired to play", f"message was {str(err)!r}"
    else:
        assert False, "play() with energy 10 should raise ValueError"
    assert stats(p) == before, f"stats changed from {before} to {stats(p)} on a failed play()"


def test_tick_changes_stats_per_hour_and_ages_the_pet():
    p = Pet("Bo")
    p.tick(2)
    assert stats(p) == (60, 44, 42), f"after tick(2): {stats(p)}, expected (60, 44, 42)"
    assert p.age == 2, f"age after tick(2) = {p.age}, expected 2"
    p.tick()
    assert p.age == 3, "tick() with no argument should mean 1 hour"
    try:
        p.tick(-1)
    except ValueError:
        pass
    else:
        assert False, "tick(-1) should raise ValueError"


def test_mood_is_a_property_checked_hungry_then_sleepy_then_happy_then_fine():
    p = Pet("Bo")
    assert p.mood == "fine", f"new pet mood = {p.mood!r}, expected 'fine' (mood is an attribute, not a method)"
    p.hunger, p.energy, p.happiness = 80, 10, 90
    assert p.mood == "hungry", f"hunger 80 -> expected 'hungry', got {p.mood!r}"
    p.hunger = 79
    assert p.mood == "sleepy", f"energy 10 -> expected 'sleepy', got {p.mood!r}"
    p.energy = 21
    assert p.mood == "happy", f"happiness 90 -> expected 'happy', got {p.mood!r}"
    p.happiness = 69
    assert p.mood == "fine", f"expected 'fine', got {p.mood!r}"


def test_base_pet_speak_raises_not_implemented_and_dog_and_cat_speak():
    try:
        Pet("Bo").speak()
    except NotImplementedError:
        pass
    else:
        assert False, "Pet.speak() should raise NotImplementedError"
    assert Dog("Rex").speak() == "Woof!"
    assert Cat("Tom").speak() == "Meow."
    assert (Pet.species, Dog.species, Cat.species) == ("pet", "dog", "cat"), "species class attributes"
    assert isinstance(Dog("Rex"), Pet) and isinstance(Cat("Tom"), Pet), "Dog and Cat must inherit from Pet"


def test_dog_play_and_cat_sleep_give_bonus_happiness():
    d = Dog("Rex")
    d.play()
    assert stats(d) == (60, 30, 75), f"Dog after play(): {stats(d)}, expected (60, 30, 75)"
    c = Cat("Tom")
    c.sleep()
    assert stats(c) == (60, 90, 55), f"Cat after sleep(): {stats(c)}, expected (60, 90, 55)"
    c.play()
    assert stats(c) == (70, 70, 70), f"Cat play() is a normal play: {stats(c)}, expected (70, 70, 70)"


def test_str_and_repr():
    d = Dog("Rex")
    assert str(d) == "Rex the dog is fine (hunger 50, energy 50, happiness 50)", f"str: {str(d)!r}"
    c = Cat("Tom")
    c.hunger = 90
    assert str(c) == "Tom the cat is hungry (hunger 90, energy 50, happiness 50)", f"str: {str(c)!r}"
    assert repr(d) == "Dog('Rex')", f"repr: {repr(d)!r}"
    assert repr(Cat("Tom")) == "Cat('Tom')", f"repr: {repr(Cat('Tom'))!r}"
    assert repr(Pet("Bo")) == "Pet('Bo')", f"repr: {repr(Pet('Bo'))!r}"


def test_pets_compare_by_happiness_so_sorted_works():
    a, b, c = Pet("A"), Pet("B"), Pet("C")
    a.happiness, b.happiness, c.happiness = 70, 10, 40
    assert (b < a) is True and (a < b) is False, "a < b should compare happiness"
    got = [p.name for p in sorted([a, b, c])]
    assert got == ["B", "C", "A"], f"sorted order {got}, expected least happy first ['B', 'C', 'A']"


def test_home_adopt_len_and_in():
    home = Home()
    assert len(home) == 0 and home.pets == [], "a new Home is empty"
    rex = Dog("Rex")
    assert home.adopt(rex) is None, "adopt() returns None"
    home.adopt(Cat("Tom"))
    assert len(home) == 2, f"len(home) = {len(home)}, expected 2"
    assert home.pets[0] is rex, "pets keeps adoption order"
    assert "Rex" in home and "Tom" in home, "'Rex' in home should be True"
    assert "Max" not in home, "'Max' in home should be False"
    try:
        home.adopt(Pet("Rex"))
    except ValueError as err:
        assert str(err) == "you already have a pet called Rex", f"message was {str(err)!r}"
    else:
        assert False, "adopting a second pet called Rex should raise ValueError"
    assert len(home) == 2, "the duplicate must not be added"


def test_home_tick_ranking_and_chorus():
    home = Home()
    assert home.chorus() == "", "empty home chorus is ''"
    rex, tom, bo = Dog("Rex"), Cat("Tom"), Dog("Bo")
    for p in (rex, tom, bo):
        home.adopt(p)
    rex.play()                       # happiness 75
    home.tick(2)                     # everyone -8 happiness
    assert rex.age == tom.age == bo.age == 2, "home.tick(2) ticks every pet"
    assert (rex.happiness, tom.happiness, bo.happiness) == (67, 42, 42)
    assert home.ranking() == ["Rex", "Tom", "Bo"], f"ranking {home.ranking()}: happiest first, ties in adoption order"
    assert home.chorus() == "Woof! Meow. Woof!", f"chorus {home.chorus()!r}"
'''

_PETS_STARTER = r'''# Pocket Pets - build your classes here. Delete the "..." and write real code.


class Pet:
    species = "pet"

    def __init__(self, name):
        ...


class Dog(Pet):
    ...


class Cat(Pet):
    ...


class Home:
    ...
'''

# ---------------------------------------------------------------------------
# dataclasses: Recipe Box
# ---------------------------------------------------------------------------

_RECIPE_SOLUTION = r'''
from dataclasses import dataclass, field, asdict, replace
from enum import Enum


class Difficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass(frozen=True)
class Ingredient:
    name: str
    qty: float
    unit: str = ""

    def __post_init__(self):
        if self.qty <= 0:
            raise ValueError("qty must be positive")


def fmt_qty(qty: float) -> str:
    return f"{round(qty, 2):g}"


@dataclass
class Recipe:
    title: str
    servings: int
    ingredients: list[Ingredient] = field(default_factory=list)
    difficulty: Difficulty = Difficulty.EASY
    tags: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.title = self.title.strip()
        if not self.title:
            raise ValueError("title can't be empty")
        if self.servings < 1:
            raise ValueError("servings must be at least 1")
        self.difficulty = Difficulty(self.difficulty)

    def scaled(self, servings: int) -> "Recipe":
        if servings < 1:
            raise ValueError("servings must be at least 1")
        factor = servings / self.servings
        items = [replace(i, qty=round(i.qty * factor, 2)) for i in self.ingredients]
        return replace(self, servings=servings, ingredients=items, tags=list(self.tags))

    def card(self) -> str:
        lines = [f"{self.title} (serves {self.servings}, {self.difficulty.value})"]
        for i in self.ingredients:
            if i.unit:
                lines.append(f"- {fmt_qty(i.qty)} {i.unit} {i.name}")
            else:
                lines.append(f"- {fmt_qty(i.qty)} {i.name}")
        if self.tags:
            lines.append("Tags: " + ", ".join(self.tags))
        return "\n".join(lines)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["difficulty"] = self.difficulty.value
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Recipe":
        items = [Ingredient(d["name"], d["qty"], d.get("unit", "")) for d in data.get("ingredients", [])]
        return cls(data["title"], data["servings"], items,
                   data.get("difficulty", "easy"), list(data.get("tags", [])))


def sort_recipes(recipes: list[Recipe]) -> list[Recipe]:
    order = list(Difficulty)
    return sorted(recipes, key=lambda r: (order.index(r.difficulty), r.title))


def shopping_list(recipes: list[Recipe]) -> list[Ingredient]:
    totals: dict[tuple[str, str], float] = {}
    for recipe in recipes:
        for i in recipe.ingredients:
            key = (i.name, i.unit)
            totals[key] = totals.get(key, 0) + i.qty
    return [Ingredient(name, round(qty, 2), unit) for (name, unit), qty in sorted(totals.items())]


if __name__ == "__main__":
    pancakes = Recipe("Pancakes", 4, [Ingredient("flour", 200, "g"), Ingredient("egg", 2),
                                      Ingredient("milk", 0.5, "l")], "easy", ["breakfast", "sweet"])
    print(pancakes.card())
    print(pancakes.scaled(2).card())
'''

_RECIPE_TESTS = r'''
import json
import dataclasses
from app import Difficulty, Ingredient, Recipe, fmt_qty, sort_recipes, shopping_list


def pancakes():
    return Recipe("Pancakes", 4,
                  [Ingredient("flour", 200, "g"), Ingredient("egg", 2), Ingredient("milk", 0.5, "l")],
                  "easy", ["breakfast", "sweet"])


def raises(exc, fn, *args):
    try:
        fn(*args)
    except exc:
        return True
    return False


def test_difficulty_enum_has_easy_medium_hard():
    assert [d.value for d in Difficulty] == ["easy", "medium", "hard"], \
        f"values in order: {[d.value for d in Difficulty]}"
    assert Difficulty.HARD.name == "HARD"


def test_ingredient_is_a_frozen_dataclass_with_unit_defaulting_to_empty():
    assert dataclasses.is_dataclass(Ingredient), "Ingredient must be a @dataclass"
    assert [f.name for f in dataclasses.fields(Ingredient)] == ["name", "qty", "unit"], "fields in order: name, qty, unit"
    egg = Ingredient("egg", 2)
    assert egg.unit == "", f"default unit should be '', got {egg.unit!r}"
    assert Ingredient("egg", 2) == egg, "== comes from @dataclass"
    assert raises(dataclasses.FrozenInstanceError, setattr, egg, "qty", 3), "Ingredient must be frozen"


def test_ingredient_qty_must_be_positive():
    assert raises(ValueError, Ingredient, "egg", 0), "qty 0 should raise ValueError"
    assert raises(ValueError, Ingredient, "egg", -1), "qty -1 should raise ValueError"


def test_recipe_fields_defaults_and_no_shared_lists():
    assert [f.name for f in dataclasses.fields(Recipe)] == ["title", "servings", "ingredients", "difficulty", "tags"]
    a, b = Recipe("Toast", 1), Recipe("Tea", 1)
    assert a.ingredients == [] and a.tags == [], "ingredients and tags default to empty lists"
    assert a.difficulty is Difficulty.EASY, f"default difficulty should be Difficulty.EASY, got {a.difficulty!r}"
    a.tags.append("quick")
    assert b.tags == [], "two recipes must not share one tags list (use a default factory)"


def test_recipe_validates_and_converts_in_post_init():
    r = Recipe("  Chili  ", 6, difficulty="hard")
    assert r.title == "Chili", f"title should be stripped, got {r.title!r}"
    assert r.difficulty is Difficulty.HARD, f"'hard' should become Difficulty.HARD, got {r.difficulty!r}"
    assert Recipe("Chili", 6, difficulty=Difficulty.MEDIUM).difficulty is Difficulty.MEDIUM
    assert raises(ValueError, Recipe, "   ", 2), "a blank title should raise ValueError"
    assert raises(ValueError, Recipe, "Chili", 0), "servings 0 should raise ValueError"
    assert raises(ValueError, Recipe, "Chili", 2, [], "extreme"), "an unknown difficulty should raise ValueError"


def test_fmt_qty_drops_trailing_zeros():
    cases = {2: "2", 2.0: "2", 200: "200", 0.5: "0.5", 1.25: "1.25", 0.333333: "0.33", 1.10: "1.1"}
    for qty, want in cases.items():
        assert fmt_qty(qty) == want, f"fmt_qty({qty!r}) = {fmt_qty(qty)!r}, expected {want!r}"


def test_card_text():
    want = "Pancakes (serves 4, easy)\n- 200 g flour\n- 2 egg\n- 0.5 l milk\nTags: breakfast, sweet"
    got = pancakes().card()
    assert got == want, f"card() returned:\n{got}\n\nexpected:\n{want}"
    plain = Recipe("Water", 1, [Ingredient("water", 0.25, "l")], "easy").card()
    assert plain == "Water (serves 1, easy)\n- 0.25 l water", f"no Tags line without tags, got:\n{plain}"


def test_scaled_returns_a_new_recipe_and_leaves_the_original_alone():
    p = pancakes()
    half = p.scaled(2)
    assert isinstance(half, Recipe) and half is not p
    assert half.servings == 2
    assert half.ingredients == [Ingredient("flour", 100, "g"), Ingredient("egg", 1), Ingredient("milk", 0.25, "l")], \
        f"scaled ingredients: {half.ingredients}"
    assert p == pancakes(), "the original recipe must not change"
    half.tags.append("mini")
    assert p.tags == ["breakfast", "sweet"], "the scaled copy must not share its tags list with the original"
    third = Recipe("Dip", 3, [Ingredient("yogurt", 1, "cup")]).scaled(1)
    assert third.ingredients[0].qty == 0.33, f"quantities are rounded to 2 decimals, got {third.ingredients[0].qty}"
    assert raises(ValueError, p.scaled, 0), "scaled(0) should raise ValueError"


def test_to_dict_is_json_ready():
    d = pancakes().to_dict()
    assert d == {
        "title": "Pancakes", "servings": 4,
        "ingredients": [{"name": "flour", "qty": 200, "unit": "g"}, {"name": "egg", "qty": 2, "unit": ""},
                        {"name": "milk", "qty": 0.5, "unit": "l"}],
        "difficulty": "easy", "tags": ["breakfast", "sweet"],
    }, f"to_dict() returned {d}"
    json.dumps(d)


def test_from_dict_builds_recipes_and_round_trips():
    r = Recipe.from_dict({"title": "Toast", "servings": 1, "ingredients": [{"name": "bread", "qty": 2}]})
    assert r == Recipe("Toast", 1, [Ingredient("bread", 2, "")]), f"from_dict gave {r}"
    assert r.difficulty is Difficulty.EASY and r.tags == []
    p = pancakes()
    back = Recipe.from_dict(json.loads(json.dumps(p.to_dict())))
    assert back == p, f"round trip changed the recipe: {back}"
    assert isinstance(back.ingredients[0], Ingredient), "ingredients must become Ingredient objects"


def test_sort_recipes_by_difficulty_then_title():
    rs = [Recipe("Soufflé", 2, difficulty="hard"), Recipe("Toast", 1), Recipe("Risotto", 4, difficulty="medium"),
          Recipe("Salad", 2), Recipe("Beef Wellington", 6, difficulty="hard")]
    before = list(rs)
    got = [r.title for r in sort_recipes(rs)]
    assert got == ["Salad", "Toast", "Risotto", "Beef Wellington", "Soufflé"], f"sorted titles: {got}"
    assert rs == before, "sort_recipes must not reorder the list you pass in"


def test_shopping_list_merges_same_name_and_unit():
    omelette = Recipe("Omelette", 1, [Ingredient("egg", 3), Ingredient("milk", 0.1, "l"),
                                      Ingredient("cheese", 50, "g"), Ingredient("milk", 100, "ml")])
    got = shopping_list([pancakes(), omelette])
    want = [Ingredient("cheese", 50, "g"), Ingredient("egg", 5, ""), Ingredient("flour", 200, "g"),
            Ingredient("milk", 0.6, "l"), Ingredient("milk", 100, "ml")]
    assert got == want, f"shopping_list returned {got}"
    assert shopping_list([]) == []
'''

_RECIPE_STARTER = r'''# Recipe Box - your typed recipe book. Replace every "..." with real code.
from dataclasses import dataclass, field
from enum import Enum


class Difficulty(Enum):
    ...


class Ingredient:
    ...


def fmt_qty(qty):
    ...


class Recipe:
    ...


def sort_recipes(recipes):
    ...


def shopping_list(recipes):
    ...
'''

# ---------------------------------------------------------------------------
# testing: Bug Hunt at the Bistro
# ---------------------------------------------------------------------------

_BILL_APP = '''"""Split a restaurant bill between friends. All money is handled in whole cents (ints)."""


def to_cents(text):
    """Turn a typed amount like "12.50", "$12.50" or " 7 " into cents (1250, 1250, 700).

    Raises ValueError for text that isn't a number and for negative amounts.
    """
    cleaned = text.strip().removeprefix("$")
    value = float(cleaned)
    if value < 0:
        raise ValueError(f"negative amount: {text!r}")
    return round(value * 100)


def split_evenly(total_cents, people):
    """Split total_cents into `people` shares that add up exactly to total_cents.

    Shares differ by at most 1 cent and the bigger shares come first:
    split_evenly(1000, 3) -> [334, 333, 333]. Raises ValueError if people < 1.
    """
    if people < 1:
        raise ValueError("need at least one person")
    share, leftover = divmod(total_cents, people)
    return [share + 1] * leftover + [share] * (people - leftover)


def add_tip(total_cents, percent):
    """Return the total with a tip of `percent` % added, rounded with round().

    add_tip(1000, 15) -> 1150. Raises ValueError if percent is negative.
    """
    if percent < 0:
        raise ValueError("tip can't be negative")
    return round(total_cents * (100 + percent) / 100)


def convert(cents, currency, get_rate):
    """Convert USD cents into `currency`, using get_rate(currency) -> a float rate.

    For "USD" the amount is returned unchanged and get_rate is NOT called
    (rate lookups are slow and cost money). Otherwise: round(cents * rate).
    """
    if currency == "USD":
        return cents
    return round(cents * get_rate(currency))
'''

_BUG_LEFTOVER = ("return [share + 1] * leftover + [share] * (people - leftover)", "return [share] * people")
_BUG_NEGATIVE = ('    if value < 0:\n        raise ValueError(f"negative amount: {text!r}")\n', "")

_BILL_BUGGY = _BILL_APP.replace(*_BUG_LEFTOVER).replace(*_BUG_NEGATIVE)
assert _BILL_BUGGY.count("divmod") == 1 and "negative amount" not in _BILL_BUGGY.split('"""', 4)[4]

_BILL_TESTS_SOLUTION = r'''from app import to_cents, split_evenly, add_tip, convert


def raises(exc, fn, *args):
    try:
        fn(*args)
    except exc:
        return True
    return False


def test_to_cents_plain_dollar_sign_and_spaces():
    assert to_cents("12.50") == 1250
    assert to_cents("$12.50") == 1250
    assert to_cents(" 7 ") == 700


def test_to_cents_rejects_garbage_and_negative():
    assert raises(ValueError, to_cents, "twelve")
    assert raises(ValueError, to_cents, "")
    assert raises(ValueError, to_cents, "-5")


def test_split_evenly_adds_up_with_bigger_shares_first():
    assert split_evenly(1000, 3) == [334, 333, 333]
    assert split_evenly(10, 4) == [3, 3, 2, 2]
    assert split_evenly(900, 3) == [300, 300, 300]
    assert split_evenly(5, 1) == [5]


def test_split_evenly_needs_at_least_one_person():
    assert raises(ValueError, split_evenly, 100, 0)
    assert raises(ValueError, split_evenly, 100, -2)


def test_add_tip_rounds_to_nearest_cent():
    assert add_tip(1000, 15) == 1150
    assert add_tip(999, 15) == 1149          # 1148.85 rounds up
    assert add_tip(1000, 0) == 1000
    assert raises(ValueError, add_tip, 1000, -5)


def make_fake_rates(rates):
    calls = []

    def get_rate(currency):
        calls.append(currency)
        return rates[currency]

    return get_rate, calls


def test_convert_uses_the_rate():
    get_rate, calls = make_fake_rates({"EUR": 0.9})
    assert convert(1000, "EUR", get_rate) == 900
    assert calls == ["EUR"]


def test_convert_usd_never_calls_get_rate():
    get_rate, calls = make_fake_rates({})
    assert convert(1234, "USD", get_rate) == 1234
    assert calls == []
'''

_BILL_STARTER_TESTS = r'''from app import to_cents, split_evenly, add_tip, convert


def test_to_cents_plain_number():
    # Arrange, act, assert - then write many more tests like this one.
    ...
'''

_BILL_HIDDEN_TESTS = r'''
import sys
import types
from app import to_cents, split_evenly, add_tip, convert

CORRECT = @@CORRECT@@


def _module_from(src):
    mod = types.ModuleType("app")
    mod.__file__ = "app.py"
    exec(compile(src, "app.py", "exec"), mod.__dict__)
    return mod


def _run_your_tests(app_src):
    """Import test_app.py against `app_src` and run every test_ function in it."""
    saved = sys.modules.get("app")
    sys.modules["app"] = _module_from(app_src)
    try:
        mod = load("test_app")
        results = {}
        for name, fn in list(vars(mod).items()):
            if name.startswith("test_") and callable(fn) and getattr(fn, "__module__", "") == "test_app":
                try:
                    fn()
                    results[name] = None
                except BaseException as exc:
                    results[name] = f"{type(exc).__name__}: {exc}"
        return results
    finally:
        if saved is not None:
            sys.modules["app"] = saved
        else:
            sys.modules.pop("app", None)
        sys.modules.pop("test_app", None)


def _mutant(old, new):
    assert CORRECT.count(old) == 1, "grader problem: mutation not found"
    return CORRECT.replace(old, new)


def _require_green():
    results = _run_your_tests(CORRECT)
    assert results, "No test functions found in test_app.py - name them test_something."
    failing = {k: v for k, v in results.items() if v is not None}
    assert not failing, "Fix your tests so they pass on correct code first: " + "; ".join(
        f"{k}: {v}" for k, v in failing.items())


def _assert_caught(old, new, bug):
    _require_green()
    results = _run_your_tests(_mutant(old, new))
    assert any(v is not None for v in results.values()), (
        f"All your tests still pass when this bug is planted: {bug}. Add a test that would notice it.")


def _raises(exc, fn, *args):
    try:
        fn(*args)
    except exc:
        return True
    return False


def test_app_py_to_cents_bug_is_fixed_negative_amounts_raise():
    assert to_cents("$12.50") == 1250 and to_cents(" 7 ") == 700, "to_cents parsing broke"
    assert _raises(ValueError, to_cents, "-5"), "to_cents('-5') should raise ValueError"
    assert _raises(ValueError, to_cents, "abc"), "to_cents('abc') should raise ValueError"


def test_app_py_split_evenly_bug_is_fixed_shares_add_up():
    assert split_evenly(1000, 3) == [334, 333, 333], f"split_evenly(1000, 3) = {split_evenly(1000, 3)}"
    assert split_evenly(10, 4) == [3, 3, 2, 2], f"split_evenly(10, 4) = {split_evenly(10, 4)}"
    assert split_evenly(5, 1) == [5]
    assert _raises(ValueError, split_evenly, 100, 0), "split_evenly(100, 0) should raise ValueError"


def test_app_py_add_tip_and_convert_still_work():
    assert add_tip(1000, 15) == 1150 and add_tip(999, 15) == 1149
    assert _raises(ValueError, add_tip, 100, -1)
    calls = []
    assert convert(1000, "EUR", lambda c: calls.append(c) or 0.9) == 900 and calls == ["EUR"]
    assert convert(500, "USD", lambda c: calls.append(c) or 2.0) == 500 and calls == ["EUR"]


def test_test_app_py_has_at_least_6_test_functions():
    results = _run_your_tests(CORRECT)
    assert len(results) >= 6, f"found {len(results)} test_ function(s) in test_app.py, need at least 6"


def test_your_tests_all_pass_on_correct_code():
    _require_green()


def test_your_tests_catch_leftover_cents_being_dropped():
    _assert_caught("return [share + 1] * leftover + [share] * (people - leftover)", "return [share] * people",
                   "split_evenly ignores the leftover cents, so shares don't add up to the total")


def test_your_tests_catch_negative_amounts_being_accepted():
    _assert_caught('    if value < 0:\n        raise ValueError(f"negative amount: {text!r}")\n', "",
                   "to_cents('-5') returns -500 instead of raising ValueError")


def test_your_tests_catch_the_dollar_sign_not_being_removed():
    _assert_caught('.removeprefix("$")', "", "to_cents('$12.50') crashes because the $ is not removed")


def test_your_tests_catch_zero_people_not_raising_value_error():
    _assert_caught("if people < 1:", "if people < 0:",
                   "split_evenly(100, 0) crashes with ZeroDivisionError instead of raising ValueError")


def test_your_tests_catch_the_tip_being_rounded_down():
    _assert_caught("return round(total_cents * (100 + percent) / 100)", "return int(total_cents * (100 + percent) / 100)",
                   "add_tip always rounds down (1148.85 becomes 1148 instead of 1149)")


def test_your_tests_catch_convert_calling_get_rate_for_usd():
    _assert_caught('    if currency == "USD":\n        return cents\n',
                   '    if currency == "USD":\n        get_rate(currency)\n        return cents\n',
                   "convert still calls get_rate for USD (wasting a paid lookup)")
'''.replace("@@CORRECT@@", repr(_BILL_APP))

# ---------------------------------------------------------------------------
# generators: Log Detective
# ---------------------------------------------------------------------------

_LOG_SOLUTION = r'''
import sys
from collections import deque
from itertools import groupby

LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")


def read_log(path):
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip()
            if line:
                yield line


def parse(lines):
    for line in lines:
        parts = line.split(maxsplit=4)
        if len(parts) != 5:
            continue
        date, time, level, source, message = parts
        if level not in LEVELS or not source.endswith(":") or len(source) < 2:
            continue
        yield {"date": date, "time": time, "level": level, "source": source[:-1], "message": message}


def at_least(records, level):
    if level not in LEVELS:
        raise ValueError(f"unknown level: {level}")
    floor = LEVELS.index(level)
    return (r for r in records if LEVELS.index(r["level"]) >= floor)


def tail(items, n):
    if n <= 0:
        return []
    return list(deque(items, maxlen=n))


def incidents(records, min_count=3):
    for is_error, group in groupby(records, key=lambda r: r["level"] == "ERROR"):
        if not is_error:
            continue
        run = list(group)
        if len(run) >= min_count:
            yield {"start": run[0]["time"], "end": run[-1]["time"], "count": len(run),
                   "sources": sorted({r["source"] for r in run})}


def summary(path):
    levels = {level: 0 for level in LEVELS}
    for record in parse(read_log(path)):
        levels[record["level"]] += 1
    errors = at_least(parse(read_log(path)), "ERROR")
    return {
        "records": sum(levels.values()),
        "levels": levels,
        "last_errors": [r["message"] for r in tail(errors, 3)],
        "incidents": sum(1 for _ in incidents(parse(read_log(path)))),
    }


if __name__ == "__main__":
    print(summary(sys.argv[1]))
'''

_LOG_TESTS = r'''
import inspect
import itertools
from app import LEVELS, read_log, parse, at_least, tail, incidents, summary

SAMPLE = """2026-09-28 09:00:00 INFO web: server started
2026-09-28 09:00:05 DEBUG db: pool size 5

2026-09-28 09:01:00 WARNING web: slow response (1200 ms)
2026-09-28 09:02:00 ERROR payments: card declined
this line is garbage
2026-09-28 09:02:01 ERROR payments: card declined
   \t
2026-09-28 09:02:02 ERROR db: connection lost
2026-09-28 09:03:00 INFO web: recovered
2026-09-28 09:04:00 ERROR web: timeout
2026-09-28 09:04:01 LOUD web: not a real level
"""


def write(name, text):
    with open(name, "w", encoding="utf-8") as fh:
        fh.write(text)
    return name


def rec(level, source="web", time="10:00:00", message="m"):
    return {"date": "2026-09-28", "time": time, "level": level, "source": source, "message": message}


def endless_lines():
    for i in itertools.count():
        yield f"2026-09-28 10:00:{i % 60:02d} {'ERROR' if i % 5 < 3 else 'INFO'} svc{i % 2}: event {i}"


def test_levels_constant_in_order():
    assert tuple(LEVELS) == ("DEBUG", "INFO", "WARNING", "ERROR"), f"LEVELS = {LEVELS!r}"


def test_read_log_is_a_generator_yielding_non_blank_lines_without_newlines():
    path = write("t1.log", SAMPLE)
    gen = read_log(path)
    assert inspect.isgenerator(gen), "read_log must be a generator function (use yield)"
    lines = list(gen)
    assert len(lines) == 10, f"expected 10 non-blank lines, got {len(lines)}"
    assert lines[0] == "2026-09-28 09:00:00 INFO web: server started", f"first line: {lines[0]!r}"
    assert all(not l.endswith(("\n", " ", "\t")) for l in lines), "strip trailing whitespace/newlines"
    assert "   \t" not in lines and "" not in lines, "whitespace-only lines are skipped"


def test_parse_yields_record_dicts_and_skips_bad_lines():
    path = write("t2.log", SAMPLE)
    records = list(parse(read_log(path)))
    assert len(records) == 8, f"expected 8 valid records, got {len(records)}"
    assert records[0] == {"date": "2026-09-28", "time": "09:00:00", "level": "INFO",
                          "source": "web", "message": "server started"}, f"first record: {records[0]}"
    assert records[2]["message"] == "slow response (1200 ms)", "message is the whole rest of the line"
    assert all(r["level"] in LEVELS for r in records)


def test_parse_skips_lines_with_missing_parts_or_no_colon_after_the_source():
    lines = ["2026-09-28 09:00:00 INFO web: ok",
             "2026-09-28 09:00:00 INFO web ok no colon",
             "2026-09-28 09:00:00 INFO web:",
             "2026-09-28 09:00:00 INFO : lonely colon",
             "2026-09-28 09:00:00 info web: lowercase level"]
    got = list(parse(lines))
    assert [r["message"] for r in got] == ["ok"], f"only the first line is valid, got {got}"


def test_parse_is_lazy_and_works_on_an_endless_stream():
    gen = parse(endless_lines())
    assert inspect.isgenerator(gen), "parse must return a generator"
    first = list(itertools.islice(gen, 3))
    assert [r["message"] for r in first] == ["event 0", "event 1", "event 2"], f"got {first}"


def test_at_least_filters_by_level_order():
    rs = [rec("DEBUG"), rec("INFO"), rec("WARNING"), rec("ERROR"), rec("INFO")]
    assert [r["level"] for r in at_least(rs, "WARNING")] == ["WARNING", "ERROR"]
    assert [r["level"] for r in at_least(rs, "INFO")] == ["INFO", "WARNING", "ERROR", "INFO"]
    assert len(list(at_least(rs, "DEBUG"))) == 5
    assert inspect.isgenerator(at_least(rs, "INFO")), "at_least must return a generator"


def test_at_least_raises_value_error_right_away_for_an_unknown_level():
    try:
        at_least([], "LOUD")
    except ValueError:
        return
    assert False, "at_least([], 'LOUD') should raise ValueError at call time, before anything is read"


def test_at_least_is_lazy():
    errors = at_least(parse(endless_lines()), "ERROR")
    got = [r["message"] for r in itertools.islice(errors, 4)]
    assert got == ["event 0", "event 1", "event 2", "event 5"], f"got {got}"


def test_tail_returns_the_last_n_items_of_any_iterable():
    assert tail([1, 2, 3, 4, 5], 2) == [4, 5]
    assert tail(iter("abc"), 5) == ["a", "b", "c"], "fewer items than n: return them all"
    assert tail((x * x for x in range(1_000_000)), 3) == [999994000009, 999996000004, 999998000001]
    assert tail([1, 2], 0) == [] and tail([], 3) == []


def test_incidents_finds_runs_of_consecutive_errors():
    rs = [rec("ERROR", "db", "01"), rec("ERROR", "api", "02"), rec("ERROR", "db", "03"), rec("INFO", time="04"),
          rec("ERROR", time="05"), rec("ERROR", time="06"), rec("WARNING", time="07"),
          rec("ERROR", "b", "08"), rec("ERROR", "a", "09"), rec("ERROR", "b", "10"), rec("ERROR", "a", "11")]
    gen = incidents(rs)
    assert inspect.isgenerator(gen), "incidents must be a generator"
    assert list(gen) == [
        {"start": "01", "end": "03", "count": 3, "sources": ["api", "db"]},
        {"start": "08", "end": "11", "count": 4, "sources": ["a", "b"]},
    ], f"got {list(incidents(rs))}"
    assert [i["count"] for i in incidents(rs, min_count=2)] == [3, 2, 4], "min_count=2 also counts the run of 2"


def test_incidents_is_lazy_on_an_endless_stream():
    first = list(itertools.islice(incidents(parse(endless_lines())), 2))
    assert first == [
        {"start": "10:00:00", "end": "10:00:02", "count": 3, "sources": ["svc0", "svc1"]},
        {"start": "10:00:05", "end": "10:00:07", "count": 3, "sources": ["svc0", "svc1"]},
    ], f"got {first}"


def test_summary_of_a_log_file():
    path = write("t3.log", SAMPLE)
    assert summary(path) == {
        "records": 8,
        "levels": {"DEBUG": 1, "INFO": 2, "WARNING": 1, "ERROR": 4},
        "last_errors": ["card declined", "connection lost", "timeout"],
        "incidents": 1,
    }, f"summary returned {summary(path)}"


def test_summary_of_an_empty_file():
    path = write("t4.log", "")
    assert summary(path) == {"records": 0, "levels": {"DEBUG": 0, "INFO": 0, "WARNING": 0, "ERROR": 0},
                             "last_errors": [], "incidents": 0}, f"summary returned {summary(path)}"
'''

_LOG_STARTER = r'''# Log Detective - lazy log analysis with generators. Replace every "..." with real code.

LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")


def read_log(path):
    ...


def parse(lines):
    ...


def at_least(records, level):
    ...


def tail(items, n):
    ...


def incidents(records, min_count=3):
    ...


def summary(path):
    ...
'''

# ---------------------------------------------------------------------------
# async: Flight Scout
# ---------------------------------------------------------------------------

_FLIGHT_SOLUTION = r'''
import asyncio


async def gather_quotes(airlines, route, limit=3, timeout=1.0):
    if limit < 1:
        raise ValueError("limit must be at least 1")
    gate = asyncio.Semaphore(limit)

    async def one(name, quote):
        async with gate:
            try:
                return name, await asyncio.wait_for(quote(route), timeout), None
            except TimeoutError:
                return name, None, "timeout"
            except Exception as err:
                return name, None, f"{type(err).__name__}: {err}"

    results = await asyncio.gather(*(one(n, q) for n, q in airlines.items()))
    return {
        "prices": {n: p for n, p, e in results if e is None},
        "errors": {n: e for n, p, e in results if e is not None},
    }


def cheapest(prices):
    if not prices:
        return None
    name = min(prices, key=lambda n: (prices[n], n))
    return name, prices[name]


async def _tagged(name, quote, route):
    return name, await quote(route)


async def _first_success(tasks):
    for next_done in asyncio.as_completed(tasks):
        try:
            return await next_done
        except Exception:
            continue
    return None


async def first_quote(airlines, route, timeout=1.0):
    tasks = [asyncio.create_task(_tagged(n, q, route)) for n, q in airlines.items()]
    try:
        winner = await asyncio.wait_for(_first_success(tasks), timeout)
    except TimeoutError:
        winner = None
    finally:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
    if winner is None:
        raise LookupError(f"no quotes for {route}")
    return winner


async def live_quotes(airlines, route):
    tasks = [asyncio.create_task(_tagged(n, q, route)) for n, q in airlines.items()]
    for next_done in asyncio.as_completed(tasks):
        try:
            yield await next_done
        except Exception:
            continue


async def _demo():
    async def airline(price, delay):
        async def quote(route):
            await asyncio.sleep(delay)
            return price
        return quote

    airlines = {"SkyLow": await airline(89.0, 0.3), "JetFast": await airline(120.0, 0.1)}
    print(await gather_quotes(airlines, "AMS-LIS"))
    print(await first_quote(airlines, "AMS-LIS"))


if __name__ == "__main__":
    asyncio.run(_demo())
'''

_FLIGHT_TESTS = r'''
import asyncio
import inspect
import time
from app import gather_quotes, cheapest, first_quote, live_quotes


def airline(price, delay=0.01, error=None, finished=None, name=None):
    async def quote(route):
        await asyncio.sleep(delay)
        if error is not None:
            raise error
        if finished is not None:
            finished.append(name)
        return price
    return quote


def test_gather_quotes_returns_prices_and_errors_in_airline_order():
    assert inspect.iscoroutinefunction(gather_quotes), "gather_quotes must be an async def"
    airlines = {"b": airline(120.0, 0.03), "down": airline(0, 0.01, ConnectionError("server down")),
                "a": airline(89.5, 0.01), "c": airline(99.0, 0.02)}
    got = asyncio.run(gather_quotes(airlines, "AMS-LIS"))
    assert got == {"prices": {"b": 120.0, "a": 89.5, "c": 99.0},
                   "errors": {"down": "ConnectionError: server down"}}, f"got {got}"
    assert list(got["prices"]) == ["b", "a", "c"], "prices keys must follow the airlines order"


def test_gather_quotes_calls_each_airline_with_the_route():
    seen = []

    async def spy(route):
        seen.append(route)
        return 50.0

    asyncio.run(gather_quotes({"x": spy, "y": spy}, "BER-ROM"))
    assert seen == ["BER-ROM", "BER-ROM"], f"calls got routes {seen}"


def test_slow_airline_is_reported_as_timeout():
    airlines = {"snail": airline(10.0, 2.0), "hare": airline(80.0, 0.01)}
    start = time.perf_counter()
    got = asyncio.run(gather_quotes(airlines, "AMS-LIS", timeout=0.05))
    took = time.perf_counter() - start
    assert got == {"prices": {"hare": 80.0}, "errors": {"snail": "timeout"}}, f"got {got}"
    assert took < 1.0, f"took {took:.2f}s - the slow call should be cut off after the timeout"


def test_limit_below_1_raises_value_error():
    try:
        asyncio.run(gather_quotes({"a": airline(1.0)}, "AMS-LIS", limit=0))
    except ValueError:
        return
    assert False, "limit=0 should raise ValueError"


def test_never_more_than_limit_calls_at_once():
    state = {"now": 0, "max": 0}

    async def counted(route):
        state["now"] += 1
        state["max"] = max(state["max"], state["now"])
        await asyncio.sleep(0.02)
        state["now"] -= 1
        return 1.0

    got = asyncio.run(gather_quotes({f"a{i}": counted for i in range(6)}, "AMS-LIS", limit=2))
    assert len(got["prices"]) == 6, f"all 6 should succeed, got {got}"
    assert state["max"] == 2, f"at most 2 at once (and actually 2), but saw {state['max']} running together"


def test_calls_run_concurrently():
    airlines = {f"a{i}": airline(float(i), 0.1) for i in range(5)}
    start = time.perf_counter()
    asyncio.run(gather_quotes(airlines, "AMS-LIS", limit=5))
    took = time.perf_counter() - start
    assert took < 0.3, f"5 calls of 0.1s with limit=5 took {took:.2f}s - they should run at the same time"


def test_timeout_clock_starts_when_the_call_starts_not_while_waiting_for_a_slot():
    airlines = {f"a{i}": airline(float(i), 0.05) for i in range(4)}
    got = asyncio.run(gather_quotes(airlines, "AMS-LIS", limit=1, timeout=0.12))
    assert got["errors"] == {}, f"each call takes 0.05s < 0.12s, none should time out: {got['errors']}"
    assert len(got["prices"]) == 4


def test_cheapest_picks_lowest_price_ties_by_name_and_none_when_empty():
    assert cheapest({"b": 120.0, "a": 89.5, "c": 99.0}) == ("a", 89.5)
    assert cheapest({"zed": 50.0, "amy": 50.0, "kit": 70.0}) == ("amy", 50.0), "ties: alphabetically first name"
    assert cheapest({}) is None


def test_first_quote_returns_the_fastest_success_and_skips_failures():
    assert inspect.iscoroutinefunction(first_quote), "first_quote must be an async def"
    airlines = {"slow": airline(70.0, 0.15), "broken": airline(0, 0.01, ValueError("no seats")),
                "quick": airline(140.0, 0.04)}
    got = asyncio.run(first_quote(airlines, "AMS-LIS"))
    assert got == ("quick", 140.0), f"got {got!r}, expected ('quick', 140.0)"


def test_first_quote_cancels_the_calls_still_running():
    finished = []
    airlines = {"slow": airline(70.0, 0.15, finished=finished, name="slow"),
                "fast": airline(120.0, 0.01, finished=finished, name="fast")}

    async def main():
        got = await first_quote(airlines, "AMS-LIS")
        await asyncio.sleep(0.3)
        return got

    got = asyncio.run(main())
    assert got == ("fast", 120.0), f"got {got!r}"
    assert finished == ["fast"], f"'slow' still ran to the end ({finished}) - cancel the calls you no longer need"


def test_first_quote_raises_lookup_error_when_nobody_answers():
    failing = {"x": airline(0, 0.01, ConnectionError("down")), "y": airline(0, 0.02, ValueError("no"))}
    for airlines, timeout in [(failing, 1.0), ({}, 1.0), ({"snail": airline(1.0, 2.0)}, 0.05)]:
        start = time.perf_counter()
        try:
            asyncio.run(first_quote(airlines, "OSL-NAP", timeout=timeout))
        except LookupError as err:
            assert str(err) == "no quotes for OSL-NAP", f"message was {str(err)!r}"
        else:
            assert False, f"first_quote with airlines {list(airlines)} should raise LookupError"
        assert time.perf_counter() - start < 1.0, "don't wait for calls past the timeout"


def test_live_quotes_yields_in_finish_order_and_skips_failures():
    assert inspect.isasyncgenfunction(live_quotes), "live_quotes must be an async generator (async def + yield)"
    airlines = {"a": airline(100.0, 0.09), "b": airline(0, 0.01, RuntimeError("oops")), "c": airline(80.0, 0.03)}

    async def main():
        return [item async for item in live_quotes(airlines, "AMS-LIS")]

    got = asyncio.run(main())
    assert got == [("c", 80.0), ("a", 100.0)], f"got {got}"
'''

_FLIGHT_STARTER = r'''# Flight Scout - ask many (fake) airline APIs at once. Replace every "..." with real code.
import asyncio


async def gather_quotes(airlines, route, limit=3, timeout=1.0):
    ...


def cheapest(prices):
    ...


async def first_quote(airlines, route, timeout=1.0):
    ...


async def live_quotes(airlines, route):
    ...
'''


MINIS = [
    {
        "id": "mini-classes",
        "chapter": "classes",
        "title": "Pocket Pets",
        "estimated_hours": 1.0,
        "main": "app.py",
        "files": ["app.py"],
        "brief": r'''
Remember those little virtual pets that got hungry, sleepy and grumpy if you ignored them?
Build the engine for one: a `Pet` base class, a `Dog` and a `Cat` that behave a bit
differently, and a `Home` that looks after several pets at once. Everything you need is
classes, methods, properties, dunder methods and inheritance.

## What to build

A file `app.py` with four classes.

**`Pet(name)`** (the base class)
- class attribute `species = "pet"`
- `name`: a string like `"Rex"`, stored **stripped** of surrounding spaces as `self.name`
- attributes `hunger`, `energy`, `happiness` (ints, all start at `50`) and `age` (int, hours, starts at `0`)
- `feed()`: hunger **-30**, happiness **+5**
- `play()`: hunger **+10**, energy **-20**, happiness **+15**
- `sleep()`: hunger **+10**, energy **+40**
- `tick(hours=1)`: time passes. `age` goes up by `hours`; per hour: hunger **+5**, energy **-3**, happiness **-4**
- `mood`: a read-only **property** (use `@property`, so it's `pet.mood`, not `pet.mood()`), a string
- `speak()`: raises `NotImplementedError` (subclasses replace it)
- `str(pet)`, `repr(pet)` and `a < b` (see Rules)
- `feed`, `play`, `sleep`, `tick` all return `None`

**`Dog(Pet)`**: `species = "dog"`, `speak()` returns `"Woof!"`. `play()` does everything
`Pet.play()` does (call it with `super()`), then gives happiness **+10** extra.

**`Cat(Pet)`**: `species = "cat"`, `speak()` returns `"Meow."`. `sleep()` does everything
`Pet.sleep()` does, then gives happiness **+5** extra.

**`Home()`**
- `pets`: attribute, a list of pets in adoption order (starts empty)
- `adopt(pet)`: adds `pet` to `pets`, returns `None`
- `len(home)`: number of pets
- `"Rex" in home`: `True` if a pet with that exact name lives here
- `tick(hours=1)`: ticks every pet
- `ranking()`: list of pet names, happiest first
- `chorus()`: every pet's `speak()` joined with single spaces, in adoption order

## Rules
- An empty or blank name (`""`, `"   "`) raises `ValueError`.
- `hunger`, `energy` and `happiness` always stay between `0` and `100`: a change that would go
  past a limit stops at the limit (e.g. feeding a pet with hunger `20` gives `0`, not `-10`).
- `play()` when `energy` is below `20` raises `ValueError("<name> is too tired to play")`
  and changes **no** stats.
- `tick(hours)` with negative `hours` raises `ValueError`.
- `mood` is checked in this order: `"hungry"` if hunger >= 80, else `"sleepy"` if energy <= 20,
  else `"happy"` if happiness >= 70, else `"fine"`.
- `str(pet)` is exactly `"<name> the <species> is <mood> (hunger <h>, energy <e>, happiness <p>)"`.
- `repr(pet)` is the class name and the quoted name: `Dog('Rex')`, `Cat('Tom')`, `Pet('Bo')`.
- `a < b` is `True` when `a.happiness < b.happiness`, so `sorted(pets)` puts the least happy first.
- `home.adopt(pet)` when a pet with the same name is already there raises
  `ValueError("you already have a pet called <name>")` and doesn't add it.
- `ranking()`: pets with equal happiness keep their adoption order.
- `chorus()` of an empty home is `""`.

## Examples
```python
rex = Dog("  Rex ")
rex.name, rex.hunger, rex.energy, rex.happiness   # ('Rex', 50, 50, 50)
rex.play()
str(rex)        # 'Rex the dog is happy (hunger 60, energy 30, happiness 75)'
repr(rex)       # "Dog('Rex')"
rex.tick(2)     # hunger 70, energy 24, happiness 67, age 2
rex.play(); rex.play()   # second play: energy is 4 -> ValueError: Rex is too tired to play

home = Home()
home.adopt(rex); home.adopt(Cat("Tom"))
len(home), "Tom" in home, "Max" in home   # (2, True, False)
home.ranking()   # ['Rex', 'Tom']
home.chorus()    # 'Woof! Meow.'
Pet("Bo").speak()   # NotImplementedError
```

## You'll need to find out
- which special ("dunder") method Python calls for the `<` operator, so that `sorted()` can order your objects
- which special method makes the `in` operator (`"Rex" in home`) work on your own class

## Try it yourself
Add an `if __name__ == "__main__":` block at the bottom that adopts a few pets, plays with
them, calls `home.tick(3)` and prints every pet, then run `python3 app.py`.
''',
        "explore": r'''- Give pets a `health` stat that drops when hunger stays at 100, and make a pet "run away" from the `Home`.
- Add a third species with its own twist (a `Dragon` whose `feed()` barely dents its hunger).
- Write a tiny text game loop in `__main__` that reads commands (`feed rex`, `play tom`) with `input()`.
- Save and load a `Home` to a JSON file.''',
        "rubric": [
            "Shared behaviour lives in Pet; Dog and Cat only override what differs and reuse the parent via super()",
            "Clamping stats to 0..100 is written once (a helper or properties), not repeated in every method",
            "Dunder methods (__str__, __repr__, __lt__, __len__, __contains__) are small and return the right types",
            "Error cases raise ValueError with clear messages and leave the object unchanged",
        ],
        "starter_files": {"app.py": _PETS_STARTER},
        "solution_files": {"app.py": _PETS_SOLUTION},
        "tests": _PETS_TESTS,
    },
    {
        "id": "mini-dataclasses",
        "chapter": "dataclasses",
        "title": "Recipe Box",
        "estimated_hours": 1.0,
        "main": "app.py",
        "files": ["app.py"],
        "brief": r'''
Build a small typed recipe book: recipes you can scale for more or fewer people, print as a
recipe card, save as JSON-ready dicts, sort by difficulty, and merge into one shopping list.
Dataclasses do the boring parts (`__init__`, `__repr__`, `==`), you add the validation and
the useful methods.

## What to build

A file `app.py` with:

1. **`Difficulty`**: an `Enum` with members `EASY`, `MEDIUM`, `HARD` whose values are `"easy"`,
   `"medium"`, `"hard"` (in that order).
2. **`Ingredient`**: a **frozen** dataclass with fields in this order:
   `name: str` (e.g. `"flour"`), `qty: float` (e.g. `200` or `0.5`), `unit: str = ""`
   (e.g. `"g"`; `""` means "just count them", like `2` eggs).
3. **`fmt_qty(qty)`**: returns a quantity as text: rounded to 2 decimals, with no trailing
   zeros and no trailing `.` (`2.0` -> `"2"`, `0.50` -> `"0.5"`, `0.333333` -> `"0.33"`).
4. **`Recipe`**: a dataclass with fields in this order:
   `title: str`, `servings: int`, `ingredients: list[Ingredient]` (default: empty list),
   `difficulty: Difficulty` (default `Difficulty.EASY`), `tags: list[str]` (default: empty list), plus:
   - `scaled(servings)` -> a **new** `Recipe` for `servings` people
   - `card()` -> the recipe card text (see Rules)
   - `to_dict()` -> a plain dict ready for `json.dumps`
   - `Recipe.from_dict(data)` -> a **classmethod** that builds a `Recipe` from such a dict
5. **`sort_recipes(recipes)`** -> a new list of recipes, sorted (see Rules).
6. **`shopping_list(recipes)`** -> a list of `Ingredient`, everything you need to buy.

## Rules
- `Ingredient` with `qty <= 0` raises `ValueError`. Assigning to a field of an `Ingredient`
  raises `dataclasses.FrozenInstanceError` (that's what `frozen=True` does).
- Two recipes must never share the same `ingredients` or `tags` list.
- In `Recipe`'s `__post_init__`: strip `title` (a blank title raises `ValueError`);
  `servings < 1` raises `ValueError`; `difficulty` may be passed as a `Difficulty` member or as
  its string value (`"hard"`), and is always stored as the member (`Difficulty.HARD`);
  an unknown string (`"extreme"`) raises `ValueError`.
- `scaled(servings)`: every `qty` becomes `qty * new_servings / old_servings`, **rounded to 2
  decimals**. The original recipe is not changed, and the new recipe gets its own copy of
  `tags`. `scaled(0)` raises `ValueError`.
- `card()`: first line `"<title> (serves <servings>, <difficulty value>)"`, then one line per
  ingredient `"- <qty> <unit> <name>"` (or `"- <qty> <name>"` when `unit` is `""`), with qty
  written by `fmt_qty`, then `"Tags: <tag>, <tag>"` **only if** there are tags.
  Lines joined with `"\n"`, no newline at the end.
- `to_dict()`: `{"title", "servings", "ingredients": [{"name", "qty", "unit"}, ...], "difficulty": "<value>", "tags"}`.
- `from_dict(data)`: `title` and `servings` are required; `ingredients` (each dict's `unit`
  optional, default `""`), `difficulty` (default `"easy"`) and `tags` are optional.
  `Recipe.from_dict(r.to_dict()) == r` for every recipe.
- `sort_recipes`: easy first, then medium, then hard; same difficulty -> by title (plain string
  order). Doesn't change the list you pass in.
- `shopping_list`: ingredients with the same `name` **and** `unit` are merged (qty added up,
  rounded to 2 decimals); same name with a different unit stays separate. Sorted by name,
  then unit. An empty list of recipes gives `[]`.

## Examples
```python
p = Recipe("Pancakes", 4, [Ingredient("flour", 200, "g"), Ingredient("egg", 2),
                           Ingredient("milk", 0.5, "l")], "easy", ["breakfast", "sweet"])
print(p.card())
# Pancakes (serves 4, easy)
# - 200 g flour
# - 2 egg
# - 0.5 l milk
# Tags: breakfast, sweet
p.scaled(2).ingredients   # [Ingredient(name='flour', qty=100.0, unit='g'), Ingredient(name='egg', qty=1.0, unit=''), Ingredient(name='milk', qty=0.25, unit='l')]
Recipe("Chili", 6, difficulty="hard").difficulty    # <Difficulty.HARD: 'hard'>
Recipe("Chili", 0)                                   # ValueError
[r.title for r in sort_recipes([Recipe("Stew", 4, difficulty="medium"), Recipe("Toast", 1)])]   # ['Toast', 'Stew']
shopping_list([p, Recipe("Omelette", 1, [Ingredient("egg", 3)])])[1]   # Ingredient(name='egg', qty=5, unit='')
```

## You'll need to find out
- a number format (for f-strings) that writes a number with no pointless trailing zeros, so `2.0` prints as `2`
- how to get all members of an `Enum` in the order they were defined (handy for "easy before medium before hard")

## Try it yourself
Build the pancake recipe from the examples in an `if __name__ == "__main__":` block, print
`p.card()` and `p.scaled(2).card()`, then run `python3 app.py`. Try
`json.dumps(p.to_dict(), indent=2)` too.
''',
        "explore": r'''- Save the whole recipe book to a JSON file and load it back with `from_dict`.
- Add unit conversion to `shopping_list` (merge `100 ml` milk with `0.5 l` milk).
- Add a `total_time_min` field and a function that plans a dinner under a time budget.
- Run a type checker (`pip install mypy`, then `mypy app.py`) and fix what it finds.''',
        "rubric": [
            "Dataclasses and the Enum are used for what they generate; no hand-written __init__ that duplicates @dataclass",
            "Mutable defaults use default_factory and scaled() doesn't share lists with the original",
            "Validation lives in __post_init__ with clear ValueError messages",
            "Type hints on fields and functions are accurate and helpful",
        ],
        "starter_files": {"app.py": _RECIPE_STARTER},
        "solution_files": {"app.py": _RECIPE_SOLUTION},
        "tests": _RECIPE_TESTS,
    },
    {
        "id": "mini-testing",
        "chapter": "testing",
        "title": "Bug Hunt at the Bistro",
        "estimated_hours": 1.0,
        "main": "app.py",
        "files": ["app.py", "test_app.py"],
        "brief": r'''
A friend wrote `app.py`, a little helper for splitting a restaurant bill (all money is whole
**cents**, as ints). They swear it works. It doesn't: it has **exactly two bugs**. Your job is
the real-world testing loop: write a test suite for the module, let your tests expose the
bugs, fix them in `app.py`, and keep the tests as a safety net. The grader then plants other
plausible bugs into a correct copy of `app.py` and checks that your tests catch every one.

## What to build

Two files:

1. **`app.py`**: the given module with its two bugs **fixed**. Don't change what the
   functions are called or what they take. The docstrings describe the correct behaviour:
   - `to_cents(text)`: `"12.50"`, `"$12.50"` or `" 7 "` -> `1250`, `1250`, `700`.
     Raises `ValueError` for text that isn't a number (e.g. `"twelve"`, `""`) and for negative amounts.
   - `split_evenly(total_cents, people)`: a list of `people` shares that add up **exactly** to
     `total_cents`, differing by at most 1 cent, bigger shares first:
     `split_evenly(1000, 3)` -> `[334, 333, 333]`. Raises `ValueError` if `people < 1`.
   - `add_tip(total_cents, percent)`: the total plus a `percent` % tip, rounded with `round()`:
     `add_tip(1000, 15)` -> `1150`. Raises `ValueError` if `percent` is negative.
   - `convert(cents, currency, get_rate)`: `get_rate` is a function `get_rate("EUR")` -> a
     float rate. Returns `round(cents * rate)`. For `"USD"` it returns `cents` unchanged and
     must **not call** `get_rate` at all.
2. **`test_app.py`**: your tests. Plain `test_*` functions (no arguments) with `assert`s that
   import from `app` (e.g. `from app import to_cents, split_evenly, add_tip, convert`).

## Rules
- `app.py` behaves exactly as described above (the two bugs are fixed, nothing else changes).
- `test_app.py` has **at least 6** `test_` functions.
- All your tests **pass** on a correct `app.py`.
- Your tests must **catch** each of these bugs (the grader plants each one into a correct
  `app.py`, one at a time, and at least one of your tests must fail):
  - `split_evenly` ignores the leftover cents, so the shares don't add up to the total
  - `to_cents("-5")` returns `-500` instead of raising `ValueError`
  - `to_cents("$12.50")` crashes because the `$` isn't removed
  - `split_evenly(100, 0)` crashes with `ZeroDivisionError` instead of raising `ValueError`
  - `add_tip` always rounds **down** (a tip result like `1148.85` becomes `1148` instead of `1149`)
  - `convert(..., "USD", get_rate)` calls `get_rate` anyway
- Tests must not need anything outside the standard library (no pytest imports), and must not
  touch the network or files.

## Examples
```python
# test_app.py - the shape of a good test (arrange, act, assert)
from app import split_evenly

def test_split_evenly_gives_leftover_cents_to_the_first_people():
    shares = split_evenly(1000, 3)
    assert shares == [334, 333, 333]
    assert sum(shares) == 1000
```
For `convert`, write a **fake** `get_rate` in your test that records the currencies it was
asked for in a list (or that fails the test if it's called at all).

## You'll need to find out
- how Python's built-in `round()` treats numbers exactly halfway between two whole numbers
  (like `2.5` or `1150.5`) - it may not be what you expect, so pick your expected values carefully

## Try it yourself
Run your tests with a few lines at the bottom of `test_app.py`:
```python
if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("passed", name)
```
then `python3 test_app.py`. (With pytest installed, just run `pytest`.)
''',
        "explore": r'''- Install pytest and rewrite your error checks with `pytest.raises(ValueError)`.
- Use `@pytest.mark.parametrize` to turn repeated asserts into a table of cases.
- Add a `split_by_items(orders)` feature to `app.py` test-first: write the failing test, then the code.
- Think of one more plausible bug the grader didn't plant, and check your tests would catch it.''',
        "rubric": [
            "Each test checks one behaviour and is named after it (test_split_evenly_...)",
            "Edge cases are covered: leftover cents, one person, zero people, empty/garbage text, negative values",
            "The get_rate fake is simple, deterministic and records how it was called",
            "The two bug fixes in app.py are minimal and don't change anything else",
        ],
        "starter_files": {"app.py": _BILL_BUGGY, "test_app.py": _BILL_STARTER_TESTS},
        "solution_files": {"app.py": _BILL_APP, "test_app.py": _BILL_TESTS_SOLUTION},
        "tests": _BILL_HIDDEN_TESTS,
    },
    {
        "id": "mini-generators",
        "chapter": "generators",
        "title": "Log Detective",
        "estimated_hours": 1.0,
        "main": "app.py",
        "files": ["app.py"],
        "brief": r'''
It's 3 a.m., the payment service is on fire and the log file is 4 GB. Loading it into a list
isn't an option. Build a small toolkit of **generators** that stream through a log one line
at a time: read, parse, filter, spot bursts of errors, and summarise - without ever holding
the whole file in memory.

Every log line looks like this (date, time, level, source followed by a colon, message):
```
2026-09-28 09:02:00 ERROR payments: card declined
```

## What to build

A file `app.py` with:

- `LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")` - a module constant, lowest to highest.
- `read_log(path)`: a **generator function**. Opens the text file at `path` (UTF-8) and
  **yields** each line with trailing whitespace and the newline removed, skipping lines that
  are empty or only whitespace.
- `parse(lines)`: a **generator function**. `lines` is any iterable of strings (a list,
  `read_log(...)`, or an endless generator). **Yields** one dict per valid line:
  `{"date": "2026-09-28", "time": "09:02:00", "level": "ERROR", "source": "payments", "message": "card declined"}`.
- `at_least(records, level)`: returns a **generator** of the records whose level is `level`
  or higher (`"WARNING"` -> WARNING and ERROR records), in their original order.
- `tail(items, n)`: returns a **list** with the last `n` items of any iterable, oldest first.
- `incidents(records, min_count=3)`: a **generator function**. An *incident* is a run of
  **consecutive** ERROR records at least `min_count` long. **Yields** one dict per incident:
  `{"start": <time of first>, "end": <time of last>, "count": <how many>, "sources": <sorted list of distinct sources>}`.
- `summary(path)`: returns a dict for the log file at `path`:
  `{"records": <number of valid records>, "levels": {"DEBUG": n, "INFO": n, "WARNING": n, "ERROR": n}, "last_errors": <messages of the last 3 ERROR records, oldest first>, "incidents": <number of incidents with min_count 3>}`.

## Rules
- A line is **valid** when it splits (on whitespace) into date, time, level, source and a
  non-empty message; the level is one of `LEVELS` exactly (uppercase); and the source ends with
  `":"` and has at least one character before it. Other lines are skipped silently.
- `"message"` is the whole rest of the line after the source, spaces inside it kept
  (`"slow response (1200 ms)"`). `"source"` has no colon.
- `parse`, `at_least` and `incidents` must be **lazy**: they work on an endless stream when
  you only take the first few results (e.g. with `itertools.islice`).
- `at_least` with an unknown level (e.g. `"LOUD"`) raises `ValueError` **immediately when it is
  called**, before anything is read. (Careful: a generator *function*'s body only starts on
  the first `next()` - so make `at_least` a normal function that checks, then returns a
  generator expression.)
- `tail(items, n)`: fewer than `n` items -> all of them; `n` is `0` or less -> `[]`.
- `summary` includes all four levels in `"levels"`, even with a count of `0`. An empty file
  gives `{"records": 0, "levels": {all 0}, "last_errors": [], "incidents": 0}`.
- Remember generators are one-shot: if `summary` needs several passes, read the file again.

## Examples
```python
lines = ["2026-09-28 09:00:00 INFO web: server started",
         "this line is garbage",
         "2026-09-28 09:02:00 ERROR payments: card declined"]
list(parse(lines))
# [{'date': '2026-09-28', 'time': '09:00:00', 'level': 'INFO', 'source': 'web', 'message': 'server started'},
#  {'date': '2026-09-28', 'time': '09:02:00', 'level': 'ERROR', 'source': 'payments', 'message': 'card declined'}]
[r["level"] for r in at_least(parse(lines), "WARNING")]   # ['ERROR']
at_least([], "LOUD")                                     # ValueError (right away)
tail(range(1_000_000), 3)                                # [999997, 999998, 999999]
tail([1, 2], 0)                                          # []
# three ERRORs in a row at 09:02:00, 09:02:01, 09:02:02 from payments, payments, db:
# incidents(...) yields {'start': '09:02:00', 'end': '09:02:02', 'count': 3, 'sources': ['db', 'payments']}
```

## You'll need to find out
- a standard-library container that works like a list with a **maximum length**, automatically
  dropping the oldest item when a new one is added - perfect for `tail` without storing the whole file

## Try it yourself
Paste a dozen log lines (mix in blank lines, garbage and runs of ERRORs) into `server.log`,
then run `python3 -c "from app import summary; print(summary('server.log'))"`.
''',
        "explore": r'''- Add `follow(path)`: a generator that keeps yielding new lines as another program appends to the file (like `tail -f`).
- Group records per minute with `itertools.groupby` and print a tiny text histogram of errors.
- Make `read_log` also read `.gz` files transparently.
- Time `summary` on a generated 1,000,000-line file and compare memory use with a list-based version.''',
        "rubric": [
            "Each stage is a small, lazy generator and the stages compose like a pipeline",
            "No stage builds a full list of the file (tail keeps at most n items)",
            "Line validation is clear and easy to read, not a tangle of index checks",
            "summary reuses the other functions instead of re-implementing parsing",
        ],
        "starter_files": {"app.py": _LOG_STARTER},
        "solution_files": {"app.py": _LOG_SOLUTION},
        "tests": _LOG_TESTS,
    },
    {
        "id": "mini-async",
        "chapter": "async",
        "title": "Flight Scout",
        "estimated_hours": 1.25,
        "main": "app.py",
        "files": ["app.py"],
        "brief": r'''
Flight search sites ask dozens of airline APIs for prices at the same time, then show you the
cheapest, or the first answer while the others are still loading. Build the async core of
one. The "airlines" are fake async functions (the tests pass them in), so no network needed,
but the problems are real: rate limits, slow APIs, broken APIs, and stopping work you no
longer need.

## What to build

A file `app.py` with:

- `async def gather_quotes(airlines, route, limit=3, timeout=1.0)`
  - `airlines`: a dict mapping an airline name to an **async** function; `await quote(route)`
    returns a price (float), or raises, or hangs. E.g. `{"SkyLow": quote1, "JetFast": quote2}`
  - `route`: a string like `"AMS-LIS"`, passed to every quote function
  - `limit`: the maximum number of quote calls running **at the same time**
  - `timeout`: seconds allowed for each single call
  - **Returns:** `{"prices": {name: price, ...}, "errors": {name: reason, ...}}`
- `def cheapest(prices)`: `prices` is a dict like `{"a": 89.5, "b": 120.0}`.
  **Returns** the tuple `(name, price)` with the lowest price, or `None` if `prices` is empty.
- `async def first_quote(airlines, route, timeout=1.0)`: starts **all** calls at once.
  **Returns** `(name, price)` from the first airline to answer **successfully**.
- `async def live_quotes(airlines, route)`: an **async generator** (`async def` + `yield`) that
  starts all calls at once and yields `(name, price)` for each success **in the order they finish**.

## Rules
- `gather_quotes`:
  - `limit < 1` raises `ValueError`.
  - Calls run concurrently, but never more than `limit` at once.
  - The timeout clock for a call starts when that call **starts**, not while it waits for a free slot.
  - A call that takes longer than `timeout` goes into `"errors"` as `"timeout"`.
  - A call that raises goes into `"errors"` as `"<ExceptionType>: <message>"`, e.g. `"ConnectionError: server down"`.
    One failing airline never affects the others.
  - Both dicts list airlines in the same order as `airlines` (not finish order).
- `cheapest`: ties on price -> the alphabetically first name.
- `first_quote`:
  - Failing airlines are skipped; the next successful one wins.
  - As soon as there is a winner, **cancel** every call that is still running (they must not
    run to the end).
  - If no airline succeeds (all fail, `airlines` is empty, or nothing succeeds within
    `timeout` seconds in total), raise `LookupError("no quotes for <route>")` - also without
    leaving calls running.
- `live_quotes`: failing airlines are skipped (no error is raised).

## Examples
```python
async def skylow(route):
    await asyncio.sleep(0.3)
    return 89.0

async def jetfast(route):
    await asyncio.sleep(0.1)
    return 120.0

async def broken(route):
    raise ConnectionError("server down")

airlines = {"SkyLow": skylow, "JetFast": jetfast, "Broken": broken}
await gather_quotes(airlines, "AMS-LIS")
# {'prices': {'SkyLow': 89.0, 'JetFast': 120.0}, 'errors': {'Broken': 'ConnectionError: server down'}}
await gather_quotes(airlines, "AMS-LIS", timeout=0.2)
# {'prices': {'JetFast': 120.0}, 'errors': {'SkyLow': 'timeout', 'Broken': 'ConnectionError: server down'}}
cheapest({"SkyLow": 89.0, "JetFast": 120.0})            # ('SkyLow', 89.0)
cheapest({})                                             # None
await first_quote(airlines, "AMS-LIS")                   # ('JetFast', 120.0) - SkyLow gets cancelled
await first_quote({"Broken": broken}, "AMS-LIS")         # LookupError: no quotes for AMS-LIS
[q async for q in live_quotes(airlines, "AMS-LIS")]      # [('JetFast', 120.0), ('SkyLow', 89.0)]
```
(`await` at the top level only works inside `async def`; from normal code use `asyncio.run(...)`.)

## You'll need to find out
- how to get the results of several running coroutines **in the order they finish** (not the order you started them)
- how to start a coroutine as a separate running *task* that you can later **cancel**

## Try it yourself
Put the example airlines in an `async def main()` in `app.py`, print the results of each
function, and run it with `asyncio.run(main())` under `if __name__ == "__main__":`. Try
different delays and limits and watch the timings with `time.perf_counter()`.
''',
        "explore": r'''- Add retries with a short back-off for airlines that raise `ConnectionError`.
- Make `live_quotes` stop on its own after a total time budget.
- Add a per-airline rate limiter ("max 2 calls per second") with a small token-bucket class.
- Swap one fake airline for a real HTTP call later (after the http chapter) using `asyncio.to_thread`.''',
        "rubric": [
            "Concurrency is real (gather/tasks), bounded by a Semaphore, and results keep a predictable order",
            "Errors and timeouts are caught per airline so one failure never sinks the batch",
            "Tasks that are no longer needed are cancelled and cleaned up, on success and on failure",
            "No blocking calls (time.sleep) inside async code; code reads top to bottom without clever tricks",
        ],
        "starter_files": {"app.py": _FLIGHT_STARTER},
        "solution_files": {"app.py": _FLIGHT_SOLUTION},
        "tests": _FLIGHT_TESTS,
    },
]
