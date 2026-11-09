"""End-to-end harness tests with the deterministic mock models."""

from codejudge.classify import Outcome
from codejudge.harness import run_eval, verify_suite
from codejudge.providers import MockModel
from codejudge.report import summarize, to_console, to_markdown
from codejudge.runner import SubprocessExecutor
from codejudge.task_suite import get_tasks

# A fast, deterministic subset (excludes the slow-fibonacci timeout trap).
SUBSET = get_tasks(ids=[
    "t01_mutable_default", "t03_float_equality", "t06_list_aliasing",
    "b01_fizzbuzz", "b05_gcd",
])
TRAP_IDS = {"t01_mutable_default", "t03_float_equality", "t06_list_aliasing"}


def _results():
    models = [MockModel("naive"), MockModel("careful")]
    return run_eval(models, SUBSET, SubprocessExecutor(timeout=10))


def test_careful_passes_subset():
    results = [r for r in _results() if r.model == "mock-careful"]
    assert all(r.passed for r in results), [r.task_id for r in results if not r.passed]


def test_naive_fails_only_the_traps():
    results = {r.task_id: r for r in _results() if r.model == "mock-naive"}
    for tid, r in results.items():
        if tid in TRAP_IDS:
            assert not r.passed, f"{tid} should have fooled the naive model"
            assert r.outcome == Outcome.EDGE_CASE_FAILURE.value
        else:
            assert r.passed, f"{tid} should have passed"


def test_summarize_and_report():
    results = _results()
    summ = summarize(results)
    assert summ["models"] == ["mock-naive", "mock-careful"]
    assert summ["overall"]["mock-careful"]["passed"] == len(SUBSET)
    assert summ["overall"]["mock-naive"]["passed"] == len(SUBSET) - len(TRAP_IDS)

    md = to_markdown(results)
    assert "Overall pass rate" in md and "traps fooled" in md
    assert "mock-naive" in to_console(results)


def test_verify_subset_reference_solutions():
    results = verify_suite(SUBSET, SubprocessExecutor(timeout=10))
    assert all(r.passed for r in results)


def test_model_generation_failure_is_recorded():
    class Boom:
        name = "boom"

        def complete(self, task):
            raise RuntimeError("no server")

    results = run_eval([Boom()], SUBSET[:1], SubprocessExecutor(timeout=5))
    assert results[0].error is True
    assert results[0].outcome == Outcome.RUNTIME_ERROR.value
