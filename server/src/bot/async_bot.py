import asyncio
from functools import wraps
from typing import Callable

from loguru import logger
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage
from telebot.types import Message

from src.config import settings
from src.crud import get_or_create_user
from src.database import sessionmanager
from src.models import User

GROUPS = ["group", "supergroup", "channel"]


async_bot = AsyncTeleBot(
    settings.TG_BOT_TOKEN,
    parse_mode="HTML",
    state_storage=StateMemoryStorage(),
    disable_web_page_preview=True,
)

bot_info = asyncio.run(async_bot.get_me())
bot_id = bot_info.id
bot_name = bot_info.first_name
bot_username = bot_info.username
bot_link = f"https://t.me/{bot_username}"

logger.info(f"\n\nBot username: {bot_username}\n\n")
logger.info(f"Bot id: {bot_id}\n\n")

asyncio.run(async_bot.set_my_short_description("Play to win 🚀✅"))
asyncio.run(
    async_bot.set_my_description(
        f"I'm {bot_name}, home of the best crash game!\n\nPlay to win 🚀✅",
    )
)


async def _ensure_user(
    func: Callable,
    message: Message,
    *args,
    **kwargs,
):
    if not message.from_user:
        await async_bot.send_message(
            message.chat.id,
            f"An error occured. Please try again later.",
        )
        return
    user_id = message.from_user.id
    # Assign first arg to user if it's a User object
    # & remove the first arg from args...
    # This prevents double-fetching if user is already in args
    if args and isinstance(args[0], User):
        user = args[0]
        args = args[1:]
    else:
        async with sessionmanager.session() as db:
            # logger.info(f"with_wallets: {with_wallets}")
            user = await get_or_create_user(
                db=db,
                id=user_id,
                first_name=message.from_user.first_name,
                username=message.from_user.username,
            )

    if not user:
        logger.error(f"Unable to get or create user with id: {user_id}")
        await async_bot.send_message(
            message.chat.id,
            f"An error occured. Please try again later.",
        )
    # Original handler
    return await func(message, user, *args, **kwargs)


def ensure_user():
    def decorator(func: Callable):
        @wraps(func)
        @logger.catch
        async def wrapper(message: Message, *args, **kwargs):
            if not message.from_user:
                await async_bot.send_message(
                    message.chat.id,
                    f"An error occured. Please try again later.",
                )
                return
            if message.from_user.is_bot:
                return
            return await _ensure_user(
                func,
                message,
                *args,
                **kwargs,
            )

        return wrapper

    return decorator


@async_bot.message_handler(
    func=lambda message: message.chat.type in GROUPS and bot_username in message.text
)
@logger.catch
async def no_response(message):
    """
    This is to prevent bot from responding to commands in groups
    """
    pass
