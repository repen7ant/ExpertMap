from app.db.session import get_db
from app.models.experience import Experience, Readiness
from app.models.skill import Endorsement, UserSkill
from app.models.user import User
from app.schemas.schemas import (
    EndorsementCreate,
    ExperienceCreate,
    ExperienceResponse,
    ReadinessUpdate,
    UserCreate,
    UserProfileResponse,
    UserResponse,
    UserSkillCreate,
    UserSkillResponse,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, selectinload

from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(tags=["Profile & Expertise"])


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Создание нового сотрудника."""
    new_user = User(**user_in.model_dump())
    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")


@router.get("/users/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(user_id: int, db: AsyncSession = Depends(get_db)):
    """Получение полного профиля сотрудника со всеми навыками, статусами и опытом."""
    stmt = (
        select(User)
        .options(
            selectinload(User.user_skills).joinedload(UserSkill.skill),
            selectinload(User.user_skills).selectinload(UserSkill.endorsements),
            selectinload(User.experiences),
            selectinload(User.readiness),
        )
        .where(User.id == user_id)
    )

    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.post("/users/{user_id}/skills", response_model=UserSkillResponse)
async def add_user_skill(
    user_id: int, skill_in: UserSkillCreate, db: AsyncSession = Depends(get_db)
):
    """Добавление навыка сотруднику."""
    user_skill = UserSkill(
        user_id=user_id, skill_id=skill_in.skill_id, level=skill_in.level
    )
    db.add(user_skill)
    try:
        await db.commit()
        stmt = (
            select(UserSkill)
            .options(joinedload(UserSkill.skill))
            .where(UserSkill.id == user_skill.id)
        )
        result = await db.execute(stmt)
        return result.scalar_one()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Skill already added to this user or skill does not exist",
        )


@router.delete(
    "/users/{user_id}/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_user_skill(
    user_id: int, skill_id: int, db: AsyncSession = Depends(get_db)
):
    """Удаление навыка у сотрудника."""
    stmt = select(UserSkill).where(
        UserSkill.user_id == user_id, UserSkill.skill_id == skill_id
    )
    result = await db.execute(stmt)
    user_skill = result.scalar_one_or_none()

    if not user_skill:
        raise HTTPException(status_code=404, detail="Skill not found for this user")

    await db.delete(user_skill)
    await db.commit()


@router.put("/users/{user_id}/readiness")
async def update_readiness(
    user_id: int, readiness_in: ReadinessUpdate, db: AsyncSession = Depends(get_db)
):
    """Обновление или создание статуса готовности (UPSERT)."""
    stmt = select(Readiness).where(
        Readiness.user_id == user_id, Readiness.type == readiness_in.type
    )
    result = await db.execute(stmt)
    readiness = result.scalar_one_or_none()

    if readiness:
        readiness.is_ready = readiness_in.is_ready
        readiness.note = readiness_in.note
    else:
        readiness = Readiness(user_id=user_id, **readiness_in.model_dump())
        db.add(readiness)

    await db.commit()
    return {"status": "success"}


@router.post("/users/{user_id}/experience", response_model=ExperienceResponse)
async def add_experience(
    user_id: int, exp_in: ExperienceCreate, db: AsyncSession = Depends(get_db)
):
    """Добавление опыта (выступление, менторство и т.д.)."""
    experience = Experience(user_id=user_id, **exp_in.model_dump())
    db.add(experience)
    await db.commit()
    await db.refresh(experience)
    return experience


@router.post("/endorsements", status_code=status.HTTP_201_CREATED)
async def create_endorsement(
    endorsement_in: EndorsementCreate, db: AsyncSession = Depends(get_db)
):
    """Подтверждение навыка (защита от дублей обеспечена UniqueConstraint в БД)."""
    if endorsement_in.from_user_id == endorsement_in.to_user_id:
        raise HTTPException(status_code=400, detail="You cannot endorse yourself")

    new_endorsement = Endorsement(**endorsement_in.model_dump())
    db.add(new_endorsement)

    try:
        await db.commit()
        return {"status": "success", "message": "Skill endorsed"}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=400, detail="You have already endorsed this skill for this user"
        )
