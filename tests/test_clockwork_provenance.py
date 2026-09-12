"""Authored local tasks: independent recomputation, native capture and rejection.

Policy check-name fixtures exercise the contract; they are not a repository
preflight, global CI result or a live-model independence certificate.
"""
from __future__ import annotations

import copy
import hashlib
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest

import yaml

from orchestration_harness import clockwork_observer as observer
from orchestration_harness import clockwork_provenance as proof

GENERATOR = b'''import sys,json,base64,hashlib
p=json.loads(sys.stdin.buffer.read())
s=json.loads(base64.b64decode(p['inputs'][0]['content']['base64']))
a=str(sum(s['numbers'])).encode()
r={'candidate':{'sha256':'sha256:'+hashlib.sha256(a).hexdigest(),'base64':base64.b64encode(a).decode()},'decision':'DECISION: PASS','findings':[]}
sys.stdout.write(json.dumps(r,sort_keys=True,separators=(',',':')))
'''
VERIFIER = b'''import sys,json,base64
p=json.loads(sys.stdin.buffer.read())
s=json.loads(base64.b64decode(p['inputs'][0]['content']['base64']))
a=base64.b64decode(p['inputs'][1]['content']['base64'])
expected=0
for n in s['numbers']: expected+=n
ok=a==str(expected).encode() and [x['name'] for x in p['inputs']]==['spec','candidate']
r={'decision':'DECISION: PASS' if ok else 'DECISION: REVISION_REQUIRED','findings':[],'checks':{n:0 if ok else 1 for n in p['required_checks']}}
sys.stdout.write(json.dumps(r,sort_keys=True,separators=(',',':')))
'''
RED = b'''import sys,json,base64
p=json.loads(sys.stdin.buffer.read())
inputs={i['name']:base64.b64decode(i['content']['base64']) for i in p['inputs']}
s=json.loads(inputs['spec'])
valid=int(inputs['candidate'])==sum(s['numbers']) and set(inputs)=={'spec','candidate'} and p['role']=='red'
r={'decision':'DECISION: PASS' if valid else 'DECISION: REVISION_REQUIRED','findings':[],'checks':{}}
sys.stdout.write(json.dumps(r,sort_keys=True,separators=(',',':')))
'''
APPROVED_LOCAL_PROGRAMS = {GENERATOR, VERIFIER, RED,
    GENERATOR.replace(b"str(sum(s['numbers']))", b"str(sum(s['numbers'])+1)"),
    b"import time; time.sleep(2)",
    b"import sys; sys.stdin.buffer.read(); sys.stdout.write('x'*200000)"}


class ProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="ariadne-g1d-")
        cls.root = Path(cls.temporary.name)
        cls.controller = cls.root / "controller"
        cls.controller.mkdir()
        cls.pins = {}
        cls.executable = Path(sys.executable).resolve(strict=True)
        cls.observer_digest = proof.sha(Path(observer.__file__).read_bytes())
        cls.runtime_digest = proof.sha(cls.executable.read_bytes())
        policies = Path(__file__).parents[1] / "assets/policies"
        names = ("operating_model", "verifier_execution_policy", "security_review_protocol")
        raw = {name: (policies / (name + ".yaml")).read_bytes() for name in names}
        pins = {
            "operating_model": "0181a3b007f800cc7b610d8f16a9ac551daf7345da15232e464f40dda1e3ca6f",
            "verifier_execution_policy": "92721606167a0bcb6b65d40e62061d9aaba25b2e57e72d9a2ee0445d51d5258d",
            "security_review_protocol": "861e5f577b98e8e3928333d28b8fade24d7e214f0cd666961f665fbce153dc70"}
        assert all(hashlib.sha256(raw[n]).hexdigest() == pins[n] for n in names)
        documents = {n: yaml.safe_load(raw[n]) for n in names}
        cls.policy = {"source_sha256": {n: proof.sha(raw[n]) for n in names},
            "security_triggers": documents["security_review_protocol"]["risk_classification"]["security_sensitive_triggers"],
            "external_triggers": documents["verifier_execution_policy"]["external_verifier"]["triggers"],
            "required_checks": list(documents["verifier_execution_policy"]["deterministic_gate"]["required_results"]),
            "live_model_required": False}
        cls.routine = cls.capture("routine-native")
        cls.dual = cls.capture("dual-native", dual=True)

    @classmethod
    def tearDownClass(cls):
        cls.saved_evidence = {}
        for name in ("routine-native", "dual-native", "native-wrong-result", "native-timeout",
                     "native-oversize", "before-anchor", "lost-anchor-response"):
            for filename in ("partial.json", "bundle.json"):
                path = cls.root / name / filename
                if path.is_file():
                    cls.saved_evidence[name + "/" + filename] = path.read_bytes()
            anchor = cls.controller / (name + ".json")
            if anchor.is_file():
                cls.saved_evidence[name + "/controller-anchor.json"] = anchor.read_bytes()
        cls.saved_anchor_pins = dict(cls.pins)
        cls.temporary.cleanup()

    @classmethod
    def assignment(cls, name, dual=False, sources=None):
        sources = sources or {"generator": GENERATOR, "verifier": VERIFIER, **({"red": RED} if dual else {})}
        now = time.time_ns()
        return {"assignment_id": name, "operation_id": "authored-sum", "attempt_id": name,
            "scope_sha256": proof.sha(b"authored-local-proof-scope"),
            "controller_reference": proof.sha(b"independently-retained-controller-reference"),
            "observer_source_sha256": cls.observer_digest, "executable_sha256": cls.runtime_digest,
            "created_ns": now, "not_after_ns": now + 300_000_000_000, "policy": copy.deepcopy(cls.policy),
            "scope": {"action": "repair_edit" if dual else "read", "domain": "controller" if dual else "artifact",
                      "triggers": [], "classification_evidence": proof.sha(b"owner-authored-classification"),
                      "non_material_rationale": "Read-only authored arithmetic task." if not dual else ""},
            "workers": {role: {"worker_id": role + "-worker", "principal_id": role + "-principal",
                "lineage_id": role + "-lineage", "source_sha256": proof.sha(source)} for role, source in sources.items()},
            "spec": proof.blob(proof.canonical({"numbers": [9, -3, 11, 0]}))}

    @classmethod
    def retain(cls, name, raw):
        # This controller-owned record is outside every supplied worker packet.
        path = cls.controller / (name + ".json")
        with path.open("xb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        cls.pins[name] = proof.sha(raw)
        return cls.pins[name]

    @classmethod
    def capture(cls, name, dual=False, sources=None, retain=None, timeout=10):
        sources = sources or {"generator": GENERATOR, "verifier": VERIFIER, **({"red": RED} if dual else {})}
        assignment = cls.assignment(name, dual, sources)
        result = observer.capture_assignment(assignment, sources, executable=cls.executable,
            capture_directory=cls.root / name, retain_anchor=retain or (lambda raw: cls.retain(name, raw)),
            process_timeout_seconds=timeout)
        bundle = Path(result["bundle_path"]).read_bytes()
        anchor = (cls.controller / (name + ".json")).read_bytes()
        return bundle, anchor, cls.pins[name]

    def evaluate(self, capture, **overrides):
        raw, anchor, expected = capture
        fields = {"expected_anchor_sha256": expected,
            "expected_assignment_id": proof.document(anchor)["assignment_id"],
            "expected_scope_sha256": proof.sha(b"authored-local-proof-scope"),
            "expected_controller_reference": proof.sha(b"independently-retained-controller-reference"),
            "now_ns": time.time_ns()}
        fields.update(overrides)
        return proof.evaluate_capture(raw, anchor, **fields)

    def authored(self, transform, capture=None):
        """Explicit authored record mutation; this is not native execution evidence."""
        raw, anchor_raw, _ = capture or self.routine
        bundle, anchor = proof.document(raw), proof.document(anchor_raw)
        transform(bundle)
        raw = proof.canonical(bundle)
        anchor["bundle_sha256"] = proof.sha(raw)
        anchor["assignment_sha256"] = proof.sha(proof.canonical(bundle["assignment"]))
        anchor_raw = proof.canonical(anchor)
        return raw, anchor_raw, proof.sha(anchor_raw)

    def rejected(self, capture, reason, **changes):
        result = self.evaluate(capture, **changes)
        self.assertFalse(result["component_verified"], result)
        self.assertEqual(result["reason_codes"], [reason])
        self.assertFalse(result["execution_authorized"])

    def test_native_routine_and_dual_capture_reopen_against_controller_anchors(self):
        for capture, roles in ((self.routine, ["generator", "verifier"]), (self.dual, ["generator", "verifier", "red"])):
            with self.subTest(roles=roles):
                result = self.evaluate(capture)
                self.assertTrue(result["component_verified"], result)
                self.assertEqual(result["verified_roles"], roles)
                self.assertFalse(result["operational_acceptance"])
                self.assertFalse(result["integration_authorized"])
                self.assertFalse(result["usage_settlement_authorized"])
                observations = proof.document(capture[0])["observations"]
                self.assertEqual(len({o["pid"] for o in observations}), len(roles))

    def test_actual_reviewer_packets_exclude_generator_and_other_review_artifacts(self):
        bundle = proof.document(self.dual[0])
        for observation in bundle["observations"][1:]:
            packet = proof.document(proof.unblob(observation["packet"]))
            self.assertEqual([row["name"] for row in packet["inputs"]], ["spec", "candidate"])
            self.assertNotIn("findings", packet)
            self.assertNotIn("decision", packet)

    def test_worker_tampering_cannot_replace_the_independently_retained_anchor(self):
        changed = self.authored(lambda b: b.update(complete=False))
        self.rejected((changed[0], changed[1], self.routine[2]), "controller_anchor_mismatch")
        self.rejected((changed[0], self.routine[1], self.routine[2]), "capture_digest_mismatch")
        self.rejected(self.routine, "trusted_anchor_required", expected_anchor_sha256=None)

    def test_assignment_scope_and_controller_mismatch_reject(self):
        for key, value in (("expected_assignment_id", "different"),
                           ("expected_scope_sha256", proof.sha(b"different")),
                           ("expected_controller_reference", proof.sha(b"different"))):
            with self.subTest(key=key):
                self.rejected(self.routine, "anchor_assignment_mismatch", **{key: value})

    def test_partial_missing_and_stale_captures_reject(self):
        self.rejected(self.authored(lambda b: b.update(complete=False)), "incomplete_capture")
        self.rejected(self.authored(lambda b: b["observations"].pop()), "incomplete_capture")
        deadline = proof.document(self.routine[0])["assignment"]["not_after_ns"]
        self.rejected(self.routine, "capture_stale", now_ns=deadline)

    def test_self_verification_aliases_and_same_source_are_rejected(self):
        for field in ("worker_id", "principal_id", "lineage_id", "source_sha256"):
            def mutate(bundle):
                workers = bundle["assignment"]["workers"]
                workers["verifier"][field] = workers["generator"][field]
            with self.subTest(field=field):
                self.rejected(self.authored(mutate), "worker_lineage_not_independent")

    def test_caller_independence_and_fresh_context_flags_create_no_authority(self):
        for flag in ("independent", "fresh_context", "verified"):
            with self.subTest(flag=flag):
                self.rejected(self.authored(lambda b: b["observations"][1].update({flag: True})), "observation_schema")

    def test_context_membership_and_exact_candidate_are_verified(self):
        def contaminate(bundle):
            observation = bundle["observations"][1]
            packet = proof.document(proof.unblob(observation["packet"]))
            packet["inputs"].append({"name": "prior-review", "content": proof.blob(b"DECISION: PASS")})
            observation["packet"] = proof.blob(proof.canonical(packet))
        self.rejected(self.authored(contaminate), "context_membership_mismatch")
        self.rejected(self.authored(lambda b: b.update(candidate=proof.blob(b"999"))), "generated_candidate_mismatch")

    def test_unknown_worker_source_runtime_invocation_and_identity_reject(self):
        mutations = [
            (lambda b: b["observations"][1].update(source=proof.blob(b"different")), "observed_source_mismatch"),
            (lambda b: b["observations"][1].update(executable_sha256=proof.sha(b"different")), "observed_source_mismatch"),
            (lambda b: b["observations"][1].update(worker_id="impostor"), "observed_worker_mismatch"),
            (lambda b: b["observations"][1]["argv"].__setitem__(1, "-O"), "observed_invocation_mismatch"),
            (lambda b: b["observations"][1].update(environment={"CONTEXT": "prior-review"}), "observed_environment_mismatch")]
        for mutate, reason in mutations:
            with self.subTest(reason=reason):
                self.rejected(self.authored(mutate), reason)

    def test_reused_run_and_backward_execution_order_reject(self):
        self.rejected(self.authored(lambda b: b["observations"][1].update(run_id=b["observations"][0]["run_id"])),
                      "observed_execution_reused")
        self.rejected(self.authored(lambda b: b["observations"][1].update(started_ns=b["assignment"]["created_ns"])),
                      "observed_execution_order")

    def test_control_and_publication_risk_floor_cannot_be_lowered_by_empty_triggers(self):
        for change in ({"domain": "controller"}, {"domain": "security"}, {"action": "recovery_publish"}):
            with self.subTest(change=change):
                self.rejected(self.authored(lambda b: b["assignment"]["scope"].update(change)), "required_worker_roles")
        self.rejected(self.authored(lambda b: b["assignment"]["scope"].update(classification_evidence=None)),
                      "classification_evidence_missing")

    def test_missing_and_nonzero_deterministic_checks_reject(self):
        for nonzero in (False, True):
            def mutate(bundle):
                row = bundle["observations"][1]
                result = proof.document(proof.unblob(row["stdout"]))
                key = next(iter(result["checks"]))
                if nonzero:
                    result["checks"][key] = 1
                else:
                    del result["checks"][key]
                row["stdout"] = proof.blob(proof.canonical(result))
            self.rejected(self.authored(mutate), "deterministic_check_failed" if nonzero else "required_checks_missing")

    def test_negative_ambiguous_and_wrong_kind_reviews_block_acceptance(self):
        for decision, reason in (("DECISION: REVISION_REQUIRED", "required_review_negative"),
                                  ("DECISION: PASS\nDECISION: REVISION_REQUIRED", "invalid_review_verdict"),
                                  ("STATUS: COMPLETE", "invalid_review_verdict")):
            def mutate(bundle):
                row = bundle["observations"][2]
                result = proof.document(proof.unblob(row["stdout"]))
                result["decision"] = decision
                row["stdout"] = proof.blob(proof.canonical(result))
            self.rejected(self.authored(mutate, self.dual), reason)

    def test_critical_high_findings_cannot_clear_themselves_with_resolved_flag(self):
        for severity in ("critical", "high"):
            for resolved in (False, True):
                def mutate(bundle):
                    row = bundle["observations"][1]
                    result = proof.document(proof.unblob(row["stdout"]))
                    result["findings"] = [{"finding_id": "issue-1", "severity": severity, "resolved": resolved}]
                    row["stdout"] = proof.blob(proof.canonical(result))
                self.rejected(self.authored(mutate), "blocking_finding_requires_resolution")

    def test_native_wrong_generated_result_is_independently_rejected(self):
        bad = GENERATOR.replace(b"str(sum(s['numbers']))", b"str(sum(s['numbers'])+1)")
        with self.assertRaisesRegex(proof.ProvenanceError, "required_review_negative"):
            self.capture("native-wrong-result", sources={"generator": bad, "verifier": VERIFIER})
        self.assertFalse((self.controller / "native-wrong-result.json").exists())
        partial = proof.document((self.root / "native-wrong-result/partial.json").read_bytes())
        self.assertEqual(len(partial["observations"]), 2)

    def test_native_timeout_and_output_limit_leave_incomplete_unanchored_capture(self):
        for name, source in (("timeout", b"import time; time.sleep(2)"),
                             ("oversize", b"import sys; sys.stdin.buffer.read(); sys.stdout.write('x'*200000)")):
            with self.subTest(name=name):
                with self.assertRaisesRegex(proof.ProvenanceError, "execution_incomplete"):
                    self.capture("native-" + name, sources={"generator": source, "verifier": VERIFIER},
                                 timeout=0.1 if name == "timeout" else 10)
                self.assertFalse((self.controller / ("native-" + name + ".json")).exists())
                partial = proof.document((self.root / ("native-" + name) / "partial.json").read_bytes())
                self.assertFalse(partial["complete"])
                self.assertEqual(len(partial["observations"]), 1)
                self.assertTrue(partial["observations"][0]["timed_out" if name == "timeout" else "output_truncated"])

    def test_anchor_failure_and_lost_response_never_authorize_redispatch(self):
        def missing(raw):
            raise RuntimeError("before controller anchor")
        with self.assertRaisesRegex(RuntimeError, "before controller anchor"):
            self.capture("before-anchor", retain=missing)
        self.assertTrue((self.root / "before-anchor/bundle.json").exists())
        self.assertFalse((self.controller / "before-anchor.json").exists())
        with self.assertRaises(FileExistsError):
            self.capture("before-anchor")
        def lost(raw):
            self.retain("lost-anchor-response", raw)
            raise RuntimeError("lost controller response")
        with self.assertRaisesRegex(RuntimeError, "lost controller response"):
            self.capture("lost-anchor-response", retain=lost)
        captured = ((self.root / "lost-anchor-response/bundle.json").read_bytes(),
            (self.controller / "lost-anchor-response.json").read_bytes(), self.pins["lost-anchor-response"])
        self.assertTrue(self.evaluate(captured)["component_verified"])
        with self.assertRaises(FileExistsError):
            self.capture("lost-anchor-response")

    def test_live_model_requirement_never_silently_falls_back_to_local_process(self):
        def require_model(bundle):
            bundle["assignment"]["policy"]["live_model_required"] = True
            candidate = proof.unblob(bundle["candidate"])
            for row in bundle["observations"]:
                row["packet"] = proof.blob(proof.packet_for(bundle["assignment"], row["role"], candidate))
        self.rejected(self.authored(require_model), "live_model_provenance_unavailable")
        assignment = self.assignment("closed-model")
        assignment["policy"]["live_model_required"] = True
        with self.assertRaisesRegex(proof.ProvenanceError, "live_model_provenance_unavailable"):
            observer.capture_assignment(assignment, {"generator": GENERATOR, "verifier": VERIFIER},
                executable=self.executable, capture_directory=self.root / "closed-model", retain_anchor=lambda raw: None)
        self.assertFalse((self.root / "closed-model").exists())

    def test_changed_source_and_malformed_or_noncanonical_records_reject(self):
        assignment = self.assignment("source-changed")
        with self.assertRaisesRegex(proof.ProvenanceError, "unreviewed_worker_source"):
            observer.capture_assignment(assignment, {"generator": GENERATOR + b"#changed", "verifier": VERIFIER},
                executable=self.executable, capture_directory=self.root / "source-changed", retain_anchor=lambda raw: None)
        self.assertFalse((self.root / "source-changed").exists())
        with self.assertRaisesRegex(proof.ProvenanceError, "duplicate_record_key"):
            proof.document(b'{"x":1,"x":2}')
        with self.assertRaisesRegex(proof.ProvenanceError, "record_not_canonical"):
            proof.document(b'{ "x": 1 }')
