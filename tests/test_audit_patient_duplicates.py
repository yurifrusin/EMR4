import uuid
from datetime import date

from scripts.audit_patient_duplicates import PatientSnapshot, find_duplicate_groups


PRACTICE_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")


def _patient(
    patient_id: str,
    first_name: str = "Billy",
    last_name: str = "Frusin",
    dob: date = date(2010, 5, 4),
    medicare: str | None = None,
    irn: str | None = None,
    ihi: str | None = None,
) -> PatientSnapshot:
    return PatientSnapshot(
        id=uuid.UUID(patient_id),
        practice_id=PRACTICE_ID,
        first_name=first_name,
        last_name=last_name,
        date_of_birth=dob,
        medicare_number=medicare,
        medicare_irn=irn,
        ihi_number=ihi,
    )


def test_duplicate_groups_cover_name_dob_medicare_irn_and_ihi():
    patients = [
        _patient("00000000-0000-0000-0000-000000000001", medicare="1234 56789", irn="1", ihi="8003600000000001"),
        _patient("00000000-0000-0000-0000-000000000002", first_name=" billy ", last_name="FRUSIN", medicare="123456789", irn="1", ihi="8003 6000 0000 0001"),
        _patient("00000000-0000-0000-0000-000000000003", first_name="Margaret", last_name="Thompson"),
    ]

    groups = find_duplicate_groups(patients)

    assert [group.kind for group in groups] == ["ihi", "medicare-irn", "same-name-dob"]
    assert all(len(group.patients) == 2 for group in groups)


def test_duplicate_groups_are_scoped_to_practice():
    patients = [
        _patient("00000000-0000-0000-0000-000000000001", medicare="123456789", irn="1"),
        PatientSnapshot(
            id=uuid.UUID("00000000-0000-0000-0000-000000000002"),
            practice_id=uuid.UUID("22222222-2222-2222-2222-222222222222"),
            first_name="Billy",
            last_name="Frusin",
            date_of_birth=date(2010, 5, 4),
            medicare_number="123456789",
            medicare_irn="1",
        ),
    ]

    assert find_duplicate_groups(patients) == []
