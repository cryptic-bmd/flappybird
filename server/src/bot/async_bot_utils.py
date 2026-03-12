from typing import List, Optional

from telebot import types
from telebot.async_telebot import AsyncTeleBot
from telebot.formatting import hlink
from telebot.types import User


async def call_command_handler(
    async_bot: AsyncTeleBot, command_handler_str: str, *args, **kwargs
):
    """
    Force call command handler
    """
    for handler in async_bot.message_handlers:
        if command_handler_str in handler["filters"].get("commands", []):
            await handler["function"].__call__(*args, **kwargs)
            break


def inline_buttons(
    names: List[str],
    row_widths: List[int],
    callback_strs: Optional[List[str]] = None,
    links: Optional[List[str]] = None,
) -> types.InlineKeyboardMarkup:
    """
    Generates an InlineKeyboardMarkup object with buttons,
    allowing for customizable row widths.

    Parameters:
        names (List[str]): List of button names.
        callback_strs (Optional[List[str]]): List of callback data strings.
        links (Optional[List[str]]): List of URLs for buttons.
        row_widths (List[int]): List specifying the number of
        buttons per row.

    Returns:
        types.InlineKeyboardMarkup: InlineKeyboardMarkup object with buttons.

    Raises:
        ValueError: If both `callback_strs` and `links` are None,
        if lists have mismatched lengths,
        or if row_widths are not sufficient.
    """
    # Checks
    if callback_strs is None and links is None:
        raise ValueError("Either callback_strs or links must be provided")
    if callback_strs and links:
        raise ValueError("Cannot provide both callback_strs and links")
    if callback_strs and len(callback_strs) != len(names):
        raise ValueError("Length of callback_strs must match length of names")
    if links and len(links) != len(names):
        raise ValueError("Length of links must match length of names")
    if sum(row_widths) < len(names):
        raise ValueError("Sum of row_widths must be at least the number of buttons")
    markup = types.InlineKeyboardMarkup()
    index = 0
    for row_width in row_widths:
        if index >= len(names):
            break
        row_btns = []
        for _ in range(row_width):
            if index >= len(names):
                break
            if callback_strs:
                row_btns.append(
                    types.InlineKeyboardButton(
                        names[index], callback_data=callback_strs[index]
                    )
                )
            else:
                assert (
                    links is not None
                ), "links must be provided if callback_strs is not"
                row_btns.append(
                    types.InlineKeyboardButton(names[index], url=links[index])
                )
            index += 1
        markup.add(*row_btns)
    return markup


def update_inline_button(
    existing_markup: types.InlineKeyboardMarkup,
    callback_data: str,
    new_btn_name: str,
    new_callback_data: str,
) -> types.InlineKeyboardMarkup:
    """
    Updates an existing InlineKeyboardMarkup object by
    replacing a button with a new one.

    This function iterates through the rows and buttons in
    the existing InlineKeyboardMarkup object and updates the
    button whose callback data matches the provided callback_data.
    The button will be replaced with a new button having the
    specified new_btn_name and new_callback_data.

    Parameters:
        existing_markup (types.InlineKeyboardMarkup): The existing InlineKeyboardMarkup object.
        callback_data (str): The callback data of the button to be updated.
        new_btn_name (str): The name (text) for the updated button.
        new_callback_data (str): The new callback data for the updated button.

    Returns:
        types.InlineKeyboardMarkup: A new InlineKeyboardMarkup object with the updated button.

    Raises:
        ValueError: If the provided callback_data does not match any
        button's callback_data.
    """
    updated_markup = []
    button_updated = False
    for row in existing_markup.keyboard:
        updated_row = []
        for button in row:
            if button.callback_data and button.callback_data.startswith(callback_data):
                updated_button = types.InlineKeyboardButton(
                    text=new_btn_name, callback_data=new_callback_data
                )
                updated_row.append(updated_button)
                button_updated = True
            else:
                updated_row.append(button)
        updated_markup.append(updated_row)

    if not button_updated:
        raise ValueError("No button found with the specified callback_data.")
    return types.InlineKeyboardMarkup(keyboard=updated_markup)


def reply_kb_remove(selection: Optional[bool] = None) -> types.ReplyKeyboardRemove:
    return types.ReplyKeyboardRemove(selection)


def close_markup(msg_id: int) -> types.InlineKeyboardMarkup:
    return inline_buttons(["Close"], [1], [f"close_{msg_id}_btn"])


def get_name(user: User) -> str:
    username = user.username
    first_name = user.first_name
    return f"@{username}" if username else first_name


def get_markdowned_name(user: User) -> str:
    username = user.username
    first_name = user.first_name
    if username:
        return hlink(first_name, f"https://t.me/{username}")
    else:
        return first_name
