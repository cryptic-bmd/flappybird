from datetime import datetime
from typing import Optional

from pydantic import ConfigDict, field_validator

from src.config import settings
from src.schemas.base import SecondaryBase

__all__ = [
    "BettedUserInfo",
    "BettedUserStats",
    "GameState",
    "MaintenanceRequest",
    "UserBase",
    "UserSchema",
    "BetState",
    "BetSideSchema",
    "GameHistory",
    "BetSchema",
    "BetBase",
    "CashOutBase",
    "ReferralResponse",
    "BotUserDetails",
]


class BettedUserInfo(SecondaryBase):
    userID: int
    userHash: str
    betAmount: float
    cashOut: Optional[float] = None
    cashedOut: bool
    target: Optional[float] = None


class BettedUserStats(SecondaryBase):
    # Bets
    noOfBets: int = 0
    totalBetAmount: float = 0.0

    # Cashouts
    noOfCashouts: int = 0
    totalWinnings: float = 0.0
    biggestWinning: float = 0.0
    biggestWinnerID: int = 0
    biggestWinnerUsername: str = ""


class GameState(SecondaryBase):
    gameState: str = "BETTING"  # "BETTING", "PLAYING", "GAMEEND"
    currentMultiplier: float = 1.0  # Current multiplier (None in BET)
    serverTimeElapsed: int  # Server timestamp for sync


class MaintenanceRequest(SecondaryBase):
    maintenance_mode: bool


class UserBase(SecondaryBase):
    id: Optional[int] = None
    username: Optional[str] = None
    img: Optional[str] = None
    f: Optional["BetSideSchema"] = None
    s: Optional["BetSideSchema"] = None


class UserSchema(UserBase):
    model_config = ConfigDict(from_attributes=True)

    balance: float
    pendingBalance: Optional[float] = None
    availableBalance: Optional[float] = None
    referralLink: Optional[str] = None


class BetState(SecondaryBase):
    fBetted: bool = False
    sBetted: bool = False
    # f: Optional[dict] = None  # { betAmount, cashout }
    # s: Optional[dict] = None


class BetSideSchema(SecondaryBase):
    model_config = ConfigDict(from_attributes=True)

    auto: bool = False
    betted: bool = False
    cashedOut: bool = False
    cashOutAmount: float = 0  # Cashout amount in currency
    betAmount: float = 1
    target: float = 10  # Cash-out multiplier


class GameHistory(SecondaryBase):
    gameID: int
    gameHash: str  # Unique hash for the game
    crashPoint: float  # Multiplier at which the game ended


class BetSchema(SecondaryBase):
    hash: str
    betAmount: float
    cashOutMultiplier: float
    cashedOut: Optional[bool] = None
    winnings: float
    date: Optional[int] = None


class BetBase(SecondaryBase):
    token: str
    betAmount: float  # Bet amount
    target: float  # Requested cash-out multiplier
    type: str  # "f" or "s" from client
    autoCashOut: bool  # True if auto cashout is enabled

    @field_validator("betAmount")
    def check_bet_amount(cls, v):
        if v <= 0 or v > settings.MAX_BET:
            raise ValueError("Invalid betAmount")
        return v

    @field_validator("type")
    def check_type(cls, v):
        if v not in ["f", "s"]:
            raise ValueError("Invalid type")
        return v

    @field_validator("autoCashOut")
    def check_auto_cashout(cls, v):
        if not isinstance(v, bool):
            raise ValueError("Invalid autoCashOut")
        return v


class CashOutBase(SecondaryBase):
    type: str  # "f" or "s"
    endTarget: Optional[float] = None  # Requested cash-out multiplier
    # clientTime: int  # Client timestamp (ms)


class ReferralResponse(SecondaryBase):
    referredId: int
    referredName: str
    referrerId: Optional[int] = None
    referrerName: Optional[str] = None
    bonusAmount: float
    status: str
    createdAt: datetime


class BotUserDetails(SecondaryBase):
    user_id: int
    username: str
    first_name: str
    token: Optional[str] = None
