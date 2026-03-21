from __future__ import annotations
from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.enums import GameStatus
from src.utils import utcnow
from src.models import Base, Bet, game_table_name


class Game(Base):
    __tablename__ = game_table_name

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    crash_point: Mapped[float] = mapped_column(Float, default=1.0)
    hash: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True)
    status: Mapped[str] = mapped_column(
        String, default=GameStatus.BETTING.value, index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    bets: Mapped[list["Bet"]] = relationship("Bet", back_populates="game")
