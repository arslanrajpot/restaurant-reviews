from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from .schema import FAQNode
from .services import get_faq_tree, get_faq_by_id



router = APIRouter(prefix="/faqs", tags=["faqs"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[FAQNode])
def list_faqs(db: Session = Depends(get_db)):
    return get_faq_tree(db)


@router.get("/{faq_id}", response_model=FAQNode)
def get_faq_node(faq_id: int, db: Session = Depends(get_db)):
    node = get_faq_by_id(db, faq_id)
    if not node:
        raise HTTPException(status_code=404, detail="FAQ not found")
    return node

