import {
  createContext,
  useContext,
  useState,
  useCallback,
  useRef,
  useEffect,
  type ReactNode,
} from "react";
import {
  PredictionMarketClient,
  type Ticker,
  type QuoteUpdate,
  type Portfolio,
  type ResolutionEvent,
} from "./client.ts";

const SERVER_URL =
  (import.meta as any).env?.VITE_SERVER_URL || "https://localhost:4443/wt";

// Baked at build time from the certgen Docker stage (see top-level Dockerfile)
// or from scripts/certgen.sh for local non-Docker dev.
const CERT_HASH_HEX: string | undefined =
  (import.meta as any).env?.VITE_CERT_HASH;

const SESSION_KEY = "umdmarket_session";

interface SavedSession {
  username: string;
  password: string;
}

function saveSession(username: string, password: string) {
  sessionStorage.setItem(SESSION_KEY, JSON.stringify({ username, password }));
}

function loadSession(): SavedSession | null {
  try {
    const raw = sessionStorage.getItem(SESSION_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as SavedSession;
  } catch {
    return null;
  }
}

function clearSession() {
  sessionStorage.removeItem(SESSION_KEY);
}

function hexToBytes(hex: string): Uint8Array {
  const clean = hex.trim();
  if (clean.length % 2 !== 0) {
    throw new Error(`cert hash has odd length (${clean.length})`);
  }
  const bytes = new Uint8Array(clean.length / 2);
  for (let i = 0; i < clean.length; i += 2) {
    bytes[i / 2] = parseInt(clean.substring(i, i + 2), 16);
  }
  return bytes;
}

// Build-time cert hash. Undefined in bare `pnpm dev` without a generated
// cert; in that case callers should connect without a hash (i.e., rely on
// a browser that trusts the cert some other way).
export const CERT_HASH: Uint8Array | undefined = CERT_HASH_HEX
  ? hexToBytes(CERT_HASH_HEX)
  : undefined;

export interface RecentResolution {
  tickerId: number;
  outcome: number; // 0 = YES, 1 = NO
  at: number; // Date.now() of the event
}

interface AppState {
  client: PredictionMarketClient;
  connected: boolean;
  authenticated: boolean;
  restoring: boolean;
  disconnectReason: string | null;
  username: string;
  balance: bigint;
  tickers: Ticker[];
  prices: Map<number, number>;
  latestSeqs: Map<number, number>;
  portfolio: Portfolio | null;
  recentResolutions: Map<number, RecentResolution>;

  getLatestSeq: (tickerId: number) => number | undefined;
  getLatestQuote: (tickerId: number) => QuoteUpdate | undefined;
  connectAndLogin: (username: string, password: string) => Promise<void>;
  connectAndRegister: (username: string, password: string) => Promise<void>;
  logout: () => void;
  refreshPortfolio: () => Promise<void>;
  setBalance: (b: bigint) => void;
}

const AppContext = createContext<AppState | null>(null);

async function doConnect(client: PredictionMarketClient): Promise<void> {
  await client.connect(SERVER_URL, CERT_HASH);
}

async function doPostAuth(
  client: PredictionMarketClient,
  setTickers: (t: Ticker[]) => void,
): Promise<void> {
  const tickerList = await client.fetchTickers();
  setTickers(tickerList);
  for (const t of tickerList) {
    await client.subscribe(t.id);
  }
}

export function AppProvider({ children }: { children: ReactNode }) {
  const clientRef = useRef(new PredictionMarketClient());
  const [connected, setConnected] = useState(false);
  const [authenticated, setAuthenticated] = useState(false);
  const [restoring, setRestoring] = useState(false);
  const [disconnectReason, setDisconnectReason] = useState<string | null>(null);
  const [username, setUsername] = useState("");
  const [balance, setBalance] = useState<bigint>(0n);
  const [tickers, setTickers] = useState<Ticker[]>([]);
  const [prices, setPrices] = useState<Map<number, number>>(new Map());
  const [latestSeqs, setLatestSeqs] = useState<Map<number, number>>(new Map());
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [recentResolutions, setRecentResolutions] = useState<
    Map<number, RecentResolution>
  >(new Map());

  // Accumulate quotes into mutable buffers, flush to React state every 500ms.
  const pendingPrices = useRef(new Map<number, number>());
  const pendingSeqs = useRef(new Map<number, number>());
  const pendingQuotes = useRef(new Map<number, QuoteUpdate>());
  const dirty = useRef(false);

  useEffect(() => {
    const client = clientRef.current;
    const unsubQuote = client.onQuote((quote: QuoteUpdate) => {
      pendingPrices.current.set(quote.tickerId, quote.yesPrice);
      pendingSeqs.current.set(quote.tickerId, quote.seq);
      pendingQuotes.current.set(quote.tickerId, quote);
      dirty.current = true;
    });

    const flushInterval = setInterval(() => {
      if (!dirty.current) return;
      dirty.current = false;

      setPrices((prev) => {
        const next = new Map(prev);
        for (const [k, v] of pendingPrices.current) next.set(k, v);
        return next;
      });
      setLatestSeqs((prev) => {
        const next = new Map(prev);
        for (const [k, v] of pendingSeqs.current) next.set(k, v);
        return next;
      });
    }, 500);

    const unsubResolution = client.onResolution((event: ResolutionEvent) => {
      // Drop any cached quote/seq for the resolved ticker: the server is
      // about to emit a fresh quote at the reset price, and meanwhile the
      // stale token in our buffer is not tradeable.
      pendingPrices.current.delete(event.tickerId);
      pendingSeqs.current.delete(event.tickerId);
      pendingQuotes.current.delete(event.tickerId);
      setPrices((prev) => {
        if (!prev.has(event.tickerId)) return prev;
        const next = new Map(prev);
        next.delete(event.tickerId);
        return next;
      });
      setLatestSeqs((prev) => {
        if (!prev.has(event.tickerId)) return prev;
        const next = new Map(prev);
        next.delete(event.tickerId);
        return next;
      });
      setRecentResolutions((prev) => {
        const next = new Map(prev);
        next.set(event.tickerId, {
          tickerId: event.tickerId,
          outcome: event.outcome,
          at: Date.now(),
        });
        return next;
      });
      // Pull fresh balance/positions since resolution zeroed holdings.
      client.portfolio().then(setPortfolio).catch(() => {});
    });

    const unsubDisconnect = client.onDisconnect(() => {
      setConnected((wasConnected) => {
        if (wasConnected) {
          setDisconnectReason("Session disconnected: you may have logged in from another tab.");
        }
        return false;
      });
      setAuthenticated(false);
      clearSession();
    });

    // Sweep expired resolution badges every 2s.
    const resolutionSweep = setInterval(() => {
      setRecentResolutions((prev) => {
        const cutoff = Date.now() - 5000;
        let changed = false;
        const next = new Map<number, RecentResolution>();
        for (const [k, v] of prev) {
          if (v.at >= cutoff) {
            next.set(k, v);
          } else {
            changed = true;
          }
        }
        return changed ? next : prev;
      });
    }, 2000);

    return () => {
      unsubQuote();
      unsubResolution();
      unsubDisconnect();
      clearInterval(flushInterval);
      clearInterval(resolutionSweep);
    };
  }, []);

  // Auto-restore session on mount
  useEffect(() => {
    const saved = loadSession();
    if (!saved) return;

    setRestoring(true);
    const client = clientRef.current;

    (async () => {
      try {
        await doConnect(client);
        setConnected(true);
        const result = await client.login(saved.username, saved.password);
        setAuthenticated(true);
        setUsername(saved.username);
        setBalance(result.balance);
        await doPostAuth(client, setTickers);
      } catch {
        // Credentials expired or server restarted; clear and show login
        clearSession();
      } finally {
        setRestoring(false);
      }
    })();
  }, []);

  const connectAndLogin = useCallback(async (user: string, pass: string) => {
    setDisconnectReason(null);
    const client = clientRef.current;
    if (!client.connected) {
      await doConnect(client);
      setConnected(true);
    }
    const result = await client.login(user, pass);
    setAuthenticated(true);
    setUsername(user);
    setBalance(result.balance);
    saveSession(user, pass);
    await doPostAuth(client, setTickers);
  }, []);

  const connectAndRegister = useCallback(async (user: string, pass: string) => {
    setDisconnectReason(null);
    const client = clientRef.current;
    if (!client.connected) {
      await doConnect(client);
      setConnected(true);
    }
    const result = await client.register(user, pass);
    setAuthenticated(true);
    setUsername(user);
    setBalance(result.balance);
    saveSession(user, pass);
    await doPostAuth(client, setTickers);
  }, []);

  const logout = useCallback(() => {
    clearSession();
    clientRef.current.close();
    setConnected(false);
    setAuthenticated(false);
    setUsername("");
    setBalance(0n);
    setTickers([]);
    setPrices(new Map());
    setLatestSeqs(new Map());
    setPortfolio(null);
    setRecentResolutions(new Map());
  }, []);

  const refreshPortfolio = useCallback(async () => {
    const p = await clientRef.current.portfolio();
    setPortfolio(p);
    setBalance(p.balance);
  }, []);

  // Real-time seq getter. Reads from mutable ref, not throttled React state.
  const getLatestSeq = useCallback(
    (tickerId: number) => pendingSeqs.current.get(tickerId),
    [],
  );

  // Real-time quote token, needed at trade time so the client can echo the
  // full signed quote back to the server.
  const getLatestQuote = useCallback(
    (tickerId: number) => pendingQuotes.current.get(tickerId),
    [],
  );

  return (
    <AppContext.Provider
      value={{
        client: clientRef.current,
        connected,
        authenticated,
        restoring,
        disconnectReason,
        username,
        balance,
        tickers,
        prices,
        latestSeqs,
        portfolio,
        recentResolutions,
        getLatestSeq,
        getLatestQuote,
        connectAndLogin,
        connectAndRegister,
        logout,
        refreshPortfolio,
        setBalance,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp(): AppState {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useApp must be used within AppProvider");
  return ctx;
}
