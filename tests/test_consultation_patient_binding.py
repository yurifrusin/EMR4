"""Patient-selection source-component regressions with real Pydantic validation.

Run only in a reviewed literal-file capsule. Route bodies are unchanged except
for removing decorators/type annotations/default dependency objects at extraction;
HTTP authentication, SQLAlchemy/PostgreSQL and provider adapters are not exercised.
This is not full application, cross-tenant or clinician-attestation acceptance.
"""
import ast
import asyncio
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List, Literal, Optional
import unittest
from urllib.parse import urlsplit
import uuid

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StrictStr,
    ValidationError,
    field_validator,
    model_validator,
)


class HTTPException(Exception):
    """Authored exception shape for isolated source execution; HTTP is not exercised."""

    def __init__(self, *, status_code, detail):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


status = SimpleNamespace(HTTP_403_FORBIDDEN=403, HTTP_409_CONFLICT=409)


SOURCE = Path(__file__).resolve().parents[1] / "app/routers/consultation.py"
COMMAND_ID = uuid.UUID("10000000-0000-4000-8000-000000000001")
DOCUMENT_CONTEXT = "https://synthetic.invalid/patient-a/fictional.docx?view=exact#context"
PATIENT_A = uuid.UUID("00000000-0000-4000-8000-000000000001")
PATIENT_B = uuid.UUID("00000000-0000-4000-8000-000000000002")
PRACTICE_A = uuid.UUID("00000000-0000-4000-8000-000000000011")
PRACTICE_B = uuid.UUID("00000000-0000-4000-8000-000000000012")
MISSING = object()


def schemas():
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    class_names = {
        "OverrideData",
        "ConsultationPayload",
        "FinalizeMbsItem",
        "FinalizeDiagnosis",
        "FinalizeMedication",
        "FinalizeOverrideData",
        "FinalizePayload",
    }
    helper_names = {
        "_same_exact_value",
        "_canonicalize_aliases",
        "_require_meaningful",
    }
    nodes = [
        node
        for node in tree.body
        if (
            isinstance(node, ast.ClassDef)
            and node.name in class_names
        ) or (
            isinstance(node, ast.FunctionDef)
            and node.name in helper_names
        )
    ]
    assert {node.name for node in nodes if isinstance(node, ast.ClassDef)} == class_names
    assert {node.name for node in nodes if isinstance(node, ast.FunctionDef)} == helper_names
    namespace = dict(
        __name__="isolated_consultation_schemas",
        BaseModel=BaseModel,
        ConfigDict=ConfigDict,
        Field=Field,
        StrictBool=StrictBool,
        StrictStr=StrictStr,
        field_validator=field_validator,
        model_validator=model_validator,
        urlsplit=urlsplit,
        uuid=uuid,
        Any=Any,
        Dict=Dict,
        List=List,
        Literal=Literal,
        Optional=Optional,
    )
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(SOURCE), "exec"), namespace)
    return namespace


def route(name, namespace):
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    node = next(n for n in tree.body if isinstance(n, ast.AsyncFunctionDef) and n.name == name)
    node.decorator_list = []
    node.returns = None
    for arg in node.args.args:
        arg.annotation = None
    node.args.defaults = []
    module = ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[]))
    exec(compile(module, str(SOURCE), "exec"), namespace)
    return namespace[name]


def forbidden(*args, **kwargs):
    raise AssertionError("Unexpected clinical write, database or provider operation")


class QueryField:
    """Authored query expression; never shadows Pydantic's real Field."""
    def __init__(self, name):
        self.name = name

    def __eq__(self, value):
        return (self.name, value)


class PatientModel:
    id = QueryField("id")
    practice_id = QueryField("practice_id")


class UserModel:
    id = QueryField("id")
    practice_id = QueryField("practice_id")


class PractitionerModel:
    id = QueryField("id")
    practice_id = QueryField("practice_id")


class AuditModel:
    event_id = QueryField("event_id")
    practice_id = QueryField("practice_id")
    event_type = QueryField("event_type")


class UserRoleModel:
    GP = SimpleNamespace(value="GP")


class PatientQuery:
    def __init__(self, rows):
        self.rows = rows
        self.conditions = None

    def filter(self, *conditions):
        self.conditions = conditions
        return self

    def with_for_update(self):
        return self

    def first(self):
        assert self.conditions is not None
        return next(
            (
                row
                for row in self.rows
                if all(getattr(row, name) == value for name, value in self.conditions)
            ),
            None,
        )


class PatientDatabase:
    def __init__(self, patients):
        practitioner_id = uuid.UUID("00000000-0000-4000-8000-000000000201")
        user_id = uuid.UUID("00000000-0000-4000-8000-000000000202")
        self.query_object = PatientQuery(patients)
        self.queries = {
            UserModel: PatientQuery([
                SimpleNamespace(
                    id=user_id,
                    practice_id=PRACTICE_A,
                    practitioner_id=practitioner_id,
                    is_active=True,
                    role=UserRoleModel.GP,
                )
            ]),
            PractitionerModel: PatientQuery([
                SimpleNamespace(
                    id=practitioner_id,
                    practice_id=PRACTICE_A,
                    is_active=True,
                )
            ]),
            PatientModel: self.query_object,
            AuditModel: PatientQuery([]),
        }
        self.current_user = SimpleNamespace(id=user_id, practice_id=PRACTICE_A)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def begin(self):
        return self

    def execute(self, *args, **kwargs):
        return None

    def query(self, model):
        return self.queries[model]

    add = commit = refresh = rollback = forbidden


def response(*, content, status_code=200):
    return SimpleNamespace(content=content, status_code=status_code)


class ConsultationPatientBindingTests(unittest.TestCase):
    def setUp(self):
        self.types = schemas()

    def finalize_payload(self, patient_id=MISSING):
        values = dict(document_id=COMMAND_ID, document_context=DOCUMENT_CONTEXT,
                      text_delta="authored synthetic notes", clinician_attested=True,
                      clinician_overrides={"consultation_type": "Reviewed synthetic consultation",
                                           "mbs_items": [{"item_number": "23"}],
                                           "diagnoses": [{
                                               "term": "synthetic",
                                               "snomed_ct_au_code": "999",
                                           }],
                                           "medications": [{"drug_name": "synthetic"}]})
        if patient_id is not MISSING:
            values["patient_id"] = patient_id
        return self.types["FinalizePayload"](**values)

    def test_finalize_requires_a_well_formed_explicit_patient_uuid(self):
        for invalid in [MISSING, None, "", "not-a-uuid", 1, False, [], {}]:
            with self.subTest(value=repr(invalid)), self.assertRaises(ValidationError):
                self.finalize_payload(invalid)

    def test_finalize_normalizes_explicit_uuid_without_a_default(self):
        payload = self.finalize_payload(str(PATIENT_A))
        self.assertEqual(payload.patient_id, PATIENT_A)
        self.assertIsInstance(payload.patient_id, uuid.UUID)
        self.assertTrue(self.types["FinalizePayload"].model_fields["patient_id"].is_required())

    def test_analysis_rejects_finalization_request(self):
        for value in [True, "true", 1]:
            with self.subTest(value=value), self.assertRaises(ValidationError):
                self.types["ConsultationPayload"](
                    document_id="authored", text_delta="synthetic notes", is_finalized=value)

    def test_analysis_accepts_only_draft_semantics(self):
        for extra in [{}, {"is_finalized": False}]:
            with self.subTest(extra=extra):
                payload = self.types["ConsultationPayload"](
                    document_id="authored", text_delta="synthetic notes", **extra)
                self.assertIs(payload.is_finalized, False)

    def test_analysis_route_has_no_clinical_write_even_without_schema_validation(self):
        async def analyze(*args):
            return SimpleNamespace(audit_events=[], raw={"_saved": True, "_save_error": "untrusted",
                                                       "encounter_metadata": {},
                                                       "clinical_diagnoses": [],
                                                       "medications_and_prescriptions": []})

        namespace = dict(_ai_service=SimpleNamespace(analyze_consultation_text=analyze),
                         _search_mbs_rules=lambda *args: "authored context",
                         ANALYSIS_PROMPT="{mbs_context}: {text}",
                         actor_context_from_user=lambda *args, **kwargs: "authored actor",
                         settings=SimpleNamespace(environment="test"),
                         _get_or_create_default_patient=forbidden, _save_encounter=forbidden,
                         persist_access_ai_audit_events=forbidden)
        analyze_route = route("analyze_consultation", namespace)
        for flag in [False, True]:
            with self.subTest(flag=flag):
                payload = SimpleNamespace(document_id="authored", text_delta="synthetic notes",
                                          is_finalized=flag, clinician_overrides=None)
                result = asyncio.run(analyze_route(payload, PatientDatabase([]),
                                                  SimpleNamespace(practice_id=PRACTICE_A)))
                self.assertNotIn("_saved", result)
                self.assertNotIn("_save_error", result)

    def finalize_route(self, payload, patients):
        saved = []
        encounter_id = uuid.UUID("00000000-0000-4000-8000-000000000101")

        def save(*args):
            saved.append(args)
            return encounter_id

        def projection(value, *, patient_id):
            overrides = value.clinician_overrides.model_dump(mode="json")
            return {
                "consultation_type": value.clinician_overrides.consultation_type,
                "document_id": str(value.document_id),
                "document_context": value.document_context,
                "text": value.text_delta,
                "overrides": overrides,
                "patient_id": str(patient_id),
            }

        database = PatientDatabase(patients)
        handler = route("finalize_consultation", dict(
            Patient=PatientModel,
            Practitioner=PractitionerModel,
            User=UserModel,
            UserRole=UserRoleModel,
            AccessAiAuditLog=AuditModel,
            _clinical_finalization_event_id=lambda *args: uuid.uuid4(),
            _effective_finalization_projection=projection,
            _reviewed_content_sha256=lambda value: "0" * 64,
            _finalization_response=lambda target, value: {
                "_saved": True,
                "encounter_id": str(target),
                "generated_clinical_note": "authored",
            },
            _validated_replay_target=forbidden,
            _save_encounter=save,
            build_access_ai_audit_event=lambda **kwargs: kwargs,
            persist_access_ai_audit_events=lambda *args: (),
            AiAuditEventType=SimpleNamespace(
                CLINICAL_CONSULTATION_ATTESTED=SimpleNamespace(value="attested")
            ),
            AiAuditSourceSurface=SimpleNamespace(API="api"),
            AiAuditDecision=SimpleNamespace(RECORDED="recorded"),
            CLINICAL_FINALIZATION_POLICY_ID="policy",
            CLINICAL_FINALIZATION_NORMALIZATION_POLICY_ID="normalization",
            _FINALIZATION_CONFLICT_CONTENT={"_saved": False},
            _FINALIZATION_SAVE_FAILURE_CONTENT={"_saved": False},
            IntegrityError=type("IntegrityError", (Exception,), {}),
            HTTPException=HTTPException,
            status=status,
            text=lambda value: value,
            uuid=SimpleNamespace(uuid4=lambda: encounter_id),
            JSONResponse=response,
            _get_or_create_default_patient=forbidden,
        ))
        result = asyncio.run(
            handler(payload, lambda: database, database.current_user)
        )
        return result, saved, database

    def test_finalize_passes_only_the_explicit_same_practice_patient_to_writer(self):
        selected = SimpleNamespace(
            id=PATIENT_A, practice_id=PRACTICE_A, document_url=DOCUMENT_CONTEXT
        )
        other = SimpleNamespace(
            id=PATIENT_B, practice_id=PRACTICE_B, document_url="https://synthetic.invalid/other"
        )
        payload = self.finalize_payload(PATIENT_A)
        result, saved, db = self.finalize_route(payload, [other, selected])
        self.assertEqual(result.status_code, 200)
        self.assertTrue(result.content["_saved"])
        self.assertEqual(
            result.content["encounter_id"],
            "00000000-0000-4000-8000-000000000101",
        )
        self.assertEqual(len(saved), 1)
        self.assertIs(saved[0][0], db)
        self.assertIs(saved[0][1], selected)
        self.assertEqual(
            saved[0][2],
            uuid.UUID("00000000-0000-4000-8000-000000000201"),
        )
        self.assertEqual(saved[0][3], uuid.UUID(result.content["encounter_id"]))
        self.assertEqual(saved[0][4:6], (str(payload.document_id), payload.text_delta))
        self.assertEqual(db.query_object.conditions,
                         (("id", PATIENT_A), ("practice_id", PRACTICE_A)))

    def test_unknown_and_cross_practice_patients_are_identically_rejected_without_write(self):
        responses = []
        for patients in [[], [SimpleNamespace(id=PATIENT_B, practice_id=PRACTICE_B)]]:
            with self.subTest(rows=len(patients)):
                result, saved, db = self.finalize_route(self.finalize_payload(PATIENT_B), patients)
                self.assertEqual(saved, [])
                self.assertEqual(result.status_code, 404)
                self.assertNotIn(str(PATIENT_B), str(result.content))
                self.assertEqual(db.query_object.conditions,
                                 (("id", PATIENT_B), ("practice_id", PRACTICE_A)))
                responses.append(result.content)
        self.assertEqual(responses[0], responses[1])
        self.assertEqual(responses[0], {"_saved": False, "_save_error": "Patient not found."})

    def test_default_patient_factory_is_absent(self):
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
        self.assertFalse(any(isinstance(n, (ast.FunctionDef, ast.Name))
                             and getattr(n, "name", getattr(n, "id", ""))
                             == "_get_or_create_default_patient" for n in ast.walk(tree)))

    def test_finalize_attestation_is_strict_and_required(self):
        values = dict(
            document_id=COMMAND_ID,
            document_context=DOCUMENT_CONTEXT,
            text_delta="synthetic notes",
            patient_id=PATIENT_A,
            clinician_overrides={},
        )
        for attestation in [MISSING, "true", 1]:
            candidate = dict(values)
            if attestation is not MISSING:
                candidate["clinician_attested"] = attestation
            with self.subTest(value=repr(attestation)), self.assertRaises(ValidationError):
                self.types["FinalizePayload"](**candidate)
        self.assertFalse(
            self.types["FinalizePayload"](
                **values,
                clinician_attested=False,
            ).clinician_attested
        )

    def test_finalize_schema_forbids_client_authority_fields(self):
        for field in ["practitioner_id", "prescribed_by", "actor_user_id", "role"]:
            with self.subTest(field=field), self.assertRaises(ValidationError):
                self.types["FinalizePayload"](
                    document_id=COMMAND_ID,
                    document_context=DOCUMENT_CONTEXT,
                    text_delta="synthetic notes",
                    patient_id=PATIENT_A,
                    clinician_attested=True,
                    clinician_overrides={},
                    **{field: "GP" if field == "role" else str(uuid.uuid4())},
                )

    def test_finalize_requires_command_uuid_and_exact_url_context(self):
        base = self.finalize_payload(PATIENT_A).model_dump(mode="json")
        for field in ["document_id", "document_context"]:
            candidate = dict(base)
            del candidate[field]
            with self.subTest(missing=field), self.assertRaises(ValidationError):
                self.types["FinalizePayload"](**candidate)
        for invalid in ["", "not-a-uuid", 1, False, None, [], {}]:
            candidate = dict(base, document_id=invalid)
            with self.subTest(document_id=repr(invalid)), self.assertRaises(ValidationError):
                self.types["FinalizePayload"](**candidate)
        for invalid in [
            "", "   ", "relative/path", "ftp://synthetic.invalid/file",
            1, False, None, [], {},
        ]:
            candidate = dict(base, document_context=invalid)
            with self.subTest(document_context=repr(invalid)), self.assertRaises(ValidationError):
                self.types["FinalizePayload"](**candidate)

    def test_finalize_context_mismatch_and_unbound_context_share_generic_409(self):
        responses = []
        for stored in [
            "https://synthetic.invalid/different.docx",
            None,
        ]:
            patient = SimpleNamespace(
                id=PATIENT_A,
                practice_id=PRACTICE_A,
                document_url=stored,
            )
            result, saved, _ = self.finalize_route(
                self.finalize_payload(PATIENT_A),
                [patient],
            )
            self.assertEqual(result.status_code, 409)
            self.assertEqual(saved, [])
            self.assertNotIn(DOCUMENT_CONTEXT, str(result.content))
            responses.append(result.content)
        self.assertEqual(responses[0], responses[1])

    def test_finalize_nested_scalars_are_strict_meaningful_and_bounded(self):
        valid = self.finalize_payload(PATIENT_A).model_dump(mode="json")
        mutations = [
            ("text-null", lambda body: body.update(text_delta=None)),
            ("text-number", lambda body: body.update(text_delta=1)),
            ("text-whitespace", lambda body: body.update(text_delta="  ")),
            ("consultation-whitespace", lambda body: body["clinician_overrides"].update(
                consultation_type="  "
            )),
            ("item-bool", lambda body: body["clinician_overrides"]["mbs_items"][0].update(
                item_number=True
            )),
            ("term-number", lambda body: body["clinician_overrides"]["diagnoses"][0].update(
                term=3
            )),
            ("drug-null", lambda body: body["clinician_overrides"]["medications"][0].update(
                drug_name=None
            )),
            ("description-null", lambda body: body["clinician_overrides"]["mbs_items"][0].update(
                description=None
            )),
            ("dosage-bool", lambda body: body["clinician_overrides"]["medications"][0].update(
                dosage_text=False
            )),
            ("text-over", lambda body: body.update(text_delta="x" * 100001)),
            ("item-over", lambda body: body["clinician_overrides"]["mbs_items"][0].update(
                item_number="1" * 11
            )),
            ("term-over", lambda body: body["clinician_overrides"]["diagnoses"][0].update(
                term="x" * 256
            )),
            ("code-over", lambda body: body["clinician_overrides"]["diagnoses"][0].update(
                snomed_ct_au_code="x" * 51
            )),
            ("drug-over", lambda body: body["clinician_overrides"]["medications"][0].update(
                drug_name="x" * 256
            )),
            ("description-over", lambda body: body["clinician_overrides"]["mbs_items"][0].update(
                description="x" * 2049
            )),
            ("dosage-over", lambda body: body["clinician_overrides"]["medications"][0].update(
                dosage_text="x" * 2049
            )),
        ]
        for case, mutate in mutations:
            candidate = json.loads(json.dumps(valid))
            mutate(candidate)
            with self.subTest(case=case), self.assertRaises(ValidationError):
                self.types["FinalizePayload"](**candidate)

    def test_finalize_forbids_extras_and_caps_each_child_list(self):
        base = self.finalize_payload(PATIENT_A).model_dump(mode="json")
        for nested in (False, True):
            candidate = json.loads(json.dumps(base))
            target = candidate["clinician_overrides"]["diagnoses"][0] if nested else candidate
            target["unexpected"] = "no"
            with self.subTest(extra_nested=nested), self.assertRaises(ValidationError) as caught:
                self.types["FinalizePayload"](**candidate)
            errors = caught.exception.errors()
            self.assertEqual(len(errors), 1)
            self.assertEqual(errors[0]["type"], "extra_forbidden")
        for key, seed in [
            ("mbs_items", {"item_number": "23", "description": ""}),
            ("diagnoses", {"term": "synthetic", "snomed_ct_au_code": "synthetic-code"}),
            ("medications", {"drug_name": "synthetic", "dosage_text": ""}),
        ]:
            candidate = json.loads(json.dumps(base))
            candidate["clinician_overrides"][key] = [seed] * 100
            with self.subTest(list_at_cap=key):
                accepted = self.types["FinalizePayload"](**candidate)
                self.assertEqual(len(getattr(accepted.clinician_overrides, key)), 100)
            candidate["clinician_overrides"][key] = [seed] * 101
            with self.subTest(list_over_cap=key), self.assertRaises(ValidationError) as caught:
                self.types["FinalizePayload"](**candidate)
            errors = caught.exception.errors()
            self.assertEqual(len(errors), 1)
            self.assertEqual(errors[0]["type"], "too_long")
            self.assertEqual(errors[0]["loc"], ("clinician_overrides", key))

    def test_finalize_known_aliases_normalize_exactly_and_conflicts_fail_closed(self):
        canonical = self.finalize_payload(PATIENT_A).model_dump(mode="json")
        aliased = json.loads(json.dumps(canonical))
        overrides = aliased["clinician_overrides"]
        overrides["mbs_item_candidates"] = [
            {"item": "23", "description": ""}
        ]
        del overrides["mbs_items"]
        overrides["clinical_diagnoses"] = [
            {"concept_name": "synthetic", "concept_id": "999"}
        ]
        del overrides["diagnoses"]
        overrides["medications_and_prescriptions"] = [
            {"drug": "synthetic", "dosage": ""}
        ]
        del overrides["medications"]
        self.assertEqual(
            self.types["FinalizePayload"](**aliased).model_dump(mode="json"),
            canonical,
        )
        duplicate_exact = json.loads(json.dumps(canonical))
        duplicate_item = duplicate_exact["clinician_overrides"]["mbs_items"][0]
        duplicate_item["item"] = duplicate_item["item_number"]
        duplicate_exact["clinician_overrides"]["mbs_item_candidates"] = json.loads(
            json.dumps(duplicate_exact["clinician_overrides"]["mbs_items"])
        )
        self.assertEqual(
            self.types["FinalizePayload"](**duplicate_exact).model_dump(mode="json"),
            canonical,
        )

        conflicts = [
            {"item_number": "23", "item": 23},
            {"item_number": "23", "item": "36"},
        ]
        for child in conflicts:
            candidate = json.loads(json.dumps(canonical))
            candidate["clinician_overrides"]["mbs_items"] = [child]
            with self.subTest(child=child), self.assertRaises(ValidationError):
                self.types["FinalizePayload"](**candidate)


if __name__ == "__main__":
    unittest.main()
