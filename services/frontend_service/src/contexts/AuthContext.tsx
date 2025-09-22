import React, { createContext, useState, useContext } from "react";

type AuthContextType = {
  token: string | null;
  setToken: (t: string | null) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setTokenState] = useState<string | null>(() => localStorage.getItem("yakhteh_token"));

  const setToken = (t: string | null) => {
    if (t) {
      localStorage.setItem("yakhteh_token", t);
    } else {
      localStorage.removeItem("yakhteh_token");
    }
    setTokenState(t);
  };

  const logout = () => setToken(null);

  return <AuthContext.Provider value={{ token, setToken, logout }}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
};