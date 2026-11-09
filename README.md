# codejudge

A small, sandboxed harness for evaluating **LLM-written Python code** against
hidden test suites. It ships with 29 hand-written tasks — a third of them
*traps* designed to make a plausible-but-wrong solution pass the obvious cases
and fail on a specific edge case — generates a solution from a model, runs it
in an isolated subprocess with a timeout, classifies each failure, and prints a
report of pass rates and which traps fooled which model.

Model code is **never executed inside the harness process**: every candidate
runs in a separate Python process with a wall-clock timeout (or in a locked-down
Docker container).

## Why this exists

Measuring whether a model can *write correct code* is harder than it looks: a
model will happily pass naive tests while getting the boundary wrong. codejudge
makes that failure visible by pairing each tricky task with the exact edge case
that catches the mistake, then reporting it as a distinct outcome
(`edge-case failure`) separate from an outright `wrong answer`, a `timeout`, or
a `runtime error`.

## Install

```bash
git clone <your-fork-url> codejudge
cd codejudge
python -m pip install -e ".[dev]"   # or: pip install pytest
```

No runtime dependencies — the harness is pure standard library. `pytest` is only
needed to run the harness's own test suite.

## Quick start

List the tasks:

```bash
python -m codejudge list
```

Run the two built-in **offline mock models** (no model server or API key
needed — great for a demo and for CI):

```bash
python -m codejudge run --models naive,careful
```

This writes `results/report.md` and a timestamped `results/results_*.json`, and
prints a summary. `naive` emits a plausible-but-wrong solution for every trap;
`careful` emits the reference solution but still trips on the two subtlest traps
— so you get a two-model comparison out of the box.

Run **real models** (see [Models](#models)):

```bash
python -m codejudge run --models "ollama:qwen2.5-coder,ollama:llama3.1"
python -m codejudge run --models "anthropic:claude-3-5-sonnet-20241022,openai:gpt-4o-mini"
```

Or **judge solutions a model already wrote** — drop one `<task_id>.py` file per
task into a directory and point codejudge at it (no model server needed at run
time):

```bash
python -m codejudge run --solutions "claude-opus=examples/claude-opus-solutions" --models naive
```

Useful flags: `--timeout 10` (per-task seconds), `--executor docker`,
`--only-traps`, `--tasks t01_mutable_default,b10_is_prime`,
`--categories math,strings`, `--out results/`.

Check that the suite itself is valid (every reference solution passes its own
hidden tests):

```bash
python -m codejudge verify
```

## Example results (built-in mock models)

From `python -m codejudge run --models naive,careful` on the 29-task suite:

| model        | pass rate   | traps fooled |
| ------------ | ----------- | ------------ |
| mock-naive   | 18/29 (62%) | 11/11        |
| mock-careful | 27/29 (93%) | 2/11         |

Failure breakdown:

| outcome           | mock-naive | mock-careful |
| ----------------- | ---------- | ------------ |
| pass              | 18         | 27           |
| edge-case failure | 10         | 2            |
| timeout           | 1          | 0            |

The naive model is caught by every trap; the careful model is caught only by the
two subtlest ones (Unicode case folding and banker's rounding). These are
illustrative numbers from the deterministic mock models — run a real model via
Ollama or an API to get its numbers.

### Example: judging real model-written code

The solutions under [`examples/claude-opus-solutions/`](examples/claude-opus-solutions)
were written by a frontier model (Claude Opus) from the task prompts, then
executed and judged by the harness (`--solutions` above). Full output:
[`examples/claude-opus-report.md`](examples/claude-opus-report.md).

An **independent model** (`stealth/crouton-alpha`, run live via the OpenRouter
API — it never saw the hidden tests and did not design the suite) was judged the
same way. Full output: [`examples/crouton-alpha-report.md`](examples/crouton-alpha-report.md).

| model                     | pass rate    | traps fooled |
| ------------------------- | ------------ | ------------ |
| stealth/crouton-alpha (independent, live API) | 29/29 (100%) | 0/11 |
| claude-opus (self-written solutions)          | 29/29 (100%) | 0/11 |
| mock-naive (baseline)                         | 18/29 (62%)  | 11/11        |

The naive baseline is caught by all 11 traps (10 edge-case failures + 1
timeout); both real models passed every task, including all 11 traps. The
mock-naive column is the reference "weak model" the harness is designed to
catch.

> Note: I authored both the task suite and the `claude-opus` solutions, so that
> row demonstrates the harness executing and judging genuine model output rather
> than measuring difficulty. The `crouton-alpha` row is the unbiased run — a
> model with no connection to the suite. To push pass rates below 100%, add
> harder tasks or run a smaller local model (e.g. a 3B via Ollama).

## The tasks

29 tasks across `algorithms`, `data-structures`, `gotchas`, `math` and
`strings`. 11 are traps, each targeting a specific, well-known failure mode:

| trap task                 | trap type                | the mistake it catches |
| ------------------------- | ------------------------ | ---------------------- |
| t01_mutable_default       | mutable-default-argument | `def f(x, acc=[])` shares one list across calls |
| t02_off_by_one_chunks     | off-by-one               | `length // n` drops the final partial chunk |
| t03_float_equality        | floating-point-equality  | `sum(xs) == target` — 0.1 + 0.2 != 0.3 |
| t04_unicode_casefold      | unicode-casefold         | `.lower()` isn't full case folding ('ß' vs 'ss') |
| t05_int32_overflow        | integer-overflow         | Python ints don't wrap; 32-bit must be emulated |
| t06_list_aliasing         | list-aliasing            | `[[0]*c]*r` makes every row the same object |
| t07_case_insensitive_sort | case-sensitive-sort      | `sorted()` orders uppercase before lowercase |
| t08_strip_suffix          | str-strip-chars          | `rstrip('.txt')` strips characters, not a suffix |
| t09_falsy_default         | falsy-vs-none            | `value or default` also replaces 0, '' and [] |
| t10_bankers_rounding      | bankers-rounding         | `round(2.5)` is 2, not 3 (round-half-to-even) |
| t11_slow_fibonacci        | exponential-time         | O(2ⁿ) recursion times out around n=40 |

Every task — trap or not — also carries ordinary edge cases (empty inputs,
boundaries, negatives, wrap-around).

### Task format

Each task is a problem statement plus a hidden list of cases. The model only
ever sees the statement.

```python
Task(
    id="t03_float_equality",
    title="Does it sum to the target?",
    category="math",
    is_trap=True,
    trap_type="floating-point-equality",
    entry_point="sums_to",
    prompt="Return True if the sum of `numbers` equals `target`, allowing "
           "for floating-point rounding error (tolerance 1e-9).",
    solution="def sums_to(numbers, target):\n    return abs(sum(numbers) - target) <= 1e-9\n",
    naive_solution="def sums_to(numbers, target):\n    return sum(numbers) == target\n",
    cases=[
        eq(([1, 2, 3], 6), True),             # obvious
        eq(([0.1, 0.2], 0.3), True, edge=True) # the trap
    ],
)
```

A `Case` is just a callable that receives the candidate function and asserts on
its behaviour, so cases can test things a simple input/output pair can't — e.g.
that two default-argument calls don't share state, or that grid rows are
independent objects. Cases marked `edge=True` are what distinguish a careful
solution from a trapped one. Arguments are deep-copied on each call, so a
function that mutates its input in place can't corrupt the fixtures.

## Failure classification

Each run is tagged with exactly one outcome and a short note on why:

| outcome             | meaning |
| ------------------- | ------- |
| `pass`              | all hidden cases passed |
| `wrong answer`      | an **obvious** (non-edge) case returned the wrong value |
| `edge-case failure` | the obvious cases passed, but an **edge** case failed — the trap worked |
| `timeout`           | the solution exceeded the wall-clock limit (infinite loop / exponential blow-up) |
| `runtime error`     | the solution crashed, didn't compile, or didn't define the function |

A thrown exception is reported as a runtime error even if assertions also
failed, so the most fundamental problem surfaces first.

## Sandboxing

> **Never run model output unsandboxed.** codejudge doesn't.

- **`subprocess` executor (default).** Each solution runs in a fresh Python
  process with a wall-clock timeout; crashes and infinite loops are isolated
  from the harness, and results travel back through a result file (not stdout,
  which the candidate could pollute). It shares the host filesystem, so only use
  it for code you're willing to run locally.
- **`docker` executor.** Runs the same runner inside a disposable
  `python:3.11-slim` container with `--network none`, a memory cap, a CPU cap
  and a PID limit; the repo is mounted read-only. Use this for untrusted output:

  ```bash
  python -m codejudge run --models "ollama:llama3.1" --executor docker
  ```

## Models

A "model" is anything with a `name` and a `complete(task) -> str` method that
returns Python source. Built in:

| spec                                | what it is |
| ----------------------------------- | ---------- |
| `naive` / `careful`                 | offline, deterministic mock models |
| `ollama:<model>`                    | local model via [Ollama](https://ollama.com) (`OLLAMA_HOST` optional) |
| `openai:<model>`                    | OpenAI-compatible chat API (`OPENAI_API_KEY`, `OPENAI_BASE_URL` optional) |
| `anthropic:<model>`                 | Anthropic Messages API (`ANTHROPIC_API_KEY`) |

To add your own, implement the two-member interface and pass it to
`codejudge.run_eval`.

## Use as a library

```python
from codejudge import run_eval, SubprocessExecutor
from codejudge.providers import MockModel
from codejudge.task_suite import get_tasks

results = run_eval(
    [MockModel("naive"), MockModel("careful")],
    get_tasks(only_traps=True),
    SubprocessExecutor(timeout=10),
)
for r in results:
    print(r.model, r.task_id, r.outcome)
```

## Development

```bash
python -m pytest        # 114 tests for the harness itself
python -m codejudge verify
```

The harness is tested independently of any model: the classifier is unit-tested,
the executor is tested against pass / wrong / crash / timeout / syntax-error
solutions, and the task suite is validated (every reference solution passes, and
every naive solution is actually caught by an edge case).

## Project layout

```
codejudge/
  core.py            # Task / Case data model + case builders
  task_suite/        # the 29 tasks (traps.py + basics.py)
  providers.py       # mock, Ollama, OpenAI, Anthropic models
  runner.py          # SubprocessExecutor + DockerExecutor
  _sandbox_runner.py # the script executed in the isolated process
  classify.py        # failure classification
  harness.py         # orchestration
  report.py          # Markdown + console reports
  cli.py             # `python -m codejudge`
tests/               # pytest suite for the harness
```

## License

MIT — see [LICENSE](LICENSE).
