"""Tests for the subprocess executor + classification end to end."""

from codejudge.classify import Outcome, classify
from codejudge.runner import SubprocessExecutor
from codejudge.task_suite import TASKS_BY_ID

TASK = TASKS_BY_ID["b18_inclusive_range"]  # entry point: inclusive_range(a, b)


def run(source, timeout=10.0):
    raw = SubprocessExecutor(timeout=timeout).run(TASK, source)
    return classify(raw)[0]


def test_correct_solution_passes():
    assert run(TASK.solution) is Outcome.PASS


def test_wrong_answer():
    outcome = run("def inclusive_range(a, b):\n    return []\n")
    assert outcome is Outcome.WRONG_ANSWER


def test_runtime_error():
    outcome = run("def inclusive_range(a, b):\n    raise ValueError('boom')\n")
    assert outcome is Outcome.RUNTIME_ERROR


def test_syntax_error():
    outcome = run("def inclusive_range(a, b)\n    return []\n")  # missing colon
    assert outcome is Outcome.RUNTIME_ERROR


def test_missing_entry_point():
    outcome = run("def something_else():\n    return 1\n")
    assert outcome is Outcome.RUNTIME_ERROR


def test_timeout():
    outcome = run("def inclusive_range(a, b):\n    while True:\n        pass\n", timeout=2.0)
    assert outcome is Outcome.TIMEOUT
