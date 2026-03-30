import redis.asyncio as redis
import typer


class RedisBridge:
    def __init__(self, REDIS_HOST, REDIS_PORT):
        self.r = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True,
            health_check_interval=6,
            socket_connect_timeout=5,
            socket_timeout=3,
        )

    async def connect(self):
        typer.echo("try connecting to REDIS server")
        await self.r.ping()
        typer.echo("Successfully connected to REDIS server")

    async def write(self, key, value):
        await self.r.set(f"{key}", value, ex=60)

    async def read(self, key):
        val = await self.r.get(f"{key}")
        return val if val is not None else "0"
