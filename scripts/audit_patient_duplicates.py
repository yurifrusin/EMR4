"""Read-only developer audit for likely duplicate patient records.

This helper intentionally prints evidence only. It never deletes, merges, or
updates patient records.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import uuid
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@dataclass(frozen=True)
class PatientSnapshot:
    id: uuid.UUID
    practice_id: uuid.UUID
    first_name: str
    last_name: str
    date_of_birth: date
    medicare_number: str | None = None
    medicare_irn: str | None = None
    ihi_number: str | None = None
    phone_mobile: str | None = None
    phone_home: str | None = None
    document_url: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(frozen=True)
class DuplicateGroup:
    kind: str
    label: str
    key: tuple[Any, ...]
    patients: tuple[PatientSnapshot, ...]


@dataclass(frozen=True)
class ReferenceColumn:
    table_name: str
    column_name: str
    table: Any
    column: Any

    @property
    def label(self) -> str:
        if self.column_name == "patient_id":
            return self.table_name
        return f"{self.table_name}.{self.column_name}"


def _clean_text(value: Any) -> str:
    return " ".join(str(value or "").strip().lower().split())


def _clean_identifier(value: Any) -> str:
    return "".join(ch for ch in str(value or "").strip().lower() if ch.isalnum())


def _format_dt(value: datetime | None) -> str:
    if value is None:
        return "-"
    return value.isoformat(timespec="seconds")


def _fingerprint(parts: tuple[Any, ...]) -> str:
    normalized = "|".join(str(part or "") for part in parts)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:12]


def _snapshot_patient(patient: Any) -> PatientSnapshot:
    return PatientSnapshot(
        id=patient.id,
        practice_id=patient.practice_id,
        first_name=patient.first_name,
        last_name=patient.last_name,
        date_of_birth=patient.date_of_birth,
        medicare_number=patient.medicare_number,
        medicare_irn=patient.medicare_irn,
        ihi_number=patient.ihi_number,
        phone_mobile=patient.phone_mobile,
        phone_home=patient.phone_home,
        document_url=patient.document_url,
        created_at=patient.created_at,
        updated_at=patient.updated_at,
    )


def find_duplicate_groups(patients: list[PatientSnapshot]) -> list[DuplicateGroup]:
    grouped: dict[tuple[str, tuple[Any, ...]], list[PatientSnapshot]] = defaultdict(list)

    for patient in patients:
        name_key = (
            "same-name-dob",
            (
                patient.practice_id,
                _clean_text(patient.first_name),
                _clean_text(patient.last_name),
                patient.date_of_birth,
            ),
        )
        grouped[name_key].append(patient)

        medicare = _clean_identifier(patient.medicare_number)
        medicare_irn = _clean_identifier(patient.medicare_irn)
        if medicare and medicare_irn:
            grouped[("medicare-irn", (patient.practice_id, medicare, medicare_irn))].append(patient)

        ihi = _clean_identifier(patient.ihi_number)
        if ihi:
            grouped[("ihi", (patient.practice_id, ihi))].append(patient)

    duplicate_groups: list[DuplicateGroup] = []
    for (kind, key), members in grouped.items():
        if len(members) < 2:
            continue
        members = sorted(members, key=lambda p: (_format_dt(p.created_at), str(p.id)))
        duplicate_groups.append(
            DuplicateGroup(
                kind=kind,
                label=_group_label(kind, key),
                key=key,
                patients=tuple(members),
            )
        )

    return sorted(duplicate_groups, key=lambda g: (g.kind, g.label))


def _group_label(kind: str, key: tuple[Any, ...]) -> str:
    if kind == "same-name-dob":
        return f"same-name-dob:{_fingerprint(key)}"
    if kind == "medicare-irn":
        return f"medicare-irn:{_fingerprint(key)}"
    if kind == "ihi":
        return f"ihi:{_fingerprint(key)}"
    return f"{kind}:{_fingerprint(key)}"


def load_database_context(database_url: str | None):
    from sqlalchemy import create_engine

    from app.config import settings
    from app.models import Base, Patient  # noqa: F401 - imports all mapped models into metadata

    engine = create_engine(database_url or settings.database_url)
    return engine, Base, Patient


def discover_patient_reference_columns(metadata: Any) -> list[ReferenceColumn]:
    references: list[ReferenceColumn] = []
    for table in metadata.sorted_tables:
        if table.name == "patients":
            continue
        for column in table.columns:
            if any(fk.column.table.name == "patients" and fk.column.name == "id" for fk in column.foreign_keys):
                references.append(
                    ReferenceColumn(
                        table_name=table.name,
                        column_name=column.name,
                        table=table,
                        column=column,
                    )
                )
    return sorted(references, key=lambda ref: ref.label)


def load_patients(session: Any, Patient: Any, practice_id: uuid.UUID | None):
    from sqlalchemy import select

    query = select(Patient)
    if practice_id is not None:
        query = query.where(Patient.practice_id == practice_id)
    query = query.order_by(Patient.practice_id, Patient.last_name, Patient.first_name, Patient.created_at)
    return [_snapshot_patient(patient) for patient in session.execute(query).scalars()]


def count_references(
    session: Any,
    reference_columns: list[ReferenceColumn],
    patient_ids: list[uuid.UUID],
) -> dict[uuid.UUID, dict[str, int]]:
    from sqlalchemy import func, select

    counts: dict[uuid.UUID, dict[str, int]] = {patient_id: {} for patient_id in patient_ids}
    for patient_id in patient_ids:
        for ref in reference_columns:
            count = session.execute(
                select(func.count()).select_from(ref.table).where(ref.column == patient_id)
            ).scalar_one()
            counts[patient_id][ref.label] = int(count or 0)
    return counts


def _patient_payload(patient_index: int, counts: dict[str, int], show_zero: bool) -> dict[str, Any]:
    references = {
        label: count
        for label, count in sorted(counts.items())
        if show_zero or count
    }
    return {
        "patient_index": patient_index,
        "reference_total": sum(counts.values()),
        "references": references,
    }


def build_json_payload(
    duplicate_groups: list[DuplicateGroup],
    reference_counts: dict[uuid.UUID, dict[str, int]],
    show_zero: bool,
) -> dict[str, Any]:
    return {
        "read_only": True,
        "duplicate_group_count": len(duplicate_groups),
        "groups": [
            {
                "kind": group.kind,
                "label": group.label,
                "patient_count": len(group.patients),
                "patient_reference_summaries": [
                    _patient_payload(patient_index, reference_counts.get(patient.id, {}), show_zero)
                    for patient_index, patient in enumerate(group.patients, start=1)
                ],
            }
            for group in duplicate_groups
        ],
    }


def print_human_report(
    duplicate_groups: list[DuplicateGroup],
    reference_counts: dict[uuid.UUID, dict[str, int]],
    show_zero: bool,
) -> None:
    print("EMR4 duplicate patient audit")
    print("Mode: read-only. No records were changed.\n")

    if not duplicate_groups:
        print("No likely duplicate patient groups found.")
        return

    print(f"Likely duplicate groups found: {len(duplicate_groups)}\n")
    for group_index, group in enumerate(duplicate_groups, start=1):
        print(f"[{group_index}] {group.kind}: {group.label}")
        print(f"    Patients in group: {len(group.patients)}")
        for patient_index, patient in enumerate(group.patients, start=1):
            counts = reference_counts.get(patient.id, {})
            visible_counts = {label: count for label, count in sorted(counts.items()) if show_zero or count}
            total = sum(counts.values())
            references = ", ".join(f"{label}={count}" for label, count in visible_counts.items())
            if not references:
                references = "none"

            print(f"    - patient #{patient_index}: {total} total references ({references})")
        print()

    print("Next step: inspect the evidence, then use a proper merge/delete workflow. This helper does not prove deletion is safe.")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read-only developer audit for likely duplicate EMR4 patient records.",
    )
    parser.add_argument("--database-url", help="Override DATABASE_URL for this read-only audit.")
    parser.add_argument("--practice-id", type=uuid.UUID, help="Limit audit to one practice UUID.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of the human report.")
    parser.add_argument("--show-zero", action="store_true", help="Show zero-count patient reference tables.")
    parser.add_argument("--debug", action="store_true", help="Show full Python tracebacks on errors.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        from sqlalchemy.orm import Session

        engine, Base, Patient = load_database_context(args.database_url)
        with engine.connect() as connection:
            with Session(connection) as session:
                patients = load_patients(session, Patient, args.practice_id)
                groups = find_duplicate_groups(patients)
                reference_patient_ids = sorted(
                    {patient.id for group in groups for patient in group.patients},
                    key=str,
                )
                references = discover_patient_reference_columns(Base.metadata)
                reference_counts = count_references(session, references, reference_patient_ids)

        if args.json:
            print(json.dumps(build_json_payload(groups, reference_counts, args.show_zero), indent=2, sort_keys=True))
        else:
            print_human_report(groups, reference_counts, args.show_zero)
        return 0
    except Exception as exc:
        if args.debug:
            raise
        print("Patient duplicate audit failed safely.", file=sys.stderr)
        print("No records were changed.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
