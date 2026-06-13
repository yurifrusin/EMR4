from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Connect to your local PostgreSQL database (assuming default port 5432)
# Format: postgresql://username:password@localhost:5432/database_name
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@127.0.0.1:5434/gp_pms_dev"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()