import Link from "next/link";

export default function NotFound() {
  return (
    <div className="mx-auto max-w-2xl px-6 py-32 text-center">
      <div className="font-mono text-[10px] tracking-[0.5em] uppercase animate-blip neon-magenta">
        ✗ signal lost · 404
      </div>
      <h1 className="display mt-6 text-6xl">no such analyst.</h1>
      <p className="mt-4 text-[color:var(--color-chalk-dim)]">
        They might have been delisted. Or they never existed. Or their lawyer
        called. Happens to the best of us.
      </p>
      <Link
        href="/analysts"
        className="mt-10 inline-block border-2 border-[color:var(--color-neon-cyan)] px-6 py-3 font-mono text-xs uppercase tracking-[0.3em] neon-cyan hover:bg-[color:var(--color-neon-cyan)] hover:text-[color:var(--color-void-deep)]"
      >
        ← back to the desk
      </Link>
    </div>
  );
}
