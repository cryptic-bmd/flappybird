from src.database import Base

user_table_name = "User"
game_table_name = "Game"
referral_table_name = "Referral"
betside_table_name = "Betside"
bet_table_name = "Bet"

from src.models.bet import Bet
from src.models.betside import BetSide
from src.models.game import Game
from src.models.referral import Referral
from src.models.user import User
