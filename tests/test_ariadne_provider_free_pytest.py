from __future__ import annotations

import argparse
from pathlib import Path

import pytest
import yaml

from scripts import ariadne_provider_free_pytest as provider_free


ROOT = Path(__file__).resolve().parents[1]


def test_command_forces_no_conftest_and_disables_cache_plugin() -> None:
    command = provider_free.provider_free_command(
        ["tests/test_ariadne_provider_free_pytest.py"]
    )

    assert command[:3] == [provider_free.sys.executable, "-m", "pytest"]
    assert command.count("--noconftest") == 1
    assert command[command.index("-p") + 1] == "no:cacheprovider"
    assert command[-1] == "tests/test_ariadne_provider_free_pytest.py"
    assert "tests/conftest.py" not in command


def test_environment_drops_database_credentials_and_inherited_pytest_options() -> None:
    environment = provider_free.provider_free_environment(
        {
            "PATH": "safe-path",
            "TEST_DATABASE_URL": "postgresql://forbidden",
            "DATABASE_URL": "postgresql://forbidden",
            "GOOGLE_APPLICATION_CREDENTIALS": "forbidden.json",
            "PYTEST_ADDOPTS": "-p tests.conftest",
        }
    )

    assert environment["PATH"] == "safe-path"
    assert environment["ARIADNE_PROVIDER_FREE_VERIFICATION"] == "1"
    assert environment["PYTEST_ADDOPTS"] == ""
    assert environment["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] == "1"
    for forbidden in (
        "TEST_DATABASE_URL",
        "DATABASE_URL",
        "GOOGLE_APPLICATION_CREDENTIALS",
    ):
        assert forbidden not in environment


@pytest.mark.parametrize(
    "path",
    [
        "../tests/test_escape.py",
        "tests/../app/test_escape.py",
        "app/test_not_allowed.py",
        "tests/not_python.txt",
        "C:/absolute/test.py",
        "/absolute/test.py",
    ],
)
def test_literal_test_path_rejects_scope_expansion(path: str) -> None:
    with pytest.raises((argparse.ArgumentTypeError, ValueError)):
        provider_free._literal_test_path(path)


def test_empty_allowlist_is_rejected() -> None:
    with pytest.raises(ValueError, match="at least one"):
        provider_free.provider_free_command([])


def test_main_uses_fixed_command_clean_environment_and_exact_root(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    test_path = tmp_path / "tests" / "test_safe.py"
    test_path.parent.mkdir()
    test_path.write_text("def test_safe():\n    assert True\n", encoding="utf-8")
    observed: dict[str, object] = {}

    class Completed:
        returncode = 0

    def fake_run(command, *, cwd, env, check, shell):
        observed.update(
            command=command,
            cwd=cwd,
            env=env,
            check=check,
            shell=shell,
        )
        return Completed()

    monkeypatch.setattr(provider_free.subprocess, "run", fake_run)
    monkeypatch.setattr(
        provider_free.os,
        "environ",
        {"PATH": "safe", "TEST_DATABASE_URL": "postgresql://forbidden"},
    )

    assert (
        provider_free.main(
            [
                "--repo-root",
                str(tmp_path),
                "tests/test_safe.py",
            ]
        )
        == 0
    )
    assert observed["cwd"] == tmp_path.resolve()
    assert observed["check"] is False
    assert observed["shell"] is False
    assert "--noconftest" in observed["command"]
    assert "TEST_DATABASE_URL" not in observed["env"]


def test_evidence_led_workflow_names_provider_free_entrypoint() -> None:
    policy = yaml.safe_load(
        (ROOT / "orchestration/harness_settings/evidence_led_workflow.yaml").read_text(
            encoding="utf-8"
        )
    )

    assert (
        "provider_free_pytest_disables_conftest_plugins_and_database_environment"
        in policy["hard_controls"]
    )
    assert policy["review_command_evidence"][
        "provider_free_database_closed_test_entrypoint"
    ] == "python -m scripts.ariadne_provider_free_pytest"
