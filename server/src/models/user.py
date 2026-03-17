from datetime import datetime
from typing import List, Optional

from sqlalchemy import BigInteger, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.utils import utcnow
from src.models import Base, BetSide, Referral, user_table_name


class User(Base):
    __tablename__ = user_table_name

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(String, index=True)

    # Websocket
    sid: Mapped[Optional[str]] = mapped_column(String, index=True)

    balance: Mapped[float] = mapped_column(Float, default=0.0, index=True)

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
