"""Source-only focused checks. Explicit literal inputs; no canonical map/graph.

Coordinator must bind/review execution and explicit module loading separately.
No test collection over a repository, conftest, Git or writer execution is needed.
"""
import copy
from pathlib import Path
import unittest

from orchestration_harness import governance_goal_update as subject


class GoalUpdateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload_raw = Path("C:/Users/there/EMR4-tools/compass-gpms-goal-steering-preparation-v1/gpms-goal-update-payload-v2.json").read_bytes()
        cls.dispositions_raw = Path("C:/Users/there/EMR4-tools/compass-g4-reconnection-candidate-v1/capability-dispositions-v1.json").read_bytes()

    def setUp(self):
        self.intent = {
            "schema_version": subject.INTENT_VERSION,
            "operation_id": subject.OPERATION_ID,
            "recorded_at": "2026-10-26T00:00:00+00:00",
            "payload_sha256": subject.PAYLOAD_SHA256,
            "capability_dispositions_sha256": subject.DISPOSITIONS_SHA256,
            "effect": "goal_roadmap_only",
            "recommendation_selection_dispatch": "unchanged_not_enabled",
        }
        # Newly authored map-shaped input only; not a canonical Compass fixture.
        self.compass = {
            "map_revision": 17, "source_graph_revision": 29,
            "updated_at": "old", "orientation_statement": "old orientation",
            "north_star": {"title": "old", "summary": "old", "evidence": ["docs/old.md"], "unknown_preserved": True},
            "programme": {"id": "existing-programme", "qualifications": ["G2/G3 accepted"]},
            "journey": [{"node_id": "accepted-governance-node"}],
            "current_position": {"node_id": "accepted-governance-node", "partial": "M1"},
            "decision_horizon": [{"id": "deferred-existing", "status": "deferred", "nested": [1, 2]}],
            "programme_support_horizon": [{"id": "context", "status": "active"}],
            "user_owned_decisions": [{"question": "retained"}],
            "map_limits": ["prior qualification"], "other_future_key": {"retained": True},
        }

    def project(self, **changes):
        return subject.project_goal_update(
            changes.get("compass", self.compass), changes.get("intent", self.intent),
            payload_raw=changes.get("payload_raw", self.payload_raw),
            dispositions_raw=changes.get("dispositions_raw", self.dispositions_raw))

    def test_exact_original_eighteen_domains_and_qualified_roadmap(self):
        payload = subject.validate_goal_sources(self.payload_raw, self.dispositions_raw)
        self.assertEqual(len(payload["capability_dispositions"]["domains"]), 18)
        self.assertEqual(payload["owner_confirmed_goal"]["pilot"], "EXCLUDED")
        result = self.project()
        horizon = result["decision_horizon"][-1]
        self.assertEqual(len(horizon["prerequisites"]), 6)
        self.assertIn("aggregate NONPASS", horizon["prerequisites"][0])
        self.assertIn("No automatic dispatch", horizon["prerequisites"][2])
        self.assertIn("M1 remains partial", horizon["prerequisites"][3])
        self.assertIn("costed_sydney_plan_v1", horizon["prerequisites"][4])
        self.assertIn("Mutable navigation pointer only", horizon["prerequisites"][4])
        self.assertEqual(horizon["boundary_changes"], [])

    def test_projection_preserves_all_unowned_values_and_input(self):
        before = copy.deepcopy(self.compass)
        result = self.project()
        self.assertEqual(self.compass, before)
        mutable = {"north_star", "orientation_statement", "decision_horizon", "map_limits", "map_revision", "updated_at"}
        self.assertEqual({k: v for k, v in result.items() if k not in mutable},
                         {k: v for k, v in before.items() if k not in mutable})
        self.assertEqual(result["decision_horizon"][:-1], before["decision_horizon"])
        self.assertEqual(result["map_limits"][:-1], before["map_limits"])
        self.assertTrue(result["north_star"]["unknown_preserved"])
        self.assertEqual(result["source_graph_revision"], 29)
        self.assertEqual(result["map_revision"], 18)

    def test_deterministic_and_duplicate_event_rejected(self):
        result = self.project()
        self.assertEqual(result, self.project())
        with self.assertRaisesRegex(subject.GoalUpdateRejection, "goal_update_already_recorded"):
            self.project(compass=result)

    def test_payload_or_original_disposition_drift_fails_closed(self):
        for key, raw in (("payload_raw", self.payload_raw), ("dispositions_raw", self.dispositions_raw)):
            with self.assertRaises(subject.GoalUpdateRejection):
                self.project(**{key: raw + b" "})

    def test_derived_lease_dispatch_or_next_operation_input_rejected(self):
        for key in ("lease_sequence", "next_operation", "active_latch", "canonical_sha256s", "dispatch"):
            intent = dict(self.intent, **{key: "forbidden"})
            with self.assertRaisesRegex(subject.GoalUpdateRejection, "goal_intent_keys"):
                self.project(intent=intent)
        for value in ("automatic", "read_only_recommendation_enabled"):
            intent = dict(self.intent, recommendation_selection_dispatch=value)
            with self.assertRaisesRegex(subject.GoalUpdateRejection, "goal_intent_effect_scope"):
                self.project(intent=intent)

    def test_wrong_event_or_pin_or_timestamp_rejected(self):
        for key, value in (("schema_version", "ariadne.g4_emr4_compass_orientation_intent.v1"),
                           ("operation_id", "old-consumed-operation"),
                           ("payload_sha256", "0" * 64),
                           ("recorded_at", "2026-10-26")):
            with self.assertRaises(subject.GoalUpdateRejection):
                self.project(intent=dict(self.intent, **{key: value}))

    def test_bad_baseline_shape_does_not_become_authority(self):
        for key, value in (("map_revision", True), ("decision_horizon", None), ("north_star", {})):
            with self.assertRaises(subject.GoalUpdateRejection):
                self.project(compass=dict(self.compass, **{key: value}))


if __name__ == "__main__":
    unittest.main()
