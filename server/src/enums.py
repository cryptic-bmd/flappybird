from enum import Enum


class Environment(Enum):
    PROD = "prod"
    STAGING = "staging"
    LOCAL = "local"


class Events(Enum):
    ENTER_ROOM = "enterRoom"
    GAME_STATE = "gameState"
    GAME_END = "gameEnd"
    GAME_HISTORY = "gameHistory"
    MY_INFO = "myInfo"
    PLACE_BET = "placeBet"
    CASH_OUT = "cashOut"
    MY_FINALIZED_BET = "myfinalizedBet"
    MY_BET_STATE = "myBetState"
    BETTED_USER_INFO = "bettedUserInfo"
    BETTED_USER_INFOS = "bettedUserInfos"
    BETTED_USER_STATS = "bettedUserStats"
    ERROR = "error"

    PING = "ping"
    PONG = "pong"

    MAINTENANCE = "maintenance"  # Server maintenance


class GameStatus(Enum):
    BETTING = "BETTING"
    RUNNING = "RUNNING"
    CRASHED = "CRASHED"
