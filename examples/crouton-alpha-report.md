# codejudge results

_Generated 2026-11-09 14:33 UTC_

## Overall pass rate

| model                        | pass rate    |
| ---------------------------- | ------------ |
| mock-naive                   | 18/35 (51%)  |
| openai:stealth/crouton-alpha | 35/35 (100%) |
| claude-opus                  | 35/35 (100%) |

## Pass rate by category

| category        | mock-naive | openai:stealth/crouton-alpha | claude-opus  |
| --------------- | ---------- | ---------------------------- | ------------ |
| algorithms      | 4/5 (80%)  | 5/5 (100%)                   | 5/5 (100%)   |
| data-structures | 3/4 (75%)  | 4/4 (100%)                   | 4/4 (100%)   |
| gotchas         | 0/3 (0%)   | 3/3 (100%)                   | 3/3 (100%)   |
| math            | 4/11 (36%) | 11/11 (100%)                 | 11/11 (100%) |
| strings         | 7/12 (58%) | 12/12 (100%)                 | 12/12 (100%) |

## Failure breakdown

| outcome           | mock-naive | openai:stealth/crouton-alpha | claude-opus |
| ----------------- | ---------- | ---------------------------- | ----------- |
| pass              | 18         | 35                           | 35          |
| wrong answer      | 0          | 0                            | 0           |
| edge-case failure | 16         | 0                            | 0           |
| timeout           | 1          | 0                            | 0           |
| runtime error     | 0          | 0                            | 0           |

## Which traps fooled each model

A trap is 'fooled' when the model does not PASS. `edge` means it passed the obvious cases but failed the edge case the trap targets.

| trap                      | trap type                | mock-naive       | openai:stealth/crouton-alpha | claude-opus |
| ------------------------- | ------------------------ | ---------------- | ---------------------------- | ----------- |
| t01_mutable_default       | mutable-default-argument | FOOLED (edge)    | ok                           | ok          |
| t02_off_by_one_chunks     | off-by-one               | FOOLED (edge)    | ok                           | ok          |
| t03_float_equality        | floating-point-equality  | FOOLED (edge)    | ok                           | ok          |
| t04_unicode_casefold      | unicode-casefold         | FOOLED (edge)    | ok                           | ok          |
| t05_int32_overflow        | integer-overflow         | FOOLED (edge)    | ok                           | ok          |
| t06_list_aliasing         | list-aliasing            | FOOLED (edge)    | ok                           | ok          |
| t07_case_insensitive_sort | case-sensitive-sort      | FOOLED (edge)    | ok                           | ok          |
| t08_strip_suffix          | str-strip-chars          | FOOLED (edge)    | ok                           | ok          |
| t09_falsy_default         | falsy-vs-none            | FOOLED (edge)    | ok                           | ok          |
| t10_bankers_rounding      | bankers-rounding         | FOOLED (edge)    | ok                           | ok          |
| t11_slow_fibonacci        | exponential-time         | FOOLED (timeout) | ok                           | ok          |
| h01_round_money           | decimal-money-rounding   | FOOLED (edge)    | ok                           | ok          |
| h02_isqrt_precision       | float-sqrt-precision     | FOOLED (edge)    | ok                           | ok          |
| h03_leap_year             | leap-year-century        | FOOLED (edge)    | ok                           | ok          |
| h04_unicode_normalize     | unicode-normalization    | FOOLED (edge)    | ok                           | ok          |
| h05_title_apostrophe      | str-title-apostrophe     | FOOLED (edge)    | ok                           | ok          |
| h06_mutate_in_place       | mutate-during-iteration  | FOOLED (edge)    | ok                           | ok          |

- **mock-naive**: fooled by 17/17 traps.
- **openai:stealth/crouton-alpha**: fooled by 0/17 traps.
- **claude-opus**: fooled by 0/17 traps.
