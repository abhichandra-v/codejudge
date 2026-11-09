"""The task suite: problem statements plus hidden test suites."""

from __future__ import annotations

from typing import Dict, List

from ..core import Task
from .basics import BASIC_TASKS
from .traps import TRAP_TASKS

ALL_TASKS: List[Task] = TRAP_TASKS + BASIC_TASKS
TASKS_BY_ID: Dict[str, Task] = {t.id: t for t in ALL_TASKS}

# Sanity check: no duplicate ids.
assert len(TASKS_BY_ID) == len(ALL_TASKS), "duplicate task id in suite"

CATEGORIES = sorted({t.category for t in ALL_TASKS})
TRAP_TYPES = sorted({t.trap_type for t in ALL_TASKS if t.trap_type})


def get_tasks(ids=None, categories=None, only_traps=False) -> List[Task]:
    """Filter the suite by id / category / trap flag."""
    tasks = ALL_TASKS
    if only_traps:
        tasks = [t for t in tasks if t.is_trap]
    if categories:
        wanted = set(categories)
        tasks = [t for t in tasks if t.category in wanted]
    if ids:
        wanted = set(ids)
        tasks = [t for t in tasks if t.id in wanted]
    return list(tasks)


__all__ = ["ALL_TASKS", "TASKS_BY_ID", "CATEGORIES", "TRAP_TYPES", "get_tasks"]
