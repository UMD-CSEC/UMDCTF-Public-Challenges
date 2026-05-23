import { notFound } from "next/navigation";
import { prisma } from "@/lib/db";
import { TIER_LABEL, asTier, formatRoi } from "@/lib/signalFormat";
import AnalystSignalsPanel from "./AnalystSignalsPanel";

export const dynamic = "force-dynamic";

export default async function AnalystProfile({
  params,
}: {
  params: Promise<{ handle: string }>;
}) {
  const { handle } = await params;
  const analyst = await prisma.analyst.findUnique({
    where: { handle },
    include: { _count: { select: { signals: true } } },
  });
  if (!analyst) notFound();

  const published = await prisma.signal.count({
    where: { analystId: analyst.id, publishedAt: { lte: new Date() } },
  });

  const tier = asTier(analyst.tier);
  const tierColor =
    tier === "DIAMOND"
      ? "var(--color-diamond)"
      : tier === "GOLD"
      ? "var(--color-gold)"
      : "var(--color-bronze)";
  const frame =
    tier === "DIAMOND" ? "cabinet" : tier === "GOLD" ? "cabinet-magenta" : "cabinet-lime";
  const glyph = tier === "DIAMOND" ? "◆" : tier === "GOLD" ? "★" : "▲";

  return (
    <div className="mx-auto max-w-7xl px-6 py-12">
      {/* CABINET HEADER */}
      <div className={`relative ${frame} crt-surface bg-[color:var(--color-void-deep)] p-8 md:p-12`}>
        <div
          className="pointer-events-none absolute inset-0 opacity-30"
          style={{
            background: `radial-gradient(circle at 15% 20%, ${tierColor}33, transparent 55%), radial-gradient(circle at 85% 80%, rgba(34,225,255,0.15), transparent 60%)`,
          }}
        />
        <div className="relative grid gap-8 md:grid-cols-[2fr_1fr]">
          <div>
            <div className="flex items-center gap-3 font-mono text-[10px] uppercase tracking-[0.3em]">
              <span style={{ color: tierColor }}>
                {glyph} {TIER_LABEL[tier]} TIER
              </span>
              <span className="text-[color:var(--color-chalk-faint)]">/</span>
              <span className="text-[color:var(--color-chalk-faint)]">
                joined{" "}
                {analyst.joinedAt.toLocaleDateString("en-US", {
                  month: "short",
                  year: "numeric",
                })}
              </span>
              <span className="text-[color:var(--color-chalk-faint)]">/</span>
              <span className="neon-magenta animate-blip">● BROADCASTING</span>
            </div>
            <h1 className="display mt-3 text-6xl md:text-7xl text-[color:var(--color-chalk)]">
              @{analyst.handle}
            </h1>
            <div className="mt-1 font-mono text-sm text-[color:var(--color-chalk-faint)]">
              aka {analyst.displayName}
            </div>
            <blockquote className="mt-7 border-l-4 border-[color:var(--color-neon-magenta)] pl-5 text-lg italic leading-relaxed text-[color:var(--color-chalk-dim)]">
              "{analyst.bio}"
            </blockquote>
          </div>
          <div className="flex flex-col justify-center gap-6 md:border-l md:border-[color:var(--color-chalk-faint)]/30 md:pl-8">
            <Stat label="Claimed ROI" value={formatRoi(analyst.claimedRoi)} big color="neon-lime" />
            <Stat label="Win rate" value={`${analyst.claimedWinRate.toString()}%`} color="neon-cyan" />
            <Stat label="Signals published" value={published.toLocaleString()} color="neon-magenta" />
          </div>
        </div>
      </div>

      {/* FILTERS + HISTORY */}
      <AnalystSignalsPanel handle={analyst.handle} />

      {/* CTA */}
      <div className="mt-12 border-2 border-[color:var(--color-neon-cyan)]/60 bg-[color:var(--color-plasma)]/40 p-8">
        <div className="flex flex-col items-start justify-between gap-6 md:flex-row md:items-center">
          <div>
            <div className="font-mono text-[10px] uppercase tracking-[0.3em] neon-cyan">
              // want @{analyst.handle}'s next call?
            </div>
            <div className="display mt-1 text-2xl md:text-3xl">
              subscribe to the desk. <span className="neon-lime">$500/mo.</span>
            </div>
            <div className="mt-1 font-mono text-xs text-[color:var(--color-chalk-faint)]">
              wire only · no refunds · DM for wire details · we prefer $USDC if you ask nicely
            </div>
          </div>
          <button
            disabled
            className="cursor-not-allowed border-2 border-[color:var(--color-neon-magenta)]/60 px-6 py-3 font-mono text-xs uppercase tracking-[0.3em] neon-magenta opacity-70"
          >
            ✦ waitlist full ✦
          </button>
        </div>
      </div>
    </div>
  );
}

function Stat({
  label,
  value,
  big,
  color,
}: {
  label: string;
  value: string;
  big?: boolean;
  color: "neon-lime" | "neon-cyan" | "neon-magenta";
}) {
  return (
    <div>
      <div className="font-mono text-[10px] uppercase tracking-[0.3em] text-[color:var(--color-chalk-faint)]">
        {label}
      </div>
      <div className={`display tabular leading-none mt-1 ${big ? "text-5xl md:text-6xl" : "text-2xl"} ${color}`}>
        {value}
      </div>
    </div>
  );
}
