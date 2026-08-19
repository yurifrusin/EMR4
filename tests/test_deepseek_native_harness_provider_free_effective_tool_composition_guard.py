from __future__ import annotations

import ast
import base64
from io import BytesIO
import hashlib
import json
from pathlib import Path
import tarfile

from jsonschema import Draft202012Validator, FormatChecker
import pytest

from scripts.deepseek_native_harness_provider_free_effective_tool_composition_guard import (
    CONTRACT_PATH,
    EVIDENCE_PATH,
    EXPECTED_TOOLS,
    FAILURE_COORDINATES,
    OPERATION_ID,
    REPORT_PATH,
    SUCCESS_COORDINATE,
    GuardError,
    _cache_blob_path,
    build_guard_source,
    load_contract,
    sanitize_terminal,
    scenario_matrix,
    simulate_guard,
    validate_guard_source,
    verify_package_blob,
)


ROOT = Path(__file__).resolve().parents[1]
OPERATION_ROOT = ROOT / "orchestration" / "continuity" / OPERATION_ID
CONTRACT_SCHEMA_PATH = OPERATION_ROOT / "contract.schema.json"
EVIDENCE_SCHEMA_PATH = OPERATION_ROOT / "evidence.schema.json"
PLAN_PATH = (
    ROOT
    / "docs"
    / "deepseek-native-harness-provider-free-effective-tool-composition-and-terminal-coordinate-guard-plan.md"
)
THREAT_PATH = (
    ROOT
    / "docs"
    / "security"
    / "deepseek-native-harness-provider-free-effective-tool-composition-and-terminal-coordinate-guard-threat-model-delta.md"
)
SCRIPT_PATH = (
    ROOT
    / "scripts"
    / "deepseek_native_harness_provider_free_effective_tool_composition_guard.py"
)


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _tarball(members: list[tuple[str, bytes, str]]) -> bytes:
    payload = BytesIO()
    with tarfile.open(fileobj=payload, mode="w:gz") as archive:
        for name, content, kind in members:
            info = tarfile.TarInfo(name)
            if kind == "file":
                info.size = len(content)
                archive.addfile(info, BytesIO(content))
            elif kind == "symlink":
                info.type = tarfile.SYMTYPE
                info.linkname = "elsewhere"
                archive.addfile(info)
            else:  # pragma: no cover - test helper misuse
                raise AssertionError(kind)
    return payload.getvalue()


def _package_row(name: str, payload: bytes, member: bytes) -> dict:
    return {
        "name": name,
        "version": "0.1.0-rc.7",
        "registry_shasum": hashlib.sha1(payload).hexdigest(),  # noqa: S324
        "registry_integrity": "sha512-"
        + base64.b64encode(hashlib.sha512(payload).digest()).decode("ascii"),
        "members": [
            {
                "path": "package.json",
                "bytes": len(member),
                "sha256": hashlib.sha256(member).hexdigest(),
            }
        ],
    }


def test_contract_and_schema_are_strict_and_valid() -> None:
    contract = _json(CONTRACT_PATH)
    schema = _json(CONTRACT_SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(contract)
    assert load_contract() == contract
    assert contract["planning_source"] == (
        "80d9e69c3dee0ddeb4b7fc620cbd0673d7ad0fa4"
    )
    assert contract["guard"]["selected_tools"] == list(EXPECTED_TOOLS)
    assert contract["guard"]["failure_coordinates"] == list(FAILURE_COORDINATES)
    assert contract["guard"]["provider_dispatch_count"] == 0


def test_contract_pins_all_four_exact_rc7_package_surfaces() -> None:
    packages = load_contract()["packages"]
    assert [row["name"] for row in packages] == [
        "@deepseek-ai/dsh",
        "@deepseek-ai/dsh-tools",
        "@deepseek-ai/dsh-agent-presets",
        "@deepseek-ai/dsh-scope",
    ]
    assert all(row["version"] == "0.1.0-rc.7" for row in packages)
    assert all(len(row["registry_shasum"]) == 40 for row in packages)
    assert all(row["registry_integrity"].startswith("sha512-") for row in packages)
    tools = packages[1]
    assert {member["path"] for member in tools["members"]} == {
        "README.md",
        "lib/index.js",
        "lib/types/index.js",
    }


def test_cache_blob_verifier_accepts_only_exact_regular_member(tmp_path: Path) -> None:
    member = b'{"name":"@deepseek-ai/example","version":"0.1.0-rc.7"}\n'
    payload = _tarball([("package/package.json", member, "file")])
    package = _package_row("@deepseek-ai/example", payload, member)
    blob = _cache_blob_path(tmp_path, package["registry_integrity"])
    blob.parent.mkdir(parents=True)
    blob.write_bytes(payload)

    projection, retained = verify_package_blob(package, tmp_path)

    assert projection == {
        "name": "@deepseek-ai/example",
        "version": "0.1.0-rc.7",
        "registry_identity_passed": True,
        "member_count": 1,
        "members_passed": True,
    }
    assert retained == {"package.json": member}


def test_cache_blob_verifier_rejects_symlink_member(tmp_path: Path) -> None:
    member = b"ignored"
    payload = _tarball([("package/package.json", member, "symlink")])
    package = _package_row("@deepseek-ai/example", payload, member)
    blob = _cache_blob_path(tmp_path, package["registry_integrity"])
    blob.parent.mkdir(parents=True)
    blob.write_bytes(payload)

    with pytest.raises(GuardError, match="package_member_missing_or_unsafe"):
        verify_package_blob(package, tmp_path)


def test_generated_helper_has_one_ordered_fail_closed_composition_path() -> None:
    payload = build_guard_source()
    projection = validate_guard_source(payload)
    source = payload.decode("utf-8")

    assert projection["mount_count"] == 1
    assert projection["view_count"] == 1
    assert projection["restriction_count"] == 1
    assert projection["schema_projection_count"] == 1
    assert projection["forbidden_generic_present"] is False
    assert source.index("await agentCtx.agentPresets.mount(") < source.index(
        "agentCtx.tools.view("
    )
    assert source.index("agentCtx.tools.view(") < source.index(
        "agentCtx.tools.restrict("
    )
    assert source.index("agentCtx.tools.restrict(") < source.index(
        "agentCtx.tools.schemas("
    )
    assert "known.filter((name) => !restrictableSet.has(name))" in source
    assert "CUSTOM_RUNNER_FAILURE" not in source


def test_generated_helper_carries_every_closed_coordinate() -> None:
    source = build_guard_source().decode("utf-8")
    assert SUCCESS_COORDINATE in source
    assert all(coordinate in source for coordinate in FAILURE_COORDINATES)
    assert 'stage: "pre_provider_tool_composition"' in source
    assert "error?.message" not in source
    assert "error?.stack" not in source


def test_accepted_projection_filters_inherited_surplus_to_exact_view() -> None:
    result = simulate_guard(
        known=("edit", "glob", "grep", "read", "write"),
        restrictable=("edit", "glob", "grep", "read", "write"),
        schemas=("read", "edit", "glob"),
    )
    assert result.coordinate == SUCCESS_COORDINATE
    assert result.detail is None


@pytest.mark.parametrize(
    ("kwargs", "coordinate", "detail"),
    [
        (
            {"selected": ("read", "glob", "edit")},
            "EFFECTIVE_TOOL_COMPOSITION_INPUT_INVALID",
            None,
        ),
        (
            {"mount_ok": False},
            "EFFECTIVE_TOOL_COMPOSITION_PRESET_MOUNT_FAILED",
            None,
        ),
        (
            {"scope_present": False},
            "EFFECTIVE_TOOL_COMPOSITION_SCOPE_MISSING",
            None,
        ),
        (
            {
                "known": ("edit", "glob", "read", "write"),
                "restrictable": ("edit", "glob", "read"),
            },
            "EFFECTIVE_TOOL_COMPOSITION_SCOPE_LOCAL_TOOL_PRESENT",
            "write",
        ),
        (
            {"known": ("edit", "read"), "restrictable": ("edit", "read")},
            "EFFECTIVE_TOOL_COMPOSITION_EXPECTED_TOOL_NOT_INHERITED",
            "glob",
        ),
        (
            {"restriction_ok": False},
            "EFFECTIVE_TOOL_COMPOSITION_RESTRICTION_FAILED",
            None,
        ),
        (
            {"schemas": ("edit", "glob", "read", "read")},
            "EFFECTIVE_TOOL_COMPOSITION_SCHEMA_VIEW_INVALID",
            None,
        ),
        (
            {"schemas": ("edit", "glob", "read", "write")},
            "EFFECTIVE_TOOL_COMPOSITION_EFFECTIVE_VIEW_MISMATCH",
            "write",
        ),
    ],
)
def test_hostile_projections_fail_at_exact_coordinate(
    kwargs: dict, coordinate: str, detail: str | None
) -> None:
    result = simulate_guard(**kwargs)
    assert result.coordinate == coordinate
    assert result.detail == detail


def test_terminal_sanitizer_never_retains_dynamic_error_or_unsafe_detail() -> None:
    unknown = sanitize_terminal("Error: C:/secret/token", ["C:/secret"])
    known = sanitize_terminal(
        "EFFECTIVE_TOOL_COMPOSITION_SCOPE_LOCAL_TOOL_PRESENT",
        ["write", "grep"],
    )
    assert unknown.coordinate == "EFFECTIVE_TOOL_COMPOSITION_UNCLASSIFIED"
    assert unknown.detail is None
    assert known.detail == "grep,write"


def test_scenario_matrix_exercises_success_and_every_failure_coordinate() -> None:
    matrix = scenario_matrix()
    observed = {row["coordinate"] for row in matrix}
    assert SUCCESS_COORDINATE in observed
    assert set(FAILURE_COORDINATES) <= observed
    assert all(
        row["detail"] is None
        or all(part.isidentifier() and part.islower() for part in row["detail"].split(","))
        for row in matrix
    )


def test_published_evidence_validates_and_records_all_zero_execution_counts() -> None:
    evidence = _json(EVIDENCE_PATH)
    schema = _json(EVIDENCE_SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(evidence)
    assert evidence["result"] == "passed_provider_free_deterministic_guard"
    assert len(evidence["package_checks"]) == 4
    assert all(evidence["source_semantic_checks"].values())
    assert evidence["profile_check"]["selected_tools"] == list(EXPECTED_TOOLS)
    assert all(value == 0 for value in evidence["zero_counts"].values())
    assert not any(evidence["retention"].values())


def test_report_keeps_the_static_claim_boundary_explicit() -> None:
    report = REPORT_PATH.read_text(encoding="utf-8")
    assert "deterministic guard-construction evidence only" in report
    assert "not a native boot, agent, model or provider result" in report
    assert "all zero" in report


def test_plan_and_threat_delta_preserve_closed_surfaces() -> None:
    plan = PLAN_PATH.read_text(encoding="utf-8")
    threat = THREAT_PATH.read_text(encoding="utf-8")
    normalized = " ".join(plan.split())
    normalized_threat = " ".join(threat.split())
    assert "zero provider calls" in normalized
    assert "no model request" in normalized
    assert "No exception text, stack" in normalized
    assert "git add ." in plan and "git add -A" in plan
    assert "docs/branding/" in plan
    assert "the outer broker still rejects" in normalized.lower()
    assert (
        "does not prove an actual native Harness composition boot"
        in normalized_threat
    )


def test_implementation_has_no_process_network_or_container_execution_surface() -> None:
    tree = ast.parse(SCRIPT_PATH.read_text(encoding="utf-8"))
    imported = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert not imported.intersection(
        {"subprocess", "socket", "requests", "urllib", "docker", "psycopg"}
    )
    source = SCRIPT_PATH.read_text(encoding="utf-8")
    assert "Popen(" not in source
    assert "os.system(" not in source
    assert "CUSTOM_RUNNER_FAILURE" in source  # frozen forbidden-coordinate check only
