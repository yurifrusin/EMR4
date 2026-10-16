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
    return json.loads((Path(__file__).parents[1] / bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE).read_bytes())

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
