/* eslint-disable react-hooks/exhaustive-deps */
import { useEffect, useCallback, useState } from "react";

import axios from 'axios';
import { toast } from "react-toastify";

import MainContext, { socket } from "./mainContext";
import { useAuthContext } from "./authContext";
import { API_URL } from "../config";
import { getAxiosError } from "../utils/errors";
import { formatTwoDecimalsExact } from "../utils/formatters";
import { log } from "../utils/logger";

import type {
  ContextDataType,
  UserType,
  UserBetStateType,
  BettedUserType,
  GameStateType as GameStateObjType,
  GameBetLimit,
  MyBetHistory,
  BettedUserStatsType,
  GameHistory,
} from "./mainContext";


const init_state = {
  gameHistory: [],
  myBets: [],
  userInfo: {
    balance: 0,
    img: "",
    username: "",
    f: {
      auto: false,
      betted: false,
      cashedOut: false,
      cashOutAmount: 0,
      betAmount: 1,
      target: 2,
    },
    s: {
      auto: false,
      betted: false,
      cashedOut: false,
      cashOutAmount: 0,
      betAmount: 1,
      target: 2,
    },
  },
  pingBarCount: 0,
} as ContextDataType;


let pingStart = 0;


const MainProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { token, authLoading, setError } = useAuthContext();

  const [state, setState] = useState<ContextDataType>(init_state);
  const [gameStateObj, setGameStateObj] = useState({
    gameState: "",
    currentMultiplier: 0,
    serverTimeElapsed: 0,
  });
  const [userBetState, setUserBetState] = useState<UserBetStateType>({
    fToBet: false,
    fBetted: false,
    sToBet: false,
    sBetted: false,
  });
  const [betLimit, setBetLimit] = useState<GameBetLimit>({
    maxBet: 1000,
    minBet: 0,
  });
  const [bettedUsers, setBettedUsers] = useState<BettedUserType[]>([]);
  const [bettedUserStats, setBettedUserStats] = useState<BettedUserStatsType>({
    noOfBets: 0,
    totalBetAmount: 0,
    noOfCashouts: 0,
    totalWinnings: 0,
    biggestWinning: 0,
    biggestWinnerID: 0,
    biggestWinnerUsername: "",
  });
  const [currentTarget, setCurrentTarget] = useState(0);
  const [showPopOverLay, setShowPopOverLay] = useState(false);
  const [showBetAmountNote, setShowBetAmountNote] = useState(false);
  const [showCrashHistory, setShowCrashHistory] = useState(false);


  const updateState = (attrs: Partial<ContextDataType>) => {
    setState(prev => ({ ...prev, ...attrs }));
  };

  const updateUserBetState = (attrs: Partial<UserBetStateType>) => {
    setUserBetState(prev => ({ ...prev, ...attrs }));
  };

  const getMyBets = useCallback(async () => {
    try {
      const response = await axios.get(
        `${API_URL}/user/bets`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (response.status === 200) {
        // log(`response.data: ${response.data}`);
        const attrs = state;
        attrs.myBets = response.data as MyBetHistory[];
        updateState(attrs);
        // log(`myBets: ${state.myBets}`);
      } else {
        setError({ message: "Failed to fetch user bets" });
      }
    } catch (e) {
      setError({ message: getAxiosError(e), autoClose: 5000 });
    }
  }, [state.userInfo.username, token, updateState]);

  const callCashOut = useCallback((index: "f" | "s") => {
    const data = { token, type: index, endTarget: 0 };
    socket.emit("cashOut", data);
  }, [token, socket]);

  const getBarCount = (ping: number): number => {
    if (ping === 0) return 0; // No ping data
    if (ping < 17) return 3; // Excellent
    if (ping < 35) return 2; // Fair
    return 1; // Poor
  };

  const getColorClasses = (multiplier: number) => {
    if (multiplier >= 10) {
      return { bg: 'bg-super', text: 'text-super' };
    }
    if (multiplier >= 2) {
      return { bg: 'bg-success', text: 'text-success' };
    }
    return { bg: 'bg-warning', text: 'text-warning' };
  };

  useEffect(() => {
    const attrs = betLimit;
    attrs.maxBet = state.userInfo.balance;
    setBetLimit(attrs);
  }, [state.userInfo.balance]);

  useEffect(() => {
    if (!token) return;

    socket.on("connect", () => {
      log("Connected to server");
    });

    socket.on("pong", () => {
      if (pingStart) {
        const pingTime = Date.now() - pingStart;
        const barCount = getBarCount(pingTime);
        // log(`Ping time: ${pingTime}ms, Bar count: ${barCount}`);
        const attrs = state;
        attrs.pingBarCount = barCount;
        updateState(attrs);
        pingStart = 0;
      }
    });

    socket.on("myInfo", (user: UserType) => {
      log(`myInfo: ${JSON.stringify(user)}`);
      const attrs = state;
      attrs.userInfo = user;
      updateState(attrs);
    });

    socket.on("myBetState", (userStatus: Partial<UserBetStateType>) => {
      // log(`myBetState: ${JSON.stringify(userStatus)}, userBetState: ${JSON.stringify(userBetState)}`);
      if (userStatus.fBetted === true) {
        userStatus.fToBet = false;
      }
      updateUserBetState(userStatus);
    });

    socket.on("bettedUserInfo", (bettedUser: BettedUserType) => {
      // log(`bettedUsers: ${JSON.stringify(bettedUsers)}, bettedUserInfo: ${JSON.stringify(bettedUser)}`);
      setBettedUsers(prev => {
        const existingUserIndex = prev.findIndex(user => user.userID === bettedUser.userID);
        if (existingUserIndex !== -1) {
          // log(`Updating existing userID: ${bettedUser.userID}`);
          const updatedUsers = [...prev];
          updatedUsers[existingUserIndex] = bettedUser;
          return updatedUsers;
        }
        return [...prev, bettedUser];
      });
    });

    socket.on("bettedUserInfos", (bettedUsers: BettedUserType[]) => {
      // log(`bettedUsers: ${JSON.stringify(bettedUsers)}`);
      setBettedUsers(bettedUsers);
    });

    socket.on("bettedUserStats", (bettedUserStats: BettedUserStatsType) => {
      // log(`bettedUserStats: ${JSON.stringify(bettedUserStats)}`);
      setBettedUserStats(bettedUserStats);

      if (bettedUserStats.noOfBets === 0) setBettedUsers([]);
    });

    socket.on("gameState", (gameStateObj: GameStateObjType) => {
      setGameStateObj(gameStateObj);
    });

    socket.on("gameHistory", (gameHistory: GameHistory[]) => {
      // log(`gameHistory: ${JSON.stringify(gameHistory)}`);
      const attrs = state;
      // Adding to the front cause it's in descending order
      attrs.gameHistory = [...gameHistory, ...attrs.gameHistory];
      updateState(attrs);
    });

    socket.on("myfinalizedBet", (bet: MyBetHistory) => {
      // log(`myfinalizedBet: ${JSON.stringify(bet)}`);
      const attrs = state;
      const myBets = attrs.myBets;
  
      let updatedBetHistory;
      const existingBetIndex = myBets.findIndex(myBet => myBet.hash === bet.hash);
      if (existingBetIndex !== -1) {
        updatedBetHistory = [...myBets];
        updatedBetHistory[existingBetIndex] = bet;
      } else {
        updatedBetHistory = [bet, ...myBets];
      }

      attrs.myBets = updatedBetHistory;
      updateState(attrs);

      if (bet.cashedOut === true) {
        toast.success(`You won ${formatTwoDecimalsExact(bet.winnings)} USDT 🐦`, {
          style: {
            backgroundColor: "rgba(0, 0, 0, 0.5)",
            borderRadius: "12px",
          },
          autoClose: 5000,
          hideProgressBar: true,
        });
      }
    });

    socket.on("gameEnd", (user: UserType) => {
      log(`gameEnd myInfo: ${JSON.stringify(user)}`);
      const attrs = state;
      attrs.userInfo = user;
      updateState(attrs);
    });

    socket.on("getBetLimits", (betAmounts: { max: number; min: number }) => {
      setBetLimit({ maxBet: betAmounts.max, minBet: betAmounts.min });
    });

    socket.on("success", (data) => {
      toast.success(data, {
        style: {
          backgroundColor: "rgba(0, 0, 0, 0.5)",
          borderRadius: "12px",
        },
        autoClose: 3000,
        hideProgressBar: true,
      });
    });

    socket.on("error", (data) => {
      // setUserBetState({
      //   ...userBetState,
      //   [`${data.index}betted`]: false,
      // });
      setError({ message: data.message });
    });

    socket.emit("enterRoom", { token });

    return () => {
      socket.off("connect");
      // socket.off("disconnect");
      socket.off("pong");
      socket.off("myInfo");
      socket.off("myBetState");
      socket.off("bettedUserInfo");
      socket.off("bettedUserStats");
      socket.off("gameState");
      socket.off("gameHistory");
      socket.off("myfinalizedBet");
      socket.off("gameEnd");
      socket.off("getBetLimits");
      socket.off("success");
      socket.off("error");
    };
  }, [socket, token]);

  // Place bet
  useEffect(() => {
    if (!token) return;
    log(`Play bet effect running with gameStateObj.gameState: ${gameStateObj.gameState}`);

    const attrs = state;
    const betStatus = userBetState;
    if (gameStateObj.gameState === "BETTING") {
      log(`Play bet effect running with betStatus.fToBet: ${betStatus.fToBet}`);

      if (betStatus.fToBet) {
        if (attrs.userInfo.balance - state.userInfo.f.betAmount < 0) {
          setError({ message: "Your balance is not enough" });
          betStatus.fToBet = false;
          betStatus.fBetted = false;
          setUserBetState(betStatus);
          return;
        }
        const data = {
          token,
          betAmount: state.userInfo.f.betAmount,
          target: state.userInfo.f.target,
          type: "f",
          autoCashOut: state.userInfo.f.auto,
        };
        // attrs.userInfo.balance -= state.userInfo.f.betAmount;
        log(`Playing bet with data: ${JSON.stringify(data)}`);
        socket.emit("placeBet", data);
        // betStatus.fToBet = false;
        // betStatus.fBetted = true;
        // update(attrs);
        // setUserBetState(betStatus);
      }
      if (betStatus.sToBet) {
        const data = {
          token,
          amount: state.userInfo.s.betAmount,
          target: state.userInfo.s.target,
          type: "s",
          autoCashOut: state.userInfo.s.auto,
        };
        if (attrs.userInfo.balance - state.userInfo.s.betAmount < 0) {
          setError({ message: "Your balance is not enough" });
          betStatus.sToBet = false;
          betStatus.sBetted = false;
          setUserBetState(betStatus);
          return;
        }
        // attrs.userInfo.balance -= state.userInfo.s.betAmount;
        socket.emit("placeBet", data);
        // betStatus.sToBet = false;
        // betStatus.sBetted = true;
        // update(attrs);
        // setUserBetState(betStatus);
      }
    }
  }, [gameStateObj.gameState, userBetState.fToBet, userBetState.sToBet, token]);

  // New: Effect to send ping every 5 seconds
  useEffect(() => {
    if (!socket) return;

    const pingInterval = setInterval(() => {
      const date = Date.now();
      pingStart = date;
      socket.emit("ping");
    }, 5000);

    return () => clearInterval(pingInterval);
  }, [socket]);

  useEffect(() => {
    if (token) getMyBets();
  }, [token]);

  return (
    <MainContext.Provider
      value={{
        state: state,
        ...betLimit,
        ...userBetState,
        ...gameStateObj,
        currentTarget,
        bettedUsers: [...bettedUsers],
        ...bettedUserStats,
        showPopOverLay,
        showBetAmountNote,
        showCrashHistory,
        authLoading,
        setCurrentTarget,
        update: updateState,
        getMyBets,
        updateUserBetState,
        callCashOut,
        setShowPopOverLay,
        setShowBetAmountNote,
        setShowCrashHistory,
        getColorClasses,
      }}
    >
      {children}
    </MainContext.Provider>
  );
};

export default MainProvider;
