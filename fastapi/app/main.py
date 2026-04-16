from app.api.v1.health import router as health_router
from app.api.v1.skills import router as skill_router
from app.api.v1.users import router as user_router
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI

app = FastAPI(title="ExpertMap API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(user_router)
app.include_router(skill_router)
