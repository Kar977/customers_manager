from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from dotenv import load_dotenv
import os
load_dotenv()


USER = os.environ.get("POSTGRES_USER")
PASSWORD = os.environ.get("POSTGRES_PASSWORD")
HOST = os.environ.get("POSTGRES_HOST")
PORT = os.environ.get("POSTGRES_PORT")
DB_NAME = os.environ.get("POSTGRES_NAME")


def get_engine():

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
