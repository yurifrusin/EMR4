"""Focused authored G3 entry checks; the reviewed launcher supplies exact inputs.

No repository discovery or application imports. Native Git admission and complete
index reversal are separate evidence, not claims made by these pure tests.
"""
import copy
import unittest
from unittest.mock import patch

from orchestration_harness import bounded_g1b as b
from orchestration_harness import raisa_policy as p

BEFORE = None
SCOPE = None
CONFIGURATION = None


class G3EntryTests(unittest.TestCase):
    def test_exact_transition_preserves_g2_and_all_other_gates(self):
        before = copy.deepcopy(BEFORE)
        scope = copy.deepcopy(SCOPE)
        after = b.build_g3_entry_transition(before, scope)
        old = b._json(before[b.STATE])
        new = b._json(after[b.STATE])
        self.assertEqual(new['g2'], old['g2'])
        for key in set(old) - {'observed_at', 'programme_mode', 'current_gate', 'current_gate_status',
                'active_correction', 'active_profile', 'task_selection'}:
            self.assertEqual(new[key], old[key], key)
        old_gates = b._document(before[b.GATES], b.GATES)
        new_gates = b._document(after[b.GATES], b.GATES)
        changed = copy.deepcopy(old_gates)
        next(g for g in changed['gates'] if g['id'] == 'G3')['status'] = 'active_bounded_offline_entry'
        self.assertEqual(changed, new_gates)
        self.assertFalse(new['g3']['completion_accepted'])
        self.assertFalse(new['g3']['product_runtime_authorized'])
        self.assertTrue(new['g3']['broader_review_required_after_tranche'])
        self.assertEqual(before, BEFORE)
        self.assertEqual(scope, SCOPE)

    def test_changed_g2_preimage_is_rejected(self):
        before = dict(BEFORE)
        state = b._json(before[b.STATE])
        state['g2']['completion_accepted'] = False
        before[b.STATE] = b._canonical(state)
        with self.assertRaisesRegex(b.BoundedG1BError, '^bounded_g3_preimage$'):
            b.build_g3_entry_transition(before, SCOPE)

    def test_scope_cannot_expand_or_claim_completion(self):
        mutations = [('allowed_paths', sorted(b.G3_PRODUCT | {'app/main.py'})),
                     ('allowed_effects', sorted(b.EFFECTS | {'provider_call'})),
                     ('g3_completion_claimed', True),
                     ('stop_after_tranche', 'continue_automatically')]
        for key, value in mutations:
            with self.subTest(field=key):
                scope = copy.deepcopy(SCOPE)
                scope[key] = value
                with self.assertRaisesRegex(b.BoundedG1BError, '^bounded_g3_scope_boundary$'):
                    b.build_g3_entry_transition(BEFORE, scope)

    def test_finite_limits_and_recorded_renewals_cannot_be_disabled(self):
        for field in ['runtime_limits', 'standing_delegation']:
            scope = copy.deepcopy(SCOPE)
            scope[field] = {}
            with self.subTest(field=field), self.assertRaisesRegex(b.BoundedG1BError, '^bounded_g3_scope_boundary$'):
                b.build_g3_entry_transition(BEFORE, scope)

    def test_complete_configuration_accepts_only_bounded_profile(self):
        after = b.build_g3_entry_transition(BEFORE, SCOPE)
        documents = {**CONFIGURATION, b.OVERLAY: after[b.OVERLAY]}
        def validate(state, docs=documents):
            return p.validate_recovery_configuration(
                documents={b.Path(x).name: v for x, v in docs.items()},
                expected_sha256={b.Path(x).name: b._sha(v) for x, v in docs.items()},
                agents_text=after[b.AGENTS].decode(), state=state)
        state = b._json(after[b.STATE])
        self.assertIsNotNone(validate(state))
        state['g3']['product_runtime_authorized'] = True
        with self.assertRaisesRegex(p.RaisaPolicyError, '^configuration_g3_offline_profile_invalid$'):
            validate(state)

    def test_exact_kind_paths_and_no_wider_gate(self):
        self.assertEqual(b.operation_paths('enable_g3_entry'), b.G3_CONTROL)
        self.assertEqual(b.operation_paths('implement_g3_offline_appointment'), b.G3_PRODUCT)
        with self.assertRaisesRegex(b.BoundedG1BError, '^bounded_g1b_operation_kind$'):
            b.operation_paths('implement_g3_all_projections')

    def test_independent_review_cannot_be_self_attested(self):
        review = {'reviewer_agent': '/root', 'independent': True, 'implementation_authorship': False,
                  'verdict': 'PASS_G3_EXACT_ADMISSION_SUBJECT', 'blocking_findings': [], 'subject_sha256': 'a'*64}
        def read(_path, _digest):
            return b._canonical(review)
        with self.assertRaisesRegex(b.BoundedG1BError, '^bounded_g3_independent_review$'):
            b._g3_review(read, {'path': 'C:/authored-review.json', 'sha256': 'b'*64}, 'a'*64,
                         'PASS_G3_EXACT_ADMISSION_SUBJECT')

    def test_actual_evaluator_dispatch_with_authored_git_observation(self):
        after = b.build_g3_entry_transition(BEFORE, SCOPE)
        payloads = {**CONFIGURATION, **after}
        q = {'operation_id': 'g3-synthetic-evaluator', 'operation_kind': 'enable_g3_entry',
             'phase': 'development', 'candidate_tree': 'a'*40,
             'payload_sha256': {p:b._sha(raw) for p,raw in payloads.items()}}
        inputs = b.BoundedG1BInputs(q, BEFORE, payloads, {}, {'observation_sha256':'b'*64})
        context = b.BoundedG1BContext(target_root=b.Path('C:/authored-target'),
            source_root=b.Path('C:/authored-source'), evidence_root=b.Path('C:/authored-evidence'),
            scratch_root=b.Path('C:/authored-scratch'), binding_path=b.Path('C:/authored-binding.json'),
            expected_binding_sha256='c'*64)
        manifest = {'schema_version': b.REQUEST_VERSION, 'operation_id':q['operation_id'],
            'operation_kind':q['operation_kind'], 'binding_sha256':'c'*64, 'candidate_tree':'a'*40,
            'allowed_paths': sorted(b.G3_CONTROL), 'intended_side_effect_classes':sorted(b.EFFECTS)}
        with patch.object(b,'load_bounded_g1b_inputs',return_value=inputs):
            result=b.evaluate_bounded_g1b_operation(context=context,manifest=manifest,
                entrypoint='recovery_preflight',phase='development')
            self.assertTrue(result.policy_admitted,result.reason_codes)
            self.assertEqual(result.current_gate,'G3')
            self.assertEqual(result.active_profile,p.G3_OFFLINE_PROFILE)
            manifest['allowed_paths'].append('app/main.py')
            denied=b.evaluate_bounded_g1b_operation(context=context,manifest=manifest,
                entrypoint='recovery_preflight',phase='development')
            self.assertEqual(denied.reason_codes,('bounded_g1b_manifest_binding_mismatch',))

