"""Focused successor policy checks using the exact permitted UI12 prestate."""
import copy
import hashlib
import json
from pathlib import Path
import pytest
from orchestration_harness import bounded_g1b, raisa_policy

BASE = Path("C:/Users/there/EMR4-tools/g4-stage1-interactive-product-actual-v1")
PUBLICATION = Path("C:/Users/there/EMR4-migration/20260911-v1/current-control-repair-20260912-v1/demo-led-stage1-20261012-v2/stage1-interactive-product-publication-source-v2/independent-stage1-interactive-product-push-effect-review-v2.json")
HISTORICAL_AFTERIMAGES = Path("C:/Users/there/EMR4-tools/g4-stage1-successor-control-actual-v2")
# Historical v1 tests retain their own accepted phase and exact Scope6e9/afterimages.
PUBLICATION_SHA = "7453f0a1819cf350464687599be78477d8d0cccde072b322cf6539bfdad476df"

def _scope():
    raw = (HISTORICAL_AFTERIMAGES / bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == "6e9ece8b95fe3b47b5969d44b0f1b644cef92e751ec62ab03bd2b6be25bcacd8"
    return json.loads(raw)

def _before():
    expected = {path: bounded_g1b.G4_STAGE1_SUCCESSOR_BASE_CONTROL[path]
                for path in (bounded_g1b.STATE, bounded_g1b.GATES, bounded_g1b.OVERLAY, bounded_g1b.AGENTS)}
    result = {}
    for path, digest in expected.items():
        raw = (BASE / path).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == digest
        result[path] = raw
    return result

def _publication():
    raw = PUBLICATION.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PUBLICATION_SHA
    return json.loads(raw)

def _build(scope):
    return bounded_g1b.build_g4_stage1_successor_transition(_before(), scope, _publication())

def test_valid_pinned_transition_matches_authored_afterimages():
    before = _before()
    result = _build(_scope())
    assert set(result) == {bounded_g1b.STATE, bounded_g1b.OVERLAY, bounded_g1b.AGENTS,
                           bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE}
    for path, raw in result.items():
        assert raw == (HISTORICAL_AFTERIMAGES / path).read_bytes()
    original = json.loads(before[bounded_g1b.STATE])
    proposed = json.loads(result[bounded_g1b.STATE])
    assert proposed["g2"] == original["g2"] and proposed["g3"] == original["g3"]

def test_missing_timestamp_is_rejected_with_valid_pinned_prestate():
    scope = _scope()
    assert scope["recorded_at"] is not None and len(scope["source_sha256"]) == 8
    scope["recorded_at"] = None
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        _build(scope)
    assert caught.value.reason_code == "bounded_g4_stage1_successor_scope_boundary"

def test_missing_source_map_is_rejected_by_required_digest_validator():
    # Exercise the mandatory source-map primitive; this is not whole-loader proof.
    scope = _scope()
    scope["source_sha256"] = None
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        bounded_g1b._digest_map(scope["source_sha256"],
            bounded_g1b.SOURCE_PATHS | bounded_g1b.CONTROLLER_PATHS,
            "bounded_g4_stage1_successor_sources")
    assert caught.value.reason_code == "bounded_g4_stage1_successor_sources"

@pytest.mark.parametrize("change", [
    {"selected_base": {"commit": "0" * 40, "tree": "0" * 40}},
    {"voice_activation": True},
    {"admission_grants_runtime_authority": True},
    {"allowed_paths": ["app/main.py"]},
    {"allowed_effects": ["provider_invocation"]},
])
def test_wrong_base_or_wider_scope_is_rejected(change):
    scope = _scope()
    scope.update(change)
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        _build(scope)
    assert caught.value.reason_code == "bounded_g4_stage1_successor_scope_boundary"

def test_reviewed_eight_file_map_cannot_be_replaced():
    scope = _scope()
    scope["product_sha256"]["stage1_demo_http.py"] = "0" * 64
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        _build(scope)
    assert caught.value.reason_code == "bounded_g4_stage1_successor_required_product"

def test_path_selection_is_exact_and_old_profile_is_preserved():
    required = frozenset(bounded_g1b.G4_STAGE1_SUCCESSOR_PRODUCT_AFTERIMAGES)
    binding = {"operation_kind": "implement_g4_stage1_successor",
               "repair_sha256": {path: {} for path in required}}
    assert bounded_g1b.operation_paths("implement_g4_stage1_successor", binding) == required
    for path, add in (("app/main.py", True), ("stage1_demo_http.py", False)):
        invalid = copy.deepcopy(binding)
        if add:
            invalid["repair_sha256"][path] = {}
        else:
            del invalid["repair_sha256"][path]
        with pytest.raises(bounded_g1b.BoundedG1BError):
            bounded_g1b.operation_paths("implement_g4_stage1_successor", invalid)
    assert len(raisa_policy.g4_stage1_interactive_profile()["allowed_paths"]) == 12
    assert len(raisa_policy.g4_stage1_successor_profile()["allowed_paths"]) == 16


# Current v2 correction tests. The v1 tests above retain the frozen prestate and
# frozen afterimages of their own accepted transition.
def _correction_scope():
    raw = (Path("C:/Users/there/EMR4-tools/g4-stage1-header-control-actual-v1") / bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == "21a77991d10acf9cb62bea845bfeeb51b23cc4b5804edde578528f883203b1e5"
    return json.loads(raw)

def test_header_correction_scope_and_literal_operations():
    scope = _correction_scope()
    assert bounded_g1b.validate_g4_header_correction_scope(scope) == scope["source_sha256"]
    assert scope["product_sha256"] == {"stage1_demo_http.py":
        "49c9424dc8a6f92f9c312c0d198691901869752889481a1d5f8b41168cce63dc"}
    for kind, paths in (
        ("enable_g4_stage1_successor", bounded_g1b.G4_HEADER_CONTROL),
        ("implement_g4_stage1_successor", bounded_g1b.G4_HEADER_PRODUCT)):
        q = {"schema_version": bounded_g1b.G4_HEADER_BINDING_SCHEMA,
             "operation_kind": kind, "repair_sha256": {p: {} for p in paths}}
        assert bounded_g1b.operation_paths(kind, q) == paths
        assert bounded_g1b._operation(kind, q)["g4_header_correction"] is True
        assert bounded_g1b._operation(kind, q)["profile"] == raisa_policy.G4_STAGE1_SUCCESSOR_PROFILE
    assert len(bounded_g1b.G4_HEADER_CONTROL) == 3
    assert len(bounded_g1b.G4_HEADER_PRODUCT) == 1

@pytest.mark.parametrize("change", [
    {"selected_base": {"commit": "0" * 40, "tree": "0" * 40}},
    {"selected_base": bounded_g1b.G4_STAGE1_SUCCESSOR_BASE},
    {"voice_activation": True},
    {"admission_grants_runtime_authority": True},
    {"runtime_binding_required": False},
    {"allowed_paths": ["static/demo/stage1-interactive.js"]},
    {"allowed_effects": ["provider_invocation"]},
    {"recorded_at": None},
])
def test_header_correction_scope_rejects_stale_or_wider_contract(change):
    scope = _correction_scope()
    scope.update(change)
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        bounded_g1b.validate_g4_header_correction_scope(scope)
    assert caught.value.reason_code == "bounded_g4_header_scope_boundary"

def test_header_correction_rejects_any_other_product_hash():
    scope = _correction_scope()
    scope["product_sha256"]["stage1_demo_http.py"] = "0" * 64
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        bounded_g1b.validate_g4_header_correction_scope(scope)
    assert caught.value.reason_code == "bounded_g4_header_product_map"

@pytest.mark.parametrize("field", ["predecessor_scope", "predecessor_publication", "correction_source_review"])
def test_header_correction_literal_evidence_cannot_be_substituted(field):
    scope = _correction_scope()
    scope[field]["path"] = "C:/unpermitted-authored-placeholder.json"
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        bounded_g1b.validate_g4_header_correction_scope(scope)
    assert caught.value.reason_code == "bounded_g4_header_literal_evidence"

def test_header_correction_keeps_eight_closed_source_rows():
    scope = _correction_scope()
    assert len(scope["source_sha256"]) == 8
    for path in scope["source_sha256"]:
        changed = copy.deepcopy(scope)
        if path == bounded_g1b.G4_HEADER_CODE:
            changed["control_sha256"][path] = "0" * 64
        else:
            changed["source_sha256"][path] = "0" * 64
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b.validate_g4_header_correction_scope(changed)
        assert caught.value.reason_code == "bounded_g4_header_source_vector"

@pytest.mark.parametrize("paths", [
    frozenset(bounded_g1b.G4_STAGE1_SUCCESSOR_PRODUCT_AFTERIMAGES),
    frozenset({"stage1_demo_http.py", "static/demo/stage1-interactive.js"}),
    frozenset({"app/main.py"}),
    frozenset(),
])
def test_header_correction_exact_one_delta_is_not_profile_ceiling(paths):
    q = {"schema_version": bounded_g1b.G4_HEADER_BINDING_SCHEMA,
         "operation_kind": "implement_g4_stage1_successor",
         "repair_sha256": {path: {} for path in paths}}
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        bounded_g1b.operation_paths(q["operation_kind"], q)
    assert caught.value.reason_code == "bounded_g4_header_changed_paths"

def test_header_correction_does_not_relax_v1_exact_eight():
    q = {"schema_version": "ariadne.g4_stage1_successor_operation_binding.v1",
         "operation_kind": "implement_g4_stage1_successor",
         "repair_sha256": {"stage1_demo_http.py": {}}}
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        bounded_g1b.operation_paths(q["operation_kind"], q)
    assert caught.value.reason_code == "bounded_g4_stage1_successor_changed_paths"
    q["repair_sha256"] = {p: {} for p in bounded_g1b.G4_STAGE1_SUCCESSOR_PRODUCT_AFTERIMAGES}
    assert bounded_g1b.operation_paths(q["operation_kind"], q) == frozenset(q["repair_sha256"])

def test_header_source_review_uses_actual_split_blocker_schema():
    row = bounded_g1b.G4_HEADER_SOURCE_REVIEW
    raw = Path(row["path"]).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == row["sha256"]
    review = json.loads(raw)
    assert "reviewer_agent" not in review
    bounded_g1b._g4_header_product_source_acceptance(review)
    for field, value in (("independent", False), ("implementation_authorship", True),
                         ("blocking_findings_for_patch", ["authored"]), ("blocking_findings_for_current_fixture", ["authored"])):
        changed = copy.deepcopy(review)
        changed[field] = value
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b._g4_header_product_source_acceptance(changed)
        assert caught.value.reason_code == "bounded_g4_header_product_source_acceptance"


# Dormant v3 voice source: exercise the narrow validators, not runtime authority.
def _voice_scope():
    path = Path("C:/Users/there/EMR4-migration/20260911-v1/current-control-repair-20260912-v1/demo-led-stage1-20261012-v2/stage1-voice-current-entry-source-v1/candidate-source-v2/orchestration/programme/g4-stage1-successor-entry-scope.json")
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == "516c286e63e94c5968eb6187783f62eb4d65b3a9eb6bfbe48a7a719ba03d037b"
    return json.loads(raw)


def _voice_binding(kind="enable_g4_stage1_successor"):
    scope = _voice_scope()
    paths = (bounded_g1b.G4_VOICE_CONTROL if kind.startswith("enable_")
             else bounded_g1b.G4_VOICE_PRODUCT)
    return {"schema_version": bounded_g1b.G4_VOICE_BINDING_SCHEMA,
            "operation_id": "voice-source-enable-development",
            "operation_kind": kind, "phase": "development",
            "base_commit": bounded_g1b.G4_VOICE_BASE["commit"],
            "base_tree": bounded_g1b.G4_VOICE_BASE["tree"],
            "expected_head": bounded_g1b.G4_VOICE_BASE["commit"],
            "expected_index_tree": bounded_g1b.G4_VOICE_BASE["tree"],
            "candidate_tree": "a" * 40, "source_sha256": scope["source_sha256"],
            "payload_sha256": {bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE: "b" * 64},
            "repair_sha256": {p: {"before_sha256": bounded_g1b.G4_VOICE_PREIMAGES[p],
                                  "after_sha256": "c" * 64} for p in paths},
            "source_review": None,
            "predecessor_publication": scope["predecessor_publication"],
            "correction_source_review": scope["correction_source_review"],
            "activation_acceptance": None}


def test_voice_v3_exact_three_path_dispatch_preserves_legacy_schemas():
    scope = _voice_scope()
    assert bounded_g1b.validate_g4_voice_source_scope(scope) == scope["source_sha256"]
    for kind, paths in (("enable_g4_stage1_successor", bounded_g1b.G4_VOICE_CONTROL),
                        ("implement_g4_stage1_successor", bounded_g1b.G4_VOICE_PRODUCT)):
        q = _voice_binding(kind)
        assert bounded_g1b.operation_paths(kind, q) == paths
        assert len(paths) == 3
        operation = bounded_g1b._operation(kind, q)
        assert operation["g4_voice_source"] is True
        assert operation["gate"] == "G4"
        assert operation["profile"] == raisa_policy.G4_STAGE1_SUCCESSOR_PROFILE
        assert "g4_header_correction" not in operation
    assert bounded_g1b.G4_HEADER_BINDING_SCHEMA.endswith(".v2")
    assert bounded_g1b.G4_HEADER_PRODUCT == {"stage1_demo_http.py"}


@pytest.mark.parametrize("change", [
    {"schema_version": bounded_g1b.G4_HEADER_SCOPE_SCHEMA},
    {"selected_base": bounded_g1b.G4_HEADER_BASE},
    {"selected_base": {"commit": bounded_g1b.G4_VOICE_BASE["commit"], "tree": "0" * 40}},
    {"voice_activation": True}, {"runtime_binding_required": False},
    {"admission_grants_runtime_authority": True}, {"native08_dependency_only": False},
    {"allowed_paths": ["stage1_demo_http.py"]},
    {"allowed_effects": ["provider_invocation"]}, {"recorded_at": None},
    {"recorded_at": "malformed"}, {"recorded_at": "2026-10-17T00:00:00"},
])
def test_voice_scope_rejects_stale_or_wider_contract(change):
    scope = _voice_scope()
    scope.update(change)
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        bounded_g1b.validate_g4_voice_source_scope(scope)
    assert caught.value.reason_code == "bounded_g4_voice_scope_boundary"


def test_voice_scope_rejects_extra_keys_product_replacement_and_source_drift():
    scope = _voice_scope()
    for mutate, reason in (
        (lambda s: s.update(extra=True), "bounded_g4_voice_scope_schema"),
        (lambda s: s["product_sha256"].update({"stage1_demo_voice.py": "0" * 64}),
         "bounded_g4_voice_product_map"),
        (lambda s: s["source_sha256"].update({"orchestration_harness/trusted_git.py": "0" * 64}),
         "bounded_g4_voice_source_vector"),
        (lambda s: s["control_sha256"].update({bounded_g1b.G4_VOICE_CODE: "0" * 64}),
         "bounded_g4_voice_source_vector"),
        (lambda s: s["predecessor_publication"].update(sha256="0" * 64),
         "bounded_g4_voice_literal_evidence"),
        (lambda s: s["correction_source_review"].update(path="C:/substitute.json"),
         "bounded_g4_voice_source_review_pin"),
    ):
        changed = copy.deepcopy(scope)
        mutate(changed)
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b.validate_g4_voice_source_scope(changed)
        assert caught.value.reason_code == reason


@pytest.mark.parametrize("kind", ["enable_g4_stage1_successor", "implement_g4_stage1_successor"])
def test_voice_dispatch_rejects_any_extra_or_missing_path(kind):
    for extra in (True, False):
        q = _voice_binding(kind)
        if extra:
            q["repair_sha256"]["app/main.py"] = {}
        else:
            q["repair_sha256"].pop(next(iter(q["repair_sha256"])))
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b.operation_paths(kind, q)
        assert caught.value.reason_code == "bounded_g4_voice_changed_paths"


@pytest.mark.parametrize("field", [
    "schema_version", "operation_id", "operation_kind", "phase", "base_commit",
    "base_tree", "expected_head", "expected_index_tree", "candidate_tree",
    "source_sha256", "payload_sha256", "repair_sha256", "predecessor_publication",
    "correction_source_review", "activation_acceptance",
])
def test_voice_exact_subject_changes_for_every_authority_bearing_field(field):
    q = _voice_binding()
    before = bounded_g1b.g4_voice_source_review_subject(q)
    changed = copy.deepcopy(q)
    changed[field] = {"substituted": True} if isinstance(q[field], dict) else "substituted"
    assert bounded_g1b.g4_voice_source_review_subject(changed) != before
    q["source_review"] = {"path": "not-in-self-referential-subject", "sha256": "d" * 64}
    assert bounded_g1b.g4_voice_source_review_subject(q) == before


def test_voice_product_review_requires_exact_map_and_independent_named_reviewer():
    review = {"schema": "emr4.stage1_voice_current_product_source_review.v1",
              "verdict": "PASS_SOURCE_ONLY", "reviewer_agent": "/root/voice_entry_scope_review",
              "independent": True, "implementation_authorship": False,
              "blocking_findings": [], "product_sha256": dict(bounded_g1b.G4_VOICE_AFTER)}
    bounded_g1b._g4_voice_product_source_acceptance(review)
    for field, value in (("reviewer_agent", "/root/author"), ("independent", False),
                         ("implementation_authorship", True), ("blocking_findings", ["blocker"]),
                         ("product_sha256", {}), ("verdict", "PENDING")):
        changed = copy.deepcopy(review)
        changed[field] = value
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b._g4_voice_product_source_acceptance(changed)
        assert caught.value.reason_code == "bounded_g4_voice_product_source_acceptance"


@pytest.mark.parametrize("kind", ["enable_g4_stage1_successor", "implement_g4_stage1_successor"])
@pytest.mark.parametrize("phase", ["development", "pre-push", "post-push"])
def test_voice_subject_review_rejects_swapped_subject_reviewer_and_operation_path(kind, phase):
    q = _voice_binding(kind)
    q["phase"] = phase
    subject = bounded_g1b.g4_voice_source_review_subject(q)
    root = bounded_g1b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT
    operation = "enable" if kind.startswith("enable_") else "implement"
    suffix = "" if phase == "development" else "-" + phase
    path = root / ("stage1-voice-current-entry-source-v1/independent-" + operation
                   + suffix + "-exact-subject-review-v1.json")
    row = {"path": str(path), "sha256": "a" * 64}
    verdict = "PASS_G4_STAGE1_VOICE_SOURCE_EXACT_ADMISSION_SUBJECT"
    review = {"schema": "emr4.g4_operation_review.v1", "status": "PASS", "verdict": verdict,
              "independent": True, "implementation_authorship": False, "blocking_findings": [],
              "reviewer_agent": "/root/voice_entry_scope_review", "subject_sha256": subject}
    reads = []
    def read(path, digest):
        reads.append((path, digest))
        return json.dumps(review_body).encode()
    def check(value, selected_kind=kind, selected_phase=phase):
        nonlocal review_body
        review_body = value
        return bounded_g1b._g4_voice_subject_review(
            read, row, root, subject, verdict, selected_kind, selected_phase)
    review_body = review
    assert check(review) == review
    assert reads == [(path, row["sha256"])]
    for field, value in (("subject_sha256", "0" * 64), ("reviewer_agent", "/root/author"),
                         ("independent", False), ("implementation_authorship", True),
                         ("blocking_findings", ["blocker"]), ("status", "PENDING")):
        changed = copy.deepcopy(review)
        changed[field] = value
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            check(changed)
        assert caught.value.reason_code == "bounded_g4_voice_independent_subject"
    other_kind = ("implement_g4_stage1_successor" if kind.startswith("enable_")
                  else "enable_g4_stage1_successor")
    for selected_kind, selected_phase, reason in (
        (other_kind, phase, "bounded_g4_voice_review_path"),
        ("unknown", phase, "bounded_g4_voice_review_kind"),
        (kind, "unknown", "bounded_g4_voice_review_phase"),
        (kind, None, "bounded_g4_voice_review_phase"),
        *((kind, other_phase, "bounded_g4_voice_review_path")
          for other_phase in ("development", "pre-push", "post-push") if other_phase != phase),
    ):
        reads.clear()
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            check(review, selected_kind, selected_phase)
        assert caught.value.reason_code == reason
        assert reads == []


def test_voice_six_phase_kind_subjects_remain_distinct_and_bind_head_and_index():
    subjects = set()
    for kind in ("enable_g4_stage1_successor", "implement_g4_stage1_successor"):
        for phase in ("development", "pre-push", "post-push"):
            q = _voice_binding(kind)
            q["phase"] = phase
            subject = bounded_g1b.g4_voice_source_review_subject(q)
            subjects.add(subject)
            for field in ("expected_head", "expected_index_tree"):
                changed = copy.deepcopy(q)
                changed[field] = "0" * 40
                assert bounded_g1b.g4_voice_source_review_subject(changed) != subject
    assert len(subjects) == 6


def test_voice_control_publication_effect_review_keeps_its_fixed_path():
    root = bounded_g1b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT
    path = root / "stage1-voice-current-entry-source-v1/independent-voice-control-push-effect-review-v1.json"
    row = {"path": str(path), "sha256": "a" * 64}
    verdict = "PASS_G4_STAGE1_VOICE_SOURCE_CONTROL_PUBLICATION_EFFECT"
    subject = "c" * 40
    review = {"schema": "emr4.g4_operation_review.v1", "status": "PASS", "verdict": verdict,
              "independent": True, "implementation_authorship": False, "blocking_findings": [],
              "reviewer_agent": "/root/voice_entry_scope_review", "subject_sha256": subject}
    reads = []
    def read(selected_path, digest):
        reads.append((selected_path, digest))
        return json.dumps(review).encode()
    assert bounded_g1b._g4_voice_subject_review(read, row, root, subject, verdict) == review
    assert reads == [(path, row["sha256"])]


def test_voice_change_pair_rejects_wrong_preimage_afterimage_and_pair_shape():
    for path, after in bounded_g1b.G4_VOICE_AFTER.items():
        before = bounded_g1b.G4_VOICE_PREIMAGES[path]
        pair = {"before_sha256": before, "after_sha256": after}
        assert bounded_g1b._g4_voice_change_pair(path, pair, after) == before
        for field in ("before_sha256", "after_sha256"):
            changed = dict(pair)
            changed[field] = "0" * 64
            with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
                bounded_g1b._g4_voice_change_pair(path, changed, after)
            assert caught.value.reason_code == "bounded_g4_voice_change_preimage"
        pair["extra"] = True
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b._g4_voice_change_pair(path, pair, after)
        assert caught.value.reason_code == "bounded_g4_voice_change_pair"


def test_voice_activation_requires_exact_control_publication_effect():
    q = {"base_commit": "c" * 40, "base_tree": "d" * 40}
    receipt = {"tree": q["base_tree"], "base": bounded_g1b.G4_VOICE_BASE["commit"],
               "commit": q["base_commit"], "candidate": "control", "phase": "push",
               "published_ref": bounded_g1b.G4_STAGE1_INTERACTIVE_BACKEND_REF,
               "whole_inverse_verified_same_attempt": True,
               "protected_refs_unchanged": True, "same_attempt_remote_readback_verified": True}
    bounded_g1b._g4_voice_activation_acceptance(receipt, q)
    for key in receipt:
        changed = copy.deepcopy(receipt)
        changed[key] = False if receipt[key] is True else "substituted"
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b._g4_voice_activation_acceptance(changed, q)
        assert caught.value.reason_code == "bounded_g4_voice_activation_acceptance"


def test_voice_loaded_policy_rejects_configuration_drift_before_configuration_loading():
    scope = _voice_scope()
    payloads = {bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE: bounded_g1b._canonical(scope) + b"\n"}
    payloads.update({path: b"changed" for path in bounded_g1b.G4_VOICE_BASE_CONFIG})
    inputs = bounded_g1b.BoundedG1BInputs({}, {}, payloads, {"scope": scope}, None)
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        bounded_g1b._validate_g4_voice_source_loaded_policy(inputs)
    assert caught.value.reason_code == "bounded_g4_voice_configuration_unchanged"


# Additive v4 manual handoff source: narrow current validators, no runtime authority.
def _handoff_scope():
    path = Path("C:/Users/there/EMR4-migration/20260911-v1/current-control-repair-20260912-v1/demo-led-stage1-20261012-v2/stage1-voice-current-entry-source-v1/native-voice-intent-handoff-source-v1/control-admission-source-v1/candidate-source/orchestration/programme/g4-stage1-successor-entry-scope.json")
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == "d2fcc9c4284478a89ea28b44f8ed80731523b67790d03ec2a54fc39966b277df"
    return json.loads(raw)


def _handoff_binding(kind="enable_g4_stage1_successor"):
    scope = _handoff_scope()
    paths = (bounded_g1b.G4_HANDOFF_CONTROL if kind.startswith("enable_")
             else bounded_g1b.G4_HANDOFF_PRODUCT)
    return {"schema_version": bounded_g1b.G4_HANDOFF_BINDING_SCHEMA,
            "operation_id": "voice-source-enable-development",
            "operation_kind": kind, "phase": "development",
            "base_commit": bounded_g1b.G4_HANDOFF_BASE["commit"],
            "base_tree": bounded_g1b.G4_HANDOFF_BASE["tree"],
            "expected_head": bounded_g1b.G4_HANDOFF_BASE["commit"],
            "expected_index_tree": bounded_g1b.G4_HANDOFF_BASE["tree"],
            "candidate_tree": "a" * 40, "source_sha256": scope["source_sha256"],
            "payload_sha256": {bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE: "b" * 64},
            "repair_sha256": {p: {"before_sha256": bounded_g1b.G4_HANDOFF_PREIMAGES[p],
                                  "after_sha256": "c" * 64} for p in paths},
            "source_review": None,
            "predecessor_publication": scope["predecessor_publication"],
            "correction_source_review": scope["correction_source_review"],
            "activation_acceptance": None}


def test_handoff_v4_exact_four_path_dispatch_preserves_legacy_schemas():
    scope = _handoff_scope()
    assert bounded_g1b.validate_g4_handoff_source_scope(scope) == scope["source_sha256"]
    for kind, paths in (("enable_g4_stage1_successor", bounded_g1b.G4_HANDOFF_CONTROL),
                        ("implement_g4_stage1_successor", bounded_g1b.G4_HANDOFF_PRODUCT)):
        q = _handoff_binding(kind)
        assert bounded_g1b.operation_paths(kind, q) == paths
        assert len(paths) == (3 if kind.startswith("enable_") else 4)
        operation = bounded_g1b._operation(kind, q)
        assert operation["g4_handoff_source"] is True
        assert operation["gate"] == "G4"
        assert operation["profile"] == raisa_policy.G4_STAGE1_SUCCESSOR_PROFILE
        assert "g4_header_correction" not in operation
    assert bounded_g1b.G4_HEADER_BINDING_SCHEMA.endswith(".v2")
    assert bounded_g1b.G4_HEADER_PRODUCT == {"stage1_demo_http.py"}
    assert bounded_g1b.G4_VOICE_BINDING_SCHEMA.endswith(".v3")
    for kind, paths in (("enable_g4_stage1_successor", bounded_g1b.G4_VOICE_CONTROL),
                        ("implement_g4_stage1_successor", bounded_g1b.G4_VOICE_PRODUCT)):
        legacy = {"schema_version": bounded_g1b.G4_VOICE_BINDING_SCHEMA,
                  "operation_kind": kind, "repair_sha256": {p: {} for p in paths}}
        assert bounded_g1b.operation_paths(kind, legacy) == paths
        assert bounded_g1b._operation(kind, legacy)["g4_voice_source"] is True


@pytest.mark.parametrize("change", [
    {"schema_version": bounded_g1b.G4_HEADER_SCOPE_SCHEMA},
    {"selected_base": bounded_g1b.G4_HEADER_BASE},
    {"selected_base": {"commit": bounded_g1b.G4_HANDOFF_BASE["commit"], "tree": "0" * 40}},
    {"voice_activation": True}, {"runtime_binding_required": False},
    {"admission_grants_runtime_authority": True}, {"native08_dependency_only": False},
    {"allowed_paths": ["stage1_demo_http.py"]},
    {"allowed_effects": ["provider_invocation"]}, {"recorded_at": None},
    {"recorded_at": "malformed"}, {"recorded_at": "2026-10-17T00:00:00"},
])
def test_handoff_scope_rejects_stale_or_wider_contract(change):
    scope = _handoff_scope()
    scope.update(change)
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        bounded_g1b.validate_g4_handoff_source_scope(scope)
    assert caught.value.reason_code == "bounded_g4_handoff_scope_boundary"


def test_handoff_scope_rejects_extra_keys_product_replacement_and_source_drift():
    scope = _handoff_scope()
    for mutate, reason in (
        (lambda s: s.update(extra=True), "bounded_g4_handoff_scope_schema"),
        (lambda s: s["product_sha256"].update({"stage1_demo_voice.py": "0" * 64}),
         "bounded_g4_handoff_product_map"),
        (lambda s: s["source_sha256"].update({"orchestration_harness/trusted_git.py": "0" * 64}),
         "bounded_g4_handoff_source_vector"),
        (lambda s: s["control_sha256"].update({bounded_g1b.G4_HANDOFF_CODE: "0" * 64}),
         "bounded_g4_handoff_source_vector"),
        (lambda s: s["predecessor_publication"].update(sha256="0" * 64),
         "bounded_g4_handoff_literal_evidence"),
        (lambda s: s["correction_source_review"].update(path="C:/substitute.json"),
         "bounded_g4_handoff_source_review_pin"),
    ):
        changed = copy.deepcopy(scope)
        mutate(changed)
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b.validate_g4_handoff_source_scope(changed)
        assert caught.value.reason_code == reason


@pytest.mark.parametrize("kind", ["enable_g4_stage1_successor", "implement_g4_stage1_successor"])
def test_handoff_dispatch_rejects_any_extra_or_missing_path(kind):
    for extra in (True, False):
        q = _handoff_binding(kind)
        if extra:
            q["repair_sha256"]["app/main.py"] = {}
        else:
            q["repair_sha256"].pop(next(iter(q["repair_sha256"])))
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b.operation_paths(kind, q)
        assert caught.value.reason_code == "bounded_g4_handoff_changed_paths"


@pytest.mark.parametrize("field", [
    "schema_version", "operation_id", "operation_kind", "phase", "base_commit",
    "base_tree", "expected_head", "expected_index_tree", "candidate_tree",
    "source_sha256", "payload_sha256", "repair_sha256", "predecessor_publication",
    "correction_source_review", "activation_acceptance",
])
def test_handoff_exact_subject_changes_for_every_authority_bearing_field(field):
    q = _handoff_binding()
    before = bounded_g1b.g4_handoff_source_review_subject(q)
    changed = copy.deepcopy(q)
    changed[field] = {"substituted": True} if isinstance(q[field], dict) else "substituted"
    assert bounded_g1b.g4_handoff_source_review_subject(changed) != before
    q["source_review"] = {"path": "not-in-self-referential-subject", "sha256": "d" * 64}
    assert bounded_g1b.g4_handoff_source_review_subject(q) == before


def test_handoff_product_review_requires_exact_map_and_independent_named_reviewer():
    review = {"schema": "emr4.stage1_voice_current_product_source_review.v1",
              "verdict": "PASS_SOURCE_ONLY", "reviewer_agent": "/root/voice_entry_scope_review",
              "independent": True, "implementation_authorship": False,
              "blocking_findings": [], "product_sha256": dict(bounded_g1b.G4_HANDOFF_AFTER)}
    bounded_g1b._g4_handoff_product_source_acceptance(review)
    for field, value in (("reviewer_agent", "/root/author"), ("independent", False),
                         ("implementation_authorship", True), ("blocking_findings", ["blocker"]),
                         ("product_sha256", {}), ("verdict", "PENDING")):
        changed = copy.deepcopy(review)
        changed[field] = value
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b._g4_handoff_product_source_acceptance(changed)
        assert caught.value.reason_code == "bounded_g4_handoff_product_source_acceptance"


@pytest.mark.parametrize("kind", ["enable_g4_stage1_successor", "implement_g4_stage1_successor"])
@pytest.mark.parametrize("phase", ["development", "pre-push", "post-push"])
def test_handoff_subject_review_rejects_swapped_subject_reviewer_and_operation_path(kind, phase):
    q = _handoff_binding(kind)
    q["phase"] = phase
    subject = bounded_g1b.g4_handoff_source_review_subject(q)
    root = bounded_g1b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT
    operation = "enable" if kind.startswith("enable_") else "implement"
    suffix = "" if phase == "development" else "-" + phase
    path = root / ("stage1-voice-current-entry-source-v1/native-voice-intent-handoff-source-v1/control-admission-source-v1/independent-" + operation
                   + suffix + "-exact-subject-review-v1.json")
    row = {"path": str(path), "sha256": "a" * 64}
    verdict = "PASS_G4_STAGE1_VOICE_SOURCE_EXACT_ADMISSION_SUBJECT"
    review = {"schema": "emr4.g4_operation_review.v1", "status": "PASS", "verdict": verdict,
              "independent": True, "implementation_authorship": False, "blocking_findings": [],
              "reviewer_agent": "/root/voice_entry_scope_review", "subject_sha256": subject}
    reads = []
    def read(path, digest):
        reads.append((path, digest))
        return json.dumps(review_body).encode()
    def check(value, selected_kind=kind, selected_phase=phase):
        nonlocal review_body
        review_body = value
        return bounded_g1b._g4_handoff_subject_review(
            read, row, root, subject, verdict, selected_kind, selected_phase)
    review_body = review
    assert check(review) == review
    assert reads == [(path, row["sha256"])]
    for field, value in (("subject_sha256", "0" * 64), ("reviewer_agent", "/root/author"),
                         ("independent", False), ("implementation_authorship", True),
                         ("blocking_findings", ["blocker"]), ("status", "PENDING")):
        changed = copy.deepcopy(review)
        changed[field] = value
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            check(changed)
        assert caught.value.reason_code == "bounded_g4_handoff_independent_subject"
    other_kind = ("implement_g4_stage1_successor" if kind.startswith("enable_")
                  else "enable_g4_stage1_successor")
    for selected_kind, selected_phase, reason in (
        (other_kind, phase, "bounded_g4_handoff_review_path"),
        ("unknown", phase, "bounded_g4_handoff_review_kind"),
        (kind, "unknown", "bounded_g4_handoff_review_phase"),
        (kind, None, "bounded_g4_handoff_review_phase"),
        *((kind, other_phase, "bounded_g4_handoff_review_path")
          for other_phase in ("development", "pre-push", "post-push") if other_phase != phase),
    ):
        reads.clear()
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            check(review, selected_kind, selected_phase)
        assert caught.value.reason_code == reason
        assert reads == []


def test_handoff_six_phase_kind_subjects_remain_distinct_and_bind_head_and_index():
    subjects = set()
    for kind in ("enable_g4_stage1_successor", "implement_g4_stage1_successor"):
        for phase in ("development", "pre-push", "post-push"):
            q = _handoff_binding(kind)
            q["phase"] = phase
            subject = bounded_g1b.g4_handoff_source_review_subject(q)
            subjects.add(subject)
            for field in ("expected_head", "expected_index_tree"):
                changed = copy.deepcopy(q)
                changed[field] = "0" * 40
                assert bounded_g1b.g4_handoff_source_review_subject(changed) != subject
    assert len(subjects) == 6


def test_handoff_control_publication_effect_review_keeps_its_fixed_path():
    root = bounded_g1b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT
    path = root / "stage1-voice-current-entry-source-v1/native-voice-intent-handoff-source-v1/control-admission-source-v1/independent-voice-control-push-effect-review-v1.json"
    row = {"path": str(path), "sha256": "a" * 64}
    verdict = "PASS_G4_STAGE1_VOICE_SOURCE_CONTROL_PUBLICATION_EFFECT"
    subject = "c" * 40
    review = {"schema": "emr4.g4_operation_review.v1", "status": "PASS", "verdict": verdict,
              "independent": True, "implementation_authorship": False, "blocking_findings": [],
              "reviewer_agent": "/root/voice_entry_scope_review", "subject_sha256": subject}
    reads = []
    def read(selected_path, digest):
        reads.append((selected_path, digest))
        return json.dumps(review).encode()
    assert bounded_g1b._g4_handoff_subject_review(read, row, root, subject, verdict) == review
    assert reads == [(path, row["sha256"])]


def test_handoff_change_pair_rejects_wrong_preimage_afterimage_and_pair_shape():
    for path, after in bounded_g1b.G4_HANDOFF_AFTER.items():
        before = bounded_g1b.G4_HANDOFF_PREIMAGES[path]
        pair = {"before_sha256": before, "after_sha256": after}
        assert bounded_g1b._g4_handoff_change_pair(path, pair, after) == before
        for field in ("before_sha256", "after_sha256"):
            changed = dict(pair)
            changed[field] = "0" * 64
            with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
                bounded_g1b._g4_handoff_change_pair(path, changed, after)
            assert caught.value.reason_code == "bounded_g4_handoff_change_preimage"
        pair["extra"] = True
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b._g4_handoff_change_pair(path, pair, after)
        assert caught.value.reason_code == "bounded_g4_handoff_change_pair"


def test_handoff_activation_requires_exact_control_publication_effect():
    q = {"base_commit": "c" * 40, "base_tree": "d" * 40}
    receipt = {"tree": q["base_tree"], "base": bounded_g1b.G4_HANDOFF_BASE["commit"],
               "commit": q["base_commit"], "candidate": "control", "phase": "push",
               "published_ref": bounded_g1b.G4_STAGE1_INTERACTIVE_BACKEND_REF,
               "whole_inverse_verified_same_attempt": True,
               "protected_refs_unchanged": True, "same_attempt_remote_readback_verified": True}
    bounded_g1b._g4_handoff_activation_acceptance(receipt, q)
    for key in receipt:
        changed = copy.deepcopy(receipt)
        changed[key] = False if receipt[key] is True else "substituted"
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b._g4_handoff_activation_acceptance(changed, q)
        assert caught.value.reason_code == "bounded_g4_handoff_activation_acceptance"


def test_handoff_loaded_policy_rejects_configuration_drift_before_configuration_loading():
    scope = _handoff_scope()
    payloads = {bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE: bounded_g1b._canonical(scope) + b"\n"}
    payloads.update({path: b"changed" for path in bounded_g1b.G4_HANDOFF_BASE_CONFIG})
    inputs = bounded_g1b.BoundedG1BInputs({}, {}, payloads, {"scope": scope}, None)
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        bounded_g1b._validate_g4_handoff_source_loaded_policy(inputs)
    assert caught.value.reason_code == "bounded_g4_handoff_configuration_unchanged"


def test_handoff_only_new_test_accepts_absent_preimage():
    absent = "tests/test_stage1_voice_intent_handoff.cjs"
    assert bounded_g1b.G4_HANDOFF_PREIMAGES[absent] is None
    assert [p for p, value in bounded_g1b.G4_HANDOFF_PREIMAGES.items() if value is None] == [absent]
    after = bounded_g1b.G4_HANDOFF_AFTER[absent]
    assert bounded_g1b._g4_handoff_change_pair(absent, {"before_sha256": None, "after_sha256": after}, after) is None
    for path, before in bounded_g1b.G4_HANDOFF_PREIMAGES.items():
        if path == absent:
            continue
        with pytest.raises(bounded_g1b.BoundedG1BError):
            bounded_g1b._g4_handoff_change_pair(path, {"before_sha256": None, "after_sha256": "a" * 64}, "a" * 64)


# Prospective v5 audit correction. These checks do not execute an operation.
def _audit_scope():
    path = Path(__file__).resolve().parents[1] / bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE
    return json.loads(path.read_bytes())


def _audit_binding(kind):
    return {
        "schema_version": bounded_g1b.G4_AUDIT_BINDING_SCHEMA,
        "operation_id": "stage1-audit-example",
        "operation_kind": kind,
        "phase": "development",
        "base_commit": bounded_g1b.G4_AUDIT_BASE["commit"],
        "base_tree": bounded_g1b.G4_AUDIT_BASE["tree"],
        "expected_head": bounded_g1b.G4_AUDIT_BASE["commit"],
        "expected_index_tree": bounded_g1b.G4_AUDIT_BASE["tree"],
        "candidate_tree": "c" * 40,
        "source_sha256": _audit_scope()["source_sha256"],
        "payload_sha256": {},
        "repair_sha256": {path: {"before_sha256": bounded_g1b.G4_AUDIT_PREIMAGES[path],
                                 "after_sha256": "a" * 64}
                          for path in (bounded_g1b.G4_AUDIT_CONTROL if kind.startswith("enable_")
                                       else bounded_g1b.G4_AUDIT_PRODUCT)},
        "predecessor_publication": bounded_g1b.G4_AUDIT_BASE_EFFECT,
        "correction_source_review": {"path": str(bounded_g1b.G4_AUDIT_SOURCE_REVIEW_PATH),
                                     "sha256": bounded_g1b.G4_AUDIT_SOURCE_REVIEW_SHA},
        "entry_route_opinion": bounded_g1b.G4_AUDIT_ROUTE_REVIEW,
        "activation_acceptance": None,
        "source_review": {"path": "not-part-of-subject", "sha256": "a" * 64},
    }


def test_audit_scope_exact_nine_and_frozen_control_profile():
    scope = _audit_scope()
    bounded_g1b.validate_g4_audit_source_scope(scope)
    assert set(scope["product_sha256"]) == bounded_g1b.G4_AUDIT_PRODUCT
    assert scope["product_sha256"]["stage1_demo_http.py"] == "81628d878d86465734a955f945e05ac31797338b6697889670e50c91ff74268c"
    assert scope["product_sha256"]["tests/test_stage1_voice_intent_handoff.cjs"] == "e0e54bafd8a94bd10bbdc382f255c482554279349f06e6a33a5a77d25de34667"
    assert scope["correction_source_review"] == {
        "path": str(bounded_g1b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT /
                    "midstream-audit-correction-source-v1/independent-product-source-review-v4.json"),
        "sha256": "d17b9a91e918033ad85610ae8ac122e311bd01fa2bb952663792f7887e51dfde"}
    assert set(scope["control_sha256"]) == {bounded_g1b.G4_AUDIT_CODE,
                                            bounded_g1b.G4_STAGE1_SUCCESSOR_TEST}
    assert scope["active_profile"] == raisa_policy.G4_STAGE1_SUCCESSOR_PROFILE
    for key, value, reason in (
        ("allowed_paths", ["stage1_demo_http.py"], "bounded_g4_audit_scope_boundary"),
        ("voice_activation", True, "bounded_g4_audit_scope_boundary"),
        ("selected_base", {"commit": "0" * 40, "tree": "0" * 40}, "bounded_g4_audit_scope_boundary"),
        ("product_sha256", {}, "bounded_g4_audit_product_map"),
        ("entry_route_opinion", {"path": "wrong", "sha256": "0" * 64},
         "bounded_g4_audit_route_opinion_pin"),
    ):
        changed = copy.deepcopy(scope)
        changed[key] = value
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b.validate_g4_audit_source_scope(changed)
        assert caught.value.reason_code == reason


def test_audit_frozen_literal_rows_keep_forward_slashes_and_reject_aliases():
    scope = _audit_scope()
    for key, expected, reason in (
        ("entry_route_opinion", bounded_g1b.G4_AUDIT_ROUTE_REVIEW,
         "bounded_g4_audit_route_opinion_pin"),
        ("predecessor_scope", bounded_g1b.G4_AUDIT_PREDECESSOR_SCOPE,
         "bounded_g4_audit_literal_evidence"),
    ):
        assert scope[key] == expected
        assert expected["path"].startswith("C:/")
        assert "\\" not in expected["path"]
        for changed in (
            {**expected, "path": expected["path"].replace("/", "\\")},
            {**expected, "sha256": "0" * 64},
        ):
            with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
                bounded_g1b._g4_audit_row(changed, expected, reason)
            assert caught.value.reason_code == reason


@pytest.mark.parametrize("kind", ["enable_g4_stage1_successor", "implement_g4_stage1_successor"])
def test_audit_dispatch_uses_only_exact_kind_paths(kind):
    q = _audit_binding(kind)
    expected = (bounded_g1b.G4_AUDIT_CONTROL if kind.startswith("enable_")
                else bounded_g1b.G4_AUDIT_PRODUCT)
    assert bounded_g1b._g4_audit_paths(kind, q) == expected
    changed = copy.deepcopy(q)
    changed["repair_sha256"]["unowned.py"] = {"before_sha256": "a" * 64,
                                               "after_sha256": "b" * 64}
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        bounded_g1b._g4_audit_paths(kind, changed)
    assert caught.value.reason_code == "bounded_g4_audit_changed_paths"
    with pytest.raises(bounded_g1b.BoundedG1BError):
        bounded_g1b._g4_audit_paths("not-a-kind", q)


@pytest.mark.parametrize("kind", ["enable_g4_stage1_successor", "implement_g4_stage1_successor"])
def test_audit_public_operation_dispatch_keeps_exact_owned_paths(kind):
    q = _audit_binding(kind)
    expected = (bounded_g1b.G4_AUDIT_CONTROL if kind.startswith("enable_")
                else bounded_g1b.G4_AUDIT_PRODUCT)
    assert bounded_g1b.operation_paths(kind, q) == expected
    operation = bounded_g1b._operation(kind, q)
    assert operation["paths"] == expected
    assert operation["g4_audit_source"] is True
    assert operation["profile"] == raisa_policy.G4_STAGE1_SUCCESSOR_PROFILE
    assert operation["gate"] == "G4"
    assert not any(operation.get(flag) for flag in (
        "g4_handoff_source", "g4_voice_source", "g4_header_correction"))
    changed = copy.deepcopy(q)
    changed["repair_sha256"].pop(next(iter(expected)))
    for entry in (bounded_g1b.operation_paths, bounded_g1b._operation):
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            entry(kind, changed)
        assert caught.value.reason_code == "bounded_g4_audit_changed_paths"


def test_audit_review_requires_exact_independent_product_map():
    review = {"schema": "emr4.stage1_midstream_audit_product_source_review.v2",
              "status": "PASS_SOURCE_ONLY_EXACT_FINAL_CORRECTION", "independent": True,
              "implementation_authorship": False, "source_only": True,
              "runtime_accepted": False, "blocking_findings": [],
              "reviewer_agent": "/root/audit_product_source_review",
              "base": bounded_g1b.G4_AUDIT_BASE,
              "candidate": {"source_sha256": dict(bounded_g1b.G4_AUDIT_AFTER)}}
    bounded_g1b._g4_audit_product_source_acceptance(review)
    for field, value in (("status", "PASS_SOURCE_ONLY"), ("independent", False),
                         ("runtime_accepted", True), ("reviewer_agent", "/root/author"),
                         ("blocking_findings", ["unresolved"])):
        changed = copy.deepcopy(review)
        changed[field] = value
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b._g4_audit_product_source_acceptance(changed)
        assert caught.value.reason_code == "bounded_g4_audit_product_source_acceptance"
    review["candidate"]["source_sha256"]["stage1_demo_http.py"] = "0" * 64
    with pytest.raises(bounded_g1b.BoundedG1BError):
        bounded_g1b._g4_audit_product_source_acceptance(review)


@pytest.mark.parametrize("kind", ["enable_g4_stage1_successor", "implement_g4_stage1_successor"])
@pytest.mark.parametrize("phase", ["development", "pre-push", "post-push"])
def test_audit_subject_is_phase_specific_and_review_path_is_exact(kind, phase):
    q = _audit_binding(kind)
    q["phase"] = phase
    subject = bounded_g1b.g4_audit_source_review_subject(q)
    for field in ("schema_version", "operation_id", "operation_kind", "phase",
                  "base_commit", "base_tree", "expected_head", "expected_index_tree",
                  "candidate_tree", "source_sha256", "payload_sha256", "repair_sha256",
                  "predecessor_publication", "correction_source_review",
                  "entry_route_opinion", "activation_acceptance"):
        changed = copy.deepcopy(q)
        changed[field] = "changed"
        assert bounded_g1b.g4_audit_source_review_subject(changed) != subject
    changed = copy.deepcopy(q)
    changed["source_review"] = {"path": "other", "sha256": "b" * 64}
    assert bounded_g1b.g4_audit_source_review_subject(changed) == subject
    operation = "enable" if kind.startswith("enable_") else "implement"
    suffix = "" if phase == "development" else "-" + phase
    root = bounded_g1b.G4_STAGE1_SUCCESSOR_EVIDENCE_ROOT
    path = root / "midstream-audit-correction-source-v1/control-admission-source-v1" / (
        "independent-" + operation + suffix + "-exact-subject-review-v2.json")
    row = {"path": str(path), "sha256": "a" * 64}
    verdict = "PASS_G4_STAGE1_AUDIT_SOURCE_EXACT_ADMISSION_SUBJECT"
    review = {"schema": "emr4.g4_operation_review.v1", "status": "PASS", "verdict": verdict,
              "independent": True, "implementation_authorship": False,
              "blocking_findings": [], "reviewer_agent": "/root/audit_admission_route_review",
              "subject_sha256": subject}
    def read(selected_path, digest):
        assert (selected_path, digest) == (path, row["sha256"])
        return json.dumps(review).encode()
    assert bounded_g1b._g4_audit_subject_review(read, row, root, subject, verdict,
                                                  kind, phase) == review
    for field, value in (("reviewer_agent", "/root/author"), ("independent", False),
                         ("subject_sha256", "0" * 64), ("status", "PENDING")):
        changed_review = dict(review)
        changed_review[field] = value
        with pytest.raises(bounded_g1b.BoundedG1BError):
            bounded_g1b._g4_audit_subject_review(
                lambda _p, _d: json.dumps(changed_review).encode(), row, root,
                subject, verdict, kind, phase)
    wrong_row = {"path": str(path.with_name("unexpected.json")), "sha256": "a" * 64}
    with pytest.raises(bounded_g1b.BoundedG1BError):
        bounded_g1b._g4_audit_subject_review(read, wrong_row, root, subject, verdict, kind, phase)
    old_row = {"path": str(path.with_name(path.name.replace("-v2.json", "-v1.json"))),
               "sha256": "a" * 64}
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        bounded_g1b._g4_audit_subject_review(read, old_row, root, subject, verdict, kind, phase)
    assert caught.value.reason_code == "bounded_g4_audit_review_path"


def test_audit_only_parser_and_parser_test_have_absent_preimages():
    absent = {"stage1_demo_intent.py", "tests/test_stage1_demo_intent.py"}
    assert {path for path, before in bounded_g1b.G4_AUDIT_PREIMAGES.items()
            if before is None} == absent
    for path, after in bounded_g1b.G4_AUDIT_AFTER.items():
        before = bounded_g1b.G4_AUDIT_PREIMAGES[path]
        assert bounded_g1b._g4_audit_change_pair(
            path, {"before_sha256": before, "after_sha256": after}, after) == before
        wrong_before = "0" * 64 if before is None else None
        with pytest.raises(bounded_g1b.BoundedG1BError):
            bounded_g1b._g4_audit_change_pair(
                path, {"before_sha256": wrong_before, "after_sha256": after}, after)


def test_audit_loaded_policy_rejects_configuration_drift_before_loading():
    scope = _audit_scope()
    payloads = {bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE: bounded_g1b._canonical(scope) + b"\n"}
    payloads.update({path: b"changed" for path in bounded_g1b.G4_AUDIT_BASE_CONFIG})
    inputs = bounded_g1b.BoundedG1BInputs({}, {}, payloads, {"scope": scope}, None)
    with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
        bounded_g1b._validate_g4_audit_source_loaded_policy(inputs)
    assert caught.value.reason_code == "bounded_g4_audit_configuration_unchanged"


def test_audit_activation_requires_exact_independent_control_publication_effect():
    q = {"base_commit": "c" * 40, "base_tree": "d" * 40}
    receipt = {"tree": q["base_tree"], "base": bounded_g1b.G4_AUDIT_BASE["commit"],
               "commit": q["base_commit"], "candidate": "control", "phase": "push",
               "published_ref": bounded_g1b.G4_STAGE1_INTERACTIVE_BACKEND_REF,
               "whole_inverse_verified_same_attempt": True,
               "protected_refs_unchanged": True,
               "same_attempt_remote_readback_verified": True}
    bounded_g1b._g4_audit_activation_acceptance(receipt, q)
    for field in receipt:
        changed = copy.deepcopy(receipt)
        changed[field] = False if receipt[field] is True else "substituted"
        with pytest.raises(bounded_g1b.BoundedG1BError) as caught:
            bounded_g1b._g4_audit_activation_acceptance(changed, q)
        assert caught.value.reason_code == "bounded_g4_audit_activation_acceptance"
