from app.models.skill import SkillCategory, SkillLevel
from pydantic import BaseModel, ConfigDict


class SkillResponse(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class UserSkillCreate(BaseModel):
    skill_id: int
    level: SkillLevel


class UserSkillResponse(BaseModel):
    id: int
    skill: SkillResponse
    level: SkillLevel
    endorsement_count: int
    model_config = ConfigDict(from_attributes=True)


class EndorsementCreate(BaseModel):
    to_user_id: int
    user_skill_id: int
    from_user_id: int


class SkillCreate(BaseModel):
    name: str
    category: SkillCategory


class SkillResponse(BaseModel):
    id: int
    name: str
    category: SkillCategory

    model_config = ConfigDict(from_attributes=True)
