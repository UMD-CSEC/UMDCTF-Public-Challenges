import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "LiveSignal — Prediction Arcade",
  description:
    "Paid prediction-market signals from the sharpest analysts online. $500/mo. Wires only. Subscribers only.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen antialiased">
        <div className="pointer-events-none fixed inset-0 z-0 pixel-grid opacity-40" />
        <div className="relative z-10">
          <TickerStrip />
          <Nav />
          <main>{children}</main>
          <Footer />
        </div>
      </body>
    </html>
  );
}

function TickerStrip() {
  return (
    <div className="relative overflow-hidden border-b-2 border-[color:var(--color-neon-magenta)] bg-[color:var(--color-void-deep)]">
      <div className="absolute inset-y-0 left-0 z-10 w-20 bg-gradient-to-r from-[color:var(--color-void-deep)] to-transparent pointer-events-none" />
      <div className="absolute inset-y-0 right-0 z-10 w-20 bg-gradient-to-l from-[color:var(--color-void-deep)] to-transparent pointer-events-none" />
      <div className="py-1.5 font-mono text-[11px] tracking-widest text-[color:var(--color-chalk-dim)]">
        <span className="marquee">
          ◉ KXBTC200K-26DEC <span className="neon-lime">37¢</span>
          &nbsp;&nbsp; ◉ KXFEDCUT-26JUL <span className="neon-lime">62¢</span>
          &nbsp;&nbsp; ◉ KXRECESSION-26H2 <span className="neon-magenta">18¢</span>
          &nbsp;&nbsp; ◉ KXNVDA5T-27Q2 <span className="neon-lime">44¢</span>
          &nbsp;&nbsp;✦✦✦&nbsp;&nbsp; 12,431 ACTIVE SUBSCRIBERS STACKING ON THE DESK
          &nbsp;&nbsp;✦✦✦&nbsp;&nbsp; "they laughed. now they subscribe." — @quant_sable
          &nbsp;&nbsp;✦✦✦&nbsp;&nbsp; $500/MO · WIRES ONLY · NO REFUNDS EVER
          &nbsp;&nbsp;✦✦✦&nbsp;&nbsp; next drop in T-MINUS...
        </span>
      </div>
    </div>
  );
}

function Nav() {
  return (
    <header className="sticky top-0 z-40 border-b border-[color:var(--color-chalk-faint)]/30 bg-[color:var(--color-void-deep)]/85 backdrop-blur-sm">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-3.5">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="relative h-6 w-6">
            <div className="absolute inset-0 rounded-sm border-2 border-[color:var(--color-neon-cyan)]" />
            <div className="absolute inset-1 rounded-[1px] bg-[color:var(--color-neon-cyan)] animate-blip" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="display text-xl text-[color:var(--color-chalk)]">
              LIVE<span className="neon-cyan">SIGNAL</span>
            </span>
            <span className="hidden font-mono text-[9px] uppercase tracking-[0.25em] text-[color:var(--color-chalk-faint)] sm:inline">
              // prediction arcade
            </span>
          </div>
        </Link>
        <nav className="flex items-center gap-1 font-mono text-[11px] uppercase tracking-widest">
          <NavLink href="/">Desk</NavLink>
          <NavLink href="/analysts">Analysts</NavLink>
          <Link
            href="/insiders"
            className="ml-2 border-2 border-[color:var(--color-neon-magenta)] px-3 py-1.5 text-[color:var(--color-neon-magenta)] transition hover:bg-[color:var(--color-neon-magenta)] hover:text-[color:var(--color-void-deep)]"
          >
            [ Insiders ]
          </Link>
        </nav>
      </div>
    </header>
  );
}

function NavLink({ href, children }: { href: string; children: React.ReactNode }) {
  return (
    <Link
      href={href}
      className="px-3 py-1.5 text-[color:var(--color-chalk-dim)] hover:text-[color:var(--color-neon-cyan)] transition"
    >
      {children}
    </Link>
  );
}

function Footer() {
  return (
    <footer className="relative mt-32 border-t-2 border-[color:var(--color-neon-cyan)] bg-[color:var(--color-void-deep)]">
      <div className="mx-auto grid max-w-7xl gap-10 px-6 py-14 md:grid-cols-4">
        <div className="md:col-span-2">
          <div className="display text-3xl">
            LIVE<span className="neon-cyan">SIGNAL</span>
          </div>
          <p className="mt-4 max-w-sm text-sm leading-relaxed text-[color:var(--color-chalk-dim)]">
            The prediction-market arcade. Pay your $500/mo, get the edge, out-earn your
            friends who still read the news for free. Signals are final. So are wires.
          </p>
          <p className="mt-3 font-mono text-[11px] text-[color:var(--color-chalk-faint)]">
            © 2026 LiveSignal LLC (Delaware, mostly). Not financial advice*
            <br />
            *legally required footnote
          </p>
        </div>
        <div>
          <div className="font-mono text-[10px] uppercase tracking-[0.3em] text-[color:var(--color-neon-lime)]">
            // inner circle
          </div>
          <p className="mt-3 text-sm text-[color:var(--color-chalk-dim)]">
            Members-only Telegram:
          </p>
          <p className="mt-1 font-mono text-sm neon-cyan">
            t.me/livesignal_desk_sk29h4n2v8eKPq
          </p>
          <p className="mt-3 text-xs text-[color:var(--color-chalk-faint)]">
            Invite-only. Referral required. DM an analyst. Wires preferred.
          </p>
        </div>
        <div>
          <div className="font-mono text-[10px] uppercase tracking-[0.3em] text-[color:var(--color-neon-lime)]">
            // operator
          </div>
          <p className="mt-3 text-sm text-[color:var(--color-chalk-dim)]">
            Insiders Portal:
          </p>
          <Link
            href="/insiders"
            className="mt-1 inline-block font-mono text-sm neon-magenta hover:underline"
          >
            /insiders ›
          </Link>
          <p className="mt-3 text-xs text-[color:var(--color-chalk-faint)]">
            You either belong or you don't.
          </p>
        </div>
      </div>
      <div className="border-t border-[color:var(--color-chalk-faint)]/20 py-3">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 font-mono text-[10px] uppercase tracking-widest text-[color:var(--color-chalk-faint)]">
          <span>SIGNAL UPLINK · 1200 BAUD · SESSION ALIVE</span>
          <span className="neon-lime">● ONLINE</span>
        </div>
      </div>
    </footer>
  );
}
