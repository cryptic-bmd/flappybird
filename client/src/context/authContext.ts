import { createContext, useContext } from "react";

export interface ErrorType {
    message: string;
    autoClose?: number;
    hideProgressBar?: boolean;
}

interface AuthContextType {
  token: string | null;
  authLoading: boolean;
  authError: string | null;
  error: ErrorType;
  setAuthError: (error: string | null) => void;
  setError: (error: ErrorType) => void;
  login: () => void;
}

const AuthContext = createContext<AuthContextType>({} as AuthContextType);

export const useAuthContext = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuthContext must be used within a AuthContextProvider');
  }
  return context;
};

export default AuthContext;
