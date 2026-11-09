# codejudge results

_Generated 2026-11-09 14:35 UTC_

## Overall pass rate

| model       | pass rate    |
| ----------- | ------------ |
| claude-opus | 35/35 (100%) |

## Pass rate by category

| category        | claude-opus  |
| --------------- | ------------ |
| algorithms      | 5/5 (100%)   |
| data-structures | 4/4 (100%)   |
| gotchas         | 3/3 (100%)   |
| math            | 11/11 (100%) |
| strings         | 12/12 (100%) |

## Failure breakdown

| outcome           | claude-opus |
| ----------------- | ----------- |
| pass              | 35          |
| wrong answer      | 0           |
| edge-case failure | 0           |
| timeout           | 0           |
| runtime error     | 0           |

## Which traps fooled each model

A trap is 'fooled' when the model does not PASS. `edge` means it passed the obvious cases but failed the edge case the trap targets.

| trap                      | trap type                | claude-opus |
| ------------------------- | ------------------------ | ----------- |
| t01_mutable_default       | mutable-default-argument | ok          |
| t02_off_by_one_chunks     | off-by-one               | ok          |
| t03_float_equality        | floating-point-equality  | ok          |
| t04_unicode_casefold      | unicode-casefold         | ok          |
| t05_int32_overflow        | integer-overflow         | ok          |
| t06_list_aliasing         | list-aliasing            | ok          |
| t07_case_insensitive_sort | case-sensitive-sort      | ok          |
| t08_strip_suffix          | str-strip-chars          | ok          |
| t09_falsy_default         | falsy-vs-none            | ok          |
| t10_bankers_rounding      | bankers-rounding         | ok          |
| t11_slow_fibonacci        | exponential-time         | ok          |
| h01_round_money           | decimal-money-rounding   | ok          |
| h02_isqrt_precision       | float-sqrt-precision     | ok          |
| h03_leap_year             | leap-year-century        | ok          |
| h04_unicode_normalize     | unicode-normalization    | ok          |
| h05_title_apostrophe      | str-title-apostrophe     | ok          |
| h06_mutate_in_place       | mutate-during-iteration  | ok          |

- **claude-opus**: fooled by 0/17 traps.
