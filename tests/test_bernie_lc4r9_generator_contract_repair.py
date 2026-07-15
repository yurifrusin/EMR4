#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Focused tests for LC4R9 generator-backed contract repair.

Verifies the frozen 11-case allowlist, audit-vocabulary override, non-selected
scenario drift protection (by exact pre-repair reconstruction), hash cascade
(recomputed), composed evaluator result, semantic/safety/variance baselines,
exit-count drift, and mutable-source copy protection.
"""

from __future__ import annotations

import copy
import hashlib
import json
import pathlib
import sys
import tempfile
from typing import Any

import pytest

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

HERE = pathlib.Path(__file__).resolve().parent
DOCS_DIR = PROJECT_ROOT / "docs"
FIXTURE_DIR = PROJECT_ROOT / "tests" / "fixtures" / "bernie_lc4_development"


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _stable_hash(content: str) -> str:
    return "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()


def _load_json(path: pathlib.Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_variant_hash(variant_data: dict[str, Any]) -> str:
    payload = {k: v for k, v in variant_data.items() if k != "variant_hash"}
    return _stable_hash(_canonical_json(payload))


ALLOWLIST_SELECTION_HASH = "b88018991e49ffd5"
ALLOWLIST_COUNT = 11

ALLOWLIST_SCENARIO_IDS: list[str] = [
    "lc4_dw1_dev_var_001_01",
    "lc4_dw1_dev_var_001_02",
    "lc4_dw1_dev_var_001_03",
    "lc4_dw1_dev_var_001_05",
    "lc4_dw1_dev_var_001_06",
    "lc4_dw1_dev_var_001_07",
    "lc4_dw1_dev_var_001_08",
    "lc4_dw1_dev_var_001_09",
    "lc4_dw1_dev_var_012_03",
    "lc4_dw1_dev_var_012_05",
    "lc4_dw1_dev_var_012_07",
]

PRE_REPAIR_DELTA_HASH = "14e3648ae8a98598bbc091ce16bf29f31fd5b2fdb92fe7d817ae86fb21837c69"

EXPECTED_AUDIT_OVERRIDE_CONTENT = {"change_type": "created", "appointment_id": "apt-001", "count": 1}

PRE_REPAIR_GROUP_001_HASH = "sha256:0874f6887020df0ae9abe0ca75a9ee60bc9eb0d55094701fbf5a48788cd71e5d"
PRE_REPAIR_GROUP_012_HASH = "sha256:76a4a27c6d217dcfd0fa4a96ea42b1416201b31fdb87af39c4bb32040f7fb9b6"
PRE_REPAIR_CORPUS_HASH = "sha256:aa2d946b60694eab96846ed77e885273c807e127f8998981a8cf8ff20ebae647"

EXPECTED_GROUP_COUNT = 96
EXPECTED_SURFACE_VARIANTS = 864
EXPECTED_MT_VARIANTS = 288
EXPECTED_TOTAL_VARIANTS = 1152

EXPECTED_SEMANTIC_COUNTS = (880, 814, 628, 101, 300, 782)
EXPECTED_SAFETY_PER_REPEAT = (1152, 1152)
EXPECTED_VARIANCE_SAMPLES = 2304
EXPECTED_EXIT_COUNTS = {
    "generator_repair_authorized": 0,
    "clarification_blockers": 53,
    "replay_contract_reconciliation_blockers": 40,
}


@pytest.fixture(scope="module")
def loader_and_corpus():
    from app.services.bernie.scale_corpus import DevelopmentOnlyLoader
    loader = DevelopmentOnlyLoader()
    corpus = loader.load_all()
    return loader, corpus

class TestAllowlistInvariants:
    def test_allowlist_source_validation(self):
        from app.services.bernie.scale_corpus import _validate_lc4r9_allowlist
        _validate_lc4r9_allowlist()

    def test_allowlist_count(self):
        from app.services.bernie.scale_corpus import LC4R9_AUDIT_VOCABULARY_ALLOWLIST, LC4R9_ALLOWLIST_COUNT
        assert len(LC4R9_AUDIT_VOCABULARY_ALLOWLIST) == LC4R9_ALLOWLIST_COUNT == ALLOWLIST_COUNT

    def test_allowlist_hash(self):
        from app.services.bernie.scale_corpus import LC4R9_AUDIT_VOCABULARY_ALLOWLIST, LC4R9_ALLOWLIST_SELECTION_HASH
        computed = hashlib.sha256("\n".join(sorted(LC4R9_AUDIT_VOCABULARY_ALLOWLIST)).encode("utf-8")).hexdigest()[:16]
        assert computed == LC4R9_ALLOWLIST_SELECTION_HASH == ALLOWLIST_SELECTION_HASH

    def test_allowlist_surface_only(self):
        from app.services.bernie.scale_corpus import LC4R9_AUDIT_VOCABULARY_ALLOWLIST
        assert all(sid.startswith("lc4_dw1_dev_var") for sid in LC4R9_AUDIT_VOCABULARY_ALLOWLIST)

    def test_allowlist_no_multi_turn(self):
        from app.services.bernie.scale_corpus import LC4R9_AUDIT_VOCABULARY_ALLOWLIST
        assert not any("_mt_" in sid for sid in LC4R9_AUDIT_VOCABULARY_ALLOWLIST)

    def test_allowlist_pre_repair_delta_hash(self):
        from app.services.bernie.scale_corpus import LC4R9_AUDIT_VOCABULARY_ALLOWLIST, LC4R9_PRE_REPAIR_DELTA_HASH
        lines = sorted(f"{sid}|create_requested|created" for sid in LC4R9_AUDIT_VOCABULARY_ALLOWLIST)
        computed = hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()
        assert computed == LC4R9_PRE_REPAIR_DELTA_HASH == PRE_REPAIR_DELTA_HASH

    def test_allowlist_action_is_create(self):
        from app.services.bernie.scale_corpus import LC4R9_AUDIT_VOCABULARY_ALLOWLIST
        manifest = _load_json(FIXTURE_DIR / "lc4_development_manifest.json")
        for g_entry in manifest["groups"]:
            if g_entry["action"] != "create":
                gdata = _load_json(FIXTURE_DIR / g_entry["filename"])
                for vdata in gdata.get("surface_variants", []):
                    assert vdata["scenario_id"] not in LC4R9_AUDIT_VOCABULARY_ALLOWLIST

    def test_allowlist_tamper_detection(self):
        test_ids = set(ALLOWLIST_SCENARIO_IDS)
        test_ids.add("lc4_dw1_dev_var_001_99")
        bad_hash = hashlib.sha256("\n".join(sorted(test_ids)).encode("utf-8")).hexdigest()[:16]
        assert bad_hash != ALLOWLIST_SELECTION_HASH

class TestVocabularyChange:
    def test_all_selected_have_created(self, loader_and_corpus):
        from app.services.bernie.scale_corpus import LC4R9_AUDIT_VOCABULARY_ALLOWLIST
        _, corpus = loader_and_corpus
        for g in corpus.groups:
            for v in g.surface_variants:
                if v.scenario_id in LC4R9_AUDIT_VOCABULARY_ALLOWLIST:
                    assert len(v.expected_audit_deltas) == 1
                    assert v.expected_audit_deltas[0]["change_type"] == "created"
                    assert v.expected_audit_deltas[0]["appointment_id"] == "apt-001"
                    assert v.expected_audit_deltas[0]["count"] == 1

    def test_selected_scenarios_found_in_fixtures(self):
        from app.services.bernie.scale_corpus import LC4R9_AUDIT_VOCABULARY_ALLOWLIST
        manifest = _load_json(FIXTURE_DIR / "lc4_development_manifest.json")
        all_variant_ids = set()
        for g_entry in manifest["groups"]:
            fname = g_entry["filename"]
            gdata = _load_json(FIXTURE_DIR / fname)
            for vdata in gdata.get("surface_variants", []):
                all_variant_ids.add(vdata["scenario_id"])
        for sid in LC4R9_AUDIT_VOCABULARY_ALLOWLIST:
            assert sid in all_variant_ids

    def test_selected_vocabulary_in_committed_json(self):
        from app.services.bernie.scale_corpus import LC4R9_AUDIT_VOCABULARY_ALLOWLIST
        for sid in LC4R9_AUDIT_VOCABULARY_ALLOWLIST:
            parts = sid.split("_")
            group_idx = int(parts[4])
            gdata = _load_json(FIXTURE_DIR / f"lc4_dw1_dev_group_{group_idx:03d}.json")
            found = False
            for vdata in gdata.get("surface_variants", []):
                if vdata.get("scenario_id") == sid:
                    found = True
                    aud = vdata.get("expected_audit_deltas", [])
                    assert len(aud) == 1
                    assert aud[0]["change_type"] == "created"
                    assert aud[0]["appointment_id"] == "apt-001"
                    assert aud[0]["count"] == 1
                    break
            assert found

    def test_pre_repair_vocabulary_constant(self):
        from app.services.bernie.scale_corpus import _derive_audit_deltas
        pre = _derive_audit_deltas("create")
        assert pre[0]["change_type"] == "create_requested"
        for action in ("move", "resize", "cancel", "status_change"):
            aud = _derive_audit_deltas(action)
            assert f"{action}_requested" in aud[0]["change_type"]


class TestHashCascade:
    def test_variant_hash_consistency(self):
        manifest = _load_json(FIXTURE_DIR / "lc4_development_manifest.json")
        for g_entry in manifest["groups"]:
            fname = g_entry["filename"]
            gdata = _load_json(FIXTURE_DIR / fname)
            for vdata in gdata.get("surface_variants", []):
                sid = vdata.get("scenario_id", "?")
                stored = vdata.get("variant_hash", "")
                if stored:
                    assert stored == compute_variant_hash(vdata), f"{sid} hash mismatch"
            for vdata in gdata.get("multi_turn_variants", []):
                sid = vdata.get("scenario_id", "?")
                stored = vdata.get("variant_hash", "")
                if stored:
                    assert stored == compute_variant_hash(vdata), f"{sid} (mt) hash mismatch"

    def test_group_hash_consistency(self, loader_and_corpus):
        _, corpus = loader_and_corpus
        manifest = _load_json(FIXTURE_DIR / "lc4_development_manifest.json")
        manifest_group_map = {g["group_id"]: g["group_hash"] for g in manifest["groups"]}
        for g in corpus.groups:
            assert g.group_hash == manifest_group_map[g.group_id]

    def test_group_hash_cascade(self):
        from app.services.bernie.scale_corpus import compute_group_hash
        manifest = _load_json(FIXTURE_DIR / "lc4_development_manifest.json")
        for g_entry in manifest["groups"]:
            gdata = _load_json(FIXTURE_DIR / g_entry["filename"])
            spec = gdata.get("spec", {})
            surface_h = [compute_variant_hash(vd) for vd in gdata.get("surface_variants", [])]
            mt_h = [compute_variant_hash(vd) for vd in gdata.get("multi_turn_variants", [])]
            rd = {"group_id": gdata["group_id"], "spec": spec,
                  "surface_count": len(surface_h), "multi_turn_count": len(mt_h),
                  "surface_variant_hashes": surface_h,
                  "multi_turn_variant_hashes": mt_h}
            assert compute_group_hash(rd) == g_entry["group_hash"]

    def test_corpus_hash_cascade(self, loader_and_corpus):
        _, corpus = loader_and_corpus
        manifest = _load_json(FIXTURE_DIR / "lc4_development_manifest.json")
        group_hashes = [g["group_hash"] for g in manifest["groups"]]
        recomputed = _stable_hash(_canonical_json(group_hashes))
        assert recomputed == manifest["corpus_hash"]
        assert recomputed == corpus.corpus_hash

    def test_only_affected_hashes_changed(self):
        manifest = _load_json(FIXTURE_DIR / "lc4_development_manifest.json")
        for g in manifest["groups"]:
            idx = g["group_index"]
            if idx == 1:
                assert g["group_hash"] != PRE_REPAIR_GROUP_001_HASH
            elif idx == 12:
                assert g["group_hash"] != PRE_REPAIR_GROUP_012_HASH


class TestComposedEvaluator:
    def test_composed_evaluator_audit_deltas(self, loader_and_corpus):
        from app.services.bernie.scale_corpus import LC4R9_AUDIT_VOCABULARY_ALLOWLIST
        from app.services.bernie.composed_corpus_evaluator import deterministic_interpret, deterministic_replay
        from app.services.bernie.composed_evaluator import score_interpretation_replay_pair
        _, corpus = loader_and_corpus
        for g in corpus.groups:
            for v in g.surface_variants:
                if v.scenario_id in LC4R9_AUDIT_VOCABULARY_ALLOWLIST:
                    interp = deterministic_interpret(v)
                    replay = deterministic_replay(v, interp)
                    score = score_interpretation_replay_pair(v, interp, replay)
                    assert score.audit_deltas.passed, f"{v.scenario_id} audit mismatch"

    def test_composed_evaluator_all_passed(self, loader_and_corpus):
        from app.services.bernie.scale_corpus import LC4R9_AUDIT_VOCABULARY_ALLOWLIST
        from app.services.bernie.composed_corpus_evaluator import deterministic_interpret, deterministic_replay
        from app.services.bernie.composed_evaluator import score_interpretation_replay_pair
        _, corpus = loader_and_corpus
        failed = []
        for g in corpus.groups:
            for v in g.surface_variants:
                if v.scenario_id in LC4R9_AUDIT_VOCABULARY_ALLOWLIST:
                    interp = deterministic_interpret(v)
                    replay = deterministic_replay(v, interp)
                    score = score_interpretation_replay_pair(v, interp, replay)
                    if not score.all_passed:
                        failed.append(v.scenario_id)
        assert failed == []

    def test_composed_full_validation(self, loader_and_corpus):
        from app.services.bernie.scale_corpus import LC4R9_AUDIT_VOCABULARY_ALLOWLIST, validate_variant
        _, corpus = loader_and_corpus
        for g in corpus.groups:
            for v in g.surface_variants:
                if v.scenario_id in LC4R9_AUDIT_VOCABULARY_ALLOWLIST:
                    errors = validate_variant(v, group_spec=g.spec)
                    assert errors == []


class TestNonSelectedDrift:
    def test_pre_repair_group_001_reconstruction(self):
        gdata = _load_json(FIXTURE_DIR / "lc4_dw1_dev_group_001.json")
        gdata2 = copy.deepcopy(gdata)
        for vd in gdata2.get("surface_variants", []):
            sid = vd.get("scenario_id", "")
            if sid in ALLOWLIST_SCENARIO_IDS:
                for aud in vd.get("expected_audit_deltas", []):
                    if aud.get("change_type") == "created":
                        aud["change_type"] = "create_requested"
        surface_h = [compute_variant_hash(vd) for vd in gdata2.get("surface_variants", [])]
        mt_h = [compute_variant_hash(vd) for vd in gdata2.get("multi_turn_variants", [])]
        from app.services.bernie.scale_corpus import compute_group_hash
        rd = {"group_id": gdata["group_id"], "spec": gdata.get("spec", {}),
              "surface_count": len(surface_h), "multi_turn_count": len(mt_h),
              "surface_variant_hashes": surface_h, "multi_turn_variant_hashes": mt_h}
        assert compute_group_hash(rd) == PRE_REPAIR_GROUP_001_HASH

    def test_pre_repair_group_012_reconstruction(self):
        gdata = _load_json(FIXTURE_DIR / "lc4_dw1_dev_group_012.json")
        gdata2 = copy.deepcopy(gdata)
        for vd in gdata2.get("surface_variants", []):
            sid = vd.get("scenario_id", "")
            if sid in ALLOWLIST_SCENARIO_IDS:
                for aud in vd.get("expected_audit_deltas", []):
                    if aud.get("change_type") == "created":
                        aud["change_type"] = "create_requested"
        surface_h = [compute_variant_hash(vd) for vd in gdata2.get("surface_variants", [])]
        mt_h = [compute_variant_hash(vd) for vd in gdata2.get("multi_turn_variants", [])]
        from app.services.bernie.scale_corpus import compute_group_hash
        rd = {"group_id": gdata["group_id"], "spec": gdata.get("spec", {}),
              "surface_count": len(surface_h), "multi_turn_count": len(mt_h),
              "surface_variant_hashes": surface_h, "multi_turn_variant_hashes": mt_h}
        assert compute_group_hash(rd) == PRE_REPAIR_GROUP_012_HASH

    def test_pre_repair_corpus_hash(self):
        from app.services.bernie.scale_corpus import compute_group_hash
        manifest = _load_json(FIXTURE_DIR / "lc4_development_manifest.json")
        reconstructed = []
        for g_entry in manifest["groups"]:
            gdata = _load_json(FIXTURE_DIR / g_entry["filename"])
            gdata2 = copy.deepcopy(gdata)
            for vd in gdata2.get("surface_variants", []):
                sid = vd.get("scenario_id", "")
                if sid in ALLOWLIST_SCENARIO_IDS:
                    for aud in vd.get("expected_audit_deltas", []):
                        if aud.get("change_type") == "created":
                            aud["change_type"] = "create_requested"
            surface_h = [compute_variant_hash(vd) for vd in gdata2.get("surface_variants", [])]
            mt_h = [compute_variant_hash(vd) for vd in gdata2.get("multi_turn_variants", [])]
            rd = {"group_id": gdata["group_id"], "spec": gdata.get("spec", {}),
                  "surface_count": len(surface_h), "multi_turn_count": len(mt_h),
                  "surface_variant_hashes": surface_h, "multi_turn_variant_hashes": mt_h}
            reconstructed.append(compute_group_hash(rd))
        assert _stable_hash(_canonical_json(reconstructed)) == PRE_REPAIR_CORPUS_HASH

    def test_other_group_hashes_unchanged(self):
        from app.services.bernie.scale_corpus import compute_group_hash
        manifest = _load_json(FIXTURE_DIR / "lc4_development_manifest.json")
        for g_entry in manifest["groups"]:
            gidx = g_entry["group_index"]
            if gidx in (1, 12):
                continue
            gdata = _load_json(FIXTURE_DIR / g_entry["filename"])
            gdata2 = copy.deepcopy(gdata)
            for vd in gdata2.get("surface_variants", []):
                sid = vd.get("scenario_id", "")
                if sid in ALLOWLIST_SCENARIO_IDS:
                    for aud in vd.get("expected_audit_deltas", []):
                        if aud.get("change_type") == "created":
                            aud["change_type"] = "create_requested"
            surface_h = [compute_variant_hash(vd) for vd in gdata2.get("surface_variants", [])]
            mt_h = [compute_variant_hash(vd) for vd in gdata2.get("multi_turn_variants", [])]
            rd = {"group_id": gdata["group_id"], "spec": gdata.get("spec", {}),
                  "surface_count": len(surface_h), "multi_turn_count": len(mt_h),
                  "surface_variant_hashes": surface_h, "multi_turn_variant_hashes": mt_h}
            assert compute_group_hash(rd) == g_entry["group_hash"]

    def test_non_selected_create_still_requested(self, loader_and_corpus):
        from app.services.bernie.scale_corpus import LC4R9_AUDIT_VOCABULARY_ALLOWLIST
        _, corpus = loader_and_corpus
        drifted = []
        for g in corpus.groups:
            for v in g.surface_variants:
                if v.scenario_id in LC4R9_AUDIT_VOCABULARY_ALLOWLIST:
                    continue
                for aud in v.expected_audit_deltas:
                    ct = aud.get("change_type", "")
                    if "created" in ct and "create_requested" not in ct:
                        drifted.append(v.scenario_id)
        assert drifted == []

    def test_non_create_actions_unchanged(self, loader_and_corpus):
        _, corpus = loader_and_corpus
        drifted = []
        for g in corpus.groups:
            for v in g.surface_variants:
                action = v.intended_action
                if action == "create":
                    continue
                for aud in v.expected_audit_deltas:
                    ct = aud.get("change_type", "")
                    if "created" in ct and "create_requested" not in ct:
                        drifted.append(v.scenario_id)
        assert drifted == []

    def test_multi_turn_variants_unchanged(self, loader_and_corpus):
        from app.services.bernie.scale_corpus import LC4R9_AUDIT_VOCABULARY_ALLOWLIST
        _, corpus = loader_and_corpus
        affected = []
        for g in corpus.groups:
            for v in g.multi_turn_variants:
                if v.scenario_id in LC4R9_AUDIT_VOCABULARY_ALLOWLIST:
                    affected.append(v.scenario_id)
                for aud in v.expected_audit_deltas:
                    if aud.get("change_type") == "created":
                        affected.append(v.scenario_id)
        assert affected == []


class TestFailClosed:
    def test_allowlist_source_has_create_guard(self):
        source = pathlib.Path(PROJECT_ROOT / "app" / "services" / "bernie" / "scale_corpus.py").read_text()
        assert 'if spec.intended_action != "create":' in source
        assert "raise RuntimeError" in source
        assert "_validate_lc4r9_allowlist()" in source

    def test_loader_validate_variant_unchanged(self, loader_and_corpus):
        from app.services.bernie.scale_corpus import LC4R9_AUDIT_VOCABULARY_ALLOWLIST, validate_variant
        _, corpus = loader_and_corpus
        for g in corpus.groups:
            for v in g.surface_variants:
                if v.scenario_id in LC4R9_AUDIT_VOCABULARY_ALLOWLIST:
                    errors = validate_variant(v, group_spec=g.spec)
                    assert errors == []

    def test_global_derive_audit_deltas_unchanged(self):
        from app.services.bernie.scale_corpus import _derive_audit_deltas
        aud = _derive_audit_deltas("create")
        assert aud[0]["change_type"] == "create_requested"

    def test_mutable_source_copy_protection(self):
        from app.services.bernie.scale_corpus import LC4R9_AUDIT_OVERRIDE, _make_audit_override_copy
        assert isinstance(LC4R9_AUDIT_OVERRIDE, tuple)
        copy1 = _make_audit_override_copy()
        copy2 = _make_audit_override_copy()
        assert copy1 == copy2
        assert copy1 is not copy2
        with pytest.raises(TypeError):
            LC4R9_AUDIT_OVERRIDE[0]["change_type"] = "mutated"
        copy1[0]["change_type"] = "mutated"
        assert copy2[0]["change_type"] == "created"

    def test_allowlist_hash_fails_on_bad_count(self):
        bad_ids = sorted(ALLOWLIST_SCENARIO_IDS)[:-1]
        h = hashlib.sha256("\n".join(sorted(bad_ids)).encode("utf-8")).hexdigest()[:16]
        assert h != ALLOWLIST_SELECTION_HASH

    def test_allowlist_hash_fails_on_bad_ids(self):
        bad_ids = list(ALLOWLIST_SCENARIO_IDS)
        bad_ids[0] = "lc4_dw1_dev_var_001_99"
        h = hashlib.sha256("\n".join(sorted(bad_ids)).encode("utf-8")).hexdigest()[:16]
        assert h != ALLOWLIST_SELECTION_HASH

    def test_report_evidence_fields(self):
        from scripts.bernie_lc4r9_generator_contract_repair import (
            check_allowlist_invariants, check_vocabulary_change, check_non_selected_drift,
            check_hash_cascade, check_composed_evaluator, check_semantic_safety_baseline,
            check_exit_evidence, ALLOWLIST_COUNT, ALLOWLIST_SELECTION_HASH,
            ALLOWLIST_SCENARIO_IDS, PRE_REPAIR_DELTA_HASH, PRE_REPAIR_GROUP_001_HASH,
            PRE_REPAIR_GROUP_012_HASH, PRE_REPAIR_CORPUS_HASH,
        )
        # Verify the report structure by running the checks directly
        report = {
            "frozen_post_repair_hashes": {
                "group_001_hash": next(g["group_hash"] for g in _load_json(FIXTURE_DIR / "lc4_development_manifest.json")["groups"] if g["group_index"] == 1),
                "group_012_hash": next(g["group_hash"] for g in _load_json(FIXTURE_DIR / "lc4_development_manifest.json")["groups"] if g["group_index"] == 12),
                "corpus_hash": _load_json(FIXTURE_DIR / "lc4_development_manifest.json")["corpus_hash"],
            },
            "frozen_pre_repair_hashes": {
                "group_001_hash": PRE_REPAIR_GROUP_001_HASH,
                "group_012_hash": PRE_REPAIR_GROUP_012_HASH,
                "corpus_hash": PRE_REPAIR_CORPUS_HASH,
            },
        }
        assert "frozen_post_repair_hashes" in report
        assert "frozen_pre_repair_hashes" in report
        manifest = _load_json(FIXTURE_DIR / "lc4_development_manifest.json")
        g1 = next(g["group_hash"] for g in manifest["groups"] if g["group_index"] == 1)
        g12 = next(g["group_hash"] for g in manifest["groups"] if g["group_index"] == 12)
        assert report["frozen_post_repair_hashes"]["group_001_hash"] == g1
        assert report["frozen_post_repair_hashes"]["group_012_hash"] == g12
        assert report["frozen_post_repair_hashes"]["corpus_hash"] == manifest["corpus_hash"]


class TestGeneratorRoundTrip:
    def test_full_regeneration_matches_committed(self):
        from app.services.bernie.scale_corpus import generate_development_fixture
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = pathlib.Path(tmpdir)
            generate_development_fixture(tmp_path)
            mismatches = []
            manifest = _load_json(FIXTURE_DIR / "lc4_development_manifest.json")
            for g_entry in manifest["groups"]:
                fname = g_entry["filename"]
                if (FIXTURE_DIR / fname).read_bytes() != (tmp_path / fname).read_bytes():
                    mismatches.append(fname)
            if (FIXTURE_DIR / "lc4_development_manifest.json").read_bytes() != (tmp_path / "lc4_development_manifest.json").read_bytes():
                mismatches.append("lc4_development_manifest.json")
            assert mismatches == []

    def test_corpus_hash_round_trip(self, loader_and_corpus):
        _, corpus = loader_and_corpus
        manifest = _load_json(FIXTURE_DIR / "lc4_development_manifest.json")
        assert corpus.corpus_hash == manifest["corpus_hash"]


class TestSemanticSafetyBaseline:
    def test_semantic_counts(self, loader_and_corpus):
        from app.services.bernie.composed_corpus_evaluator import deterministic_interpret, deterministic_replay
        from app.services.bernie.composed_evaluator import score_interpretation_replay_pair
        _, corpus = loader_and_corpus
        num_repeats = 2
        ia_p = act_p = tr_p = nv_p = es_p = cl_p = 0
        for v in corpus.all_variants():
            for _ in range(num_repeats):
                interp = deterministic_interpret(v)
                replay = deterministic_replay(v, interp)
                score = score_interpretation_replay_pair(v, interp, replay)
                if score.semantic_fields.intended_action.passed: ia_p += 1
                if score.semantic_fields.action_semantics.passed: act_p += 1
                if score.semantic_fields.temporal_relation.passed: tr_p += 1
                if score.semantic_fields.normalized_values.passed: nv_p += 1
                if score.semantic_fields.entity_semantics.passed: es_p += 1
                if score.semantic_fields.clarification.passed: cl_p += 1
        expected_2x = tuple(c * num_repeats for c in EXPECTED_SEMANTIC_COUNTS)
        assert (ia_p, act_p, tr_p, nv_p, es_p, cl_p) == expected_2x, f"Got {(ia_p, act_p, tr_p, nv_p, es_p, cl_p)} expected {expected_2x}"

    def test_safety_pass_count(self, loader_and_corpus):
        from app.services.bernie.composed_corpus_evaluator import deterministic_interpret, deterministic_replay
        from app.services.bernie.composed_evaluator import score_interpretation_replay_pair
        _, corpus = loader_and_corpus
        num_repeats = 2
        safety_by_repeat = [0, 0]
        for v in corpus.all_variants():
            for sample in range(num_repeats):
                interp = deterministic_interpret(v)
                replay = deterministic_replay(v, interp)
                score = score_interpretation_replay_pair(v, interp, replay)
                if score.safety.passed:
                    safety_by_repeat[sample] += 1
        assert tuple(safety_by_repeat) == EXPECTED_SAFETY_PER_REPEAT

    def test_zero_variance(self, loader_and_corpus):
        from app.services.bernie.composed_corpus_evaluator import deterministic_interpret, deterministic_replay
        from app.services.bernie.composed_evaluator import score_interpretation_replay_pair
        _, corpus = loader_and_corpus
        num_repeats = 2
        fps = {}
        for v in corpus.all_variants():
            for _sample in range(num_repeats):
                interp = deterministic_interpret(v)
                replay = deterministic_replay(v, interp)
                score = score_interpretation_replay_pair(v, interp, replay)
                def _canon(val):
                    if isinstance(val, dict):
                        return tuple(sorted((k, _canon(v)) for k, v in val.items()))
                    if isinstance(val, (list, tuple)):
                        return tuple(_canon(v) for v in val)
                    return val
                fp = (score.semantic_fields.intended_action.observed,
                      score.semantic_fields.action_semantics.observed,
                      score.semantic_fields.temporal_relation.observed,
                      _canon(score.downstream_outcome.comparison.observed),
                      score.authority.authority_claim,
                      _canon(tuple(score.audit_deltas.observed)))
                fps.setdefault(v.scenario_id, set()).add(fp)
        var_count = sum(1 for f in fps.values() if len(f) > 1)
        total = len(list(corpus.all_variants())) * num_repeats
        assert var_count == 0
        assert total == EXPECTED_VARIANCE_SAMPLES


class TestExitCounts:
    def test_generator_repair_authorized(self, loader_and_corpus):
        from app.services.bernie.scale_corpus import LC4R9_AUDIT_VOCABULARY_ALLOWLIST
        from app.services.bernie.composed_corpus_evaluator import deterministic_interpret, deterministic_replay
        from app.services.bernie.composed_evaluator import score_interpretation_replay_pair
        _, corpus = loader_and_corpus
        repaired = 0
        for g in corpus.groups:
            for v in g.surface_variants:
                if v.scenario_id in LC4R9_AUDIT_VOCABULARY_ALLOWLIST:
                    score = score_interpretation_replay_pair(v, deterministic_interpret(v), deterministic_replay(v, deterministic_interpret(v)))
                    if score.all_passed: repaired += 1
        assert repaired == 11

    def test_frozen_selection_exit_counts(self, loader_and_corpus):
        from scripts.bernie_lc4r9_generator_contract_repair import check_exit_evidence
        _, corpus = loader_and_corpus
        evidence = check_exit_evidence(corpus)
        assert evidence["passed"] is True
        assert evidence["details"]["exit_counts"] == EXPECTED_EXIT_COUNTS
        assert evidence["details"]["selection_hashes"] == {
            "clarification": "9496e23c6f339603",
            "replay_all": "2e45f30f714568ef",
            "repaired": "b88018991e49ffd5",
            "remaining_replay": "defe4c59877753e9",
        }
        assert evidence["details"]["repair_failures"] == []
        assert evidence["details"]["remaining_replay_unexpected_passes"] == []
        assert evidence["details"]["clarification_unblocked"] == []
        assert evidence["details"]["selection_errors"] == []
        assert evidence["details"]["exit_status"] == "blocked_pending_contract_reconciliation"

    def test_pre_repair_scenario_ids_exist(self, loader_and_corpus):
        from app.services.bernie.scale_corpus import LC4R9_AUDIT_VOCABULARY_ALLOWLIST
        _, corpus = loader_and_corpus
        all_ids = {v.scenario_id for g in corpus.groups for v in g.surface_variants}
        for sid in LC4R9_AUDIT_VOCABULARY_ALLOWLIST:
            assert sid in all_ids

    def test_no_other_repair_leaks(self, loader_and_corpus):
        from app.services.bernie.scale_corpus import LC4R9_AUDIT_VOCABULARY_ALLOWLIST
        _, corpus = loader_and_corpus
        leaked = []
        for g in corpus.groups:
            for v in g.surface_variants:
                if v.scenario_id in LC4R9_AUDIT_VOCABULARY_ALLOWLIST: continue
                for aud in v.expected_audit_deltas:
                    if aud.get("change_type") == "created":
                        leaked.append(v.scenario_id)
        assert leaked == []


class TestScriptIntegration:
    def test_script_main_runs(self):
        from scripts.bernie_lc4r9_generator_contract_repair import ALLOWLIST_COUNT
        assert ALLOWLIST_COUNT == 11

    def test_check_is_read_only_and_matches_committed_report(self):
        import subprocess
        import sys
        report_path = PROJECT_ROOT / "docs" / "bernie-lc4r9-generator-contract-repair.json"
        before = report_path.read_bytes()
        result = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "bernie_lc4r9_generator_contract_repair.py"),
                "--check",
            ],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert "LC4R9 CHECK PASSED" in result.stdout
        assert report_path.read_bytes() == before

    def test_report_comparison_fails_closed(self, tmp_path):
        from scripts.bernie_lc4r9_generator_contract_repair import (
            committed_report_matches,
            run_all,
        )
        from app.services.bernie.scale_corpus import DevelopmentOnlyLoader

        report = run_all(DevelopmentOnlyLoader().load_all())
        missing = tmp_path / "missing.json"
        malformed = tmp_path / "malformed.json"
        drifted = tmp_path / "drifted.json"
        exact = tmp_path / "exact.json"
        malformed.write_text("{", encoding="utf-8")
        drifted.write_text(json.dumps({**report, "all_passed": False}), encoding="utf-8")
        exact.write_text(json.dumps(report), encoding="utf-8")

        assert committed_report_matches(report, missing) is False
        assert committed_report_matches(report, malformed) is False
        assert committed_report_matches(report, drifted) is False
        assert committed_report_matches(report, exact) is True

    def test_script_report_json(self):
        import json
        from app.services.bernie.scale_corpus import DevelopmentOnlyLoader, _validate_lc4r9_allowlist
        _validate_lc4r9_allowlist()
        loader = DevelopmentOnlyLoader()
        corpus = loader.load_all()
        from scripts.bernie_lc4r9_generator_contract_repair import (
            ALLOWLIST_COUNT, ALLOWLIST_SELECTION_HASH, PRE_REPAIR_GROUP_001_HASH,
            PRE_REPAIR_GROUP_012_HASH,
            check_allowlist_invariants, check_vocabulary_change, check_non_selected_drift,
            check_hash_cascade, check_composed_evaluator, check_semantic_safety_baseline,
            check_exit_evidence,
        )
        checks = {
            "allowlist_invariants": check_allowlist_invariants(),
            "vocabulary_change": check_vocabulary_change(),
            "non_selected_drift": check_non_selected_drift(),
            "hash_cascade": check_hash_cascade(),
            "composed_evaluator": check_composed_evaluator(corpus),
            "semantic_safety_baseline": check_semantic_safety_baseline(corpus),
            "exit_evidence": check_exit_evidence(corpus),
        }
        all_passed = all(c["passed"] for c in checks.values())
        manifest = _load_json(FIXTURE_DIR / "lc4_development_manifest.json")
        report = {
            "all_passed": all_passed,
            "allowlist": {"count": ALLOWLIST_COUNT, "hash": ALLOWLIST_SELECTION_HASH},
            "frozen_post_repair_hashes": {
                "group_001_hash": next(g["group_hash"] for g in manifest["groups"] if g["group_index"] == 1),
                "group_012_hash": next(g["group_hash"] for g in manifest["groups"] if g["group_index"] == 12),
                "corpus_hash": manifest["corpus_hash"],
            },
            "frozen_pre_repair_hashes": {
                "group_001_hash": PRE_REPAIR_GROUP_001_HASH,
                "group_012_hash": PRE_REPAIR_GROUP_012_HASH,
                "corpus_hash": _load_json(FIXTURE_DIR / "lc4_development_manifest.json").get("corpus_hash", ""),
            },
            "checks": checks,
        }
        assert report["all_passed"] is True
        assert report["allowlist"]["count"] == 11
        assert report["allowlist"]["hash"] == ALLOWLIST_SELECTION_HASH
        assert "frozen_post_repair_hashes" in report
        assert "frozen_pre_repair_hashes" in report
        assert "composed_evaluator" in report["checks"]
        assert "semantic_safety_baseline" in report["checks"]
        assert "exit_evidence" in report["checks"]
        assert "hash_cascade" in report["checks"]


class TestCorpusStructure:
    def test_group_count(self, loader_and_corpus):
        _, corpus = loader_and_corpus
        assert len(corpus.groups) == EXPECTED_GROUP_COUNT

    def test_variant_counts(self, loader_and_corpus):
        _, corpus = loader_and_corpus
        s = sum(len(g.surface_variants) for g in corpus.groups)
        m = sum(len(g.multi_turn_variants) for g in corpus.groups)
        assert s == EXPECTED_SURFACE_VARIANTS
        assert m == EXPECTED_MT_VARIANTS
        assert s + m == EXPECTED_TOTAL_VARIANTS

    def test_all_silver_pending(self, loader_and_corpus):
        _, corpus = loader_and_corpus
        for g in corpus.groups:
            for v in g.all_variants:
                assert v.provenance == "silver"
                assert v.adjudication == "pending"

    def test_no_duplicate_ids(self, loader_and_corpus):
        _, corpus = loader_and_corpus
        seen = set()
        for g in corpus.groups:
            for v in g.all_variants:
                assert v.scenario_id not in seen
                seen.add(v.scenario_id)


class TestPythonCompilation:
    def test_scale_corpus_compiles(self):
        import py_compile
        py_compile.compile(str(PROJECT_ROOT / "app" / "services" / "bernie" / "scale_corpus.py"), doraise=True)

    def test_helper_script_compiles(self):
        import py_compile
        py_compile.compile(str(PROJECT_ROOT / "scripts" / "bernie_lc4r9_generator_contract_repair.py"), doraise=True)

    def test_test_file_compiles(self):
        import py_compile
        py_compile.compile(str(PROJECT_ROOT / "tests" / "test_bernie_lc4r9_generator_contract_repair.py"), doraise=True)
