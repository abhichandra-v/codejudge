"""Command-line interface for codejudge."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

from .classify import LABELS, Outcome
from .harness import run_eval, verify_suite
from .providers import make_model
from .report import to_console, to_markdown
from .runner import make_executor
from .task_suite import CATEGORIES, TRAP_TYPES, get_tasks


def _split(value):
    return [v.strip() for v in value.split(",") if v.strip()] if value else None


def cmd_list(args) -> int:
    tasks = get_tasks(
        ids=_split(args.tasks), categories=_split(args.categories), only_traps=args.only_traps
    )
    print(f"{len(tasks)} task(s)  |  categories: {', '.join(CATEGORIES)}")
    print(f"trap types: {', '.join(TRAP_TYPES)}\n")
    width = max((len(t.id) for t in tasks), default=4)
    for t in tasks:
        tag = f"TRAP:{t.trap_type}" if t.is_trap else t.category
        print(f"  {t.id.ljust(width)}  [{tag}]  {t.title}")
    return 0


def _progress(result):
    mark = "PASS" if result.passed else LABELS[Outcome(result.outcome)].upper()
    print(f"  [{result.model}] {result.task_id:<22} {mark}")


def cmd_run(args) -> int:
    tasks = get_tasks(
        ids=_split(args.tasks), categories=_split(args.categories), only_traps=args.only_traps
    )
    if not tasks:
        print("no tasks selected", file=sys.stderr)
        return 1

    try:
        models = [make_model(spec) for spec in _split(args.models)]
    except (ValueError, RuntimeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    executor = make_executor(args.executor, timeout=args.timeout)
    print(f"Running {len(models)} model(s) x {len(tasks)} task(s) "
          f"on the {executor.name} executor (timeout {args.timeout}s)\n")

    results = run_eval(models, tasks, executor, on_result=_progress)

    print()
    print(to_console(results))

    os.makedirs(args.out, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    json_path = os.path.join(args.out, f"results_{stamp}.json")
    md_path = os.path.join(args.out, "report.md")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump([r.as_dict() for r in results], f, indent=2)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(to_markdown(results))
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return 0


def cmd_verify(args) -> int:
    """Run reference solutions to confirm the hidden suites are valid."""
    tasks = get_tasks(
        ids=_split(args.tasks), categories=_split(args.categories), only_traps=args.only_traps
    )
    executor = make_executor(args.executor, timeout=args.timeout)
    print(f"Verifying {len(tasks)} reference solution(s)...\n")
    results = verify_suite(tasks, executor)
    bad = [r for r in results if not r.passed]
    for r in results:
        if not r.passed:
            print(f"  FAIL {r.task_id}: {r.outcome} - {r.note}")
    if bad:
        print(f"\n{len(bad)} task(s) have a broken test suite.", file=sys.stderr)
        return 1
    print(f"All {len(results)} reference solutions pass their own hidden tests.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="codejudge",
        description="Evaluate LLM-written Python code against hidden test suites.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    def add_filters(sp):
        sp.add_argument("--tasks", help="comma-separated task ids to include")
        sp.add_argument("--categories", help="comma-separated categories to include")
        sp.add_argument("--only-traps", action="store_true", help="only trap tasks")

    sp = sub.add_parser("list", help="list the tasks in the suite")
    add_filters(sp)
    sp.set_defaults(func=cmd_list)

    sp = sub.add_parser("run", help="run models against the suite")
    sp.add_argument("--models", default="naive,careful",
                    help="comma-separated model specs (default: naive,careful)")
    sp.add_argument("--timeout", type=float, default=10.0, help="per-task timeout in seconds")
    sp.add_argument("--executor", default="subprocess", choices=["subprocess", "docker"])
    sp.add_argument("--out", default="results", help="output directory")
    add_filters(sp)
    sp.set_defaults(func=cmd_run)

    sp = sub.add_parser("verify", help="check that reference solutions pass their own tests")
    sp.add_argument("--timeout", type=float, default=10.0)
    sp.add_argument("--executor", default="subprocess", choices=["subprocess", "docker"])
    add_filters(sp)
    sp.set_defaults(func=cmd_verify)

    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
