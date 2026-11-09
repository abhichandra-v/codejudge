"""Harder trap tasks -- subtle failure modes that can catch even strong models.

Same contract as traps.py: a correct ``solution`` plus a plausible
``naive_solution`` that passes the obvious cases and is caught by the edge
cases.
"""

from __future__ import annotations

from ..core import Task, check, eq

HARD_TASKS = []


def _add(task: Task) -> Task:
    HARD_TASKS.append(task)
    return task


# --- helpers for custom (mutation) cases, defined before the tasks ----------

def _remove_evens_basic(remove_evens):
    lst = [1, 3, 5]
    ret = remove_evens(lst)
    assert ret is None, f"should return None, got {ret!r}"
    assert lst == [1, 3, 5], f"list changed unexpectedly: {lst!r}"


def _remove_evens_simple(remove_evens):
    lst = [1, 2, 3]
    remove_evens(lst)
    assert lst == [1, 3], f"in-place result wrong: {lst!r}"


def _remove_evens_consecutive(remove_evens):
    lst = [2, 4, 6]
    ret = remove_evens(lst)
    assert ret is None, f"should return None, got {ret!r}"
    assert lst == [], f"consecutive evens not fully removed (skipped during iteration): {lst!r}"


def _remove_evens_interleaved(remove_evens):
    lst = [1, 2, 4, 3]
    remove_evens(lst)
    assert lst == [1, 3], f"elements skipped during iteration: {lst!r}"


# --- h01: decimal / money rounding -----------------------------------------
_add(Task(
    id="h01_round_money",
    title="Round money, half up",
    category="math",
    is_trap=True,
    trap_type="decimal-money-rounding",
    trap_note="round(2.675, 2) gives 2.67: the float 2.675 is slightly below 2.675, and round() is banker's.",
    entry_point="round_money",
    prompt=(
        "Round a monetary amount to exactly 2 decimal places, rounding a halfway "
        "value up (away from zero), and return it as a float. For example "
        "2.675 -> 2.68, 1.005 -> 1.01, 2.345 -> 2.35."
    ),
    solution=(
        "from decimal import Decimal, ROUND_HALF_UP\n"
        "def round_money(amount):\n"
        "    cents = Decimal(str(amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)\n"
        "    return float(cents)\n"
    ),
    naive_solution=(
        "def round_money(amount):\n"
        "    return round(amount, 2)\n"
    ),
    cases=[
        eq((2.5,), 2.5),
        eq((1.23,), 1.23),
        eq((0.0,), 0.0),
        eq((10.0,), 10.0),
        eq((2.675,), 2.68, edge=True),
        eq((1.005,), 1.01, edge=True),
        eq((2.345,), 2.35, edge=True),
    ],
))


# --- h02: integer square root precision ------------------------------------
_ISQRT_R = 1152921504606846973
_BIG_SQUARE = _ISQRT_R * _ISQRT_R  # 37-digit perfect square; float sqrt is off by 3

_add(Task(
    id="h02_isqrt_precision",
    title="Perfect square (large)",
    category="math",
    is_trap=True,
    trap_type="float-sqrt-precision",
    trap_note="int(math.sqrt(n)) loses precision for large n; use math.isqrt for exactness.",
    entry_point="is_perfect_square",
    prompt=(
        "Return True if the non-negative integer n is a perfect square. It must "
        "be correct for very large n (hundreds of bits), where floating-point "
        "square roots lose precision."
    ),
    solution=(
        "import math\n"
        "def is_perfect_square(n):\n"
        "    if n < 0:\n"
        "        return False\n"
        "    r = math.isqrt(n)\n"
        "    return r * r == n\n"
    ),
    naive_solution=(
        "import math\n"
        "def is_perfect_square(n):\n"
        "    r = int(math.sqrt(n))\n"
        "    return r * r == n\n"
    ),
    cases=[
        eq((0,), True),
        eq((1,), True),
        eq((4,), True),
        eq((9,), True),
        eq((2,), False),
        eq((10,), False),
        eq((144,), True),
        eq((_BIG_SQUARE,), True, edge=True),
        eq((_BIG_SQUARE + 1,), False, edge=True),
    ],
))


# --- h03: leap-year century rule -------------------------------------------
_add(Task(
    id="h03_leap_year",
    title="Days in a month",
    category="math",
    is_trap=True,
    trap_type="leap-year-century",
    trap_note="A century year is a leap year only if divisible by 400; `year % 4 == 0` gets 1900 wrong.",
    entry_point="days_in_month",
    prompt=(
        "Return the number of days in the given month (1-12) of the given year, "
        "accounting for leap years. A year is a leap year if it is divisible by "
        "4, except that century years (divisible by 100) are leap years only if "
        "also divisible by 400."
    ),
    solution=(
        "def days_in_month(year, month):\n"
        "    if month == 2:\n"
        "        leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)\n"
        "        return 29 if leap else 28\n"
        "    if month in (4, 6, 9, 11):\n"
        "        return 30\n"
        "    return 31\n"
    ),
    naive_solution=(
        "def days_in_month(year, month):\n"
        "    if month == 2:\n"
        "        return 29 if year % 4 == 0 else 28\n"
        "    if month in (4, 6, 9, 11):\n"
        "        return 30\n"
        "    return 31\n"
    ),
    cases=[
        eq((2021, 1), 31),
        eq((2021, 2), 28),
        eq((2020, 2), 29),
        eq((2021, 4), 30),
        eq((2021, 12), 31),
        eq((1900, 2), 28, edge=True),
        eq((2100, 2), 28, edge=True),
        eq((2000, 2), 29, edge=True),
    ],
))


# --- h04: unicode normalization --------------------------------------------
_add(Task(
    id="h04_unicode_normalize",
    title="Canonical string equality",
    category="strings",
    is_trap=True,
    trap_type="unicode-normalization",
    trap_note="'é' can be one code point or 'e' + combining accent; `==` sees them as different.",
    entry_point="normalized_equal",
    prompt=(
        "Return True if two strings are canonically equivalent in Unicode. For "
        "example 'é' written as a single code point (U+00E9) must compare equal "
        "to 'e' followed by a combining acute accent (U+0301). Use Unicode "
        "normalization."
    ),
    solution=(
        "import unicodedata\n"
        "def normalized_equal(a, b):\n"
        "    return unicodedata.normalize('NFC', a) == unicodedata.normalize('NFC', b)\n"
    ),
    naive_solution=(
        "def normalized_equal(a, b):\n"
        "    return a == b\n"
    ),
    cases=[
        eq(("abc", "abc"), True),
        eq(("abc", "abd"), False),
        eq(("", ""), True),
        eq(("é", "é"), True, edge=True),
        eq(("café", "café"), True, edge=True),
        eq(("é", "e"), False, edge=True),
    ],
))


# --- h05: apostrophe-aware title case --------------------------------------
_add(Task(
    id="h05_title_apostrophe",
    title="Title case with apostrophes",
    category="strings",
    is_trap=True,
    trap_type="str-title-apostrophe",
    trap_note="str.title() capitalizes the letter after an apostrophe, turning \"they're\" into \"They'Re\".",
    entry_point="smart_title",
    prompt=(
        "Capitalize the first letter of each word and lowercase the rest. A word "
        "is a run of characters separated by spaces, so an apostrophe inside a "
        "word does NOT start a new word: \"they're\" -> \"They're\" and "
        "\"o'brien\" -> \"O'brien\". Join words with single spaces."
    ),
    solution=(
        "def smart_title(s):\n"
        "    return ' '.join(w[:1].upper() + w[1:].lower() for w in s.split())\n"
    ),
    naive_solution=(
        "def smart_title(s):\n"
        "    return s.title()\n"
    ),
    cases=[
        eq(("hello world",), "Hello World"),
        eq(("the quick brown",), "The Quick Brown"),
        eq(("python",), "Python"),
        eq(("",), ""),
        eq(("they're here",), "They're Here", edge=True),
        eq(("o'brien",), "O'brien", edge=True),
        eq(("mary's little lamb",), "Mary's Little Lamb", edge=True),
    ],
))


# --- h06: mutate a list during iteration -----------------------------------
_add(Task(
    id="h06_mutate_in_place",
    title="Remove evens in place",
    category="gotchas",
    is_trap=True,
    trap_type="mutate-during-iteration",
    trap_note="Calling list.remove() while iterating the same list skips the element after each removal.",
    entry_point="remove_evens",
    prompt=(
        "Given a list of integers, remove every even number IN PLACE (modify the "
        "list that was passed in) and return None. After the call the list must "
        "contain only the odd numbers, in their original order."
    ),
    solution=(
        "def remove_evens(lst):\n"
        "    lst[:] = [x for x in lst if x % 2 != 0]\n"
    ),
    naive_solution=(
        "def remove_evens(lst):\n"
        "    for x in lst:\n"
        "        if x % 2 == 0:\n"
        "            lst.remove(x)\n"
    ),
    cases=[
        check(_remove_evens_basic, name="no evens, unchanged"),
        check(_remove_evens_simple, name="single even removed"),
        check(_remove_evens_consecutive, name="consecutive evens removed", edge=True),
        check(_remove_evens_interleaved, name="interleaved evens removed", edge=True),
    ],
))
