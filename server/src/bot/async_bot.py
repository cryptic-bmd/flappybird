import asyncio
from functools import wraps
from typing import Callable, Optional

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


async def get_referrer_id(message: Message) -> Optional[int]:
    """
    Extracts and validates the referrer_id from the message text. Expected format is "r-<id>".
    Returns None if no valid referrer_id is found or if self-referral.
    """
    try:
        if not message.text or not message.from_user:
            return

        parts = message.text.split(" ", maxsplit=1)
        if len(parts) <= 1:
            return

        referral_arg = parts[1].strip()
        if not referral_arg.startswith("r-"):
            return

        # Only accept "r-<digits>"
        referral_id_str = referral_arg.replace("r-", "", 1)
        if not referral_id_str.isdigit():
            return

        referral_id = int(referral_id_str)
        # Prevent self-referral
        if referral_id != message.from_user.id:
            return referral_id
    except Exception as e:
        logger.exception(f"Failed to extract referrer_id: {e}")


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
        referrer_id = await get_referrer_id(message)
        async with sessionmanager.session() as db:
            # logger.info(f"with_wallets: {with_wallets}")
            user = await get_or_create_user(
                db=db,
                id=user_id,
                first_name=message.from_user.first_name,
                username=message.from_user.username,
                referrer_id=referrer_id,
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
