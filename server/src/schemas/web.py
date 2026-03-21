from typing import Optional

from pydantic import ConfigDict

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
