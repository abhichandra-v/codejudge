from codejudge.classify import Outcome, classify


def ok(cases):
    return {"phase": "ok", "cases": cases}


def case(name, status, edge=False, detail=""):
    c = {"name": name, "edge": edge, "status": status}
    if detail:
        c["detail"] = detail
    return c


def test_all_pass():
    outcome, _ = classify(ok([case("a", "pass"), case("b", "pass", edge=True)]))
    assert outcome is Outcome.PASS


def test_obvious_failure_is_wrong_answer():
    outcome, note = classify(ok([case("a", "fail", detail="x"), case("b", "pass", edge=True)]))
    assert outcome is Outcome.WRONG_ANSWER
    assert "a" in note


def test_edge_only_failure_is_edge_case_failure():
    outcome, _ = classify(ok([case("a", "pass"), case("edge", "fail", edge=True, detail="boom")]))
    assert outcome is Outcome.EDGE_CASE_FAILURE


def test_exception_is_runtime_error():
    outcome, _ = classify(ok([case("a", "pass"), case("b", "error", detail="KeyError")]))
    assert outcome is Outcome.RUNTIME_ERROR


def test_exception_beats_assertion():
    outcome, _ = classify(ok([case("a", "fail"), case("b", "error", detail="Boom")]))
    assert outcome is Outcome.RUNTIME_ERROR


def test_timeout():
    assert classify({"phase": "timeout"})[0] is Outcome.TIMEOUT


def test_compile_error_is_runtime_error():
    assert classify({"phase": "compile_error", "error": "SyntaxError"})[0] is Outcome.RUNTIME_ERROR


def test_no_entry_point_is_runtime_error():
    assert classify({"phase": "no_entry_point", "error": "missing"})[0] is Outcome.RUNTIME_ERROR


def test_crash_is_runtime_error():
    assert classify({"phase": "crash", "error": "segfault"})[0] is Outcome.RUNTIME_ERROR


def test_empty_cases_is_runtime_error():
    assert classify(ok([]))[0] is Outcome.RUNTIME_ERROR
