from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.dependencies import get_db
from app.models.billing import MbsDirectory, SnomedDirectory

router = APIRouter(prefix="/api/v1", tags=["search"])


@router.get("/search-mbs")
def search_mbs(q: str = Query(..., min_length=2), db: Session = Depends(get_db)):
    results = db.query(MbsDirectory).filter(
        or_(
            MbsDirectory.item_number.ilike(f"%{q}%"),
            MbsDirectory.description.ilike(f"%{q}%"),
        )
    ).limit(10).all()
    return [{"item_number": r.item_number, "description": r.description, "fee": r.fee} for r in results]


@router.get("/search-snomed")
def search_snomed(q: str = Query(..., min_length=2), db: Session = Depends(get_db)):
    results = db.query(SnomedDirectory).filter(
        or_(
            SnomedDirectory.concept_id.ilike(f"%{q}%"),
            SnomedDirectory.term.ilike(f"%{q}%"),
        )
    ).limit(10).all()
    return [{"concept_id": r.concept_id, "term": r.term} for r in results]
