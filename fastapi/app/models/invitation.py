import enum
from datetime import datetime
from typing import TYPE_CHECKING

from app.models.base import Base
from app.models.experience import ReadinessType
from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.user import User


class InvitationStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"


class BadgeType(str, enum.Enum):
    speaker = "speaker"
    mentor = "mentor"
    expert = "expert"


class Invitation(Base):
    """Приглашение HR к эксперту на активность."""

    __tablename__ = "invitations"

    id: Mapped[int] = mapped_column(primary_key=True)
    hr_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[ReadinessType] = mapped_column(Enum(ReadinessType), nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    event_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[InvitationStatus] = mapped_column(
        Enum(InvitationStatus), nullable=False, default=InvitationStatus.pending
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    responded_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # relationships
    hr: Mapped["User"] = relationship(
        foreign_keys=[hr_id], back_populates="invitations_sent"
    )
    candidate: Mapped["User"] = relationship(
        foreign_keys=[candidate_id], back_populates="invitations_received"
    )

    def __repr__(self) -> str:
        return f"<Invitation id={self.id} candidate={self.candidate_id} role={self.role} status={self.status}>"


class UserBadge(Base):
    """Награды (бейджи) сотрудника."""

    __tablename__ = "user_badges"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    badge_type: Mapped[BadgeType] = mapped_column(Enum(BadgeType), nullable=False)
    awarded_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # relationships
    user: Mapped["User"] = relationship(back_populates="badges")

    def __repr__(self) -> str:
        return f"<UserBadge user_id={self.user_id} badge={self.badge_type}>"
