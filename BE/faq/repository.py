from typing import List, Optional
from sqlalchemy.orm import Session

from .model import FAQ


def get_tree(db: Session) -> List[FAQ]:
    nodes = db.query(FAQ).filter(FAQ.is_active == True).all()
    by_id = {n.id: n for n in nodes}
    roots = []
    for n in nodes:
        if n.parent_id and n.parent_id in by_id:
            by_id[n.parent_id].children.append(n)
        else:
            roots.append(n)
    return roots


def get_faq(db: Session, faq_id: int) -> Optional[FAQ]:
    from sqlalchemy.orm import joinedload
    return db.query(FAQ).options(joinedload(FAQ.children)).filter(FAQ.id == faq_id, FAQ.is_active == True).first()


