from datetime import datetime

from app.models.invitation import Invitation, InvitationStatus
from app.models.user import User
from app.schemas.invitation import InvitationCreate, InvitationRespond
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fastapi import HTTPException


class InvitationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_invitation_with_relations(self, invitation_id: int) -> Invitation:
        stmt = (
            select(Invitation)
            .options(
                joinedload(Invitation.hr),
                joinedload(Invitation.candidate),
            )
            .where(Invitation.id == invitation_id)
        )
        result = await self.db.execute(stmt)
        invitation = result.scalar_one_or_none()
        if not invitation:
            raise HTTPException(status_code=404, detail="Invitation not found")
        return invitation

    async def create_invitation(self, invitation_in: InvitationCreate) -> Invitation:
        candidate = await self.db.get(User, invitation_in.candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")

        if invitation_in.hr_id == invitation_in.candidate_id:
            raise HTTPException(status_code=400, detail="Cannot invite yourself")

        invitation = Invitation(**invitation_in.model_dump())
        self.db.add(invitation)
        await self.db.commit()

        return await self._get_invitation_with_relations(invitation.id)

    async def get_invitation(self, invitation_id: int) -> Invitation:
        return await self._get_invitation_with_relations(invitation_id)

    async def respond_to_invitation(
        self, invitation_id: int, respond_in: InvitationRespond, candidate_id: int
    ) -> Invitation:
        invitation = await self.db.get(Invitation, invitation_id)
        if not invitation:
            raise HTTPException(status_code=404, detail="Invitation not found")

        if invitation.candidate_id != candidate_id:
            raise HTTPException(status_code=403, detail="Not your invitation")

        if invitation.status != InvitationStatus.pending:
            raise HTTPException(
                status_code=400,
                detail=f"Invitation already {invitation.status.value}",
            )

        invitation.status = respond_in.status
        invitation.responded_at = datetime.utcnow()
        await self.db.commit()

        return await self._get_invitation_with_relations(invitation_id)

    async def get_user_invitations(
        self, user_id: int, as_candidate: bool = True
    ) -> list[Invitation]:
        stmt = select(Invitation).options(
            joinedload(Invitation.hr),
            joinedload(Invitation.candidate),
        )
        if as_candidate:
            stmt = stmt.where(Invitation.candidate_id == user_id)
        else:
            stmt = stmt.where(Invitation.hr_id == user_id)

        stmt = stmt.order_by(Invitation.created_at.desc())
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()
