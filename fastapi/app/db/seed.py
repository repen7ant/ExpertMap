import asyncio
from datetime import date

from app.db.session import get_db
from app.models.experience import Experience, ExperienceType, Readiness, ReadinessType
from app.models.invitation import BadgeType, Invitation, InvitationStatus, UserBadge
from app.models.skill import Endorsement, Skill, SkillCategory, SkillLevel, UserSkill
from app.models.user import DepartmentEnum, User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def seed_data(db: AsyncSession):
    # === 1. Навыки ===
    skills_data = [
        ("FastAPI", SkillCategory.professional),
        ("React", SkillCategory.professional),
        ("PostgreSQL", SkillCategory.professional),
        ("Python", SkillCategory.professional),
        ("Java", SkillCategory.professional),
        ("Usability Testing", SkillCategory.professional),
        ("UX Research", SkillCategory.professional),
        ("Public Speaking", SkillCategory.expert),
        ("Mentoring", SkillCategory.expert),
        ("Technical Writing", SkillCategory.expert),
        ("Conference Speaking", SkillCategory.expert),
        ("Jury Experience", SkillCategory.expert),
    ]

    existing = (await db.execute(select(Skill))).scalars().all()
    if existing:
        print("Данные уже существуют, пропускаем сеедер.")
        return

    skills = {}
    for name, category in skills_data:
        skill = Skill(name=name, category=category)
        db.add(skill)
        await db.flush()
        skills[name] = skill

    await db.commit()

    # === 2. Пользователи ===
    users_data = [
        (
            "Алексей Иванов",
            "alex@company.ru",
            DepartmentEnum.engineering,
            "Senior Backend Developer",
            False,
        ),
        (
            "Мария Смирнова",
            "maria@company.ru",
            DepartmentEnum.design,
            "Lead UX Researcher",
            False,
        ),
        (
            "Дмитрий Петров",
            "dmitry@company.ru",
            DepartmentEnum.engineering,
            "Backend Team Lead",
            False,
        ),
        (
            "Анна Козлова",
            "anna@company.ru",
            DepartmentEnum.hr,
            "HR Business Partner",
            True,
        ),
        (
            "Сергей Морозов",
            "sergey@company.ru",
            DepartmentEnum.engineering,
            "Frontend Developer",
            False,
        ),
        (
            "Екатерина Волкова",
            "ekaterina@company.ru",
            DepartmentEnum.product,
            "Product Manager",
            False,
        ),
        (
            "Игорь Соколов",
            "igor@company.ru",
            DepartmentEnum.engineering,
            "QA Engineer",
            False,
        ),
        (
            "Ольга Лебедева",
            "olga@company.ru",
            DepartmentEnum.marketing,
            "Marketing Specialist",
            False,
        ),
    ]

    users = {}
    for name, email, dept, pos, is_hr in users_data:
        user = User(
            name=name,
            email=email,
            department=dept,
            position=pos,
            is_hr=is_hr,
            is_active=True,
        )
        db.add(user)
        await db.flush()
        users[email] = user

    await db.commit()

    # === 3. UserSkills + Endorsements ===
    # Алексей: FastAPI, Python, Public Speaking
    alex = users["alex@company.ru"]
    user_skills = {}

    # Алексей
    us1 = UserSkill(
        user_id=alex.id, skill_id=skills["FastAPI"].id, level=SkillLevel.expert
    )
    us2 = UserSkill(
        user_id=alex.id, skill_id=skills["Python"].id, level=SkillLevel.expert
    )
    us3 = UserSkill(
        user_id=alex.id,
        skill_id=skills["Public Speaking"].id,
        level=SkillLevel.confident,
    )
    db.add_all([us1, us2, us3])
    await db.flush()

    # Мария
    maria = users["maria@company.ru"]
    us4 = UserSkill(
        user_id=maria.id,
        skill_id=skills["Usability Testing"].id,
        level=SkillLevel.expert,
    )
    us5 = UserSkill(
        user_id=maria.id, skill_id=skills["UX Research"].id, level=SkillLevel.expert
    )
    us6 = UserSkill(
        user_id=maria.id, skill_id=skills["Mentoring"].id, level=SkillLevel.confident
    )
    db.add_all([us4, us5, us6])
    await db.flush()

    # Добавляем подтверждения (endorsements)
    endorsement1 = Endorsement(
        from_user_id=maria.id, to_user_id=alex.id, user_skill_id=us1.id
    )
    endorsement2 = Endorsement(
        from_user_id=maria.id, to_user_id=alex.id, user_skill_id=us2.id
    )
    endorsement3 = Endorsement(
        from_user_id=alex.id, to_user_id=maria.id, user_skill_id=us4.id
    )
    db.add_all([endorsement1, endorsement2, endorsement3])
    await db.commit()

    # === 4. Опыт и готовность ===
    # Алексей
    exp1 = Experience(
        user_id=alex.id,
        type=ExperienceType.talk,
        title="Выступление на HighLoad 2025",
        description="Доклад про высоконагруженные API на FastAPI",
        organization="HighLoad",
        date=date(2025, 3, 15),
        url="https://example.com/talk",
    )
    readiness1 = Readiness(
        user_id=alex.id,
        type=ReadinessType.speaker,
        is_ready=True,
        note="Готов в любой момент",
    )
    readiness2 = Readiness(user_id=alex.id, type=ReadinessType.mentor, is_ready=True)

    # Мария
    readiness3 = Readiness(user_id=maria.id, type=ReadinessType.jury, is_ready=True)
    readiness4 = Readiness(user_id=maria.id, type=ReadinessType.mentor, is_ready=True)

    db.add_all([exp1, readiness1, readiness2, readiness3, readiness4])
    await db.commit()

    # === 5. Бейджи и приглашения (для теста) ===
    badge1 = UserBadge(user_id=alex.id, badge_type=BadgeType.speaker)
    badge2 = UserBadge(user_id=maria.id, badge_type=BadgeType.expert)

    invitation = Invitation(
        hr_id=users["anna@company.ru"].id,
        candidate_id=alex.id,
        role=ReadinessType.speaker,
        message="Приглашаем вас выступить на конференции QA Days в мае",
        event_name="QA Days 2026",
        status=InvitationStatus.pending,
    )

    db.add_all([badge1, badge2, invitation])
    await db.commit()

    print(
        "✅ Seeder успешно выполнен! Создано 8 пользователей, 12 навыков, endorsements, опыт и готовность."
    )


async def main():
    async for db in get_db():
        await seed_data(db)
        break  # один раз


if __name__ == "__main__":
    asyncio.run(main())
