import { createContext, useContext, useState, type ReactNode } from "react";
import type { User, AuthTokens } from "../types";
import * as api from "../services/apiClient";
import { setAccessToken } from "../services/tokenStore";

interface AuthContextValue {
  user: User | null;
  tokens: AuthTokens | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [tokens, setTokens] = useState<AuthTokens | null>(null);

  async function login(email: string, password: string) {
    const t = await api.login(email, password);
    setTokens(t);
    setAccessToken(t.access_token);
    setUser({ email, role: "user" });
  }

  async function register(email: string, password: string) {
    const u = await api.register(email, password);
    setUser(u);
  }

  function logout() {
    setUser(null);
    setTokens(null);
    setAccessToken(null);
  }

  return (
    <AuthContext.Provider value={{ user, tokens, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}