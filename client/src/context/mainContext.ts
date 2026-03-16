import { createContext, useContext } from "react";
import { io } from "socket.io-client";
import { SOCKET_URL } from "../config";


export interface BettedUserType {
  userID: number;
  userHash: string;
  betAmount: number;
  cashOut: number;
  cashedOut: boolean;
  target: number;
}

export interface BettedUserStatsType {
  noOfBets: number;
  totalBetAmount: number;
  noOfCashouts: number;
  totalWinnings: number;
  biggestWinning: number;
  biggestWinnerID: number;
  biggestWinnerUsername: string;
}

export interface UserBetStateType {
  fToBet: boolean;
  fBetted: boolean;
  sToBet: boolean;
  sBetted: boolean;
}

export interface UserType {
  balance: number;
  img: string;
  username: string;
  f: {
    auto: boolean;
    betted: boolean;
    cashedOut: boolean;
    betAmount: number;
    cashOutAmount: number;
    target: number;
  };
  s: {
    auto: boolean;
    betted: boolean;
    cashedOut: boolean;
    betAmount: number;
    cashOutAmount: number;
    target: number;
  };
}

export interface GameHistory {
  gameID: number;
  gameHash: string;
  crashPoint: number;
}

export interface GameStateType {
  gameState: string;
  currentMultiplier: number;
  serverTimeElapsed: number;
}

export interface GameBetLimit {
  maxBet: number;
  minBet: number;
}

export interface MyBetHistory {
  hash: string;
  betAmount: number;
  cashOutMultiplier: number;
  cashedOut: boolean | null;
  winnings: number;
  date: number;
}

export interface ContextDataType {
  gameHistory: GameHistory[];
  myBets: MyBetHistory[];
  userInfo: UserType;
  pingBarCount: number;
}

export interface ContextType extends GameBetLimit, UserBetStateType, GameStateType, BettedUserStatsType {
  state: ContextDataType;
  bettedUsers: BettedUserType[];
  currentTarget: number;
  showPopOverLay: boolean;
  showBetAmountNote: boolean;
  showCrashHistory: boolean;
  authLoading: boolean;
  setCurrentTarget(attrs: Partial<number>): void;
  update(attrs: Partial<ContextDataType>): void;
  getMyBets(): void;
  updateUserBetState(attrs: Partial<UserBetStateType>): void;
  callCashOut(index: "f" | "s"): void;
  setShowPopOverLay(state: boolean): void;
  setShowBetAmountNote(state: boolean): void;
  setShowCrashHistory(state: boolean): void;
  getColorClasses(multiplier: number): { bg: string; text: string };
}

export const socket = io(SOCKET_URL, {
  path: "/socket.io",
  transports: ['websocket'], // Force WebSocket, skip polling
});

const MainContext = createContext<ContextType>({} as ContextType);

export const useMainContext = () => {
  const context = useContext(MainContext);
  if (context === undefined) {
    throw new Error('useMainContext must be used within a MainContextProvider');
  }
  return context;
};

export default MainContext;
