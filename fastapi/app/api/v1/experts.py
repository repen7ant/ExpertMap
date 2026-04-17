from app.db.session import get_db
from app.models.experience import ReadinessType
from app.models.skill import SkillLevel
from app.schemas.invitation import (
    ExpertCard,
    InvitationCreate,
    InvitationRespond,
    InvitationResponse,
    SearchResponse,
)
from app.services.invitation_service import InvitationService
from app.services.search_service import ExpertSearchService
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends, Query

router = APIRouter()


async def get_search_service(db: AsyncSession = Depends(get_db)):
    return ExpertSearchService(db)


async def get_invitation_service(db: AsyncSession = Depends(get_db)):
    return InvitationService(db)


@router.get(
    "/experts/search",
    tags=["Expert Search"],
    response_model=SearchResponse,
    summary="Поиск экспертов по фильтрам",
    description="""
    Главный эндпоинт для HR-сценария. Позволяет найти нужного эксперта по комбинации фильтров.

    **Примеры запросов:**
    * `/experts/search?skills=Java&activity=speaker`
    * `/experts/search?skills=usability+testing&skills=UX&level=expert`
    * `/experts/search?activity=jury&sort_by=endorsements`
    """,
)
async def search_experts(
    skills: list[str] | None = Query(
        default=None,
        description="Один или несколько навыков. Поиск по вхождению, без учёта регистра.",
        example=["Java", "UX Research"],
    ),
    level: SkillLevel | None = Query(
        default=None,
        description="Уровень владения навыком: basic | confident | expert",
    ),
    activity: ReadinessType | None = Query(
        default=None,
        description="Тип активности: speaker | mentor | jury",
    ),
    ready_only: bool = Query(
        default=True,
        description="Показывать только тех, кто отметил готовность к активности",
    ),
    sort_by: str = Query(
        default="endorsements",
        description="Сортировка: endorsements | name",
        pattern="^(endorsements|name)$",
    ),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: ExpertSearchService = Depends(get_search_service),
):
    experts, total = await service.search_experts(
        skills=skills,
        level=level,
        activity=activity,
        ready_only=ready_only,
        sort_by=sort_by,
        limit=limit,
        offset=offset,
    )

    results = [
        ExpertCard(
            id=e["user"].id,
            name=e["user"].name,
            position=e["user"].position,
            department=e["user"].department,
            avatar_url=e["user"].avatar_url,
            total_endorsements=e["total_endorsements"],
            relevant_skills=e["relevant_skills"],
            readiness=e["user"].readiness,
            badges=[b.badge_type.value for b in e["user"].badges],
        )
        for e in experts
    ]

    return SearchResponse(total=total, limit=limit, offset=offset, results=results)


@router.get(
    "/analytics/skills",
    tags=["Analytics"],
    summary="Покрытие навыков в компании",
    description="Показывает сколько сотрудников владеет каждым навыком и сколько подтверждений он собрал. Помогает HR видеть дефицитные компетенции.",
)
async def skills_analytics(service: ExpertSearchService = Depends(get_search_service)):
    stats = await service.get_skill_stats()
    return [dict(row) for row in stats]


@router.post(
    "/invitations",
    tags=["Invitations"],
    response_model=InvitationResponse,
    summary="Создать приглашение",
    description="HR создаёт приглашение эксперту для участия в конкретной активности (конференция, жюри, менторинг).",
    responses={
        404: {"description": "Кандидат не найден"},
        400: {"description": "Нельзя пригласить себя"},
    },
)
async def create_invitation(
    invitation_in: InvitationCreate,
    service: InvitationService = Depends(get_invitation_service),
):
    return await service.create_invitation(invitation_in)


@router.get(
    "/invitations/{invitation_id}",
    tags=["Invitations"],
    response_model=InvitationResponse,
    summary="Получить статус приглашения",
)
async def get_invitation(
    invitation_id: int,
    service: InvitationService = Depends(get_invitation_service),
):
    return await service.get_invitation(invitation_id)


@router.put(
    "/invitations/{invitation_id}/respond",
    tags=["Invitations"],
    response_model=InvitationResponse,
    summary="Ответить на приглашение (принять / отклонить)",
    description="Кандидат принимает или отклоняет приглашение. Можно ответить только один раз.",
    responses={
        400: {"description": "Приглашение уже получило ответ"},
        403: {"description": "Это приглашение не адресовано вам"},
    },
)
async def respond_to_invitation(
    invitation_id: int,
    respond_in: InvitationRespond,
    candidate_id: int = Query(..., description="ID кандидата, который отвечает"),
    service: InvitationService = Depends(get_invitation_service),
):
    return await service.respond_to_invitation(invitation_id, respond_in, candidate_id)


@router.get(
    "/users/{user_id}/invitations",
    tags=["Invitations"],
    response_model=list[InvitationResponse],
    summary="Список приглашений пользователя",
    description="Возвращает все приглашения — входящие (как кандидат) или исходящие (как HR).",
)
async def get_user_invitations(
    user_id: int,
    as_candidate: bool = Query(
        default=True,
        description="True — входящие приглашения (кандидат). False — исходящие (HR).",
    ),
    service: InvitationService = Depends(get_invitation_service),
):
    return await service.get_user_invitations(user_id, as_candidate)
