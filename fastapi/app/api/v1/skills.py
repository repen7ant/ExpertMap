from typing import List

from app.db.session import get_db
from app.schemas.skill import SkillCreate, SkillResponse
from app.services.skill_service import SkillService
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends, status

router = APIRouter(prefix="/skills", tags=["Skills Dictionary"])


async def get_skill_service(db: AsyncSession = Depends(get_db)):
    return SkillService(db)


@router.post(
    "",
    response_model=SkillResponse,
    summary="Создать новый навык в справочнике",
    description="Добавляет новый навык (например, 'FastAPI' или 'Public Speaking') в глобальный справочник компании.",
    responses={
        400: {
            "description": "Навык с таким именем уже существует (уникальное ограничение)"
        }
    },
)
async def create_skill(
    skill_in: SkillCreate, service: SkillService = Depends(get_skill_service)
):
    return await service.create_skill(skill_in)


@router.get(
    "",
    response_model=List[SkillResponse],
    summary="Получить список всех навыков",
    description="Возвращает полный список доступных навыков из базы. Используется на фронтенде для отрисовки выпадающих списков при добавлении навыка в профиль.",
)
async def list_skills(service: SkillService = Depends(get_skill_service)):
    return await service.get_all_skills()


@router.delete(
    "/{skill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить навык из справочника",
    description="Удаляет навык из глобального справочника. **Внимание:** удалить навык можно только в том случае, если он еще не привязан ни к одному пользователю.",
    responses={
        400: {
            "description": "Невозможно удалить навык, так как он уже используется в профилях сотрудников"
        },
        404: {"description": "Навык не найден"},
    },
)
async def delete_skill(
    skill_id: int, service: SkillService = Depends(get_skill_service)
):
    await service.delete_skill(skill_id)
    return None
