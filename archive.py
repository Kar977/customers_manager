"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from customers_manager.database_structure.database import get_db, async_engine
from customers_manager.main import app
from customers_manager.database_structure.models import Base

DATABASE_URL = "sqlite:///:memory:"


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False,}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

client = TestClient(app)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

async def setup():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all(bind=engine))


async def test_read_root():
    response = client.get("/customers/")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_slot():
    await setup()
    response = client.get("/customers/slots/available/")
    assert response.status_code == 200


"""