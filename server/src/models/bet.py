from typing import TYPE_CHECKING, Optional
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.enums import BetStatus
from src.utils import utcnow
from src.models import Base, bet_table_name, user_table_name, game_table_name

if TYPE_CHECKING:
    from src.models import User, Game


class Bet(Base):
    __tablename__ = bet_table_name

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey(f"{user_table_name}.id"), index=True
    )
    game_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey(f"{game_table_name}.id"), index=True
    )
    hash: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True)
    amount: Mapped[float] = mapped_column(Float)
    # Represents the amount of the bet for auto cashout
    target: Mapped[float] = mapped_column(Float, default=0.0, server_default="0.0")
    # Represents the multiplier of the cashout
    cashout_multiplier: Mapped[float] = mapped_column(Float, default=0.0)
    winnings: Mapped[float] = mapped_column(Float, default=0.0)
    auto_cashout: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String, default=BetStatus.ACTIVE.value)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    user: Mapped["User"] = relationship("User", back_populates="bets")
    game: Mapped["Game"] = relationship("Game", back_populates="bets")
