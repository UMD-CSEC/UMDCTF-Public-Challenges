import Link from "next/link";
import { parseCells, type Cells } from "@/lib/sheets";
import type { SheetRow } from "@/lib/db";

export function SheetCard({
  sheet,
  ownerUsername,
  delay = 0,
}: {
  sheet: SheetRow;
  ownerUsername: string;
  delay?: number;
}) {
  const cells = parseCells(sheet);
  const preview = previewStrings(cells, 4);
  const rowCount = countRows(cells);
  const updated = new Date(sheet.updated_at);

  return (
    <Link
      href={`/sheets/${sheet.id}`}
      className="group block border-t border-[color:var(--color-rule)] py-6 transition-colors hover:border-[color:var(--color-rule-strong)]"
      style={{
        animation: `fade-up 0.55s cubic-bezier(.2,.7,.2,1) ${delay}ms both`,
      }}
    >
      <div className="flex items-baseline justify-between gap-6">
        <div className="flex-1">
          <div className="flex items-baseline gap-3">
            <p className="eyebrow text-[color:var(--color-paper-faint)]">
              by{" "}
              <span className="font-mono text-[color:var(--color-paper-dim)]">
                {ownerUsername}
              </span>
            </p>
            <span className="eyebrow text-[color:var(--color-paper-faint)]">
              · {rowCount} rows
            </span>
            <span className="eyebrow text-[color:var(--color-paper-faint)]">
              · updated{" "}
              {updated.toLocaleDateString("en-US", {
                month: "short",
                day: "numeric",
              })}
            </span>
          </div>
          <h3
            className="display mt-2 text-2xl leading-tight text-[color:var(--color-paper)] transition-colors group-hover:text-[color:var(--color-signal)]"
            style={{ fontVariationSettings: '"opsz" 48, "SOFT" 30' }}
          >
            {sheet.title}
          </h3>
          <ul className="mt-3 hidden gap-x-6 gap-y-1 font-mono text-[11px] text-[color:var(--color-paper-dim)] md:grid md:grid-cols-2 lg:grid-cols-4">
            {preview.map((p, i) => (
              <li key={i} className="truncate">
                <span className="text-[color:var(--color-paper-faint)]">
                  {p.ref}
                </span>{" "}
                {p.value}
              </li>
            ))}
          </ul>
        </div>
        <span
          aria-hidden
          className="shrink-0 translate-y-1 font-mono text-xs text-[color:var(--color-paper-faint)] transition-colors group-hover:text-[color:var(--color-signal)]"
        >
          ▸
        </span>
      </div>
    </Link>
  );
}

function previewStrings(cells: Cells, n: number) {
  const entries = Object.entries(cells).slice(0, n);
  return entries.map(([ref, c]) => ({
    ref,
    value:
      c.formula.length > 32 ? c.formula.slice(0, 32) + "…" : c.formula,
  }));
}

function countRows(cells: Cells): number {
  const rows = new Set<number>();
  for (const ref of Object.keys(cells)) {
    const n = parseInt(ref.slice(1), 10);
    if (!isNaN(n)) rows.add(n);
  }
  return rows.size;
}
