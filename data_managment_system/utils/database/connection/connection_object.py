from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine,
    AsyncSessionTransaction,
)
from sqlalchemy.schema import CreateSchema
from dataclasses import dataclass


from .credential_object import RDBCredential
from ..models import Base


@dataclass
class RDBConnection:
    engine: AsyncEngine
    async_session_local: AsyncSession

    @classmethod
    def create(cls, credentials: RDBCredential):
        async_engine = create_async_engine(credentials.get_connection_string())

        async_session = async_sessionmaker(
            bind=async_engine, autoflush=False, autocommit=False
        )

        return cls(engine=async_engine, async_session_local=async_session)

    async def get_session(self) -> AsyncSessionTransaction:
        return self.async_session_local.begin()
