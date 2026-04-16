from datetime import datetime
from typing import List, Optional

from app.models.experience import ExperienceType, ReadinessType
from app.models.skill import SkillLevel
from app.models.user import DepartmentEnum
from pydantic import BaseModel, ConfigDict, EmailStr

# --- Base Models ---


class UserBase(BaseModel):
    name: str
    email: EmailStr
    department: Optional[DepartmentEnum] = None
    position: Optional[str] = None
    bio: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class SkillResponse(BaseModel):
    id: int
    name: str


class UserSkillCreate(BaseModel):
    skill_id: int
    level: SkillLevel


class UserSkillResponse(BaseModel):
    id: int
    skill: SkillResponse
    level: SkillLevel
    endorsement_count: int

    model_config = ConfigDict(from_attributes=True)


class ReadinessUpdate(BaseModel):
    type: ReadinessType
    is_ready: bool
    note: Optional[str] = None


class ReadinessResponse(ReadinessUpdate):
    id: int

    model_config = ConfigDict(from_attributes=True)


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


class EndorsementCreate(BaseModel):
    to_user_id: int
    user_skill_id: int
    from_user_id: int


# --- Profile Response (Aggregated) ---


class UserProfileResponse(UserResponse):
    user_skills: List[UserSkillResponse] = []
    experiences: List[ExperienceResponse] = []
    readiness: List[ReadinessResponse] = []

    model_config = ConfigDict(from_attributes=True)
