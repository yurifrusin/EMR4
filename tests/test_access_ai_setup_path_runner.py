from pathlib import Path

import pytest

from access_ai.runner.run_setup_path import (
    SetupPathError,
    build_command,
    load_setup_path,
    resolve_document,
    run_setup_path,
)


def test_setup_path_resolves_references():
    data = {
        "goal": "test",
        "context": {"user_email": "yuri@example.com"},
        "projects": {"scribe": {"project_id": "scribe-dev"}},
        "steps": [
            {
                "id": "enable",
                "executable": "gcloud",
                "args": [
                    "services",
                    "enable",
                    "aiplatform.googleapis.com",
                    "--project",
                    "${projects.scribe.project_id}",
                    "--member=user:${context.user_email}",
                ],
            }
        ],
    }

    resolved = resolve_document(data)

    assert resolved["steps"][0]["args"][4] == "scribe-dev"
    assert resolved["steps"][0]["args"][5] == "--member=user:yuri@example.com"


def test_setup_path_dry_run_does_not_execute(tmp_path):
    data = {
        "goal": "dry-run-test",
        "steps": [
            {
                "id": "would_fail_if_executed",
                "executable": "python",
                "args": ["-c", "raise SystemExit(99)"],
            }
        ],
    }

    results = run_setup_path(data, repo_root=tmp_path, execute=False)

    assert len(results) == 1
    assert results[0].dry_run is True
    assert results[0].returncode == 0
    assert results[0].command == ("python", "-c", "raise SystemExit(99)")


def test_setup_path_execute_runs_command(tmp_path):
    data = {
        "goal": "execute-test",
        "steps": [
            {
                "id": "print_marker",
                "executable": "python",
                "args": ["-c", "print('marker')"],
            }
        ],
    }

    results = run_setup_path(data, repo_root=tmp_path, execute=True)

    assert results[0].returncode == 0
    assert results[0].stdout.strip() == "marker"


def test_setup_path_rejects_unknown_executable(tmp_path):
    step = {"id": "bad", "executable": "not-a-real-runner", "args": []}

    with pytest.raises(SetupPathError):
        build_command(step, repo_root=tmp_path)


def test_setup_path_loads_example():
    path = Path("access_ai/setup_paths/dev-yuri-scribe-bernie.yaml")

    data = load_setup_path(path)
    results = run_setup_path(data, repo_root=Path.cwd(), execute=False)

    assert data["goal"] == "setup_access_ai_dev_user_for_scribe_and_bernie"
    assert any(result.step_id == "enable_scribe_vertex_ai" for result in results)
    assert all(result.dry_run for result in results)

