"""Authored synthetic P1-P4/D1-D3 point bridge sources; not execution evidence.

D4 remains separately admitted server verification: existing move endpoint owns
DST nonexistent/ambiguous times, conflict/break/temporal guards, source races and
staff confirmation. These tests do not establish those server runtime results.
"""
import copy
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import uuid

from scripts import reception_one_bureau_typed_plan_protocol as protocol
from app.services import reception_one_proposal_runtime as runtime
from app.services.appointment_lifecycle import LifecycleRejected, validate_move_intent
from app.routers import appointments as routes

NOW = datetime(2026, 11, 1, 23, 1, tzinfo=timezone.utc)
TENANT, ACTOR, APPOINTMENT, PATIENT, PRACTITIONER = [str(uuid.UUID(int=n)) for n in range(1, 6)]


def point_frame():
    selected = {"id": "synthetic-appointment-selected", "patient_ref": "synthetic-patient-selected",
                "practitioner_ref": "synthetic-practitioner-selected", "date": "2026-11-03",
                "start_time": "14:00", "duration_minutes": 30, "status": "booked"}
    return {
        "contract_version": "reception.one.bureau.plan-input.v1", "request_id": "synthetic-request-point",
        "practice_ref": "synthetic-practice-point", "correlation_id": "synthetic-correlation-point",
        "context_revision": 7, "observed_at": "2026-11-01T23:00:00Z", "expires_at": "2026-11-01T23:02:00Z",
        "data_class": "authored_synthetic", "utterances": ["Move this appointment to 2026-11-05 at 15:00."],
        "reference_date": "2026-11-02", "context": {
            "patients": [{"id": selected["patient_ref"], "display": "Morgan Bell", "aliases": ["Morgan"]}],
            "practitioners": [{"id": selected["practitioner_ref"], "display": "Dr Lee", "aliases": ["Lee"]}],
            "selected_appointment": selected, "appointments": [copy.deepcopy(selected)], "candidate_slots": [],
            "squeeze_policy": {"id": "synthetic-policy-point", "assessment_enabled": True,
                "allow_move_existing": False, "allow_overbook": False, "requires_human_review": True},
            "default_duration_minutes": 15, "allowed_statuses": ["arrived", "completed", "dna"]},
        "authority": {"effect_ceiling": "proposal_only", "appointment_write_authority": False,
            "confirmation_authority": False, "provider_execution": False, "network_access": False,
            "database_access": False, "product_delivery": False}}


def candidate(row, field, value, text, identifier=None, supersedes=()):
    start = row["utterances"][0].index(text)
    return {"id": identifier or "candidate-" + field.replace("_", "-"), "field": field, "value": value,
            "evidence": {"utterance_index": 0, "start": start, "end": start + len(text), "text": text},
            "supersedes": list(supersedes)}


def point_packet(row):
    candidates = [candidate(row, "intended_action", "move", "Move"),
                  candidate(row, "appointment_date", "2026-11-05", "2026-11-05"),
                  candidate(row, "target_start_local", "15:00", "15:00")]
    return {"packet_schema": protocol.POINT_PACKET_VERSION, "case_id": "authored-point",
            "interpretation": {"frame_sha256": protocol.canonical_sha256(row), "context_revision": row["context_revision"],
                "reference_date": row["reference_date"], "candidates": candidates,
                "selected": {item["field"]: item["id"] for item in candidates}},
            "target_bindings": {"appointment": {"kind": "context_ref", "field": "selected_appointment"},
                "patient_for_selected_appointment": {"kind": "context_ref", "field": "selected_appointment.patient_ref"}}}


def compiled(row, packet=None):
    packet = point_packet(row) if packet is None else packet
    built = protocol.compile_model_semantic_packet(row, protocol.canonical_json(packet).encode(),
        case_id=packet["case_id"], now=NOW)
    built["execution"] = protocol.execute_plan(row, built["plan"], built["review"], now=NOW)
    return built


def captured_context():
    return {"tenant_id": TENANT, "actor_id": ACTOR, "role": "reception", "move_capability": "appointments.move.propose",
        "source_revision": 12, "selected_appointment_id": APPOINTMENT, "selected_state_version": 12,
        "selected_status": "Booked", "selected_date": "2026-11-03", "selected_start_local": "14:00",
        "patient_id": PATIENT, "practitioner_id": PRACTITIONER, "appointment_type_id": None, "location_id": None,
        "duration_minutes": 30, "practice_timezone": "Australia/Brisbane", "captured_at": "2026-11-01T23:00:00Z",
        "as_of": "2026-11-01T23:00:00Z"}


def capture(row, context=None, **overrides):
    values = dict(frame_sha256=protocol.canonical_sha256(row), request_id=row["request_id"],
                  selected_handle=row["context"]["selected_appointment"]["id"],
                  context_items=tuple(sorted((context or captured_context()).items())))
    values.update(overrides)
    return runtime.SelectedMoveSource(**values)


def join_args(row, built):
    return dict(frame=row, normalized_plan=built["plan"], review=built["review"], execution=built["execution"],
                provenance=built["provenance"], capture=capture(row), tenant_id=TENANT, actor_id=ACTOR,
                selected_appointment_id=APPOINTMENT, now=NOW)


class PointProtocolTests(unittest.TestCase):
    def test_P1_exact_two_steps_empty_slots_and_observed_duration(self):
        for default in (5, 90):
            row = point_frame()
            row["context"]["default_duration_minutes"] = default
            built = compiled(row)
            self.assertEqual([s["operator"] for s in built["plan"]["steps"]],
                             ["read_selected_appointment", "prepare_point_move_proposal"])
            output = built["execution"]["final_output"]
            self.assertEqual((output["target_date"], output["target_start_local"], output["duration_minutes"]),
                             ("2026-11-05", "15:00", 30))
            self.assertEqual(output["candidate_slot_ids"], [])
            self.assertFalse(output["write_performed"])
            self.assertTrue(output["requires_human_confirmation"])
            self.assertFalse(set(output) & {"latest_time", "earliest_time", "end", "target_end", "start_time"})
            self.assertEqual(built["review"]["safe_repairs"], [])

    def test_P2_strict_evidence_values_selection_and_surplus_fields_refuse(self):
        mutations = [
            lambda p: p["interpretation"]["candidates"][2].update(value="24:00"),
            lambda p: p["interpretation"]["candidates"][2].update(value=True),
            lambda p: p["interpretation"]["candidates"][1].update(value="2026-02-30"),
            lambda p: p["interpretation"]["candidates"][2]["evidence"].update(text="invented"),
            lambda p: p["interpretation"]["selected"].pop("target_start_local"),
            lambda p: p["target_bindings"]["appointment"].update(field="other_appointment"),
        ]
        for mutate in mutations:
            row = point_frame(); packet = point_packet(row); mutate(packet)
            with self.subTest(packet=packet), self.assertRaises(protocol.SemanticPacketRefusal):
                compiled(row, packet)
        for field, value in (("earliest_time", "15:00"), ("latest_time", "15:00"), ("duration_minutes", 45)):
            row = point_frame(); packet = point_packet(row)
            extra = candidate(row, field, value, "15:00")
            packet["interpretation"]["candidates"].append(extra)
            packet["interpretation"]["selected"][field] = extra["id"]
            with self.subTest(field=field), self.assertRaises(protocol.SemanticPacketRefusal):
                compiled(row, packet)

    def test_P2_chronological_same_field_supersession_only(self):
        row = point_frame(); row["utterances"][0] += " Rather 16:00."
        packet = point_packet(row); prior = packet["interpretation"]["candidates"][2]
        later = candidate(row, "target_start_local", "16:00", "16:00", "candidate-later", [prior["id"]])
        packet["interpretation"]["candidates"].append(later)
        packet["interpretation"]["selected"]["target_start_local"] = later["id"]
        self.assertEqual(compiled(row, packet)["execution"]["final_output"]["target_start_local"], "16:00")
        for supersedes in ([], [packet["interpretation"]["candidates"][1]["id"]]):
            changed = copy.deepcopy(packet); changed["interpretation"]["candidates"][-1]["supersedes"] = supersedes
            with self.assertRaises(protocol.SemanticPacketRefusal): compiled(row, changed)
        changed = copy.deepcopy(packet)
        changed["interpretation"]["candidates"][2]["supersedes"] = [later["id"]]
        with self.assertRaises(protocol.SemanticPacketRefusal): compiled(row, changed)

    def test_P3_selected_identity_scope_authority_and_wrong_same_type_binding_refuse(self):
        for kind in ("patients", "practitioners"):
            for duplicate in (False, True):
                row = point_frame()
                row["context"][kind] = row["context"][kind] * 2 if duplicate else []
                with self.subTest(kind=kind, duplicate=duplicate), self.assertRaises(protocol.SemanticPacketRefusal): compiled(row)
        row = point_frame(); built = compiled(row)
        mutations = [lambda p: p.update(practice_ref="synthetic-practice-foreign"),
                     lambda p: p.update(effect_ceiling="confirmed_write"),
                     lambda p: p["steps"][-1].update(operator="confirm_appointment"),
                     lambda p: p["steps"][-1]["args"].update(target_start_local={"kind": "semantic_ref", "field": "appointment_date"}),
                     lambda p: p["steps"][-1]["args"].update(appointment={"kind": "context_ref", "field": "selected_appointment"})]
        for mutate in mutations:
            changed = copy.deepcopy(built["plan"]); mutate(changed)
            review, _ = protocol.proofread_plan(row, changed, now=NOW)
            self.assertNotEqual(review["disposition"], "admit")

    def test_P4_v2_point_fields_never_reclassified(self):
        row = point_frame(); packet = point_packet(row)
        packet["packet_schema"] = protocol.SEMANTIC_PACKET_VERSION
        with self.assertRaises(protocol.SemanticPacketRefusal): compiled(row, packet)
        # Existing model-first tests retain window/resize/cancel/clarification,
        # full original evidence and frozen v2 earliest-only refusal assertions.


class PointJoinTests(unittest.TestCase):
    def test_D1_closed_envelope_and_empty_slots(self):
        row = point_frame(); built = compiled(row)
        envelope = runtime.point_move_envelope(**join_args(row, built))
        self.assertEqual(set(envelope), {"schema_version", "tenant_id", "actor_id", "role", "source_appointment_id",
            "source_state_version", "source_revision", "target_date", "target_start_local", "authority"})
        self.assertEqual((envelope["source_state_version"], envelope["source_revision"]), (12, 12))
        self.assertEqual((envelope["target_date"], envelope["target_start_local"]), ("2026-11-05", "15:00"))
        self.assertEqual(validate_move_intent(envelope, {**captured_context(), "as_of": "2026-11-01T23:01:00Z"}).duration_minutes, 30)

    def test_JOIN1_final_frame_plan_review_output_provenance_and_handle_mismatch_refuse(self):
        row = point_frame(); built = compiled(row); base = join_args(row, built)
        variants = []
        for key in ("frame_sha256", "compiled_plan_sha256", "raw_response_sha256", "packet_sha256"):
            args = copy.deepcopy(base); args["provenance"][key] = "0" * 64 if key not in {"raw_response_sha256", "packet_sha256"} else "invalid"
            variants.append(args)
        for key in ("target_date", "target_start_local", "appointment_ref", "duration_minutes"):
            args = copy.deepcopy(base)
            args["execution"]["final_output"][key] = {"target_date": "2026-11-06", "target_start_local": "16:00",
                "appointment_ref": "synthetic-appointment-other", "duration_minutes": 45}[key]
            variants.append(args)
        args = copy.deepcopy(base); args["review"]["normalized_plan_sha256"] = "0" * 64; variants.append(args)
        args = copy.deepcopy(base); args["frame"]["request_id"] = "synthetic-request-first"; variants.append(args)
        args = copy.deepcopy(base); args["capture"] = capture(row, selected_handle="synthetic-appointment-other"); variants.append(args)
        args = copy.deepcopy(base); args["capture"] = capture(row, frame_sha256="0" * 64); variants.append(args)
        args = copy.deepcopy(base); args["now"] = NOW + timedelta(minutes=2); variants.append(args)
        for args in variants:
            with self.subTest(args=args), self.assertRaises(ValueError): runtime.point_move_envelope(**args)

    def test_D2_JOIN3_closed_context_actual_duration_scope_age_and_version_refuse(self):
        row = point_frame(); built = compiled(row); base = join_args(row, built)
        args = dict(base, capture=None)
        with self.assertRaises(ValueError): runtime.point_move_envelope(**args)
        changes = [{"unexpected": "closed"}, {"duration_minutes": True}, {"duration_minutes": 15},
                   {"duration_minutes": 0}, {"source_revision": 7}, {"selected_state_version": True},
                   {"tenant_id": ACTOR}, {"actor_id": TENANT},
                   {"captured_at": "2026-11-01T22:55:59Z"}, {"captured_at": "2026-11-01T23:01:01Z"}]
        for change in changes:
            args = dict(base, capture=capture(row, {**captured_context(), **change}))
            with self.subTest(change=change), self.assertRaises(ValueError): runtime.point_move_envelope(**args)
        args = dict(base, selected_appointment_id=PATIENT)
        with self.assertRaises(ValueError): runtime.point_move_envelope(**args)

    def test_D3_existing_closed_validator_rejections_retained(self):
        row = point_frame(); built = compiled(row)
        envelope = runtime.point_move_envelope(**join_args(row, built))
        for context_change, intent_change, code in [
            ({"tenant_id": ACTOR}, {}, "SCOPE_MISMATCH"),
            ({"selected_state_version": 13}, {}, "REVISION_MISMATCH"),
            ({"as_of": "2026-11-01T23:05:01Z"}, {}, "SOURCE_STALE"),
            ({"selected_status": "Arrived"}, {}, "STATUS_NOT_MOVABLE"),
            ({"practice_timezone": "UTC"}, {}, "TIMEZONE_UNSUPPORTED"),
            ({}, {"target_date": "2026-11-03", "target_start_local": "14:00"}, "NO_CHANGE"),
            ({}, {"authority": "confirmed_write"}, "AUTHORITY_INVALID"),
            ({}, {"source_state_version": True}, "REVISION_MISMATCH"),
            ({"extra": 1}, {}, "STRUCTURE_INVALID"),
        ]:
            with self.subTest(code=code), self.assertRaises(LifecycleRejected) as caught:
                validate_move_intent({**envelope, **intent_change}, {**captured_context(), **context_change})
            self.assertEqual(caught.exception.code, code)

    def test_D1_JOIN2_dispatch_calls_existing_endpoint_without_slot_loop_or_capability_leak(self):
        row = point_frame(); built = compiled(row)
        user = SimpleNamespace(id=uuid.UUID(ACTOR), practice_id=uuid.UUID(TENANT))
        proposal = SimpleNamespace(safe=True, warnings=[], blocks=[], update_proposal_freshness_id="fresh",
            signed_confirmation_evidence={"secret": "never release"}, move_binding={"secret": "never release"},
            confirm_payload={"secret": "never release"})
        class Clock:
            @staticmethod
            def now(zone): return NOW
        with patch.object(routes, "datetime", Clock), patch.object(routes, "_move_reception_user", return_value=user), \
                patch.object(routes, "propose_seeded_move_time", return_value=proposal) as endpoint, \
                patch.object(routes, "propose_update_appointment", side_effect=AssertionError("slot loop forbidden")):
            result = routes._reception_one_adapter_review(execution=built["execution"], frame=row,
                selected_appointment_id=uuid.UUID(APPOINTMENT), db=object(), current_user=user,
                normalized_plan=built["plan"], review=built["review"], selected_source_capture=capture(row),
                semantic_provenance=built["provenance"])
        self.assertTrue(result.safe); self.assertEqual(result.candidate_count, 1)
        endpoint.assert_called_once()
        body = endpoint.call_args.kwargs["body"].model_dump(mode="json")
        self.assertEqual(body, runtime.point_move_envelope(**join_args(row, built)))
        released = protocol.canonical_json(result.model_dump(mode="json"))
        for secret in ("signed_confirmation_evidence", "move_binding", "confirm_payload", "never release"):
            self.assertNotIn(secret, released)

    def test_D2_current_version_race_is_rejected_by_existing_validator_before_release(self):
        row = point_frame(); built = compiled(row)
        user = SimpleNamespace(id=uuid.UUID(ACTOR), practice_id=uuid.UUID(TENANT))
        class Clock:
            @staticmethod
            def now(zone): return NOW
        def current_source_endpoint(**kwargs):
            # Synthetic endpoint collaborator preserves the actual pure version
            # guard. This is not evidence of an application/database race run.
            context = {**captured_context(), "source_revision": 13, "selected_state_version": 13,
                       "as_of": "2026-11-01T23:01:00Z"}
            return validate_move_intent(kwargs["body"].model_dump(mode="json"), context)
        with patch.object(routes, "datetime", Clock), patch.object(routes, "_move_reception_user", return_value=user), \
                patch.object(routes, "propose_seeded_move_time", side_effect=current_source_endpoint) as endpoint:
            result = routes._reception_one_adapter_review(execution=built["execution"], frame=row,
                selected_appointment_id=uuid.UUID(APPOINTMENT), db=object(), current_user=user,
                normalized_plan=built["plan"], review=built["review"], selected_source_capture=capture(row),
                semantic_provenance=built["provenance"])
        endpoint.assert_called_once(); self.assertFalse(result.safe)
        self.assertEqual(result.block_codes, ["point_move_review_refused"])

    def test_absent_live_provenance_refuses_without_endpoint(self):
        row = point_frame(); built = compiled(row)
        user = SimpleNamespace(id=uuid.UUID(ACTOR), practice_id=uuid.UUID(TENANT))
        with patch.object(routes, "_move_reception_user", return_value=user), \
                patch.object(routes, "propose_seeded_move_time") as endpoint:
            result = routes._reception_one_adapter_review(execution=built["execution"], frame=row,
                selected_appointment_id=uuid.UUID(APPOINTMENT), db=object(), current_user=user,
                normalized_plan=built["plan"], review=built["review"], selected_source_capture=capture(row))
        self.assertFalse(result.safe); endpoint.assert_not_called()




class ModelReplyCarrierContractTests(unittest.TestCase):
    """Unexecuted authored-synthetic receive-boundary sources, not live proof."""
    def received(self, row=None, packet=None, *, raw=None, now=NOW):
        from app.services import reception_one_isolated_vertex_planner as planner
        row = point_frame() if row is None else row
        packet = point_packet(row) if packet is None else packet
        packet = copy.deepcopy(packet)
        packet["case_id"] = row["request_id"]
        raw = (b" \n" + protocol.canonical_json(packet).encode("utf-8") + b"\n ") if raw is None else raw
        result = planner.compile_received_model_reply(
            frame=row, raw_response=raw,
            frame_observed_at=datetime.fromisoformat(row["observed_at"].replace("Z", "+00:00")),
            received_at=now,
        )
        return row, raw, result

    def test_actual_received_bytes_hash_not_reserialized_plan_or_packet(self):
        import hashlib
        row, raw, result = self.received()
        provenance = result.semantic_provenance
        self.assertEqual(provenance["raw_response_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertNotEqual(provenance["raw_response_sha256"], provenance["packet_sha256"])
        self.assertEqual(provenance["frame_sha256"], protocol.canonical_sha256(row))
        self.assertEqual(provenance["compiled_plan_sha256"], protocol.canonical_sha256(result.normalized_plan))
        self.assertEqual(result.provider_calls, 0)
        self.assertEqual(result.runtime_audit_ref, "contract-only-unwired")
        self.assertNotIn(raw.decode(), repr(result))
        output = result.final_output
        self.assertEqual((output["appointment_ref"], output["target_date"], output["target_start_local"], output["duration_minutes"]),
                         (row["context"]["selected_appointment"]["id"], "2026-11-05", "15:00", 30))
        self.assertTrue(output["requires_human_confirmation"])
        self.assertFalse(output["write_performed"])
        envelope = runtime.point_move_envelope(
            frame=row, normalized_plan=result.normalized_plan, review=result.review,
            execution={"final_output": output}, provenance=provenance, capture=capture(row),
            tenant_id=TENANT, actor_id=ACTOR, selected_appointment_id=APPOINTMENT, now=NOW,
        )
        self.assertEqual(envelope["authority"], "proposal_only")

    def test_reply_frame_context_case_extra_operator_and_refusal_fail_closed(self):
        from app.services import reception_one_isolated_vertex_planner as planner
        for mutation in (lambda p: p["interpretation"].update(frame_sha256="0" * 64),
                         lambda p: p["interpretation"].update(context_revision=8),
                         lambda p: p.update(steps=[{"operator": "confirm_appointment"}]),
                         lambda p: p.update(case_id="synthetic-other-request")):
            row = point_frame(); packet = point_packet(row); packet["case_id"] = row["request_id"]; mutation(packet)
            raw = protocol.canonical_json(packet).encode("utf-8")
            with self.assertRaises(planner.IsolatedVertexPlannerError): self.received(row, raw=raw)
        for raw in (b'not-json', b'{"refusal":"no"}', b'{"case_id":1,"case_id":2}', bytearray(b'{}')):
            with self.assertRaises(planner.IsolatedVertexPlannerError): self.received(raw=raw)
        with self.assertRaises(planner.IsolatedVertexPlannerError): self.received(now=NOW + timedelta(minutes=5))

    def test_consumed_receipt_raw_hash_and_plan_tampering_refuse(self):
        from dataclasses import replace
        from app.services import reception_one_isolated_vertex_planner as planner
        _, raw, result = self.received()
        changed = replace(result, _model_reply_receipt=replace(result._model_reply_receipt, raw_response=raw + b" "))
        with self.assertRaises(planner.IsolatedVertexPlannerError): _ = changed.semantic_provenance
        changed = copy.deepcopy(result); changed.normalized_plan["context_revision"] += 1
        with self.assertRaises(planner.IsolatedVertexPlannerError): _ = changed.semantic_provenance
        provenance = result.semantic_provenance; provenance["raw_response_sha256"] = "0" * 64
        self.assertNotEqual(result.semantic_provenance["raw_response_sha256"], provenance["raw_response_sha256"])

    def test_packet_hash_only_and_paired_raw_hash_replacement_refuse(self):
        import hashlib
        from dataclasses import replace
        from app.services import reception_one_isolated_vertex_planner as planner
        _, _, result = self.received()
        receipt = result._model_reply_receipt
        packet_only = dict(receipt.provenance_items)
        packet_only["packet_sha256"] = "0" * 64
        changed = replace(result, _model_reply_receipt=replace(
            receipt, provenance_items=tuple(sorted(packet_only.items())),
        ))
        with self.assertRaisesRegex(planner.IsolatedVertexPlannerError, "^isolated_model_reply_join_invalid$"):
            _ = changed.semantic_provenance
        # Paired bytes + matching raw hash bypassed v1's hash-only check. The
        # existing compiler must now reject this substituted nonpacket response.
        replacement_raw = b'{}'
        paired = dict(receipt.provenance_items)
        paired["raw_response_sha256"] = hashlib.sha256(replacement_raw).hexdigest()
        changed = replace(result, _model_reply_receipt=replace(
            receipt, raw_response=replacement_raw,
            provenance_items=tuple(sorted(paired.items())),
        ))
        with self.assertRaisesRegex(planner.IsolatedVertexPlannerError, "^isolated_model_reply_join_invalid$"):
            _ = changed.semantic_provenance

    def test_selected_source_version_duration_and_final_frame_still_refuse(self):
        row, _, result = self.received()
        for context in ({**captured_context(), "selected_state_version": 13},
                        {**captured_context(), "duration_minutes": 45}):
            with self.assertRaises(runtime.ReceptionOneRuntimeError):
                runtime.point_move_envelope(
                    frame=row, normalized_plan=result.normalized_plan, review=result.review,
                    execution={"final_output": result.final_output}, provenance=result.semantic_provenance,
                    capture=capture(row, context), tenant_id=TENANT, actor_id=ACTOR,
                    selected_appointment_id=APPOINTMENT, now=NOW,
                )
        changed = copy.deepcopy(row); changed["context_revision"] += 1
        with self.assertRaises(runtime.ReceptionOneRuntimeError):
            runtime.point_move_envelope(
                frame=changed, normalized_plan=result.normalized_plan, review=result.review,
                execution={"final_output": result.final_output}, provenance=result.semantic_provenance,
                capture=capture(row), tenant_id=TENANT, actor_id=ACTOR,
                selected_appointment_id=APPOINTMENT, now=NOW,
            )


if __name__ == "__main__":
    unittest.main()
