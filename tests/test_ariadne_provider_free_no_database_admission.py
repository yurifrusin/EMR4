from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

from orchestration_harness.provider_free_no_database_admission import (
    MANIFEST_ADMISSION_SCHEMA_VERSION,
    admit_test_paths,
    canonical_sha256,
)
from scripts.ariadne_evidence_gate import COMMAND_MANIFEST_SCHEMA_VERSION
from scripts.ariadne_validation_runner import (
    validate_execution_manifest_with_admission,
)


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/ariadne-provider-free-no-database-manifest-runner-admission-repair-plan.md"
THREAT = ROOT / "docs/security/ariadne-provider-free-no-database-manifest-runner-admission-repair-threat-model-delta.md"
CONTRACT = ROOT / "orchestration/continuity/ariadne-provider-free-no-database-manifest-runner-admission-repair/contract.json"


def _repo(tmp_path: Path, test_source: str, conftest_source: str = "# none\n") -> Path:
    repo = tmp_path / "repo"
    tests = repo / "tests"
    tests.mkdir(parents=True)
    (tests / "conftest.py").write_text(conftest_source, encoding="utf-8")
    (tests / "test_selected.py").write_text(test_source, encoding="utf-8")
    return repo


def _manifest(repo: Path) -> dict[str, object]:
    return {
        "schema_version": COMMAND_MANIFEST_SCHEMA_VERSION,
        "commands": [
            {
                "id": "PF",
                "argv": [
                    sys.executable,
                    "-m",
                    "scripts.ariadne_provider_free_pytest",
                    "--repo-root",
                    str(repo),
                    "tests/test_selected.py",
                ],
            }
        ],
    }


def test_plan_contract_and_threat_delta_freeze_exact_closed_scope() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    threat = THREAT.read_text(encoding="utf-8")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    assert "440fc7bbd071fbb97a97c986e8c80fe69b83f747" in plan
    assert "No selected test module" in plan
    assert "no attempt-004" in plan
    assert "DeepSeek: declined" in plan
    assert "Gemini: reserved" in plan
    assert all(f"ND-{index:03d}" in threat for index in range(1, 15))
    assert contract["admission_schema"] == MANIFEST_ADMISSION_SCHEMA_VERSION
    assert contract["broker_work_order_schema"] == "ariadne.deepseek_work_order.v2"
    assert contract["legacy_v1_broker_policy"].startswith("test_mode")


def test_static_reading_resolves_local_transitive_autouse_and_literal_marks(
    tmp_path: Path,
) -> None:
    repo = _repo(
        tmp_path,
        """import pytest

@pytest.fixture
def leaf(tmp_path):
    return tmp_path

@pytest.fixture(autouse=True)
def local_guard(leaf):
    return None

@pytest.mark.usefixtures("leaf")
@pytest.mark.parametrize("value", [1, 2])
def test_safe(value, monkeypatch):
    assert value
""",
    )

    first = admit_test_paths(
        repo_root=repo, test_paths=["tests/test_selected.py"]
    )
    second = admit_test_paths(
        repo_root=repo, test_paths=["tests/test_selected.py"]
    )

    assert first == second
    assert first["status"] == "passed"
    assert first["selected_tests"][0]["test_count"] == 1
    assert canonical_sha256(first) == canonical_sha256(second)
    edges = first["selected_tests"][0]["resolved_fixture_edges"]
    assert {row["fixture"] for row in edges} == {
        "leaf",
        "local_guard",
        "monkeypatch",
        "tmp_path",
    }


@pytest.mark.parametrize(
    ("test_source", "reason"),
    [
        (
            "def test_shared(practice):\n    pass\n",
            "provider_free_shared_postgresql_fixture_reachable:practice",
        ),
        (
            "from tests.conftest import make_token\n\ndef test_import():\n    pass\n",
            "provider_free_conftest_import_forbidden",
        ),
        (
            "def test_unknown(mystery_fixture):\n    pass\n",
            "provider_free_fixture_unknown:mystery_fixture",
        ),
        (
            "import pytest\n\n@pytest.fixture(autouse=bool(1))\ndef guard():\n    pass\n\ndef test_dynamic():\n    pass\n",
            "fixture_autouse_dynamic",
        ),
        (
            "import pytest\n\n@pytest.mark.parametrize('value', [1], indirect=unknown)\ndef test_dynamic(value):\n    pass\n",
            "parametrize_indirect_dynamic",
        ),
        (
            "import pytest\n\n@pytest.fixture\ndef one(two):\n    pass\n\n@pytest.fixture\ndef two(one):\n    pass\n\ndef test_cycle(one):\n    pass\n",
            "fixture_dependency_cycle",
        ),
    ],
)
def test_unsafe_or_ambiguous_fixture_graphs_fail_closed(
    tmp_path: Path, test_source: str, reason: str
) -> None:
    repo = _repo(
        tmp_path,
        test_source,
        """import pytest

@pytest.fixture
def practice():
    return object()

def make_token():
    return "synthetic"
""",
    )
    with pytest.raises(ValueError, match=reason):
        admit_test_paths(repo_root=repo, test_paths=["tests/test_selected.py"])


def test_manifest_preflight_derives_the_same_selection_reading(tmp_path: Path) -> None:
    repo = _repo(tmp_path, "def test_safe(tmp_path):\n    assert tmp_path\n")
    manifest = _manifest(repo)

    admitted, aggregate = validate_execution_manifest_with_admission(
        manifest, repo_root=repo, require_provider_free=True
    )
    direct = admit_test_paths(
        repo_root=repo, test_paths=["tests/test_selected.py"]
    )

    assert admitted == manifest
    assert aggregate is not None
    assert aggregate["schema_version"] == MANIFEST_ADMISSION_SCHEMA_VERSION
    assert aggregate["commands"][0]["selection"] == direct
    assert aggregate["commands"][0]["selection_sha256"] == canonical_sha256(direct)


def test_duplicate_path_and_repository_a5_1_conftest_import_are_denied(
    tmp_path: Path,
) -> None:
    repo = _repo(tmp_path, "def test_safe():\n    pass\n")
    with pytest.raises(ValueError, match="selector_duplicate"):
        admit_test_paths(
            repo_root=repo,
            test_paths=["tests/test_selected.py", "tests/test_selected.py"],
        )
    with pytest.raises(ValueError, match="conftest_import_forbidden"):
        admit_test_paths(
            repo_root=ROOT,
            test_paths=["tests/test_model_required_bureau_a5_1_check_in_runtime.py"],
        )
