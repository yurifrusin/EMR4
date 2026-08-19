"""Deterministic evidence builder for no-database provider-free admission."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile
from typing import Any

from jsonschema import Draft202012Validator

from orchestration_harness.provider_free_no_database_admission import (
    PYTEST_CORE_FIXTURES,
    admit_test_paths,
    canonical_sha256,
)
from scripts.ariadne_evidence_gate import COMMAND_MANIFEST_SCHEMA_VERSION
from scripts.ariadne_validation_runner import validate_execution_manifest_with_admission


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "orchestration/continuity/ariadne-provider-free-no-database-manifest-runner-admission-repair"
CONTRACT = BASE / "contract.json"
CONTRACT_SCHEMA = BASE / "contract.schema.json"
EVIDENCE = BASE / "provider-free-no-database-admission-evidence.json"
PLAN = ROOT / "docs/ariadne-provider-free-no-database-manifest-runner-admission-repair-plan.md"
THREAT = ROOT / "docs/security/ariadne-provider-free-no-database-manifest-runner-admission-repair-threat-model-delta.md"


def _json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"object_required:{path.name}")
    return value


def _write_repo(root: Path, test_source: str, conftest_source: str) -> Path:
    tests = root / "tests"
    tests.mkdir(parents=True, exist_ok=True)
    (tests / "conftest.py").write_text(conftest_source, encoding="utf-8")
    (tests / "test_selected.py").write_text(test_source, encoding="utf-8")
    return root


def _must_reject(repo: Path, test_source: str, conftest_source: str) -> str:
    (repo / "tests" / "test_selected.py").write_text(test_source, encoding="utf-8")
    (repo / "tests" / "conftest.py").write_text(conftest_source, encoding="utf-8")
    try:
        admit_test_paths(repo_root=repo, test_paths=["tests/test_selected.py"])
    except ValueError as error:
        return str(error)
    raise AssertionError("hostile mutation escaped")


def build_evidence(repo_root: Path = ROOT) -> dict[str, Any]:
    root = repo_root.resolve(strict=True)
    contract = _json(CONTRACT)
    schema = _json(CONTRACT_SCHEMA)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(contract)
    if list(PYTEST_CORE_FIXTURES) != contract["pytest_core_fixture_allowlist"]:
        raise ValueError("fixture_allowlist_contract_drift")
    plan = PLAN.read_text(encoding="utf-8")
    threat = THREAT.read_text(encoding="utf-8")
    for marker in (
        contract["planning_source"],
        "No selected test module",
        "no attempt-004",
        "DeepSeek: declined",
        "Gemini: reserved",
    ):
        if marker not in plan:
            raise ValueError(f"plan_marker_missing:{marker}")
    if not all(f"ND-{index:03d}" in threat for index in range(1, 15)):
        raise ValueError("threat_matrix_incomplete")

    safe_selection = admit_test_paths(
        repo_root=root,
        test_paths=["tests/test_ariadne_provider_free_no_database_admission.py"],
    )
    command_manifest = {
        "schema_version": COMMAND_MANIFEST_SCHEMA_VERSION,
        "commands": [
            {
                "id": "PF",
                "argv": [
                    str(root / ".venv" / "Scripts" / "python.exe"),
                    "-m",
                    "scripts.ariadne_provider_free_pytest",
                    "--repo-root",
                    str(root),
                    "tests/test_ariadne_provider_free_no_database_admission.py",
                ],
            }
        ],
    }
    admitted_manifest, aggregate = validate_execution_manifest_with_admission(
        command_manifest, repo_root=root, require_provider_free=True
    )
    if aggregate is None or aggregate["commands"][0]["selection"] != safe_selection:
        raise ValueError("manifest_runner_selection_drift")

    rejected: list[str] = []
    escaped: list[str] = []
    conftest = "import pytest\n" + "\n".join(
        f"@pytest.fixture\ndef shared_{index:03d}(): return object()"
        for index in range(32)
    ) + "\n"
    with tempfile.TemporaryDirectory(prefix="ariadne-no-db-admission-") as temporary:
        repo = _write_repo(
            Path(temporary), "def test_safe(): pass\n", conftest
        )
        mutations: list[tuple[str, str, str]] = []
        for index in range(32):
            mutations.append(
                (
                    f"shared_fixture_{index:03d}",
                    f"def test_unsafe(shared_{index:03d}): pass\n",
                    conftest,
                )
            )
            mutations.append(
                (
                    f"unknown_fixture_{index:03d}",
                    f"def test_unsafe(unknown_{index:03d}): pass\n",
                    conftest,
                )
            )
            mutations.append(
                (
                    f"conftest_import_{index:03d}",
                    f"from tests.conftest import helper_{index:03d}\n\ndef test_unsafe(): pass\n",
                    conftest,
                )
            )
        dynamic_sources = (
            "import pytest\nNAME='fixture'\n@pytest.fixture(name=NAME)\ndef local(): pass\ndef test_unsafe(local): pass\n",
            "import pytest\n@pytest.fixture(autouse=bool(1))\ndef local(): pass\ndef test_unsafe(): pass\n",
            "import pytest\nflag=True\n@pytest.mark.parametrize('value',[1],indirect=flag)\ndef test_unsafe(value): pass\n",
            "import pytest\nnames=['local']\n@pytest.mark.usefixtures(*names)\ndef test_unsafe(): pass\n",
        )
        for index in range(16):
            mutations.append(
                (
                    f"dynamic_grammar_{index:03d}",
                    dynamic_sources[index % len(dynamic_sources)],
                    conftest,
                )
            )
        invalid_paths = [
            "../tests/test_selected.py",
            "tests/../test_selected.py",
            "app/test_selected.py",
            "tests/test_selected.txt",
            "/tests/test_selected.py",
            "C:/tests/test_selected.py",
            "tests/test_selected.py::test_safe",
            "tests/*.py",
        ]
        for index in range(16):
            label = f"selector_{index:03d}"
            candidate = invalid_paths[index % len(invalid_paths)]
            try:
                admit_test_paths(repo_root=repo, test_paths=[candidate])
            except ValueError as error:
                rejected.append(f"{label}:{type(error).__name__}")
            else:
                escaped.append(label)
        for label, source, fixture_source in mutations:
            try:
                _must_reject(repo, source, fixture_source)
            except AssertionError:
                escaped.append(label)
            else:
                rejected.append(label)

    a5_reason: str | None = None
    try:
        admit_test_paths(
            repo_root=root,
            test_paths=["tests/test_model_required_bureau_a5_1_check_in_runtime.py"],
        )
    except ValueError as error:
        a5_reason = str(error)
    if a5_reason != "provider_free_conftest_import_forbidden":
        raise ValueError("repository_a5_1_not_rejected")
    if escaped or len(rejected) != 128:
        raise ValueError("hostile_mutation_escape")

    return {
        "schema_version": "ariadne.provider_free_no_database_admission_evidence.v1",
        "status": "passed",
        "planning_source": contract["planning_source"],
        "contract_sha256": canonical_sha256(contract),
        "safe_selection_sha256": canonical_sha256(safe_selection),
        "safe_selection_test_count": safe_selection["selected_tests"][0]["test_count"],
        "command_manifest_sha256": aggregate["command_manifest_sha256"],
        "manifest_admission_sha256": canonical_sha256(aggregate),
        "manifest_runner_selection_identical": True,
        "repository_a5_1": {
            "status": "rejected_before_subprocess",
            "reason": a5_reason,
        },
        "hostile_mutations": {
            "named": 128,
            "rejected": len(rejected),
            "escaped": escaped,
        },
        "invocations": {
            "selected_module_imports": 0,
            "pytest_collections": 0,
            "ordinary_pytest": 0,
            "docker": 0,
            "postgresql": 0,
            "provider": 0,
            "occupied_deepseek_attempts": 0,
        },
        "broker_work_order_schema": contract["broker_work_order_schema"],
        "legacy_v1_broker_policy": contract["legacy_v1_broker_policy"],
        "admitted_manifest_command_count": len(admitted_manifest["commands"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    evidence = build_evidence()
    if args.check:
        if _json(EVIDENCE) != evidence:
            raise SystemExit("provider-free no-database evidence drift")
        print("provider-free no-database admission evidence: passed")
        return 0
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
