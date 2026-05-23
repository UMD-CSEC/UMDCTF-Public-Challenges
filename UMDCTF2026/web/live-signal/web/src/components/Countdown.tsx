"use client";

import { useEffect, useState } from "react";

export default function Countdown({ targetIso }: { targetIso: string }) {
  const target = new Date(targetIso).getTime();
  const [now, setNow] = useState<number>(() => Date.now());

  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(id);
  }, []);

  const delta = Math.max(0, target - now);
  const d = Math.floor(delta / 86400_000);
  const h = Math.floor((delta / 3600_000) % 24);
  const m = Math.floor((delta / 60_000) % 60);
  const s = Math.floor((delta / 1000) % 60);
  const pad = (n: number, w = 2) => n.toString().padStart(w, "0");

  return (
    <div className="grid grid-cols-4 gap-2 font-mono tabular">
      <Cell label="DAYS" value={pad(d, 3)} color="neon-cyan" />
      <Cell label="HRS" value={pad(h)} color="neon-cyan" />
      <Cell label="MIN" value={pad(m)} color="neon-magenta" />
      <Cell label="SEC" value={pad(s)} color="neon-lime" />
    </div>
  );
}

function Cell({
  label,
  value,
  color,
}: {
  label: string;
  value: string;
  color: "neon-cyan" | "neon-magenta" | "neon-lime";
}) {
  return (
    <div className="relative border-2 border-[color:var(--color-chalk-faint)]/30 bg-[color:var(--color-void-deep)] p-3 text-center crt-surface">
      <div className={`display text-4xl md:text-5xl ${color}`}>{value}</div>
      <div className="mt-1 font-mono text-[9px] tracking-[0.3em] text-[color:var(--color-chalk-faint)]">
        {label}
      </div>
    </div>
  );
}
