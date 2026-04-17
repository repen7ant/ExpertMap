from app.db.session import get_db
from app.schemas.auth import Token
from app.schemas.user import UserRegister, UserResponse
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix="/auth", tags=["Auth"])


async def get_auth_service(db: AsyncSession = Depends(get_db)):
    return AuthService(db)


async def get_user_service(db: AsyncSession = Depends(get_db)):
    return UserService(db)


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
):
    user = await service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return await service.create_access_token(user)


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    user_in: UserRegister,
    service: UserService = Depends(get_user_service),
):
    """
    Регистрация нового сотрудника.
    """
    return await service.register_user(user_in)
