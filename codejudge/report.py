"""Turn a list of :class:`TaskResult` into summaries and a Markdown report."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List

from .classify import LABELS, Outcome
from .harness import TaskResult

_OUTCOME_ORDER = [
    Outcome.PASS, Outcome.WRONG_ANSWER, Outcome.EDGE_CASE_FAILURE,
    Outcome.TIMEOUT, Outcome.RUNTIME_ERROR,
]


def _rate(passed: int, total: int) -> str:
    if total == 0:
        return "-"
    return f"{passed}/{total} ({100 * passed / total:.0f}%)"


def _models(results: List[TaskResult]) -> List[str]:
    seen = []
    for r in results:
        if r.model not in seen:
            seen.append(r.model)
    return seen


def _md_table(headers: List[str], rows: List[List[str]]) -> str:
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))

    def fmt(cells):
        return "| " + " | ".join(str(c).ljust(widths[i]) for i, c in enumerate(cells)) + " |"

    sep = "| " + " | ".join("-" * widths[i] for i in range(len(headers))) + " |"
    return "\n".join([fmt(headers), sep] + [fmt(r) for r in rows])


def summarize(results: List[TaskResult]) -> Dict:
    """Compute aggregate statistics from results."""
    models = _models(results)
    by_model = {m: [r for r in results if r.model == m] for m in models}

    overall = {}
    outcomes = {}
    by_category = {}
    for m, rs in by_model.items():
        overall[m] = {"passed": sum(r.passed for r in rs), "total": len(rs)}
        outcomes[m] = {o.value: sum(r.outcome == o.value for r in rs) for o in _OUTCOME_ORDER}
        cat = defaultdict(lambda: [0, 0])
        for r in rs:
            cat[r.category][1] += 1
            cat[r.category][0] += int(r.passed)
        by_category[m] = {c: {"passed": p, "total": t} for c, (p, t) in cat.items()}

    return {
        "models": models,
        "overall": overall,
        "outcomes": outcomes,
        "by_category": by_category,
    }


def to_markdown(results: List[TaskResult]) -> str:
    models = _models(results)
    summ = summarize(results)
    categories = sorted({r.category for r in results})
    trap_results = [r for r in results if r.is_trap]
    trap_ids = []
    for r in trap_results:
        if r.task_id not in trap_ids:
            trap_ids.append(r.task_id)

    lines: List[str] = []
    lines.append("# codejudge results")
    lines.append("")
    lines.append(f"_Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}_")
    lines.append("")

    # Overall
    lines.append("## Overall pass rate")
    lines.append("")
    lines.append(_md_table(
        ["model", "pass rate"],
        [[m, _rate(summ["overall"][m]["passed"], summ["overall"][m]["total"])] for m in models],
    ))
    lines.append("")

    # By category
    lines.append("## Pass rate by category")
    lines.append("")
    rows = []
    for c in categories:
        row = [c]
        for m in models:
            cell = summ["by_category"][m].get(c)
            row.append(_rate(cell["passed"], cell["total"]) if cell else "-")
        rows.append(row)
    lines.append(_md_table(["category"] + models, rows))
    lines.append("")

    # Failure breakdown
    lines.append("## Failure breakdown")
    lines.append("")
    rows = []
    for o in _OUTCOME_ORDER:
        rows.append([LABELS[o]] + [str(summ["outcomes"][m][o.value]) for m in models])
    lines.append(_md_table(["outcome"] + models, rows))
    lines.append("")

    # Trap table
    lines.append("## Which traps fooled each model")
    lines.append("")
    lines.append("A trap is 'fooled' when the model does not PASS. `edge` means it "
                 "passed the obvious cases but failed the edge case the trap targets.")
    lines.append("")
    index = {(r.model, r.task_id): r for r in results}
    rows = []
    for tid in trap_ids:
        sample = next(r for r in trap_results if r.task_id == tid)
        row = [tid, sample.trap_type or ""]
        for m in models:
            r = index.get((m, tid))
            if r is None:
                row.append("-")
            elif r.passed:
                row.append("ok")
            else:
                short = {
                    Outcome.EDGE_CASE_FAILURE.value: "FOOLED (edge)",
                    Outcome.WRONG_ANSWER.value: "FOOLED (wrong)",
                    Outcome.TIMEOUT.value: "FOOLED (timeout)",
                    Outcome.RUNTIME_ERROR.value: "FOOLED (error)",
                }.get(r.outcome, "FOOLED")
                row.append(short)
        rows.append(row)
    lines.append(_md_table(["trap", "trap type"] + models, rows))
    lines.append("")

    n_traps = len(trap_ids)
    for m in models:
        fooled = sum(1 for tid in trap_ids if not index[(m, tid)].passed)
        lines.append(f"- **{m}**: fooled by {fooled}/{n_traps} traps.")
    lines.append("")

    return "\n".join(lines)


def to_console(results: List[TaskResult]) -> str:
    """A compact plain-text summary for the terminal."""
    models = _models(results)
    summ = summarize(results)
    trap_ids = []
    for r in results:
        if r.is_trap and r.task_id not in trap_ids:
            trap_ids.append(r.task_id)
    index = {(r.model, r.task_id): r for r in results}

    out = []
    out.append("=" * 60)
    out.append("codejudge summary")
    out.append("=" * 60)
    for m in models:
        ov = summ["overall"][m]
        out.append(f"\n{m}: {_rate(ov['passed'], ov['total'])}")
        for o in _OUTCOME_ORDER:
            n = summ["outcomes"][m][o.value]
            if n:
                out.append(f"    {LABELS[o]:<18} {n}")
        fooled = sum(1 for tid in trap_ids if not index[(m, tid)].passed)
        out.append(f"    traps fooled       {fooled}/{len(trap_ids)}")
    out.append("")
    return "\n".join(out)
