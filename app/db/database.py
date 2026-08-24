from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy_utils import create_database, database_exists
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)

if not database_exists(engine.url):
    create_database(engine.url)

class Base(DeclarativeBase):
    pass

sessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
)

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()