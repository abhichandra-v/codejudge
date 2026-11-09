"""Orchestration: generate solutions, run them, classify, collect results."""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional

from .classify import Outcome, classify
from .core import Task


@dataclass
class TaskResult:
    model: str
    task_id: str
    title: str
    category: str
    is_trap: bool
    trap_type: Optional[str]
    outcome: str  # Outcome value
    note: str
    duration: float
    source: str
    error: bool = False  # True if the model failed to even produce a solution

    @property
    def passed(self) -> bool:
        return self.outcome == Outcome.PASS.value

    def as_dict(self) -> Dict:
        return asdict(self)


def _generate(model, task: Task):
    """Return (source, gen_error). gen_error is set if the model call failed."""
    try:
        return model.complete(task), None
    except Exception as e:  # noqa: BLE001 - network/model errors must not abort the run
        return None, f"{type(e).__name__}: {e}"


def run_eval(models, tasks: List[Task], executor, on_result=None) -> List[TaskResult]:
    """Evaluate every model against every task; return a flat list of results.

    ``on_result`` is an optional callback invoked with each TaskResult as it is
    produced (useful for progress output).
    """
    results: List[TaskResult] = []
    for model in models:
        for task in tasks:
            start = time.perf_counter()
            source, gen_error = _generate(model, task)
            if gen_error is not None:
                result = TaskResult(
                    model=model.name, task_id=task.id, title=task.title,
                    category=task.category, is_trap=task.is_trap, trap_type=task.trap_type,
                    outcome=Outcome.RUNTIME_ERROR.value,
                    note=f"model failed to produce a solution: {gen_error}",
                    duration=time.perf_counter() - start, source="", error=True,
                )
            else:
                raw = executor.run(task, source)
                outcome, note = classify(raw)
                result = TaskResult(
                    model=model.name, task_id=task.id, title=task.title,
                    category=task.category, is_trap=task.is_trap, trap_type=task.trap_type,
                    outcome=outcome.value, note=note,
                    duration=time.perf_counter() - start, source=source,
                )
            results.append(result)
            if on_result:
                on_result(result)
    return results


def verify_suite(tasks: List[Task], executor) -> List[TaskResult]:
    """Run each task's *reference* solution through the executor.

    Every task should PASS; anything else means a bug in the task's own hidden
    test suite.
    """
    class _Reference:
        name = "reference"

        def complete(self, task):  # always the canonical correct solution
            return task.solution

    return run_eval([_Reference()], tasks, executor)
