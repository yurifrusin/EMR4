"""Bounded G1B/G1C checks for an externally reviewed publication request.

This route reads a fixed set of ordinary files. It never imports candidate code,
discovers settings, loads historical policy, or executes a commit/push. Its
distinct decision establishes policy eligibility only. The reviewed publisher
must also establish complete scope, source/review authority, leases and readback.
An expected binding digest comes from the trusted caller, never the candidate.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from orchestration_harness import trusted_git

PROFILE = "G1B_COMPLETION_ACTIVE"
TASK_CLASS = "g1b_persistence_recovery_lease_and_narrative"
REQUEST_VERSION = "ariadne.bounded_g1b_request.v1"
BINDING_VERSION = "ariadne.bounded_g1b_binding.v1"
SCOPE_VERSION = "ariadne.g1b_completion_scope.v1"
SCOPE_PATH = "orchestration/programme/g1b-completion-scope.json"
STATE = "orchestration/programme/current-state.json"
GATES = "orchestration/programme/gates.yaml"
OVERLAY = "orchestration/harness_settings/programme_recovery.yaml"
PROJECT = "orchestration/harness_settings/project.yaml"
CONTINUATION = "orchestration/harness_settings/autonomous_continuation.yaml"
LATCH = "orchestration/continuity/ariadne-active-operation-latch/current.json"
G1B1_SURFACE = "orchestration/programme/g1b1-accepted-surface.yaml"
JOURNAL_SCOPE = "orchestration/programme/g1b2-journal-replay-scope.yaml"
AGENTS = "AGENTS.md"
RECOVERY_REF = "refs/heads/codex/raisa-ariadne-recovery-g0"
REMOTE_URL = "https://github.com/yurifrusin/emr4"
PROTECTED = "2e34bdad732fdab32fbf778280b3d3c70d66d602"
JOURNAL_COMMIT = "723e42fc70841b0e8ceed7fd5a2f63e0eecd573e"
JOURNAL_PARENT = "d512399aa52fdc1d43b68e3e5117d3142037671d"
JOURNAL_TREE = "7bcbaa456c508ccfedb386893e64784f69734e7a"
OLD_PROFILE = "G1B.2_PURE_JOURNAL_REPLAY_KERNEL_ACTIVE"
OLD_PREAMBLE = "Gate G1B.2 is active only for the pure versioned journal and deterministic replay kernel"
NEW_PREAMBLE = "Gate G1B is active only for bounded persistence, recovery, stale-lease protection and derived narrative"

KERNEL_PINS = {
    "orchestration_harness/clockwork_journal.py": "98686ae95c8477511e0ebee0170e0232ee39c5270b14d1cdcba74def11791b6c",
    "orchestration_harness/clockwork_state.py": "6e54a4414c3fb22a46caa6b471749d31a4e9fcc356f90f011e9fd8d17a31d052",
    "tests/test_clockwork_journal.py": "53f9daef9c2051e2422924f179a23bd953dbc3cceedbfe956bf3dd4744620126",
}
BASELINE_PINS = {
    STATE: "0410f8aff9c633d704765f4d454893f8d48ff42c49108f368eef36f4bdbd3232",
    GATES: "02a1fea8f12b26a892b2d035671a5e8cd689d2ca8d843547e5c2412a42030339",
    OVERLAY: "a9c1b1d7ad601ec26b41ea62efcee9062fa8f4273511dc281a777b9e207207bb",
    AGENTS: "7b56fe9c15d17db44cdfc3cf8b7b79f480bd30766dc3baae4151469c9a466715",
}
FROZEN_PINS = {
    G1B1_SURFACE: "2d189829518f3525b3da34a10931985f3e1e48e4fd6a08346efdb6ad9112c3a8",
    PROJECT: "a3835edf35116088ef1808e2590c0b7ab837171ab40457b51f96f8519a235f84",
    CONTINUATION: "0a205c109383ed64c6c87435b259bbdd5a1989f834de6f505385bbf6c52bbd0d",
    LATCH: "f1bc5b3545293834365b7992882ebc09e6c83ccd63687c28fd443ac049e2e437",
    JOURNAL_SCOPE: "8c3ed98d0111e5e9314a7e20561235dc6a6f6f5e434ead6c45ae7f60e3033779",
    **KERNEL_PINS,
}
EVIDENCE_PINS = {
    "admission/review-subject.json": "c52012b8bacd02c9c0913d181eeac1b0ab355bf9a6d66b502e2a72921c87ca9e",
    "admission/independent-review-transcription.md": "96adb86f86a95006c92c7fa2e6b6d90102c1e24480937563e6581e6bfb3b17b4",
    "admission/verification-summary.json": "37659de2dc169592cdc777fb13f9d6547d6b75235249d806e19394e97e82a11c",
    "admission/six-tests.stdout.json": "6ccc59097a279282fe9d75bdf262687421b89f5948a15a4cd3e2d44f7883eaa6",
    "admission/exhaustive.stdout.json": "949dfa4f66961abecd92b60d16cc0c52ee525d6199ebda86d00689187d6f2fca",
    "publication/commit-receipt.json": "7d772cb914988e85bb4d98741c880718047b8e684880f12d4fb970281bd6ff75",
    "publication/push-receipt.json": "dc81592c371eb707e23a2be582e7de191e385162124a2ad27d52a642028c3f93",
    "publication/post-publication-readback.json": "128bdab8ca9c3fa244de51bc0797c4b15c96255e1d7a7d932a330de2e68896f4",
    "current-control-evidence.json": "80b688756a13dabf93ee60debbf7cee1a766d88b20260370f199ae49ccd50f8f",
}
SOURCE_PATHS = frozenset({
    "orchestration_harness/bounded_g1b.py",
    "orchestration_harness/trusted_git.py",
    "orchestration_harness/programme_admission.py",
    "orchestration_harness/pinned_programme_gatekeeper.py",
    "scripts/raisa_ariadne_recovery_preflight.py",
})
INPUT_PATHS = frozenset({STATE, GATES, OVERLAY, PROJECT, CONTINUATION, LATCH,
                         G1B1_SURFACE, JOURNAL_SCOPE, AGENTS, SCOPE_PATH, *KERNEL_PINS})
TRANSITION_PATHS = frozenset({STATE, GATES, OVERLAY, AGENTS, SCOPE_PATH})
COMPLETION_PATHS = frozenset({"orchestration_harness/clockwork_persistence.py",
                              "tests/test_clockwork_persistence.py"})
CRITERIA = (
    "versioned_journal_entry_vocabulary",
    "fixed_genesis_and_exact_previous_digest_chain",
    "canonical_entry_bytes_and_sha256_digest",
    "replay_rederives_every_result_with_accepted_G1B1_reducer",
    "closed_tamper_gap_reorder_mismatch_and_type_rejection",
    "pure_no_filesystem_git_process_network_database_clock_randomness_or_existing_clockwork_imports",
)
FORBIDDEN = frozenset({"provider_invocation", "integration", "protected_ref_movement",
                       "deployment", "pages", "real_data_access", "product_behavior_change",
                       "dependency_change", "migration_change", "existing_clockwork_runtime_mutation",
                       "autonomous_worker_dispatch"})
EFFECTS = frozenset({"repository_read", "control_plane_edit", "task_branch_commit", "task_branch_push"})
LIMITS = ("policy eligibility is not publication authority", "no complete physical worktree attestation",
          "no full-suite or whole-loader acceptance", "G1B completion and G1C remain unaccepted")

G1C_PROFILE = "G1C_GOVERNOR_ACTIVE"
G1C_TASK = "g1c_finite_budgets_and_progress_governor"
G1C_PREAMBLE = "Gate G1C is active only for the bounded recovery governor and its versioned persistence integration"
G1C_SCOPE = "orchestration/programme/g1c-governor-scope.json"
COST = "orchestration/harness_settings/cost_controls.yaml"
COST_PIN = "9ed7844a22dfafa33c064cb1c26ca62779cc08f2195b93c3c7f436417cb0473f"
PROFILE_PREAMBLES = {PROFILE: NEW_PREAMBLE, G1C_PROFILE: G1C_PREAMBLE}
BOUNDED_SCOPE_PATHS = frozenset({SCOPE_PATH, G1C_SCOPE})
G1B_BASELINE_PINS = {
    AGENTS: "5901c286901ca6bf49ccee71e6d6e7419db177226c19aaf634d55ed6d3fe90da",
    STATE: "6147906ffb7e20b4f070d5ffbfa0c223d6f50c4a5814be5d35d218ceca6b0a87",
    GATES: "cdc87526fe78910f81735e55b4e8922f80b9a2ed34af3d386f657b8e33589f39",
    OVERLAY: "37b99386aeb07c34d10c7ea1a6fac9c73606a4db88e5329c088d583deb4a6f65",
    SCOPE_PATH: "023a9307fb4b02e44136cece07ad697f0cf6c952e82bbcc162a7b7c57eb4814d",
}
PERSISTENCE_PUBLICATION = {
    "commit": "9a1a2a44cfd7f083398671cc7a44d5f7c16c8d5a",
    "parent": "257b5e9fb7839b114b34712161fd4bf85d5e3d9f",
    "tree": "e46587bf13ee83c2c0e81b7931b2f3eb1fbdbb1a",
}
PERSISTENCE_PINS = {
    "orchestration_harness/clockwork_persistence.py": "b9f1db70f0cad685253522ce3a732b8b8265da140560d9fc5a47b3d778a18166",
    "tests/test_clockwork_persistence.py": "cbdc38a0f7b89af0d91b630b18e333968c9b9825234e5fac2db8ed664f52c0c6",
}
G1B_EVIDENCE_PINS = {
    **EVIDENCE_PINS,
    "g1b-evidence/implementation-review.json": "bd786906c98380b840dbae08f73a0d48cc9d965436be81f6b0b7127c3fffc2e9",
    "g1b-evidence/windows-test-2.stdout.json": "406b254d9d09a0cf335935a15ee666098f794be85107fd1402dec51b1d818da1",
    "g1b-evidence/fresh-readback.json": "3d7f0b55d71fe7455542df866b1fa0bcaf6484a5495be1cbd8d8176b5d4464ba",
    "g1b-evidence/candidate-manifest-v2.json": "705345c96b7be2ecd277d321f3ce5bd0300a2bef41caa076903c68a4bcf8442a",
}
G1B_CRITERIA = ("closed_state_machine_implemented", "append_only_versioned_event_journal",
                "invalid_transition_rejected", "crash_recovery_deterministic", "stale_lease_cannot_commit",
                "narrative_generated_from_structured_state")
G1C_CRITERIA = ("finite_retry_cost_token_and_wall_clock_budgets", "global_red_enters_repair_only_mode",
                "no_progress_stops_or_quarantines", "wip_and_stack_limits_enforced",
                "high_risk_human_authority_enforced", "structured_stop_reason")
G1C_INPUT_PATHS = INPUT_PATHS | {G1C_SCOPE, COST}
G1C_TRANSITION_PATHS = frozenset({STATE, GATES, OVERLAY, AGENTS, G1C_SCOPE})
GOVERNOR_PATHS = frozenset({"orchestration_harness/clockwork_governor.py",
                           "orchestration_harness/clockwork_persistence.py", "tests/test_clockwork_governor.py"})
G1C_LIMITS = ("policy eligibility is not publication authority", "no complete physical worktree attestation",
              "no full-suite or whole-loader acceptance", "G1C implementation and operational multi-task control remain unaccepted",
              "providers, existing writers, worker dispatch, product work and protected refs remain closed")
OPERATION_PATHS = {"accept_journal": TRANSITION_PATHS, "complete_g1b": COMPLETION_PATHS,
                   "accept_g1b": G1C_TRANSITION_PATHS, "implement_g1c": GOVERNOR_PATHS}


def operation_paths(kind: str) -> frozenset[str]:
    _need(type(kind) is str and kind in OPERATION_PATHS, "bounded_g1b_operation_kind")
    return OPERATION_PATHS[kind]


def _operation(kind: str) -> dict:
    paths = operation_paths(kind)
    successor = kind in {"accept_g1b", "implement_g1c"}
    return {
        "paths": paths, "successor": successor, "transition": kind in {"accept_journal", "accept_g1b"},
        "input_paths": G1C_INPUT_PATHS if successor else INPUT_PATHS,
        "transition_paths": G1C_TRANSITION_PATHS if successor else TRANSITION_PATHS,
        "scope_path": G1C_SCOPE if successor else SCOPE_PATH,
        "baseline_pins": G1B_BASELINE_PINS if successor else BASELINE_PINS,
        "baseline_directory": "g1b-baseline" if successor else "baseline",
        "evidence_pins": G1B_EVIDENCE_PINS if successor else EVIDENCE_PINS,
        "profile": G1C_PROFILE if successor else PROFILE,
        "gate": "G1C" if successor else "G1B",
        "limits": (("G1B component acceptance awaits reviewed transition publication",) + G1C_LIMITS
                   if kind == "accept_g1b" else ("G1B component accepted",) + G1C_LIMITS if successor else LIMITS),
    }


class BoundedG1BError(ValueError):
    def __init__(self, reason_code: str):
        super().__init__(reason_code)
        self.reason_code = reason_code


def _need(condition: bool, reason: str) -> None:
    if not condition:
        raise BoundedG1BError(reason)


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _keys(value: object, expected: set[str] | frozenset[str], reason: str) -> dict:
    _need(type(value) is dict and set(value) == expected, reason)
    return value


def _pairs(rows):
    result = {}
    for key, value in rows:
        _need(type(key) is str and key not in result, "bounded_g1b_duplicate_or_invalid_key")
        result[key] = value
    return result


def _constant(value):
    raise BoundedG1BError("bounded_g1b_nonfinite_json")


def _canonical(value: object) -> bytes:
    seen = set()
    remaining = 50000

    def visit(item: object, depth: int) -> None:
        nonlocal remaining
        remaining -= 1
        _need(remaining >= 0 and depth <= 64, "bounded_g1b_structure_bound")
        if type(item) in (dict, list):
            _need(id(item) not in seen, "bounded_g1b_shared_or_cyclic_container")
            seen.add(id(item))
            if type(item) is dict:
                _need(all(type(key) is str for key in item), "bounded_g1b_invalid_key")
                children = item.values()
            else:
                children = item
            for child in children:
                visit(child, depth + 1)
        else:
            _need(type(item) in (str, int, float, bool, type(None)), "bounded_g1b_non_json_value")

    visit(value, 0)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def _json(raw: bytes) -> dict:
    _need(type(raw) is bytes and len(raw) <= 2 * 1024 * 1024, "bounded_g1b_payload_size")
    value = json.loads(raw, object_pairs_hook=_pairs, parse_constant=_constant)
    _need(type(value) is dict, "bounded_g1b_object_required")
    _canonical(value)
    return value


class _Yaml(yaml.SafeLoader):
    pass


def _yaml_mapping(loader, node, deep=False):
    return _pairs((loader.construct_object(key, deep=deep), loader.construct_object(value, deep=deep))
                  for key, value in node.value)


_Yaml.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _yaml_mapping)


def _document(raw: bytes, path: str) -> dict:
    if path.endswith(".json"):
        return _json(raw)
    _need(type(raw) is bytes and len(raw) <= 2 * 1024 * 1024, "bounded_g1b_payload_size")
    value = yaml.load(raw, Loader=_Yaml)
    _need(type(value) is dict, "bounded_g1b_object_required")
    # Also reject YAML NaN, date objects and cyclic/non-JSON structures.
    _canonical(value)
    return value


def recognises_bounded_request(manifest: object) -> bool:
    if type(manifest) is not dict:
        return False
    version = manifest.get("schema_version")
    kind = manifest.get("operation_kind")
    task = manifest.get("task_class")
    return ((type(version) is str and version.startswith("ariadne.bounded_g1b_"))
            or (type(kind) is str and kind in OPERATION_PATHS)
            or (type(task) is str and task in {TASK_CLASS, G1C_TASK}))


def build_completion_scope(recorded_at: str, transition_base: str) -> dict:
    return {
        "schema_version": SCOPE_VERSION,
        "recorded_at": recorded_at,
        "transition_base_commit": transition_base,
        "accepted_component": "G1B.2_pure_journal_and_replay",
        "implementation_review": {
            "reviewer": "/root/journal_independent_review",
            "subject_sha256": EVIDENCE_PINS["admission/review-subject.json"],
            "transcription_sha256": EVIDENCE_PINS["admission/independent-review-transcription.md"],
            "verdict": "PASS_BOUNDED_IMPLEMENTATION_ONLY",
            "original_operational_acceptance": False,
        },
        "publication": {"commit": JOURNAL_COMMIT, "parent": JOURNAL_PARENT, "tree": JOURNAL_TREE,
                        "commit_receipt_sha256": EVIDENCE_PINS["publication/commit-receipt.json"],
                        "push_receipt_sha256": EVIDENCE_PINS["publication/push-receipt.json"]},
        "kernel_sha256": dict(KERNEL_PINS),
        "criteria": list(CRITERIA),
        "evidence_sha256": dict(EVIDENCE_PINS),
        "current_operation": {"operation_id": "g1b-persistence-recovery-completion", "profile": PROFILE,
                              "task_class": TASK_CLASS, "status": "active", "completion_accepted": False},
        "completion_paths": sorted(COMPLETION_PATHS),
        "allowed_effects": sorted(EFFECTS),
        "forbidden_effects": sorted(FORBIDDEN),
        "claim_limits": list(LIMITS),
        "g1b_complete": False, "g1c_eligible": False,
        "feature_work_eligible": False, "existing_clockwork_writers_activated": False,
    }


def _validate_scope(scope: dict) -> None:
    stamp, base = scope.get("recorded_at"), scope.get("transition_base_commit")
    _need(type(stamp) is str and datetime.fromisoformat(stamp).tzinfo is not None,
          "bounded_g1b_timestamp_invalid")
    _need(type(base) is str and re.fullmatch(r"[0-9a-f]{40}", base) is not None,
          "bounded_g1b_transition_base_invalid")
    _need(_canonical(scope) == _canonical(build_completion_scope(stamp, base)), "bounded_g1b_acceptance_scope_invalid")


def build_g1b_acceptance_transition(before: dict[str, bytes], scope: dict) -> dict[str, bytes]:
    """Derive the sole allowed delta from already authenticated predecessor bytes."""
    _keys(before, set(BASELINE_PINS), "bounded_g1b_predecessor_paths")
    for path, digest in BASELINE_PINS.items():
        _need(type(before[path]) is bytes and _sha(before[path]) == digest,
              "bounded_g1b_predecessor_changed")
    _validate_scope(scope)
    state = _document(before[STATE], STATE)
    gates = _document(before[GATES], GATES)
    overlay = _document(before[OVERLAY], OVERLAY)
    _need(state["active_profile"] == OLD_PROFILE and state["current_gate"] == "G1B.2",
          "bounded_g1b_predecessor_profile")
    _need(state["feature_work_eligible"] is False and state["product_work_eligible"] is False
          and state["global_checks"]["global_gate"] == "red_repair_only"
          and state["global_checks"]["feature_work_suspended"] is True,
          "bounded_g1b_repair_only_required")
    scope_raw = _canonical(scope) + b"\n"
    state.update(current_gate="G1B", active_correction="G1B", active_profile=PROFILE,
                 observed_at=scope["recorded_at"])
    state["g1b"].update(status="active_completion", next_action=TASK_CLASS)
    state["g1b"]["subgates"]["G1B.2"].update(status="passed", implementation_started=True,
                                                implementation_authorized=False)
    state["g1b"]["completion"] = {"scope_path": SCOPE_PATH, "scope_sha256": _sha(scope_raw),
                                    "current_operation": copy.deepcopy(scope["current_operation"])}
    state["task_selection"].update(allowed_task_kinds=[TASK_CLASS], next_eligible_tranche="G1B",
                                   next_eligibility_condition="bounded_G1B_completion_profile_active")
    gates["programme"].update(current_gate="G1B", next_eligible_tranche="G1B",
                                prepared_at=scope["recorded_at"])
    by_id = {row["id"]: row for row in gates["gates"]}
    _need(len(by_id) == len(gates["gates"]), "bounded_g1b_duplicate_gate")
    _need(by_id["G1B.2"]["exit_checks"] == list(CRITERIA), "bounded_g1b_criteria_changed")
    by_id["G1B"]["status"] = "active_completion"
    by_id["G1B"]["next_gate"] = "G1C"
    by_id["G1B.2"]["status"] = "passed"
    overlay["active_profile"] = PROFILE
    _need(PROFILE not in overlay["profiles"], "bounded_g1b_predecessor_already_active")
    overlay["profiles"][PROFILE] = {
        "profile_kind": "bounded_G1B_completion", "expected_programme_mode": "recovery",
        "expected_current_gate": "G1B", "expected_gate_status": "active", "active_correction": "G1B",
        "programme_gate": "G1B", "admitted_task_classes": [TASK_CLASS],
        "allowed_effects": sorted(EFFECTS), "forbidden_effects": sorted(FORBIDDEN),
        "allowed_paths": sorted(COMPLETION_PATHS), "autonomous_task_selection": False,
        "feature_work_eligible": False, "product_work_eligible": False,
        "provider_calls_eligible": False, "deployment_eligible": False,
        "protected_ref_movement_eligible": False, "g1c_eligible": False,
        "scope_behavior": "bounded_g1b_completion", "scope_file": SCOPE_PATH,
        "closed_entrypoints": ["worker_dispatch", "provider_invocation", "clockwork_tick_mutation",
                               "clockwork_closeout_mutation", "integration", "protected_ref_operation", "deployment"],
    }
    text = before[AGENTS].decode("utf-8")
    _need(text.count(OLD_PREAMBLE) == 1 and text.startswith("# EMERGENCY RAISA/ARIADNE RECOVERY PRECEDENCE\n"),
          "bounded_g1b_predecessor_preamble")
    text = text.replace(OLD_PREAMBLE, NEW_PREAMBLE, 1)
    old_gate = "| Active programme gate | G1B.2 pure journal/replay; G1B.1 closeout accepted. G1B.2 closeout and G1C remain pending. |"
    new_gate = "| Active programme gate | G1B completion; the pure G1B.2 journal is accepted for composition. Persistence, recovery, stale-lease protection and derived narrative remain to be completed. G1C remains closed. |"
    _need(text.count(old_gate) == 1, "bounded_g1b_baton_gate_missing")
    text = text.replace(old_gate, new_gate, 1)
    old_next = "| Next dependency | Verify relevant current controls, accept the published G1B.2 journal through the required controller transition, then complete the remaining G1B guarantees. |"
    new_next = "| Next dependency | Implement and verify the bounded G1B completion task in orchestration/programme/g1b-completion-scope.json; its current operation supersedes the preserved historical latch. |"
    _need(text.count(old_next) == 1, "bounded_g1b_baton_next_missing")
    text = text.replace(old_next, new_next, 1)
    return {
        STATE: json.dumps(state, indent=2, ensure_ascii=False).encode() + b"\n",
        GATES: yaml.safe_dump(gates, sort_keys=False, allow_unicode=True).encode(),
        OVERLAY: yaml.safe_dump(overlay, sort_keys=False, allow_unicode=True).encode(),
        AGENTS: text.encode(), SCOPE_PATH: scope_raw,
    }


def validate_g1b_acceptance_transition(before: dict[str, bytes], after: dict[str, bytes],
                                       evidence: dict[str, bytes]) -> None:
    _keys(after, TRANSITION_PATHS, "bounded_g1b_transition_paths")
    _keys(evidence, set(EVIDENCE_PINS), "bounded_g1b_evidence_paths")
    for path, digest in EVIDENCE_PINS.items():
        _need(type(evidence[path]) is bytes and _sha(evidence[path]) == digest,
              "bounded_g1b_evidence_changed")
    expected = build_g1b_acceptance_transition(before, _json(after[SCOPE_PATH]))
    for path in TRANSITION_PATHS:
        if path.endswith((".json", ".yaml")):
            _need(_canonical(_document(after[path], path)) == _canonical(_document(expected[path], path)),
                  "bounded_g1b_authority_delta_invalid")
        else:
            _need(after[path] == expected[path], "bounded_g1b_agents_delta_invalid")
    # The digest in state refers to the canonical scope bytes, not an equivalent
    # but differently encoded candidate file.
    _need(after[SCOPE_PATH] == expected[SCOPE_PATH], "bounded_g1b_scope_encoding_invalid")


def build_governor_scope(recorded_at: str, transition_base: str) -> dict:
    return {
        "schema_version": "ariadne.g1c_governor_scope.v1", "recorded_at": recorded_at,
        "transition_base_commit": transition_base, "accepted_component": "G1B_persisted_versioned_journal",
        "accepted_publication": dict(PERSISTENCE_PUBLICATION), "accepted_source_sha256": dict(PERSISTENCE_PINS),
        "kernel_sha256": dict(KERNEL_PINS), "criteria": list(G1B_CRITERIA),
        "evidence_sha256": dict(G1B_EVIDENCE_PINS),
        "preserved_predecessor_scope": {"path": SCOPE_PATH, "sha256": G1B_BASELINE_PINS[SCOPE_PATH]},
        "current_operation": {
            "operation_id": "g1c-recovery-governor", "profile": G1C_PROFILE, "task_class": G1C_TASK,
            "status": "active", "completion_accepted": False,
            "supersedes": {"operation_id": "g1b-persistence-recovery-completion", "scope_path": SCOPE_PATH,
                           "scope_sha256": G1B_BASELINE_PINS[SCOPE_PATH], "historical_latch_preserved": True},
        },
        "implementation_paths": sorted(GOVERNOR_PATHS), "governor_criteria": list(G1C_CRITERIA),
        "allowed_effects": sorted(EFFECTS), "forbidden_effects": sorted(FORBIDDEN),
        "budget_semantics": {
            "cost_policy_path": COST, "cost_policy_sha256": COST_PIN,
            "accounting_mode": "subscription_usage_window", "monetary_budget_enforcement": "inactive",
            "estimated_cost_reporting": "advisory_only", "estimated_cost_or_local_cap_triggers_fallback": False,
            "recovery_envelope_requires": ["finite_usage_and_token_reservations", "finite_operation_and_total_attempts",
                "finite_operation_and_envelope_deadlines", "fresh_account_pool_window_unit_bound_usage",
                "atomic_reservation_wip_and_journal_head", "retain_unresolved_reservations_until_verified_settlement"],
            "global_defaults_changed": False,
        },
        "versioned_persistence_change_permitted": True, "automatic_v1_migration_permitted": False,
        "g1b_component_accepted": True, "g1c_complete": False, "g1d_eligible": False,
        "feature_work_eligible": False, "existing_clockwork_writers_activated": False,
        "claim_limits": list(G1C_LIMITS),
    }


def _validate_governor_scope(scope: dict) -> None:
    stamp, base = scope.get("recorded_at"), scope.get("transition_base_commit")
    _need(type(stamp) is str and datetime.fromisoformat(stamp).tzinfo is not None,
          "bounded_g1b_timestamp_invalid")
    _need(type(base) is str and re.fullmatch(r"[0-9a-f]{40}", base) is not None,
          "bounded_g1b_transition_base_invalid")
    _need(_canonical(scope) == _canonical(build_governor_scope(stamp, base)), "bounded_g1c_scope_invalid")


def build_g1c_acceptance_transition(before: dict[str, bytes], scope: dict) -> dict[str, bytes]:
    """Accept the immutable G1B component and enable only the G1C implementation."""
    _keys(before, set(G1B_BASELINE_PINS), "bounded_g1c_predecessor_paths")
    for path, digest in G1B_BASELINE_PINS.items():
        _need(type(before[path]) is bytes and _sha(before[path]) == digest, "bounded_g1c_predecessor_changed")
    _validate_governor_scope(scope)
    state = _document(before[STATE], STATE)
    gates = _document(before[GATES], GATES)
    overlay = _document(before[OVERLAY], OVERLAY)
    _need(state["active_profile"] == PROFILE and state["current_gate"] == "G1B"
          and state["g1b"]["status"] == "active_completion" and "g1c" not in state,
          "bounded_g1c_predecessor_profile")
    _need(state["feature_work_eligible"] is False and state["product_work_eligible"] is False
          and state["global_checks"]["global_gate"] == "red_repair_only"
          and state["global_checks"]["feature_work_suspended"] is True, "bounded_g1b_repair_only_required")
    _need(state["g1b"]["completion"]["scope_sha256"] == _sha(before[SCOPE_PATH])
          and state["g1b"]["completion"]["current_operation"] == _json(before[SCOPE_PATH])["current_operation"],
          "bounded_g1c_predecessor_operation_changed")
    scope_raw = _canonical(scope) + b"\n"
    state.update(current_gate="G1C", active_correction="G1C", active_profile=G1C_PROFILE,
                 observed_at=scope["recorded_at"])
    state["g1b"].update(status="passed", next_action="G1C_governor_implementation")
    # Preserve the previous completion object verbatim as historical authority.
    state["g1b"]["acceptance"] = {"scope_path": G1C_SCOPE, "scope_sha256": _sha(scope_raw),
        "accepted_component_commit": PERSISTENCE_PUBLICATION["commit"], "criteria": list(G1B_CRITERIA)}
    state["g1c"] = {"status": "active", "scope_path": G1C_SCOPE, "scope_sha256": _sha(scope_raw),
                     "current_operation": copy.deepcopy(scope["current_operation"]), "completion_accepted": False}
    state["task_selection"].update(allowed_task_kinds=[G1C_TASK], next_eligible_tranche="G1C",
                                   next_eligibility_condition="bounded_G1C_governor_profile_active")
    gates["programme"].update(current_gate="G1C", next_eligible_tranche="G1C", prepared_at=scope["recorded_at"])
    by_id = {row["id"]: row for row in gates["gates"]}
    _need(len(by_id) == len(gates["gates"]) and by_id["G1B"]["exit_checks"] == list(G1B_CRITERIA)
          and by_id["G1C"]["exit_checks"] == list(G1C_CRITERIA) and by_id["G1C"]["status"] == "blocked_by_G1B"
          and by_id["G1D"]["status"] == "blocked_by_G1C", "bounded_g1c_gate_predecessor_invalid")
    by_id["G1B"]["status"] = "passed"
    by_id["G1C"]["status"] = "active"
    _need(overlay["active_profile"] == PROFILE and G1C_PROFILE not in overlay["profiles"], "bounded_g1c_profile_already_active")
    overlay["active_profile"] = G1C_PROFILE
    overlay["profiles"][G1C_PROFILE] = {
        "profile_kind": "bounded_G1C_governor", "expected_programme_mode": "recovery",
        "expected_current_gate": "G1C", "expected_gate_status": "active", "active_correction": "G1C",
        "programme_gate": "G1C", "admitted_task_classes": [G1C_TASK],
        "allowed_effects": sorted(EFFECTS), "forbidden_effects": sorted(FORBIDDEN),
        "allowed_paths": sorted(GOVERNOR_PATHS), "autonomous_task_selection": False,
        "feature_work_eligible": False, "product_work_eligible": False, "provider_calls_eligible": False,
        "deployment_eligible": False, "protected_ref_movement_eligible": False, "g1d_eligible": False,
        "scope_behavior": "bounded_g1c_governor", "scope_file": G1C_SCOPE,
        "recovery_envelope_limits_required": True, "global_execution_defaults_unchanged": True,
        "closed_entrypoints": ["worker_dispatch", "provider_invocation", "clockwork_tick_mutation",
                               "clockwork_closeout_mutation", "integration", "protected_ref_operation", "deployment"],
    }
    text = before[AGENTS].decode("utf-8")
    replacements = {
        NEW_PREAMBLE: G1C_PREAMBLE,
        "| Active programme gate | G1B completion; the pure G1B.2 journal is accepted for composition. Persistence, recovery, stale-lease protection and derived narrative remain to be completed. G1C remains closed. |":
        "| Active programme gate | G1C governor; the bounded G1B persistence component is accepted. G1C implementation is eligible; operational multi-task control and G1D remain unaccepted. |",
        "| Next dependency | Implement and verify the bounded G1B completion task in orchestration/programme/g1b-completion-scope.json; its current operation supersedes the preserved historical latch. |":
        "| Next dependency | Integrate and verify the bounded G1C governor task in orchestration/programme/g1c-governor-scope.json; its current operation explicitly supersedes the preserved G1B operation. |",
    }
    for old, new in replacements.items():
        _need(text.count(old) == 1, "bounded_g1c_agents_predecessor_changed")
        text = text.replace(old, new, 1)
    return {STATE: json.dumps(state, indent=2, ensure_ascii=False).encode() + b"\n",
            GATES: yaml.safe_dump(gates, sort_keys=False, allow_unicode=True).encode(),
            OVERLAY: yaml.safe_dump(overlay, sort_keys=False, allow_unicode=True).encode(),
            AGENTS: text.encode(), G1C_SCOPE: scope_raw}


def validate_g1c_acceptance_transition(before: dict[str, bytes], after: dict[str, bytes],
                                       evidence: dict[str, bytes]) -> None:
    _keys(after, G1C_TRANSITION_PATHS, "bounded_g1c_transition_paths")
    _keys(evidence, set(G1B_EVIDENCE_PINS), "bounded_g1c_evidence_paths")
    for path, digest in G1B_EVIDENCE_PINS.items():
        _need(type(evidence[path]) is bytes and _sha(evidence[path]) == digest, "bounded_g1c_evidence_changed")
    review = _json(evidence["g1b-evidence/implementation-review.json"])
    tests = _json(evidence["g1b-evidence/windows-test-2.stdout.json"])
    readback = _json(evidence["g1b-evidence/fresh-readback.json"])
    _need(review["verdict"] == "G1B_PERSISTENCE_IMPLEMENTATION_PASS"
          and review["source_sha256"] == PERSISTENCE_PINS["orchestration_harness/clockwork_persistence.py"]
          and review["test_sha256"] == PERSISTENCE_PINS["tests/test_clockwork_persistence.py"]
          and review["windows_result_sha256"] == G1B_EVIDENCE_PINS["g1b-evidence/windows-test-2.stdout.json"]
          and tests["status"] == "pass" and tests["tests_run"] == 15 and tests["guard_violations"] == []
          and tests["native_process_death_boundaries"] == ["after_commit", "before_commit"]
          and all(readback[key] == value for key, value in PERSISTENCE_PUBLICATION.items()),
          "bounded_g1c_component_evidence_invalid")
    expected = build_g1c_acceptance_transition(before, _json(after[G1C_SCOPE]))
    for path in G1C_TRANSITION_PATHS:
        if path.endswith((".json", ".yaml")):
            _need(_canonical(_document(after[path], path)) == _canonical(_document(expected[path], path)),
                  "bounded_g1c_authority_delta_invalid")
        else:
            _need(after[path] == expected[path], "bounded_g1c_agents_delta_invalid")
    _need(after[G1C_SCOPE] == expected[G1C_SCOPE], "bounded_g1c_scope_encoding_invalid")


@dataclass(frozen=True, slots=True)
class BoundedG1BContext:
    target_root: Path
    source_root: Path
    evidence_root: Path
    scratch_root: Path
    binding_path: Path
    expected_binding_sha256: str


@dataclass(frozen=True, slots=True)
class BoundedG1BInputs:
    binding: dict[str, Any]
    before: dict[str, bytes]
    payloads: dict[str, bytes]
    evidence: dict[str, bytes]
    index_observation: dict[str, Any]


@dataclass(frozen=True, slots=True)
class BoundedG1BDecision:
    policy_admitted: bool
    reason_codes: tuple[str, ...]
    entrypoint: str
    phase: str
    operation_id: str | None = None
    candidate_tree: str | None = None
    binding_sha256: str | None = None
    observation_sha256: str | None = None
    execution_authorized: bool = False
    claim_limits: tuple[str, ...] = LIMITS
    current_gate: str | None = None
    active_profile: str | None = None


def _digest_map(value: object, paths: frozenset[str], reason: str) -> dict:
    result = _keys(value, paths, reason)
    _need(all(type(v) is str and re.fullmatch(r"[0-9a-f]{64}", v) for v in result.values()), reason)
    return result


def load_bounded_g1b_inputs(context: BoundedG1BContext) -> BoundedG1BInputs:
    """Read authenticated ordinary inputs; expected digest is caller authority."""
    _need(type(context) is BoundedG1BContext, "bounded_g1b_context_required")
    for path in (context.target_root, context.source_root, context.evidence_root,
                 context.scratch_root, context.binding_path):
        trusted_git._validate_path_components(path.absolute())
    target, source, evidence_root, scratch = (p.resolve(strict=True) for p in
        (context.target_root, context.source_root, context.evidence_root, context.scratch_root))
    _need(all(p != target and not p.is_relative_to(target) and not target.is_relative_to(p)
              for p in (source, evidence_root, scratch)), "bounded_g1b_external_roots_required")
    administration = trusted_git._physical_git_administration(target)
    _need(all(a != b and not a.is_relative_to(b) and not b.is_relative_to(a)
              for a in (source, evidence_root, scratch)
              for b in (administration["gitdir"], administration["commondir"])),
          "bounded_g1b_roots_overlap_git_administration")
    _need(scratch != source and not scratch.is_relative_to(source) and not source.is_relative_to(scratch),
          "bounded_g1b_scratch_overlaps_source")
    _need(Path(__file__).resolve() == source / "orchestration_harness/bounded_g1b.py"
          and Path(trusted_git.__file__).resolve() == source / "orchestration_harness/trusted_git.py",
          "bounded_g1b_source_not_isolated")
    binding_path = context.binding_path.resolve(strict=True)
    _need(binding_path != target and not binding_path.is_relative_to(target),
          "bounded_g1b_binding_inside_target")
    _need(all(not binding_path.is_relative_to(p) for p in
              (administration["gitdir"], administration["commondir"])), "bounded_g1b_binding_inside_git")
    snapshots = {}

    def read(path: Path, expected: str) -> bytes:
        snapshot = trusted_git._read_regular_snapshot(path, maximum_bytes=2 * 1024 * 1024)
        _need(_sha(snapshot[1]) == expected, "bounded_g1b_input_digest_changed")
        snapshots[path] = snapshot
        return snapshot[1]

    binding = _json(read(binding_path, context.expected_binding_sha256))
    _keys(binding, {"schema_version", "operation_id", "operation_kind", "phase", "base_commit", "base_tree",
                    "expected_head", "expected_index_tree", "candidate_tree", "source_sha256", "payload_sha256",
                    "activation_commit"},
          "bounded_g1b_binding_schema")
    _need(binding["schema_version"] == BINDING_VERSION, "bounded_g1b_binding_version")
    operation = _operation(binding["operation_kind"])
    _need(type(binding["operation_id"]) is str and re.fullmatch(r"[a-z0-9][a-z0-9-]{1,79}", binding["operation_id"]),
          "bounded_g1b_operation_id")
    _need(binding["phase"] in {"development", "pre-push", "post-push"}, "bounded_g1b_phase")
    _need(all(type(binding[k]) is str and re.fullmatch(r"[0-9a-f]{40}", binding[k])
              for k in ("base_commit", "base_tree", "expected_head", "expected_index_tree", "candidate_tree")),
          "bounded_g1b_git_binding")
    source_pins = _digest_map(binding["source_sha256"], SOURCE_PATHS, "bounded_g1b_source_paths")
    payload_pins = _digest_map(binding["payload_sha256"], operation["input_paths"], "bounded_g1b_payload_paths")
    for path, digest in source_pins.items():
        read(source / path, digest)
    _need(source_pins["orchestration_harness/trusted_git.py"] ==
          "5f8bfd44b63282e205a22bef1b81d0b8b5271572ba47c5b5df7371c0f638874f", "bounded_g1b_git_source_changed")
    before = {path: read(source / operation["baseline_directory"] / path, digest)
              for path, digest in operation["baseline_pins"].items()}
    payloads = {path: read(target / path, payload_pins[path]) for path in sorted(operation["input_paths"])}
    frozen_pins = dict(FROZEN_PINS)
    if operation["successor"]:
        frozen_pins.update({COST: COST_PIN, SCOPE_PATH: G1B_BASELINE_PINS[SCOPE_PATH]})
    for path, digest in frozen_pins.items():
        _need(_sha(payloads[path]) == digest, "bounded_g1b_frozen_input_changed")
    evidence = {path: read(evidence_root / path, digest) for path, digest in operation["evidence_pins"].items()}
    base = binding["base_commit"]
    if operation["successor"]:
        accepted = PERSISTENCE_PUBLICATION["commit"]
        headers = trusted_git.run_git(target, "cat-file", "commit", accepted).split("\n\n", 1)[0].splitlines()
        _need([line for line in headers if line.startswith("parent ")] ==
              ["parent " + PERSISTENCE_PUBLICATION["parent"]]
              and [line for line in headers if line.startswith("tree ")] ==
              ["tree " + PERSISTENCE_PUBLICATION["tree"]], "bounded_g1c_component_publication_invalid")
        trusted_git.run_git(target, "merge-base", "--is-ancestor", accepted, base)
        for path, digest in PERSISTENCE_PINS.items():
            _need(_sha(trusted_git.run_git_bytes(target, "cat-file", "blob", accepted + ":" + path)) == digest,
                  "bounded_g1c_accepted_component_changed")
    if operation["transition"]:
        _need(binding["activation_commit"] is None, "bounded_g1b_premature_activation")
        for path, digest in operation["baseline_pins"].items():
            _need(_sha(trusted_git.run_git_bytes(target, "cat-file", "blob", base + ":" + path)) == digest,
                  "bounded_g1b_actual_predecessor_changed")
        _need(trusted_git.run_git_bytes(target, "ls-tree", "-z", base, "--", operation["scope_path"]) == b"",
              "bounded_g1b_predecessor_already_active")
    else:
        activation = binding["activation_commit"]
        _need(type(activation) is str and re.fullmatch(r"[0-9a-f]{40}", activation),
              "bounded_g1b_activation_binding_required")
        scope = _json(payloads[operation["scope_path"]])
        headers = trusted_git.run_git(target, "cat-file", "commit", activation).split("\n\n", 1)[0].splitlines()
        _need([line for line in headers if line.startswith("parent ")] ==
              ["parent " + scope["transition_base_commit"]], "bounded_g1b_activation_parent_invalid")
        trusted_git.run_git(target, "merge-base", "--is-ancestor", activation, base)
        for path in operation["transition_paths"]:
            for commit in (activation, base):
                _need(trusted_git.run_git_bytes(target, "cat-file", "blob", commit + ":" + path) == payloads[path],
                      "bounded_g1b_activation_not_committed")
    attested = operation["input_paths"]
    if operation["transition"] and binding["phase"] == "development":
        attested = attested - operation["transition_paths"]
    observation = trusted_git.attest_target_index(target, attested_paths=tuple(sorted(attested)),
        expected_head=binding["expected_head"], expected_index_tree=binding["expected_index_tree"], scratch_parent=scratch)
    _need(trusted_git.run_git(target, "rev-parse", binding["base_commit"] + "^{tree}") == binding["base_tree"],
          "bounded_g1b_base_tree_changed")
    if binding["phase"] == "development":
        _need(binding["expected_head"] == binding["base_commit"] and binding["expected_index_tree"]
              in {binding["base_tree"], binding["candidate_tree"]}, "bounded_g1b_development_binding")
    else:
        headers = trusted_git.run_git(target, "cat-file", "commit", binding["expected_head"]).split("\n\n", 1)[0].splitlines()
        _need([line for line in headers if line.startswith("parent ")] == ["parent " + binding["base_commit"]]
              and [line for line in headers if line.startswith("tree ")] == ["tree " + binding["candidate_tree"]]
              and binding["expected_index_tree"] == binding["candidate_tree"], "bounded_g1b_committed_binding")
    for path, snapshot in snapshots.items():
        _need(trusted_git._read_regular_snapshot(path, maximum_bytes=2 * 1024 * 1024) == snapshot,
              "bounded_g1b_snapshot_drift")
    return BoundedG1BInputs(binding, before, payloads, evidence, observation)


def _validate_loaded_policy(inputs: BoundedG1BInputs) -> dict[str, bytes]:
    from orchestration_harness import programme_admission

    operation = _operation(inputs.binding["operation_kind"])
    after = {path: inputs.payloads[path] for path in operation["transition_paths"]}
    validator = validate_g1c_acceptance_transition if operation["successor"] else validate_g1b_acceptance_transition
    validator(inputs.before, after, inputs.evidence)
    try:
        programme_admission._validate_precedence(
            _document(inputs.payloads[PROJECT], PROJECT),
            _document(inputs.payloads[CONTINUATION], CONTINUATION),
            after[AGENTS].decode("utf-8"), _json(after[STATE]),
        )
    except programme_admission.ProgrammeAdmissionError as error:
        raise BoundedG1BError(error.reason_code) from error
    if operation["transition"]:
        _need(_json(after[operation["scope_path"]])["transition_base_commit"] == inputs.binding["base_commit"],
              "bounded_g1b_transition_base_mismatch")
    return after


def build_bounded_g1b_manifest(context: BoundedG1BContext) -> dict:
    inputs = load_bounded_g1b_inputs(context)
    _validate_loaded_policy(inputs)
    q = inputs.binding
    return {"schema_version": REQUEST_VERSION, "operation_id": q["operation_id"],
            "operation_kind": q["operation_kind"], "binding_sha256": context.expected_binding_sha256,
            "candidate_tree": q["candidate_tree"], "allowed_paths": sorted(operation_paths(q["operation_kind"])),
            "intended_side_effect_classes": sorted(EFFECTS)}


def evaluate_bounded_g1b_operation(*, context: BoundedG1BContext | None, manifest: object,
                                  entrypoint: str, phase: str, target_root: Path | None = None,
                                  source_root: Path | None = None) -> BoundedG1BDecision:
    try:
        _need(type(context) is BoundedG1BContext, "bounded_g1b_context_required")
        _need(target_root is None or target_root.absolute() == context.target_root.absolute(),
              "bounded_g1b_caller_target_mismatch")
        _need(source_root is None or source_root.absolute() == context.source_root.absolute(),
              "bounded_g1b_caller_source_mismatch")
        _need(entrypoint in {"recovery_preflight", "task_branch_commit", "task_branch_push"},
              "bounded_g1b_entrypoint_closed")
        _need(phase in {"development", "pre-push", "post-push"}, "bounded_g1b_phase")
        _need(entrypoint != "task_branch_commit" or phase == "development", "bounded_g1b_commit_phase")
        _need(entrypoint != "task_branch_push" or phase in {"pre-push", "post-push"}, "bounded_g1b_push_phase")
        _keys(manifest, {"schema_version", "operation_id", "operation_kind", "binding_sha256", "candidate_tree",
                         "allowed_paths", "intended_side_effect_classes"}, "bounded_g1b_manifest_schema")
        _need(manifest["schema_version"] == REQUEST_VERSION, "bounded_g1b_manifest_version")
        inputs = load_bounded_g1b_inputs(context)
        q = inputs.binding
        _need(q["phase"] == phase, "bounded_g1b_phase_disagreement")
        expected = {"schema_version": REQUEST_VERSION, "operation_id": q["operation_id"],
                    "operation_kind": q["operation_kind"], "binding_sha256": context.expected_binding_sha256,
                    "candidate_tree": q["candidate_tree"], "allowed_paths": sorted(operation_paths(q["operation_kind"])),
                    "intended_side_effect_classes": sorted(EFFECTS)}
        _need(_canonical(manifest) == _canonical(expected), "bounded_g1b_manifest_binding_mismatch")
        _validate_loaded_policy(inputs)
        operation = _operation(q["operation_kind"])
        return BoundedG1BDecision(True, (), entrypoint, phase, q["operation_id"], q["candidate_tree"],
                                 context.expected_binding_sha256, inputs.index_observation["observation_sha256"],
                                 claim_limits=operation["limits"], current_gate=operation["gate"],
                                 active_profile=operation["profile"])
    except (BoundedG1BError, trusted_git.TrustedGitError) as error:
        return BoundedG1BDecision(False, (error.reason_code,), entrypoint, phase)
    except (OSError, ValueError, TypeError, KeyError, RecursionError, yaml.YAMLError):
        return BoundedG1BDecision(False, ("bounded_g1b_invalid_input",), entrypoint, phase)


def bounded_g1b_report(*, context: BoundedG1BContext | None, manifest: object,
                       entrypoint: str, phase: str, target_root: Path | None = None) -> dict:
    decision = evaluate_bounded_g1b_operation(context=context, manifest=manifest, entrypoint=entrypoint,
                                             phase=phase, target_root=target_root)
    return {"schema_version": "raisa-ariadne.bounded-g1b-preflight.v1",
            "status": "policy_eligible" if decision.policy_admitted else "blocked", "read_only": True,
            "phase": phase, "requested_entrypoint": entrypoint, "programme_mode": "recovery",
            "current_gate": decision.current_gate, "active_profile": decision.active_profile,
            "feature_work_eligible": False, "global_gate": "red_repair_only", "execution_authorized": False,
            "reason_codes": list(decision.reason_codes), "failed_checks": list(decision.reason_codes),
            "candidate_tree": decision.candidate_tree, "binding_sha256": decision.binding_sha256,
            "observation_sha256": decision.observation_sha256, "claim_limits": list(decision.claim_limits), "checks": []}
