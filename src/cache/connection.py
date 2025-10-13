import asyncio 
from redis.asyncio.client import Redis


class ConnectionManager:
    conn: Redis | None = None 

    @staticmethod
    async def connect(
        host: str,
        port: int,
        password: str | None,
        db: int
    ):
        conn = Redis(
            host=host,
            port=port,
            password=password,
            db=db
        )
        await asyncio.wait_for(conn.ping(), 1)
        ConnectionManager.conn = conn
        
    @staticmethod
    async def get_connection() -> Redis:
        assert ConnectionManager.conn is not None 
        return ConnectionManager.conn

    @staticmethod
    async def close() -> None:
        assert ConnectionManager.conn is not None 
        await ConnectionManager.conn.aclose()
        ConnectionManager.conn = None 

