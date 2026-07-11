"""Tests for the S4c advisory allocation-plan command."""

import json
import subprocess
import sys
from pathlib import Path

from scripts.ariadne_allocation_plan import build_allocation_report


REPO_ROOT = Path(__file__).resolve().parents[1]
PROBES = REPO_ROOT / "tests" / "fixtures" / "ariadne_harness" / "s4c_normal_probes.json"


def test_s4c_report_is_deterministic_and_has_no_execution_authority():
    first = build_allocation_report(sprint_id="s4c-fixture", probes_path=PROBES)
    second = build_allocation_report(sprint_id="s4c-fixture", probes_path=PROBES)

    assert first == second
    assert first["advisory_only"] is True
    assert first["execution_permitted"] is False
    assert first["verifier_decision"] is None
    assert first["conductor_plan"]["assignments"][0]["resource_id"] == "claude-fable-conductor"
    assert first["worker_mix_bounds"]["deepseek_flash_maximum_instances"] == 3


def test_s4c_cli_writes_only_the_requested_report_artifact(tmp_path: Path):
    output = tmp_path / "plan.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/ariadne_allocation_plan.py",
            "--sprint-id", "s4c-cli",
            "--probes", str(PROBES),
            "--output", str(output),
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == ""
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["conductor_plan"]["sprint_id"] == "s4c-cli"
    assert payload["execution_permitted"] is False


def test_s4c_rejects_a_probe_method_that_is_not_declared_for_its_transport(tmp_path: Path):
    payload = json.loads(PROBES.read_text(encoding="utf-8"))
    payload["probes"][0]["method"] = "claude_cli_observation"
    invalid_probes = tmp_path / "invalid-probes.json"
    invalid_probes.write_text(json.dumps(payload), encoding="utf-8")

    try:
        build_allocation_report(sprint_id="invalid-adapter", probes_path=invalid_probes)
    except ValueError as error:
        assert "not declared" in str(error)
    else:
        raise AssertionError("undeclared transport probe method must fail closed")
