import asyncio

from src.config import settings
from src.bot.async_bot import async_bot


if __name__ == "__main__":
    # uses fastapi + uvicorn
    asyncio.run(
        async_bot.run_webhooks(
            listen=settings.DOMAIN,
        )
    )
