# codejudge results

_Generated 2026-11-09 09:52 UTC_

## Overall pass rate

| model       | pass rate    |
| ----------- | ------------ |
| mock-naive  | 18/29 (62%)  |
| claude-opus | 29/29 (100%) |

## Pass rate by category

| category        | mock-naive | claude-opus  |
| --------------- | ---------- | ------------ |
| algorithms      | 4/5 (80%)  | 5/5 (100%)   |
| data-structures | 3/4 (75%)  | 4/4 (100%)   |
| gotchas         | 0/2 (0%)   | 2/2 (100%)   |
| math            | 4/8 (50%)  | 8/8 (100%)   |
| strings         | 7/10 (70%) | 10/10 (100%) |

## Failure breakdown

| outcome           | mock-naive | claude-opus |
| ----------------- | ---------- | ----------- |
| pass              | 18         | 29          |
| wrong answer      | 0          | 0           |
| edge-case failure | 10         | 0           |
| timeout           | 1          | 0           |
| runtime error     | 0          | 0           |

## Which traps fooled each model

A trap is 'fooled' when the model does not PASS. `edge` means it passed the obvious cases but failed the edge case the trap targets.

| trap                      | trap type                | mock-naive       | claude-opus |
| ------------------------- | ------------------------ | ---------------- | ----------- |
| t01_mutable_default       | mutable-default-argument | FOOLED (edge)    | ok          |
| t02_off_by_one_chunks     | off-by-one               | FOOLED (edge)    | ok          |
| t03_float_equality        | floating-point-equality  | FOOLED (edge)    | ok          |
| t04_unicode_casefold      | unicode-casefold         | FOOLED (edge)    | ok          |
| t05_int32_overflow        | integer-overflow         | FOOLED (edge)    | ok          |
| t06_list_aliasing         | list-aliasing            | FOOLED (edge)    | ok          |
| t07_case_insensitive_sort | case-sensitive-sort      | FOOLED (edge)    | ok          |
| t08_strip_suffix          | str-strip-chars          | FOOLED (edge)    | ok          |
| t09_falsy_default         | falsy-vs-none            | FOOLED (edge)    | ok          |
| t10_bankers_rounding      | bankers-rounding         | FOOLED (edge)    | ok          |
| t11_slow_fibonacci        | exponential-time         | FOOLED (timeout) | ok          |

- **mock-naive**: fooled by 11/11 traps.
- **claude-opus**: fooled by 0/11 traps.
