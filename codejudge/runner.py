"""Executors that run candidate code in a sandbox and return a raw result.

The default :class:`SubprocessExecutor` runs each solution in a fresh Python
process with a wall-clock timeout, so model code never runs inside the harness
process. :class:`DockerExecutor` adds OS-level isolation (no network, capped
memory/CPU) and is recommended when evaluating untrusted model output.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from typing import Dict

from .core import Task

_RUNNER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_sandbox_runner.py")
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@dataclass
class SubprocessExecutor:
    """Run candidate solutions in a subprocess with a timeout.

    This isolates crashes and infinite loops from the harness but shares the
    host filesystem, so only run code you are willing to execute locally. Use
    :class:`DockerExecutor` for stronger isolation.
    """

    timeout: float = 10.0
    python: str = sys.executable

    name = "subprocess"

    def run(self, task: Task, source: str) -> Dict:
        with tempfile.TemporaryDirectory(prefix="codejudge_") as workdir:
            src_path = os.path.join(workdir, "solution.py")
            res_path = os.path.join(workdir, "result.json")
            with open(src_path, "w", encoding="utf-8") as f:
                f.write(source)

            cmd = [self.python, _RUNNER, task.id, src_path, res_path]
            try:
                proc = subprocess.run(
                    cmd,
                    cwd=workdir,  # empty dir: candidate relative file ops stay contained
                    timeout=self.timeout,
                    capture_output=True,
                    text=True,
                )
            except subprocess.TimeoutExpired:
                return {"phase": "timeout"}

            if not os.path.exists(res_path):
                detail = (proc.stderr or "").strip()[-800:] or f"exit code {proc.returncode}"
                return {"phase": "crash", "error": detail}

            try:
                with open(res_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (OSError, json.JSONDecodeError) as e:
                return {"phase": "crash", "error": f"could not read result file: {e}"}


@dataclass
class DockerExecutor:
    """Run candidate solutions inside a disposable Docker container.

    Requires Docker to be installed and running. The repository is mounted
    read-only; the container has no network and limited memory/CPU.
    """

    timeout: float = 10.0
    image: str = "python:3.11-slim"
    memory: str = "256m"
    cpus: str = "1.0"

    name = "docker"

    @staticmethod
    def available() -> bool:
        return shutil.which("docker") is not None

    def run(self, task: Task, source: str) -> Dict:
        with tempfile.TemporaryDirectory(prefix="codejudge_") as workdir:
            src_path = os.path.join(workdir, "solution.py")
            with open(src_path, "w", encoding="utf-8") as f:
                f.write(source)

            res_name = "result.json"
            res_host = os.path.join(workdir, res_name)

            cmd = [
                "docker", "run", "--rm",
                "--network", "none",
                "--memory", self.memory,
                "--cpus", self.cpus,
                "--pids-limit", "128",
                "-v", f"{_REPO_ROOT}:/repo:ro",
                "-v", f"{workdir}:/work",
                "-w", "/work",
                self.image,
                "python", "/repo/codejudge/_sandbox_runner.py",
                task.id, "/work/solution.py", f"/work/{res_name}",
            ]
            try:
                proc = subprocess.run(
                    cmd, timeout=self.timeout + 15, capture_output=True, text=True
                )
            except subprocess.TimeoutExpired:
                return {"phase": "timeout"}

            if not os.path.exists(res_host):
                detail = (proc.stderr or "").strip()[-800:] or f"exit code {proc.returncode}"
                # Distinguish an in-container timeout signalled by docker from a crash.
                if "timeout" in detail.lower():
                    return {"phase": "timeout"}
                return {"phase": "crash", "error": detail}

            try:
                with open(res_host, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (OSError, json.JSONDecodeError) as e:
                return {"phase": "crash", "error": f"could not read result file: {e}"}


def make_executor(kind: str, timeout: float) -> object:
    kind = kind.lower()
    if kind == "subprocess":
        return SubprocessExecutor(timeout=timeout)
    if kind == "docker":
        return DockerExecutor(timeout=timeout)
    raise ValueError(f"unknown executor: {kind!r} (expected 'subprocess' or 'docker')")
