from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
import yaml


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "deepseek-native-harness-emr4-worker-profile-and-first-monitored-development-admission"
)
PROFILE_PATH = CONTRACT_DIR / "profile-family.yaml"
SCHEMA_PATH = CONTRACT_DIR / "profile-family.schema.json"
PLAN_PATH = (
    ROOT
    / "docs"
    / "deepseek-native-harness-emr4-worker-profile-and-first-monitored-development-admission-plan.md"
)
RECOVERY_PATH = (
    ROOT
    / "docs"
    / "deepseek-native-harness-emr4-worker-profile-and-first-monitored-development-admission-enclosure-recovery.md"
)
EXACT_TOOL_VIEW_PLAN_PATH = (
    ROOT
    / "docs"
    / "deepseek-native-harness-exact-tool-view-recovery-and-second-monitored-development-admission-plan.md"
)
EXACT_TOOL_VIEW_EVIDENCE_PATH = (
    ROOT
    / "orchestration"
    / "agent_inbox"
    / "codex"
    / "deepseek-native-harness-exact-tool-view-provider-free-composed-request-evidence.json"
)


def _profile_family() -> dict:
    return yaml.safe_load(PROFILE_PATH.read_text(encoding="utf-8"))


def _schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _canonical_sha256(value: object) -> str:
    canonical = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(canonical).hexdigest()}"


def test_profile_family_validates_against_checked_schema() -> None:
    schema = _schema()
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(
        _profile_family()
    )


def test_profile_family_pins_package_model_and_loop_controls() -> None:
    family = _profile_family()
    assert family["schema_version"] == (
        "emr4.deepseek-native-harness-profile-family.v2"
    )
    assert family["package"] == {
        "name": "@deepseek-ai/dsh",
        "version": "0.1.0-rc.7",
        "registry_shasum": "8a69013c06179d7af437de92fb4a9a2e1fd7d410",
        "registry_integrity": "sha512-ZceDCJ8FAywih+USW/OMk9jEhunlvJBGEz4kqrhau23hPzbciOazZrywH0nBRsaalSeAJ1JGBmjtw4OSjToStw==",
    }
    assert family["model_route"] == {
        "provider": "deepseek-official",
        "model": "deepseek-v4-flash",
        "reasoning_effort": "high",
        "endpoint_authority": (
            "isolated_broker_sidecar_allowlisted_deepseek_official"
        ),
    }
    assert family["loop_control"] == {
        "automatic_retries": 0,
        "fallbacks": [],
        "max_parallel_tool_calls": 1,
        "wall_clock_seconds": 900,
        "monetary_boundary": "operator_prepaid_account",
    }


def test_profile_family_pins_package_native_exact_tool_view_enforcement() -> None:
    enforcement = _profile_family()["tool_view_enforcement"]
    assert enforcement["selector"] == {
        "package": "@deepseek-ai/dsh-tools",
        "version": "0.1.0-rc.7",
        "public_api": "ctx.tools.restrict",
        "allow_argument": "selected_profile.tools",
        "applied_scope": "agent_setup_context",
    }
    assert enforcement["preset_mount"] == {
        "package": "@deepseek-ai/dsh-agent-presets",
        "version": "0.1.0-rc.7",
        "public_api": "ctx.agentPresets.mount",
        "preset_id": "selected_profile_name",
        "mount_phase": "agents.create_setup_before_first_request",
    }
    assert enforcement["semantics"] == {
        "model_request_effect": "remove_unselected_tool_schemas",
        "unnamed_late_global_tools": "excluded",
        "multiple_restrictions": "intersection",
        "unknown_local_or_reserved_names": "reject",
        "security_boundary": False,
    }
    assert enforcement["outer_broker"] == {
        "required": True,
        "tool_allowlist_source": "selected_profile.tools",
        "exact_match_required": True,
    }
    assert enforcement["source_mapping"] == [
        {
            "package": "@deepseek-ai/dsh-tools",
            "path": "README.md",
            "sha256": (
                "695e1f49dc4929133a5bca9da0d1f96601027a2643159efff5b82fb2709aa90d"
            ),
        },
        {
            "package": "@deepseek-ai/dsh-tools",
            "path": "lib/index.js",
            "sha256": (
                "47de95d14493dbd22d1a3ade14890fc99d7232db4e363f2190c9063b030dd029"
            ),
        },
        {
            "package": "@deepseek-ai/dsh-agent-presets",
            "path": "README.md",
            "sha256": (
                "c9fdecbd3d6047f171f0e0a6208b31fe38891685e9fdee86a46d5d7effcd7733"
            ),
        },
        {
            "package": "@deepseek-ai/dsh-agent-presets",
            "path": "lib/index.js",
            "sha256": (
                "a0b417514e3d285ad5fef74867e8049af333ebdec6e4d7639e388aa0903e0039"
            ),
        },
    ]


def test_profiles_have_exact_fail_closed_authority() -> None:
    profiles = _profile_family()["profiles"]
    assert list(profiles) == [
        "emr4-provider-free-preflight",
        "emr4-readonly-review",
        "emr4-bounded-worker",
    ]
    assert profiles["emr4-provider-free-preflight"]["tools"] == []
    assert profiles["emr4-provider-free-preflight"]["credential_policy"] == (
        "intentionally_absent"
    )
    assert profiles["emr4-provider-free-preflight"][
        "expected_pre_provider_terminal"
    ] == "MISSING_CREDENTIAL"
    assert profiles["emr4-readonly-review"]["permission"]["sandbox"] == (
        "read-only"
    )
    assert profiles["emr4-readonly-review"]["tools"] == ["read", "glob"]
    assert profiles["emr4-readonly-review"]["credential_policy"] == (
        "broker_capability_only"
    )
    assert profiles["emr4-bounded-worker"]["permission"] == {
        "sandbox": "workspace-write",
        "approval": "never",
    }
    assert profiles["emr4-bounded-worker"]["tools"] == ["read", "glob", "edit"]
    assert profiles["emr4-bounded-worker"]["credential_policy"] == (
        "broker_capability_only"
    )


def test_auxiliary_and_unbounded_surfaces_are_explicitly_disabled() -> None:
    family = _profile_family()
    disabled = set(family["disabled_surfaces"])
    assert {
        "subagents",
        "workflows",
        "web",
        "browser",
        "mcp",
        "acp",
        "compaction_model",
        "session_title_model",
        "telemetry",
        "pi_ai_routes",
        "pwsh",
    } <= disabled
    assert family["session_policy"]["terminal_session_not_resumable"] is True
    assert family["evidence_policy"]["raw_session_commit"] == "forbidden"
    assert "credential" in family["evidence_policy"]["forbidden_retention"]


def test_execution_enclosure_separates_worker_host_and_provider_credential() -> None:
    enclosure = _profile_family()["execution_enclosure"]
    assert enclosure == {
        "image": (
            "node@sha256:6f7b03f7c2c8e2e784dcf9295400527b9b1270fd37b7e9a7285cf83b6951452d"
        ),
        "host_filesystem_visibility": "exact_sparse_worktree_bind_only",
        "worker_network": "internal_broker_only_no_direct_egress",
        "provider_credential_holder": "isolated_broker_sidecar",
        "worker_provider_credential": "forbidden",
        "worker_broker_capability": "required_at_process_start",
        "broker_provider_call_budget": (
            "none_beyond_single_session_wall_clock_and_prepaid_balance"
        ),
        "model_facing_shell": "disabled_for_first_monitored_development",
        "focused_test_executor": "sol_outside_worker_container",
    }


def test_provider_free_capture_proves_exact_composed_tool_view_and_cleanup() -> None:
    family = _profile_family()
    evidence = json.loads(EXACT_TOOL_VIEW_EVIDENCE_PATH.read_text(encoding="utf-8"))
    contract = evidence["normalized_contract"]
    capture = evidence["accepted_isolated_capture"]

    assert evidence["provider_free_phase_2_passed"] is True
    assert evidence["occupied_dispatch_authorized_at_generation"] is False
    assert contract["profile_family_sha256"] == _canonical_sha256(family)
    selected = family["profiles"][contract["selected_profile"]]
    assert contract["selected_profile_sha256"] == _canonical_sha256(selected)
    assert contract["selected_tools"] == selected["tools"] == ["read", "glob", "edit"]
    assert capture["declared_tool_names"] == ["edit", "glob", "read"]
    assert capture["declared_tool_count"] == 3
    assert capture["duplicate_or_surplus_tool_schema"] is False
    assert capture["request_count"] == 1
    assert capture["external_provider_calls"] == 0
    assert capture["provider_credential_present"] is False
    assert all(attempt["request_count"] == 0 for attempt in evidence["isolated_attempts"])
    assert all(
        evidence["cleanup"][key] is True
        for key in (
            "containers_absent",
            "volumes_absent",
            "networks_absent",
            "package_volume_absent",
            "session_volume_absent",
            "disposable_profile_root_absent",
        )
    )
    mapped_sources = [
        {
            "path": f"{row['package']}/{row['path']}",
            "sha256": row["sha256"],
        }
        for row in family["tool_view_enforcement"]["source_mapping"]
    ]
    assert [
        {"path": row["path"], "sha256": row["sha256"]}
        for row in evidence["package_native_tool_view"]["source_mapping"]
    ] == mapped_sources


def test_plan_freezes_real_sparse_worker_package_and_prepaid_budget_boundary() -> None:
    plan = PLAN_PATH.read_text(encoding="utf-8")
    recovery = RECOVERY_PATH.read_text(encoding="utf-8")
    exact_tool_view_plan = EXACT_TOOL_VIEW_PLAN_PATH.read_text(encoding="utf-8")
    normalized_recovery = " ".join(recovery.split())
    normalized_exact_tool_view_plan = " ".join(exact_tool_view_plan.split())
    assert "scripts/ariadne_deepseek_native_harness_profiles.py" in plan
    assert "tests/test_ariadne_deepseek_native_harness_profiles.py" in plan
    assert "sparse worktree" in plan
    assert "prepaid DeepSeek balance is the monetary budget mechanism" in plan
    assert "No local request-count/budget proxy" in plan
    assert "No product, patient, clinical" in plan
    assert "reads always pass through" in normalized_recovery
    assert "It receives no DeepSeek provider credential" in normalized_recovery
    assert "No model-facing shell is mounted" in normalized_recovery
    assert (
        "does not introduce a request-count or token-spend budget"
        in normalized_recovery
    )
    assert "package-native scoped-tool facility" in normalized_exact_tool_view_plan
    assert (
        "present exactly `read`, `glob` and `edit`"
        in normalized_exact_tool_view_plan
    )
