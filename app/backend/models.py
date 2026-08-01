from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    collection = Column(String)
    fabric_type = Column(String)
    print_width_cm = Column(Integer)
    repeat_size_cm = Column(Integer)
    palette = Column(String)
    parent_id = Column(Integer, ForeignKey("assets.id"), nullable=True)
    image_path = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    parent = relationship("Asset", remote_side=[id], backref="variants")
