from datetime import datetime
from typing import List, Optional

from sqlalchemy import BigInteger, Boolean, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.utils import utcnow
from src.models import Base, Bet, BetSide, Referral, user_table_name


class User(Base):
    __tablename__ = user_table_name

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(String, index=True)
    is_bot: Mapped[Optional[bool]] = mapped_column(Boolean, index=True)

    # Websocket
    sid: Mapped[Optional[str]] = mapped_column(String, index=True)
    hash: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True)

    balance: Mapped[float] = mapped_column(Float, default=0.0, index=True)
    # Newly added funds on chain or via a payment method that's
    # not yet added to the main balance.
    # This is to avoid a race condition when the balance is updated
    # since the user can place a bet when/before the balance is updated
    pending_balance: Mapped[float] = mapped_column(
        Float, default=0.0, server_default="0.0", index=True
    )
    # Bonus balances that have not been wagered
    unwagered_balance: Mapped[float] = mapped_column(
        Float, default=0.0, server_default="0.0", index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    referral_entry: Mapped[Referral] = relationship(
        back_populates="referred",  # "referred" refers to this User
        foreign_keys="[Referral.referred_id]",
    )
    referrals: Mapped[list[Referral]] = relationship(
        back_populates="referrer",  # likewise "referrer"
        foreign_keys="[Referral.referrer_id]",
    )

    betsides: Mapped[List[BetSide]] = relationship("BetSide", back_populates="user")
    bets: Mapped[list[Bet]] = relationship("Bet", back_populates="user")
