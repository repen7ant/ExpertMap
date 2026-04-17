from datetime import datetime

from app.models.experience import ReadinessType
from app.models.invitation import InvitationStatus
from app.schemas.experience import ReadinessResponse
from app.schemas.skill import UserSkillResponse
from pydantic import BaseModel, Field


class ExpertCard(BaseModel):
    """Краткая карточка эксперта в результатах поиска."""

    id: int
    name: str
    position: str | None
    department: str | None
    avatar_url: str | None
    total_endorsements: int
    relevant_skills: list[UserSkillResponse]
    readiness: list[ReadinessResponse]
    badges: list[str] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class SearchResponse(BaseModel):
    total: int
    limit: int
    offset: int
    results: list[ExpertCard]


class InvitationCreate(BaseModel):
    hr_id: int
    candidate_id: int
    role: ReadinessType
    event_name: str | None = None
    message: str | None = None


class InvitationRespond(BaseModel):
    status: InvitationStatus = Field(
        ..., description="Только 'accepted' или 'declined'"
    )

    model_config = {"json_schema_extra": {"example": {"status": "accepted"}}}


class UserBriefResponse(BaseModel):
    id: int
    name: str
    email: str
    position: str | None

    model_config = {"from_attributes": True}


class InvitationResponse(BaseModel):
    id: int
    role: ReadinessType
    event_name: str | None
    message: str | None
    status: InvitationStatus
    created_at: datetime
    responded_at: datetime | None
    hr: UserBriefResponse
    candidate: UserBriefResponse

    model_config = {"from_attributes": True}
