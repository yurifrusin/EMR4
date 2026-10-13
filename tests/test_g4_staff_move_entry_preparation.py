"""Pure G4 transition checks; a reviewed launcher supplies exact BEFORE, SCOPE and REVIEW.

The fixture REVIEW is the independently accepted G3 criterion record. These tests
neither admit the operation nor grant application/database execution.
"""
import copy
import json
import unittest
from pathlib import Path

from orchestration_harness import bounded_g1b as b
from orchestration_harness import raisa_policy as p

BEFORE = None
SCOPE = None
REVIEW = None


class G4StaffMoveEntryTests(unittest.TestCase):
    def test_exact_transition_preserves_g2_and_other_authority(self):
        before, scope, review = copy.deepcopy(BEFORE), copy.deepcopy(SCOPE), copy.deepcopy(REVIEW)
        after = b.build_g4_staff_move_transition(before, scope, review)
        old, new = b._json(before[b.STATE]), b._json(after[b.STATE])
        self.assertEqual(new['g2'], old['g2'])
        for key in set(old) - {'observed_at', 'current_gate', 'current_gate_status',
                'active_correction', 'active_profile', 'task_selection', 'g3'}:
            self.assertEqual(new[key], old[key], key)
        self.assertEqual(new['g3']['status'], 'passed')
        self.assertTrue(new['g3']['completion_accepted'])
        self.assertFalse(new['g3']['product_runtime_authorized'])
        self.assertEqual(new['current_gate'], 'G4')
        self.assertEqual(new['task_selection']['allowed_task_kinds'], ['g4_seeded_staff_move'])
        old_gates = b._document(before[b.GATES], b.GATES)
        new_gates = b._document(after[b.GATES], b.GATES)
        self.assertEqual(next(g for g in new_gates['gates'] if g['id'] == 'G3')['status'], 'passed')
        self.assertEqual(next(g for g in new_gates['gates'] if g['id'] == 'G4')['status'], 'active_bounded_staff_move')
        for old_gate in old_gates['gates']:
            if old_gate['id'] not in {'G3', 'G4'}:
                self.assertEqual(next(g for g in new_gates['gates'] if g['id'] == old_gate['id']), old_gate)
        overlay = b._document(after[b.OVERLAY], b.OVERLAY)
        self.assertEqual(overlay['active_profile'], p.G4_STAFF_MOVE_PROFILE)
        self.assertEqual(overlay['profiles'][p.G4_STAFF_MOVE_PROFILE], p.g4_staff_move_profile())
        self.assertEqual(before, BEFORE)
        self.assertEqual(scope, SCOPE)
        self.assertEqual(review, REVIEW)

    def test_missing_or_claimed_review_is_not_a_transition(self):
        for review in (None, {'full_g3_accepted': True, 'verdict': 'PASS_G3_CRITERION_ACCEPTANCE'}):
            with self.subTest(review=review):
                with self.assertRaisesRegex(b.BoundedG1BError, '^bounded_g4_g3_acceptance_pending$'):
                    b.build_g4_staff_move_transition(BEFORE, SCOPE, review)

    def test_one_unaccepted_criterion_stops_transition(self):
        review = copy.deepcopy(REVIEW)
        review['criterion_assessment']['stable_fallback_renders_same_semantics']['accepted'] = False
        with self.assertRaisesRegex(b.BoundedG1BError, '^bounded_g4_criterion_unaccepted$'):
            b.build_g4_staff_move_transition(BEFORE, SCOPE, review)

    def test_scope_widening_and_runtime_claim_rejected(self):
        for key, value in [('allowed_paths', sorted(b.G4_PRODUCT | {'app/main.py'})),
                ('allowed_effects', sorted(b.EFFECTS | {'provider_call'})),
                ('admission_grants_runtime_authority', True)]:
            with self.subTest(key=key):
                scope = copy.deepcopy(SCOPE)
                scope[key] = value
                with self.assertRaisesRegex(b.BoundedG1BError, '^bounded_g4_scope_boundary$'):
                    b.build_g4_staff_move_transition(BEFORE, scope, REVIEW)

    def test_changed_before_image_rejected(self):
        before = dict(BEFORE)
        state = b._json(before[b.STATE])
        state['g3']['completion_accepted'] = True
        before[b.STATE] = b._canonical(state) + b'\n'
        with self.assertRaisesRegex(b.BoundedG1BError, '^bounded_g4_preimage_drift$'):
            b.build_g4_staff_move_transition(before, SCOPE, REVIEW)

    def test_registered_route_is_exact_and_has_no_runtime_grant(self):
        self.assertEqual(b.operation_paths('enable_g4_staff_move'), b.G4_CONTROL)
        self.assertEqual(b.operation_paths('implement_g4_staff_move'), b.G4_PRODUCT)
        self.assertEqual(b.operation_effects('enable_g4_staff_move'), b.EFFECTS)
        self.assertEqual(b.operation_effects('implement_g4_staff_move'), b.EFFECTS | {'product_behavior_change'})
        self.assertFalse(SCOPE['admission_grants_runtime_authority'])

    def test_later_g4_review_requires_distinct_independent_identity(self):
        row = {'path': str(Path(__file__).resolve()), 'sha256': 'a' * 64}
        review = {'reviewer_agent': '/root/g3_entry_review', 'independent': True,
            'implementation_authorship': False, 'verdict': 'PASS_G4_STAFF_MOVE_EXACT_ADMISSION_SUBJECT',
            'blocking_findings': [], 'subject_sha256': 'b' * 64}
        read = lambda _path, _digest: json.dumps(review).encode()
        with self.assertRaisesRegex(b.BoundedG1BError,
                                    '^bounded_g4_operation_independent_review$'):
            b._g4_operation_review(read, row, 'b' * 64,
                                   'PASS_G4_STAFF_MOVE_EXACT_ADMISSION_SUBJECT')


if __name__ == '__main__':
    unittest.main()
