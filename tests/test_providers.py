import pytest

from codejudge.providers import (
    CAREFUL_MISSES,
    MockModel,
    OllamaModel,
    StaticModel,
    build_prompt,
    extract_code,
    make_model,
)
from codejudge.task_suite import TASKS_BY_ID


def test_extract_code_strips_fences():
    text = "Here you go:\n```python\ndef f():\n    return 1\n```\nDone."
    assert extract_code(text) == "def f():\n    return 1\n"


def test_extract_code_picks_block_with_entry_point():
    text = "```python\nx = 1\n```\nand\n```python\ndef target():\n    return 2\n```"
    assert "def target" in extract_code(text, entry_point="target")


def test_extract_code_plain_text_fallback():
    assert extract_code("def f():\n    return 1").strip() == "def f():\n    return 1"


def test_mock_naive_returns_naive_solution():
    task = TASKS_BY_ID["t01_mutable_default"]
    assert MockModel("naive").complete(task) == task.naive_solution


def test_mock_careful_returns_reference_for_most_traps():
    task = TASKS_BY_ID["t01_mutable_default"]
    assert MockModel("careful").complete(task) == task.solution


def test_mock_careful_falls_for_subtle_traps():
    task = TASKS_BY_ID[next(iter(CAREFUL_MISSES))]
    assert MockModel("careful").complete(task) == task.naive_solution


def test_build_prompt_mentions_entry_point():
    task = TASKS_BY_ID["b01_fizzbuzz"]
    prompt = build_prompt(task)
    assert task.entry_point in prompt and "function" in prompt


def test_make_model_mock():
    assert isinstance(make_model("naive"), MockModel)
    assert make_model("careful").name == "mock-careful"


def test_make_model_ollama_spec():
    m = make_model("ollama:llama3.1")
    assert isinstance(m, OllamaModel) and m.name == "ollama:llama3.1"


def test_make_model_unknown_raises():
    with pytest.raises(ValueError):
        make_model("banana:x")
    with pytest.raises(ValueError):
        make_model("nonsense")


def test_static_model_reads_solution(tmp_path):
    task = TASKS_BY_ID["b01_fizzbuzz"]
    (tmp_path / f"{task.id}.py").write_text("def fizzbuzz(n):\n    return []\n")
    model = StaticModel("claude", str(tmp_path))
    assert model.name == "claude"
    assert "def fizzbuzz" in model.complete(task)


def test_static_model_missing_file_raises(tmp_path):
    task = TASKS_BY_ID["b01_fizzbuzz"]
    with pytest.raises(FileNotFoundError):
        StaticModel("claude", str(tmp_path)).complete(task)
