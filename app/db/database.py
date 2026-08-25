from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy_utils import create_database, database_exists
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)

if not database_exists(engine.url):
    create_database(engine.url)

class Base(DeclarativeBase):
    pass

# Tự đông thêm cột nếu như bảng đã được tạo
def ensure_club_soft_delete_column():
    columns = {column["name"] for column in inspect(engine).get_columns("clubs")}
    with engine.begin() as connection:
        if "is_deleted" not in columns:
            connection.execute(
                text("ALTER TABLE clubs ADD COLUMN is_deleted BOOLEAN NOT NULL DEFAULT FALSE")
            )
        if "deleted_at" not in columns:
            connection.execute(
                text("ALTER TABLE clubs ADD COLUMN deleted_at DATETIME NULL")
            )
        connection.execute(
            text("UPDATE clubs SET is_deleted = TRUE WHERE deleted_at IS NOT NULL")
        )

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