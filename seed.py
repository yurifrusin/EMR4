"""
Dev seed: creates a default Practice, admin User, and GP Practitioner.
Run once after `alembic upgrade head`.

Usage:
    .venv\Scripts\python seed.py
"""
import sys
from app.database import SessionLocal
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from app.models.tenancy import Practice, User, Practitioner, UserRole, PracticeLocation
from app.models.patients import Patient
from app.models.clinical import Allergy
from app.models.billing import MbsDirectory, SnomedDirectory
from app.models.appointments import (
    Appointment, AppointmentType, AppointmentStatus,
    BookingChannel, PractitionerSchedule,
)
from app.models.diary import DiaryTemplate, DiaryColumn, DiaryBreak, Room, DiaryRoster, WaitingArea
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

        # --- Practice Location ---
        location = db.query(PracticeLocation).filter_by(
            practice_id=practice.id, name="Main Street Surgery"
        ).first()
        if not location:
            location = PracticeLocation(
                practice_id=practice.id,
                name="Main Street Surgery",
                address_line1=practice.address_line1,
                address_suburb=practice.address_suburb,
                address_state=practice.address_state,
                address_postcode=practice.address_postcode,
                phone=practice.phone,
                is_active=True,
            )
            db.add(location)
            db.flush()
            print(f"  Created location: {location.name} ({location.id})")
        else:
            print(f"  Location already exists: {location.id}")

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

        # --- Nurse Practitioner ---
        # Nurses are real Practitioner records so Room 2 is genuinely bookable
        # (appointment contract requires practitioner_id — no resource-only rows).
        nurse = db.query(Practitioner).filter_by(
            practice_id=practice.id, ahpra_number="NMW0001234567"
        ).first()
        if not nurse:
            nurse = Practitioner(
                practice_id=practice.id,
                first_name="Sarah",
                last_name="Chen",
                ahpra_number="NMW0001234567",
                specialty="Nursing",
                is_active=True,
            )
            db.add(nurse)
            db.flush()
            print(f"  Created Nurse: {nurse.first_name} {nurse.last_name} ({nurse.id})")
        else:
            print(f"  Nurse already exists: {nurse.id}")

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

        # --- Practitioner Schedules (Mon-Fri 09:00-17:00, 15-min slots) ---
        for prac, label in [(gp, "GP"), (nurse, "Nurse")]:
            for day in range(5):
                if not db.query(PractitionerSchedule).filter_by(
                    practitioner_id=prac.id, day_of_week=day
                ).first():
                    db.add(PractitionerSchedule(
                        practitioner_id=prac.id,
                        day_of_week=day,
                        start_time=time(9, 0),
                        end_time=time(17, 0),
                        slot_duration_minutes=15,
                    ))
        db.flush()
        print("  Practitioner schedules seeded (GP + Nurse, Mon-Fri 09:00-17:00)")

        # --- Sample appointments for today (so the Schedule tab is non-empty) ---
        today = date.today()
        try:
            practice_tz = ZoneInfo(practice.timezone or "Australia/Sydney")
        except ZoneInfoNotFoundError:
            practice_tz = ZoneInfo("Australia/Sydney")

        def _appt_dt(h: int, m: int) -> datetime:
            return datetime.combine(today, time(h, m)).replace(tzinfo=practice_tz).astimezone(timezone.utc)

        # Margaret 09:00 is seeded as Confirmed so the diary's lifecycle
        # colour rendering (ALL-CAPS + blue) is demonstrated out of the box.
        # The nurse appointment demonstrates Room 2 is genuinely bookable.
        sample_appts = [
            (patient, gp,    _appt_dt(9, 0),  "Hypertension review",   AppointmentStatus.Confirmed, 30),
            (billy,   gp,    _appt_dt(9, 15), "Paediatric check-up",    AppointmentStatus.Booked,    15),
            (patient, gp,    _appt_dt(10, 0), "Care plan review",       AppointmentStatus.Booked,    45),
            (patient, nurse, _appt_dt(9, 30), "Wound dressing",         AppointmentStatus.Booked,    15),
        ]
        for pt, prac, start, reason, init_status, duration_minutes in sample_appts:
            local_start = start.astimezone(practice_tz).time().replace(tzinfo=None)
            exists = db.query(Appointment).filter_by(
                practice_id=practice.id,
                patient_id=pt.id,
                practitioner_id=prac.id,
                appointment_date=today,
                start_time_local=local_start,
            ).first()
            if not exists:
                db.add(Appointment(
                    practice_id=practice.id,
                    patient_id=pt.id,
                    practitioner_id=prac.id,
                    appointment_type_id=std_type.id if std_type else None,
                    booked_by=gp_user.id,
                    start_time=start,
                    appointment_date=today,
                    start_time_local=local_start,
                    duration_minutes=duration_minutes,
                    status=init_status,
                    reason=reason,
                    booked_via=BookingChannel.Receptionist,
                    location_id=location.id,
                ))
            elif exists.status == AppointmentStatus.Booked and init_status != AppointmentStatus.Booked:
                # Idempotent upgrade: apply the demo status if user hasn't changed it
                exists.status = init_status
            if (
                exists
                and exists.reason == reason
                and exists.duration_minutes != duration_minutes
            ):
                exists.duration_minutes = duration_minutes
            if exists and exists.location_id is None:
                exists.location_id = location.id
        db.flush()
        print(f"  Sample appointments seeded for today ({today})")

        # --- Diary Template ---
        tmpl = db.query(DiaryTemplate).filter_by(practice_id=practice.id).first()
        if not tmpl:
            tmpl = DiaryTemplate(
                practice_id=practice.id,
                practice_name=practice.name,
                slot_start=time(9, 0),
                slot_end=time(17, 0),
                slot_interval_minutes=15,
                footer=["Messages:", "Phone Consultations:"],
            )
            db.add(tmpl)
            db.flush()

            columns_data = [
                {
                    "room_label": "Room 1",
                    "assignment": f"Dr Alex Shera",
                    "practitioner_id": gp.id,
                    "practitioner_ahpra": "MED0001234567",
                    "tint_hex": None,
                    "breaks": [
                        ("MORNING TEA", time(10, 45), time(11, 0)),
                        ("LUNCH",       time(13, 0),  time(14, 0)),
                    ],
                },
                {
                    "room_label": "Room 2",
                    "assignment": f"Nurse {nurse.first_name} {nurse.last_name}",
                    "practitioner_id": nurse.id,
                    "practitioner_ahpra": nurse.ahpra_number,
                    "tint_hex": "FFFF99",
                    "breaks": [
                        ("MORNING TEA", time(10, 45), time(11, 0)),
                        ("LUNCH",       time(13, 0),  time(14, 0)),
                    ],
                },
                {
                    "room_label": "Room 3",
                    "assignment": "[Available]",
                    "practitioner_id": None,
                    "practitioner_ahpra": None,
                    "tint_hex": None,
                    "breaks": [
                        ("MORNING TEA", time(10, 45), time(11, 0)),
                        ("LUNCH",       time(13, 0),  time(14, 0)),
                    ],
                },
            ]
            for order, col_data in enumerate(columns_data):
                col = DiaryColumn(
                    template_id=tmpl.id,
                    practice_id=practice.id,
                    display_order=order,
                    room_label=col_data["room_label"],
                    assignment=col_data["assignment"],
                    practitioner_id=col_data["practitioner_id"],
                    practitioner_ahpra=col_data["practitioner_ahpra"],
                    tint_hex=col_data["tint_hex"],
                )
                db.add(col)
                db.flush()
                for brk_order, (label, from_t, to_t) in enumerate(col_data["breaks"]):
                    db.add(DiaryBreak(
                        column_id=col.id,
                        display_order=brk_order,
                        label=label,
                        from_time=from_t,
                        to_time=to_t,
                    ))
            db.flush()
            print(f"  Diary template seeded ({len(columns_data)} columns)")
        else:
            print(f"  Diary template already exists: {tmpl.id}")
            # Idempotent backfill: wire Room 2 column to nurse if it was seeded
            # before the nurse Practitioner row existed (practitioner_id=None).
            from app.models.diary import DiaryColumn as _DC
            room2_col = db.query(_DC).filter_by(
                template_id=tmpl.id, room_label="Room 2"
            ).first()
            if room2_col and room2_col.practitioner_id is None and nurse:
                room2_col.practitioner_id = nurse.id
                room2_col.practitioner_ahpra = nurse.ahpra_number
                room2_col.assignment = f"Nurse {nurse.first_name} {nurse.last_name}"
                db.flush()
                print(f"  Updated Room 2 column -> nurse ({nurse.id})")

        # --- Rooms (mirror the 3 diary template columns) ---
        rooms_data = [
            ("Room 1", 0),
            ("Room 2", 1),
            ("Room 3", 2),
        ]
        rooms = {}
        for room_name, order in rooms_data:
            room = db.query(Room).filter_by(
                practice_id=practice.id, name=room_name
            ).first()
            if not room:
                room = Room(
                    practice_id=practice.id,
                    name=room_name,
                    display_order=order,
                    is_active=True,
                    location_id=location.id,
                )
                db.add(room)
                db.flush()
            elif room.location_id is None:
                room.location_id = location.id
            rooms[room_name] = room
        print(f"  Rooms seeded ({len(rooms)} rooms)")

        # --- DiaryRoster for today ---
        roster_entries = [
            (rooms["Room 1"], gp.id,    "MED0001234567",          None),
            (rooms["Room 2"], nurse.id,  nurse.ahpra_number,       None),
            (rooms["Room 3"], None,      None,                     "[Available]"),
        ]
        for room, prac_id, ahpra, label in roster_entries:
            exists = db.query(DiaryRoster).filter_by(
                practice_id=practice.id,
                room_id=room.id,
                roster_date=today,
            ).first()
            if not exists:
                db.add(DiaryRoster(
                    practice_id=practice.id,
                    room_id=room.id,
                    roster_date=today,
                    practitioner_id=prac_id,
                    practitioner_ahpra=ahpra,
                    label=label,
                ))
            elif exists.practitioner_id is None and prac_id is not None:
                # Backfill: roster was created before nurse existed
                exists.practitioner_id = prac_id
                exists.practitioner_ahpra = ahpra
                exists.label = label
        db.flush()
        print(f"  Diary roster seeded for today ({today})")

        # --- Waiting Areas ---
        waiting_areas_data = [
            ("Main Waiting Room", 0),
            ("Children's Area", 1),
        ]
        waiting_areas = {}
        for area_name, order in waiting_areas_data:
            area = db.query(WaitingArea).filter_by(
                practice_id=practice.id, name=area_name
            ).first()
            if not area:
                area = WaitingArea(
                    practice_id=practice.id,
                    name=area_name,
                    display_order=order,
                    is_active=True,
                    location_id=location.id,
                )
                db.add(area)
                db.flush()
            elif area.location_id is None:
                area.location_id = location.id
            waiting_areas[area_name] = area

        room_default_areas = {
            "Room 1": "Main Waiting Room",
            "Room 2": "Children's Area",
            "Room 3": "Main Waiting Room",
        }
        for room_name, area_name in room_default_areas.items():
            room = rooms.get(room_name)
            area = waiting_areas.get(area_name)
            if room and area and room.default_waiting_area_id != area.id:
                room.default_waiting_area_id = area.id
        db.flush()
        print(f"  Waiting areas seeded ({len(waiting_areas_data)} areas)")

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
