from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DesignBase(BaseModel):
    name: Optional[str] = None
    filename: str
    dominant_colors: Optional[str] = None
    fabric_type: Optional[str] = None
    print_width_cm: Optional[int] = None
    repeat_size_cm: Optional[int] = None
    caption: Optional[str] = None


class DesignCreate(DesignBase):
    pass


class DesignResponse(DesignBase):
    id: int
    uploaded_at: datetime
    image_url: Optional[str] = None
    type: str = "design"

    class Config:
        from_attributes = True


class VariantBase(BaseModel):
    parent_id: int
    prompt_used: Optional[str] = None
    lora_used: Optional[str] = None
    filename: str


class VariantCreate(VariantBase):
    pass


class VariantResponse(VariantBase):
    id: int
    created_at: datetime
    image_url: Optional[str] = None
    type: str = "variant"

    class Config:
        from_attributes = True


class ExportBase(BaseModel):
    variant_id: int
    dpi: Optional[int] = None
    color_mode: Optional[str] = None
    file_path: str


class ExportResponse(ExportBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
