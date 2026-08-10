import json
from pathlib import Path

import pytest

from scripts.python_source_state import (
    DEFAULT_MANIFEST,
    ROOT,
    SourceStateError,
    compile_selected_sources,
    load_source_state,
    require_target_runtime,
)
from scripts.verify_repository import CI_CORRECTNESS_TESTS, RUFF_PATHS, _correctness_commands


def _write_manifest(tmp_path: Path, value: dict) -> Path:
    path = tmp_path / "python-source-state.json"
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def _minimal_manifest(tmp_path: Path) -> tuple[Path, dict]:
    (tmp_path / "safe").mkdir()
    (tmp_path / "safe" / "module.py").write_text("VALUE = 1\n", encoding="utf-8")
    (tmp_path / "verify.py").write_text("VALUE = 2\n", encoding="utf-8")
    value = {
        "schema_version": "emr4.python_source_state.v1",
        "target_python": "3.11",
        "allowed_states": [
            "mounted_current",
            "mounted_default_off",
            "accepted_unmounted",
        ],
        "forbidden_path_tokens": ["holdout", "local_data", "historical-diary-trove"],
        "forbidden_recursive_roots": ["closed"],
        "source_entries": [
            {"path": "safe", "mode": "recursive", "state": "mounted_current"}
        ],
        "verification_paths": ["verify.py"],
    }
    return _write_manifest(tmp_path, value), value


def test_repository_source_state_is_exact_safe_and_compiles() -> None:
    state = load_source_state()
    selected = {path.relative_to(ROOT).as_posix() for path in state["source_files"]}
    assert state["target_python"] == "3.11"
    assert {
        "app/main.py",
        "app/graphql/schema.py",
        "app/services/bernie/session.py",
        "app/services/bernie/ui_view_model.py",
    } <= selected
    assert "app/services/bernie/lc4v4d4_composed_evidence.py" not in selected
    assert not any("holdout" in path.lower() or "local_data" in path.lower() for path in selected)
    compile_selected_sources(state)


@pytest.mark.parametrize(
    ("path", "mode", "message"),
    [
        ("../escape.py", "file", "escapes"),
        ("closed", "recursive", "closed root"),
        ("safe/holdout-v1", "recursive", "forbidden"),
        ("missing.py", "file", "absent"),
    ],
)
def test_hostile_source_entries_fail_closed(
    tmp_path: Path,
    path: str,
    mode: str,
    message: str,
) -> None:
    manifest_path, value = _minimal_manifest(tmp_path)
    if path == "safe/holdout-v1":
        (tmp_path / "safe" / "holdout-v1").mkdir()
        (tmp_path / "safe" / "holdout-v1" / "fixture.py").write_text(
            "VALUE = 3\n", encoding="utf-8"
        )
    value["source_entries"] = [
        {"path": path, "mode": mode, "state": "mounted_current"}
    ]
    manifest_path = _write_manifest(tmp_path, value)
    with pytest.raises(SourceStateError, match=message):
        load_source_state(manifest_path, repo_root=tmp_path)


def test_duplicate_expanded_source_fails_closed(tmp_path: Path) -> None:
    manifest_path, value = _minimal_manifest(tmp_path)
    value["source_entries"].append(
        {"path": "safe/module.py", "mode": "file", "state": "mounted_current"}
    )
    manifest_path = _write_manifest(tmp_path, value)
    with pytest.raises(SourceStateError, match="duplicate selected"):
        load_source_state(manifest_path, repo_root=tmp_path)


def test_target_runtime_mismatch_fails_closed() -> None:
    require_target_runtime("3.11", version=(3, 11))
    with pytest.raises(SourceStateError, match="target runtime mismatch"):
        require_target_runtime("3.11", version=(3, 12))


def test_ci_correctness_requires_target_runtime_and_bounded_tests() -> None:
    commands = _correctness_commands()
    assert "--require-target-runtime" in commands[0].argv
    assert "--noconftest" in commands[-1].argv
    assert commands[-1].argv[-len(CI_CORRECTNESS_TESTS) :] == CI_CORRECTNESS_TESTS
    workflow = (ROOT / ".github/workflows/python-security.yml").read_text(encoding="utf-8")
    requirements = (ROOT / "requirements-dev.txt").read_text(encoding="utf-8")
    assert "python-version: \"3.11\"" in workflow
    assert "--profile ci-correctness" in workflow
    assert "pytest==9.1.1" in requirements
    assert "PyYAML==6.0.3" in requirements
    assert all("holdout" not in path.lower() for path in RUFF_PATHS)
    assert DEFAULT_MANIFEST.is_file()
