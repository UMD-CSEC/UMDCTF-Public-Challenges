import Link from "next/link";
import { prisma } from "@/lib/db";
import { TIER_LABEL, asTier, formatRoi } from "@/lib/signalFormat";

export const dynamic = "force-dynamic";

export default async function AnalystsPage() {
  const analysts = await prisma.analyst.findMany({
    orderBy: [{ tier: "desc" }, { claimedRoi: "desc" }],
    include: { _count: { select: { signals: true } } },
  });

  return (
    <div className="mx-auto max-w-7xl px-6 py-14">
      <div className="flex flex-col gap-4 border-b border-[color:var(--color-chalk-faint)]/30 pb-6 md:flex-row md:items-end md:justify-between">
        <div>
          <div className="font-mono text-[11px] uppercase tracking-[0.3em] text-[color:var(--color-chalk-faint)]">
            // desk directory · all operators
          </div>
          <h1 className="display mt-2 text-6xl">
            the <span className="neon-magenta">analysts</span>.
          </h1>
          <p className="mt-4 max-w-xl text-[15px] leading-relaxed text-[color:var(--color-chalk-dim)]">
            Eight operators. Allegedly the sharpest minds on any prediction
            market. Each one self-verified. Each one accepting new subscribers
            (with references). Most will ghost you if you ask about drawdowns.
          </p>
        </div>
        <div className="hidden text-right font-mono text-[10px] uppercase tracking-widest text-[color:var(--color-chalk-faint)] md:block">
          sorted by tier × <span className="neon-lime">claimed ROI</span>
          <div className="mt-1">(self-reported, not audited)</div>
        </div>
      </div>

      <div className="mt-10 grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        {analysts.map((a, i) => {
          const tier = asTier(a.tier);
          const frame =
            tier === "DIAMOND"
              ? "cabinet"
              : tier === "GOLD"
              ? "border-2 border-[color:var(--color-gold)]/70"
              : "border-2 border-[color:var(--color-bronze)]/60";
          const accent =
            tier === "DIAMOND"
              ? "text-[color:var(--color-diamond)]"
              : tier === "GOLD"
              ? "text-[color:var(--color-gold)]"
              : "text-[color:var(--color-bronze)]";
          const glyph = tier === "DIAMOND" ? "◆" : tier === "GOLD" ? "★" : "▲";
          return (
            <Link
              key={a.id}
              href={`/analyst/${a.handle}`}
              className={`group relative ${frame} crt-surface bg-[color:var(--color-void-deep)]/70 p-6 transition hover:bg-[color:var(--color-plasma)]/50`}
            >
              <div className="absolute right-3 top-3 flex items-center gap-2 font-mono text-[10px] uppercase tracking-[0.25em]">
                <span className={accent}>{glyph}</span>
                <span className={accent}>{TIER_LABEL[tier]}</span>
              </div>

              <div className="font-mono text-[10px] text-[color:var(--color-chalk-faint)]">
                operator {String(i + 1).padStart(2, "0")} / 08
              </div>
              <div className="display mt-2 text-3xl text-[color:var(--color-chalk)] group-hover:neon-cyan">
                @{a.handle}
              </div>
              <div className="font-mono text-xs text-[color:var(--color-chalk-faint)]">
                aka {a.displayName}
              </div>

              <div className="mt-6 flex items-end justify-between">
                <div>
                  <div className="font-mono text-[9px] uppercase tracking-[0.3em] text-[color:var(--color-chalk-faint)]">
                    claimed ROI
                  </div>
                  <div className="display text-4xl neon-lime tabular leading-none">
                    {formatRoi(a.claimedRoi)}
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-mono text-[9px] uppercase tracking-[0.3em] text-[color:var(--color-chalk-faint)]">
                    win rate
                  </div>
                  <div className="font-mono text-xl neon-cyan tabular">
                    {a.claimedWinRate.toString()}%
                  </div>
                </div>
              </div>

              <p className="mt-5 line-clamp-3 text-sm italic text-[color:var(--color-chalk-dim)]">
                "{a.bio}"
              </p>

              <div className="mt-5 flex items-center justify-between border-t border-[color:var(--color-chalk-faint)]/20 pt-3 font-mono text-[10px] uppercase tracking-widest">
                <span className="text-[color:var(--color-chalk-faint)]">
                  {a._count.signals} signals on tape
                </span>
                <span className="neon-cyan opacity-0 transition group-hover:opacity-100">
                  open profile ▶
                </span>
              </div>
            </Link>
          );
        })}
      </div>

      <div className="mt-16 border-2 border-dashed border-[color:var(--color-chalk-faint)]/40 bg-[color:var(--color-void-deep)]/50 p-10 text-center">
        <div className="font-mono text-[10px] uppercase tracking-[0.3em] neon-magenta">
          ✦ applications open ✦
        </div>
        <div className="display mt-2 text-3xl">verified analyst program</div>
        <p className="mx-auto mt-3 max-w-xl text-sm text-[color:var(--color-chalk-dim)]">
          Submit a 90-day track record and a{" "}
          <span className="neon-lime">non-refundable $2,000 processing fee</span>{" "}
          to the desk. Most applicants are rejected. Most accepted applicants
          are rejected again. We reserve the right to audit you, your cousin,
          and your discord.
        </p>
      </div>
    </div>
  );
}
