from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class FAQBase(BaseModel):
    id: int
    parent_id: Optional[int]
    title: str
    question: str
    prompt_template: str
    output_format: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


class FAQNode(FAQBase):
    children: List["FAQNode"] = []

