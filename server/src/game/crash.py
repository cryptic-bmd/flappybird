import asyncio, random, time
from typing import Dict, Set

from socketio.async_server import AsyncServer
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.crud import (
    create_game,
    get_bets_by_game_id,
    get_user_by_id_with_betsides,
    update_game_status,
    update_user_betside,
)
from src.database import sessionmanager
from src.enums import BetStatus, Events, GameStatus
from src.logger import logger
from src.models import Bet, User
from src.schemas import (
    BetSchema,
    BetSideSchema,
    BetState,
    BettedUserInfo,
    BettedUserStats,
    GameHistory,
    GameState,
    UserStorage,
    UserSchema,
)
from src.storage import storage
from src.utils import broadcast


class CrashGame:
    def __init__(self):
        self.state = GameStatus.BETTING
        self.game_id = 0
        self.current_multiplier = 1.0
        self.crash_point: float = 0
        self.start_time_in_ms: int = 0

        self.betted_user_infos: Dict[int, BettedUserInfo] = {}
        self.betted_user_states: Dict[int, BetState] = {}
        self.betted_user_stats = BettedUserStats()

        # Track current game state-changing callback invokers
        # This is to prevent users from, for example, cashing out twice in a session
        self.invokers: Set[int] = set()

        # Used when game is running
        # Users to auto cash out
        self.auto_cashout_users: Dict[int, UserStorage] = {}
        # Tasks that are for cashing out automatically
        self.auto_cashout_tasks: Set[asyncio.Task] = set()

        # Maintenance
        self.maintenance_mode: bool = (
            settings.MAINTENANCE_MODE
        )  # Runtime maintenance flag
        self.m_last_update_in_ms = 0
        self.m_update_interval_in_ms = 0

    @property
    def time_in_ms(self) -> int:
        return int((time.time() * 1000))

    @property
    def elapsed_time_in_ms(self) -> int:
        return self.time_in_ms - self.start_time_in_ms

    def generate_crash_point(self) -> float:
        r = lambda: random.random()

        def cp():
            # Applies instant bust
            if r() < settings.HOUSE_EDGE:
                return 1.00
            raw = 1 / (1 - r())
            return round(max(1.0, raw * settings.PAYOUT_FACTOR), 2)

        crash_point = cp()
        # logger.info(f"\nRandom number: {round(r, 2)}")
        logger.info(f"Crash point: {crash_point}")

        return crash_point

    async def calculate_multiplier(self, elapsed_time: float) -> float:
        # Matches client-side formula
        # t = elapsed_time / 1000  # Convert ms to seconds
        # return 1 + 0.06 * t
        # return 1 + 0.06 * t + (0.06 * t) ** 2 - (0.04 * t) ** 3 + (0.04 * t) ** 4
        t = elapsed_time * 0.001  # Pre-scale ms to s
        t_scaled = 0.06 * t
        t3 = 0.04 * t
        t4 = t3
        return (
            1 + t_scaled + (t_scaled * t_scaled) - (t3 * t3 * t3) + (t4 * t4 * t4 * t4)
        )

    async def estimate_time_to_crash(self, crash_point: float) -> int:
        """
        Estimate time (ms) to reach crash_point using Newton-Raphson method.
        Solves m(t) = crash_point where m(t) = 1 + 0.06t + (0.06t)^2 - (0.04t)^3 + (0.04t)^4.
        """

        def multiplier(t: float) -> float:
            t_scaled = 0.06 * t
            t3 = 0.04 * t
            t4 = 0.04 * t
            return 1 + t_scaled + t_scaled * t_scaled - t3 * t3 * t3 + t4 * t4 * t4 * t4

        def derivative(t: float) -> float:
            return 0.06 + 0.0072 * t - 0.000192 * t * t + 0.00001024 * t * t * t

        def f(t: float) -> float:
            return multiplier(t) - crash_point

        # Initial guess: approximate linear term (0.06t)
        t = crash_point / 0.06
        max_iterations = 10
        tolerance = 0.01  # Allow small error in multiplier

        for _ in range(max_iterations):
            f_t = f(t)
            if abs(f_t) < tolerance:
                break
            f_prime_t = derivative(t)
            if abs(f_prime_t) < 1e-10:  # Avoid division by zero
                break
            t -= f_t / f_prime_t

        # Ensure t is positive and reasonable
        if t <= 0 or t > 1000:  # Cap at 1000s
            return int(crash_point * 1000)  # Fallback
        return int(t * 1000)  # Convert seconds to ms

    async def auto_cash_out(self, sio: AsyncServer): ...

    async def emit_user_info(self, sio: AsyncServer, user: User, bet: Bet):
        if not (sid := user.sid):
            return

        # logger.info(f"Sending user info for user {user.id}")
        await sio.emit(
            Events.MY_BET_STATE.value,
            BetState().json_(),
            to=sid,
        )
        await sio.emit(
            Events.MY_FINALIZED_BET.value,
            BetSchema(
                hash=bet.hash[:8],  # type: ignore
                betAmount=bet.amount,
                cashOutMultiplier=bet.cashout_multiplier,
                winnings=bet.winnings,
            ).json_(),
            to=sid,
        )
        betside = user.betsides[0]
        f = BetSideSchema(
            auto=betside.auto,
            betted=betside.betted,
            cashedOut=betside.cashed_out,
            cashOutAmount=betside.cashout_amount,
            betAmount=betside.bet_amount,
            target=betside.target,
        )
        await sio.emit(
            Events.GAME_END.value,
            UserSchema(
                id=user.id,
                username=user.username,
                img=user.username,
                balance=user.balance,
                f=f,
                s=BetSideSchema(),
            ).json_(),
            to=sid,
        )

    def update_betted_user_stats(self, user_store: UserStorage, winnings: float):
        self.betted_user_stats.noOfCashouts += 1
        self.betted_user_stats.totalWinnings += winnings
        self.betted_user_stats.biggestWinning = max(
            self.betted_user_stats.biggestWinning, winnings
        )
        if self.betted_user_stats.biggestWinning != winnings:
            return
        self.betted_user_stats.biggestWinnerID = user_store.id
        self.betted_user_stats.biggestWinnerUsername = user_store.username

    async def _run(self, sio: AsyncServer, db: AsyncSession):
        # Main game loop
        self.crash_point = self.generate_crash_point()
        game = await create_game(db, self.crash_point)
        self.game_id = game.id

        logger.info(f"\nGame {game.id} started")

        # BETTING phase - Users can now place their bets (in BETTING_PHASE_DURATION seconds)
        self.state = GameStatus.BETTING
        self.current_multiplier = 1.0
        self.start_time_in_ms = self.time_in_ms

        self.betted_user_infos = {}
        self.betted_user_states = {}

        self.betted_user_stats = BettedUserStats()
        await broadcast(
            sio,
            Events.BETTED_USER_STATS.value,
            self.betted_user_stats.json_(),
        )
        await broadcast(
            sio,
            Events.GAME_STATE.value,
            GameState(
                gameState=self.state.value,
                currentMultiplier=self.current_multiplier,
                serverTimeElapsed=self.elapsed_time_in_ms,
            ).json_(),
        )
        await asyncio.sleep(settings.BETTING_PHASE_DURATION)

        # PLAYING phase - Users can now cash out from here
        self.state = GameStatus.RUNNING
        self.start_time_ms = self.time_in_ms
        time_estimate = await self.estimate_time_to_crash(self.crash_point)
        update_interval_ms = max(100, time_estimate // 10)
        last_update_ms = 0

        while self.state == GameStatus.RUNNING:
            elapsed_time_ms = self.elapsed_time_in_ms
            self.current_multiplier = await self.calculate_multiplier(elapsed_time_ms)
            # logger.info(f"current_multiplier: {self.current_multiplier}")

            if self.current_multiplier >= self.crash_point:
                self.state = GameStatus.CRASHED
                break

            await self.auto_cash_out(sio)

            # sleep for 20ms if it's not time to send an update
            # else send an update
            # Note: overall sleep time might be more than 20ms
            if (
                not ((elapsed_time_ms - last_update_ms) >= update_interval_ms)
                and last_update_ms != 0
            ):
                # logger.info(
                #     f"(sleeping) elapsed_time: {elapsed_time} "
                #     f"last_update: {last_update} "
                #     f"update_interval: {update_interval}"
                # )
                await asyncio.sleep(0.02)  # ms updates
                continue

            await broadcast(
                sio,
                Events.GAME_STATE.value,
                GameState(
                    gameState=self.state.value,
                    currentMultiplier=self.current_multiplier,
                    serverTimeElapsed=self.elapsed_time_in_ms,
                ).json_(),
            )
            last_update_ms = elapsed_time_ms
            await asyncio.sleep(0.02)  # ms updates

        # GAME END phase - Users cannot cashout no more if they haven't already
        game = await update_game_status(db, game, self.state)  # CRASHED
        await broadcast(
            sio,
            Events.GAME_STATE.value,
            GameState(
                gameState=self.state.value,
                currentMultiplier=self.crash_point,
                serverTimeElapsed=self.elapsed_time_in_ms,
            ).json_(),
        )
        game_history = GameHistory(
            gameID=game.id,
            gameHash=game.hash,  # type: ignore
            crashPoint=self.crash_point,
        ).json_()
        await broadcast(sio, Events.GAME_HISTORY.value, [game_history])

        self.auto_cashout_users = {}
        asyncio.gather(*self.auto_cashout_tasks)

        # Update bets and balances
        bets = await get_bets_by_game_id(db, game.id)
        # logger.info(f"Bets: {bets}")
        for bet in bets:
            user_id = bet.user_id
            try:
                user_store = UserStorage(**storage.get_data(user_id=user_id))
            except Exception as e:
                # Not supposed to happnen in an ideal case
                # Critical error, betted user not found in local storage
                logger.exception(repr(e))
                continue

            betside_store = user_store.betsides[0]
            if not betside_store:
                # Critical error, betted user has no betsides
                logger.error(f"User {user_id} has no betsides")
                continue

            bet_store = user_store.bet
            if not bet_store:
                # Critical error, betted user has no bet
                logger.error(f"User {user_id} has no bet")
                continue

            user = await get_user_by_id_with_betsides(db, user_id)
            if user is None:
                logger.error(f"User with id {user_id} and betsides not found")
                raise ValueError(f"User with id {user_id} and betsides not found")
                # We raise an error here and stop game loop
                # cause it is crucial for user to exist atp

            user.balance = user_store.balance
            bet.winnings = bet_store.winnings

            if bet_store.status == BetStatus.CASHED_OUT.value:
                # Player cashed out.
                bet.status = BetStatus.CASHED_OUT.value
                bet.cashout_multiplier = bet_store.cashout_multiplier
            else:
                bet.status = BetStatus.LOST.value

            betside_data = BetSideSchema(
                auto=betside_store.auto,
                betted=False,
                cashedOut=False,
                cashOutAmount=betside_store.cashout_amount,
                betAmount=bet_store.amount,
                target=bet_store.target,
            )
            user_updated = await update_user_betside(db, user, betside_data)
            if user_updated is None:
                logger.error(f"Update to user.betsides failed")
                user.betsides[0].betted = False
                user.betsides[0].cashed_out = False
            else:
                user = await get_user_by_id_with_betsides(db, user_id)

            if not user:
                logger.error(f"User with id {user_id} and betsides not found")
                raise ValueError(f"User with id {user_id} and betsides not found")
                # We raise an error here and stop game loop
                # cause it is crucial for user to exist atp

            storage.reset_data(user_id=user_id)
            await self.emit_user_info(sio, user, bet)

        await db.commit()

        logger.info(f"Game {game.id} ended\n")
        await asyncio.sleep(2)

    async def run(self, sio: AsyncServer):
        while True:
            try:
                in_maintenance = await self.check_maintenance(sio)
                if in_maintenance:
                    continue

                async with sessionmanager.session() as db:
                    await self._run(sio, db)
            except Exception as e:
                logger.error(repr(e))
                logger.exception(repr(e))
                break

    async def check_maintenance(self, sio: AsyncServer) -> bool:
        # Check for maintenance mode first before starting a new game session
        if self.maintenance_mode:
            logger.info("Maintenance mode enabled")
            if (
                self.time_in_ms - self.m_last_update_in_ms
            ) < self.m_update_interval_in_ms:
                await asyncio.sleep(5)
                return True
            # In maintenance mode, pause game loop and notify clients
            await broadcast(
                sio,
                Events.MAINTENANCE.value,
                {"message": "Server is under maintenance. Betting is disabled."},
            )
            self.m_update_interval_in_ms += min(
                self.m_update_interval_in_ms + 5000, 60000
            )
            self.m_last_update_in_ms = self.time_in_ms
            await asyncio.sleep(5)
            return True
        else:
            self.m_update_interval_in_ms = 0
            self.m_last_update_in_ms = 0

        return False
