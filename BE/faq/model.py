from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from database import Base


class FAQ(Base):
    __tablename__ = "faqs"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("faqs.id"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    question = Column(Text, nullable=False)
    prompt_template = Column(Text, nullable=False)
    output_format = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now())

    parent = relationship("FAQ", remote_side=[id], backref="children")


