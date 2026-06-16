"""
Dev seed: creates a default Practice, admin User, and GP Practitioner.
Run once after `alembic upgrade head`.

Usage:
    .venv\Scripts\python seed.py
"""
import sys
from app.database import SessionLocal
from datetime import date, datetime, time, timedelta
from app.models.tenancy import Practice, User, Practitioner, UserRole
from app.models.patients import Patient
from app.models.clinical import Allergy
from app.models.billing import MbsDirectory, SnomedDirectory
from app.models.appointments import (
    Appointment, AppointmentType, AppointmentStatus,
    BookingChannel, PractitionerSchedule,
)
from app.services.auth_service import hash_password


def seed():
    db = SessionLocal()
    try:
        # --- Practice ---
        practice = db.query(Practice).filter_by(name="EMR4 Dev Clinic").first()
        if not practice:
            practice = Practice(
                name="EMR4 Dev Clinic",
                abn="12 345 678 901",
                address_line1="1 Medical Street",
                address_suburb="Sydney",
                address_state="NSW",
                address_postcode="2000",
                phone="(02) 9000 0000",
                email="admin@emr4dev.local",
                timezone="Australia/Sydney",
                hive_mind_opt_in=False,
            )
            db.add(practice)
            db.flush()
            print(f"  Created practice: {practice.name} ({practice.id})")
        else:
            print(f"  Practice already exists: {practice.id}")

        # --- Practitioner ---
        gp = db.query(Practitioner).filter_by(
            practice_id=practice.id, ahpra_number="MED0001234567"
        ).first()
        if not gp:
            gp = Practitioner(
                practice_id=practice.id,
                first_name="Alex",
                last_name="Shera",
                provider_number="1234561A",
                prescriber_number="1234561",
                ahpra_number="MED0001234567",
                specialty="General Practice",
                is_active=True,
            )
            db.add(gp)
            db.flush()
            print(f"  Created GP: Dr {gp.first_name} {gp.last_name} ({gp.id})")
        else:
            print(f"  GP already exists: {gp.id}")

        # --- Admin User ---
        admin = db.query(User).filter_by(email="admin@emr4dev.local").first()
        if not admin:
            admin = User(
                practice_id=practice.id,
                email="admin@emr4dev.local",
                password_hash=hash_password("Password1!"),
                role=UserRole.PracticeOwner,
                practitioner_id=gp.id,
                is_active=True,
            )
            db.add(admin)
            print(f"  Created admin user: {admin.email}")
        else:
            print(f"  Admin user already exists: {admin.email}")

        # --- GP User ---
        gp_user = db.query(User).filter_by(email="dr.shera@emr4dev.local").first()
        if not gp_user:
            gp_user = User(
                practice_id=practice.id,
                email="dr.shera@emr4dev.local",
                password_hash=hash_password("Password1!"),
                role=UserRole.GP,
                practitioner_id=gp.id,
                is_active=True,
            )
            db.add(gp_user)
            print(f"  Created GP user: {gp_user.email}")
        else:
            print(f"  GP user already exists: {gp_user.email}")

        # --- Mock Patient ---
        patient = db.query(Patient).filter_by(
            practice_id=practice.id, medicare_number="2345678901"
        ).first()
        if not patient:
            patient = Patient(
                practice_id=practice.id,
                first_name="Margaret",
                last_name="Thompson",
                date_of_birth=date(1952, 3, 14),
                sex="Female",
                medicare_number="2345678901",
                phone_mobile="0412 345 678",
                email="margaret.thompson@example.com",
                address_line1="42 Eucalyptus Drive",
                address_suburb="Parramatta",
                address_state="NSW",
                address_postcode="2150",
                emergency_contact_name="Robert Thompson",
                emergency_contact_phone="0413 999 888",
                emergency_contact_relationship="Spouse",
                concession_type="Pensioner",
            )
            db.add(patient)
            db.flush()
            print(f"  Created patient: {patient.first_name} {patient.last_name} ({patient.id})")

            db.add(Allergy(
                practice_id=practice.id,
                patient_id=patient.id,
                substance="Penicillin",
                reaction="Anaphylaxis",
                severity="Life-threatening",
            ))
            db.add(Allergy(
                practice_id=practice.id,
                patient_id=patient.id,
                substance="Aspirin",
                reaction="Urticaria",
                severity="Moderate",
            ))
            print("    Added 2 allergies")
        else:
            print(f"  Patient already exists: {patient.id}")

        # --- Mock Patient 2: Billy Frusin (paediatric; matches the generated
        #     BILLY FRUSIN 15-10-2015.docx used for patient-file testing) ---
        billy = db.query(Patient).filter_by(
            practice_id=practice.id, medicare_number="3456789012"
        ).first()
        if not billy:
            billy = Patient(
                practice_id=practice.id,
                first_name="Billy",
                last_name="Frusin",
                date_of_birth=date(2015, 10, 15),
                sex="Male",
                medicare_number="3456789012",
                phone_mobile="0413 222 333",
                address_line1="15 Wattle Street",
                address_suburb="Blacktown",
                address_state="NSW",
                address_postcode="2148",
            )
            db.add(billy)
            db.flush()
            print(f"  Created patient: {billy.first_name} {billy.last_name} ({billy.id})")
        else:
            print(f"  Patient already exists: {billy.id}")

        # --- MBS Directory seed ---
        mbs_items = [
            ("3",  "Professional attendance, Level A — < 5 mins", "$18.85"),
            ("23", "Professional attendance, Level B — 5–19 mins", "$41.40"),
            ("36", "Professional attendance, Level C — 20–39 mins", "$80.10"),
            ("44", "Professional attendance, Level D — ≥ 40 mins", "$118.00"),
            ("721", "GP Management Plan preparation", "$154.45"),
            ("723", "Team Care Arrangement — GP coordination", "$114.65"),
            ("965", "Chronic Disease Management Plan (GPCCMP) preparation", "$154.45"),
            ("967", "Chronic Disease Management Plan review", "$77.25"),
            ("2715", "Mental Health Treatment Plan preparation", "$154.45"),
            ("2717", "Mental Health Treatment Plan review", "$77.25"),
            ("701", "Health Assessment — 45–49 years", "$154.45"),
            ("703", "Health Assessment — 75+ years", "$154.45"),
            ("715", "Health Assessment — Aboriginal/Torres Strait Islander", "$154.45"),
        ]
        for item_number, description, fee in mbs_items:
            if not db.query(MbsDirectory).filter_by(item_number=item_number).first():
                db.add(MbsDirectory(item_number=item_number, description=description, fee=fee))

        # --- SNOMED seed ---
        snomed_items = [
            ("59621000", "Essential hypertension"),
            ("44054006", "Type 2 diabetes mellitus"),
            ("195967001", "Asthma"),
            ("55822004", "Hyperlipidaemia"),
            ("73211009", "Diabetes mellitus"),
            ("414545008", "Ischaemic heart disease"),
            ("35489007", "Depressive disorder"),
            ("35240004", "Anxiety disorder"),
            ("40122008", "Pneumonia"),
            ("267032009", "Tired all the time"),
            ("386661006", "Fever"),
            ("57676002", "Joint pain"),
            ("84114007", "Heart failure"),
        ]
        for concept_id, term in snomed_items:
            if not db.query(SnomedDirectory).filter_by(concept_id=concept_id).first():
                db.add(SnomedDirectory(concept_id=concept_id, term=term))

        # --- Appointment Types ---
        appt_types = [
            ("Standard Consult",    15, "3B82F6", True),
            ("Long Consult",        30, "8B5CF6", True),
            ("Procedure",           30, "EF4444", False),
            ("Nurse Appointment",   15, "10B981", True),
            ("Telehealth",          15, "F59E0B", True),
        ]
        for name, duration, color, online in appt_types:
            if not db.query(AppointmentType).filter_by(
                practice_id=practice.id, name=name
            ).first():
                db.add(AppointmentType(
                    practice_id=practice.id,
                    name=name,
                    default_duration=duration,
                    color_hex=f"#{color}",
                    is_bookable_online=online,
                ))
        db.flush()
        print("  Appointment types seeded")

        std_type = db.query(AppointmentType).filter_by(
            practice_id=practice.id, name="Standard Consult"
        ).first()

        # --- Practitioner Schedule (Mon-Fri 09:00-17:00, 15-min slots) ---
        for day in range(5):   # 0=Mon .. 4=Fri
            if not db.query(PractitionerSchedule).filter_by(
                practitioner_id=gp.id, day_of_week=day
            ).first():
                db.add(PractitionerSchedule(
                    practitioner_id=gp.id,
                    day_of_week=day,
                    start_time=time(9, 0),
                    end_time=time(17, 0),
                    slot_duration_minutes=15,
                ))
        db.flush()
        print("  Practitioner schedule seeded (Mon-Fri 09:00-17:00)")

        # --- Sample appointments for today (so the Schedule tab is non-empty) ---
        today = date.today()
        def _appt_dt(h: int, m: int) -> datetime:
            return datetime.combine(today, time(h, m))

        # Margaret 09:00 is seeded as Confirmed so the diary's lifecycle
        # colour rendering (ALL-CAPS + blue) is demonstrated out of the box.
        sample_appts = [
            (patient, _appt_dt(9, 0),  "Hypertension review",   AppointmentStatus.Confirmed),
            (billy,   _appt_dt(9, 15), "Paediatric check-up",    AppointmentStatus.Booked),
            (patient, _appt_dt(10, 0), "Care plan review",       AppointmentStatus.Booked),
        ]
        for pt, start, reason, init_status in sample_appts:
            exists = db.query(Appointment).filter_by(
                practice_id=practice.id,
                patient_id=pt.id,
                start_time=start,
            ).first()
            if not exists:
                db.add(Appointment(
                    practice_id=practice.id,
                    patient_id=pt.id,
                    practitioner_id=gp.id,
                    appointment_type_id=std_type.id if std_type else None,
                    booked_by=gp_user.id,
                    start_time=start,
                    duration_minutes=15,
                    status=init_status,
                    reason=reason,
                    booked_via=BookingChannel.Receptionist,
                ))
            elif exists.status == AppointmentStatus.Booked and init_status != AppointmentStatus.Booked:
                # Idempotent upgrade: apply the demo status if user hasn't changed it
                exists.status = init_status
        db.flush()
        print(f"  Sample appointments seeded for today ({today})")

        db.commit()
        print("\nSeed complete.")
        print("\nLogin credentials:")
        print("  GP:    dr.shera@emr4dev.local  /  Password1!")
        print("  Admin: admin@emr4dev.local      /  Password1!")

    except Exception as e:
        db.rollback()
        print(f"Seed failed: {e}", file=sys.stderr)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
