from datetime import datetime
from typing import Optional

from app.models.experience import ExperienceType, ReadinessType
from pydantic import BaseModel, ConfigDict


class ExperienceCreate(BaseModel):
    type: ExperienceType
    title: str
    description: Optional[str] = None
    organization: Optional[str] = None
    date: Optional[datetime] = None
    url: Optional[str] = None


class ExperienceResponse(ExperienceCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ReadinessUpdate(BaseModel):
    type: ReadinessType
    is_ready: bool
    note: Optional[str] = None


class ReadinessResponse(ReadinessUpdate):
    id: int
    model_config = ConfigDict(from_attributes=True)
