from app.db.session import get_db
from app.schemas.experience import ExperienceCreate, ExperienceResponse, ReadinessUpdate
from app.schemas.skill import EndorsementCreate, UserSkillCreate, UserSkillResponse
from app.schemas.user import UserCreate, UserProfileResponse, UserResponse
from app.services.user_service import UserService
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends, status

router = APIRouter()


async def get_user_service(db: AsyncSession = Depends(get_db)):
    return UserService(db)


@router.post(
    "/users",
    tags=["Users"],
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать профиль сотрудника",
    description="Регистрирует нового сотрудника в системе ExpertMap.",
    responses={400: {"description": "Email уже зарегистрирован в системе"}},
)
async def create_user(
    user_in: UserCreate, service: UserService = Depends(get_user_service)
):
    return await service.create_user(user_in)


@router.get(
    "/users/{user_id}",
    tags=["Users"],
    response_model=UserProfileResponse,
    summary="Получить полный профиль сотрудника",
    description="""
    Возвращает всю агрегированную информацию о сотруднике:
    * Базовые данные (имя, должность, отдел)
    * Список добавленных навыков с уровнем владения и **количеством подтверждений**
    * Профессиональный опыт (выступления, проекты)
    * Статусы готовности (ментор, спикер и т.д.)
    """,
    responses={404: {"description": "Пользователь не найден"}},
)
async def get_user_profile(
    user_id: int, service: UserService = Depends(get_user_service)
):
    return await service.get_user_profile(user_id)


@router.post(
    "/users/{user_id}/skills",
    tags=["Profile & Expertise"],
    response_model=UserSkillResponse,
    summary="Добавить навык сотруднику",
    description="Привязывает навык из глобального справочника к профилю сотрудника с указанием уровня самооценки (базовый, уверенный, эксперт).",
    responses={
        400: {
            "description": "Навык уже добавлен этому пользователю или ID навыка не существует"
        }
    },
)
async def add_skill(
    user_id: int,
    skill_in: UserSkillCreate,
    service: UserService = Depends(get_user_service),
):
    return await service.add_skill(user_id, skill_in)


@router.delete(
    "/users/{user_id}/skills/{skill_id}",
    tags=["Profile & Expertise"],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить навык из профиля",
    description="Убирает навык из профиля сотрудника. **Внимание:** при этом каскадно удалятся все подтверждения (endorsements) от коллег для этого навыка.",
    responses={404: {"description": "Навык не найден в профиле данного пользователя"}},
)
async def remove_skill(
    user_id: int, skill_id: int, service: UserService = Depends(get_user_service)
):
    await service.remove_skill(user_id, skill_id)


@router.put(
    "/users/{user_id}/readiness",
    tags=["Profile & Expertise"],
    summary="Обновить статус готовности (UPSERT)",
    description="Устанавливает или обновляет статус готовности сотрудника к определенной активности (например, стать ментором или спикером). Если статус для этого типа уже существует — он будет перезаписан.",
)
async def update_readiness(
    user_id: int,
    readiness_in: ReadinessUpdate,
    service: UserService = Depends(get_user_service),
):
    await service.update_readiness(user_id, readiness_in)
    return {"status": "success"}


@router.post(
    "/users/{user_id}/experience",
    tags=["Profile & Expertise"],
    response_model=ExperienceResponse,
    summary="Добавить опыт или проект",
    description="Добавляет запись о конкретном профессиональном опыте сотрудника (например: участие в конференции QA Days, внутренний проект по рефакторингу).",
)
async def add_experience(
    user_id: int,
    exp_in: ExperienceCreate,
    service: UserService = Depends(get_user_service),
):
    return await service.add_experience(user_id, exp_in)


@router.post(
    "/endorsements",
    tags=["Profile & Expertise"],
    status_code=status.HTTP_201_CREATED,
    summary="Подтвердить навык коллеги (Endorse)",
    description="""
    Создает подтверждение (endorsement) навыка другого сотрудника. Это повышает "вес" экспертизы в поиске.
    
    **Ограничения:**
    * Один человек может подтвердить конкретный навык коллеги только один раз.
    * Нельзя подтвердить навык самому себе (self-endorsement).
    """,
    responses={
        400: {
            "description": "Попытка подтвердить свой собственный навык или дублирование подтверждения"
        }
    },
)
async def endorse_skill(
    endorsement_in: EndorsementCreate, service: UserService = Depends(get_user_service)
):
    await service.endorse_skill(endorsement_in)
    return {"status": "success"}
