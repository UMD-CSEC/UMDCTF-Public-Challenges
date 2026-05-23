"use client";

import { useState, useTransition } from "react";
import { verifyInsider } from "@/app/actions/insiders";

type Result =
  | { ok: true; message: string; flag: string }
  | { ok: false; message: string };

export default function InsiderForm() {
  const [ticker, setTicker] = useState("");
  const [side, setSide] = useState<"YES" | "NO">("YES");
  const [price, setPrice] = useState("");
  const [hmac, setHmac] = useState("");
  const [result, setResult] = useState<Result | null>(null);
  const [pending, startTransition] = useTransition();

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    const p = Number(price);
    startTransition(async () => {
      const r = await verifyInsider(
        ticker.trim().toUpperCase(),
        side,
        p,
        hmac.trim(),
      );
      setResult(r as Result);
    });
  }

  if (result?.ok) {
    return (
      <div className="py-4 text-center">
        <div className="font-mono text-[10px] tracking-[0.5em] uppercase neon-lime">
          ✓ welcome, insider
        </div>
        <div className="display mt-4 text-5xl neon-lime">ACCESS GRANTED</div>
        <div className="mt-4 font-mono text-sm text-[color:var(--color-chalk-dim)]">
          {result.message}
        </div>
        <div className="mt-8 cabinet-lime bg-[color:var(--color-void-deep)] p-6">
          <div className="font-mono text-[10px] uppercase tracking-[0.3em] neon-lime">
            ▸ flag packet
          </div>
          <div className="mt-3 select-all break-all font-mono text-lg md:text-xl text-[color:var(--color-chalk)]">
            {result.flag}
          </div>
        </div>
        <button
          onClick={() => {
            setResult(null);
            setTicker("");
            setPrice("");
            setHmac("");
          }}
          className="mt-8 font-mono text-xs uppercase tracking-[0.3em] text-[color:var(--color-chalk-faint)] hover:neon-cyan"
        >
          ← reset terminal
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={onSubmit} className="grid gap-5">
      <label className="grid gap-2">
        <span className="font-mono text-[10px] uppercase tracking-[0.3em] text-[color:var(--color-chalk-faint)]">
          ▸ contract ticker
        </span>
        <input
          type="text"
          required
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
          placeholder="KX…"
          className="border-2 border-[color:var(--color-chalk-faint)]/50 bg-[color:var(--color-void-deep)] px-4 py-3 font-mono text-lg tracking-widest text-[color:var(--color-chalk)] outline-none focus:border-[color:var(--color-neon-cyan)]"
        />
      </label>

      <div className="grid gap-2">
        <span className="font-mono text-[10px] uppercase tracking-[0.3em] text-[color:var(--color-chalk-faint)]">
          ▸ side
        </span>
        <div className="grid grid-cols-2 gap-3">
          {(["YES", "NO"] as const).map((opt) => (
            <button
              type="button"
              key={opt}
              onClick={() => setSide(opt)}
              className={`border-2 px-4 py-3 font-mono font-bold tracking-widest transition ${
                side === opt
                  ? opt === "YES"
                    ? "border-[color:var(--color-neon-lime)] bg-[color:var(--color-neon-lime)]/15 neon-lime"
                    : "border-[color:var(--color-neon-magenta)] bg-[color:var(--color-neon-magenta)]/15 neon-magenta"
                  : "border-[color:var(--color-chalk-faint)]/40 text-[color:var(--color-chalk-faint)] hover:border-[color:var(--color-chalk-faint)]"
              }`}
            >
              {opt}
            </button>
          ))}
        </div>
      </div>

      <label className="grid gap-2">
        <span className="font-mono text-[10px] uppercase tracking-[0.3em] text-[color:var(--color-chalk-faint)]">
          ▸ contract price · cents
        </span>
        <input
          type="number"
          required
          min={1}
          max={99}
          step={1}
          value={price}
          onChange={(e) => setPrice(e.target.value)}
          placeholder="1–99"
          className="border-2 border-[color:var(--color-chalk-faint)]/50 bg-[color:var(--color-void-deep)] px-4 py-3 font-mono text-lg tabular text-[color:var(--color-chalk)] outline-none focus:border-[color:var(--color-neon-cyan)]"
        />
      </label>

      <label className="grid gap-2">
        <span className="font-mono text-[10px] uppercase tracking-[0.3em] text-[color:var(--color-chalk-faint)]">
          ▸ signal hmac · 32 hex
        </span>
        <input
          type="text"
          required
          value={hmac}
          onChange={(e) => setHmac(e.target.value)}
          placeholder="desk-issued signal authenticity tag"
          className="border-2 border-[color:var(--color-chalk-faint)]/50 bg-[color:var(--color-void-deep)] px-4 py-3 font-mono text-sm tracking-widest text-[color:var(--color-chalk)] outline-none focus:border-[color:var(--color-neon-cyan)]"
        />
      </label>

      <button
        type="submit"
        disabled={pending}
        className="mt-2 bg-[color:var(--color-neon-magenta)] px-6 py-3 font-mono font-bold uppercase tracking-[0.25em] text-[color:var(--color-void-deep)] transition hover:bg-[color:var(--color-chalk)] disabled:opacity-50"
      >
        {pending ? "verifying…" : "▸ submit credentials"}
      </button>

      {result && !result.ok && (
        <div className="border-2 border-[color:var(--color-neon-magenta)] bg-[color:var(--color-neon-magenta)]/10 p-5 text-center crt-surface">
          <div className="font-mono text-[10px] tracking-[0.5em] uppercase animate-blip neon-magenta">
            ✗ access denied
          </div>
          <div className="display mt-2 text-3xl neon-magenta">REJECTED</div>
          <div className="mt-2 font-mono text-xs text-[color:var(--color-chalk-dim)]">
            {result.message}
          </div>
        </div>
      )}
    </form>
  );
}
