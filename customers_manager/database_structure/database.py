from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from dotenv import load_dotenv
import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
load_dotenv()



USER = os.environ.get("POSTGRES_USER")
PASSWORD = os.environ.get("POSTGRES_PASSWORD")
HOST = os.environ.get("POSTGRES_HOST")
PORT = os.environ.get("POSTGRES_PORT")
DB_NAME = os.environ.get("POSTGRES_NAME")

SYNC_DATABASE_URL = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"
ASYNC_DATABASE_URL = f"postgresql+asyncpg://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"

def init_database():
    sync_engine = create_engine(SYNC_DATABASE_URL)
    if not database_exists(sync_engine.url):
        create_database(sync_engine.url)

init_database()

sync_engine = create_engine(SYNC_DATABASE_URL)
async_engine = create_async_engine(ASYNC_DATABASE_URL)

SessionLocal = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with SessionLocal() as session:
        yield session







"""def get_engine():

    database_url = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"

    if database_exists(database_url) == False:
        create_database(database_url)

    engine = create_engine(database_url, pool_size=50, echo=False)

    return engine


db_engine = get_engine()


SessionLocal = sessionmaker(bind=db_engine)
SecondSessionLocal = sessionmaker(bind=db_engine)


def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
"""