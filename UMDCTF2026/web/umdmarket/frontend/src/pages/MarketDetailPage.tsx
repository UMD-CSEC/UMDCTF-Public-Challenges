import { useEffect, useRef, useState, useCallback } from "react";
import { useParams, Link } from "react-router-dom";
import { createChart, AreaSeries, type IChartApi, type ISeriesApi, ColorType, LineStyle } from "lightweight-charts";
import { useApp } from "../lib/store.tsx";
import {
  priceToPercent,
  balanceToDollars,
  PRICE_UNIT,
  SIDE_BUY_YES,
  SIDE_BUY_NO,
  SIDE_SELL_YES,
  SIDE_SELL_NO,
} from "../lib/protocol.ts";

export function MarketDetailPage() {
  const { id } = useParams<{ id: string }>();
  const tickerId = parseInt(id || "0", 10);
  const {
    client,
    tickers,
    prices,
    getLatestQuote,
    balance,
    refreshPortfolio,
    portfolio,
    setBalance,
    recentResolutions,
  } = useApp();

  const ticker = tickers.find((t) => t.id === tickerId);
  const currentPrice = prices.get(tickerId);
  const pct = currentPrice !== undefined ? priceToPercent(currentPrice) : null;
  const recentlyResolved = recentResolutions.get(tickerId);

  const [historyMinutes, setHistoryMinutes] = useState(1); // 1 = realtime mode
  const [tradeDirection, setTradeDirection] = useState<"yes" | "no">("yes");
  const [tradeAction, setTradeAction] = useState<"buy" | "sell">("buy");
  const [qty, setQty] = useState("10");
  const [tradeLoading, setTradeLoading] = useState(false);
  const [tradeResult, setTradeResult] = useState<string | null>(null);
  const [tradeError, setTradeError] = useState<string | null>(null);

  // Fetch portfolio on mount
  useEffect(() => {
    refreshPortfolio().catch(() => {});
  }, [refreshPortfolio]);

  const position = portfolio?.positions.find((p) => p.tickerId === tickerId);

  // Determine the side byte
  const getSide = (): number => {
    if (tradeAction === "buy" && tradeDirection === "yes") return SIDE_BUY_YES;
    if (tradeAction === "buy" && tradeDirection === "no") return SIDE_BUY_NO;
    if (tradeAction === "sell" && tradeDirection === "yes") return SIDE_SELL_YES;
    return SIDE_SELL_NO;
  };

  // Cost calculation
  const qtyNum = parseInt(qty) || 0;
  const tradePrice =
    currentPrice !== undefined
      ? tradeDirection === "yes"
        ? tradeAction === "buy"
          ? currentPrice
          : currentPrice
        : tradeAction === "buy"
          ? PRICE_UNIT - currentPrice
          : PRICE_UNIT - currentPrice
      : 0;
  const estimatedCost = qtyNum * tradePrice;

  const handleTrade = useCallback(async () => {
    // Read the latest signed quote token at trade time and echo it to the
    // server. The token carries seq + ticker + price + hmac.
    const freshQuote = getLatestQuote(tickerId);
    if (freshQuote === undefined || qtyNum <= 0) return;
    setTradeLoading(true);
    setTradeError(null);
    setTradeResult(null);

    try {
      const result = await client.trade(freshQuote, getSide(), qtyNum);
      const fillPct = priceToPercent(result.fillPrice).toFixed(2);
      setTradeResult(
        `Filled ${qtyNum} contracts at ${fillPct}¢. New balance: $${balanceToDollars(result.newBalance)}`,
      );
      setBalance(result.newBalance);
      await refreshPortfolio();
    } catch (err: any) {
      setTradeError(err.message || "Trade failed");
    } finally {
      setTradeLoading(false);
    }
  }, [qtyNum, tickerId, tradeDirection, tradeAction, client, getLatestQuote, refreshPortfolio, setBalance]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Breadcrumb */}
      <div className="mb-6 animate-fade-in">
        <Link
          to="/"
          className="inline-flex items-center gap-1.5 text-sm text-muted hover:text-white transition-colors"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M19 12H5M12 19l-7-7 7-7" />
          </svg>
          Markets
        </Link>
      </div>

      {recentlyResolved && (
        <div
          className={`mb-6 px-4 py-3 rounded-xl border text-sm font-medium animate-fade-in ${
            recentlyResolved.outcome === 0
              ? "bg-yes/10 border-yes/30 text-yes"
              : "bg-no/10 border-no/30 text-no"
          }`}
        >
          Market just resolved{" "}
          <span className="font-bold uppercase">
            {recentlyResolved.outcome === 0 ? "YES" : "NO"}
          </span>
          . Any positions you held were wiped, and the price has been reset.
          Trading resumes immediately.
        </div>
      )}

      {/* Title area */}
      <div className="mb-8 animate-slide-up">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-xs font-mono font-bold text-primary uppercase tracking-widest">
            {ticker?.name || `Ticker #${tickerId}`}
          </span>
          {currentPrice !== undefined && (
            <div className="flex items-center gap-1.5 ml-2">
              <div className="w-1.5 h-1.5 rounded-full bg-yes animate-pulse" />
              <span className="text-[10px] text-muted uppercase tracking-wider font-medium">
                Live
              </span>
            </div>
          )}
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
          {ticker?.description || "Loading..."}
        </h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chart area - 2 cols */}
        <div className="lg:col-span-2 space-y-4">
          {/* Price display */}
          <div className="flex items-end gap-6 animate-fade-in">
            <div>
              <div className="text-xs text-muted uppercase tracking-wider mb-1">
                Yes Price
              </div>
              <div className="text-4xl font-mono font-bold text-yes">
                {pct !== null ? `${pct.toFixed(2)}¢` : "-"}
              </div>
            </div>
            <div>
              <div className="text-xs text-muted uppercase tracking-wider mb-1">
                No Price
              </div>
              <div className="text-4xl font-mono font-bold text-no">
                {pct !== null ? `${(100 - pct).toFixed(2)}¢` : "-"}
              </div>
            </div>
          </div>

          {/* Chart */}
          <div className="bg-surface-2 border border-border rounded-2xl overflow-hidden animate-slide-up stagger-2">
            {/* Time controls */}
            <div className="flex items-center gap-1 p-3 border-b border-border">
              {[
                { label: "1m", value: 1 },
                { label: "15m", value: 15 },
                { label: "30m", value: 30 },
                { label: "1h", value: 60 },
                { label: "All", value: 1440 },
              ].map((opt) => (
                <button
                  key={opt.value}
                  onClick={() => setHistoryMinutes(opt.value)}
                  className={`px-3.5 py-1.5 text-xs font-semibold rounded-lg transition-all ${
                    historyMinutes === opt.value
                      ? "bg-surface-4 text-white"
                      : "text-muted hover:text-white hover:bg-surface-3"
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>

            <PriceChart
              tickerId={tickerId}
              minutes={historyMinutes}
              currentPrice={currentPrice}
            />
          </div>

          {/* Position info */}
          {position && (position.yesQty > 0 || position.noQty > 0) && (
            <div className="bg-surface-2 border border-border rounded-2xl p-5 animate-fade-in">
              <h3 className="text-sm font-semibold text-muted uppercase tracking-wider mb-3">
                Your Position
              </h3>
              <div className="flex gap-4">
                {position.yesQty > 0 && (
                  <div className="flex-1 px-4 py-3 bg-yes-dim border border-yes/10 rounded-xl">
                    <div className="text-xs text-yes/70 mb-1">Yes Contracts</div>
                    <div className="text-xl font-mono font-bold text-yes">
                      {position.yesQty}
                    </div>
                    {currentPrice !== undefined && (
                      <div className="text-xs text-yes/60 font-mono mt-1">
                        Value: ${balanceToDollars(position.yesQty * currentPrice)}
                      </div>
                    )}
                  </div>
                )}
                {position.noQty > 0 && (
                  <div className="flex-1 px-4 py-3 bg-no-dim border border-no/10 rounded-xl">
                    <div className="text-xs text-no/70 mb-1">No Contracts</div>
                    <div className="text-xl font-mono font-bold text-no">
                      {position.noQty}
                    </div>
                    {currentPrice !== undefined && (
                      <div className="text-xs text-no/60 font-mono mt-1">
                        Value: ${balanceToDollars(position.noQty * (PRICE_UNIT - currentPrice))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Trading panel - 1 col */}
        <div className="animate-slide-up stagger-3">
          <div className="sticky top-24 bg-surface-2 border border-border rounded-2xl overflow-hidden">
            {/* Direction toggle */}
            <div className="flex p-1.5 m-4 bg-surface rounded-xl">
              <button
                onClick={() => setTradeDirection("yes")}
                className={`flex-1 py-2.5 text-sm font-bold rounded-lg transition-all duration-200 ${
                  tradeDirection === "yes"
                    ? "bg-yes/15 text-yes shadow-sm"
                    : "text-muted hover:text-yes/70"
                }`}
              >
                Yes
              </button>
              <button
                onClick={() => setTradeDirection("no")}
                className={`flex-1 py-2.5 text-sm font-bold rounded-lg transition-all duration-200 ${
                  tradeDirection === "no"
                    ? "bg-no/15 text-no shadow-sm"
                    : "text-muted hover:text-no/70"
                }`}
              >
                No
              </button>
            </div>

            {/* Buy / Sell toggle */}
            <div className="flex gap-2 mx-4 mb-5">
              <button
                onClick={() => setTradeAction("buy")}
                className={`flex-1 py-2 text-xs font-bold uppercase tracking-wider rounded-lg border transition-all ${
                  tradeAction === "buy"
                    ? "border-yes/30 bg-yes-dim text-yes"
                    : "border-border text-muted hover:text-white hover:border-border-light"
                }`}
              >
                Buy
              </button>
              <button
                onClick={() => setTradeAction("sell")}
                className={`flex-1 py-2 text-xs font-bold uppercase tracking-wider rounded-lg border transition-all ${
                  tradeAction === "sell"
                    ? "border-no/30 bg-no-dim text-no"
                    : "border-border text-muted hover:text-white hover:border-border-light"
                }`}
              >
                Sell
              </button>
            </div>

            <div className="px-4 space-y-4">
              {/* Price display */}
              <div className="flex justify-between items-center py-3 px-4 bg-surface rounded-xl">
                <span className="text-xs text-muted font-medium">
                  Price
                </span>
                <span
                  className={`text-lg font-mono font-bold ${
                    tradeDirection === "yes" ? "text-yes" : "text-no"
                  }`}
                >
                  {currentPrice !== undefined
                    ? `${priceToPercent(tradeDirection === "yes" ? currentPrice : PRICE_UNIT - currentPrice).toFixed(2)}¢`
                    : "-"}
                </span>
              </div>

              {/* Quantity */}
              <div>
                <label className="block text-xs text-muted font-medium uppercase tracking-wider mb-2">
                  Contracts
                </label>
                <input
                  type="number"
                  min="1"
                  step="1"
                  value={qty}
                  onChange={(e) => setQty(e.target.value)}
                  className="w-full px-4 py-3 bg-surface border border-border rounded-xl text-white font-mono text-base focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/30 transition-all"
                  placeholder="Quantity"
                />
                {/* Quick qty buttons */}
                <div className="flex gap-2 mt-2">
                  {[10, 100, 500, 1000].map((q) => (
                    <button
                      key={q}
                      onClick={() => setQty(String(q))}
                      className="flex-1 py-1.5 text-[11px] font-mono font-medium text-muted hover:text-white bg-surface-3 hover:bg-surface-4 rounded-lg transition-colors"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>

              {/* Cost summary */}
              <div className="space-y-2 py-3 border-t border-border">
                <div className="flex justify-between text-sm">
                  <span className="text-muted">Est. Cost</span>
                  <span className="font-mono font-semibold text-white">
                    ${balanceToDollars(estimatedCost)}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted">Potential Return</span>
                  <span className="font-mono font-semibold text-yes">
                    ${balanceToDollars(qtyNum * PRICE_UNIT)}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-muted">Balance</span>
                  <span className="font-mono font-semibold text-text-dim">
                    ${balanceToDollars(balance)}
                  </span>
                </div>
              </div>
            </div>

            {/* Submit */}
            <div className="p-4">
              <button
                onClick={handleTrade}
                disabled={tradeLoading || qtyNum <= 0 || currentPrice === undefined}
                className={`w-full py-3.5 font-bold rounded-xl transition-all duration-200 active:scale-[0.98] disabled:opacity-40 disabled:cursor-not-allowed ${
                  tradeAction === "buy"
                    ? "bg-yes hover:brightness-110 text-black shadow-lg shadow-yes/20"
                    : "bg-no hover:brightness-110 text-white shadow-lg shadow-no/20"
                }`}
              >
                {tradeLoading
                  ? "Executing..."
                  : `${tradeAction === "buy" ? "Buy" : "Sell"} ${tradeDirection.toUpperCase()}`}
              </button>

              {tradeResult && (
                <div className="mt-3 px-4 py-3 bg-yes-dim border border-yes/20 rounded-xl text-yes text-xs font-medium animate-fade-in">
                  {tradeResult}
                </div>
              )}
              {tradeError && (
                <div className="mt-3 px-4 py-3 bg-no-dim border border-no/20 rounded-xl text-no text-xs font-medium animate-fade-in">
                  {tradeError}
                </div>
              )}
            </div>

            {/* Cooldown note */}
            <div className="px-4 pb-4">
              <p className="text-[11px] text-muted/60 leading-relaxed">
                5s cooldown between trades. Quotes valid for 500ms.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ---------- Chart Component ----------

function PriceChart({
  tickerId,
  minutes,
  currentPrice,
}: {
  tickerId: number;
  minutes: number;
  currentPrice: number | undefined;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<any>(null);
  const { client, prices, getLatestSeq } = useApp();

  // Create chart
  useEffect(() => {
    if (!containerRef.current) return;

    const chart = createChart(containerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: "transparent" },
        textColor: "#72727e",
        fontFamily: "'JetBrains Mono', monospace",
        fontSize: 11,
      },
      grid: {
        vertLines: { color: "#1e1e24" },
        horzLines: { color: "#1e1e24" },
      },
      crosshair: {
        vertLine: {
          color: "#3d5afe55",
          width: 1,
          style: LineStyle.Dashed,
          labelBackgroundColor: "#3d5afe",
        },
        horzLine: {
          color: "#3d5afe55",
          width: 1,
          style: LineStyle.Dashed,
          labelBackgroundColor: "#3d5afe",
        },
      },
      rightPriceScale: {
        borderColor: "#2a2a33",
        scaleMargins: { top: 0.1, bottom: 0.1 },
      },
      timeScale: {
        borderColor: "#2a2a33",
        timeVisible: true,
        secondsVisible: false,
      },
      handleScroll: { vertTouchDrag: false },
      width: containerRef.current.clientWidth,
      height: 380,
    });

    const series = chart.addSeries(AreaSeries, {
      lineColor: "#00e676",
      lineWidth: 2,
      topColor: "rgba(0, 230, 118, 0.15)",
      bottomColor: "rgba(0, 230, 118, 0.0)",
      crosshairMarkerRadius: 5,
      crosshairMarkerBackgroundColor: "#00e676",
      crosshairMarkerBorderColor: "#000",
      crosshairMarkerBorderWidth: 2,
      priceFormat: {
        type: "custom",
        formatter: (price: number) => `${price.toFixed(1)}%`,
      },
    });

    chartRef.current = chart;
    seriesRef.current = series;

    const handleResize = () => {
      if (containerRef.current) {
        chart.applyOptions({ width: containerRef.current.clientWidth });
      }
    };
    const observer = new ResizeObserver(handleResize);
    observer.observe(containerRef.current);

    return () => {
      observer.disconnect();
      chart.remove();
      chartRef.current = null;
      seriesRef.current = null;
    };
  }, []);

  const isRealtime = minutes === 1;

  // Historical mode: fetch on mount + periodic refresh every 30s.
  useEffect(() => {
    if (isRealtime) return;
    let cancelled = false;

    async function loadHistory() {
      try {
        const records = await client.fetchHistory(tickerId, minutes);
        if (cancelled || !seriesRef.current) return;

        const data = records.map((r) => ({
          time: r.timestamp as any,
          value: priceToPercent(r.price),
        }));

        seriesRef.current.setData(data);
        chartRef.current?.timeScale().fitContent();
      } catch {
        // History not available yet
      }
    }

    loadHistory();
    const interval = setInterval(loadHistory, 30_000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, [tickerId, minutes, client, isRealtime]);

  // Realtime mode: rolling 60s window of live datagram prices.
  const realtimeBuffer = useRef<{ time: number; value: number }[]>([]);
  const baseTimeRef = useRef<number>(0);
  const baseSeqRef = useRef<number | null>(null);

  // Reset realtime buffer when switching to realtime or changing ticker.
  useEffect(() => {
    if (!isRealtime) return;
    realtimeBuffer.current = [];
    baseSeqRef.current = null;
    baseTimeRef.current = 0;
    if (seriesRef.current) {
      seriesRef.current.setData([]);
    }
  }, [tickerId, isRealtime]);

  useEffect(() => {
    if (!isRealtime || currentPrice === undefined || !seriesRef.current) return;

    // Derive a deterministic timestamp from seq so all tabs agree.
    // Anchor: first seq we see maps to Date.now(), then each subsequent
    // seq is +0.1s. This keeps the chart internally consistent.
    const latestSeq = getLatestSeq(tickerId);
    if (latestSeq === undefined) return;

    if (baseSeqRef.current === null) {
      baseSeqRef.current = latestSeq;
      baseTimeRef.current = Math.floor(Date.now() / 1000);
    }

    const seqDelta = ((latestSeq - baseSeqRef.current) & 0xffff);
    const time = baseTimeRef.current + seqDelta * 0.1;

    const buf = realtimeBuffer.current;
    // Only append if time is advancing.
    if (buf.length === 0 || time > buf[buf.length - 1].time) {
      buf.push({ time, value: priceToPercent(currentPrice) });
    }

    // Trim to 60s window.
    const cutoff = time - 60;
    while (buf.length > 0 && buf[0].time < cutoff) {
      buf.shift();
    }

    seriesRef.current.setData(buf.map((p) => ({ time: p.time as any, value: p.value })));
    chartRef.current?.timeScale().fitContent();
  }, [currentPrice, isRealtime, tickerId]);

  return <div ref={containerRef} className="w-full" />;
}
