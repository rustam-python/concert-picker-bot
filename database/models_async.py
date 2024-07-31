import asyncio
import datetime
import uuid

import sqlmodel
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

DATABASE_URL = "postgresql+asyncpg://postgres:test@localhost:5433/spotify"

engine = create_async_engine(DATABASE_URL, echo=True, future=True)


async def init_db():
    async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    await asyncio.sleep(0)
    return AsyncSession(engine)


class ScrobbleModel(sqlmodel.SQLModel, table=True):
    id: int = sqlmodel.Field(primary_key=True)
    album: str
    album_mbid: uuid.UUID | None
    artist: str
    artist_mbid: uuid.UUID | None
    date: datetime.datetime
    track: str
    track_mbid: uuid.UUID | None
