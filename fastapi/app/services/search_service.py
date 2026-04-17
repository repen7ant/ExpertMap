from app.models.experience import Readiness, ReadinessType
from app.models.skill import Endorsement, Skill, SkillLevel, UserSkill
from app.models.user import User
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class ExpertSearchService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def search_experts(
        self,
        skills: list[str] | None = None,
        level: SkillLevel | None = None,
        activity: ReadinessType | None = None,
        ready_only: bool = True,
        sort_by: str = "endorsements",
        limit: int = 20,
        offset: int = 0,
    ) -> list[dict]:
        """
        Ищет экспертов по фильтрам.
        Возвращает список пользователей с агрегированными данными.
        """

        # --- базовый запрос: users у которых есть хотя бы один навык ---
        stmt = (
            select(User)
            .join(User.user_skills)
            .join(UserSkill.skill)
            .options(
                selectinload(User.user_skills).joinedload(UserSkill.skill),
                selectinload(User.user_skills).selectinload(UserSkill.endorsements),
                selectinload(User.readiness),
                selectinload(User.experiences),
                selectinload(User.badges),
            )
            .where(User.is_active == True)  # noqa: E712
            .distinct()
        )

        # --- фильтр по навыкам (имя навыка, case-insensitive) ---
        if skills:
            skill_filters = [Skill.name.ilike(f"%{s.strip()}%") for s in skills]
            # пользователь должен иметь хотя бы один из указанных навыков
            from sqlalchemy import or_

            stmt = stmt.where(or_(*skill_filters))

        # --- фильтр по уровню навыка ---
        if level:
            stmt = stmt.where(UserSkill.level == level)

        # --- фильтр по готовности к активности ---
        if activity or ready_only:
            readiness_subq = (
                select(Readiness.user_id).where(Readiness.is_ready == True)  # noqa: E712
            )
            if activity:
                readiness_subq = readiness_subq.where(Readiness.type == activity)
            stmt = stmt.where(User.id.in_(readiness_subq))

        result = await self.db.execute(stmt)
        users = result.unique().scalars().all()

        # --- агрегация: считаем подтверждения и формируем ответ ---
        experts = []
        for user in users:
            total_endorsements = sum(len(us.endorsements) for us in user.user_skills)

            # находим релевантные навыки (те, что совпали с фильтром)
            relevant_skills = user.user_skills
            if skills:
                relevant_skills = [
                    us
                    for us in user.user_skills
                    if any(s.strip().lower() in us.skill.name.lower() for s in skills)
                ] or user.user_skills  # fallback — все навыки

            experts.append(
                {
                    "user": user,
                    "total_endorsements": total_endorsements,
                    "relevant_skills": relevant_skills,
                }
            )

        # --- сортировка ---
        if sort_by == "endorsements":
            experts.sort(key=lambda x: x["total_endorsements"], reverse=True)
        elif sort_by == "name":
            experts.sort(key=lambda x: x["user"].name)

        # --- пагинация ---
        total = len(experts)
        experts = experts[offset : offset + limit]

        return experts, total

    async def get_skill_stats(self) -> list[dict]:
        """Аналитика: сколько экспертов по каждому навыку."""
        stmt = (
            select(
                Skill.name,
                Skill.category,
                func.count(UserSkill.id).label("user_count"),
                func.count(Endorsement.id).label("endorsement_count"),
            )
            .join(UserSkill, UserSkill.skill_id == Skill.id, isouter=True)
            .join(Endorsement, Endorsement.user_skill_id == UserSkill.id, isouter=True)
            .group_by(Skill.id, Skill.name, Skill.category)
            .order_by(func.count(UserSkill.id).desc())
        )
        result = await self.db.execute(stmt)
        return result.mappings().all()
