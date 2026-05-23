import Link from "next/link";
import { prisma } from "@/lib/db";
import { SIDE_LABEL, TIER_LABEL, asSide, asTier, formatRoi } from "@/lib/signalFormat";
import Countdown from "@/components/Countdown";
import SignalBadge from "@/components/SignalBadge";

export const dynamic = "force-dynamic";

export default async function Home() {
  const [draft, leaderboard, recent, totalSignals] = await Promise.all([
    prisma.signal.findFirst({
      where: { analyst: { handle: "quant_sable" }, publishedAt: { gt: new Date() } },
      orderBy: { publishedAt: "asc" },
    }),
    prisma.analyst.findMany({
      orderBy: { claimedRoi: "desc" },
      take: 5,
    }),
    prisma.signal.findMany({
      where: { publishedAt: { lte: new Date() } },
      orderBy: { publishedAt: "desc" },
      take: 9,
      include: { analyst: true },
    }),
    prisma.signal.count({ where: { publishedAt: { lte: new Date() } } }),
  ]);

  const top = leaderboard[0];

  return (
    <div>
      {/* HERO */}
      <section className="relative mx-auto max-w-7xl px-6 pt-14 pb-16">
        <div className="font-mono text-[11px] uppercase tracking-[0.4em] text-[color:var(--color-chalk-faint)]">
          <span className="neon-magenta">●</span> LIVE &nbsp;/&nbsp; SEASON{" "}
          <span className="neon-cyan">XVII</span> &nbsp;/&nbsp; SIGNAL BROADCAST
        </div>

        <div className="mt-6 grid items-end gap-10 lg:grid-cols-12">
          <div className="lg:col-span-7">
            <h1 className="display text-[clamp(3rem,7vw,6rem)] text-[color:var(--color-chalk)]">
              <span className="block">out-trade</span>
              <span className="block neon-magenta">the crowd.</span>
              <span className="block text-[color:var(--color-chalk-faint)]">
                out-earn your friends.
              </span>
            </h1>
            <p className="mt-6 max-w-xl text-[17px] leading-relaxed text-[color:var(--color-chalk-dim)]">
              <span className="neon-cyan">LiveSignal</span> is the paid
              prediction-market desk. Our analysts publish timed YES/NO calls
              before the herd notices. You subscribe, you stack, you rotate
              before CNBC gets the memo.
            </p>
            <p className="mt-3 font-mono text-xs text-[color:var(--color-chalk-faint)]">
              $500/mo · wires only · no refunds · zelle is for civilians
            </p>

            <div className="mt-8 flex flex-wrap items-center gap-4">
              <Link
                href="/analysts"
                className="group inline-flex items-center gap-3 bg-[color:var(--color-neon-cyan)] px-6 py-3 font-mono text-xs font-bold uppercase tracking-[0.2em] text-[color:var(--color-void-deep)] transition hover:bg-[color:var(--color-chalk)]"
              >
                Browse analysts
                <span className="transition group-hover:translate-x-1">▶</span>
              </Link>
              <Link
                href="/insiders"
                className="inline-flex items-center gap-2 border-2 border-[color:var(--color-neon-magenta)] px-6 py-3 font-mono text-xs uppercase tracking-[0.2em] neon-magenta hover:bg-[color:var(--color-neon-magenta)]/15"
              >
                ▌ insiders portal
              </Link>
              <span className="font-mono text-[11px] text-[color:var(--color-chalk-faint)]">
                <span className="neon-lime">{totalSignals.toLocaleString()}</span>{" "}
                signals shipped ·{" "}
                <span className="neon-magenta">0</span> refunds issued
              </span>
            </div>
          </div>

          <div className="lg:col-span-5">
            <div className="cabinet-magenta crt-surface bg-[color:var(--color-plasma)] p-6">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-mono text-[10px] uppercase tracking-[0.3em] neon-magenta">
                    ▌ next drop
                  </div>
                  <Link
                    href="/analyst/quant_sable"
                    className="mt-1 block font-mono text-sm text-[color:var(--color-diamond)] hover:underline"
                  >
                    @quant_sable / DIAMOND TIER ◆
                  </Link>
                </div>
                <div className="text-right font-mono text-[10px] text-[color:var(--color-chalk-faint)] uppercase tracking-widest">
                  embargo lifts in
                </div>
              </div>

              {draft ? (
                <div className="mt-5">
                  <Countdown targetIso={draft.publishedAt.toISOString()} />
                </div>
              ) : (
                <div className="mt-5 text-center font-mono text-sm text-[color:var(--color-chalk-faint)]">
                  no pending drop.
                </div>
              )}

              <p className="mt-5 border-t border-[color:var(--color-chalk-faint)]/20 pt-3 font-mono text-[10px] leading-relaxed text-[color:var(--color-chalk-dim)]">
                [ EMBARGOED ] Subscribers receive the ticker, side, and entry
                price at drop. No previews. No screenshots. No exceptions.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* LEADERBOARD */}
      <section className="mx-auto max-w-7xl px-6 py-12">
        <SectionHeader
          kicker="// desk rankings · YTD"
          title="The Leaderboard"
          aside={
            <Link href="/analysts" className="font-mono text-xs uppercase tracking-widest neon-cyan hover:underline">
              view all 8 →
            </Link>
          }
        />

        {top && (
          <div className="mt-8 cabinet crt-surface bg-gradient-to-br from-[color:var(--color-plasma)] to-[color:var(--color-void)] p-8">
            <div className="grid items-center gap-8 md:grid-cols-[1fr_auto]">
              <div>
                <div className="font-mono text-[10px] uppercase tracking-[0.3em] neon-cyan">
                  ▲▲▲ #1 desk · {TIER_LABEL[asTier(top.tier)]} tier
                </div>
                <Link
                  href={`/analyst/${top.handle}`}
                  className="mt-2 block display text-5xl md:text-6xl text-[color:var(--color-chalk)] hover:text-[color:var(--color-neon-cyan)]"
                >
                  @{top.handle}
                </Link>
                <p className="mt-4 max-w-xl text-sm leading-relaxed text-[color:var(--color-chalk-dim)] line-clamp-2 italic">
                  "{top.bio}"
                </p>
              </div>
              <div className="relative text-right">
                <div className="font-mono text-[10px] uppercase tracking-[0.3em] text-[color:var(--color-chalk-faint)]">
                  claimed ROI
                </div>
                <div className="display text-7xl md:text-8xl neon-lime tabular leading-none">
                  {formatRoi(top.claimedRoi)}
                </div>
                <div className="mt-2 font-mono text-sm text-[color:var(--color-chalk-dim)]">
                  win rate{" "}
                  <span className="neon-cyan tabular">{top.claimedWinRate.toString()}%</span>
                </div>
                <span className="absolute -top-3 right-0 stamp neon-magenta bg-[color:var(--color-void-deep)]">
                  ★ alpha chad
                </span>
              </div>
            </div>
          </div>
        )}

        <div className="mt-4 grid gap-2">
          {leaderboard.slice(1).map((a, i) => {
            const tier = asTier(a.tier);
            return (
              <Link
                key={a.id}
                href={`/analyst/${a.handle}`}
                className="group grid grid-cols-[3.5rem_1fr_6rem_10rem] items-center gap-5 border border-[color:var(--color-chalk-faint)]/30 px-5 py-3 transition hover:border-[color:var(--color-neon-cyan)] hover:bg-[color:var(--color-plasma)]/40"
              >
                <span className="font-mono text-2xl text-[color:var(--color-chalk-faint)] tabular">
                  {String(i + 2).padStart(2, "0")}
                </span>
                <div className="min-w-0">
                  <div className="font-mono text-[color:var(--color-chalk)] group-hover:neon-cyan">
                    @{a.handle}
                  </div>
                  <div className="truncate text-xs text-[color:var(--color-chalk-faint)]">
                    {a.bio}
                  </div>
                </div>
                <div className={`font-mono text-[10px] font-bold uppercase tracking-[0.2em] ${tierAccent(tier)}`}>
                  {TIER_LABEL[tier]}
                </div>
                <div className="text-right font-mono text-2xl neon-lime tabular">
                  {formatRoi(a.claimedRoi)}
                </div>
              </Link>
            );
          })}
        </div>
      </section>

      {/* RECENT SIGNALS */}
      <section className="mx-auto max-w-7xl px-6 py-12">
        <SectionHeader
          kicker="// tape · most recent"
          title="Public Signals"
          aside={
            <span className="font-mono text-[11px] text-[color:var(--color-chalk-faint)]">
              showing {recent.length} of{" "}
              <span className="neon-cyan">{totalSignals}</span>
            </span>
          }
        />

        <div className="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {recent.map((s) => {
            const tier = asTier(s.analyst.tier);
            return (
              <div key={s.id} className="border border-[color:var(--color-chalk-faint)]/30 bg-[color:var(--color-void-deep)]/60 p-4">
                <div className="mb-3 flex items-center justify-between">
                  <Link
                    href={`/analyst/${s.analyst.handle}`}
                    className={`font-mono text-sm hover:underline ${tierAccent(tier)}`}
                  >
                    @{s.analyst.handle}
                  </Link>
                  <span className="font-mono text-[9px] uppercase tracking-[0.25em] text-[color:var(--color-chalk-faint)]">
                    {TIER_LABEL[tier]}
                  </span>
                </div>
                <SignalBadge
                  ticker={s.ticker}
                  side={s.side}
                  contractPrice={s.contractPrice}
                  publishedAt={s.publishedAt}
                />
                <div className="mt-3 font-mono text-[10px] text-[color:var(--color-chalk-faint)]">
                  broadcast {new Date(s.publishedAt).toLocaleDateString()} · side {SIDE_LABEL[asSide(s.side)]}
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* CTA — group chat tease */}
      <section className="mx-auto max-w-7xl px-6 py-16">
        <div className="cabinet-lime relative crt-surface bg-[color:var(--color-void-deep)] p-12 text-center">
          <div className="font-mono text-[11px] uppercase tracking-[0.4em] neon-lime">
            // subscribers-only broadcast
          </div>
          <h2 className="display mt-3 text-4xl md:text-5xl">
            the real alpha lives in{" "}
            <span className="neon-lime">the group chat.</span>
          </h2>
          <p className="mt-4 font-mono text-sm text-[color:var(--color-chalk-dim)]">
            Invite-only Telegram:{" "}
            <span className="neon-cyan">t.me/livesignal_vip_q7rT3mxZ9bnLK4</span> · referral required ·
            don't screenshot
          </p>
        </div>
      </section>
    </div>
  );
}

function SectionHeader({
  kicker,
  title,
  aside,
}: {
  kicker: string;
  title: string;
  aside?: React.ReactNode;
}) {
  return (
    <div className="flex items-end justify-between border-b border-[color:var(--color-chalk-faint)]/30 pb-3">
      <div>
        <div className="font-mono text-[11px] uppercase tracking-[0.3em] text-[color:var(--color-chalk-faint)]">
          {kicker}
        </div>
        <h2 className="display mt-1 text-3xl">{title}</h2>
      </div>
      {aside}
    </div>
  );
}

function tierAccent(tier: "BRONZE" | "GOLD" | "DIAMOND") {
  if (tier === "DIAMOND") return "text-[color:var(--color-diamond)]";
  if (tier === "GOLD") return "text-[color:var(--color-gold)]";
  return "text-[color:var(--color-bronze)]";
}
