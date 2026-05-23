import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useApp } from "../lib/store.tsx";
import {
  balanceToDollars,
  priceToPercent,
  PRICE_UNIT,
} from "../lib/protocol.ts";

export function PortfolioPage() {
  const { balance, portfolio, refreshPortfolio, tickers, prices, client } =
    useApp();
  const [flag, setFlag] = useState<string | null>(null);
  const [flagLoading, setFlagLoading] = useState(false);
  const [flagError, setFlagError] = useState<string | null>(null);

  useEffect(() => {
    refreshPortfolio().catch(() => {});
  }, [refreshPortfolio]);

  const flagPrice = 10_000_000;
  const canBuyFlag = balance >= BigInt(flagPrice);

  const handleBuyFlag = async () => {
    setFlagLoading(true);
    setFlagError(null);
    try {
      const f = await client.buyFlag();
      setFlag(f);
      await refreshPortfolio();
    } catch (err: any) {
      setFlagError(err.message);
    } finally {
      setFlagLoading(false);
    }
  };

  // Compute total portfolio value
  let totalValue = Number(balance);
  const positionRows: {
    tickerId: number;
    name: string;
    description: string;
    yesQty: number;
    noQty: number;
    yesPrice: number | undefined;
    yesValue: number;
    noValue: number;
  }[] = [];

  if (portfolio) {
    for (const pos of portfolio.positions) {
      if (pos.yesQty === 0 && pos.noQty === 0) continue;
      const ticker = tickers.find((t) => t.id === pos.tickerId);
      const yesPrice = prices.get(pos.tickerId);
      const yesValue =
        yesPrice !== undefined ? pos.yesQty * yesPrice : 0;
      const noValue =
        yesPrice !== undefined
          ? pos.noQty * (PRICE_UNIT - yesPrice)
          : 0;
      totalValue += yesValue + noValue;
      positionRows.push({
        tickerId: pos.tickerId,
        name: ticker?.name || `#${pos.tickerId}`,
        description: ticker?.description || "",
        yesQty: pos.yesQty,
        noQty: pos.noQty,
        yesPrice,
        yesValue,
        noValue,
      });
    }
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-10 animate-fade-in">
        <h1 className="text-3xl font-bold text-white tracking-tight mb-2">
          Portfolio
        </h1>
        <p className="text-muted text-sm">
          Your balance, positions, and estimated value.
        </p>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-10">
        <div className="bg-surface-2 border border-border rounded-2xl p-6 animate-slide-up stagger-1">
          <div className="text-xs text-muted uppercase tracking-wider font-medium mb-2">
            Cash Balance
          </div>
          <div className="text-3xl font-mono font-bold text-yes">
            ${balanceToDollars(balance)}
          </div>
        </div>
        <div className="bg-surface-2 border border-border rounded-2xl p-6 animate-slide-up stagger-2">
          <div className="text-xs text-muted uppercase tracking-wider font-medium mb-2">
            Position Value
          </div>
          <div className="text-3xl font-mono font-bold text-white">
            ${balanceToDollars(totalValue - Number(balance))}
          </div>
        </div>
        <div className="bg-surface-2 border border-border rounded-2xl p-6 animate-slide-up stagger-3">
          <div className="text-xs text-muted uppercase tracking-wider font-medium mb-2">
            Total Value
          </div>
          <div className="text-3xl font-mono font-bold text-primary">
            ${balanceToDollars(totalValue)}
          </div>
        </div>
      </div>

      {/* Flag section */}
      {flag ? (
        <div className="mb-10 p-6 bg-yes-dim border border-yes/20 rounded-2xl animate-slide-up">
          <div className="text-xs text-yes/70 uppercase tracking-wider font-medium mb-2">
            Flag Captured
          </div>
          <code className="text-lg font-mono font-bold text-yes break-all">
            {flag}
          </code>
        </div>
      ) : canBuyFlag ? (
        <div className="mb-10 p-6 bg-primary-dim border border-primary/20 rounded-2xl animate-slide-up">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-white mb-1">
                You can afford the flag!
              </h3>
              <p className="text-sm text-text-dim">
                Cost:{" "}
                <span className="font-mono font-bold text-white">
                  $1,000.00
                </span>
              </p>
            </div>
            <button
              onClick={handleBuyFlag}
              disabled={flagLoading}
              className="px-6 py-3 bg-primary hover:bg-primary-hover text-white font-bold rounded-xl transition-all shadow-lg shadow-primary/30 active:scale-95 disabled:opacity-50"
            >
              {flagLoading ? "Buying..." : "Buy Flag · $1,000"}
            </button>
          </div>
          {flagError && (
            <div className="mt-3 text-no text-sm font-medium">{flagError}</div>
          )}
        </div>
      ) : (
        <div className="mb-10 p-5 bg-surface-2 border border-border rounded-2xl animate-fade-in">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-muted mb-1">Flag Price</div>
              <div className="text-lg font-mono font-bold text-white">
                $1,000.00
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm text-muted mb-1">You need</div>
              <div className="text-lg font-mono font-bold text-no">
                ${balanceToDollars(flagPrice - Number(balance))} more
              </div>
            </div>
          </div>
          {/* Progress bar */}
          <div className="mt-4 h-2 bg-surface rounded-full overflow-hidden">
            <div
              className="h-full bg-primary/60 rounded-full transition-all duration-700"
              style={{
                width: `${Math.min(100, (Number(balance) / flagPrice) * 100)}%`,
              }}
            />
          </div>
          <div className="mt-1.5 text-xs text-muted text-right font-mono">
            {((Number(balance) / flagPrice) * 100).toFixed(2)}%
          </div>
        </div>
      )}

      {/* Positions table */}
      <div className="animate-slide-up stagger-4">
        <h2 className="text-sm font-semibold text-muted uppercase tracking-wider mb-4">
          Open Positions
        </h2>

        {positionRows.length === 0 ? (
          <div className="bg-surface-2 border border-border rounded-2xl p-10 text-center">
            <div className="text-muted text-sm mb-3">No open positions</div>
            <Link
              to="/"
              className="text-sm text-primary hover:text-primary-hover font-medium transition-colors"
            >
              Browse markets to start trading
            </Link>
          </div>
        ) : (
          <div className="bg-surface-2 border border-border rounded-2xl overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left text-xs text-muted uppercase tracking-wider font-medium px-5 py-3">
                    Market
                  </th>
                  <th className="text-right text-xs text-muted uppercase tracking-wider font-medium px-5 py-3">
                    Price
                  </th>
                  <th className="text-right text-xs text-muted uppercase tracking-wider font-medium px-5 py-3">
                    Yes
                  </th>
                  <th className="text-right text-xs text-muted uppercase tracking-wider font-medium px-5 py-3">
                    No
                  </th>
                  <th className="text-right text-xs text-muted uppercase tracking-wider font-medium px-5 py-3">
                    Value
                  </th>
                  <th className="px-5 py-3" />
                </tr>
              </thead>
              <tbody>
                {positionRows.map((row) => (
                  <tr
                    key={row.tickerId}
                    className="border-b border-border/50 last:border-0 hover:bg-surface-3/30 transition-colors"
                  >
                    <td className="px-5 py-4">
                      <div className="text-sm font-semibold text-white">
                        {row.name}
                      </div>
                      <div className="text-xs text-muted truncate max-w-[250px]">
                        {row.description}
                      </div>
                    </td>
                    <td className="text-right px-5 py-4">
                      <span className="text-sm font-mono text-text-dim">
                        {row.yesPrice !== undefined
                          ? `${priceToPercent(row.yesPrice).toFixed(1)}¢`
                          : "-"}
                      </span>
                    </td>
                    <td className="text-right px-5 py-4">
                      {row.yesQty > 0 ? (
                        <span className="text-sm font-mono font-semibold text-yes">
                          {row.yesQty}
                        </span>
                      ) : (
                        <span className="text-sm text-muted/40">-</span>
                      )}
                    </td>
                    <td className="text-right px-5 py-4">
                      {row.noQty > 0 ? (
                        <span className="text-sm font-mono font-semibold text-no">
                          {row.noQty}
                        </span>
                      ) : (
                        <span className="text-sm text-muted/40">-</span>
                      )}
                    </td>
                    <td className="text-right px-5 py-4">
                      <span className="text-sm font-mono font-semibold text-white">
                        ${balanceToDollars(row.yesValue + row.noValue)}
                      </span>
                    </td>
                    <td className="px-5 py-4">
                      <Link
                        to={`/market/${row.tickerId}`}
                        className="text-xs text-primary hover:text-primary-hover font-medium transition-colors"
                      >
                        Trade
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
