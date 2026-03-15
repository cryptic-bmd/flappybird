/* eslint-disable react-hooks/exhaustive-deps */
import { useEffect, useCallback, useState } from "react";

import {
  initDataRaw as _initDataRaw,
  useSignal,
} from '@telegram-apps/sdk-react';
import axios from 'axios';
import { toast } from "react-toastify";

import AuthContext, {type ErrorType } from "./authContext";
import { API_URL } from "../config";
import { getAxiosError } from "../utils/errors";
import { log } from "../utils/logger";


const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const initDataRaw = useSignal(_initDataRaw);

  const [token, setToken] = useState<string | null>(null);
  const [authLoading, setAuthLoading] = useState<boolean>(true);
  const [authError, setAuthError] = useState<string | null>(null);
  const [error, setError] = useState<ErrorType>({ message: "An error occurred" });

  const login = useCallback(async () => {
    setAuthError(null);
    try {
      if (!initDataRaw) {
        throw new Error('No initDataRaw available');
      }
      const response = await axios.post(
        `${API_URL}/auth/telegram`,
        { initDataRaw },
        { headers: { Authorization: `Bearer ${initDataRaw}` } }
      );
      const token = response.data.token;
      // console.log(`token: ${token}`);
      // localStorage.setItem('token', token);
      setToken(token);
      setAuthLoading(false);
    } catch (e) {
      // localStorage.removeItem('token');
      setError({ message: getAxiosError(e), autoClose: 5000 });
    }
  }, [initDataRaw]);

  useEffect(() => {
    if (token) return;

    const initializeAuth = async () => {
      await login();
    };

    initializeAuth();
  }, []);
  
  useEffect(() => {
    if (authError) {
      log(`authError: ${authError}`);
      toast.error(authError, {
        style: {
          backgroundColor: "rgba(0, 0, 0, 0.5)",
          borderRadius: "12px",
        },
        autoClose: 5000,
        hideProgressBar: true,
      });
    }
  }, [authError]);

  useEffect(() => {
    if (error && error.message !== "An error occurred") {
      log(`error: ${JSON.stringify(error)}`);
      toast.error(error.message, {
        style: {
          backgroundColor: "rgba(0, 0, 0, 0.5)",
          borderRadius: "12px",
        },
        autoClose: error.autoClose || 1000,
        hideProgressBar: error.hideProgressBar || true,
      });
    }
  }, [error])

  return (
    <AuthContext.Provider
      value={{
        token,
        authLoading,
        authError,
        error,
        setAuthError,
        setError,
        login: login,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export default AuthProvider;
