"""Generation matrix tests for seedling copier template."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALL_JUSTFILE_TARGETS = (
    '["test-cov","e2e","pre-commit","commitizen","complexity","vulture",'
    '"darglint","docstr-coverage","audit","bandit","radon","find-dupes",'
    '"docs-frontmatter-fix"]'
)


def _run(
    args: list[str],
    *,
    cwd: Path,
    timeout: int = 120,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env.pop("VIRTUAL_ENV", None)
    result = subprocess.run(
        args,
        cwd=cwd,
        text=True,
        input=input_text,
        capture_output=True,
        timeout=timeout,
        env=env,
        check=False,
    )
    if result.returncode != 0:
        cmd = " ".join(args)
        raise AssertionError(
            f"Command failed ({result.returncode}): {cmd}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return result


def _render_project(
    tmp_path: Path,
    *,
    cli_mode: str,
    include_ai_workflow: bool = True,
    extra_answers: dict[str, str] | None = None,
) -> Path:
    destination = tmp_path / f"{cli_mode}-{'ai' if include_ai_workflow else 'no-ai'}"
    project_slug = f"sample-{cli_mode}"
    package_name = project_slug.replace("-", "_")
    cli_name = f"{cli_mode}app"

    args = [
        sys.executable,
        "-m",
        "copier",
        "copy",
        str(ROOT),
        str(destination),
        "--trust",
        "-d",
        f"project_name=Sample {cli_mode.title()}",
        "-d",
        f"project_slug={project_slug}",
        "-d",
        f"package_name={package_name}",
        "-d",
        f"cli_mode={cli_mode}",
        "-d",
        f"include_ai_workflow={str(include_ai_workflow).lower()}",
    ]
    if cli_mode != "none":
        args.extend(["-d", f"cli_name={cli_name}"])
    answers = {"justfile_targets": ALL_JUSTFILE_TARGETS}
    if extra_answers:
        answers.update(extra_answers)
    for key, value in answers.items():
        args.extend(["-d", f"{key}={value}"])

    _run(args, cwd=ROOT)
    return destination


def test_copy_matrix_none(tmp_path: Path) -> None:
    project = _render_project(tmp_path, cli_mode="none")
    package_name = "sample_none"

    assert (project / f"src/{package_name}/__init__.py").exists()
    assert not (project / f"src/{package_name}/cli.py").exists()
    assert not (project / "tests/unit/test_cli.py").exists()

    pyproject = (project / "pyproject.toml").read_text(encoding="utf-8")
    assert "[project.scripts]" not in pyproject

    _run(["uv", "run", "pytest", "-q"], cwd=project)


def test_copy_matrix_command(tmp_path: Path) -> None:
    project = _render_project(tmp_path, cli_mode="command")
    package_name = "sample_command"

    assert (project / f"src/{package_name}/cli.py").exists()
    assert (project / "tests/unit/test_cli.py").exists()

    pyproject = (project / "pyproject.toml").read_text(encoding="utf-8")
    assert "[project.scripts]" in pyproject
    assert 'commandapp = "sample_command.cli:app"' in pyproject

    result = _run(["uv", "run", "commandapp", "hello", "--name", "matrix"], cwd=project)
    assert "hello, matrix" in result.stdout

    _run(["uv", "run", "pytest", "-q"], cwd=project)


def test_copy_matrix_repl(tmp_path: Path) -> None:
    project = _render_project(tmp_path, cli_mode="repl")
    package_name = "sample_repl"

    assert (project / f"src/{package_name}/cli.py").exists()
    assert (project / "tests/unit/test_cli.py").exists()

    pyproject = (project / "pyproject.toml").read_text(encoding="utf-8")
    assert "[project.scripts]" in pyproject
    assert 'replapp = "sample_repl.cli:app"' in pyproject
    assert '"textual>=0.80.0"' in pyproject

    root_help = _run(["uv", "run", "replapp", "--help"], cwd=project)
    assert "repl" in root_help.stdout
    repl_help = _run(["uv", "run", "replapp", "repl", "--help"], cwd=project)
    assert "Run a tiny Textual-backed REPL loop." in repl_help.stdout

    _run(["uv", "run", "pytest", "-q"], cwd=project)


def test_copy_matrix_ai_toggle(tmp_path: Path) -> None:
    with_ai = _render_project(tmp_path, cli_mode="command", include_ai_workflow=True)
    without_ai = _render_project(tmp_path, cli_mode="command", include_ai_workflow=False)

    assert (with_ai / ".ai").is_dir()
    assert (with_ai / ".ai/COMMANDS").is_dir()
    assert (with_ai / ".ai/REF").is_dir()
    assert (with_ai / ".ai/RULES.md").is_file()
    assert (with_ai / ".ai/HUMAN_RUNBOOK.md").is_file()
    assert not (with_ai / ".ai/PLANS").exists()

    assert not (without_ai / ".ai").exists()


def test_copy_matrix_optional_target_toggles(tmp_path: Path) -> None:
    project = _render_project(
        tmp_path,
        cli_mode="command",
        extra_answers={
            "justfile_targets": "[]",
        },
    )

    justfile = (project / "justfile").read_text(encoding="utf-8")
    assert "test-cov:" not in justfile
    assert "e2e:" not in justfile
    assert "pre-commit-install:" not in justfile
    assert "commit:" not in justfile
    assert "complexity:" not in justfile
    assert "vulture:" not in justfile
    assert "darglint:" not in justfile
    assert "docstr-coverage:" not in justfile
    assert "audit:" not in justfile
    assert "bandit:" not in justfile
    assert "radon:" not in justfile
    assert "find-dupes:" not in justfile
    assert "docs-frontmatter-fix:" not in justfile

    pyproject = (project / "pyproject.toml").read_text(encoding="utf-8")
    assert "pytest-cov" not in pyproject
    assert "pre-commit" not in pyproject
    assert "commitizen" not in pyproject
    assert "xenon" not in pyproject
    assert "vulture" not in pyproject
    assert "darglint" not in pyproject
    assert "docstr-coverage" not in pyproject
    assert "pip-audit" not in pyproject
    assert "bandit" not in pyproject
    assert "radon" not in pyproject
    assert "pylint" not in pyproject
