from app.models.skill import Skill, UserSkill
from app.schemas.skill import SkillCreate
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from fastapi import HTTPException, status


class SkillService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_skill(self, skill_in: SkillCreate) -> Skill:
        new_skill = Skill(**skill_in.model_dump())
        self.db.add(new_skill)
        try:
            await self.db.commit()
            await self.db.refresh(new_skill)
            return new_skill
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(status_code=400, detail="Skill already exists")

    async def get_all_skills(self):
        result = await self.db.execute(select(Skill))
        return result.scalars().all()

    async def delete_skill(self, skill_id: int) -> None:
        """Удаляет навык по ID. Если навык используется — 409."""
        result = await self.db.execute(select(Skill).where(Skill.id == skill_id))
        skill = result.scalar_one_or_none()
        if not skill:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Skill with id {skill_id} not found",
            )

        count = await self.db.scalar(
            select(func.count()).where(UserSkill.skill_id == skill_id)
        )
        if count > 0:
            raise HTTPException(
                status_code=409,
                detail="Cannot delete skill because it is used by users",
            )

        await self.db.delete(skill)
        await self.db.commit()
