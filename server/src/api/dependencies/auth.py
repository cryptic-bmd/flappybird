import http

from fastapi import Depends
from fastapi import HTTPException
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
from loguru import logger
from telegram_webapp_auth.auth import (
    TelegramAuthenticator,
    WebAppUser,
    generate_secret_key,
)
from telegram_webapp_auth.errors import InvalidInitDataError

from src.config import settings
from src.utils import get_admin_key_from_token, get_current_user_id_from_token

authentication_schema = HTTPBearer()


def get_telegram_authenticator() -> TelegramAuthenticator:
    secret_key = generate_secret_key(settings.TG_BOT_TOKEN)
    return TelegramAuthenticator(secret_key)


def get_current_telegram_user(
    auth_cred: HTTPAuthorizationCredentials = Depends(authentication_schema),
    telegram_authenticator: TelegramAuthenticator = Depends(get_telegram_authenticator),
) -> WebAppUser:
    try:
        init_data = telegram_authenticator.validate(auth_cred.credentials)
    except InvalidInitDataError as e:
        logger.exception(repr(e))
        raise HTTPException(
            status_code=http.HTTPStatus.FORBIDDEN,
            detail="Forbidden access.",
        )
    except Exception as e:
        logger.exception(repr(e))
        raise HTTPException(
            status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Internal error.",
        )

    if init_data.user is None:
        raise HTTPException(
            status_code=http.HTTPStatus.FORBIDDEN,
            detail="Forbidden access.",
        )

    return init_data.user


def get_admin_key(
    admin_key_cred: HTTPAuthorizationCredentials = Depends(authentication_schema),
) -> str:
    admin_key = admin_key_cred.credentials
    return get_admin_key_from_token(admin_key)


def get_current_user_id(
    token_auth_cred: HTTPAuthorizationCredentials = Depends(authentication_schema),
) -> str:
    token = token_auth_cred.credentials
    # logger.info(f"Token: {token}")
    return get_current_user_id_from_token(token)
