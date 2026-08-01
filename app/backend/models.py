from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime, timezone

from database import Base


def _utcnow():
    return datetime.now(timezone.utc)


class Design(Base):
    __tablename__ = "designs"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    filename = Column(String, nullable=False, unique=True)
    dominant_colors = Column(String)
    fabric_type = Column(String)
    print_width_cm = Column(Integer)
    repeat_size_cm = Column(Integer)
    caption = Column(String)
    uploaded_at = Column(DateTime, default=_utcnow)


class Variant(Base):
    __tablename__ = "variants"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("designs.id"))
    prompt_used = Column(String)
    lora_used = Column(String)
    filename = Column(String)
    created_at = Column(DateTime, default=_utcnow)


class Export(Base):
    __tablename__ = "exports"
    id = Column(Integer, primary_key=True)
    variant_id = Column(Integer, ForeignKey("variants.id"))
    dpi = Column(Integer)
    color_mode = Column(String)
    file_path = Column(String)
    created_at = Column(DateTime, default=_utcnow)
