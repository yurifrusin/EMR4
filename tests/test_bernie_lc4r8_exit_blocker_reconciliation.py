"""Focused tests for LC4R8 exit-blocker reconciliation.

Reproduces every frozen count and hash from contract constants, validates
redacted record schemas, exercises the build_from_variants entry point with
original/shuffled/reversed variant orders, and fails closed on drift.
"""

from __future__ import annotations

import copy
import hashlib
import json
import pathlib
import random
import sys

import pytest

# Ensure the project root is on sys.path for imports
PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------------
# Helper fixtures
# ---------------------------------------------------------------------------

HERE = pathlib.Path(__file__).resolve().parent
DOCS_DIR = PROJECT_ROOT / "docs"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"


def _canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _selection_hash(scenario_ids: list[str]) -> str:
    return hashlib.sha256(
        "\n".join(sorted(scenario_ids)).encode("utf-8")
    ).hexdigest()[:16]


def _records_hash(lines: list[str]) -> str:
    return hashlib.sha256(
        "\n".join(sorted(lines)).encode("utf-8")
    ).hexdigest()[:16]


def _stable_hash(content: str) -> str:
    return "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Contract constants  (must match the frozen contract exactly)
# ---------------------------------------------------------------------------

EXPECTED_CLARIFICATION_SELECTION_HASH = "9496e23c6f339603"
EXPECTED_CLARIFICATION_SELECTION_COUNT = 53

EXPECTED_CLARIFICATION_CLASSES: dict[str, dict] = {
    "normalization_contract_blocked": {"count": 3, "hash": "db484a50adc0b601"},
    "entity_and_normalization_contract_blocked": {"count": 6, "hash": "ff20612b3c9e276e"},
    "temporal_and_normalization_contract_blocked": {"count": 20, "hash": "910950860133d8b9"},
    "temporal_entity_and_normalization_contract_blocked": {"count": 24, "hash": "7cfaa6e4ddefc172"},
    "isolated_clarification_policy_choice": {"count": 0, "hash": "e3b0c44298fc1c14"},
}

EXPECTED_CLARIFICATION_ACTION_DISTRIBUTION = {
    "create": 13, "move": 13, "resize": 14, "cancel": 13,
}

EXPECTED_CLARIFICATION_ACTION_HASHES = {
    "create": "1839c8c567e44922",
    "move": "ec7e009f37f0834a",
    "resize": "e49785ce6f8922e5",
    "cancel": "830386f883de7fd0",
}

CLARIFICATION_RECORD_HASH = "baf4c66b1a7ee139"

CLARIFICATION_REQUIRED_KEYS = {
    "scenario_id", "blocker_class", "decision_readiness", "provenance", "adjudication",
}

CLARIFICATION_ALLOWED_CLASSES = set(EXPECTED_CLARIFICATION_CLASSES.keys())

EXPECTED_REPLAY_SELECTION_HASH = "2e45f30f714568ef"
EXPECTED_REPLAY_SELECTION_COUNT = 51

EXPECTED_REPLAY_CLASSES: dict[str, dict] = {
    "audit_change_type_vocabulary_only": {"count": 11, "hash": "b88018991e49ffd5"},
    "clarification_tool_without_clarification_contract": {"count": 11, "hash": "dc7446b93a05c648"},
    "creation_expectation_conflicts_with_replay_policy": {"count": 28, "hash": "3206003d4bc39a23"},
    "negated_surface_conflicts_with_create_contract": {"count": 1, "hash": "020fade8ca644684"},
    "genuine_replay_integration_defect": {"count": 0, "hash": "e3b0c44298fc1c14"},
}

REPLAY_RECORD_HASH = "2fabb972ad0bc00b"
COMBINED_HASH = "fd0de59a2967ddf8"

REPLAY_REQUIRED_KEYS = {
    "scenario_id", "blocker_class", "remediation_status", "provenance", "adjudication",
}

REPLAY_ALLOWED_CLASSES = set(EXPECTED_REPLAY_CLASSES.keys())

EXPECTED_REPLAY_REMEDIATION = {
    "audit_change_type_vocabulary_only": "authorized_for_generator_backed_contract_repair",
}

EXPECTED_EXIT = {
    "clarification_policy_decision_ready": 0,
    "genuine_replay_integration_defect": 0,
    "generator_backed_contract_repair_authorized": 11,
    "upstream_clarification_contract_blockers": 53,
    "remaining_replay_contract_reconciliation_blockers": 40,
}

# Semantic baseline
TOTAL_SCENARIOS = 1152
TOTAL_SAMPLES = 2304
CURRENT_SEMANTIC_BASELINE = (880, 814, 628, 101, 300, 782)
CURRENT_SAFETY = 1152

DEVELOPMENT_CORPUS_HASH = "sha256:aa2d946b60694eab96846ed77e885273c807e127f8998981a8cf8ff20ebae647"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_json(rel_path: str):
    with open(PROJECT_ROOT / rel_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _prep_variants() -> tuple[list, dict, list]:
    """Return (all_variants_list, variants_dict, queue_records) from live corpus."""
    from app.services.bernie.scale_corpus import DevelopmentOnlyLoader
    corpus = DevelopmentOnlyLoader().load_all()
    all_variants = list(corpus.all_variants())
    variants = {v.scenario_id: v for v in all_variants}
    queue = _load_json("docs/bernie-lc4r7-adjudication-queue.json")
    return all_variants, variants, queue


# ===================================================================
# 1.  Helper compilation
# ===================================================================


class TestHelperCompilation:
    """The helper script must compile and be importable."""

    def test_compile(self):
        """The helper must compile without syntax errors."""
        import py_compile
        py_compile.compile(
            str(SCRIPTS_DIR / "bernie_lc4r8_exit_blocker_reconciliation.py"),
            doraise=True,
        )

    def test_import(self):
        """The helper must be importable."""
        import scripts.bernie_lc4r8_exit_blocker_reconciliation as mod
        assert hasattr(mod, "build_all")
        assert hasattr(mod, "build_from_variants")
        assert hasattr(mod, "run_check")
        assert hasattr(mod, "EXPECTED_CLARIFICATION_SELECTION_HASH")


# ===================================================================
# 2.  build_from_variants entry point — original, shuffled, reversed
# ===================================================================


class TestBuildFromVariants:
    """The build_from_variants entry point must produce identical results
    for original, deterministically shuffled, and reversed variant orders."""

    @pytest.fixture(scope="class")
    def variant_sets(self):
        """Return three variant dicts with different iteration orders."""
        all_variants, variants_original, queue = _prep_variants()

        # Deterministic shuffle: use fixed seed, shuffle IDs, rebuild dict
        rng = random.Random(42)
        shuffled_ids = [v.scenario_id for v in all_variants]
        rng.shuffle(shuffled_ids)
        variants_shuffled = {sid: variants_original[sid] for sid in shuffled_ids}

        # Reverse order
        reversed_ids = [v.scenario_id for v in reversed(all_variants)]
        variants_reversed = {sid: variants_original[sid] for sid in reversed_ids}

        return {
            "original": variants_original,
            "shuffled": variants_shuffled,
            "reversed": variants_reversed,
            "queue": queue,
        }

    def test_orders_differ(self, variant_sets):
        """Verify the three variant dicts have genuinely different key insertion orders."""
        orig_keys = list(variant_sets["original"].keys())
        shuf_keys = list(variant_sets["shuffled"].keys())
        rev_keys = list(variant_sets["reversed"].keys())
        # All contain the same keys
        assert set(orig_keys) == set(shuf_keys) == set(rev_keys)
        assert len(orig_keys) == 1152
        # Insertion orders must differ
        assert orig_keys != shuf_keys, "shuffled order must differ from original"
        assert orig_keys != rev_keys, "reversed order must differ from original"
        assert shuf_keys != rev_keys, "shuffled and reversed orders must differ"

    def _run_and_extract(self, variants, queue):
        """Run build_from_variants and return a comparison dict."""
        from scripts.bernie_lc4r8_exit_blocker_reconciliation import build_from_variants
        cls, rp, report = build_from_variants(variants, queue)
        return {
            "clarification_records": cls["records"],
            "replay_records": rp["records"],
            "clarification_selection_hash": cls["selection"]["hash"],
            "clarification_selection_count": cls["selection"]["count"],
            "replay_selection_hash": rp["selection"]["hash"],
            "replay_selection_count": rp["selection"]["count"],
            "clarification_class_hashes": {
                k: v["hash"] for k, v in cls["blocker_classes"].items()
            },
            "replay_class_hashes": {
                k: v["hash"] for k, v in rp["blocker_classes"].items()
            },
            "clarification_action_hashes": cls.get("action_hashes", {}),
            "replay_action_hashes": rp.get("action_hashes", {}),
            "clarification_record_hash": cls["record_hash"],
            "replay_record_hash": rp["record_hash"],
            "combined_hash": report["replay_contract_audit"]["combined_hash"],
            "observed_exit_counts": report["exit_counts"]["observed"],
            "report_hash": report["report_hash"],
        }

    def test_original_order(self, variant_sets):
        """Original variant order must match contract constants."""
        result = self._run_and_extract(
            variant_sets["original"], variant_sets["queue"]
        )
        assert result["clarification_selection_count"] == EXPECTED_CLARIFICATION_SELECTION_COUNT
        assert result["clarification_selection_hash"] == EXPECTED_CLARIFICATION_SELECTION_HASH
        assert result["replay_selection_count"] == EXPECTED_REPLAY_SELECTION_COUNT
        assert result["replay_selection_hash"] == EXPECTED_REPLAY_SELECTION_HASH
        assert result["clarification_record_hash"] == CLARIFICATION_RECORD_HASH
        assert result["replay_record_hash"] == REPLAY_RECORD_HASH
        assert result["combined_hash"] == COMBINED_HASH

    def test_orders_produce_identical_output(self, variant_sets):
        """Original, shuffled, and reversed must produce identical full output."""
        orig_result = self._run_and_extract(
            variant_sets["original"], variant_sets["queue"]
        )
        shuf_result = self._run_and_extract(
            variant_sets["shuffled"], variant_sets["queue"]
        )
        rev_result = self._run_and_extract(
            variant_sets["reversed"], variant_sets["queue"]
        )

        # Compare every field
        for key in orig_result:
            assert orig_result[key] == shuf_result[key], (
                f"shuffled differs from original on {key}"
            )
            assert orig_result[key] == rev_result[key], (
                f"reversed differs from original on {key}"
            )


# ===================================================================
# 3.  Committed artifact record schema  (clarification)
# ===================================================================


class TestClarificationRecords:
    """53 redacted clarification records must have exact allowed schema."""

    @pytest.fixture(scope="class")
    def clarification(self):
        return _load_json("docs/bernie-lc4r8-clarification-decision-surface.json")

    def test_selection_count(self, clarification):
        assert clarification["selection"]["count"] == EXPECTED_CLARIFICATION_SELECTION_COUNT

    def test_selection_hash(self, clarification):
        assert clarification["selection"]["hash"] == EXPECTED_CLARIFICATION_SELECTION_HASH

    def test_selection_hash_match(self, clarification):
        assert clarification["selection"]["hash_match"] is True

    def test_record_hash(self, clarification):
        assert clarification["record_hash"] == CLARIFICATION_RECORD_HASH

    def test_development_only(self, clarification):
        assert clarification["development_only"] is True

    def test_silver_pending_only(self, clarification):
        assert clarification["silver_pending_only"] is True

    def test_record_count(self, clarification):
        assert len(clarification["records"]) == EXPECTED_CLARIFICATION_SELECTION_COUNT

    def test_record_schema(self, clarification):
        """Every record must have exactly the required keys."""
        for i, record in enumerate(clarification["records"]):
            assert set(record) == CLARIFICATION_REQUIRED_KEYS, (
                f"Record {i}: keys {set(record)} != {CLARIFICATION_REQUIRED_KEYS}"
            )
            assert all(isinstance(v, str) for v in record.values()), (
                f"Record {i}: all values must be strings"
            )

    def test_record_blocker_classes_allowed(self, clarification):
        """Every record's blocker_class must be an allowed value."""
        for i, record in enumerate(clarification["records"]):
            assert record["blocker_class"] in CLARIFICATION_ALLOWED_CLASSES, (
                f"Record {i}: invalid blocker_class {record['blocker_class']!r}"
            )

    def test_provenance_silver(self, clarification):
        """Every record must have provenance=silver."""
        for i, record in enumerate(clarification["records"]):
            assert record["provenance"] == "silver", (
                f"Record {i}: provenance != silver"
            )

    def test_adjudication_pending(self, clarification):
        """Every record must have adjudication=pending."""
        for i, record in enumerate(clarification["records"]):
            assert record["adjudication"] == "pending", (
                f"Record {i}: adjudication != pending"
            )

    def test_decision_readiness_blocked(self, clarification):
        """Every record must have decision_readiness=blocked_by_upstream_contract_defect."""
        for i, record in enumerate(clarification["records"]):
            assert record["decision_readiness"] == "blocked_by_upstream_contract_defect", (
                f"Record {i}: decision_readiness != blocked"
            )

    def test_class_counts(self, clarification):
        """Each blocker class count must match the frozen contract."""
        for cls_name, expected_info in EXPECTED_CLARIFICATION_CLASSES.items():
            actual = clarification["blocker_classes"].get(cls_name, {})
            assert actual.get("count") == expected_info["count"], (
                f"{cls_name}: expected count {expected_info['count']}, got {actual.get('count')}"
            )

    def test_class_hashes(self, clarification):
        """Each blocker class hash must match the frozen contract."""
        for cls_name, expected_info in EXPECTED_CLARIFICATION_CLASSES.items():
            actual = clarification["blocker_classes"].get(cls_name, {})
            assert actual.get("hash") == expected_info["hash"], (
                f"{cls_name}: expected hash {expected_info['hash']}, got {actual.get('hash')}"
            )

    def test_action_distribution(self, clarification):
        """Action distribution must match frozen contract."""
        dist = clarification.get("action_distribution", {})
        for action, expected in EXPECTED_CLARIFICATION_ACTION_DISTRIBUTION.items():
            assert dist.get(action) == expected, (
                f"Action {action}: expected {expected}, got {dist.get(action)}"
            )

    def test_action_hashes(self, clarification):
        """Action hashes must match frozen contract."""
        hashes = clarification.get("action_hashes", {})
        for action, expected_hash in EXPECTED_CLARIFICATION_ACTION_HASHES.items():
            assert hashes.get(action) == expected_hash, (
                f"Action hash {action}: expected {expected_hash}, got {hashes.get(action)}"
            )

    def test_zero_decision_ready(self, clarification):
        """isolated_clarification_policy_choice must be 0."""
        assert clarification["blocker_classes"]["isolated_clarification_policy_choice"]["count"] == 0

    def test_no_extra_records(self, clarification):
        """No records with unexpected scenario_ids or classes."""
        seen_ids = set()
        for record in clarification["records"]:
            seen_ids.add(record["scenario_id"])
        assert len(seen_ids) == EXPECTED_CLARIFICATION_SELECTION_COUNT


# ===================================================================
# 4.  Committed artifact record schema  (replay)
# ===================================================================


class TestReplayRecords:
    """51 redacted replay records must have exact allowed schema."""

    @pytest.fixture(scope="class")
    def replay_audit(self):
        return _load_json("docs/bernie-lc4r8-replay-contract-audit.json")

    def test_selection_count(self, replay_audit):
        assert replay_audit["selection"]["count"] == EXPECTED_REPLAY_SELECTION_COUNT

    def test_selection_hash(self, replay_audit):
        assert replay_audit["selection"]["hash"] == EXPECTED_REPLAY_SELECTION_HASH

    def test_selection_hash_match(self, replay_audit):
        assert replay_audit["selection"]["hash_match"] is True

    def test_record_hash(self, replay_audit):
        assert replay_audit["record_hash"] == REPLAY_RECORD_HASH

    def test_development_only(self, replay_audit):
        assert replay_audit["development_only"] is True

    def test_silver_pending_only(self, replay_audit):
        assert replay_audit["silver_pending_only"] is True

    def test_record_count(self, replay_audit):
        assert len(replay_audit["records"]) == EXPECTED_REPLAY_SELECTION_COUNT

    def test_record_schema(self, replay_audit):
        """Every record must have exactly the required keys."""
        for i, record in enumerate(replay_audit["records"]):
            assert set(record) == REPLAY_REQUIRED_KEYS, (
                f"Record {i}: keys {set(record)} != {REPLAY_REQUIRED_KEYS}"
            )
            assert all(isinstance(v, str) for v in record.values()), (
                f"Record {i}: all values must be strings"
            )

    def test_record_blocker_classes_allowed(self, replay_audit):
        """Every record's blocker_class must be an allowed value."""
        for i, record in enumerate(replay_audit["records"]):
            assert record["blocker_class"] in REPLAY_ALLOWED_CLASSES, (
                f"Record {i}: invalid blocker_class {record['blocker_class']!r}"
            )

    def test_provenance_silver(self, replay_audit):
        """Every record must have provenance=silver."""
        for i, record in enumerate(replay_audit["records"]):
            assert record["provenance"] == "silver"

    def test_adjudication_pending(self, replay_audit):
        """Every record must have adjudication=pending."""
        for i, record in enumerate(replay_audit["records"]):
            assert record["adjudication"] == "pending"

    def test_remediation_status(self, replay_audit):
        """Only audit_change_type gets authorized; others must be not_authorized."""
        for i, record in enumerate(replay_audit["records"]):
            expected = EXPECTED_REPLAY_REMEDIATION.get(
                record["blocker_class"],
                "not_authorized_contract_reconciliation_required",
            )
            assert record["remediation_status"] == expected, (
                f"Record {i} ({record['blocker_class']}): "
                f"expected remediation {expected!r}, got {record['remediation_status']!r}"
            )

    def test_class_counts(self, replay_audit):
        """Each replay blocker class count must match contract."""
        for cls_name, expected_info in EXPECTED_REPLAY_CLASSES.items():
            actual = replay_audit["blocker_classes"].get(cls_name, {})
            assert actual.get("count") == expected_info["count"]

    def test_class_hashes(self, replay_audit):
        """Each replay blocker class hash must match contract."""
        for cls_name, expected_info in EXPECTED_REPLAY_CLASSES.items():
            actual = replay_audit["blocker_classes"].get(cls_name, {})
            assert actual.get("hash") == expected_info["hash"]

    def test_zero_genuine_defects(self, replay_audit):
        assert replay_audit["blocker_classes"]["genuine_replay_integration_defect"]["count"] == 0


# ===================================================================
# 5.  Exit report
# ===================================================================


class TestExitReport:
    """Aggregate exit report must preserve correct exit counts."""

    @pytest.fixture(scope="class")
    def report(self):
        return _load_json("docs/bernie-lc4r8-exit-blocker-report.json")

    def test_exit_counts(self, report):
        """Every exit count must match the frozen contract."""
        observed = report.get("exit_counts", {}).get("observed", {})
        expected = report.get("exit_counts", {}).get("expected", {})
        for key, exp_val in EXPECTED_EXIT.items():
            assert observed.get(key) == exp_val, (
                f"exit_counts.observed.{key}: expected {exp_val}, got {observed.get(key)}"
            )
            assert expected.get(key) == exp_val, (
                f"exit_counts.expected.{key}: expected {exp_val}, got {expected.get(key)}"
            )

    def test_exit_status(self, report):
        assert report["exit_status"] == "blocked_pending_generator_repair_and_contract_reconciliation"

    def test_assertions(self, report):
        """All exit report assertions must be True."""
        assertions = report.get("assertions", {})
        for name, value in assertions.items():
            assert value is True, f"Assertion {name} is {value!r}"

    def test_report_hash_integrity(self, report):
        """Report hash must match recomputed hash."""
        from scripts.bernie_lc4r8_exit_blocker_reconciliation import _compute_report_hash
        recomputed = _compute_report_hash(report)
        assert recomputed == report.get("report_hash", ""), (
            f"Report hash mismatch: recomputed={recomputed}, stored={report.get('report_hash')}"
        )

    def test_corpus_hash(self, report):
        """Corpus hash must match development record."""
        ch = report.get("corpus_hash", {})
        assert ch.get("observed") == DEVELOPMENT_CORPUS_HASH
        assert ch.get("expected") == DEVELOPMENT_CORPUS_HASH
        assert ch.get("match") is True

    def test_semantic_baseline(self, report):
        """Semantic baseline must match contract."""
        sb = report.get("semantic_baseline", {})
        obs = sb.get("observed", {})
        exp = sb.get("expected", {})
        for field, val in [("intended_action", 880), ("action_semantics", 814),
                           ("temporal_relation", 628), ("normalized_values", 101),
                           ("entity_semantics", 300), ("clarification", 782)]:
            assert obs.get(field) == val, f"semantic_baseline.observed.{field}: {obs.get(field)} != {val}"
            assert exp.get(field) == val, f"semantic_baseline.expected.{field}: {exp.get(field)} != {val}"

    def test_safety(self, report):
        """Safety section must show 1152/1152 all_safe."""
        saf = report.get("safety", {})
        assert saf.get("observed", {}).get("passed") == CURRENT_SAFETY
        assert saf.get("observed", {}).get("total") == TOTAL_SCENARIOS
        assert saf.get("observed", {}).get("all_safe") is True

    def test_variance(self, report):
        """Variance section must show zero variance over 2304 samples."""
        var = report.get("variance", {})
        assert var.get("observed", {}).get("variant_scenario_count") == 0
        assert var.get("observed", {}).get("sample_count") == TOTAL_SAMPLES
        assert var.get("observed", {}).get("all_samples_deterministic") is True


# ===================================================================
# 6.  Combined hash
# ===================================================================


class TestCombinedHash:
    """Combined clarification/replay record hash must match contract."""

    def test_combined_hash(self):
        report = _load_json("docs/bernie-lc4r8-exit-blocker-report.json")
        stored = report.get("replay_contract_audit", {}).get("combined_hash", "")
        assert stored == COMBINED_HASH, (
            f"Combined hash in report: {stored} != expected {COMBINED_HASH}"
        )

        # Also verify by recomputing from committed record artifacts
        clarification = _load_json("docs/bernie-lc4r8-clarification-decision-surface.json")
        replay_audit = _load_json("docs/bernie-lc4r8-replay-contract-audit.json")
        combined_lines = []
        for r in clarification["records"]:
            combined_lines.append(
                f"clarification|{r['scenario_id']}|{r['blocker_class']}|{r['decision_readiness']}"
            )
        for r in replay_audit["records"]:
            combined_lines.append(
                f"replay|{r['scenario_id']}|{r['blocker_class']}|{r['remediation_status']}"
            )
        computed = _records_hash(combined_lines)
        assert computed == COMBINED_HASH, (
            f"Recomputed combined hash: {computed} != expected {COMBINED_HASH}"
        )


# ===================================================================
# 7.  Replay of deterministic evaluation  (LC7-preserved semantic baseline)
# ===================================================================


class TestSemanticBaselinePreserved:
    """The LC4R8 helper must not change the deterministic evaluation results."""

    def test_semantic_baseline(self):
        """Semantic counts must match the LC4R7 contract (880/814/628/101/300/782)."""
        from app.services.bernie.scaled_evaluator import generate_scaled_evaluation_report
        report = generate_scaled_evaluation_report()
        per_dim = report["per_dimension"]
        sf = per_dim["semantic_fields"]

        expected = {
            "intended_action": CURRENT_SEMANTIC_BASELINE[0],
            "action_semantics": CURRENT_SEMANTIC_BASELINE[1],
            "temporal_relation": CURRENT_SEMANTIC_BASELINE[2],
            "normalized_values": CURRENT_SEMANTIC_BASELINE[3],
            "entity_semantics": CURRENT_SEMANTIC_BASELINE[4],
            "requires_clarification": CURRENT_SEMANTIC_BASELINE[5],
        }
        for field, expected_passed in expected.items():
            actual = sf[field]["passed"] // 2  # divide by 2 for per-scenario count
            assert actual == expected_passed, (
                f"{field}: expected {expected_passed}, got {actual} "
                f"(raw {sf[field]['passed']}/{sf[field]['total']})"
            )

    def test_safety_preserved(self):
        """Safety must be 1152/1152."""
        from app.services.bernie.scaled_evaluator import generate_scaled_evaluation_report
        report = generate_scaled_evaluation_report()
        safety = report["per_dimension"]["safety"]
        assert safety["passed"] == TOTAL_SAMPLES, (
            f"Safety passed: {safety['passed']} != {TOTAL_SAMPLES}"
        )
        assert safety["total"] == TOTAL_SAMPLES
        assert safety["failed"] == 0

    def test_variance_zero(self):
        """Repeat variance must be zero over 2,304 samples."""
        from app.services.bernie.scaled_evaluator import generate_scaled_evaluation_report
        report = generate_scaled_evaluation_report()
        variance = report["variance"]
        assert variance["variant_scenario_count"] == 0
        assert variance["all_samples_deterministic"] is True
        assert variance["total_repeats"] == 2


# ===================================================================
# 8.  LC4R8 CLI --check
# ===================================================================


class TestCLICheck:
    """The --check flag must pass against committed artifacts."""

    def test_cli_check(self):
        """The helper --check must return exit code 0."""
        import subprocess
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "bernie_lc4r8_exit_blocker_reconciliation.py"),
                "--check",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        assert result.returncode == 0, (
            f"CLI --check returned {result.returncode}:\n{result.stdout}"
        )
        assert "LC4R8 CHECK PASSED" in result.stdout


# ===================================================================
# 9.  Fail-closed mutation tests
# ===================================================================


class TestFailClosedMutations:
    """run_check must return False for every observable form of drift.

    Each mutation alters one aspect of a deep copy of the real build output
    and asserts that run_check returns False. Alternate values are selected
    deterministically, never through unordered-set iteration.
    """

    @pytest.fixture(scope="class")
    def real_artifacts(self):
        """Build the real artifacts once."""
        from scripts.bernie_lc4r8_exit_blocker_reconciliation import build_all
        return build_all()

    # -- Helpers --

    def _mutate_and_check(self, artifacts, mutator, desc: str) -> bool:
        """Deep-copy artifacts, apply mutator, return run_check result."""
        cls, rp, report = copy.deepcopy(artifacts)
        mutator(cls, rp, report)
        from scripts.bernie_lc4r8_exit_blocker_reconciliation import run_check
        return run_check(cls, rp, report)

    # -- Record field mutations --

    def test_missing_record_field(self, real_artifacts):
        """Missing scenario_id in a clarification record must return False."""
        def mut(cls, rp, report):
            if cls["records"]:
                del cls["records"][0]["scenario_id"]
        assert self._mutate_and_check(real_artifacts, mut,
                                       "missing scenario_id") is False

    def test_extra_record_field(self, real_artifacts):
        """Extra field in a clarification record must return False."""
        def mut(cls, rp, report):
            if cls["records"]:
                cls["records"][0]["extra_field"] = "bogus"
        assert self._mutate_and_check(real_artifacts, mut,
                                       "extra field") is False

    def test_unexpected_class(self, real_artifacts):
        """Unexpected blocker class must return False."""
        def mut(cls, rp, report):
            if cls["records"]:
                cls["records"][0]["blocker_class"] = "nonexistent_class"
        assert self._mutate_and_check(real_artifacts, mut,
                                       "unexpected class") is False

    def test_wrong_remediation_status(self, real_artifacts):
        """Wrong remediation status must return False."""
        def mut(cls, rp, report):
            if rp["records"]:
                rp["records"][0]["remediation_status"] = "bogus_status"
        assert self._mutate_and_check(real_artifacts, mut,
                                       "wrong remediation") is False

    def test_wrong_decision_readiness(self, real_artifacts):
        """Wrong decision_readiness must return False."""
        def mut(cls, rp, report):
            if cls["records"]:
                cls["records"][0]["decision_readiness"] = "bogus_readiness"
        assert self._mutate_and_check(real_artifacts, mut,
                                       "wrong readiness") is False

    def test_provenance_drift(self, real_artifacts):
        """Drifted provenance must return False."""
        def mut(cls, rp, report):
            if cls["records"]:
                cls["records"][0]["provenance"] = "gold"
        assert self._mutate_and_check(real_artifacts, mut,
                                       "provenance drift") is False

    def test_adjudication_drift(self, real_artifacts):
        """Drifted adjudication must return False."""
        def mut(cls, rp, report):
            if rp["records"]:
                rp["records"][0]["adjudication"] = "accepted"
        assert self._mutate_and_check(real_artifacts, mut,
                                       "adjudication drift") is False

    # -- Selection mutations --

    def test_selection_count_drift(self, real_artifacts):
        """Wrong selection count must return False."""
        def mut(cls, rp, report):
            cls["selection"]["count"] = 52
        assert self._mutate_and_check(real_artifacts, mut,
                                       "selection count drift") is False

    def test_selection_hash_drift(self, real_artifacts):
        """Wrong selection hash must return False."""
        def mut(cls, rp, report):
            cls["selection"]["hash"] = "0000000000000000"
        assert self._mutate_and_check(real_artifacts, mut,
                                       "selection hash drift") is False

    # -- Class count/hash mutations --

    def test_class_count_drift(self, real_artifacts):
        """Wrong class count must return False."""
        def mut(cls, rp, report):
            if "temporal_and_normalization_contract_blocked" in cls["blocker_classes"]:
                cls["blocker_classes"]["temporal_and_normalization_contract_blocked"]["count"] = 99
        assert self._mutate_and_check(real_artifacts, mut,
                                       "class count drift") is False

    def test_class_hash_drift(self, real_artifacts):
        """Wrong class hash must return False."""
        def mut(cls, rp, report):
            if "temporal_and_normalization_contract_blocked" in cls["blocker_classes"]:
                cls["blocker_classes"]["temporal_and_normalization_contract_blocked"]["hash"] = "0000000000000000"
        assert self._mutate_and_check(real_artifacts, mut,
                                       "class hash drift") is False

    # -- Action mutations --

    def test_action_count_drift(self, real_artifacts):
        """Wrong action distribution count must return False."""
        def mut(cls, rp, report):
            cls["action_distribution"]["create"] = 99
        assert self._mutate_and_check(real_artifacts, mut,
                                       "action count drift") is False

    def test_action_hash_drift(self, real_artifacts):
        """Wrong action hash must return False."""
        def mut(cls, rp, report):
            cls["action_hashes"]["create"] = "0000000000000000"
        assert self._mutate_and_check(real_artifacts, mut,
                                       "action hash drift") is False

    # -- Canonical record drift --

    def test_canonical_record_drift(self, real_artifacts):
        """Different record content must return False."""
        def mut(cls, rp, report):
            if cls["records"]:
                cls["records"][0]["blocker_class"] = "normalization_contract_blocked"
        assert self._mutate_and_check(real_artifacts, mut,
                                       "canonical record drift") is False

    # -- Combined hash drift --

    def test_combined_hash_drift(self, real_artifacts):
        """Wrong combined hash must return False."""
        def mut(cls, rp, report):
            report["replay_contract_audit"]["combined_hash"] = "0000000000000000"
        assert self._mutate_and_check(real_artifacts, mut,
                                       "combined hash drift") is False

    # -- Corpus hash drift --

    def test_corpus_hash_drift(self, real_artifacts):
        """Wrong corpus hash must return False."""
        def mut(cls, rp, report):
            report["corpus_hash"]["observed"] = "sha256:0000000000000000000000000000000000000000000000000000000000000000"
        assert self._mutate_and_check(real_artifacts, mut,
                                       "corpus hash drift") is False

    # -- Baseline class drift --

    def test_baseline_intended_action_drift(self, real_artifacts):
        """Drifted intended_action baseline must return False."""
        def mut(cls, rp, report):
            report["semantic_baseline"]["observed"]["intended_action"] = 0
        assert self._mutate_and_check(real_artifacts, mut,
                                       "baseline intended_action drift") is False

    def test_baseline_action_semantics_drift(self, real_artifacts):
        """Drifted action_semantics baseline must return False."""
        def mut(cls, rp, report):
            report["semantic_baseline"]["observed"]["action_semantics"] = 0
        assert self._mutate_and_check(real_artifacts, mut,
                                       "baseline action_semantics drift") is False

    def test_baseline_temporal_relation_drift(self, real_artifacts):
        """Drifted temporal_relation baseline must return False."""
        def mut(cls, rp, report):
            report["semantic_baseline"]["observed"]["temporal_relation"] = 0
        assert self._mutate_and_check(real_artifacts, mut,
                                       "baseline temporal_relation drift") is False

    def test_baseline_normalized_values_drift(self, real_artifacts):
        """Drifted normalized_values baseline must return False."""
        def mut(cls, rp, report):
            report["semantic_baseline"]["observed"]["normalized_values"] = 0
        assert self._mutate_and_check(real_artifacts, mut,
                                       "baseline normalized_values drift") is False

    def test_baseline_entity_semantics_drift(self, real_artifacts):
        """Drifted entity_semantics baseline must return False."""
        def mut(cls, rp, report):
            report["semantic_baseline"]["observed"]["entity_semantics"] = 0
        assert self._mutate_and_check(real_artifacts, mut,
                                       "baseline entity_semantics drift") is False

    def test_baseline_clarification_drift(self, real_artifacts):
        """Drifted clarification baseline must return False."""
        def mut(cls, rp, report):
            report["semantic_baseline"]["observed"]["clarification"] = 0
        assert self._mutate_and_check(real_artifacts, mut,
                                       "baseline clarification drift") is False

    # -- Safety drift --

    def test_safety_passed_drift(self, real_artifacts):
        """Drifted safety passed must return False."""
        def mut(cls, rp, report):
            report["safety"]["observed"]["passed"] = 0
        assert self._mutate_and_check(real_artifacts, mut,
                                       "safety passed drift") is False

    def test_safety_total_drift(self, real_artifacts):
        """Drifted safety total must return False."""
        def mut(cls, rp, report):
            report["safety"]["observed"]["total"] = 0
        assert self._mutate_and_check(real_artifacts, mut,
                                       "safety total drift") is False

    def test_safety_boolean_drift(self, real_artifacts):
        """Drifted safety all_safe boolean must return False."""
        def mut(cls, rp, report):
            report["safety"]["observed"]["all_safe"] = False
        assert self._mutate_and_check(real_artifacts, mut,
                                       "safety all_safe drift") is False

    # -- Variance drift --

    def test_variance_count_drift(self, real_artifacts):
        """Drifted variance count must return False."""
        def mut(cls, rp, report):
            report["variance"]["observed"]["variant_scenario_count"] = 5
        assert self._mutate_and_check(real_artifacts, mut,
                                       "variance count drift") is False

    def test_variance_sample_drift(self, real_artifacts):
        """Drifted variance sample count must return False."""
        def mut(cls, rp, report):
            report["variance"]["observed"]["sample_count"] = 0
        assert self._mutate_and_check(real_artifacts, mut,
                                       "variance sample drift") is False

    def test_variance_boolean_drift(self, real_artifacts):
        """Drifted variance deterministic boolean must return False."""
        def mut(cls, rp, report):
            report["variance"]["observed"]["all_samples_deterministic"] = False
        assert self._mutate_and_check(real_artifacts, mut,
                                       "variance boolean drift") is False

    # -- Observed exit count drift --

    def test_exit_count_drift(self, real_artifacts):
        """Drifted exit count must return False."""
        def mut(cls, rp, report):
            report["exit_counts"]["observed"]["generator_backed_contract_repair_authorized"] = 99
        assert self._mutate_and_check(real_artifacts, mut,
                                       "exit count drift") is False

    def test_exit_status_drift(self, real_artifacts):
        """Drifted exit status must return False."""
        def mut(cls, rp, report):
            report["exit_status"] = "some_other_status"
        assert self._mutate_and_check(real_artifacts, mut,
                                       "exit status drift") is False

    # -- Assertion drift --

    def test_assertion_drift(self, real_artifacts):
        """Drifted assertion must return False."""
        def mut(cls, rp, report):
            report["assertions"]["clarification_selection_53"] = False
        assert self._mutate_and_check(real_artifacts, mut,
                                       "assertion drift") is False

    # -- Report hash/content drift --

    def test_report_hash_drift(self, real_artifacts):
        """Wrong report_hash that doesn't match recomputed hash must return False."""
        def mut(cls, rp, report):
            # Change a content field not directly validated elsewhere
            report["development_only"] = False
        assert self._mutate_and_check(real_artifacts, mut,
                                       "report hash drift") is False

    def test_report_content_drift(self, real_artifacts):
        """Changed report schema_version must return False."""
        def mut(cls, rp, report):
            report["schema_version"] = "lc4r8.drifted.v1"
        assert self._mutate_and_check(real_artifacts, mut,
                                       "report content drift") is False
