from typing import List, Optional

from app.models.user import DepartmentEnum
from app.schemas.experience import ExperienceResponse, ReadinessResponse
from app.schemas.skill import UserSkillResponse
from pydantic import BaseModel, ConfigDict, EmailStr


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


class UserProfileResponse(UserResponse):
    user_skills: List[UserSkillResponse] = []
    experiences: List[ExperienceResponse] = []
    readiness: List[ReadinessResponse] = []
