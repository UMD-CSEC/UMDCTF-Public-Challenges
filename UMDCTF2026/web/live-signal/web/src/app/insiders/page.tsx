import InsiderForm from "./InsiderForm";

export const dynamic = "force-dynamic";

export default function InsidersPage() {
  return (
    <div className="relative min-h-[85vh]">
      <div
        className="pointer-events-none absolute inset-0 opacity-70"
        style={{
          background:
            "radial-gradient(circle at 50% 10%, rgba(255,63,164,0.25), transparent 55%), radial-gradient(circle at 50% 90%, rgba(34,225,255,0.15), transparent 60%)",
        }}
      />
      <div className="relative mx-auto max-w-3xl px-6 py-16">
        <div className="text-center">
          <div className="font-mono text-[11px] tracking-[0.4em] uppercase animate-blip neon-magenta">
            ⬤ ACCESS RESTRICTED ⬤ ACCESS RESTRICTED ⬤
          </div>
          <h1 className="display mt-6 text-6xl md:text-7xl">
            INSIDERS <span className="neon-cyan">PORTAL</span>
          </h1>
          <p className="mx-auto mt-4 max-w-lg text-sm leading-relaxed text-[color:var(--color-chalk-dim)]">
            If you've been handed the <span className="neon-cyan">ticker</span>,
            the <span className="neon-lime">side</span>, and the{" "}
            <span className="neon-magenta">price</span> — you already belong.
            Enter them. You have one job.
          </p>
          <p className="mt-4 font-mono text-[11px] text-[color:var(--color-chalk-faint)]">
            backchannel dispatch:{" "}
            <span className="neon-cyan">t.me/livesignal_insiders_Zx8v4Nm2kqPR7t</span>{" "}
            <span className="text-[color:var(--color-chalk-faint)]">
              (you didn't see this here)
            </span>
          </p>
        </div>

        <div className="relative mt-12 cabinet-magenta crt-surface bg-[color:var(--color-void-deep)] p-8">
          <div className="absolute -top-3 left-6 bg-[color:var(--color-void-deep)] px-2 py-0.5 font-mono text-[10px] uppercase tracking-[0.3em] neon-magenta">
            verify credentials
          </div>
          <InsiderForm />
        </div>

        <ul className="mt-10 space-y-2 font-mono text-[11px] text-[color:var(--color-chalk-faint)]">
          <li>
            <span className="neon-magenta">▸</span> Three fields. Three attempts
            per minute per IP. Be decisive.
          </li>
          <li>
            <span className="neon-magenta">▸</span> Uppercase tickers. YES/NO
            only. Prices are integers 1–99¢.
          </li>
          <li>
            <span className="neon-magenta">▸</span> We do not log who tries. We
            do not log who succeeds. We remember both.
          </li>
        </ul>
      </div>
    </div>
  );
}
