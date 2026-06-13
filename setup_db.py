from database import engine, SessionLocal, Base
import models

def initialize_database():
    print("Creating database tables...")
    # This requires the 'vector' extension to be enabled in your Postgres DB first!
    # You can enable it by running: CREATE EXTENSION IF NOT EXISTS vector; in pgAdmin/psql
    with engine.connect() as conn:
        conn.execute(models.text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()

    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

def seed_directories():
    db = SessionLocal()
    print("Seeding MBS and SNOMED directories...")

    # Seed MBS Items
    mbs_items = [
        models.MbsDirectory(item_number="23", description="Professional attendance (Level B) - < 20 mins", fee="$41.40"),
        models.MbsDirectory(item_number="36", description="Professional attendance (Level C) - at least 20 mins", fee="$80.10"),
        models.MbsDirectory(item_number="44", description="Professional attendance (Level D) - at least 40 mins", fee="$118.00")
    ]

    # Seed SNOMED Codes
    snomed_items = [
        models.SnomedDirectory(concept_id="59621000", term="Essential hypertension"),
        models.SnomedDirectory(concept_id="44054006", term="Type 2 diabetes mellitus"),
        models.SnomedDirectory(concept_id="195967001", term="Asthma")
    ]

    # Insert only if they don't already exist
    for item in mbs_items:
        if not db.query(models.MbsDirectory).filter_by(item_number=item.item_number).first():
            db.add(item)

    for item in snomed_items:
        if not db.query(models.SnomedDirectory).filter_by(concept_id=item.concept_id).first():
            db.add(item)

    db.commit()
    db.close()
    print("Directories seeded successfully.")

if __name__ == "__main__":
    initialize_database()
    seed_directories()