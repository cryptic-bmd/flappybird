import argparse, sys
from typing import Optional

import jwt
import requests
from loguru import logger

from src.config import settings

TIMEOUT = 120


def make_request(
    method: str,
    endpoint: str,
    data: Optional[dict] = None,
    params: Optional[dict] = None,
    headers: Optional[dict] = None,
) -> dict:
    """
    Make an HTTP request to the server with error handling.
    """
    url = f"{settings.BACK_BASE_URL}/admin/{endpoint}"
    headers = {"Content-Type": "application/json"}
    payload = data or {}
    if "Authorization" not in headers:
        token = jwt.encode(
            {"subb": settings.ADMIN_KEY},
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
        headers["Authorization"] = f"Bearer {token}"

    try:
        response = requests.request(
            method=method,
            url=url,
            json=payload if method != "GET" else None,
            params=params,
            headers=headers,
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            logger.error("Invalid admin key")
        else:
            logger.error(f"HTTP error: {e}")
        sys.exit(1)
    except requests.exceptions.ConnectionError as e:
        logger.error("Failed to connect to server. Ensure the server is running.")
        logger.error(f"Connection error: {e}")
        sys.exit(1)
    except requests.exceptions.Timeout:
        logger.error("Request timed out. Server may be unresponsive.")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


def toggle_maintenance(enable: bool):
    """
    Toggle maintenance mode.
    """
    data = {"maintenance_mode": enable}
    result = make_request("POST", "maintenance", data)
    logger.info(result["message"])


def main():
    """
    CLI for admin functions.
    """
    parser = argparse.ArgumentParser(description="Admin CLI for Crash Game Server")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Maintenance
    maintenance_parser = subparsers.add_parser(
        "maintenance", help="Toggle maintenance mode"
    )
    maintenance_parser.add_argument(
        "action", choices=["enable", "disable"], help="Enable or disable maintenance"
    )

    args = parser.parse_args()

    if args.command == "maintenance":
        toggle_maintenance(args.action == "enable")


if __name__ == "__main__":
    main()
