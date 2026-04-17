import enum
from datetime import datetime
from typing import TYPE_CHECKING

from app.models.base import Base
from sqlalchemy import Boolean, DateTime, Enum, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.models.experience import Experience, Readiness
    from app.models.invitation import Invitation, UserBadge
    from app.models.skill import Endorsement, UserSkill


class DepartmentEnum(str, enum.Enum):
    engineering = "engineering"
    design = "design"
    product = "product"
    hr = "hr"
    marketing = "marketing"
    other = "other"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    department: Mapped[DepartmentEnum | None] = mapped_column(
        Enum(DepartmentEnum), nullable=True
    )
    position: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_hr: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # relationships
    user_skills: Mapped[list["UserSkill"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    experiences: Mapped[list["Experience"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    readiness: Mapped[list["Readiness"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    badges: Mapped[list["UserBadge"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    # endorsements given/received
    endorsements_given: Mapped[list["Endorsement"]] = relationship(
        foreign_keys="Endorsement.from_user_id",
        back_populates="from_user",
        cascade="all, delete-orphan",
    )
    endorsements_received: Mapped[list["Endorsement"]] = relationship(
        foreign_keys="Endorsement.to_user_id",
        back_populates="to_user",
        cascade="all, delete-orphan",
    )

    # invitations
    invitations_sent: Mapped[list["Invitation"]] = relationship(
        foreign_keys="Invitation.hr_id",
        back_populates="hr",
        cascade="all, delete-orphan",
    )
    invitations_received: Mapped[list["Invitation"]] = relationship(
        foreign_keys="Invitation.candidate_id",
        back_populates="candidate",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"
