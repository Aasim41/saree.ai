from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class AssetBase(BaseModel):
    name: str
    collection: str
    fabric_type: str
    print_width_cm: int
    repeat_size_cm: int
    palette: str
    parent_id: Optional[int] = None
    image_path: str

class AssetCreate(AssetBase):
    pass

class AssetResponse(AssetBase):
    id: int
    created_at: datetime
    image_url: Optional[str] = None # Added dynamically in FastAPI

    class Config:
        from_attributes = True
