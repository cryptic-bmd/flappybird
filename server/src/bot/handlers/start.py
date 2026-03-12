from telebot.types import Message

from src.models import User as UserDB
from src.bot.async_bot import async_bot, bot_name, ensure_user


# Handle '/start'
@async_bot.message_handler(commands=["start"])
@ensure_user()
async def start(message: Message, user: UserDB):
    if not message.from_user:
        return

    await async_bot.send_message(
        message.chat.id,
        f"Hi, {message.from_user.first_name}! welcome to {bot_name}, "
        f"home of the best crash game!\n\n"
        f"Deposit Crypto, get bonuses, play to win 😎✅\n\n"
        f"Click button to start 🚀",
    )
