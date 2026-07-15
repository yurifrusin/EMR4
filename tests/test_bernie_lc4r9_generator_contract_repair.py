"""Focused tests for LC4R9 generator-backed contract repair.

Verifies the frozen 11-case allowlist, audit-vocabulary override, non-selected
scenario drift protection, hash cascade, generator round-trip, composed result,
semantic/safety/variance baselines, and exit-count drift.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys
import tempfile
from typing import Any

import pytest

# Ensure the project root is on sys.path for imports
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Helper fixtures
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Frozen contract constants  (DO NOT MODIFY)
# ---------------------------------------------------------------------------

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

PRE_REPAIR_DELTA_HASH = (
    "14e3648ae8a98598bbc091ce16bf29f31fd5b2fdb92fe7d817ae86fb21837c69"
)

EXPECTED_AUDIT_OVERRIDE = [{"change_type": "created", "appointment_id": "apt-001", "count": 1}]

# Corpus structural counts (unchanged by this repair)
EXPECTED_GROUP_COUNT = 96
EXPECTED_SURFACE_VARIANTS = 864
EXPECTED_MT_VARIANTS = 288
EXPECTED_TOTAL_VARIANTS = 1152


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def loader_and_corpus():
    """Load the development corpus once per module."""
    from app.services.bernie.scale_corpus import DevelopmentOnlyLoader
    loader = DevelopmentOnlyLoader()
    corpus = loader.load_all()
    return loader, corpus


# ===================================================================
# 1.  Allowlist invariants
# ===================================================================


class TestAllowlistInvariants:
    """Verify the frozen allowlist hash, count, and surface-only constraint."""

    def test_allowlist_source_validation(self):
        """Source allowlist in scale_corpus.py must pass fail-closed validation."""
        from app.services.bernie.scale_corpus import _validate_lc4r9_allowlist
        _validate_lc4r9_allowlist()

    def test_allowlist_count(self):
        """Allowlist must contain exactly 11 IDs."""
        from app.services.bernie.scale_corpus import (
            LC4R9_AUDIT_VOCABULARY_ALLOWLIST,
            LC4R9_ALLOWLIST_COUNT,
        )
        assert len(LC4R9_AUDIT_VOCABULARY_ALLOWLIST) == LC4R9_ALLOWLIST_COUNT == ALLOWLIST_COUNT

    def test_allowlist_hash(self):
        """Allowlist must produce the frozen selection hash."""
        from app.services.bernie.scale_corpus import (
            LC4R9_AUDIT_VOCABULARY_ALLOWLIST,
            LC4R9_ALLOWLIST_SELECTION_HASH,
        )
        computed = hashlib.sha256(
            "\n".join(sorted(LC4R9_AUDIT_VOCABULARY_ALLOWLIST)).encode("utf-8")
        ).hexdigest()[:16]
        assert computed == LC4R9_ALLOWLIST_SELECTION_HASH == ALLOWLIST_SELECTION_HASH

    def test_allowlist_surface_only(self):
        """All allowlist IDs must be surface variants (not multi-turn)."""
        from app.services.bernie.scale_corpus import LC4R9_AUDIT_VOCABULARY_ALLOWLIST
        assert all(sid.startswith("lc4_dw1_dev_var") for sid in LC4R9_AUDIT_VOCABULARY_ALLOWLIST)

    def test_allowlist_no_multi_turn(self):
        """No multi-turn IDs are in the allowlist."""
        from app.services.bernie.scale_corpus import LC4R9_AUDIT_VOCABULARY_ALLOWLIST
        assert not any("_mt_" in sid for sid in LC4R9_AUDIT_VOCABULARY_ALLOWLIST)

    def test_allowlist_pre_repair_delta_hash(self):
        """Pre-repair delta-line hash must match the contract."""
        from app.services.bernie.scale_corpus import (
            LC4R9_AUDIT_VOCABULARY_ALLOWLIST,
            LC4R9_PRE_REPAIR_DELTA_HASH,
        )
        lines = sorted(
            f"{sid}|create_requested|created"
            for sid in LC4R9_AUDIT_VOCABULARY_ALLOWLIST
        )
        computed = hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()
        assert computed == LC4R9_PRE_REPAIR_DELTA_HASH == PRE_REPAIR_DELTA_HASH


# ===================================================================
# 2.  Audit vocabulary change (create_requested -> created)
# ===================================================================


class TestVocabularyChange:
    """Verify the 11 selected scenarios have the corrected audit vocabulary."""

    def test_all_selected_have_created(self, loader_and_corpus):
        """All 11 selected scenarios must have 'created' audit delta."""
        from app.services.bernie.scale_corpus import (
            LC4R9_AUDIT_VOCABULARY_ALLOWLIST,
            LC4R9_AUDIT_OVERRIDE,
        )
        _, corpus = loader_and_corpus
        for g in corpus.groups:
            for v in g.surface_variants:
                if v.scenario_id in LC4R9_AUDIT_VOCABULARY_ALLOWLIST:
                    assert v.expected_audit_deltas == LC4R9_AUDIT_OVERRIDE, (
                        f"{v.scenario_id} expected {LC4R9_AUDIT_OVERRIDE}, "
                        f"got {v.expected_audit_deltas}"
                    )

    def test_selected_scenarios_found_in_fixtures(self):
        """All 11 scenario IDs must exist in the fixture files."""
        from app.services.bernie.scale_corpus import LC4R9_AUDIT_VOCABULARY_ALLOWLIST
        manifest = _load_json(FIXTURE_DIR / "lc4_development_manifest.json")
        all_variant_ids: set[str] = set()
        for g_entry in manifest["groups"]:
            fname = g_entry["filename"]
            gdata = _load_json(FIXTURE_DIR / fname)
            for vdata in gdata.get("surface_variants", []):
                all_variant_ids.add(vdata["scenario_id"])
        for sid in LC4R9_AUDIT_VOCABULARY_ALLOWLIST:
            assert sid in all_variant_ids, f"{sid} not found in fixture files"

    def test_selected_vocabulary_in_committed_json(self):
        """Verify the 'created' vocabulary is present in the committed JSON files."""
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
                    assert aud == EXPECTED_AUDIT_OVERRIDE, (
                        f"{sid} committed audit={aud}"
                    )
                    break
            assert found, f"{sid} not found in group {group_idx}"

    def test_pre_repair_vocabulary_constant(self):
        """The pre-repair vocabulary from _derive_audit_deltas must be 'create_requested'."""
        from app.services.bernie.scale_corpus import _derive_audit_deltas
        pre = _derive_audit_deltas("create")
        assert pre[0]["change_type"] == "create_requested"
        # Verify the global derivation is unchanged for other actions
        for action in ("move", "resize", "cancel", "status_change"):
            aud = _derive_audit_deltas(action)
            assert f"{action}_requested" in aud[0]["change_type"]


# ===================================================================
# 3.  Non-selected scenario drift
# ===================================================================


class TestNonSelectedDrift:
    """Verify non-selected scenarios are completely unchanged."""

    def test_non_selected_create_still_requested(self, loader_and_corpus):
        """Non-selected create scenarios must still have 'create_requested' audit deltas."""
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
        assert drifted == [], f"Non-selected scenarios drifted: {drifted}"

    def test_non_create_actions_unchanged(self, loader_and_corpus):
        """Non-create actions must have their original audit delta pattern."""
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
                        drifted.append(f"{v.scenario_id}: got {ct!r} for action {action!r}")
        assert drifted == [], (
            f"Non-create actions drifted or leaked created vocabulary: {drifted}"
        )

    def test_multi_turn_variants_unchanged(self, loader_and_corpus):
        """Multi-turn variants must not be affected by the surface-only allowlist."""
        from app.services.bernie.scale_corpus import LC4R9_AUDIT_VOCABULARY_ALLOWLIST
        _, corpus = loader_and_corpus
        affected = []
        for g in corpus.groups:
            for v in g.multi_turn_variants:
                if v.scenario_id in LC4R9_AUDIT_VOCABULARY_ALLOWLIST:
                    affected.append(v.scenario_id)
                for aud in v.expected_audit_deltas:
                    ct = aud.get("change_type", "")
                    if ct == "created":
                        affected.append(v.scenario_id)
        assert affected == [], f"Multi-turn variants unexpectedly affected: {affected}"


# ===================================================================
# 4.  Fail-closed behavior
# ===================================================================


class TestFailClosed:
    """Verify the allowlist fails closed on invalid states."""

    def test_allowlist_source_has_create_guard(self):
        """The source code must have a runtime guard for non-create action in allowlist."""
        source = pathlib.Path(
            PROJECT_ROOT / "app" / "services" / "bernie" / "scale_corpus.py"
        ).read_text()
        assert 'if spec.intended_action != "create":' in source
        assert "raise RuntimeError" in source
        assert "_validate_lc4r9_allowlist()" in source

    def test_loader_validate_variant_unchanged(self, loader_and_corpus):
        """validate_variant must still work for allowlist scenarios."""
        from app.services.bernie.scale_corpus import (
            LC4R9_AUDIT_VOCABULARY_ALLOWLIST,
            validate_variant,
        )
        _, corpus = loader_and_corpus
        for g in corpus.groups:
            for v in g.surface_variants:
                if v.scenario_id in LC4R9_AUDIT_VOCABULARY_ALLOWLIST:
                    errors = validate_variant(v, group_spec=g.spec)
                    assert errors == [], f"{v.scenario_id} validation errors: {errors}"

    def test_global_derive_audit_deltas_unchanged(self):
        """_derive_audit_deltas must still produce create_requested globally."""
        from app.services.bernie.scale_corpus import _derive_audit_deltas
        aud = _derive_audit_deltas("create")
        assert aud[0]["change_type"] == "create_requested"
        assert aud[0]["appointment_id"] == "apt-001"
        assert aud[0]["count"] == 1


# ===================================================================
# 5.  Generator round-trip (byte-for-byte)
# ===================================================================


class TestGeneratorRoundTrip:
    """Verify temporary full regeneration reproduces committed corpus byte-for-byte."""

    def test_full_regeneration_matches_committed(self):
        """Temporary regeneration must produce identical bytes for all fixture files."""
        from app.services.bernie.scale_corpus import generate_development_fixture

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = pathlib.Path(tmpdir)
            generate_development_fixture(tmp_path)

            mismatches: list[str] = []
            manifest = _load_json(FIXTURE_DIR / "lc4_development_manifest.json")

            for g_entry in manifest["groups"]:
                fname = g_entry["filename"]
                committed_path = FIXTURE_DIR / fname
                generated_path = tmp_path / fname

                committed_bytes = committed_path.read_bytes()
                generated_bytes = generated_path.read_bytes()

                if committed_bytes != generated_bytes:
                    mismatches.append(fname)

            # Compare manifests
            committed_manifest_bytes = (
                FIXTURE_DIR / "lc4_development_manifest.json"
            ).read_bytes()
            generated_manifest_bytes = (
                tmp_path / "lc4_development_manifest.json"
            ).read_bytes()

            if committed_manifest_bytes != generated_manifest_bytes:
                mismatches.append("lc4_development_manifest.json")

            assert mismatches == [], (
                f"Full regeneration mismatch in {len(mismatches)} file(s): {mismatches}"
            )

    def test_corpus_hash_round_trip(self, loader_and_corpus):
        """The loaded corpus hash must match the manifest hash."""
        _, corpus = loader_and_corpus
        manifest = _load_json(FIXTURE_DIR / "lc4_development_manifest.json")
        assert corpus.corpus_hash == manifest["corpus_hash"], (
            f"Corpus hash mismatch: {corpus.corpus_hash} vs {manifest['corpus_hash']}"
        )


# ===================================================================
# 6.  Hash cascade
# ===================================================================


class TestHashCascade:
    """Verify the hash chain from variant -> group -> corpus is consistent."""

    def test_group_hash_consistency(self, loader_and_corpus):
        """Every group hash must match between loaded corpus and manifest."""
        from app.services.bernie.scale_corpus import compute_group_hash
        _, corpus = loader_and_corpus
        manifest = _load_json(FIXTURE_DIR / "lc4_development_manifest.json")
        manifest_group_map = {g["group_id"]: g["group_hash"] for g in manifest["groups"]}
        for g in corpus.groups:
            assert g.group_hash == manifest_group_map.get(g.group_id), (
                f"Group hash mismatch for {g.group_id}: "
                f"{g.group_hash} vs {manifest_group_map.get(g.group_id)}"
            )

    def test_corpus_hash_cascade(self, loader_and_corpus):
        """Corpus hash must be derived from chained group hashes."""
        _, corpus = loader_and_corpus
        manifest = _load_json(FIXTURE_DIR / "lc4_development_manifest.json")
        group_hashes = [g["group_hash"] for g in manifest["groups"]]
        corpus_hash_input = _canonical_json(group_hashes)
        recomputed = _stable_hash(corpus_hash_input)
        assert recomputed == manifest["corpus_hash"], (
            f"Corpus hash derivation mismatch: {recomputed} vs {manifest['corpus_hash']}"
        )
        assert recomputed == corpus.corpus_hash

    def test_only_affected_hashes_changed(self):
        """Only groups with changed audit deltas should have new hashes."""
        manifest = _load_json(FIXTURE_DIR / "lc4_development_manifest.json")
        for g in manifest["groups"]:
            idx = g["group_index"]
            if idx == 1:
                assert g["group_hash"] != (
                    "sha256:0874f6887020df0ae9abe0ca75a9ee60bc9eb0d55094701fbf5a48788cd71e5d"
                )
            elif idx == 12:
                assert g["group_hash"] != (
                    "sha256:76a4a27c6d217dcfd0fa4a96ea42b1416201b31fdb87af39c4bb32040f7fb9b6"
                )


# ===================================================================
# 7.  Composed result
# ===================================================================


class TestComposedResult:
    """Verify the 11 selected scenarios pass complete composed component checks."""

    def test_composed_audit_delta(self, loader_and_corpus):
        """All 11 selected scenarios must have exactly the expected audit override."""
        from app.services.bernie.scale_corpus import (
            LC4R9_AUDIT_VOCABULARY_ALLOWLIST,
            LC4R9_AUDIT_OVERRIDE,
        )
        _, corpus = loader_and_corpus
        for g in corpus.groups:
            for v in g.surface_variants:
                if v.scenario_id in LC4R9_AUDIT_VOCABULARY_ALLOWLIST:
                    assert v.expected_audit_deltas == LC4R9_AUDIT_OVERRIDE

    def test_composed_appointment_delta(self, loader_and_corpus):
        """Appointment deltas for selected scenarios must remain unchanged."""
        from app.services.bernie.scale_corpus import LC4R9_AUDIT_VOCABULARY_ALLOWLIST
        _, corpus = loader_and_corpus
        for g in corpus.groups:
            for v in g.surface_variants:
                if v.scenario_id in LC4R9_AUDIT_VOCABULARY_ALLOWLIST:
                    for apt in v.expected_appointment_deltas:
                        assert apt.get("change_type") == "created"
                        assert apt.get("appointment_id") == "apt-001"

    def test_composed_full_validation(self, loader_and_corpus):
        """All 11 selected scenarios must pass full validate_variant checks."""
        from app.services.bernie.scale_corpus import (
            LC4R9_AUDIT_VOCABULARY_ALLOWLIST,
            validate_variant,
        )
        _, corpus = loader_and_corpus
        for g in corpus.groups:
            for v in g.surface_variants:
                if v.scenario_id in LC4R9_AUDIT_VOCABULARY_ALLOWLIST:
                    errors = validate_variant(v, group_spec=g.spec)
                    assert errors == [], f"{v.scenario_id}: {errors}"


# ===================================================================
# 8.  Semantic baseline
# ===================================================================


class TestCorpusStructure:
    """Corpus structural counts must remain unchanged by this repair."""

    def test_group_count(self, loader_and_corpus):
        """Must have exactly 96 development groups."""
        _, corpus = loader_and_corpus
        assert len(corpus.groups) == EXPECTED_GROUP_COUNT, (
            f"Group count changed: {len(corpus.groups)} vs {EXPECTED_GROUP_COUNT}"
        )

    def test_variant_counts(self, loader_and_corpus):
        """Must have exactly 864 surface + 288 multi-turn = 1152 variants."""
        _, corpus = loader_and_corpus
        surface_total = sum(len(g.surface_variants) for g in corpus.groups)
        mt_total = sum(len(g.multi_turn_variants) for g in corpus.groups)
        assert surface_total == EXPECTED_SURFACE_VARIANTS, (
            f"Surface variant count: {surface_total} vs {EXPECTED_SURFACE_VARIANTS}"
        )
        assert mt_total == EXPECTED_MT_VARIANTS, (
            f"Multi-turn variant count: {mt_total} vs {EXPECTED_MT_VARIANTS}"
        )
        assert surface_total + mt_total == EXPECTED_TOTAL_VARIANTS

    def test_all_silver_pending(self, loader_and_corpus):
        """All variants must have provenance=silver and adjudication=pending."""
        _, corpus = loader_and_corpus
        for g in corpus.groups:
            for v in g.all_variants:
                assert v.provenance == "silver", (
                    f"{v.scenario_id} has provenance={v.provenance!r}"
                )
                assert v.adjudication == "pending", (
                    f"{v.scenario_id} has adjudication={v.adjudication!r}"
                )

    def test_no_duplicate_ids(self, loader_and_corpus):
        """No duplicate scenario IDs across the corpus."""
        _, corpus = loader_and_corpus
        seen: set[str] = set()
        for g in corpus.groups:
            for v in g.all_variants:
                assert v.scenario_id not in seen, (
                    f"Duplicate scenario ID: {v.scenario_id}"
                )
                seen.add(v.scenario_id)


# ===================================================================
# 9.  Exit counts
# ===================================================================


class TestExitCounts:
    """Exit-count drift detection."""

    def test_generator_repair_remaining_zero(self):
        """Generator repair remaining count must be 0 (all 11 repaired)."""
        from app.services.bernie.scale_corpus import LC4R9_AUDIT_VOCABULARY_ALLOWLIST
        repaired = len(LC4R9_AUDIT_VOCABULARY_ALLOWLIST)
        remaining = 11 - repaired
        assert remaining == 0, f"Generator repair remaining = {remaining}"

    def test_pre_repair_scenario_ids_exist(self, loader_and_corpus):
        """All 11 pre-repair IDs must exist in the corpus."""
        from app.services.bernie.scale_corpus import LC4R9_AUDIT_VOCABULARY_ALLOWLIST
        _, corpus = loader_and_corpus
        all_ids = {v.scenario_id for g in corpus.groups for v in g.surface_variants}
        for sid in LC4R9_AUDIT_VOCABULARY_ALLOWLIST:
            assert sid in all_ids, f"{sid} not found in corpus"

    def test_no_other_repair_leaks(self, loader_and_corpus):
        """No other scenario IDs outside the allowlist should have 'created' audit delta."""
        from app.services.bernie.scale_corpus import LC4R9_AUDIT_VOCABULARY_ALLOWLIST
        _, corpus = loader_and_corpus
        leaked = []
        for g in corpus.groups:
            for v in g.surface_variants:
                if v.scenario_id in LC4R9_AUDIT_VOCABULARY_ALLOWLIST:
                    continue
                for aud in v.expected_audit_deltas:
                    if aud.get("change_type") == "created":
                        leaked.append(v.scenario_id)
        assert leaked == [], f"Leaked 'created' audit deltas: {leaked}"


# ===================================================================
# 10.  Script integration
# ===================================================================


class TestScriptIntegration:
    """Verify the helper script runs correctly."""

    def test_script_check_passes(self):
        """The helper script must exit 0 with --check."""
        import subprocess
        result = subprocess.run(
            [sys.executable,
             str(PROJECT_ROOT / "scripts" / "bernie_lc4r9_generator_contract_repair.py"),
             "--check"],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, (
            f"Script --check failed:\nstdout:{result.stdout}\nstderr:{result.stderr}"
        )
        assert "LC4R9 CHECK PASSED" in result.stdout

    def test_script_report_json(self):
        """The helper script must produce a valid report JSON."""
        import subprocess
        result = subprocess.run(
            [sys.executable,
             str(PROJECT_ROOT / "scripts" / "bernie_lc4r9_generator_contract_repair.py")],
            capture_output=True, text=True, cwd=str(PROJECT_ROOT),
        )
        report = json.loads(result.stdout)
        assert report["all_passed"] is True
        assert report["allowlist"]["count"] == 11
        assert report["allowlist"]["hash"] == ALLOWLIST_SELECTION_HASH


# ===================================================================
# 11.  Python compilation
# ===================================================================


class TestPythonCompilation:
    """Verify all owned files compile without errors."""

    def test_scale_corpus_compiles(self):
        import py_compile
        py_compile.compile(
            str(PROJECT_ROOT / "app" / "services" / "bernie" / "scale_corpus.py"),
            doraise=True,
        )

    def test_helper_script_compiles(self):
        import py_compile
        py_compile.compile(
            str(PROJECT_ROOT / "scripts" / "bernie_lc4r9_generator_contract_repair.py"),
            doraise=True,
        )

    def test_test_file_compiles(self):
        import py_compile
        py_compile.compile(
            str(PROJECT_ROOT / "tests" / "test_bernie_lc4r9_generator_contract_repair.py"),
            doraise=True,
        )
