from typing import TYPE_CHECKING, Optional
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base, betside_table_name, user_table_name
from src.utils import utcnow

if TYPE_CHECKING:
    from src.models.user import User


class BetSide(Base):
    __tablename__ = betside_table_name

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey(f"{user_table_name}.id")
    )
    side_name: Mapped[Optional[str]] = mapped_column(String)
    auto: Mapped[bool] = mapped_column(Boolean, default=False)
    betted: Mapped[bool] = mapped_column(Boolean, default=False)
    cashed_out: Mapped[bool] = mapped_column(Boolean, default=False)
    cashout_amount: Mapped[float] = mapped_column(Float, default=0.0)
    bet_amount: Mapped[float] = mapped_column(Float, default=1.0)
    target: Mapped[float] = mapped_column(Float, default=2.0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    user: Mapped["User"] = relationship("User", back_populates="betsides")
