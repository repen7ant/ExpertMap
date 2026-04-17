from app.api.v1.experts import router as expert_router
from app.api.v1.health import router as health_router
from app.api.v1.skills import router as skill_router
from app.api.v1.users import router as user_router
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI

description = """
**ExpertMap API** помогает HR и сотрудникам находить внутренних экспертов.

## Пользователи (Users)
* Создание профилей сотрудников.
* Получение полной информации о компетенциях.

## Справочник навыков (Skills)
* Управление глобальным списком технологий и софт-скиллов.

## Экспертиза (Expertise)
* Подтверждение навыков (Endorsements).
* Управление статусами готовности (Speaker/Mentor).
"""

app = FastAPI(
    title="ExpertMap API",
    description=description,
    openapi_tags=[
        {"name": "Users", "description": "Профили сотрудников и их личные данные"},
        {
            "name": "Skills Dictionary",
            "description": "Глобальный справочник доступных навыков",
        },
        {
            "name": "Profile & Expertise",
            "description": "Связи пользователя с навыками и опытом",
        },
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(user_router)
app.include_router(skill_router)
app.include_router(expert_router)
