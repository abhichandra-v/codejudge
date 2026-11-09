"""Validate the task suite itself: reference solutions pass, traps actually trap."""

import pytest

from codejudge.task_suite import ALL_TASKS, TASKS_BY_ID, get_tasks

# The naive version of this task is intentionally non-terminating-for-practical-n,
# so we don't execute it in-process; its timeout behaviour is covered in test_runner.
SLOW_TRAP = "t11_slow_fibonacci"


def run_in_process(source, task):
    """Run every hidden case against `source`, in-process. Returns per-case results."""
    ns = {}
    exec(compile(source, "<sol>", "exec"), ns)  # noqa: S102
    func = ns[task.entry_point]
    out = []
    for c in task.cases:
        try:
            c.fn(func)
            out.append((c.name, c.edge, "pass"))
        except AssertionError as e:
            out.append((c.name, c.edge, "fail"))
        except Exception as e:  # noqa: BLE001
            out.append((c.name, c.edge, f"error:{type(e).__name__}"))
    return out


def test_suite_size_and_trap_fraction():
    assert 20 <= len(ALL_TASKS) <= 30, f"suite has {len(ALL_TASKS)} tasks"
    traps = [t for t in ALL_TASKS if t.is_trap]
    # "about a third" -- at least a quarter, no more than half
    assert len(ALL_TASKS) // 4 <= len(traps) <= len(ALL_TASKS) // 2


def test_ids_unique():
    assert len(TASKS_BY_ID) == len(ALL_TASKS)


@pytest.mark.parametrize("task", ALL_TASKS, ids=[t.id for t in ALL_TASKS])
def test_reference_solution_passes_all_cases(task):
    results = run_in_process(task.solution, task)
    bad = [r for r in results if r[2] != "pass"]
    assert not bad, f"reference for {task.id} failed: {bad}"


@pytest.mark.parametrize("task", ALL_TASKS, ids=[t.id for t in ALL_TASKS])
def test_entry_point_is_defined(task):
    ns = {}
    exec(compile(task.solution, "<sol>", "exec"), ns)  # noqa: S102
    assert callable(ns.get(task.entry_point))


@pytest.mark.parametrize("task", [t for t in ALL_TASKS if t.is_trap],
                         ids=[t.id for t in ALL_TASKS if t.is_trap])
def test_trap_metadata(task):
    assert task.trap_type, f"{task.id} is a trap but has no trap_type"
    assert task.naive_solution, f"{task.id} is a trap but has no naive_solution"
    assert task.edge_cases, f"{task.id} is a trap but has no edge cases"


@pytest.mark.parametrize(
    "task",
    [t for t in ALL_TASKS if t.is_trap and t.id != SLOW_TRAP],
    ids=[t.id for t in ALL_TASKS if t.is_trap and t.id != SLOW_TRAP],
)
def test_naive_solution_falls_into_trap(task):
    results = run_in_process(task.naive_solution, task)
    obvious = [r for r in results if not r[1]]
    edges = [r for r in results if r[1]]
    # A good trap: the naive solution passes the obvious cases ...
    assert all(r[2] == "pass" for r in obvious), \
        f"naive for {task.id} already fails an obvious case: {obvious}"
    # ... but is caught by at least one edge case.
    assert any(r[2] != "pass" for r in edges), \
        f"naive for {task.id} was NOT caught by any edge case: {edges}"


def test_slow_trap_naive_is_recursive():
    # Sanity-only: don't execute it (it would hang). Just confirm it's set up.
    task = TASKS_BY_ID[SLOW_TRAP]
    assert "fib(" in task.naive_solution and task.trap_type == "exponential-time"


def test_get_tasks_filters():
    assert all(t.is_trap for t in get_tasks(only_traps=True))
    assert {t.id for t in get_tasks(ids=["b01_fizzbuzz"])} == {"b01_fizzbuzz"}
    assert all(t.category == "math" for t in get_tasks(categories=["math"]))
