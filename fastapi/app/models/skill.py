import enum
from datetime import datetime
from typing import TYPE_CHECKING

from app.models.base import Base
from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.user import User


class SkillCategory(str, enum.Enum):
    professional = "professional"
    expert = "expert"


class SkillLevel(str, enum.Enum):
    basic = "basic"
    confident = "confident"
    expert = "expert"


class Skill(Base):
    """Справочник навыков."""

    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    category: Mapped[SkillCategory] = mapped_column(Enum(SkillCategory), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # relationships
    user_skills: Mapped[list["UserSkill"]] = relationship(back_populates="skill")

    def __repr__(self) -> str:
        return f"<Skill id={self.id} name={self.name}>"


class UserSkill(Base):
    """Навык конкретного сотрудника с уровнем владения."""

    __tablename__ = "user_skills"
    __table_args__ = (
        UniqueConstraint("user_id", "skill_id", "level", name="uq_user_skill_level"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id"), nullable=False, index=True
    )
    level: Mapped[SkillLevel] = mapped_column(
        Enum(SkillLevel), nullable=False, default=SkillLevel.basic
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # relationships
    user: Mapped["User"] = relationship(back_populates="user_skills")
    skill: Mapped["Skill"] = relationship(back_populates="user_skills")
    endorsements: Mapped[list["Endorsement"]] = relationship(
        back_populates="user_skill", cascade="all, delete-orphan"
    )

    @property
    def endorsement_count(self) -> int:
        return len(self.endorsements)

    def __repr__(self) -> str:
        return f"<UserSkill user_id={self.user_id} skill_id={self.skill_id} level={self.level}>"


class Endorsement(Base):
    """Подтверждение навыка сотрудника другим сотрудником."""

    __tablename__ = "endorsements"
    __table_args__ = (
        # один пользователь — одно подтверждение конкретного навыка конкретного человека
        UniqueConstraint("from_user_id", "user_skill_id", name="uq_endorsement"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    from_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    to_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_skill_id: Mapped[int] = mapped_column(
        ForeignKey("user_skills.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # relationships
    from_user: Mapped["User"] = relationship(
        foreign_keys=[from_user_id], back_populates="endorsements_given"
    )
    to_user: Mapped["User"] = relationship(
        foreign_keys=[to_user_id], back_populates="endorsements_received"
    )
    user_skill: Mapped["UserSkill"] = relationship(back_populates="endorsements")

    def __repr__(self) -> str:
        return f"<Endorsement from={self.from_user_id} to={self.to_user_id} skill={self.user_skill_id}>"
