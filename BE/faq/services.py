from typing import List, Optional
from sqlalchemy.orm import Session

from .model import FAQ
from .repository import get_tree, get_faq


def get_faq_tree(db: Session) -> List[FAQ]:
    return get_tree(db)


def get_faq_by_id(db: Session, faq_id: int) -> Optional[FAQ]:
    return get_faq(db, faq_id)


def render_faq_prompt(db: Session, faq_id: int) -> tuple[str, Optional[str]]:
    faq = get_faq(db, faq_id)
    if not faq:
        raise ValueError(f"FAQ with id {faq_id} not found")
    
    return faq.prompt_template, faq.output_format
