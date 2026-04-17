from app.models.experience import Experience, Readiness
from app.models.skill import Endorsement, UserSkill
from app.models.user import User
from app.schemas.experience import ExperienceCreate, ReadinessUpdate
from app.schemas.skill import EndorsementCreate, UserSkillCreate
from app.schemas.user import UserCreate, UserRegister, UserUpdate
from app.services.auth_service import get_password_hash
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, selectinload

from fastapi import HTTPException


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_user(self, user_in: UserRegister) -> User:
        """Регистрация обычного сотрудника (is_hr=False)."""
        hashed_password = get_password_hash(user_in.password)
        new_user = User(
            email=user_in.email,
            hashed_password=hashed_password,
            is_hr=False,
        )
        self.db.add(new_user)
        try:
            await self.db.commit()
            await self.db.refresh(new_user)
            return new_user
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(status_code=400, detail="Email already registered")

    async def update_user(self, user_id: int, user_in: UserUpdate) -> User:
        """Частичное обновление профиля пользователя."""
        user = await self.db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        update_data = user_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def create_hr_user(self, user_in: UserCreate) -> User:
        """Создание HR-сотрудника (is_hr=True)."""
        user_data = user_in.model_dump()
        hashed_password = get_password_hash(user_data.pop("password"))

        new_user = User(**user_data, hashed_password=hashed_password, is_hr=True)
        self.db.add(new_user)
        try:
            await self.db.commit()
            await self.db.refresh(new_user)
            return new_user
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(status_code=400, detail="Email already registered")

    async def get_users(self, limit: int = 100, offset: int = 0) -> list[User]:
        """Получение списка всех пользователей с пагинацией."""
        stmt = select(User).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_user_profile(self, user_id: int) -> User:
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
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def add_skill(self, user_id: int, skill_in: UserSkillCreate) -> UserSkill:
        user_skill = UserSkill(user_id=user_id, **skill_in.model_dump())
        self.db.add(user_skill)
        try:
            await self.db.commit()

            stmt = (
                select(UserSkill)
                .options(
                    joinedload(UserSkill.skill), selectinload(UserSkill.endorsements)
                )
                .where(UserSkill.id == user_skill.id)
            )
            result = await self.db.execute(stmt)
            return result.scalar_one()
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Skill error: check if skill exists or already added",
            )

    async def remove_skill(self, user_id: int, skill_id: int):
        stmt = select(UserSkill).where(
            UserSkill.user_id == user_id, UserSkill.skill_id == skill_id
        )
        result = await self.db.execute(stmt)
        user_skill = result.scalar_one_or_none()
        if not user_skill:
            raise HTTPException(status_code=404, detail="Skill not found")
        await self.db.delete(user_skill)
        await self.db.commit()

    async def update_readiness(self, user_id: int, readiness_in: ReadinessUpdate):
        stmt = select(Readiness).where(
            Readiness.user_id == user_id, Readiness.type == readiness_in.type
        )
        result = await self.db.execute(stmt)
        readiness = result.scalar_one_or_none()

        if readiness:
            readiness.is_ready = readiness_in.is_ready
            readiness.note = readiness_in.note
        else:
            readiness = Readiness(user_id=user_id, **readiness_in.model_dump())
            self.db.add(readiness)
        await self.db.commit()

    async def add_experience(
        self, user_id: int, exp_in: ExperienceCreate
    ) -> Experience:
        experience = Experience(user_id=user_id, **exp_in.model_dump())
        self.db.add(experience)
        await self.db.commit()
        await self.db.refresh(experience)
        return experience

    async def endorse_skill(self, endorsement_in: EndorsementCreate):
        """Подтверждение навыка с полной валидацией."""
        user_skill = await self.db.get(UserSkill, endorsement_in.user_skill_id)
        if user_skill is None:
            raise HTTPException(status_code=404, detail="User skill not found")

        if user_skill.user_id != endorsement_in.to_user_id:
            raise HTTPException(400, "to_user_id must match user_skill owner")

        if endorsement_in.from_user_id == endorsement_in.to_user_id:
            raise HTTPException(status_code=400, detail="Self-endorsement not allowed")

        new_endorsement = Endorsement(**endorsement_in.model_dump())
        self.db.add(new_endorsement)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(status_code=400, detail="Already endorsed")
