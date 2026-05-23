"use client";

import { useEffect, useState, useTransition } from "react";
import { signalsByAnalyst, type SignalRow } from "@/app/actions/signals";
import { SIDE_LABEL, type Side } from "@/lib/signalFormat";

export default function AnalystSignalsPanel({ handle: initialHandle }: { handle: string }) {
  const [handle, setHandle] = useState(initialHandle);
  const [tier, setTier] = useState<"" | "BRONZE" | "GOLD" | "DIAMOND">("");
  const [rows, setRows] = useState<SignalRow[] | null>(null);
  const [pending, startTransition] = useTransition();

  useEffect(() => {
    load(initialHandle, "");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialHandle]);

  function load(h: string, t: "" | "BRONZE" | "GOLD" | "DIAMOND") {
    const author: Record<string, string> = {};
    if (h) author.handle = h;
    if (t) author.tier = t;
    startTransition(async () => {
      try {
        setRows(await signalsByAnalyst(author as never, 25));
      } catch {
        setRows([]);
      }
    });
  }

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    load(handle, tier);
  }

  const displayed = rows ?? [];

  return (
    <div className="mt-12">
      <div className="flex items-end justify-between border-b border-[color:var(--color-chalk-faint)]/30 pb-3">
        <div>
          <div className="font-mono text-[10px] uppercase tracking-[0.3em] text-[color:var(--color-chalk-faint)]">
            // track record · public tape
          </div>
          <h2 className="display mt-1 text-3xl">signal history</h2>
        </div>
        <div className="font-mono text-[10px] text-[color:var(--color-chalk-faint)] uppercase tracking-widest">
          server // signalsByAnalyst()
        </div>
      </div>

      <form
        onSubmit={onSubmit}
        className="mt-5 grid gap-3 border border-[color:var(--color-neon-cyan)]/40 bg-[color:var(--color-void-deep)]/60 p-4 md:grid-cols-[1fr_auto_auto]"
      >
        <label className="flex items-center gap-3">
          <span className="font-mono text-[10px] uppercase tracking-widest text-[color:var(--color-chalk-faint)]">
            handle
          </span>
          <input
            type="text"
            value={handle}
            onChange={(e) => setHandle(e.target.value)}
            placeholder="quant_sable"
            className="flex-1 border-b border-[color:var(--color-chalk-faint)]/50 bg-transparent py-1 font-mono text-sm text-[color:var(--color-chalk)] outline-none focus:border-[color:var(--color-neon-cyan)]"
          />
        </label>
        <label className="flex items-center gap-3">
          <span className="font-mono text-[10px] uppercase tracking-widest text-[color:var(--color-chalk-faint)]">
            tier
          </span>
          <select
            value={tier}
            onChange={(e) =>
              setTier(e.target.value as "" | "BRONZE" | "GOLD" | "DIAMOND")
            }
            className="border border-[color:var(--color-chalk-faint)]/50 bg-[color:var(--color-void-deep)] px-2 py-1 font-mono text-sm text-[color:var(--color-chalk)] outline-none focus:border-[color:var(--color-neon-cyan)]"
          >
            <option value="">ANY</option>
            <option value="BRONZE">BRONZE</option>
            <option value="GOLD">GOLD</option>
            <option value="DIAMOND">DIAMOND</option>
          </select>
        </label>
        <button
          type="submit"
          disabled={pending}
          className="bg-[color:var(--color-neon-cyan)] px-5 py-2 font-mono text-xs font-bold uppercase tracking-[0.25em] text-[color:var(--color-void-deep)] disabled:opacity-50"
        >
          {pending ? "querying…" : "apply"}
        </button>
      </form>

      <div className="mt-6 overflow-x-auto border border-[color:var(--color-chalk-faint)]/30">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-[color:var(--color-chalk-faint)]/30 text-left font-mono text-[10px] uppercase tracking-[0.25em] text-[color:var(--color-chalk-faint)]">
              <th className="px-5 py-3">Ticker</th>
              <th className="px-5 py-3">Side</th>
              <th className="px-5 py-3">Entry</th>
              <th className="px-5 py-3">HMAC</th>
              <th className="px-5 py-3 text-right">Published</th>
            </tr>
          </thead>
          <tbody className="font-mono">
            {displayed.length === 0 && !pending && (
              <tr>
                <td colSpan={5} className="px-5 py-12 text-center text-[color:var(--color-chalk-faint)]">
                  no signals match the filter.
                </td>
              </tr>
            )}
            {displayed.map((r) => {
              const s: Side = r.side === "YES" ? "YES" : "NO";
              const sideColor = s === "YES" ? "neon-lime" : "neon-magenta";
              return (
                <tr
                  key={r.id}
                  className="border-b border-[color:var(--color-chalk-faint)]/15 transition hover:bg-[color:var(--color-plasma)]/40"
                >
                  <td className="px-5 py-3 text-[color:var(--color-chalk)]">{r.ticker}</td>
                  <td className={`px-5 py-3 font-bold ${sideColor}`}>
                    {SIDE_LABEL[s]}
                  </td>
                  <td className="px-5 py-3 tabular text-[color:var(--color-chalk-dim)]">
                    {r.contractPrice}¢
                  </td>
                  <td className="px-5 py-3 text-[11px] tabular text-[color:var(--color-chalk-faint)]">
                    {r.signalHmac}
                  </td>
                  <td className="px-5 py-3 text-right tabular text-[color:var(--color-chalk-faint)]">
                    {new Date(r.publishedAt).toLocaleDateString("en-US", {
                      month: "short",
                      day: "numeric",
                      year: "numeric",
                    })}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
