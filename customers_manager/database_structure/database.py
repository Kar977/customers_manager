import asyncio

from customers_manager.database_structure.models import (
    Base,
    SlotToHour,
    insert_default_data,
)
from customers_manager.settings import settings
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from customers_manager.settings import settings


async_engine = create_async_engine(settings.ASYNC_DATABASE_URL)

SessionLocal = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db():
    async with SessionLocal() as session:
        yield session


async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def after_create(target, connection, **kw):
    async with SessionLocal() as session:
        await insert_default_data(session)


event.listen(
    SlotToHour.__table__,
    "after_create",
    lambda *args, **kwargs: asyncio.create_task(after_create(*args, **kwargs)),
)
