from typing import Optional

from src.schemas.base import SecondaryBase


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
