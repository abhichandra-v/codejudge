"""Trap tasks: the deliberately tricky third of the suite.

Each task ships a correct ``solution`` and a ``naive_solution`` -- a plausible
implementation that passes the obvious cases but falls into a specific trap on
an edge case. The edge cases (``edge=True``) are what catch the trap.
"""

from __future__ import annotations

from ..core import Case, Task, check, eq

TRAP_TASKS = []


def _add(task: Task) -> Task:
    TRAP_TASKS.append(task)
    return task


# --- helpers used by custom cases (defined before the tasks that use them) --

def _independent_fresh_calls(accumulate):
    first = accumulate("x")
    second = accumulate("y")
    assert first == ["x"], f"first fresh call -> {first!r}"
    assert second == ["y"], f"second call leaked state from the first -> {second!r}"


def _assert_grid_independent(make_grid):
    g = make_grid(3, 3)
    g[0][0] = 9
    assert g[1][0] == 0 and g[2][0] == 0, f"rows are aliased: {g!r}"


# --- t01: mutable default argument -----------------------------------------
_add(Task(
    id="t01_mutable_default",
    title="Accumulate into a list",
    category="gotchas",
    is_trap=True,
    trap_type="mutable-default-argument",
    trap_note="Using `bucket=[]` as a default shares one list across all calls.",
    entry_point="accumulate",
    prompt=(
        "Write a function `accumulate(value, bucket=None)` that appends `value` "
        "to the list `bucket` and returns the resulting list. When called "
        "without a bucket it must start from a fresh empty list every time, so "
        "two independent calls never share state."
    ),
    solution=(
        "def accumulate(value, bucket=None):\n"
        "    if bucket is None:\n"
        "        bucket = []\n"
        "    bucket.append(value)\n"
        "    return bucket\n"
    ),
    naive_solution=(
        "def accumulate(value, bucket=[]):\n"
        "    bucket.append(value)\n"
        "    return bucket\n"
    ),
    cases=[
        eq(("a", []), ["a"]),
        eq((1, [10]), [10, 1]),
        check(_independent_fresh_calls, name="independent fresh calls", edge=True),
    ],
))


# --- t02: off-by-one (ceiling division) ------------------------------------
_add(Task(
    id="t02_off_by_one_chunks",
    title="Number of chunks",
    category="math",
    is_trap=True,
    trap_type="off-by-one",
    trap_note="`length // n` drops the final partial chunk; you need a ceiling.",
    entry_point="num_chunks",
    prompt=(
        "Given a number of items `length` and a chunk size `n` (n > 0), return "
        "how many chunks are needed to cover all items. The last chunk may be "
        "partial. For example 10 items in chunks of 3 needs 4 chunks."
    ),
    solution=(
        "def num_chunks(length, n):\n"
        "    return (length + n - 1) // n\n"
    ),
    naive_solution=(
        "def num_chunks(length, n):\n"
        "    return length // n\n"
    ),
    cases=[
        eq((10, 5), 2),
        eq((9, 3), 3),
        eq((0, 5), 0),
        eq((10, 3), 4, edge=True),
        eq((1, 5), 1, edge=True),
        eq((7, 2), 4, edge=True),
    ],
))


# --- t03: floating-point equality ------------------------------------------
_add(Task(
    id="t03_float_equality",
    title="Does it sum to the target?",
    category="math",
    is_trap=True,
    trap_type="floating-point-equality",
    trap_note="`sum(xs) == target` fails because 0.1 + 0.2 != 0.3 in binary float.",
    entry_point="sums_to",
    prompt=(
        "Return True if the sum of the list `numbers` equals `target`, allowing "
        "for floating-point rounding error (use a tolerance of 1e-9)."
    ),
    solution=(
        "def sums_to(numbers, target):\n"
        "    return abs(sum(numbers) - target) <= 1e-9\n"
    ),
    naive_solution=(
        "def sums_to(numbers, target):\n"
        "    return sum(numbers) == target\n"
    ),
    cases=[
        eq(([1, 2, 3], 6), True),
        eq(([1.5, 1.5], 3.0), True),
        eq(([1, 2], 4), False),
        eq(([0.1, 0.2], 0.3), True, edge=True),
        eq(([0.1, 0.1, 0.1], 0.3), True, edge=True),
        eq(([0.1, 0.2], 0.4), False, edge=True),
    ],
))


# --- t04: unicode case folding ---------------------------------------------
_add(Task(
    id="t04_unicode_casefold",
    title="Case-insensitive compare",
    category="strings",
    is_trap=True,
    trap_type="unicode-casefold",
    trap_note="`.lower()` is not full case folding; 'STRASSE' should match 'straße'.",
    entry_point="equal_ignore_case",
    prompt=(
        "Return True if strings `a` and `b` are equal ignoring case, using "
        "proper Unicode case folding. For example the German 'ß' should compare "
        "equal to 'ss', so 'STRASSE' and 'straße' are equal."
    ),
    solution=(
        "def equal_ignore_case(a, b):\n"
        "    return a.casefold() == b.casefold()\n"
    ),
    naive_solution=(
        "def equal_ignore_case(a, b):\n"
        "    return a.lower() == b.lower()\n"
    ),
    cases=[
        eq(("Hello", "hello"), True),
        eq(("ABC", "abc"), True),
        eq(("cat", "dog"), False),
        eq(("STRASSE", "straße"), True, edge=True),
        eq(("GROSSE", "große"), True, edge=True),
    ],
))


# --- t05: integer overflow / wraparound ------------------------------------
_add(Task(
    id="t05_int32_overflow",
    title="32-bit integer addition",
    category="math",
    is_trap=True,
    trap_type="integer-overflow",
    trap_note="Python ints never overflow, so you must wrap to 32-bit two's complement yourself.",
    entry_point="add_int32",
    prompt=(
        "Add two 32-bit signed integers and return the result as it would "
        "appear in 32-bit two's-complement arithmetic, i.e. with overflow "
        "wrapping around (valid range -2**31 .. 2**31-1)."
    ),
    solution=(
        "def add_int32(a, b):\n"
        "    s = (a + b) & 0xFFFFFFFF\n"
        "    if s >= 0x80000000:\n"
        "        s -= 0x100000000\n"
        "    return s\n"
    ),
    naive_solution=(
        "def add_int32(a, b):\n"
        "    return a + b\n"
    ),
    cases=[
        eq((1, 2), 3),
        eq((-5, 3), -2),
        eq((0, 0), 0),
        eq((2**31 - 1, 1), -(2**31), edge=True),
        eq((-(2**31), -1), 2**31 - 1, edge=True),
        eq((2**31 - 1, 2**31 - 1), -2, edge=True),
    ],
))


# --- t06: list aliasing -----------------------------------------------------
_add(Task(
    id="t06_list_aliasing",
    title="Build a grid",
    category="data-structures",
    is_trap=True,
    trap_type="list-aliasing",
    trap_note="`[[0]*cols]*rows` makes every row the same list object.",
    entry_point="make_grid",
    prompt=(
        "Return a `rows` x `cols` grid (a list of lists) filled with 0. Each "
        "row must be an independent list, so assigning to one cell must not "
        "change cells in any other row."
    ),
    solution=(
        "def make_grid(rows, cols):\n"
        "    return [[0] * cols for _ in range(rows)]\n"
    ),
    naive_solution=(
        "def make_grid(rows, cols):\n"
        "    return [[0] * cols] * rows\n"
    ),
    cases=[
        eq((2, 3), [[0, 0, 0], [0, 0, 0]]),
        eq((1, 1), [[0]]),
        eq((0, 5), []),
        check(_assert_grid_independent, name="rows are independent", edge=True),
    ],
))


# --- t07: case-sensitive sort ----------------------------------------------
_add(Task(
    id="t07_case_insensitive_sort",
    title="Sort names alphabetically",
    category="strings",
    is_trap=True,
    trap_type="case-sensitive-sort",
    trap_note="Plain `sorted` orders by code point, so uppercase sorts before lowercase.",
    entry_point="sort_names",
    prompt=(
        "Sort a list of names alphabetically, case-insensitively, returning a "
        "new list. Names that differ only in case must keep their original "
        "relative order (stable)."
    ),
    solution=(
        "def sort_names(names):\n"
        "    return sorted(names, key=str.casefold)\n"
    ),
    naive_solution=(
        "def sort_names(names):\n"
        "    return sorted(names)\n"
    ),
    cases=[
        eq((["banana", "apple", "cherry"],), ["apple", "banana", "cherry"]),
        eq(([],), []),
        eq((["Banana", "apple"],), ["apple", "Banana"], edge=True),
        eq((["delta", "Alpha", "bravo"],), ["Alpha", "bravo", "delta"], edge=True),
    ],
))


# --- t08: str.strip removes characters, not a suffix -----------------------
_add(Task(
    id="t08_strip_suffix",
    title="Remove a .txt extension",
    category="strings",
    is_trap=True,
    trap_type="str-strip-chars",
    trap_note="`rstrip('.txt')` strips any of the characters . t x, not the suffix.",
    entry_point="remove_extension",
    prompt=(
        "Remove a trailing '.txt' extension from a filename and return the base "
        "name. If the name does not end in '.txt', return it unchanged. Only a "
        "single trailing '.txt' should be removed."
    ),
    solution=(
        "def remove_extension(filename):\n"
        "    if filename.endswith('.txt'):\n"
        "        return filename[:-4]\n"
        "    return filename\n"
    ),
    naive_solution=(
        "def remove_extension(filename):\n"
        "    return filename.rstrip('.txt')\n"
    ),
    cases=[
        eq(("notes.txt",), "notes"),
        eq(("data",), "data"),
        eq(("report.pdf",), "report.pdf"),
        eq(("mytext.txt",), "mytext", edge=True),
        eq(("exit.txt",), "exit", edge=True),
        eq(("a.txt.txt",), "a.txt", edge=True),
    ],
))


# --- t09: falsy value vs None ----------------------------------------------
_add(Task(
    id="t09_falsy_default",
    title="Return value or default",
    category="gotchas",
    is_trap=True,
    trap_type="falsy-vs-none",
    trap_note="`value or default` also replaces falsy values like 0, '' and [].",
    entry_point="with_default",
    prompt=(
        "Return `value`, unless `value` is None, in which case return `default`. "
        "A `value` of 0, an empty string, or an empty list is NOT None and must "
        "be returned as-is."
    ),
    solution=(
        "def with_default(value, default):\n"
        "    return default if value is None else value\n"
    ),
    naive_solution=(
        "def with_default(value, default):\n"
        "    return value or default\n"
    ),
    cases=[
        eq((5, 0), 5),
        eq((None, "x"), "x"),
        eq(("hi", "bye"), "hi"),
        eq((0, 99), 0, edge=True),
        eq(("", "d"), "", edge=True),
        eq(([], [1]), [], edge=True),
    ],
))


# --- t10: banker's rounding ------------------------------------------------
_add(Task(
    id="t10_bankers_rounding",
    title="Round half up",
    category="math",
    is_trap=True,
    trap_type="bankers-rounding",
    trap_note="Built-in round() uses banker's rounding, so round(2.5) == 2, not 3.",
    entry_point="round_half_up",
    prompt=(
        "Round a non-negative number to the nearest integer, rounding a halfway "
        "value (.5) up. For example 2.5 -> 3, 0.5 -> 1 and 4.5 -> 5."
    ),
    solution=(
        "import math\n"
        "def round_half_up(x):\n"
        "    return math.floor(x + 0.5)\n"
    ),
    naive_solution=(
        "def round_half_up(x):\n"
        "    return round(x)\n"
    ),
    cases=[
        eq((2.4,), 2),
        eq((2.6,), 3),
        eq((3.0,), 3),
        eq((2.5,), 3, edge=True),
        eq((0.5,), 1, edge=True),
        eq((4.5,), 5, edge=True),
    ],
))


# --- t11: exponential-time recursion (timeout) -----------------------------
_add(Task(
    id="t11_slow_fibonacci",
    title="Nth Fibonacci number",
    category="algorithms",
    is_trap=True,
    trap_type="exponential-time",
    trap_note="Naive double recursion is O(2**n) and times out for n around 40.",
    entry_point="fib",
    prompt=(
        "Return the n-th Fibonacci number (0-indexed, fib(0)=0, fib(1)=1). It "
        "must handle n up to at least 40 efficiently (well under a second)."
    ),
    solution=(
        "def fib(n):\n"
        "    a, b = 0, 1\n"
        "    for _ in range(n):\n"
        "        a, b = b, a + b\n"
        "    return a\n"
    ),
    naive_solution=(
        "def fib(n):\n"
        "    if n < 2:\n"
        "        return n\n"
        "    return fib(n - 1) + fib(n - 2)\n"
    ),
    cases=[
        eq((0,), 0),
        eq((1,), 1),
        eq((10,), 55),
        eq((40,), 102334155, edge=True),  # the naive version blows the timeout here
    ],
))
