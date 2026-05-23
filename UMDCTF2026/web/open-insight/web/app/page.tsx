import Link from "next/link";
import { db, type UserRow } from "@/lib/db";
import { listPopular } from "@/lib/sheets";
import { SheetCard } from "@/components/SheetCard";

export default async function HomePage() {
  const popular = listPopular(20);

  const userMap = new Map<number, string>();
  for (const row of db()
    .prepare("SELECT id, username FROM users")
    .all() as Pick<UserRow, "id" | "username">[]) {
    userMap.set(row.id, row.username);
  }

  const now = new Date();
  const timestamp = now.toLocaleString("en-US", {
    timeZone: "UTC",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });

  return (
    <>
      {/* Hero */}
      <section className="mx-auto max-w-6xl px-6 pt-16 pb-20">
        <div className="grid grid-cols-12 items-end gap-6">
          <div className="col-span-12 md:col-span-8">
            <p className="eyebrow">
              Vol. 1 · No. {String(new Date().getDate()).padStart(2, "0")} ·
              Research Desk
            </p>
            <h1
              className="display mt-6 text-[clamp(3.5rem,8vw,7rem)] text-[color:var(--color-paper)]"
              style={{ fontVariationSettings: '"opsz" 144, "SOFT" 40' }}
            >
              Shared models
              <br />
              for{" "}
              <span className="italic text-[color:var(--color-signal)]">
                forecasters
              </span>
              .
            </h1>
          </div>
          <div className="col-span-12 flex flex-col gap-3 border-l border-[color:var(--color-rule)] pl-5 md:col-span-4">
            <p className="text-[15px] leading-relaxed text-[color:var(--color-paper-dim)]">
              OpenInsight is a research desk in the browser. Publish your
              spreadsheets, plug into live market data, and see how your calls
              hold up.
            </p>
            <div className="mt-2 flex flex-wrap gap-2">
              <Link
                href="/signup"
                className="bg-[color:var(--color-signal)] px-4 py-2 font-mono text-xs font-medium text-[#0b0c0e] hover:brightness-110"
              >
                Open an account →
              </Link>
              <Link
                href="/sheets/new"
                className="eyebrow border border-[color:var(--color-rule)] px-4 py-2 text-[color:var(--color-paper-dim)] hover:border-[color:var(--color-rule-strong)] hover:text-[color:var(--color-paper)]"
              >
                Start a workbook
              </Link>
            </div>
          </div>
        </div>

        {/* ticker strip */}
        <div className="mt-14 flex flex-wrap items-baseline justify-between gap-3 border-y border-[color:var(--color-rule)] py-3">
          <p className="eyebrow">
            <span className="mr-2 inline-block h-[6px] w-[6px] -translate-y-[1px] rounded-full bg-[color:var(--color-signal)] blink" />
            LIVE · {timestamp} UTC
          </p>
          <p className="eyebrow text-[color:var(--color-paper-dim)]">
            {popular.length} featured · curated weekly
          </p>
        </div>
      </section>

      {/* Popular sheets */}
      <section className="mx-auto max-w-6xl px-6 pb-24">
        <div className="flex items-baseline justify-between pb-4">
          <div>
            <p className="eyebrow">01 · Featured</p>
            <h2
              className="display mt-1 text-3xl"
              style={{ fontVariationSettings: '"opsz" 48, "SOFT" 30' }}
            >
              Popular spreadsheets.
            </h2>
          </div>
          <p className="eyebrow hidden text-[color:var(--color-paper-faint)] md:block">
            Curated by the research desk
          </p>
        </div>
        <div>
          {popular.length === 0 ? (
            <p className="border-t border-[color:var(--color-rule)] py-10 font-mono text-sm text-[color:var(--color-paper-faint)]">
              No featured sheets yet. Run{" "}
              <code className="rounded bg-[color:var(--color-bg-elevated)] px-1 text-[color:var(--color-paper-dim)]">
                pnpm seed
              </code>{" "}
              to populate.
            </p>
          ) : (
            popular.map((sheet, i) => (
              <SheetCard
                key={sheet.id}
                sheet={sheet}
                ownerUsername={userMap.get(sheet.owner_id) ?? "unknown"}
                delay={i * 40}
              />
            ))
          )}
          <div className="border-t border-[color:var(--color-rule)]" />
        </div>
      </section>
    </>
  );
}
