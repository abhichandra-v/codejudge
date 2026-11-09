"""Core data model for the codejudge harness.

A :class:`Task` is a problem statement plus a *hidden* test suite (a list of
:class:`Case` objects). The problem statement is the only thing shown to a
model; the cases are run against whatever code the model writes.

Each case is a callable that receives the candidate function and either returns
normally (pass), raises ``AssertionError`` (wrong answer) or raises any other
exception (runtime error). Cases flagged ``edge=True`` are the tricky boundary
cases that distinguish a careful solution from a plausible-but-wrong one.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional


@dataclass
class Case:
    """A single hidden test.

    ``fn`` is given the candidate function and should assert on its behaviour.
    """

    name: str
    fn: Callable[[Callable[..., Any]], None]
    edge: bool = False


@dataclass
class Task:
    id: str
    title: str
    category: str
    prompt: str
    entry_point: str
    solution: str  # reference (correct) source
    cases: List[Case] = field(default_factory=list)
    is_trap: bool = False
    trap_type: Optional[str] = None
    naive_solution: Optional[str] = None  # a plausible-but-wrong source
    trap_note: Optional[str] = None  # human explanation of the trap

    @property
    def obvious_cases(self) -> List[Case]:
        return [c for c in self.cases if not c.edge]

    @property
    def edge_cases(self) -> List[Case]:
        return [c for c in self.cases if c.edge]


# --- case builders ---------------------------------------------------------

def eq(args, expected, *, edge: bool = False, kwargs=None, name: Optional[str] = None) -> Case:
    """Case asserting ``func(*args, **kwargs) == expected``."""
    kwargs = kwargs or {}

    def fn(func):
        # Deep-copy so a function that mutates its arguments in place cannot
        # corrupt the stored fixtures; cases stay idempotent across runs.
        got = func(*copy.deepcopy(args), **copy.deepcopy(kwargs))
        assert got == expected, f"{func.__name__}{tuple(args)} -> {got!r}, expected {expected!r}"

    label = name or f"{tuple(args)} == {expected!r}"
    return Case(name=label, fn=fn, edge=edge)


def raises(args, exc, *, edge: bool = False, name: Optional[str] = None) -> Case:
    """Case asserting ``func(*args)`` raises ``exc``."""

    def fn(func):
        try:
            func(*args)
        except exc:
            return
        except Exception as e:  # noqa: BLE001
            raise AssertionError(
                f"expected {exc.__name__}, got {type(e).__name__}: {e}"
            )
        raise AssertionError(f"expected {exc.__name__}, but no exception was raised")

    return Case(name=name or f"{tuple(args)} raises {exc.__name__}", fn=fn, edge=edge)


def check(fn: Callable[[Callable[..., Any]], None], name: str, *, edge: bool = False) -> Case:
    """Case wrapping a custom assertion function."""
    return Case(name=name, fn=fn, edge=edge)
