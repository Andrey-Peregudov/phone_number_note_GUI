from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

class Database:
    def __init__(self, database_url: str = "sqlite+aiosqlite:///./database.db", echo: bool = True):
        self.database_url = database_url
        self.engine = create_async_engine(self.database_url, echo=echo)
        self.async_session_maker = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)

    async def create_db_and_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_session(self):
        async with self.async_session_maker() as session:
            yield session

Base = declarative_base()
database = Database()