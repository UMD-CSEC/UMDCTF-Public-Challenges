"use server";

import { getSessionUser } from "@/lib/session";
import { getSheet, updateSheet, type Cells } from "@/lib/sheets";

const CELL_RE = /^[A-L](?:[1-9]|[12][0-9]|30)$/;

function sanitizeCells(input: unknown): Cells {
  const out: Cells = {};
  if (!input || typeof input !== "object") return out;
  for (const [k, v] of Object.entries(input as Record<string, unknown>)) {
    if (!CELL_RE.test(k)) continue;
    if (!v || typeof v !== "object") continue;
    const formula = String((v as { formula?: unknown }).formula ?? "");
    if (formula.length > 2000) continue;
    out[k] = { formula };
  }
  return out;
}

export async function saveSheetAction(
  id: string,
  patch: { title?: string; cells?: unknown },
) {
  const user = await getSessionUser();
  if (!user) return { ok: false, error: "unauthorized" as const };
  const sheet = getSheet(id);
  if (!sheet) return { ok: false, error: "not_found" as const };
  if (sheet.owner_id !== user.id)
    return { ok: false, error: "not_owner" as const };

  const cells =
    patch.cells !== undefined ? sanitizeCells(patch.cells) : undefined;
  const updated = updateSheet(id, {
    title: patch.title?.toString().slice(0, 200),
    cells,
  });
  if (!updated) return { ok: false, error: "not_found" as const };
  return { ok: true as const, updated_at: updated.updated_at };
}
