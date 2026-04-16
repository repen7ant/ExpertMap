from app.db.session import get_db
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends

router = APIRouter(prefix="/api/v1/health", tags=["health"])


@router.get("/db")
async def check_db(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT 1"))
    return {"status": "ok", "result": result.scalar()}
