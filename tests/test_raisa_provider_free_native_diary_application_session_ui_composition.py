"""Deterministic acceptance for default-off native-Diary UI composition."""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Iterator

import pytest


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_RECONCILER = (
    ROOT
    / "orchestration/continuity/raisa-provider-free-native-diary-application-session-practitioner-reconciliation"
    / "client-reconciler.mjs"
)
PUBLISHED_RECONCILER = (
    ROOT / "docs/diary/application-session-practitioner-reconciler.mjs"
)
COMPOSITION = ROOT / "docs/diary/application-session-practitioner-directory.mjs"
DIARY_JS = ROOT / "docs/diary/diary.js"
DIARY_HTML = ROOT / "docs/diary/diary.html"
PLAN = (
    ROOT
    / "docs/raisa-provider-free-native-diary-application-session-ui-composition-plan.md"
)
THREAT = (
    ROOT
    / "docs/security/raisa-provider-free-native-diary-application-session-ui-composition-threat-model-delta.md"
)
CONTRACT = (
    ROOT
    / "orchestration/continuity/raisa-provider-free-native-diary-application-session-ui-composition"
    / "ui-composition-contract.json"
)
SCHEMA = CONTRACT.with_name("ui-composition-contract.schema.json")
ACCEPTANCE = (
    ROOT
    / "scripts/raisa_provider_free_native_diary_application_session_ui_composition_acceptance.mjs"
)
SOURCE_HEAD = "e7d209e6652106c8f69036460223259a33af19c9"


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical_lf(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n")


def _run_acceptance(output: Path) -> dict[str, Any]:
    completed = subprocess.run(
        ["node", str(ACCEPTANCE), "--output", str(output)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    stdout = json.loads(completed.stdout.strip())
    persisted = json.loads(output.read_text(encoding="utf-8"))
    assert stdout == persisted
    return persisted


def _extract_async_function(source: str, name: str) -> str:
    start = source.index(f"async function {name}(")
    opening = source.index("{", start)
    depth = 0
    for index in range(opening, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[start : index + 1]
    raise AssertionError(f"unterminated function: {name}")


def _leaf_paths(value: Any, path: tuple[Any, ...] = ()) -> Iterator[tuple[Any, ...]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _leaf_paths(child, path + (key,))
    elif isinstance(value, list):
        yield path
    else:
        yield path


def _mutate_leaf(payload: Any, path: tuple[Any, ...]) -> None:
    parent = payload
    for key in path[:-1]:
        parent = parent[key]
    key = path[-1]
    value = parent[key]
    if isinstance(value, bool):
        parent[key] = not value
    elif isinstance(value, str):
        parent[key] = f"{value}-mutated"
    elif isinstance(value, int):
        parent[key] = value + 1
    elif isinstance(value, list):
        parent[key] = [*value, "authority-bearing-mutation"]
    else:  # pragma: no cover - contract leaves are intentionally closed above
        raise AssertionError(f"unsupported leaf type: {type(value)!r}")


def test_node_acceptance_harness_passes_with_exact_evidence_label(tmp_path: Path) -> None:
    evidence = _run_acceptance(tmp_path / "ui-composition-evidence.json")

    assert evidence["result"] == (
        "provider_free_native_diary_application_session_ui_composition_pass"
    )
    assert evidence["evidence_label"] == (
        "provider_free_default_off_ui_composition_harness"
    )
    assert evidence["data_class"] == "authored_synthetic"
    assert evidence["case_count"] == evidence["passed_case_count"]
    assert evidence["failed_case_count"] == 0
    assert evidence["properties"]["strict_true_default_off"] is True
    assert evidence["properties"]["enabled_path_has_no_legacy_fallback"] is True
    assert evidence["properties"]["provider_or_external_effect"] is False


def test_acceptance_harness_requires_one_explicit_output() -> None:
    completed = subprocess.run(
        ["node", str(ACCEPTANCE)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert completed.returncode != 0
    assert "explicit_output_path_required" in completed.stderr


def test_published_reconciler_is_canonical_lf_byte_equivalent() -> None:
    assert _canonical_lf(PUBLISHED_RECONCILER) == _canonical_lf(CANONICAL_RECONCILER)
    assert hashlib.sha256(_canonical_lf(PUBLISHED_RECONCILER)).digest() == hashlib.sha256(
        _canonical_lf(CANONICAL_RECONCILER)
    ).digest()


def test_contract_validates_and_every_leaf_mutation_fails() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    contract = _json(CONTRACT)
    validator = jsonschema.Draft202012Validator(_json(SCHEMA))
    validator.validate(contract)

    paths = list(_leaf_paths(contract))
    assert len(paths) >= 40
    for path in paths:
        mutated = copy.deepcopy(contract)
        _mutate_leaf(mutated, path)
        assert list(validator.iter_errors(mutated)), f"mutation passed at {path!r}"


def test_contract_schema_is_recursively_closed() -> None:
    schema = _json(SCHEMA)

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            if node.get("type") == "object":
                assert node.get("additionalProperties") is False
            for child in node.values():
                visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)

    visit(schema)


def test_existing_graphql_and_rest_functions_are_exact_at_source_head() -> None:
    current = DIARY_JS.read_text(encoding="utf-8").replace("\r\n", "\n")
    original = subprocess.run(
        ["git", "show", f"{SOURCE_HEAD}:docs/diary/diary.js"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        encoding="utf-8",
        timeout=10,
    ).stdout.replace("\r\n", "\n")

    for name in (
        "fetchPractitionerDirectoryRest",
        "fetchPractitionerDirectoryGraphql",
    ):
        assert _extract_async_function(current, name) == _extract_async_function(
            original, name
        )


def test_diary_wiring_is_strict_true_and_enabled_branch_has_no_fallback() -> None:
    source = DIARY_JS.read_text(encoding="utf-8")
    load = _extract_async_function(source, "loadPractitionerDirectory")
    enabled = load.index("isApplicationSessionPractitionerBootstrapEnabled")
    enabled_return = load.index("return loadApplicationSessionPractitionerDirectory")
    legacy = load.index("if (!ENABLE_GRAPHQL_PRACTITIONERS)")
    assert enabled < enabled_return < legacy
    assert "bootstrap.enabled === true" in source

    application_session = _extract_async_function(
        source, "loadApplicationSessionPractitionerDirectory"
    )
    assert "fetchPractitionerDirectoryGraphql" not in application_session
    assert "fetchPractitionerDirectoryRest" not in application_session
    assert "apiFetch(" not in application_session
    assert 'diary.js?v=195' in DIARY_HTML.read_text(encoding="utf-8")


def test_new_modules_have_no_direct_effectful_surface() -> None:
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (PUBLISHED_RECONCILER, COMPOSITION)
    )
    for pattern in (
        r"\bfetch\s*\(",
        r"XMLHttpRequest",
        r"\bdocument\s*\.",
        r"\bwindow\s*\.",
        r"\blocalStorage\b",
        r"\bsessionStorage\b",
        r"\bWebSocket\b",
        r"\bEventSource\b",
        r"\bindexedDB\b",
    ):
        assert not re.search(pattern, source)


def test_plan_threat_and_contract_keep_api_spine_and_claims_closed() -> None:
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (PLAN, THREAT)
    )
    contract = _json(CONTRACT)

    assert "GraphQL remains read-only" in combined
    assert "No `app.main` mount" in combined
    assert "docs/branding/" in combined
    assert "provider_free_default_off_ui_composition_harness" in combined
    assert contract["api_spine"] == {
        "classification": "scoped_read_consumer",
        "graphql_mutation": False,
        "command_tunnel": False,
        "new_rest_surface": False,
        "event_actuator": False,
        "manifest_change": False,
    }
    assert "deployment_production_release" in contract["closed_gates"]
    assert "browser" in contract["claims_not_made"]


def test_python_test_module_has_no_database_or_product_runtime_fixture() -> None:
    module = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(module):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    assert not {"sqlalchemy", "psycopg", "fastapi", "httpx", "requests"} & imports
