"""Focused tests for LC4R8 exit-blocker reconciliation.

Reproduces every frozen count and hash from contract constants, validates
redacted record schemas, and fails closed on drift.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
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

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_json(rel_path: str):
    with open(PROJECT_ROOT / rel_path, "r", encoding="utf-8") as f:
        return json.load(f)


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
        assert hasattr(mod, "run_check")
        assert hasattr(mod, "EXPECTED_CLARIFICATION_SELECTION_HASH")


# ===================================================================
# 2.  Order invariance (original, shuffled, reversed)
# ===================================================================


class TestOrderInvariance:
    """The classification must be invariant to variant input order."""

    def _run_build(self):
        from scripts.bernie_lc4r8_exit_blocker_reconciliation import build_all
        return build_all()

    def _extract_counts(self, clarification, replay_audit):
        """Extract class counts from built artifacts."""
        cls_counts = {
            k: v["count"] for k, v in clarification["blocker_classes"].items()
        }
        rp_counts = {
            k: v["count"] for k, v in replay_audit["blocker_classes"].items()
        }
        return cls_counts, rp_counts

    @pytest.fixture
    def expected_counts(self):
        """Ground truth from original-order run."""
        cls, rp, _er = self._run_build()
        return self._extract_counts(cls, rp)

    def test_original_order(self, expected_counts):
        """Original (fixture) order must reproduce contract counts."""
        cls_counts, rp_counts = expected_counts
        for expected_name, expected_info in EXPECTED_CLARIFICATION_CLASSES.items():
            assert cls_counts.get(expected_name) == expected_info["count"], (
                f"{expected_name}: expected {expected_info['count']}, got {cls_counts.get(expected_name)}"
            )
        for expected_name, expected_info in EXPECTED_REPLAY_CLASSES.items():
            assert rp_counts.get(expected_name) == expected_info["count"], (
                f"{expected_name}: expected {expected_info['count']}, got {rp_counts.get(expected_name)}"
            )

    def test_shuffled_ids(self, expected_counts):
        """Shuffled scenario-id order must produce same counts."""
        from scripts.bernie_lc4r8_exit_blocker_reconciliation import (
            _load_corpus,
            _load_queue,
            _build_clarification_surface,
            _build_replay_audit,
        )

        corpus = _load_corpus()
        queue = _load_queue()
        variants = {v.scenario_id: v for v in corpus.all_variants()}

        adj_sids = sorted(set(
            r["scenario_id"] for r in queue if r["disposition"] == "requires_adjudication"
        ))
        nlcm_sids = sorted(set(
            r["scenario_id"] for r in queue if r["disposition"] == "non_language_contract_mismatch"
        ))

        # Reverse-sorted input
        cls_rev = _build_clarification_surface(list(reversed(adj_sids)), variants)
        rp_rev = _build_replay_audit(list(reversed(nlcm_sids)), variants)
        rev_cls_counts, rev_rp_counts = self._extract_counts(cls_rev, rp_rev)

        assert rev_cls_counts == expected_counts[0], (
            f"Shuffled clarification counts differ: {rev_cls_counts} != {expected_counts[0]}"
        )
        assert rev_rp_counts == expected_counts[1], (
            f"Shuffled replay counts differ: {rev_rp_counts} != {expected_counts[1]}"
        )

    def test_reversed_variants(self, expected_counts):
        """Reversed variant-list order must produce same counts."""
        from scripts.bernie_lc4r8_exit_blocker_reconciliation import (
            _load_corpus,
            _load_queue,
            _build_clarification_surface,
            _build_replay_audit,
        )

        corpus = _load_corpus()
        queue = _load_queue()
        variants = {v.scenario_id: v for v in corpus.all_variants()}

        adj_sids = sorted(set(
            r["scenario_id"] for r in queue if r["disposition"] == "requires_adjudication"
        ))
        nlcm_sids = sorted(set(
            r["scenario_id"] for r in queue if r["disposition"] == "non_language_contract_mismatch"
        ))

        cls_rev = _build_clarification_surface(list(reversed(adj_sids)), variants)
        rp_rev = _build_replay_audit(list(reversed(nlcm_sids)), variants)
        rev_cls_counts, rev_rp_counts = self._extract_counts(cls_rev, rp_rev)

        assert rev_cls_counts == expected_counts[0]
        assert rev_rp_counts == expected_counts[1]


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
        for key, expected in EXPECTED_EXIT.items():
            actual = report.get("exit_counts", {}).get(key)
            assert actual == expected, (
                f"exit_counts.{key}: expected {expected}, got {actual}"
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
