from app.db.session import get_db
from app.schemas.experience import ExperienceCreate, ExperienceResponse, ReadinessUpdate
from app.schemas.skill import EndorsementCreate, UserSkillCreate, UserSkillResponse
from app.schemas.user import UserCreate, UserProfileResponse, UserResponse
from app.services.user_service import UserService
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends, status

router = APIRouter(tags=["Profile & Expertise"])


async def get_user_service(db: AsyncSession = Depends(get_db)):
    return UserService(db)


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate, service: UserService = Depends(get_user_service)
):
    return await service.create_user(user_in)


@router.get("/users/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: int, service: UserService = Depends(get_user_service)
):
    return await service.get_user_profile(user_id)


@router.post("/users/{user_id}/skills", response_model=UserSkillResponse)
async def add_skill(
    user_id: int,
    skill_in: UserSkillCreate,
    service: UserService = Depends(get_user_service),
):
    return await service.add_skill(user_id, skill_in)


@router.delete(
    "/users/{user_id}/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_skill(
    user_id: int, skill_id: int, service: UserService = Depends(get_user_service)
):
    await service.remove_skill(user_id, skill_id)


@router.put("/users/{user_id}/readiness")
async def update_readiness(
    user_id: int,
    readiness_in: ReadinessUpdate,
    service: UserService = Depends(get_user_service),
):
    await service.update_readiness(user_id, readiness_in)
    return {"status": "success"}


@router.post("/users/{user_id}/experience", response_model=ExperienceResponse)
async def add_experience(
    user_id: int,
    exp_in: ExperienceCreate,
    service: UserService = Depends(get_user_service),
):
    return await service.add_experience(user_id, exp_in)


@router.post("/endorsements", status_code=status.HTTP_201_CREATED)
async def endorse_skill(
    endorsement_in: EndorsementCreate, service: UserService = Depends(get_user_service)
):
    await service.endorse_skill(endorsement_in)
    return {"status": "success"}
