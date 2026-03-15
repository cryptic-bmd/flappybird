from src.config import settings
from src.app import app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        ssl_certfile=settings.SSL_CERT,
        ssl_keyfile=settings.SSL_KEY,
    )
