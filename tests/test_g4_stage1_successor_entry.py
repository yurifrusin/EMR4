"""Focused successor policy checks using the exact permitted UI12 prestate."""
import copy
import hashlib
import json
from pathlib import Path
import pytest
from orchestration_harness import bounded_g1b, raisa_policy

BASE = Path("C:/Users/there/EMR4-tools/g4-stage1-interactive-product-actual-v1")
PUBLICATION = Path("C:/Users/there/EMR4-migration/20260911-v1/current-control-repair-20260912-v1/demo-led-stage1-20261012-v2/stage1-interactive-product-publication-source-v2/independent-stage1-interactive-product-push-effect-review-v2.json")
PUBLICATION_SHA = "7453f0a1819cf350464687599be78477d8d0cccde072b322cf6539bfdad476df"

def _scope():
    return json.loads((Path(__file__).parents[1] / bounded_g1b.G4_STAGE1_SUCCESSOR_SCOPE).read_bytes())

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
        assert raw == (Path(__file__).parents[1] / path).read_bytes()
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
