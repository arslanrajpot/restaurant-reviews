from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from .model import FAQ


def _build_active_nodes(db: Session) -> Dict[int, dict]:
    """
    Build plain-dict nodes for all active FAQs, linked to their active children.
    Plain dicts are used so the ORM `children` relationship is never modified
    (appending to it lazily loads all children, inactive ones included, and duplicates them).
    """
    nodes = db.query(FAQ).filter(FAQ.is_active == True).order_by(FAQ.id).all()
    by_id = {
        n.id: {
            "id": n.id,
            "parent_id": n.parent_id,
            "title": n.title,
            "question": n.question,
            "prompt_template": n.prompt_template,
            "output_format": n.output_format,
            "is_active": n.is_active,
            "children": [],
        }
        for n in nodes
    }
    for node in by_id.values():
        if node["parent_id"] in by_id:
            by_id[node["parent_id"]]["children"].append(node)
    return by_id


def get_tree(db: Session) -> List[dict]:
    # Children of an inactive parent are hidden together with it
    return [node for node in _build_active_nodes(db).values() if node["parent_id"] is None]


def get_subtree(db: Session, faq_id: int) -> Optional[dict]:
    return _build_active_nodes(db).get(faq_id)


def get_faq(db: Session, faq_id: int) -> Optional[FAQ]:
    from sqlalchemy.orm import joinedload
    return db.query(FAQ).options(joinedload(FAQ.children)).filter(FAQ.id == faq_id, FAQ.is_active == True).first()


