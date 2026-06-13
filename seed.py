"""
Dev seed: creates a default Practice, admin User, and GP Practitioner.
Run once after `alembic upgrade head`.

Usage:
    .venv\Scripts\python seed.py
"""
import sys
from app.database import SessionLocal
from app.models.tenancy import Practice, User, Practitioner, UserRole
from app.models.billing import MbsDirectory, SnomedDirectory
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
