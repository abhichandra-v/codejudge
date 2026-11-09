"""Models that turn a task into candidate Python source.

A "model" is anything with a ``name`` attribute and a ``complete(task) -> str``
method returning source code. Three kinds are provided:

* :class:`MockModel` -- offline, deterministic. ``careful`` returns the
  reference solution (and falls for a couple of the subtlest traps); ``naive``
  returns a plausible-but-wrong solution for every trap. Great for demos and
  for testing the harness without a model server.
* :class:`OllamaModel` -- a local model served by Ollama.
* :class:`OpenAIChatModel` / :class:`AnthropicModel` -- hosted APIs (key read
  from an environment variable).

Only stdlib is used for HTTP so the package has no hard runtime dependencies.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Optional

from .core import Task

# Traps subtle enough that even the "careful" mock model falls for them.
CAREFUL_MISSES = {"t04_unicode_casefold", "t10_bankers_rounding"}


def build_prompt(task: Task) -> str:
    return (
        "You are an expert Python programmer. Solve the problem by writing a "
        "single Python function.\n\n"
        f"Problem:\n{task.prompt}\n\n"
        "Requirements:\n"
        f"- Define exactly one function named `{task.entry_point}`.\n"
        "- Do not read input() or print anything; just return the result.\n"
        "- Do not include tests or usage examples.\n"
        "- Respond with only a single Python code block."
    )


_FENCE_RE = re.compile(r"```(?:python|py)?\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)


def extract_code(text: str, entry_point: Optional[str] = None) -> str:
    """Pull Python source out of a model response.

    Prefers a fenced code block (the one that defines ``entry_point`` if given),
    otherwise returns the stripped text.
    """
    blocks = [m.group(1) for m in _FENCE_RE.finditer(text)]
    if blocks:
        if entry_point:
            for b in blocks:
                if re.search(rf"\bdef\s+{re.escape(entry_point)}\b", b):
                    return b.strip() + "\n"
        return blocks[0].strip() + "\n"
    return text.strip() + "\n"


# --- static (solutions written to a directory) -----------------------------

class StaticModel:
    """Serve pre-written solutions from a directory of ``<task_id>.py`` files.

    Lets you judge any model's output offline: dump each solution to
    ``<directory>/<task_id>.py`` and point a StaticModel at it. A task with no
    file is reported as a failure to produce a solution (a fair "no answer").
    """

    def __init__(self, name: str, directory: str):
        self.name = name
        self.directory = directory

    def complete(self, task: Task) -> str:
        path = os.path.join(self.directory, f"{task.id}.py")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()


# --- mock (offline) --------------------------------------------------------

class MockModel:
    """Deterministic offline model. ``variant`` is 'naive' or 'careful'."""

    def __init__(self, variant: str = "careful"):
        if variant not in ("naive", "careful"):
            raise ValueError("variant must be 'naive' or 'careful'")
        self.variant = variant
        self.name = f"mock-{variant}"

    def complete(self, task: Task) -> str:
        if self.variant == "naive":
            return task.naive_solution or task.solution
        # careful: reference solution, except it still trips on the subtlest traps
        if task.id in CAREFUL_MISSES and task.naive_solution:
            return task.naive_solution
        return task.solution


# --- HTTP helpers ----------------------------------------------------------

def _post_json(url: str, payload: dict, headers: dict, timeout: float = 120.0) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - fixed scheme
        return json.loads(resp.read().decode("utf-8"))


# --- Ollama ----------------------------------------------------------------

class OllamaModel:
    def __init__(self, model: str, host: Optional[str] = None, temperature: float = 0.0):
        self.model = model
        self.host = (host or os.environ.get("OLLAMA_HOST") or "http://localhost:11434").rstrip("/")
        self.temperature = temperature
        self.name = f"ollama:{model}"

    def complete(self, task: Task) -> str:
        payload = {
            "model": self.model,
            "prompt": build_prompt(task),
            "stream": False,
            "options": {"temperature": self.temperature},
        }
        out = _post_json(f"{self.host}/api/generate", payload, {"Content-Type": "application/json"})
        return extract_code(out.get("response", ""), task.entry_point)


# --- OpenAI-compatible chat API -------------------------------------------

class OpenAIChatModel:
    def __init__(self, model: str, base_url: Optional[str] = None,
                 api_key_env: str = "OPENAI_API_KEY", temperature: float = 0.0):
        self.model = model
        self.base_url = (base_url or os.environ.get("OPENAI_BASE_URL")
                         or "https://api.openai.com/v1").rstrip("/")
        self.api_key = os.environ.get(api_key_env)
        self.temperature = temperature
        self.name = f"openai:{model}"
        if not self.api_key:
            raise RuntimeError(f"environment variable {api_key_env} is not set")

    def complete(self, task: Task) -> str:
        payload = {
            "model": self.model,
            "temperature": self.temperature,
            "messages": [{"role": "user", "content": build_prompt(task)}],
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        out = _post_json(f"{self.base_url}/chat/completions", payload, headers)
        content = out["choices"][0]["message"]["content"]
        return extract_code(content, task.entry_point)


# --- Anthropic Messages API ------------------------------------------------

class AnthropicModel:
    def __init__(self, model: str, api_key_env: str = "ANTHROPIC_API_KEY",
                 max_tokens: int = 1024, temperature: float = 0.0):
        self.model = model
        self.api_key = os.environ.get(api_key_env)
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.name = f"anthropic:{model}"
        if not self.api_key:
            raise RuntimeError(f"environment variable {api_key_env} is not set")

    def complete(self, task: Task) -> str:
        payload = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [{"role": "user", "content": build_prompt(task)}],
        }
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        }
        out = _post_json("https://api.anthropic.com/v1/messages", payload, headers)
        parts = [b.get("text", "") for b in out.get("content", []) if b.get("type") == "text"]
        return extract_code("".join(parts), task.entry_point)


# --- spec parsing ----------------------------------------------------------

def make_model(spec: str):
    """Build a model from a short spec string.

    Examples::

        naive                 careful                 mock:naive
        ollama:llama3.1       ollama:qwen2.5-coder
        openai:gpt-4o-mini    anthropic:claude-3-5-sonnet-20241022
    """
    spec = spec.strip()
    if spec in ("naive", "careful"):
        return MockModel(spec)

    if ":" not in spec:
        raise ValueError(
            f"unknown model spec {spec!r}; use 'naive', 'careful', or '<provider>:<model>'"
        )

    provider, model = spec.split(":", 1)
    provider = provider.lower()
    if provider == "mock":
        return MockModel(model)
    if provider == "ollama":
        return OllamaModel(model)
    if provider == "openai":
        return OpenAIChatModel(model)
    if provider == "anthropic":
        return AnthropicModel(model)
    raise ValueError(f"unknown provider {provider!r} in spec {spec!r}")
