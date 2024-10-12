from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database


def get_engine(user: str, password: str, host: str, port: str, db: str):

    database_url = f"postgresql://{user}:{password}@{host}:{port}/{db}"

    if database_exists(database_url) == False:
        create_database(database_url)

    engine = create_engine(database_url, pool_size=50, echo=False)

    return engine


db_engine = get_engine("postgres", "password", "localhost", "5432", "postgresV4")


SessionLocal = sessionmaker(bind=db_engine)
SecondSessionLocal = sessionmaker(bind=db_engine)


def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
