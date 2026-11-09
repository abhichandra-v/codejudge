"""Regular tasks.

Not deliberately trappy, but each still carries edge cases (empty inputs,
boundaries, negatives, wrap-around) that a careless solution can miss.
"""

from __future__ import annotations

from ..core import Task, eq, raises

BASIC_TASKS = []


def _add(task: Task) -> Task:
    BASIC_TASKS.append(task)
    return task


_add(Task(
    id="b01_fizzbuzz",
    title="FizzBuzz",
    category="algorithms",
    entry_point="fizzbuzz",
    prompt=(
        "Return a list of strings for the numbers 1..n. Multiples of 3 become "
        "'Fizz', multiples of 5 become 'Buzz', multiples of both become "
        "'FizzBuzz', and every other number becomes its own string."
    ),
    solution=(
        "def fizzbuzz(n):\n"
        "    out = []\n"
        "    for i in range(1, n + 1):\n"
        "        if i % 15 == 0:\n"
        "            out.append('FizzBuzz')\n"
        "        elif i % 3 == 0:\n"
        "            out.append('Fizz')\n"
        "        elif i % 5 == 0:\n"
        "            out.append('Buzz')\n"
        "        else:\n"
        "            out.append(str(i))\n"
        "    return out\n"
    ),
    cases=[
        eq((3,), ["1", "2", "Fizz"]),
        eq((5,), ["1", "2", "Fizz", "4", "Buzz"]),
        eq((0,), [], edge=True),
        eq((15,), ["1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz",
                   "Buzz", "11", "Fizz", "13", "14", "FizzBuzz"], edge=True),
    ],
))


_add(Task(
    id="b02_palindrome",
    title="Palindrome check",
    category="strings",
    entry_point="is_palindrome",
    prompt=(
        "Return True if the string is a palindrome, considering only "
        "alphanumeric characters and ignoring case."
    ),
    solution=(
        "def is_palindrome(s):\n"
        "    cleaned = [c.lower() for c in s if c.isalnum()]\n"
        "    return cleaned == cleaned[::-1]\n"
    ),
    cases=[
        eq(("A man, a plan, a canal: Panama",), True),
        eq(("race a car",), False),
        eq(("",), True, edge=True),
        eq(("Able was I, ere I saw Elba",), True),
        eq(("0P",), False, edge=True),
    ],
))


_add(Task(
    id="b03_two_sum",
    title="Two sum (indices)",
    category="algorithms",
    entry_point="two_sum",
    prompt=(
        "Given a list of integers `nums` and a `target`, return a tuple of the "
        "two indices (i, j) with i < j such that nums[i] + nums[j] == target. "
        "Return None if no such pair exists. Assume at most one answer."
    ),
    solution=(
        "def two_sum(nums, target):\n"
        "    seen = {}\n"
        "    for i, x in enumerate(nums):\n"
        "        if target - x in seen:\n"
        "            return (seen[target - x], i)\n"
        "        seen[x] = i\n"
        "    return None\n"
    ),
    cases=[
        eq(([2, 7, 11, 15], 9), (0, 1)),
        eq(([3, 2, 4], 6), (1, 2)),
        eq(([3, 3], 6), (0, 1), edge=True),
        eq(([1, 2, 3], 100), None),
        eq(([], 5), None, edge=True),
    ],
))


_add(Task(
    id="b04_factorial",
    title="Factorial",
    category="math",
    entry_point="factorial",
    prompt=(
        "Return n! (n factorial). factorial(0) is 1. If n is negative, raise a "
        "ValueError."
    ),
    solution=(
        "def factorial(n):\n"
        "    if n < 0:\n"
        "        raise ValueError('n must be non-negative')\n"
        "    result = 1\n"
        "    for i in range(2, n + 1):\n"
        "        result *= i\n"
        "    return result\n"
    ),
    cases=[
        eq((0,), 1, edge=True),
        eq((1,), 1),
        eq((5,), 120),
        eq((10,), 3628800),
        raises((-1,), ValueError, edge=True),
    ],
))


_add(Task(
    id="b05_gcd",
    title="Greatest common divisor",
    category="math",
    entry_point="gcd",
    prompt="Return the greatest common divisor of two integers a and b.",
    solution=(
        "def gcd(a, b):\n"
        "    a, b = abs(a), abs(b)\n"
        "    while b:\n"
        "        a, b = b, a % b\n"
        "    return a\n"
    ),
    cases=[
        eq((12, 8), 4),
        eq((17, 5), 1),
        eq((0, 5), 5, edge=True),
        eq((5, 0), 5, edge=True),
        eq((0, 0), 0, edge=True),
        eq((-12, 8), 4, edge=True),
    ],
))


_add(Task(
    id="b06_reverse_words",
    title="Reverse word order",
    category="strings",
    entry_point="reverse_words",
    prompt=(
        "Reverse the order of words in a sentence. Words are separated by "
        "whitespace; collapse runs of whitespace and strip leading/trailing "
        "whitespace in the result."
    ),
    solution=(
        "def reverse_words(sentence):\n"
        "    return ' '.join(sentence.split()[::-1])\n"
    ),
    cases=[
        eq(("hello world",), "world hello"),
        eq(("  the sky  is blue ",), "blue is sky the", edge=True),
        eq(("",), "", edge=True),
        eq(("one",), "one"),
    ],
))


_add(Task(
    id="b07_count_vowels",
    title="Count vowels",
    category="strings",
    entry_point="count_vowels",
    prompt="Count the vowels (a, e, i, o, u) in a string, case-insensitively.",
    solution=(
        "def count_vowels(s):\n"
        "    return sum(1 for c in s.lower() if c in 'aeiou')\n"
    ),
    cases=[
        eq(("hello",), 2),
        eq(("xyz",), 0),
        eq(("",), 0, edge=True),
        eq(("AEIOU",), 5, edge=True),
        eq(("Programming",), 3),
    ],
))


_add(Task(
    id="b08_flatten",
    title="Flatten one level",
    category="data-structures",
    entry_point="flatten",
    prompt=(
        "Given a list of lists, return a single list with the sub-lists "
        "concatenated (flatten one level only)."
    ),
    solution=(
        "def flatten(nested):\n"
        "    out = []\n"
        "    for sub in nested:\n"
        "        out.extend(sub)\n"
        "    return out\n"
    ),
    cases=[
        eq(([[1, 2], [3, 4]],), [1, 2, 3, 4]),
        eq(([[1], [], [2, 3]],), [1, 2, 3], edge=True),
        eq(([],), [], edge=True),
        eq(([[], []],), [], edge=True),
    ],
))


_add(Task(
    id="b09_merge_sorted",
    title="Merge two sorted lists",
    category="algorithms",
    entry_point="merge_sorted",
    prompt=(
        "Merge two already-sorted (ascending) lists into one sorted list and "
        "return it."
    ),
    solution=(
        "def merge_sorted(a, b):\n"
        "    i = j = 0\n"
        "    out = []\n"
        "    while i < len(a) and j < len(b):\n"
        "        if a[i] <= b[j]:\n"
        "            out.append(a[i]); i += 1\n"
        "        else:\n"
        "            out.append(b[j]); j += 1\n"
        "    out.extend(a[i:])\n"
        "    out.extend(b[j:])\n"
        "    return out\n"
    ),
    cases=[
        eq(([1, 3, 5], [2, 4, 6]), [1, 2, 3, 4, 5, 6]),
        eq(([], [1, 2]), [1, 2], edge=True),
        eq(([1, 2], []), [1, 2], edge=True),
        eq(([], []), [], edge=True),
        eq(([1, 1], [1]), [1, 1, 1]),
    ],
))


_add(Task(
    id="b10_is_prime",
    title="Primality test",
    category="math",
    entry_point="is_prime",
    prompt="Return True if n is a prime number, else False.",
    solution=(
        "def is_prime(n):\n"
        "    if n < 2:\n"
        "        return False\n"
        "    if n < 4:\n"
        "        return True\n"
        "    if n % 2 == 0:\n"
        "        return False\n"
        "    i = 3\n"
        "    while i * i <= n:\n"
        "        if n % i == 0:\n"
        "            return False\n"
        "        i += 2\n"
        "    return True\n"
    ),
    cases=[
        eq((2,), True, edge=True),
        eq((3,), True),
        eq((4,), False),
        eq((1,), False, edge=True),
        eq((0,), False, edge=True),
        eq((-7,), False, edge=True),
        eq((17,), True),
        eq((97,), True),
        eq((100,), False),
        eq((7919,), True),
    ],
))


_add(Task(
    id="b11_binary_search",
    title="Binary search",
    category="algorithms",
    entry_point="binary_search",
    prompt=(
        "Given an ascending-sorted list and a target, return the index of the "
        "target, or -1 if it is not present."
    ),
    solution=(
        "def binary_search(items, target):\n"
        "    lo, hi = 0, len(items) - 1\n"
        "    while lo <= hi:\n"
        "        mid = (lo + hi) // 2\n"
        "        if items[mid] == target:\n"
        "            return mid\n"
        "        if items[mid] < target:\n"
        "            lo = mid + 1\n"
        "        else:\n"
        "            hi = mid - 1\n"
        "    return -1\n"
    ),
    cases=[
        eq(([1, 3, 5, 7, 9], 5), 2),
        eq(([1, 3, 5, 7, 9], 1), 0, edge=True),
        eq(([1, 3, 5, 7, 9], 9), 4, edge=True),
        eq(([1, 3, 5, 7, 9], 4), -1),
        eq(([], 5), -1, edge=True),
        eq(([42], 42), 0, edge=True),
    ],
))


_add(Task(
    id="b12_anagram",
    title="Anagram check",
    category="strings",
    entry_point="is_anagram",
    prompt=(
        "Return True if two strings are anagrams of each other, ignoring case "
        "and spaces (compare letters only)."
    ),
    solution=(
        "def is_anagram(a, b):\n"
        "    def norm(s):\n"
        "        return sorted(c.lower() for c in s if c.isalpha())\n"
        "    return norm(a) == norm(b)\n"
    ),
    cases=[
        eq(("listen", "silent"), True),
        eq(("Dormitory", "Dirty room"), True, edge=True),
        eq(("hello", "world"), False),
        eq(("", ""), True, edge=True),
        eq(("a", "ab"), False),
    ],
))


_add(Task(
    id="b13_rle",
    title="Run-length encode",
    category="strings",
    entry_point="run_length_encode",
    prompt=(
        "Run-length encode a string: replace each run of a repeated character "
        "with the character followed by the run length. For example 'aaabb' -> "
        "'a3b2'. A single character still gets a count of 1 ('a' -> 'a1'). The "
        "empty string encodes to ''."
    ),
    solution=(
        "def run_length_encode(s):\n"
        "    if not s:\n"
        "        return ''\n"
        "    out = []\n"
        "    prev = s[0]\n"
        "    count = 1\n"
        "    for c in s[1:]:\n"
        "        if c == prev:\n"
        "            count += 1\n"
        "        else:\n"
        "            out.append(prev + str(count))\n"
        "            prev = c\n"
        "            count = 1\n"
        "    out.append(prev + str(count))\n"
        "    return ''.join(out)\n"
    ),
    cases=[
        eq(("aaabb",), "a3b2"),
        eq(("abc",), "a1b1c1", edge=True),
        eq(("",), "", edge=True),
        eq(("a",), "a1", edge=True),
        eq(("wwwwww",), "w6"),
    ],
))


_add(Task(
    id="b14_most_common",
    title="Most common element",
    category="data-structures",
    entry_point="most_common",
    prompt=(
        "Return the element that appears most often in a list. On a tie, return "
        "the element whose first occurrence comes earliest. Return None for an "
        "empty list."
    ),
    solution=(
        "def most_common(items):\n"
        "    counts = {}\n"
        "    for x in items:\n"
        "        counts[x] = counts.get(x, 0) + 1\n"
        "    best = None\n"
        "    best_count = -1\n"
        "    for x in items:\n"
        "        if counts[x] > best_count:\n"
        "            best = x\n"
        "            best_count = counts[x]\n"
        "    return best\n"
    ),
    cases=[
        eq(([1, 2, 2, 3, 3],), 2, edge=True),
        eq((["a", "b", "a"],), "a"),
        eq(([5],), 5),
        eq(([1, 1, 2, 2],), 1, edge=True),
        eq(([],), None, edge=True),
    ],
))


_add(Task(
    id="b15_caesar",
    title="Caesar cipher",
    category="strings",
    entry_point="caesar_cipher",
    prompt=(
        "Shift every letter in `text` forward by `shift` positions in the "
        "alphabet, wrapping around. Preserve case and leave non-letters "
        "unchanged. `shift` may be negative."
    ),
    solution=(
        "def caesar_cipher(text, shift):\n"
        "    out = []\n"
        "    for c in text:\n"
        "        if c.isupper():\n"
        "            out.append(chr((ord(c) - 65 + shift) % 26 + 65))\n"
        "        elif c.islower():\n"
        "            out.append(chr((ord(c) - 97 + shift) % 26 + 97))\n"
        "        else:\n"
        "            out.append(c)\n"
        "    return ''.join(out)\n"
    ),
    cases=[
        eq(("abc", 1), "bcd"),
        eq(("xyz", 3), "abc", edge=True),
        eq(("Hello, World!", 5), "Mjqqt, Btwqi!"),
        eq(("abc", 0), "abc"),
        eq(("abc", 26), "abc", edge=True),
        eq(("abc", -1), "zab", edge=True),
    ],
))


_add(Task(
    id="b16_valid_parens",
    title="Valid parentheses",
    category="data-structures",
    entry_point="valid_parentheses",
    prompt=(
        "Return True if a string of brackets is balanced. The brackets are "
        "(), [] and {}; they must be closed in the correct order. Other "
        "characters are not present."
    ),
    solution=(
        "def valid_parentheses(s):\n"
        "    pairs = {')': '(', ']': '[', '}': '{'}\n"
        "    stack = []\n"
        "    for c in s:\n"
        "        if c in '([{':\n"
        "            stack.append(c)\n"
        "        elif c in ')]}':\n"
        "            if not stack or stack.pop() != pairs[c]:\n"
        "                return False\n"
        "    return not stack\n"
    ),
    cases=[
        eq(("()",), True),
        eq(("()[]{}",), True),
        eq(("(]",), False),
        eq(("([)]",), False, edge=True),
        eq(("{[]}",), True),
        eq(("",), True, edge=True),
        eq(("(",), False, edge=True),
        eq((")(",), False, edge=True),
    ],
))


_add(Task(
    id="b17_title_case",
    title="Title case",
    category="strings",
    entry_point="title_case",
    prompt=(
        "Capitalize the first letter of each word and lowercase the rest. Words "
        "are whitespace-separated; join them with single spaces."
    ),
    solution=(
        "def title_case(s):\n"
        "    return ' '.join(w[:1].upper() + w[1:].lower() for w in s.split())\n"
    ),
    cases=[
        eq(("hello world",), "Hello World"),
        eq(("the QUICK brown",), "The Quick Brown", edge=True),
        eq(("",), "", edge=True),
        eq(("python",), "Python"),
    ],
))


_add(Task(
    id="b18_inclusive_range",
    title="Inclusive range",
    category="math",
    entry_point="inclusive_range",
    prompt=(
        "Return a list of all integers from a to b, inclusive of both "
        "endpoints. Assume a <= b."
    ),
    solution=(
        "def inclusive_range(a, b):\n"
        "    return list(range(a, b + 1))\n"
    ),
    cases=[
        eq((1, 3), [1, 2, 3]),
        eq((5, 5), [5], edge=True),
        eq((-2, 2), [-2, -1, 0, 1, 2], edge=True),
        eq((0, 0), [0], edge=True),
    ],
))
