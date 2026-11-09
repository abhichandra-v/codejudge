"""Failure classification.

Turns a raw execution result (produced by an executor, see :mod:`runner`) into
one of a small set of outcomes plus a short human-readable note.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, Tuple


class Outcome(str, Enum):
    PASS = "pass"
    WRONG_ANSWER = "wrong_answer"
    EDGE_CASE_FAILURE = "edge_case_failure"
    TIMEOUT = "timeout"
    RUNTIME_ERROR = "runtime_error"

    def __str__(self) -> str:  # nicer printing
        return self.value


#: Short labels for reports.
LABELS = {
    Outcome.PASS: "pass",
    Outcome.WRONG_ANSWER: "wrong answer",
    Outcome.EDGE_CASE_FAILURE: "edge-case failure",
    Outcome.TIMEOUT: "timeout",
    Outcome.RUNTIME_ERROR: "runtime error",
}


def classify(raw: Dict) -> Tuple[Outcome, str]:
    """Map a raw execution result to ``(Outcome, note)``.

    ``raw`` is a dict with a ``phase`` key:

    * ``timeout``                  -> TIMEOUT
    * ``compile_error`` / ``load_error`` / ``no_entry_point`` / ``crash``
                                   -> RUNTIME_ERROR
    * ``ok`` with a ``cases`` list -> inspected case by case
    """
    phase = raw.get("phase")

    if phase == "timeout":
        return Outcome.TIMEOUT, "execution exceeded the time limit"

    if phase == "compile_error":
        return Outcome.RUNTIME_ERROR, f"solution did not compile: {raw.get('error', '')}"
    if phase == "load_error":
        return Outcome.RUNTIME_ERROR, f"error while loading solution: {raw.get('error', '')}"
    if phase == "no_entry_point":
        return Outcome.RUNTIME_ERROR, raw.get("error", "entry-point function not defined")
    if phase == "crash":
        return Outcome.RUNTIME_ERROR, f"interpreter crashed: {raw.get('error', '')}"

    if phase != "ok":
        return Outcome.RUNTIME_ERROR, f"unexpected execution phase: {phase!r}"

    cases = raw.get("cases", [])
    if not cases:
        return Outcome.RUNTIME_ERROR, "no test cases were executed"

    errors = [c for c in cases if c.get("status") == "error"]
    fails = [c for c in cases if c.get("status") == "fail"]

    if not errors and not fails:
        return Outcome.PASS, f"all {len(cases)} cases passed"

    # A thrown exception on any case is a runtime error first and foremost.
    if errors:
        first = errors[0]
        return (
            Outcome.RUNTIME_ERROR,
            f"{len(errors)} case(s) raised; e.g. '{first['name']}': {first.get('detail', '')}",
        )

    # Only assertion failures remain. If an *obvious* (non-edge) case failed the
    # solution is simply wrong; if every failure is on an edge case, the model
    # fell into the trap.
    obvious_fail = [c for c in fails if not c.get("edge")]
    first = fails[0]
    note = f"failed '{first['name']}': {first.get('detail', '')}"
    if obvious_fail:
        return Outcome.WRONG_ANSWER, note
    return Outcome.EDGE_CASE_FAILURE, note
