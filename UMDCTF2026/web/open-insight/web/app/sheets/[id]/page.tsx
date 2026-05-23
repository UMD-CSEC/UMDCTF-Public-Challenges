import { notFound } from "next/navigation";
import Link from "next/link";
import { getSheet, parseCells } from "@/lib/sheets";
import { getSessionUser } from "@/lib/session";
import { db, type UserRow } from "@/lib/db";
import { Sheet } from "@/components/Sheet";

export default async function SheetPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const sheet = getSheet(id);
  if (!sheet) notFound();

  const viewer = await getSessionUser();
  const owner = db()
    .prepare("SELECT * FROM users WHERE id = ?")
    .get(sheet.owner_id) as UserRow | undefined;
  const isOwner = !!viewer && viewer.id === sheet.owner_id;
  const cells = parseCells(sheet);

  return (
    <>
      <div className="mx-auto max-w-6xl">
        <div className="flex flex-wrap items-baseline justify-between gap-3 px-6 pt-6">
          <p className="eyebrow">
            <Link
              href="/"
              className="hover:text-[color:var(--color-paper)]"
            >
              ← Popular
            </Link>
            <span className="mx-2 text-[color:var(--color-rule-strong)]">
              ·
            </span>
            <span>Owner</span>{" "}
            <span className="ml-1 font-mono text-[color:var(--color-paper-dim)]">
              {owner?.username ?? "unknown"}
            </span>
          </p>
        </div>
      </div>
      <div className="mx-auto max-w-6xl">
        <Sheet
          id={sheet.id}
          initialTitle={sheet.title}
          initialCells={cells}
          isOwner={isOwner}
        />
      </div>
    </>
  );
}
