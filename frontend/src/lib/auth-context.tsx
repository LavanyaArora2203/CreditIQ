import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { api, type UserProfile } from "./api-client";

const TOKEN_KEY = "loan_assistant_token";
const CID_KEY = "loan_assistant_cid";

type AuthState = {
  token: string | null;
  customerId: string | null;
  profile: UserProfile | null;
  loading: boolean;
  login: (customerId: string, password: string) => Promise<void>;
  signup: (customerId: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [customerId, setCustomerId] = useState<string | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  // Bootstrap from localStorage on client only.
  useEffect(() => {
    const t = typeof window !== "undefined" ? window.localStorage.getItem(TOKEN_KEY) : null;
    const c = typeof window !== "undefined" ? window.localStorage.getItem(CID_KEY) : null;
    if (t && c) {
      setToken(t);
      setCustomerId(c);
      api
        .me(t)
        .then(setProfile)
        .catch(() => {
          // Token invalid or server down — clear it.
          window.localStorage.removeItem(TOKEN_KEY);
          window.localStorage.removeItem(CID_KEY);
          setToken(null);
          setCustomerId(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const persist = useCallback((t: string, cid: string) => {
    if (typeof window !== "undefined") {
      window.localStorage.setItem(TOKEN_KEY, t);
      window.localStorage.setItem(CID_KEY, cid);
    }
    setToken(t);
    setCustomerId(cid);
  }, []);

  const login = useCallback(
    async (cid: string, password: string) => {
      const res = await api.login(cid.trim().toUpperCase(), password);
      persist(res.access_token, res.customer_id);
      const p = await api.me(res.access_token).catch(() => null);
      setProfile(p);
    },
    [persist],
  );

  const signup = useCallback(
    async (cid: string, password: string) => {
      const res = await api.signup(cid.trim().toUpperCase(), password);
      persist(res.access_token, res.customer_id);
      const p = await api.me(res.access_token).catch(() => null);
      setProfile(p);
    },
    [persist],
  );

  const logout = useCallback(() => {
    if (typeof window !== "undefined") {
      window.localStorage.removeItem(TOKEN_KEY);
      window.localStorage.removeItem(CID_KEY);
    }
    setToken(null);
    setCustomerId(null);
    setProfile(null);
  }, []);

  const value = useMemo<AuthState>(
    () => ({ token, customerId, profile, loading, login, signup, logout }),
    [token, customerId, profile, loading, login, signup, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}
