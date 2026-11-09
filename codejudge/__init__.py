"""codejudge: a sandboxed harness for evaluating LLM-written Python code."""

from __future__ import annotations

from .classify import Outcome, classify
from .core import Case, Task
from .harness import TaskResult, run_eval, verify_suite
from .runner import DockerExecutor, SubprocessExecutor

__version__ = "0.1.0"

__all__ = [
    "Task",
    "Case",
    "Outcome",
    "classify",
    "run_eval",
    "verify_suite",
    "TaskResult",
    "SubprocessExecutor",
    "DockerExecutor",
    "__version__",
]
