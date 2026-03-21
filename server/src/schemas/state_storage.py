from typing import List, Optional

from src.schemas.base import SecondaryBase

__all__ = ["BetStorage", "BetSideStorage", "UserStorage"]


class BetStorage(SecondaryBase):
    id: int
    user_id: int
    game_id: int
    hash: str
    amount: float
    target: float
    cashout_multiplier: float
    winnings: float
    auto_cashout: bool
    status: str


class BetSideStorage(SecondaryBase):
    id: int
    user_id: int
    side_name: str
    auto: bool
    betted: bool
    cashed_out: bool
    cashout_amount: float
    bet_amount: float
    target: float


class UserStorage(SecondaryBase):
    id: int
    hash: str
    sid: Optional[str] = None
    username: str
    balance: float
    is_bot: bool
    betsides: List[BetSideStorage]
    bet: Optional[BetStorage]
