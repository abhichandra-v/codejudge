"""Subprocess entry point that executes one candidate solution.

Run as::

    python _sandbox_runner.py <task_id> <source_path> <result_path>

It compiles and executes the candidate source in a throwaway namespace, runs
every hidden case for the task, and writes a JSON result to ``result_path``.
It never trusts the candidate's stdout: results only ever travel through the
result file. The parent process applies the wall-clock timeout and kills this
process if it runs too long (that is how infinite loops / pathological
recursion are caught).
"""

from __future__ import annotations

import json
import os
import sys


def _write(path, payload):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f)


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: _sandbox_runner.py <task_id> <source_path> <result_path>", file=sys.stderr)
        return 2

    task_id, source_path, result_path = sys.argv[1], sys.argv[2], sys.argv[3]

    # Make the codejudge package importable regardless of how we were launched.
    pkg_parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if pkg_parent not in sys.path:
        sys.path.insert(0, pkg_parent)

    from codejudge.task_suite import TASKS_BY_ID

    task = TASKS_BY_ID[task_id]

    with open(source_path, "r", encoding="utf-8") as f:
        source = f.read()

    # Compile the candidate (syntax errors are a distinct, clean signal).
    try:
        compiled = compile(source, "<solution>", "exec")
    except SyntaxError as e:
        _write(result_path, {"phase": "compile_error", "error": f"{type(e).__name__}: {e}"})
        return 0

    namespace: dict = {}
    try:
        exec(compiled, namespace)  # noqa: S102 - executing model code is the whole point
    except Exception as e:  # noqa: BLE001
        _write(result_path, {"phase": "load_error", "error": f"{type(e).__name__}: {e}"})
        return 0

    func = namespace.get(task.entry_point)
    if not callable(func):
        _write(
            result_path,
            {"phase": "no_entry_point", "error": f"function {task.entry_point!r} was not defined"},
        )
        return 0

    results = {"phase": "ok", "cases": []}
    for case in task.cases:
        record = {"name": case.name, "edge": case.edge}
        try:
            case.fn(func)
            record["status"] = "pass"
        except AssertionError as e:
            record["status"] = "fail"
            record["detail"] = str(e) or "assertion failed"
        except Exception as e:  # noqa: BLE001
            record["status"] = "error"
            record["detail"] = f"{type(e).__name__}: {e}"
        results["cases"].append(record)

    _write(result_path, results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
