from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.enums import ReferralStatus
from src.utils import utcnow
from src.models import Base, referral_table_name, user_table_name

if TYPE_CHECKING:
    from src.models import User


class Referral(Base):
    __tablename__ = referral_table_name

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    referred_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey(f"{user_table_name}.id"), index=True
    )
    referrer_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey(f"{user_table_name}.id"), index=True
    )
    referred_name: Mapped[str] = mapped_column(String)
    referrer_name: Mapped[Optional[str]] = mapped_column(String)
    bonus_amount: Mapped[float] = mapped_column(
        Float, default=0.0, server_default="0.0"
    )
    status: Mapped[str] = mapped_column(
        String,
        default=ReferralStatus.PENDING.value,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    referred: Mapped["User"] = relationship(
        back_populates="referral_entry", foreign_keys=[referred_id]
    )
    referrer: Mapped["User"] = relationship(
        back_populates="referrals", foreign_keys=[referrer_id]
    )
