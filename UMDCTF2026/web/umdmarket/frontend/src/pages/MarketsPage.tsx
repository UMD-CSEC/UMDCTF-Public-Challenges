import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { useApp } from "../lib/store.tsx";
import { priceToPercent, balanceToDollars } from "../lib/protocol.ts";

// Ticker category icons (arrays of SVG path strings)
const TICKER_ICONS: Record<string, string[]> = {
  MATH404_A: ["M2 13l3 7L11 4h11"],
  HINT_RELEASE: [
    "M15 14c.2-1 .7-1.7 1.5-2.5c1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5c.7.7 1.3 1.5 1.5 2.5",
    "M9 18h6",
    "M10 22h4",
  ],
  P_EQ_NP: [
    "M4 12c0-2.2 1.8-4 4-4s4 1.8 4 4-1.8 4-4 4-4-1.8-4-4z",
    "M12 12c0-2.2 1.8-4 4-4s4 1.8 4 4-1.8 4-4 4-4-1.8-4-4z",
  ],
  PARTY_WINS: [
    "m9 12 2 2 4-4",
    "M5 7c0-1.1.9-2 2-2h10a2 2 0 0 1 2 2v12H5V7z",
    "M22 19H2",
  ],
  USDT_ABOVE_1: [
    "M6 4h12",
    "M12 4v16",
    "M7 10h10",
  ],
  HL3_2100: [
    "M7 3l7 17",
    "M10 10l-5 10",
  ],
  UMD_CS_T10: [
    "m12 10 2 4v3a1 1 0 0 0 1 1h2a1 1 0 0 0 1-1v-3a8 8 0 1 0-16 0v3a1 1 0 0 0 1 1h2a1 1 0 0 0 1-1v-3l2-4h4Z",
    "M4.82 7.9 8 10",
    "M15.18 7.9 12 10",
    "M16.93 10H20a2 2 0 0 1 0 4H2",
  ],
  AI_SWE_REPLACE: [
    "M12 2v3",
    "M5 7h14v12H5z",
    "M9 12h.01",
    "M15 12h.01",
    "M9 16h6",
    "M2 11h3",
    "M19 11h3",
  ],
  CTF_PRIZES: [
    "M20 12v10H4V12",
    "M2 7h20v5H2z",
    "M12 22V7",
    "M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z",
    "M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z",
  ],
  RAIN_SEA: [
    "M4 14.899A7 7 0 1 1 15.71 8h1.79a4.5 4.5 0 0 1 2.5 8.242",
    "M16 14v6",
    "M8 14v6",
    "M12 16v6",
  ],
  MRBEAST_SLOP: [
    "M22.54 6.42a2.78 2.78 0 0 0-1.94-2C18.88 4 12 4 12 4s-6.88 0-8.6.46a2.78 2.78 0 0 0-1.94 2A29 29 0 0 0 1 11.75a29 29 0 0 0 .46 5.33A2.78 2.78 0 0 0 3.4 19.13C5.12 19.56 12 19.56 12 19.56s6.88 0 8.6-.46a2.78 2.78 0 0 0 1.94-2 29 29 0 0 0 .46-5.25 29 29 0 0 0-.46-5.43z",
    "M9.75 15.02l5.75-3.27-5.75-3.27v6.54z",
  ],
  MIDEAST_PEACE: [
    "M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z",
    "M2 12h20",
    "M12 2a15 15 0 0 1 4 10 15 15 0 0 1-4 10",
    "M12 2a15 15 0 0 0-4 10 15 15 0 0 0 4 10",
  ],
  AMTRAK_NEC: [
    "M21 13c0-3.87-3.37-7-10-7H3",
    "M3 15h16a2 2 0 0 0 2-2",
    "M3 6v5h17.5",
    "M3 11v4",
    "M8 11V6",
    "M13 11V6.5",
    "M3 19h18",
  ],
  BILLIONAIRE_JAIL: [
    "M13 10l7.383 7.418c.823.82.823 2.148 0 2.967a2.11 2.11 0 0 1-2.976 0l-7.407-7.385",
    "M6 9l4 4",
    "M13 10l-4-4",
    "M3 21h7",
    "M6.793 15.793l-3.586-3.586a1 1 0 0 1 0-1.414l2.293-2.293.5.5 3-3-.5-.5 2.293-2.293a1 1 0 0 1 1.414 0l3.586 3.586a1 1 0 0 1 0 1.414l-2.293 2.293-.5-.5-3 3 .5.5-2.293 2.293a1 1 0 0 1-1.414 0",
  ],
};

// Ticker images (used instead of SVG when available)
const TICKER_IMAGES: Record<string, string> = {
  KRUSKAL_RETIRE: "/250px-ClydeKruskal2019.png",
};

const TICKER_COLORS: Record<string, string> = {
  KRUSKAL_RETIRE: "#f59e0b",
  MATH404_A: "#60a5fa",
  HINT_RELEASE: "#34d399",
  P_EQ_NP: "#a78bfa",
  PARTY_WINS: "#f472b6",
  USDT_ABOVE_1: "#2dd4bf",
  HL3_2100: "#fb923c",
  UMD_CS_T10: "#ef4444",
  AI_SWE_REPLACE: "#22d3ee",
  CTF_PRIZES: "#eab308",
  RAIN_SEA: "#94a3b8",
  MRBEAST_SLOP: "#f43f5e",
  MIDEAST_PEACE: "#8b5cf6",
  AMTRAK_NEC: "#1e6eb5",
  BILLIONAIRE_JAIL: "#d4d4d8",
};

const CARD_UPDATE_INTERVAL = 2000; // ms between visual price updates on summary page

function MarketCard({
  id,
  name,
  description,
  price,
  index,
  resolvedOutcome,
}: {
  id: number;
  name: string;
  description: string;
  price: number | undefined;
  index: number;
  resolvedOutcome?: number; // 0=YES, 1=NO, undefined=no recent resolution
}) {
  // Throttle displayed price: only update visually every CARD_UPDATE_INTERVAL ms
  const [displayPrice, setDisplayPrice] = useState(price);
  const lastUpdateRef = useRef(0);

  useEffect(() => {
    if (price === undefined) return;
    const now = Date.now();
    const elapsed = now - lastUpdateRef.current;
    if (elapsed >= CARD_UPDATE_INTERVAL) {
      setDisplayPrice(price);
      lastUpdateRef.current = now;
    } else {
      const timer = setTimeout(() => {
        setDisplayPrice(price);
        lastUpdateRef.current = Date.now();
      }, CARD_UPDATE_INTERVAL - elapsed);
      return () => clearTimeout(timer);
    }
  }, [price]);

  const pct = displayPrice !== undefined ? priceToPercent(displayPrice) : null;
  const noPct = pct !== null ? 100 - pct : null;
  const prevPriceRef = useRef<number | undefined>(undefined);
  const cardRef = useRef<HTMLDivElement>(null);
  const color = TICKER_COLORS[name] || "#3d5afe";

  useEffect(() => {
    if (
      prevPriceRef.current !== undefined &&
      displayPrice !== undefined &&
      displayPrice !== prevPriceRef.current
    ) {
      const el = cardRef.current;
      if (el) {
        el.classList.remove("flash-up", "flash-down");
        void el.offsetWidth;
        el.classList.add(
          displayPrice > prevPriceRef.current ? "flash-up" : "flash-down",
        );
      }
    }
    prevPriceRef.current = displayPrice;
  }, [displayPrice]);

  return (
    <Link
      to={`/market/${id}`}
      className="block group"
    >
      <div
        ref={cardRef}
        className={`animate-slide-up stagger-${index + 1} relative bg-surface-2 border border-border rounded-2xl p-6 hover:border-border-light hover:bg-surface-3/50 transition-all duration-300 overflow-hidden`}
      >
        {/* Subtle top accent line */}
        <div
          className="absolute top-0 left-0 right-0 h-[2px] opacity-40 group-hover:opacity-70 transition-opacity"
          style={{ background: `linear-gradient(90deg, transparent, ${color}, transparent)` }}
        />

        {resolvedOutcome !== undefined && (
          <div
            className={`absolute top-2 right-2 z-10 px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider ${
              resolvedOutcome === 0
                ? "bg-yes/20 text-yes border border-yes/40"
                : "bg-no/20 text-no border border-no/40"
            }`}
            title="Market resolved: positions wiped, price reset"
          >
            Resolved {resolvedOutcome === 0 ? "YES" : "NO"}
          </div>
        )}

        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div
              className="w-10 h-10 rounded-xl flex items-center justify-center overflow-hidden"
              style={{ background: `${color}15` }}
            >
              {TICKER_IMAGES[name] ? (
                <img src={TICKER_IMAGES[name]} alt={name} className="w-full h-full object-cover" />
              ) : (
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke={color}
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  {(TICKER_ICONS[name] || ["M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"]).map((d, i) => (
                    <path key={i} d={d} />
                  ))}
                </svg>
              )}
            </div>
            <div>
              <span
                className="text-[10px] font-mono font-bold uppercase tracking-widest"
                style={{ color }}
              >
                {name}
              </span>
            </div>
          </div>
          {/* Live indicator */}
          {price !== undefined && (
            <div className="flex items-center gap-1.5">
              <div className="w-1.5 h-1.5 rounded-full bg-yes animate-pulse" />
              <span className="text-[10px] text-muted uppercase tracking-wider font-medium">
                Live
              </span>
            </div>
          )}
        </div>

        {/* Question */}
        <h3 className="text-[15px] font-semibold text-white leading-snug mb-5 group-hover:text-white/90">
          {description}
        </h3>

        {/* Probability bar */}
        {pct !== null && (
          <div className="mb-4">
            <div className="h-1.5 bg-surface rounded-full overflow-hidden">
              <div
                className="h-full bg-yes/60 rounded-full transition-all duration-500 ease-out"
                style={{ width: `${pct}%` }}
              />
            </div>
          </div>
        )}

        {/* Yes / No pills */}
        <div className="flex gap-2">
          <div className="flex-1 flex items-center justify-between px-4 py-3 bg-yes-dim border border-yes/10 rounded-xl">
            <span className="text-xs font-semibold text-yes/80 uppercase tracking-wider">
              Yes
            </span>
            <span className="text-lg font-mono font-bold text-yes">
              {pct !== null ? `${pct.toFixed(1)}¢` : "-"}
            </span>
          </div>
          <div className="flex-1 flex items-center justify-between px-4 py-3 bg-no-dim border border-no/10 rounded-xl">
            <span className="text-xs font-semibold text-no/80 uppercase tracking-wider">
              No
            </span>
            <span className="text-lg font-mono font-bold text-no">
              {noPct !== null ? `${noPct.toFixed(1)}¢` : "-"}
            </span>
          </div>
        </div>
      </div>
    </Link>
  );
}

export function MarketsPage() {
  const {
    tickers,
    prices,
    balance,
    portfolio,
    refreshPortfolio,
    client,
    recentResolutions,
  } = useApp();

  useEffect(() => {
    refreshPortfolio().catch(() => {});
  }, [refreshPortfolio]);

  const flagPrice = 10_000_000;
  const canBuyFlag = balance >= BigInt(flagPrice);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-10 animate-fade-in">
        <h1 className="text-3xl font-bold text-white tracking-tight mb-2">
          Markets
        </h1>
        <p className="text-muted text-sm">
          Trade prediction contracts on real-world events. Prices reflect market
          probability.
        </p>
      </div>

      {/* Flag banner */}
      {canBuyFlag && (
        <div className="mb-8 p-5 bg-primary-dim border border-primary/20 rounded-2xl animate-slide-up">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-white mb-1">
                You can afford the flag!
              </h3>
              <p className="text-sm text-text-dim">
                Your balance of{" "}
                <span className="font-mono font-bold text-yes">
                  ${balanceToDollars(balance)}
                </span>{" "}
                exceeds the flag price of{" "}
                <span className="font-mono font-bold text-white">
                  $1,000.00
                </span>
              </p>
            </div>
            <FlagButton />
          </div>
        </div>
      )}

      {/* Portfolio summary */}
      {portfolio && portfolio.positions.length > 0 && (
        <div className="mb-8 animate-fade-in">
          <h2 className="text-sm font-semibold text-muted uppercase tracking-wider mb-3">
            Your Positions
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {portfolio.positions.map((pos) => {
              const ticker = tickers.find((t) => t.id === pos.tickerId);
              const price = prices.get(pos.tickerId);
              return (
                <Link
                  key={pos.tickerId}
                  to={`/market/${pos.tickerId}`}
                  className="flex items-center justify-between px-4 py-3 bg-surface-2 border border-border rounded-xl hover:border-border-light transition-colors"
                >
                  <span className="text-sm font-medium text-white truncate mr-3">
                    {ticker?.name || `#${pos.tickerId}`}
                  </span>
                  <div className="flex items-center gap-3 shrink-0">
                    {pos.yesQty > 0 && (
                      <span className="text-xs font-mono text-yes">
                        {pos.yesQty} YES
                      </span>
                    )}
                    {pos.noQty > 0 && (
                      <span className="text-xs font-mono text-no">
                        {pos.noQty} NO
                      </span>
                    )}
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      )}

      {/* Market grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {tickers.map((ticker, i) => (
          <MarketCard
            key={ticker.id}
            id={ticker.id}
            name={ticker.name}
            description={ticker.description}
            price={prices.get(ticker.id)}
            index={i}
            resolvedOutcome={recentResolutions.get(ticker.id)?.outcome}
          />
        ))}
      </div>

      {tickers.length === 0 && (
        <div className="text-center py-20">
          <div className="inline-flex items-center gap-2 text-muted">
            <svg
              className="animate-spin h-4 w-4"
              viewBox="0 0 24 24"
              fill="none"
            >
              <circle
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="3"
                className="opacity-25"
              />
              <path
                d="M4 12a8 8 0 018-8"
                stroke="currentColor"
                strokeWidth="3"
                strokeLinecap="round"
              />
            </svg>
            Loading markets...
          </div>
        </div>
      )}
    </div>
  );
}

function FlagButton() {
  const { client } = useApp();
  const [flag, setFlag] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleBuy = async () => {
    setLoading(true);
    try {
      const f = await client.buyFlag();
      setFlag(f);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (flag) {
    return (
      <div className="px-5 py-3 bg-yes-dim border border-yes/30 rounded-xl">
        <div className="text-xs text-yes/70 mb-1 font-medium">FLAG</div>
        <code className="text-sm font-mono font-bold text-yes break-all">
          {flag}
        </code>
      </div>
    );
  }

  return (
    <button
      onClick={handleBuy}
      disabled={loading}
      className="px-6 py-3 bg-primary hover:bg-primary-hover text-white font-bold rounded-xl transition-all shadow-lg shadow-primary/30 active:scale-95 disabled:opacity-50"
    >
      {loading ? "Buying..." : "Buy Flag · $1,000"}
    </button>
  );
}

