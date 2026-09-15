"""Patient-selection source-component regressions with real Pydantic validation.

Run only in a reviewed literal-file capsule. Route bodies are unchanged except
for removing decorators/type annotations/default dependency objects at extraction;
HTTP authentication, SQLAlchemy/PostgreSQL and provider adapters are not exercised.
This is not full application, cross-tenant or clinician-attestation acceptance.
"""
import ast
import asyncio
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List, Literal, Optional
import unittest
import uuid

from pydantic import BaseModel, ValidationError


SOURCE = Path(__file__).resolve().parents[1] / "app/routers/consultation.py"
PATIENT_A = uuid.UUID("00000000-0000-4000-8000-000000000001")
PATIENT_B = uuid.UUID("00000000-0000-4000-8000-000000000002")
PRACTICE_A = uuid.UUID("00000000-0000-4000-8000-000000000011")
PRACTICE_B = uuid.UUID("00000000-0000-4000-8000-000000000012")
MISSING = object()


def schemas():
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    names = {"OverrideData", "ConsultationPayload", "FinalizePayload"}
    nodes = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name in names]
    assert {n.name for n in nodes} == names
    namespace = dict(__name__="isolated_consultation_schemas", BaseModel=BaseModel,
                     uuid=uuid, Any=Any, Dict=Dict, List=List, Literal=Literal,
                     Optional=Optional)
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


class Field:
    def __init__(self, name):
        self.name = name

    def __eq__(self, value):
        return (self.name, value)


class PatientModel:
    id = Field("id")
    practice_id = Field("practice_id")


class PatientQuery:
    def __init__(self, patients):
        self.patients = patients
        self.conditions = None

    def filter(self, *conditions):
        self.conditions = conditions
        return self

    def first(self):
        assert self.conditions is not None
        return next((p for p in self.patients
                     if all(getattr(p, name) == value for name, value in self.conditions)), None)


class PatientDatabase:
    def __init__(self, patients):
        self.query_object = PatientQuery(patients)

    def query(self, model):
        assert model is PatientModel
        return self.query_object

    add = commit = refresh = rollback = forbidden


def response(*, content, status_code=200):
    return SimpleNamespace(content=content, status_code=status_code)


class ConsultationPatientBindingTests(unittest.TestCase):
    def setUp(self):
        self.types = schemas()

    def finalize_payload(self, patient_id=MISSING):
        values = dict(document_id="authored-document", text_delta="authored synthetic notes",
                      clinician_overrides={"consultation_type": "Reviewed synthetic consultation",
                                           "mbs_items": [{"item_number": "23"}],
                                           "diagnoses": [{"term": "synthetic"}],
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

        def save(*args):
            saved.append(args)
            return SimpleNamespace(id="authored-encounter")

        database = PatientDatabase(patients)
        handler = route("finalize_consultation", dict(
            Patient=PatientModel, _save_encounter=save, JSONResponse=response,
            _get_or_create_default_patient=forbidden))
        result = asyncio.run(handler(payload, database, SimpleNamespace(practice_id=PRACTICE_A)))
        return result, saved, database

    def test_finalize_passes_only_the_explicit_same_practice_patient_to_writer(self):
        selected = SimpleNamespace(id=PATIENT_A, practice_id=PRACTICE_A)
        other = SimpleNamespace(id=PATIENT_B, practice_id=PRACTICE_B)
        payload = self.finalize_payload(PATIENT_A)
        result, saved, db = self.finalize_route(payload, [other, selected])
        self.assertEqual(result.status_code, 200)
        self.assertTrue(result.content["_saved"])
        self.assertEqual(len(saved), 1)
        self.assertIs(saved[0][0], db)
        self.assertIs(saved[0][1], selected)
        self.assertEqual(saved[0][2:4], (payload.document_id, payload.text_delta))
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


if __name__ == "__main__":
    unittest.main()
