from typing import List

from app.db.session import get_db
from app.schemas.skill import SkillCreate, SkillResponse
from app.services.skill_service import SkillService
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends, status

router = APIRouter(prefix="/skills", tags=["Skills Dictionary"])


async def get_skill_service(db: AsyncSession = Depends(get_db)):
    return SkillService(db)


@router.post("", response_model=SkillResponse)
async def create_skill(
    skill_in: SkillCreate, service: SkillService = Depends(get_skill_service)
):
    """Добавление нового навыка в глобальный справочник."""
    return await service.create_skill(skill_in)


@router.get("", response_model=List[SkillResponse])
async def list_skills(service: SkillService = Depends(get_skill_service)):
    """Получение списка всех доступных навыков."""
    return await service.get_all_skills()


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(
    skill_id: int, service: SkillService = Depends(get_skill_service)
):
    """Удаление навыка из справочника (только если не используется)."""
    await service.delete_skill(skill_id)
    return None  # 204 No Content
