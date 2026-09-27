"""Synthetic SQL data only for the frozen B32 relationship acceptance contract.

No schema or migration implementation is imported here. Callers own transaction
boundaries, role/context assertions, migration callbacks, and SQLSTATE oracles.
Every table/column interpolated into SQL comes from the literal sets below.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from hashlib import sha256
import json
from uuid import UUID, uuid4

from sqlalchemy import text


@dataclass(frozen=True)
class Edge:
    id: str
    child: str
    column: str
    parent: str
    nullable: bool
    constraint: str


EDGES = (
    Edge("APPT_PATIENT", "appointments", "patient_id", "patients", True, "fk_appointments_practice_patient"),
    Edge("APPT_PRACTITIONER", "appointments", "practitioner_id", "practitioners", False, "fk_appointments_practice_practitioner"),
    Edge("APPT_LOCATION", "appointments", "location_id", "practice_locations", True, "fk_appointments_practice_location"),
    Edge("APPT_TYPE", "appointments", "appointment_type_id", "appointment_types", True, "fk_appointments_practice_type"),
    Edge("APPT_WAITING_AREA", "appointments", "waiting_area_id", "waiting_areas", True, "fk_appointments_practice_waiting_area"),
    Edge("ENCOUNTER_PATIENT", "encounters", "patient_id", "patients", False, "fk_encounters_practice_patient"),
    Edge("ENCOUNTER_PRACTITIONER", "encounters", "practitioner_id", "practitioners", True, "fk_encounters_practice_practitioner"),
    Edge("ENCOUNTER_APPOINTMENT", "encounters", "appointment_id", "appointments", True, "fk_encounters_practice_appointment"),
    Edge("DIAGNOSIS_PATIENT", "clinical_diagnoses", "patient_id", "patients", False, "fk_clinical_diagnoses_practice_patient"),
    Edge("PRESCRIPTION_PATIENT", "prescriptions", "patient_id", "patients", False, "fk_prescriptions_practice_patient"),
    Edge("PRESCRIPTION_PRESCRIBER", "prescriptions", "prescribed_by", "practitioners", True, "fk_prescriptions_practice_prescriber"),
    Edge("CLAIM_PATIENT", "mbs_claims", "patient_id", "patients", False, "fk_mbs_claims_practice_patient"),
    Edge("CLAIM_PRACTITIONER", "mbs_claims", "practitioner_id", "practitioners", True, "fk_mbs_claims_practice_practitioner"),
    Edge("INVOICE_PATIENT", "invoices", "patient_id", "patients", False, "fk_invoices_practice_patient"),
    Edge("DIAGNOSIS_ENCOUNTER", "clinical_diagnoses", "encounter_id", "encounters", True, "fk_clinical_diagnoses_practice_encounter"),
    Edge("PRESCRIPTION_ENCOUNTER", "prescriptions", "encounter_id", "encounters", True, "fk_prescriptions_practice_encounter"),
    Edge("CLAIM_ENCOUNTER", "mbs_claims", "encounter_id", "encounters", True, "fk_mbs_claims_practice_encounter"),
    Edge("INVOICE_ENCOUNTER", "invoices", "encounter_id", "encounters", True, "fk_invoices_practice_encounter"),
)

UPDATE_EDGES = tuple(
    edge for edge in EDGES
    if edge.id in {"APPT_PATIENT", "APPT_TYPE", "APPT_WAITING_AREA"}
)

DATA_TABLES = (
    "practices", "patients", "practitioners", "practice_locations",
    "appointment_types", "waiting_areas", "appointments", "encounters",
    "clinical_diagnoses", "prescriptions", "mbs_claims", "invoices",
    "appointment_audit_log", "appointment_command_idempotency",
)

_INSERT_COLUMNS = {
    "practices": frozenset({"id", "name", "timezone"}),
    "patients": frozenset({"id", "practice_id", "first_name", "last_name", "date_of_birth"}),
    "practitioners": frozenset({"id", "practice_id", "first_name", "last_name", "default_location_id", "is_active"}),
    "practice_locations": frozenset({"id", "practice_id", "name", "is_active"}),
    "appointment_types": frozenset({"id", "practice_id", "name", "default_duration", "is_bookable_online"}),
    "waiting_areas": frozenset({"id", "practice_id", "location_id", "name", "display_order", "is_active"}),
    "appointments": frozenset({
        "id", "practice_id", "patient_id", "patient_name_provisional",
        "practitioner_id", "location_id", "appointment_type_id", "waiting_area_id",
        "booked_by", "start_time", "appointment_date", "start_time_local",
        "duration_minutes", "status", "booked_via", "appointment_state_version",
    }),
    "encounters": frozenset({
        "id", "practice_id", "patient_id", "practitioner_id", "appointment_id",
        "status", "template_type", "consultation_type", "raw_document_text",
    }),
    "clinical_diagnoses": frozenset({"id", "practice_id", "patient_id", "encounter_id", "term"}),
    "prescriptions": frozenset({"id", "practice_id", "patient_id", "encounter_id", "prescribed_by", "drug_name", "dosage_text"}),
    "mbs_claims": frozenset({"id", "practice_id", "patient_id", "practitioner_id", "encounter_id", "item_number", "description", "claim_status"}),
    "invoices": frozenset({"id", "practice_id", "patient_id", "encounter_id", "total_amount", "paid_amount", "status"}),
    "appointment_audit_log": frozenset(),
    "appointment_command_idempotency": frozenset(),
}

_EDGE_BY_ID = {edge.id: edge for edge in EDGES}
assert len(_EDGE_BY_ID) == 18
assert len(UPDATE_EDGES) == 3
assert set(_INSERT_COLUMNS) == set(DATA_TABLES)


def insert(connection, table: str, payload: dict) -> dict:
    """Insert a literal allowlisted table/column payload; return the full row."""
    allowed = _INSERT_COLUMNS.get(table)
    if allowed is None or not payload or not set(payload) <= allowed:
        raise ValueError("unapproved synthetic insert table or columns")
    columns = tuple(payload)
    statement = text(
        f"INSERT INTO public.{table} ({', '.join(columns)}) "
        f"VALUES ({', '.join(':' + column for column in columns)}) RETURNING *"
    )
    return dict(connection.execute(statement, payload).mappings().one())


def update_reference(connection, row_id: UUID, column: str, target: UUID | None) -> dict:
    """Update only one of the three reviewed appointment reference columns."""
    if column not in {edge.column for edge in UPDATE_EDGES}:
        raise ValueError("unapproved synthetic appointment update column")
    statement = text(
        f"UPDATE public.appointments SET {column} = :target "
        "WHERE id = :row_id RETURNING *"
    )
    return dict(connection.execute(statement, {"target": target, "row_id": row_id}).mappings().one())


def snapshot(connection) -> dict[str, list[dict]]:
    """Canonical full rows for exact owned tables; use owner/observer connection.

    Keep this raw value out of assertion messages because it contains synthetic
    generated IDs. Compare using snapshot_fingerprint for safe diagnostics.
    """
    return {
        table: connection.execute(
            text(f"SELECT to_jsonb(t) FROM public.{table} AS t ORDER BY t.id")
        ).scalars().all()
        for table in DATA_TABLES
    }


def snapshot_fingerprint(rows: dict[str, list[dict]]) -> dict[str, dict[str, str | int]]:
    """Per-table full-row comparison facts without exposing generated IDs."""
    if set(rows) != set(DATA_TABLES):
        raise ValueError("snapshot table set differs from frozen data table set")
    result = {}
    for table in DATA_TABLES:
        canonical = json.dumps(
            rows[table], sort_keys=True, separators=(",", ":"),
            ensure_ascii=False, allow_nan=False,
        ).encode("utf-8")
        result[table] = {"count": len(rows[table]), "sha256": sha256(canonical).hexdigest()}
    return result


class World:
    """Committed coherent P/Q fixture, with per-probe fresh child payloads."""

    def __init__(self) -> None:
        self.practices = {"P": uuid4(), "Q": uuid4()}
        self.targets = {
            table: {"P": uuid4(), "Q": uuid4()}
            for table in (
                "practice_locations", "practitioners", "patients",
                "appointment_types", "waiting_areas", "appointments", "encounters",
            )
        }
        self.alternates = {
            table: {"P": uuid4()}
            for table in ("patients", "appointment_types", "waiting_areas")
        }
        self.anchors: dict[str, dict[str, UUID]] = {
            table: {"P": uuid4(), "Q": uuid4()}
            for table in ("clinical_diagnoses", "prescriptions", "mbs_claims", "invoices")
        }
        self.anchors["appointments"] = dict(self.targets["appointments"])
        self.anchors["encounters"] = dict(self.targets["encounters"])
        self.null_anchors: dict[str, dict[str, UUID]] = {
            table: {"P": uuid4(), "Q": uuid4()}
            for table in (
                "appointments", "encounters", "clinical_diagnoses",
                "prescriptions", "mbs_claims", "invoices",
            )
        }
        self._time_counter = 0

    @classmethod
    def seed(cls, owner_engine) -> World:
        """Commit a nonempty, cross-tenant coherent baseline via owner SQL."""
        world = cls()
        with owner_engine.begin() as connection:
            for label in ("P", "Q"):
                insert(connection, "practices", {
                    "id": world.practices[label],
                    "name": "Synthetic relationship " + label,
                    "timezone": "UTC",
                })
                for table in (
                    "practice_locations", "practitioners", "patients",
                    "appointment_types", "waiting_areas",
                ):
                    insert(connection, table, world._parent_payload(table, label))
                insert(connection, "appointments", world._child_payload("appointments", label, world.targets["appointments"][label]))
                insert(connection, "encounters", world._child_payload("encounters", label, world.targets["encounters"][label]))
                for table in ("clinical_diagnoses", "prescriptions", "mbs_claims", "invoices"):
                    insert(connection, table, world._child_payload(table, label, world.anchors[table][label]))
                for table in world.null_anchors:
                    insert(connection, table, world._null_child_payload(table, label, world.null_anchors[table][label]))
            for table in world.alternates:
                insert(connection, table, world._parent_payload(table, "P", world.alternates[table]["P"]))
        return world

    def _next_start(self) -> datetime:
        self._time_counter += 1
        return datetime(2035, 1, 1, 9, 0, tzinfo=timezone.utc) + timedelta(days=self._time_counter)

    def _parent_payload(self, table: str, label: str, row_id: UUID | None = None) -> dict:
        practice_id = self.practices[label]
        row_id = row_id or self.targets[table][label]
        if table == "practice_locations":
            return {"id": row_id, "practice_id": practice_id, "name": "Synthetic location " + str(row_id), "is_active": True}
        if table == "practitioners":
            return {"id": row_id, "practice_id": practice_id, "first_name": "Synthetic", "last_name": "Practitioner " + str(row_id), "default_location_id": None, "is_active": True}
        if table == "patients":
            return {"id": row_id, "practice_id": practice_id, "first_name": "Synthetic", "last_name": "Patient " + str(row_id), "date_of_birth": date(1980, 1, 1)}
        if table == "appointment_types":
            return {"id": row_id, "practice_id": practice_id, "name": "Synthetic type " + str(row_id), "default_duration": 15, "is_bookable_online": False}
        if table == "waiting_areas":
            return {"id": row_id, "practice_id": practice_id, "location_id": self.targets["practice_locations"][label], "name": "Synthetic area " + str(row_id), "display_order": 0, "is_active": True}
        raise ValueError("unapproved synthetic parent table")

    def _child_payload(self, table: str, label: str, row_id: UUID) -> dict:
        practice_id = self.practices[label]
        patient = self.targets["patients"][label]
        practitioner = self.targets["practitioners"][label]
        encounter = self.targets["encounters"][label]
        if table == "appointments":
            start = self._next_start()
            return {
                "id": row_id, "practice_id": practice_id,
                "patient_id": patient, "practitioner_id": practitioner,
                "location_id": self.targets["practice_locations"][label],
                "appointment_type_id": self.targets["appointment_types"][label],
                "waiting_area_id": self.targets["waiting_areas"][label],
                "start_time": start, "appointment_date": start.date(),
                "start_time_local": time(9, 0), "duration_minutes": 15,
                "status": "Booked", "booked_via": "Receptionist",
                "appointment_state_version": 1,
            }
        if table == "encounters":
            return {
                "id": row_id, "practice_id": practice_id,
                "patient_id": patient, "practitioner_id": practitioner,
                "appointment_id": self.targets["appointments"][label],
                "status": "Draft", "template_type": "SOAP",
                "consultation_type": "Synthetic",
            }
        if table == "clinical_diagnoses":
            return {"id": row_id, "practice_id": practice_id, "patient_id": patient, "encounter_id": encounter, "term": "Synthetic diagnosis"}
        if table == "prescriptions":
            return {"id": row_id, "practice_id": practice_id, "patient_id": patient, "encounter_id": encounter, "prescribed_by": practitioner, "drug_name": "Synthetic medicine", "dosage_text": "Synthetic only"}
        if table == "mbs_claims":
            return {"id": row_id, "practice_id": practice_id, "patient_id": patient, "encounter_id": encounter, "practitioner_id": practitioner, "item_number": "90000", "description": "Synthetic claim", "claim_status": "Draft"}
        if table == "invoices":
            return {"id": row_id, "practice_id": practice_id, "patient_id": patient, "encounter_id": encounter, "total_amount": Decimal("1.00"), "paid_amount": Decimal("0.00"), "status": "Draft"}
        raise ValueError("unapproved synthetic child table")

    def _null_child_payload(self, table: str, label: str, row_id: UUID) -> dict:
        """Committed optional-NULL controls; required patient/practitioner stay set."""
        payload = self._child_payload(table, label, row_id)
        optional = {
            "appointments": ("patient_id", "location_id", "appointment_type_id", "waiting_area_id"),
            "encounters": ("practitioner_id", "appointment_id"),
            "clinical_diagnoses": ("encounter_id",),
            "prescriptions": ("encounter_id", "prescribed_by"),
            "mbs_claims": ("encounter_id", "practitioner_id"),
            "invoices": ("encounter_id",),
        }
        for column in optional[table]:
            payload[column] = None
        if table == "appointments":
            payload["patient_name_provisional"] = "Synthetic provisional"
        return payload

    def payload(self, edge: Edge, target: UUID | None = None) -> dict:
        """Fresh P child; target=None chooses P. Copy one result for P/Q comparisons.

        To exercise nullable SQL NULL, set the selected key to None on the copy.
        """
        if _EDGE_BY_ID.get(edge.id) != edge:
            raise ValueError("unapproved relationship edge")
        payload = self._child_payload(edge.child, "P", uuid4())
        payload[edge.column] = self.targets[edge.parent]["P"] if target is None else target
        return payload


@dataclass(frozen=True)
class DedicatedParent:
    edge_id: str
    table: str
    id: UUID


def seed_dedicated_parent(connection, edge: Edge, world: World) -> DedicatedParent:
    """Create a P target with no incoming references until caller adds one child.

    Invoke twice for separate referenced/unreferenced rollback controls. A
    dedicated appointment has only its required P practitioner; a dedicated
    encounter has only its required P patient. Other optional refs are NULL.
    """
    if _EDGE_BY_ID.get(edge.id) != edge:
        raise ValueError("unapproved relationship edge")
    row_id = uuid4()
    if edge.parent in {"patients", "practitioners", "practice_locations", "appointment_types", "waiting_areas"}:
        payload = world._parent_payload(edge.parent, "P", row_id)
        if edge.parent == "waiting_areas":
            payload["location_id"] = None
    elif edge.parent == "appointments":
        start = world._next_start()
        payload = {
            "id": row_id, "practice_id": world.practices["P"],
            "patient_id": None, "patient_name_provisional": "Synthetic provisional",
            "practitioner_id": world.targets["practitioners"]["P"],
            "location_id": None, "appointment_type_id": None,
            "waiting_area_id": None, "booked_by": None,
            "start_time": start, "appointment_date": start.date(),
            "start_time_local": time(9, 0), "duration_minutes": 15,
            "status": "Cancelled", "booked_via": "Receptionist",
            "appointment_state_version": 1,
        }
    elif edge.parent == "encounters":
        payload = {
            "id": row_id, "practice_id": world.practices["P"],
            "patient_id": world.targets["patients"]["P"],
            "practitioner_id": None, "appointment_id": None,
            "status": "Draft", "template_type": "SOAP",
            "consultation_type": "Synthetic dedicated",
        }
    else:
        raise ValueError("unapproved dedicated parent table")
    insert(connection, edge.parent, payload)
    return DedicatedParent(edge.id, edge.parent, row_id)


def move_parent(connection, dedicated: DedicatedParent, world: World) -> dict:
    """Move only this P parent to Q, keeping its own outgoing references valid.

    The appointment/encounter required dependency switches to its Q counterpart
    in the same UPDATE statement. The matching unreferenced control must succeed
    before attributing a referenced failure to a specific incoming composite FK.
    """
    edge = _EDGE_BY_ID.get(dedicated.edge_id)
    if edge is None or edge.parent != dedicated.table:
        raise ValueError("unapproved dedicated parent")
    assignments = ["practice_id = :q"]
    params = {"q": world.practices["Q"], "row_id": dedicated.id}
    if dedicated.table == "appointments":
        assignments.append("practitioner_id = :q_practitioner")
        params["q_practitioner"] = world.targets["practitioners"]["Q"]
    elif dedicated.table == "encounters":
        assignments.append("patient_id = :q_patient")
        params["q_patient"] = world.targets["patients"]["Q"]
    statement = text(
        f"UPDATE public.{dedicated.table} SET {', '.join(assignments)} "
        "WHERE id = :row_id RETURNING *"
    )
    return dict(connection.execute(statement, params).mappings().one())
