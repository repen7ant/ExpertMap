import enum
from datetime import datetime
from typing import TYPE_CHECKING

from app.models.base import Base
from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.user import User


class ExperienceType(str, enum.Enum):
    project = "project"
    talk = "talk"
    mentoring = "mentoring"
    teaching = "teaching"


class ReadinessType(str, enum.Enum):
    speaker = "speaker"
    mentor = "mentor"
    jury = "jury"


class Experience(Base):
    """Опыт сотрудника: проекты, выступления, менторство."""

    __tablename__ = "experiences"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[ExperienceType] = mapped_column(Enum(ExperienceType), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    organization: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )  # конференция, компания и т.д.
    date: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    url: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )  # ссылка на запись/материалы
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # relationships
    user: Mapped["User"] = relationship(back_populates="experiences")

    def __repr__(self) -> str:
        return f"<Experience id={self.id} user_id={self.user_id} type={self.type}>"


class Readiness(Base):
    """Статус готовности сотрудника к активности."""

    __tablename__ = "readiness"
    __table_args__ = (
        # один статус одного типа на пользователя
        UniqueConstraint("user_id", "type", name="uq_user_readiness_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[ReadinessType] = mapped_column(Enum(ReadinessType), nullable=False)
    is_ready: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    note: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )  # дополнительный комментарий
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # relationships
    user: Mapped["User"] = relationship(back_populates="readiness")

    def __repr__(self) -> str:
        return f"<Readiness user_id={self.user_id} type={self.type} is_ready={self.is_ready}>"
