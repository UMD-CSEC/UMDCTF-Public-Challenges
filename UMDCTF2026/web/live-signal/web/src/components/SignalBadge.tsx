"use client";

import { useState } from "react";
import { SIDE_LABEL, type Side } from "@/lib/signalFormat";

type Props = {
  ticker: string;
  side: Side | string;
  contractPrice?: number | null;
  publishedAt: string | Date;
};

export default function SignalBadge({ ticker, side, contractPrice, publishedAt }: Props) {
  const [hover, setHover] = useState(false);
  const when = typeof publishedAt === "string" ? new Date(publishedAt) : publishedAt;
  const s: Side = side === "YES" ? "YES" : "NO";
  const accent = s === "YES" ? "neon-lime" : "neon-magenta";
  const frame =
    s === "YES"
      ? "border-[color:var(--color-neon-lime)]/70"
      : "border-[color:var(--color-neon-magenta)]/70";

  return (
    <div
      className={`relative border-2 ${frame} bg-[color:var(--color-void-deep)] transition`}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
    >
      <div className="flex items-stretch">
        <div className={`flex w-16 items-center justify-center border-r-2 ${frame} bg-black/40 py-3 font-mono text-xs font-bold ${accent}`}>
          {SIDE_LABEL[s]}
        </div>
        <div className="flex-1 px-3 py-2">
          <div className="font-mono text-sm tracking-tight text-[color:var(--color-chalk)]">
            {ticker}
          </div>
          <div className="mt-0.5 flex items-center justify-between text-[11px] text-[color:var(--color-chalk-faint)] tabular">
            <span>{when.toLocaleDateString("en-US", { month: "short", day: "numeric" })}</span>
            {contractPrice != null && (
              <span className="font-mono">@ {contractPrice}¢</span>
            )}
          </div>
        </div>
      </div>
      {hover && (
        <div className="absolute left-0 top-full z-30 mt-1 whitespace-nowrap border border-[color:var(--color-neon-cyan)]/60 bg-[color:var(--color-void-deep)] px-3 py-1.5 font-mono text-[10px] text-[color:var(--color-chalk-dim)] shadow-[0_0_24px_rgba(34,225,255,0.25)]">
          <span className="neon-cyan">▸</span> {SIDE_LABEL[s]} · published{" "}
          {when.toLocaleString("en-US", { dateStyle: "short", timeStyle: "short" })}
        </div>
      )}
    </div>
  );
}
