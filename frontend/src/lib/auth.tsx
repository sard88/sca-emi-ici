"use client";

import type { ReactNode } from "react";
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { getMe, login as apiLogin, logout as apiLogout } from "./api";
import type { AuthenticatedUser } from "./types";

type AuthState = {
  user: AuthenticatedUser | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthenticatedUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const me = await getMe();
      setUser(me.authenticated ? me : null);
    } catch (err) {
      setUser(null);
      setError(err instanceof Error ? err.message : "No fue posible validar la sesión.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const login = useCallback(async (username: string, password: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiLogin(username, password);
      setUser(response.user);
    } catch (err) {
      setUser(null);
      const message = err instanceof Error ? err.message : "No fue posible iniciar sesión.";
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      await apiLogout();
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const value = useMemo(() => ({ user, loading, error, refresh, login, logout }), [user, loading, error, refresh, login, logout]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) {
    throw new Error("useAuth debe usarse dentro de AuthProvider");
  }
  return value;
}
